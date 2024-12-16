def test_api_save_link(mock_settings):
    from edutap.wallet_google.settings import ROOT_DIR

    mock_settings.issuer_id = "1234567890123456789"
    mock_settings.credentials_file = (
        ROOT_DIR / "tests" / "data" / "credentials_fake.json"
    )

    from edutap.wallet_google import api

    link = api.save_link(
        [
            api.new(
                "Reference", {"id": "test-1.edutap.eu", "model_name": "GenericObject"}
            ),
            api.new(
                "OfferObject",
                {"id": "test-2.edutap.eu", "classId": "test-class-1.edutap.eu"},
            ),
        ]
    )
    assert (
        link
        == "https://pay.google.com/gp/v/save/eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJSUzI1NiIsICJraWQiOiAiMTIzNDU2Nzg5MGFiY2RlZjEyMzQ1Njc4OTBhYmNkZWYxMjM0NTY3OCJ9.eyJpc3MiOiAiZWR1dGFwLXRlc3QtZXhhbXBsZUBzb2RpdW0tcmF5LTEyMzQ1Ni5pYW0uZ3NlcnZpY2VhY2NvdW50LmNvbSIsICJhdWQiOiAiZ29vZ2xlIiwgInR5cCI6ICJzYXZldHRvd2FsbGV0IiwgImlhdCI6ICIiLCAicGF5bG9hZCI6IHsib2ZmZXJPYmplY3RzIjogW3siaWQiOiAidGVzdC0yLmVkdXRhcC5ldSIsICJjbGFzc0lkIjogInRlc3QtY2xhc3MtMS5lZHV0YXAuZXUiLCAic3RhdGUiOiAiU1RBVEVfVU5TUEVDSUZJRUQiLCAiaGFzTGlua2VkRGV2aWNlIjogZmFsc2UsICJkaXNhYmxlRXhwaXJhdGlvbk5vdGlmaWNhdGlvbiI6IGZhbHNlLCAibm90aWZ5UHJlZmVyZW5jZSI6ICJOT1RJRklDQVRJT05fU0VUVElOR1NfRk9SX1VQREFURVNfVU5TUEVDSUZJRUQifV0sICJnZW5lcmljT2JqZWN0cyI6IFt7ImlkIjogInRlc3QtMS5lZHV0YXAuZXUifV19LCAib3JpZ2lucyI6IFtdfQ.LEPJBlt7ic9cPWKUvpoxUWe5yvdK0_kqPlBFkHmqFBfO5eeYN-owTHCElCGhnHeE730D4U3XjQWeZXfcaEAQcdBKB8udoT2Tja7Rw_M8M18kpBrSdGDRKT_uXG_-RkG3uVB30Lu5otlJiX2VOJWg9H6NR7wD_pfUt67cLjiBeMILuIVi-h0CDUV0dObEjnOHrRhj6KeKdfqq6izwwmw4iSQxsaQrDxWZtwCZ__pV5UK54Od6-lNrsBQwz241SDYv9kJTXrImrjRZXdoht6xgwqxg-GcuqUJgcczG-TLyN_9aI4FtA2cz8PCXyKPXnd-_HTe9nohi05dfMDeVWsmP6g"
    )
