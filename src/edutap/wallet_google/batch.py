"""Batch requests against the Google Wallet API.

A :class:`Batch` collects sub-requests and sends them as a single
``multipart/mixed`` request, following the mechanism documented at
https://developers.google.com/wallet/generic/resources/performance-tips.

A batch appears to count as a single call against the 20-calls-per-second rate
limit (https://developers.google.com/wallet/generic/resources/faq), so a hundred
updates in one Batch cost what one update costs. This is an operational finding
from running the real system, not something Google documents or guarantees.
"""

from .clientpool import client_pool
from .models.bases import make_partial_model
from .models.bases import Model
from .multipart import decode_multipart
from .multipart import encode_multipart
from .multipart import make_boundary
from .multipart import SubRequest
from .multipart import SubResponse
from .registry import lookup_metadata_by_name
from .registry import raise_when_operation_not_allowed
from .utils import handle_response_errors
from pydantic import ConfigDict
from pydantic import ValidationError as PydanticValidationError

import typing
import urllib.parse


class BatchError(Model):
    """The error Google reports for a single failed sub-request.

    Unlike the wallet models, this describes a *foreign* response payload, not
    something of ours: Google's real error object carries fields beyond the three
    modeled here (``details``, and in the classic error envelope, ``errors``).
    ``extra="ignore"`` -- rather than the strict base's ``extra="forbid"`` -- keeps
    those extra fields from turning an ordinary error response into a
    ``ValidationError`` that would take the whole batch down with it.
    """

    model_config = ConfigDict(extra="ignore")

    code: int
    message: str
    status: str | None = None


class BatchResult(Model):
    """The outcome of one sub-request, correlated back to its input item."""

    index: int
    name: str
    resource_id: str
    status_code: int
    body: dict | None = None
    error: BatchError | None = None

    @property
    def ok(self) -> bool:
        """True when Google accepted this sub-request."""
        return self.error is None and 200 <= self.status_code < 300


class Batch:
    """Collects sub-requests and sends them as one API call.

    Fill it, then execute it::

        batch = Batch()
        batch.add_update("LoyaltyObject", {"id": "issuer.m1", "state": "EXPIRED"})
        results = batch.execute()

    Pass types may be mixed freely — each sub-request carries its own path.

    A ``Batch`` is single-use: :meth:`execute` (and :meth:`aexecute`) neither clears
    nor locks the collected sub-requests, so calling it a second time sends
    everything again as a new request. Build a fresh ``Batch`` for the next call.
    """

    def __init__(self) -> None:
        self._sub_requests: list[SubRequest] = []
        # Parallel to _sub_requests: what each one was about, for the results.
        self._items: list[tuple[str, str]] = []

    def __len__(self) -> int:
        """Number of sub-requests collected so far.

        One Batch is one HTTP request, so this is the number the caller needs in
        order to decide whether to send it or start a new one.
        """
        return len(self._sub_requests)

    def add_update(self, name: str, data: dict[str, typing.Any]) -> None:
        """Add a PATCH for one object.

        Only the attributes present in ``data`` are sent. The payload is
        validated here rather than at execute time, so a typo fails on the line
        that caused it.

        :param name: Registered model name, e.g. "LoyaltyObject".
        :param data: The attributes to change, plus the resource id.
        :raises ValueError: When the payload is invalid or carries no resource id.
        """
        metadata = lookup_metadata_by_name(name)
        raise_when_operation_not_allowed(name, "update")
        resource_id_key = metadata["resource_id"]

        resource_id = data.get(resource_id_key)
        if not resource_id:
            raise ValueError(
                f"Item for '{name}' has no '{resource_id_key}'; nothing to update."
            )

        partial_model = make_partial_model(metadata["model"])
        try:
            verified = partial_model.model_validate(data)
        except PydanticValidationError as exc:
            raise ValueError(
                f"Item '{resource_id}' is invalid for '{name}': {exc}"
            ) from exc

        api_path = urllib.parse.urlparse(str(client_pool.settings.api_url)).path
        self._sub_requests.append(
            SubRequest(
                method="PATCH",
                path=f"{api_path}/{metadata['url_part']}/{resource_id}",
                body=verified.model_dump_json(exclude_unset=True, by_alias=True),
                content_id=f"item-{len(self._sub_requests)}",
            )
        )
        self._items.append((name, resource_id))

    def add_updates(
        self,
        name: str,
        data: list[dict[str, typing.Any]],
    ) -> None:
        """Add a PATCH for each object in a list.

        :param name: Registered model name, applied to every item.
        :param data: One dict per object.
        :raises ValueError: When any payload is invalid or carries no resource id.
        """
        for item in data:
            self.add_update(name, item)

    def _ordered_sub_requests(self) -> list[SubRequest]:
        """Return the sub-requests in the order they should go on the wire.

        Grouped by pass type. ``sorted`` is stable, so within a type the add
        order survives. This is free to change: results are correlated by
        Content-ID, not by position, so reordering here cannot affect what
        :meth:`execute` returns.
        """
        order = sorted(
            range(len(self._sub_requests)),
            key=lambda index: self._items[index][0],
        )
        return [self._sub_requests[index] for index in order]

    def _build_results(self, sub_responses: list[SubResponse]) -> list[BatchResult]:
        """Correlate sub-responses back to the items that produced them.

        Correlation is by Content-ID, not by position: the specification does not
        promise the server answers in the order it was asked.
        """
        by_content_id = {r.content_id: r for r in sub_responses if r.content_id}
        results: list[BatchResult] = []
        for index, (name, resource_id) in enumerate(self._items):
            sub_response = by_content_id.get(f"item-{index}")
            if sub_response is None:
                results.append(
                    BatchResult(
                        index=index,
                        name=name,
                        resource_id=resource_id,
                        status_code=0,
                        error=BatchError(
                            code=0, message="No response part for this sub-request."
                        ),
                    )
                )
                continue
            body = sub_response.body
            error = None
            if body is not None and isinstance(body.get("error"), dict):
                # Total by construction: no future shape of Google's error object
                # may raise out of here and take the rest of the batch down with
                # it -- that is exactly the contract this whole class exists to
                # keep. BatchError.model_config already ignores unknown fields
                # (see its docstring); this except is the backstop for whatever
                # that config does not anticipate, e.g. a field of the wrong type.
                try:
                    error = BatchError.model_validate(body["error"])
                except PydanticValidationError:
                    error = BatchError(
                        code=sub_response.status_code, message=str(body["error"])
                    )
                body = None
            elif not (200 <= sub_response.status_code < 300):
                # Invariant: BatchResult.ok is False implies BatchResult.error is
                # not None. Google's protocol only guarantees an "error" key in
                # the body for the errors it recognises; a non-2xx status can
                # still arrive with no such key (or, per _parse_http_payload, a
                # status line that could not even be parsed, degraded here to
                # status_code=0). Without this branch, callers following the
                # documented `if not result.ok: print(result.error.message)`
                # pattern would hit AttributeError on error=None.
                if sub_response.status_code == 0:
                    message = "Sub-response status line could not be parsed."
                else:
                    message = (
                        f"Sub-response returned status {sub_response.status_code} "
                        "without an error body."
                    )
                error = BatchError(code=sub_response.status_code, message=message)
            results.append(
                BatchResult(
                    index=index,
                    name=name,
                    resource_id=resource_id,
                    status_code=sub_response.status_code,
                    body=body,
                    error=error,
                )
            )
        return results

    def execute(self, *, credentials: dict | None = None) -> list[BatchResult]:
        """Send the collected sub-requests as one API call.

        Individual sub-request failures do **not** raise; they come back as
        results carrying an ``error``. Only the batch request itself failing
        raises.

        Sub-requests may be grouped and reordered on the wire. The results are
        not: they come back in the order the items were added, correlated by
        Content-ID.

        This does not chunk, throttle or retry. The Google Wallet API is rate
        limited to 20 calls per second; staying within it is the caller's
        business. Parameters are keyword-only so that a later driver stage can
        add ``chunk_size`` and friends without breaking existing calls.

        :param credentials: Optional session credentials as dict.
        :raises WalletException: When the batch request itself fails.
        :return: One result per added sub-request, in the order they were added.
        """
        if not self._sub_requests:
            return []
        boundary = make_boundary()

        client = client_pool.client(credentials=credentials)
        response = client.post(
            url=str(client_pool.settings.batch_url),
            content=encode_multipart(self._ordered_sub_requests(), boundary),
            headers={"Content-Type": f"multipart/mixed; boundary={boundary}"},
        )
        handle_response_errors(response, "batch", "Batch", f"{len(self)} items")

        return self._build_results(
            decode_multipart(response.content, response.headers.get("Content-Type", ""))
        )

    async def aexecute(self, *, credentials: dict | None = None) -> list[BatchResult]:
        """Asynchronously send the collected sub-requests as one API call.

        See :meth:`execute` for the full description; behaviour is identical.

        :param credentials: Optional session credentials as dict.
        :raises WalletException: When the batch request itself fails.
        :return: One result per added sub-request, in the order they were added.
        """
        if not self._sub_requests:
            return []
        boundary = make_boundary()

        client = client_pool.async_client(credentials=credentials)
        response = await client.post(
            url=str(client_pool.settings.batch_url),
            content=encode_multipart(self._ordered_sub_requests(), boundary),
            headers={"Content-Type": f"multipart/mixed; boundary={boundary}"},
        )
        handle_response_errors(response, "batch", "Batch", f"{len(self)} items")

        return self._build_results(
            decode_multipart(response.content, response.headers.get("Content-Type", ""))
        )
