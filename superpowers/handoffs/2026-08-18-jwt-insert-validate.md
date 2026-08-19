# Handoff: the `jwt.insert` and `jwt.validate` endpoints

**Written:** 2026-08-18 · **Status:** `insert` decided against, `validate` open ·
**Language:** English (this is an eduTAP package on GitHub)

## Where this comes from

PR #99 held the models against the discovery document. Two schemas turned out to be
missing, and both belong to endpoints this package does not implement:

* `JsonResource` — the body of `walletobjects.jwt.validate`
* `ModifyLinkedOfferObjects` — the body of `loyaltyobject.modifylinkedofferobjects`

They were put on `UNIMPLEMENTED_ENDPOINT_SCHEMAS` in `tests/test_check_models.py`, which
keeps the schema-set assertion honest without pretending the endpoints exist. **This
handoff covers only the two `jwt` methods.** `modifylinkedofferobjects` is a separate
question and is out of scope here.

## Already verified — do not redo this

Measured on 2026-08-18 against discovery revision `20260818`.

### What the API offers

```
walletobjects.jwt.insert    POST walletobjects/v1/jwt
                            request  JwtResource        {jwt: str}
                            response JwtInsertResponse  {saveUri: str, resources: Resources}
                            "Inserts the resources in the JWT."

walletobjects.jwt.validate  POST walletobjects/v1/jwt/validate
                            request  JwtValidateRequest  {jwtResource?: JwtResource,
                                                          jsonResource?: JsonResource}
                            response JwtValidateResponse {}   ← no properties at all
                            "Checks that the JWT or JSON string in the request
                             represents a valid pass to be saved."
```

Both need the scope `https://www.googleapis.com/auth/wallet_object.issuer`, which the
package already requests. `JwtValidateResponse` is empty by design: valid means an empty
body, invalid means an error response.

### Which models exist

`JwtResource`, `Resources` and `JwtResponse` (`{saveUri, resources}`) exist in
`models/misc.py` and match the API. Missing, all three only needed for `validate`:
`JsonResource` (`{json: str}`), `JwtValidateRequest`, `JwtValidateResponse`.

## `jwt.insert` — decided against

**Do not build this.** The decision is Alexander's, taken 2026-08-18, and the reasoning
is recorded here so nobody proposes it a third time.

The endpoint solves exactly one problem: `save_link()` puts the entire JWT into the URL,
and `api.py:235` warns past 1800 bytes, which is Google's documented recommendation.
`jwt.insert` posts the JWT once, creates the resources server-side and returns a short
`saveUri` instead.

**We do hit that ceiling — regularly.** It is not a theoretical concern. Measured with a
plausible student card (title, header, subheader, logo, hero image, QR barcode, three
text modules):

```
Vollobjekt im JWT    claims JSON 1252 B  ->  JWT ~2029 B   over the recommendation
Reference im JWT     claims JSON  212 B  ->  JWT  ~642 B   comfortably under
```

And that is the point: **the ceiling was already solved another way.** Class and object
are created up front through the CRUD API, and the JWT carries only the id. The package
supports this directly — `JWTPayload` accepts `Model | Reference`, `save_link()` takes
`list[ClassModel | ObjectModel | Reference]`, and `_create_payload()` (`api.py:107`)
sorts a `Reference` into the right list by `model_name` or `model_type`.

So `jwt.insert` would buy a second route to a problem that has a working first route,
at the cost of a network round trip `save_link()` does not need today. Not worth it.

### The loose end it leaves — worth fixing on its own

`JwtResource` is registered with `url_part="jwt"` and `can_create=True`
(`models/misc.py:89`), and `create()` parses the response with the same model it sent.
So `api.create(JwtResource(jwt="..."))` posts to the correct URL and then fails on the
response. Verified by constructing the objects, not by reading the code:

```python
>>> from edutap.wallet_google.models.misc import JwtResource, JwtResponse
>>> body = {"saveUri": "https://pay.google.com/gp/v/save/eyJ...",
...         "resources": {"genericObjects": [{"id": "...", "classId": "...", "state": "ACTIVE"}]}}
>>> JwtResource.model_validate(body)
ValidationError: 3 validation errors for JwtResource
>>> JwtResponse.model_validate(body)   # parses fine
```

`JwtResponse` is referenced from nowhere but `docs/reference.md`.

Now that `insert` is off the table, the honest fix is small: **set `can_create=False` on
`JwtResource`**. `_prepare_create()` then raises through
`raise_when_operation_not_allowed()` — a clear "not allowed" instead of a confusing
`ValidationError` three fields deep.

`JwtResource` itself has to stay either way: the API declares that schema, and
`is_envelope()` does not drop it — "Resource" is not "Response". Whether `JwtResponse`
stays as documentation of the endpoint or goes is free; `is_envelope()` does drop that
one, so `test_known_schemas` does not care. Checked, not assumed.

While in there: `MODEL_ALIAS_DICT` in `tests/test_check_models.py` maps `"Jwt"` to
`"JwtResource"`, and no class named `Jwt` exists in the package. The entry predates PR #99
and is harmless — the map is only ever read with `.get()` — but it is dead and can go.

This is a one-line change plus a test. It does not belong in PR #99 and was deliberately
not smuggled in there.

## `jwt.validate` — open

This is the part still worth thinking about, and it has **not** been decided.

### What it might buy us

Our models validate structure: Pydantic with `extra="forbid"` catches unknown fields,
wrong types and — since PR #99 — wrong enum values. What it cannot catch is everything
that depends on state at Google:

* does the referenced `classId` exist, and is it `LIVE` rather than `DRAFT`?
* does our issuer own it?
* whatever semantic rules Google applies that are documented nowhere

Given that we hand save links to students, a pre-flight check that catches a broken pass
before the user sees a failure page is plausibly worth one call. **Plausibly** — nobody
has measured what `validate` actually rejects that we do not.

### What to find out first

**Do not implement anything before this is answered**, because the answer decides whether
there is a feature here at all:

1. Feed `validate` a pass our models accept but that is broken at Google — a `classId`
   that does not exist, a class in `DRAFT`, an id belonging to another issuer. Does it
   reject them? With a usable error?
2. Feed it something our models already reject. If `validate` only catches what Pydantic
   catches, there is no feature here.

That needs real credentials and an integration test. `tests/integration/` and
`--run-integration` are the place; there is no way to answer it from the discovery
document.

### If it turns out to be worth it

Small, verifiable steps, test first.

**Shape.** `validate` is not a CRUD operation — nothing is created, read, updated or
listed, and the response has no body. Do not try to bend it into the registry; a
dedicated pair in `api.py` next to `save_link()` fits what it is. Something like
`validate_pass(...)` / `avalidate_pass(...)`, sync and async, because every other call
here has both.

Note the contrast with `insert`: that one *would* have raised the question of whether
`RegistryMetadataDict` (`registry.py:16`) needs a `response_model`, since it has no notion
of a response shape differing from the request. With `insert` out, that question is moot —
do not reopen it for `validate`.

**Models.** `JsonResource`, `JwtValidateRequest`, `JwtValidateResponse`. The request takes
**either** `jwtResource` **or** `jsonResource` — Google's own wording is "Either this or
json_resource should be provided" — so a `model_validator` enforcing exactly-one belongs
there. `JsonResource.json` is the *unencoded* JWT payload as a JSON string, which means a
pass can be validated without signing it first; that is the more useful of the two inputs
for a pre-flight check.

Careful: `json` is a field name that shadows nothing in Pydantic v2 but reads badly. Keep
the API name — `test_known_schemas` compares property names and would fail otherwise.

**Return value.** `JwtValidateResponse` has no properties. Decide deliberately between
returning `None`, returning `True`, and raising only on the error path, and say why in the
docstring — a model with no fields will look like a mistake to the next reader.

**Ignore list.** Once modelled, delete `JsonResource` from
`UNIMPLEMENTED_ENDPOINT_SCHEMAS` (`tests/test_check_models.py:41`). The schema-set
assertion then covers it, and `test_property_types` and `test_deprecated_properties` pick
it up automatically. `ModifyLinkedOfferObjects` stays.

**`test_methods`.** It silently skips API resources with no registered model of the same
name, which is why `jwt` never showed up as missing. If anything under `jwt` becomes
registered, that test needs a case for it — much like the `Permissions` special case
already there (`tests/test_check_models.py:389`).

## Environment

* No `Makefile` here, contrary to the eduTAP house style. Tests run through
  `uvx tox -e py313`, lint through `uvx tox -e lint`.
* **Run the suite through tox, not in a bare venv.** The `py` tox environment
  (`pyproject.toml:161`) installs `tests/data/test_wallet_google_plugins` as an editable
  dependency; without it 10 tests fail on missing entry points and look like real
  breakage.
* `tests/test_check_models.py` needs network access. Both Google endpoints are reachable
  without authentication.
* Integration tests need real credentials and `--run-integration`. Everything this handoff
  leaves open is a question about behaviour, so that is the only way to close it.
* Dev extras live in `[project.optional-dependencies]`, not `[dependency-groups]`. Not
  this task's business.
* After opening the PR, wait for Copilot's review and work through the comments one by
  one. On PR #99 it came back empty because the requesting account had hit its quota —
  check for that before concluding there was nothing to say.

## Suggested skills

* `superpowers:brainstorming` — for `validate`, if and only if the two questions above
  come back in its favour. The scope is genuinely open and may end in "we do not build
  this".
* `superpowers:test-driven-development` — for the `can_create=False` fix, which needs no
  brainstorming at all.
* `superpowers:verification-before-completion` — the discovery document says what Google
  declares. Anything about behaviour needs an integration test or the label "untested".
