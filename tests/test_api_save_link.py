def test_api_save_link():
    from edutap.wallet_google.api import save_link
    from edutap.wallet_google.models.datatypes.jwt import Reference
    from edutap.wallet_google.models.passes.retail import OfferClass
    from edutap.wallet_google.models.passes.retail import OfferObject

    link = save_link(
        [
            Reference(id="test-1.edutap.eu", model_name="GenericObject"),
            OfferObject(id="test-2.edutap.eu", classId="test-class-1.edutap.eu"),
        ]
    )
    assert link == "https://walletobjects.googleapis.com/walletobjects/v1/jwt/eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJSUzI1NiIsICJraWQiOiAiZThjMTFjZDI0ZmVjYTE1ZjViMzNmMjhiZjNiOWQ0MmUyZjE4ZTM2MSJ9.eyJpc3MiOiAiZWR1dGFwLXdhbGxldC1hcGlAZWR1dGFwLTQwMTgxMS5pYW0uZ3NlcnZpY2VhY2NvdW50LmNvbSIsICJhdWQiOiAiZ29vZ2xlIiwgInR5cCI6ICJzYXZldHRvd2FsbGV0IiwgImlhdCI6ICIiLCAicGF5bG9hZCI6IHsib2ZmZXJPYmplY3RzIjogW3siaWQiOiAidGVzdC0yLmVkdXRhcC5ldSIsICJjbGFzc0lkIjogInRlc3QtY2xhc3MtMS5lZHV0YXAuZXUiLCAic3RhdGUiOiAiU1RBVEVfVU5TUEVDSUZJRUQiLCAiaGFzTGlua2VkRGV2aWNlIjogZmFsc2UsICJkaXNhYmxlRXhwaXJhdGlvbk5vdGlmaWNhdGlvbiI6IGZhbHNlLCAibm90aWZ5UHJlZmVyZW5jZSI6ICJOT1RJRklDQVRJT05fU0VUVElOR1NfRk9SX1VQREFURVNfVU5TUEVDSUZJRUQifV0sICJnZW5lcmljT2JqZWN0cyI6IFt7ImlkIjogInRlc3QtMS5lZHV0YXAuZXUifV19LCAib3JpZ2lucyI6IFtdfQ.IHyJZ3Vuz9lMB6LRbihdljdQBKqYajLp1dPESZF0TJ57x1Sc4doWoTlNJtYC36qE65NJgi2MQnP0NoKXCt2b9ZNCGkqiH5Sz-yGZ8xTpbrP_juZAfIEMOW6x17uWA6_Hed4AywXEdl-b7Whq8YY8hgodRJy330V5U5lMaVb0j6uPUjTI-bj_xWleCVr-JY4BRTvBKsIiVt94jwLED3F023KjNodOgIenLHtGdsxHp8fE9O889Tn16SvEo9zrJZXao0YBUdUDuXrHxKwCYH6JKG4LfjmS1F-JKj5Lx7ebBLudBLsFweIINMp3Y7JKV_5jGhjPDYIsJdnN7aj5bA9Icg"