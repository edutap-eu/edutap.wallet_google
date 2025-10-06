# Tutorials

We prepared several tutorials to get you started with the Google Wallet API.

Before starting, follow the [installation and configuration instructions](installation.md).

**Note:** All examples use the synchronous API (`api`). For async operations with FastAPI or other async frameworks, use `api_async` with the same function signatures but with `async`/`await`.

## Create a pass and load it into the Google Wallet


In this tutorial you will
- create a Wallet Class (a template),
- a Wallet Object (the pass) based on the Wallet Class and
- create a save link to download the pass to the Google Wallet form your mobile device.

We start with a simple example, a generic pass with a title and a header.

At first we create the most simple Wallet Class.

```python
from edutap.wallet_google import api

import os

# if you run the code more than once, you need to change the ID of the class,
# like by incrementing the number part.
class_id = f"{os.environ.get('EDUTAP_WALLET_GOOGLE_ISSUER_ID')}.example_class01.edutap_example"

# Option 1: Create with dict
new_class = api.create(
    api.new("GenericClass", {"id": class_id})
)

# Option 2: Create with dict directly (also works)
new_class = api.create(
    api.new("GenericClass", {
        "id": class_id,
    })
)
```

Now we create a simple Wallet Object based on the freshly created class.

```python
# if you run the code more than once, you need to change the ID of the object
object_id = f"{os.environ.get('EDUTAP_WALLET_GOOGLE_ISSUER_ID')}.example_object01.edutap_example"

new_object = api.create(
    api.new("GenericObject", {
        "id": object_id,
        "classId": class_id,
        "cardTitle": {
            "defaultValue": {
                "language": "en",
                "value": "Edutap Example Pass 01"
            },
            "translatedValues": []
        },
        "header": {
            "defaultValue": {
                "language": "en",
                "value": "This is an example pass from the edutap tutorial."
            },
            "translatedValues": []
        },
        "state": "ACTIVE"
    })
)
```

Now we can create a save link for downloading the pass.
The save link encodes the pass data in a JWT and creates/updates the pass when the link is opened.

```python
from edutap.wallet_google.models.datatypes.jwt import Reference

# Option 1: Embed the full object in the link (creates/updates on link open)
# The object data is encoded in the JWT, so the pass is created when user clicks the link
link = api.save_link(
    [new_object],
    origins=["www.example.com"],
)

# Option 2: Reference an existing pass by ID (pass must already exist)
# Only the ID is in the JWT, the pass must be created via api.create() first
link = api.save_link(
    [Reference(id=object_id, model_name="GenericObject")],
    origins=["www.example.com"],
)

print(link)
```

**Important:**
- **Option 1** encodes the full pass data in the link. When clicked, Google Wallet creates or updates the pass automatically. Use this for on-the-fly pass creation.
- **Option 2** only references a pass ID. The pass must already exist (created via `api.create()` beforehand). Use this for passes that are managed server-side.

The link can be opened on a mobile device to download the pass to the Google Wallet.
It can also be opened in the desktop browser if logged in with the same Google account as on your mobile device.

## Update a class

To update an existing class, use the `update()` function. You can do a partial update (default) or a full replacement.

```python
# Read the existing class
existing_class = api.read("GenericClass", class_id)

# Partial update (only updates specified fields)
updated_class = api.update(
    api.new("GenericClass", {
        "id": class_id,
        "heroImage": {
            "sourceUri": {
                "uri": "https://example.com/hero.png"
            }
        }
    }),
    partial=True  # default
)

# Full replacement (replaces entire object)
updated_class = api.update(
    api.new("GenericClass", {
        "id": class_id,
        # ... all required fields ...
    }),
    partial=False
)
```

## Update a pass

Updating a pass (object) works the same way as updating a class:

```python
# Partial update to change the state
updated_object = api.update(
    api.new("GenericObject", {
        "id": object_id,
        "state": "EXPIRED"
    }),
    partial=True
)

# Update multiple fields
updated_object = api.update(
    api.new("GenericObject", {
        "id": object_id,
        "header": {
            "defaultValue": {
                "language": "en",
                "value": "Updated header text"
            }
        },
        "validTimeInterval": {
            "end": {
                "date": "2024-12-31T23:59:59"
            }
        }
    }),
    partial=True
)
```

## Send a notification to a pass

You can send messages to passes to notify users about updates or important information:

```python
from edutap.wallet_google.models.datatypes.message import Message

# Send a simple notification
result = api.message(
    "GenericObject",
    object_id,
    Message(
        header="Important Update",
        body="Your pass has been updated with new information."
    )
)

# Send with custom message type
result = api.message(
    "GenericObject",
    object_id,
    {
        "header": "Expiring Soon",
        "body": "This pass will expire in 7 days.",
        "messageType": "EXPIRATION_NOTIFICATION"
    }
)
```

**Note:** Messages appear as notifications on the user's device and in the Google Wallet app.

## Disable a pass

To disable a pass, update its state to `INACTIVE` or `EXPIRED`:

```python
# Mark as inactive (can be reactivated later)
api.update(
    api.new("GenericObject", {
        "id": object_id,
        "state": "INACTIVE"
    }),
    partial=True
)

# Mark as expired (permanent)
api.update(
    api.new("GenericObject", {
        "id": object_id,
        "state": "EXPIRED"
    }),
    partial=True
)
```

**States:**
- `ACTIVE`: Pass is active and usable
- `INACTIVE`: Pass is temporarily disabled (can be reactivated)
- `EXPIRED`: Pass is permanently expired
- `COMPLETED`: Pass has been used/redeemed

## List passes

You can list all passes (objects) for a given class or all classes for an issuer:

```python
import os

issuer_id = os.environ.get('EDUTAP_WALLET_GOOGLE_ISSUER_ID')

# List all classes for an issuer
for wallet_class in api.listing("GenericClass", issuer_id=issuer_id):
    print(f"Class: {wallet_class.id}")

# List all objects for a specific class
for wallet_object in api.listing("GenericObject", resource_id=class_id):
    print(f"Object: {wallet_object.id}, State: {wallet_object.state}")

# Paginated listing (manual pagination)
page_size = 10
next_token = None
while True:
    results = list(api.listing(
        "GenericObject",
        resource_id=class_id,
        result_per_page=page_size,
        next_page_token=next_token
    ))

    # Process objects (all but potentially last item which is the token)
    for item in results:
        if isinstance(item, str):
            next_token = item  # This is the next page token
        else:
            print(f"Object: {item.id}")

    # Check if there's a next page
    if not next_token or next_token == results[-1]:
        break
```

**Note:** Without `result_per_page`, the generator automatically fetches all pages.

## Using the Async API

All the examples above can be used with the async API by replacing `api` with `api_async` and adding `async`/`await`:

```python
from edutap.wallet_google import api_async
import asyncio

async def create_pass():
    """Example async function to create a pass."""
    class_id = f"{os.environ.get('EDUTAP_WALLET_GOOGLE_ISSUER_ID')}.async_example"

    # Create class
    new_class = await api_async.create(
        api_async.new("GenericClass", {"id": class_id})
    )

    # Create object
    object_id = f"{class_id}.object01"
    new_object = await api_async.create(
        api_async.new("GenericObject", {
            "id": object_id,
            "classId": class_id,
            "state": "ACTIVE"
        })
    )

    # Read
    fetched = await api_async.read("GenericObject", object_id)

    # Update
    updated = await api_async.update(
        api_async.new("GenericObject", {
            "id": object_id,
            "state": "EXPIRED"
        }),
        partial=True
    )

    # Send message
    result = await api_async.message(
        "GenericObject",
        object_id,
        {"header": "Test", "body": "Async message"}
    )

    # List (using async generator)
    async for obj in api_async.listing("GenericObject", resource_id=class_id):
        print(f"Found: {obj.id}")

# Run the async function
asyncio.run(create_pass())
```

**Use async API when:**
- Working with async frameworks (FastAPI, aiohttp, etc.)
- Making multiple concurrent API calls
- Need non-blocking I/O operations

**Note:** `save_link()` is only available in the synchronous API as it uses synchronous JWT signing.
