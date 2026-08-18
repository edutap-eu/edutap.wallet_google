# Handoff: the `jwt.insert` and `jwt.validate` endpoints

**Written:** 2026-08-18 · **Status:** investigation, not decided · **Language:** English
(this is an eduTAP package on GitHub)

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

### What the package has today

`api.save_link()` builds the same `savetowallet` JWT **locally** and returns
`{settings.save_url}/{jwt}` without ever calling Google. `jwt.insert` is the server side
of the same idea, and the two are not interchangeable — see "Why bother" below.

`JwtResource` is **already registered**, with `url_part="jwt"` and `can_create=True`
(`src/edutap/wallet_google/models/misc.py:89`). `JwtResponse` — `{saveUri, resources}` —
exists right below it and is referenced from nowhere but `docs/reference.md`.

**That combination is a latent bug, not just a gap.** `api.create()` parses the response
with the same model it sent, so `api.create(JwtResource(jwt="..."))` posts to the correct
URL and then fails on the response. Verified by constructing the objects rather than by
reading the code:

```python
>>> from edutap.wallet_google.models.misc import JwtResource, JwtResponse
>>> body = {"saveUri": "https://pay.google.com/gp/v/save/eyJ...",
...         "resources": {"genericObjects": [{"id": "...", "classId": "...", "state": "ACTIVE"}]}}
>>> JwtResource.model_validate(body)
ValidationError: 3 validation errors for JwtResource
>>> JwtResponse.model_validate(body)   # parses fine
```

So whoever picks this up is not starting from zero, and is not starting from something
that works either.

### Which models are missing

`Resources` and `JwtResponse` exist and match the API. Missing for `validate`:
`JsonResource` (`{json: str}`), `JwtValidateRequest`, `JwtValidateResponse`.

## Why bother — the case for `insert`

`save_link()` puts the entire JWT in the URL. `api.py:235` already logs a warning past
1800 bytes, which is Google's documented recommendation. A pass with several objects, or
one carrying full class definitions instead of `Reference`s, runs into that ceiling, and
there is nothing `save_link()` can do about it: the payload *is* the link.

`jwt.insert` posts the JWT once, creates the resources server-side and hands back a short
`saveUri`. The length problem disappears. That, and not convenience, is the reason to
have it.

The case for `validate` is weaker but real: it is a pre-flight check that costs one call
and tells you a pass is well formed before you hand a link to a user.

**Neither has been tested against the real API.** The whole section above describes what
Google *declares*, not what it does.

## What the work is

Roughly in order of value. Each step small and verifiable, test first.

### 1. Decide how a differing response type is expressed

This is the design decision everything else hangs off, and it should be made before any
code is written.

`RegistryMetadataDict` (`registry.py:16`) has no notion of "the response has a different
shape than the request". Every registered model is assumed to round-trip. `jwt` is the
first endpoint where that does not hold.

Two directions, and they are genuinely different in spirit:

* **(a) Teach the registry a `response_model`.** `create()` then parses with it when
  present. Small change, keeps `jwt.insert` inside the CRUD machinery, and any future
  endpoint with an asymmetric response gets it for free. Risk: `create()` grows a special
  case, and `JwtResource` keeps pretending to be a CRUD resource when it is not one —
  there is nothing to read, update or list.
* **(b) A dedicated function in `api.py`, outside CRUD.** Something like
  `insert_jwt(models, ...) -> JwtResponse` (plus `ainsert_jwt`), sitting next to
  `save_link()` because that is what it is related to, and unregistering `JwtResource`
  from the CRUD registry. Honest about the shape of the endpoint. Risk: a second path
  that has to repeat client handling and error handling.

My reading is that (b) fits the endpoint better — `jwt.insert` is not "create a JWT", it
is "create everything named in this JWT" — but (a) is the smaller diff and I have not
weighed it against how the maintainers want the registry to evolve. **Ask before
choosing.**

Whichever wins, `can_create=True` on `JwtResource` must stop meaning what it means today.

### 2. `jwt.insert`

Test first, with `respx`, the way `test_api_sync.py` and `test_api_async.py` mock the
other endpoints. Sync and async, since every other call has both.

Watch out for:

* the JWT is built by the existing `_create_claims()` / `_create_payload()`; do not write
  a second JWT builder
* `JwtResponse.saveUri` is `AnyHttpUrl` while the API declares a plain string — that is a
  deliberate refinement and `test_property_types` accepts it
* `Resources` holds the *created* objects, so the return value is worth surfacing, not
  discarding

### 3. `jwt.validate`

Needs the three models from above. Note the request takes **either** `jwtResource` **or**
`jsonResource`; Google's description says "Either this or json_resource should be
provided", so a validator enforcing exactly-one is appropriate.

The empty response needs a decision of its own: return `None`, return `True`, or raise on
the error path only. Whatever is chosen, `JwtValidateResponse` is a model with no fields,
which will look odd to a reader — say why in the docstring.

### 4. Remove them from the ignore list

Once modelled, delete `JsonResource` from `UNIMPLEMENTED_ENDPOINT_SCHEMAS` in
`tests/test_check_models.py`. The schema-set assertion then covers them, and
`test_property_types` and `test_deprecated_properties` pick them up automatically.
`ModifyLinkedOfferObjects` stays until someone does that separately.

Also revisit `test_methods`: it silently skips resources with no registered model of the
same name, which is why `jwt` never showed up as missing. After this, `jwt` has models
but still no `get`/`list`/`patch`, so the expected-method logic needs a case for it —
much like the `Permissions` special case already there (`test_check_models.py:389`).

## Open questions

* **Do we want `insert` at all?** It only pays off if we actually hit the JWT length
  ceiling. Does any eduTAP pass do that today, or is this speculative? If nobody has seen
  the warning in a log, this is a solution looking for a problem, and the honest answer
  might be "not yet".
* **Registry or dedicated function** — step 1 above.
* **Does `insert` create or upsert?** "Inserts the resources in the JWT" does not say what
  happens when an object already exists. `create()` maps 409 to
  `ObjectAlreadyExistsException`; whether `jwt.insert` behaves that way is unknown and
  only an integration test against a real issuer can answer it.
* **Is `validate` worth a round trip?** Our models already validate locally, and Pydantic
  with `extra="forbid"` catches most of what Google would. What does `validate` catch that
  we do not?

## Environment

* No `Makefile` here, contrary to the eduTAP house style. Tests run through
  `uvx tox -e py313`, lint through `uvx tox -e lint`.
* **Run the suite through tox, not in a bare venv.** The `py` tox environment (`pyproject.toml:161`) installs
  `tests/data/test_wallet_google_plugins` as an editable dependency; without it 10 tests
  fail on missing entry points and look like real breakage.
* `tests/test_check_models.py` needs network access. Both Google endpoints are reachable
  without authentication.
* Integration tests need real credentials and `--run-integration`. For anything in this
  handoff that touches "what does the API actually do", that is the only way to find out.
* Dev extras live in `[project.optional-dependencies]`, not `[dependency-groups]`. Not
  this task's business.
* After opening the PR, wait for Copilot's review and work through the comments one by
  one. On PR #99 it came back empty because the requesting account had hit its quota —
  check for that before concluding there was nothing to say.

## Suggested skills

* `superpowers:brainstorming` — unlike PR #99, the scope here is **not** settled. Step 1
  is a real design decision and the first open question may end with "we do not build
  this". Brainstorm before planning.
* `superpowers:test-driven-development` — once the direction is set.
* `superpowers:verification-before-completion` — the discovery document says what Google
  declares. Anything about behaviour needs an integration test or the label "untested".
