# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**edutap.wallet_google** is a Python library for interacting with the Google Wallet RESTful API to issue and manage digital wallet passes.

The package provides:
- CRUD API for Google Wallet classes (templates) and objects (passes)
- Single `api.py` module with both sync and async functions (async prefixed with `a`)
- Pydantic models matching Google Wallet's data structures
- FastAPI endpoints for callbacks and image serving
- Plugin system for business logic integration

### Installation

Install the base package or with optional extras:
- `pip install edutap.wallet_google` - Base package with both sync and async APIs (authlib + httpx)
- `pip install edutap.wallet_google[callback]` - Includes FastAPI callback endpoints
- `pip install edutap.wallet_google[test]` - Includes testing dependencies
- `pip install edutap.wallet_google[develop]` - Includes development tools (pdbp debugger)

## Development Commands

### Setup and Testing

```bash
# Run all tests
uvx tox -e py313

# Run specific test file
uvx tox -e py313 -- tests/test_api_crud.py -v

# Run single test
uvx tox -e py313 -- tests/test_api_crud.py::test_read_generic_class -v

# Run with coverage
uvx tox -e py313 -- --cov=src/edutap/wallet_google/api --cov-report=term-missing tests/

# Run integration tests (requires credentials)
uvx tox -e py313 -- tests/integration/ -v --run-integration
```

### Code Quality

```bash
# Run all pre-commit hooks
uvx pre-commit run --all-files

# Auto-format code
uvx ruff format src tests

# Type checking
uvx mypy src tests
```

### Utilities

```bash
# Generate Fernet encryption key
uv run generate-fernet-key
```

## Architecture

### Core Components

**API Layer** (`api.py`):
- `new(name, data)` - Create model instances from dict/Model (shared for sync/async)
- `create(data)` / `acreate(data)` - POST new class/object to Google API
- `read(name, resource_id)` / `aread(name, resource_id)` - GET class/object by ID
- `update(data, partial=True)` / `aupdate(data, partial=True)` - PATCH/PUT existing class/object
- `listing(name, issuer_id=..., resource_id=...)` / `alisting(...)` - List classes by issuer or objects by class
- `message(name, resource_id, message)` / `amessage(...)` - Send notification to class/object holders
- `save_link(models)` - Generate "Add to Wallet" JWT link (shared for sync/async)

**HTTP Client Pooling** (`clientpool.py`):
- Single `ClientPoolManager` class handles both sync and async operations with **persistent client pooling**
- **Connection Pooling**: HTTP clients are cached per credentials set and reused across API calls
- Sync: `client_pool.client()` returns cached AssertionClient (thread-safe)
- Async: `client_pool.async_client()` returns cached AsyncAssertionClient (task-safe)
- Clients persist for the application lifetime; call `close_all_clients()` or `aclose_all_clients()` at shutdown
- Automatic cleanup via `atexit` handler for sync clients
- Single `client_pool` singleton instance handles both sync and async

**Models** (`models/`):
- `passes/` - Top-level wallet classes/objects (Generic, GiftCard, Loyalty, Offer, EventTicket, Transit, etc.)
- `datatypes/` - Reusable field types (enums, barcodes, images, localized strings, etc.)
- `bases.py` - Base models (WithIdModel, ClassModel, ObjectModel)
- All models are Pydantic v2 with Google API field mappings

**Registry** (`registry.py`):
- Maps model names (e.g., "GenericClass") to model classes
- Stores metadata: `url_part`, `can_create`, `can_read`, `can_update`, `can_list`, `can_message`
- Use `lookup_model_by_name(name)` to get model class
- Use `lookup_metadata_by_name(name)` to get capabilities

**Utilities** (`utils.py`):
- `validate_data()` - Validate dict/Model against expected model type
- `validate_data_and_convert_to_json()` - Validate and serialize for API
- `handle_response_errors()` - Unified HTTP error handling
- `parse_response_json()` - Deserialize and validate API responses
- `encrypt_data()` / `decrypt_data()` - Fernet symmetric encryption
- `save_link(models)` - Generate "Add to Wallet" JWT link
- JWT helper functions: `_create_payload()`, `_create_claims()`, `_convert_str_or_datetime_to_str()`

**Handlers** (`handlers/`):
- `validate.py` - Google Wallet callback signature verification (sync + async)
- Uses elliptic curve cryptography to verify signed messages from Google

### Configuration

Settings loaded via Pydantic Settings from environment variables or files:

**Required for API operations**:
- `EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE` - Path to Google service account JSON
- `EDUTAP_WALLET_GOOGLE_TEST_ISSUER_ID` - Issuer ID for integration tests

**Optional**:
- `EDUTAP_WALLET_GOOGLE_ENVIRONMENT` - `"testing"` or `"production"` (default: testing)
- `EDUTAP_WALLET_GOOGLE_FERNET_ENCRYPTION_KEY` - For data encryption (generate with CLI)

Settings class: `src/edutap/wallet_google/settings.py`

## Testing Patterns

### Unit Tests
- Use `respx` for both sync and async API tests (see `test_api_sync.py` and `test_api_async.py`)
- Mock `client_pool.client()` or `client_pool.async_client()` to avoid real credentials
- All tests require complete model data (e.g., GenericObject needs `id`, `classId`, `state`)
- JWT tests are in `test_api_jwt.py`

### Integration Tests
- Marked with `@pytest.mark.integration`
- Excluded by default via `pytest-explicit` config
- Run with `--run-integration` flag
- See `tests/integration/test_CRULM.py` (sync) and `test_async_CRULM.py` (async)
- Test full CRUD lifecycle: Create, Read, Update, List, Message

## Key Patterns

### Model Registration
All top-level Google Wallet models use the `@register_model()` decorator:
```python
@register_model(
    "GenericClass",
    url_part="genericClass",
    plural="genericClasses",
    can_message=True,
)
class GenericClass(ClassModel):
    ...
```

### API Function Pattern
Most API functions accept a `name` parameter (registered model name):
```python
# Read by name + ID
result = read(name="GenericObject", resource_id="issuer.object.id")

# List by name + issuer/class
for obj in listing(name="GenericObject", resource_id="issuer.class.id"):
    ...
```

### Error Handling
- `ObjectAlreadyExistsException` - 409 on create
- `QuotaExceededException` - 403 with quota/rate keywords
- `WalletException` - General API errors
- `LookupError` - 404 not found

### Async vs Sync
Both sync and async functions are in the same `api` module with consistent naming:
- Sync: `from edutap.wallet_google import api` then `api.create(...)`, `api.read(...)`, etc.
- Async: `from edutap.wallet_google import api` then `await api.acreate(...)`, `await api.aread(...)`, etc.
- Shared: `api.new()` and `api.save_link()` work for both sync and async (no await needed)
- Both implementations use `httpx` + `authlib` for consistency

## Important Constraints

1. **No Delete Operation**: Google Wallet doesn't support deletion. Expire passes by updating with past `validTimeInterval.end`.

2. **ID Format**: IDs must follow pattern `{issuer_id}.{suffix}` where issuer_id is from Google Cloud project.

3. **Class Before Object**: Always create/update class before creating objects referencing it.

4. **Listing Restrictions**:
   - Classes: Must provide `issuer_id`
   - Objects: Must provide `resource_id` (class ID)
   - Cannot mix `issuer_id` and `resource_id`

5. **Message Capability**: Check `lookup_metadata_by_name(name)["can_message"]` before calling `message()`.

## Documentation

Full documentation at: https://docs.edutap.eu/packages/edutap_wallet_google/index.html

- **Tutorials**: Step-by-step guides for common tasks
- **Reference**: Complete API and model documentation
- **Explanation**: Architecture and design decisions

The docs follow the [Diátaxis](https://diataxis.fr/) framework.
- always use uv instead of pip
