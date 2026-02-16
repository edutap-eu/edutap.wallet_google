import pytest


def test_reference_validator_missing():
    import pydantic

    from edutap.wallet_google.models.passes.bases import Reference

    with pytest.raises(pydantic.ValidationError):
        Reference(id="1234")


def test_reference_validator_both():
    import pydantic

    from edutap.wallet_google.models.passes.bases import Reference
    from edutap.wallet_google.models.passes.generic import GenericObject

    with pytest.raises(pydantic.ValidationError):
        Reference(id="1234", model_name="GenericObject", model_type=GenericObject)


def test_loyality_LoyaltyPointsBalance_validator_OK():
    from edutap.wallet_google.models.datatypes.loyalty import LoyaltyPointsBalance
    from edutap.wallet_google.models.datatypes.money import Money

    LoyaltyPointsBalance(string="1234")
    LoyaltyPointsBalance(int=1234)
    LoyaltyPointsBalance(double=1234.00)
    LoyaltyPointsBalance(money=Money(micros="123400", currencyCode="USD"))


def test_loyality_LoyaltyPointsBalance_validator_failures():
    import pydantic

    from edutap.wallet_google.models.datatypes.loyalty import LoyaltyPointsBalance
    from edutap.wallet_google.models.datatypes.money import Money

    # at least one
    with pytest.raises(pydantic.ValidationError):
        LoyaltyPointsBalance()

    # not 2
    with pytest.raises(pydantic.ValidationError):
        LoyaltyPointsBalance(int=1234, string="1234")

    # not 3
    with pytest.raises(pydantic.ValidationError):
        LoyaltyPointsBalance(int=1234, string="1234", double=1234.00)

    # not 4
    with pytest.raises(pydantic.ValidationError):
        LoyaltyPointsBalance(
            int=1234,
            string="1234",
            double=1234.00,
            money=Money(
                micros="123400",
                currencyCode="USD",
            ),
        )


# TransitObject validators tests


def test_transit_object_concession_category_ok():
    """Test valid cases for concession category fields."""
    from edutap.wallet_google.models.datatypes.enums import ConcessionCategory
    from edutap.wallet_google.models.datatypes.general import LocalizedString
    from edutap.wallet_google.models.passes.tickets_and_transit import TransitObject

    # Only default concessionCategory (UNSPECIFIED), no customConcessionCategory
    obj = TransitObject(id="issuer.obj1", classId="issuer.class1")
    assert obj.concessionCategory == ConcessionCategory.CONCESSION_CATEGORY_UNSPECIFIED
    assert obj.customConcessionCategory is None

    # Only concessionCategory set (non-default), no customConcessionCategory
    obj = TransitObject(
        id="issuer.obj2",
        classId="issuer.class1",
        concessionCategory=ConcessionCategory.ADULT,
    )
    assert obj.concessionCategory == ConcessionCategory.ADULT
    assert obj.customConcessionCategory is None

    # Only customConcessionCategory set, concessionCategory stays UNSPECIFIED
    obj = TransitObject(
        id="issuer.obj3",
        classId="issuer.class1",
        customConcessionCategory=LocalizedString(
            defaultValue={"language": "en", "value": "Student"}
        ),
    )
    assert obj.concessionCategory == ConcessionCategory.CONCESSION_CATEGORY_UNSPECIFIED
    assert obj.customConcessionCategory is not None


def test_transit_object_concession_category_fails():
    """Test that setting both concessionCategory and customConcessionCategory raises error."""
    import pydantic

    from edutap.wallet_google.models.datatypes.enums import ConcessionCategory
    from edutap.wallet_google.models.datatypes.general import LocalizedString
    from edutap.wallet_google.models.passes.tickets_and_transit import TransitObject

    # Both concessionCategory (non-default) and customConcessionCategory set
    with pytest.raises(pydantic.ValidationError):
        TransitObject(
            id="issuer.obj1",
            classId="issuer.class1",
            concessionCategory=ConcessionCategory.ADULT,
            customConcessionCategory=LocalizedString(
                defaultValue={"language": "en", "value": "Student"}
            ),
        )


def test_transit_object_ticket_leg_ok():
    """Test valid cases for ticketLeg/ticketLegs fields."""
    from edutap.wallet_google.models.datatypes.transit import TicketLeg
    from edutap.wallet_google.models.passes.tickets_and_transit import TransitObject

    # Neither ticketLeg nor ticketLegs set
    obj = TransitObject(id="issuer.obj1", classId="issuer.class1")
    assert obj.ticketLeg is None
    assert obj.ticketLegs is None

    # Only ticketLeg set
    obj = TransitObject(
        id="issuer.obj2",
        classId="issuer.class1",
        ticketLeg=TicketLeg(),
    )
    assert obj.ticketLeg is not None
    assert obj.ticketLegs is None

    # Only ticketLegs set
    obj = TransitObject(
        id="issuer.obj3",
        classId="issuer.class1",
        ticketLegs=[TicketLeg(), TicketLeg()],
    )
    assert obj.ticketLeg is None
    assert obj.ticketLegs is not None


def test_transit_object_ticket_leg_fails():
    """Test that setting both ticketLeg and ticketLegs raises error."""
    import pydantic

    from edutap.wallet_google.models.datatypes.transit import TicketLeg
    from edutap.wallet_google.models.passes.tickets_and_transit import TransitObject

    # Both ticketLeg and ticketLegs set
    with pytest.raises(pydantic.ValidationError):
        TransitObject(
            id="issuer.obj1",
            classId="issuer.class1",
            ticketLeg=TicketLeg(),
            ticketLegs=[TicketLeg()],
        )
