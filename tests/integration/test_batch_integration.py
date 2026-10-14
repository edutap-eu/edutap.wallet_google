"""Integration test for Batch against the real Google Wallet API.

A 200 status inside a batch part is not by itself proof that the write
landed -- it only proves Google accepted the part. This test reads the
objects back afterwards to prove the attribute actually changed server-side.

Google Wallet objects cannot be deleted, so every id used here must be
unique per run (see ``integration_test_id``) and nothing is torn down
afterwards -- the created objects persist in the test issuer account.
"""

import pytest


@pytest.mark.integration
def test_batch_update_round_trip(integration_test_id):
    """Batch-update one attribute on two objects, then read both back.

    Creates a class and two GenericObjects (state=INACTIVE), sends one
    Batch with an update for each object (state=ACTIVE), asserts both
    results are ok, then reads both objects back and asserts the state
    change actually landed.
    """
    from edutap.wallet_google import api
    from edutap.wallet_google.clientpool import client_pool

    import time

    class_type = "GenericClass"
    object_type = "GenericObject"

    ############################
    # class, required as classId for the objects
    class_base = f"{integration_test_id}.{class_type}.test_batch.wallet_google.edutap"
    class_id = f"{client_pool.settings.test_issuer_id}.{class_base}"
    class_data = api.new(class_type, {"id": class_id})
    api.create(class_data)

    ############################
    # two objects to batch-update
    object_ids = [
        f"{client_pool.settings.test_issuer_id}."
        f"{integration_test_id}.{object_type}.test_batch.{n}.wallet_google.edutap"
        for n in (1, 2)
    ]
    for object_id in object_ids:
        object_data = api.new(
            object_type,
            {
                "id": object_id,
                "classId": class_id,
                "state": "INACTIVE",
            },
        )
        result_create = api.create(object_data)
        assert result_create is not None
        assert result_create.state == "INACTIVE"

    ############################
    # one batch request updating both objects' state
    batch = api.Batch()
    batch.add_updates(
        object_type,
        [{"id": object_id, "state": "ACTIVE"} for object_id in object_ids],
    )
    assert len(batch) == 2

    results = batch.execute()

    assert len(results) == 2
    for object_id, result in zip(object_ids, results):
        assert result.ok is True, (
            f"Batch update for '{object_id}' failed: "
            f"{result.error.message if result.error else 'unknown error'}"
        )
        assert result.resource_id == object_id
        assert result.body is not None
        assert result.body["state"] == "ACTIVE"

    # relax - not sure if this is necessary
    time.sleep(0.05)

    ############################
    # read both objects back -- the actual proof the write landed
    for object_id in object_ids:
        result_read = api.read(name=object_type, resource_id=object_id)
        assert result_read is not None
        assert result_read.state == "ACTIVE"
