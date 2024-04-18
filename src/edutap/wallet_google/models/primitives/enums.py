from enum import Enum


class CamelCaseAliasEnum(Enum):
    """Add an value alias in camelcase to the enum,
    given the value in snakecase.

    example: a enum like

    class FooExample(CamelCaseAliasEnum):
        FOO_BAR_BAZ = "FOO_BAR_BAZ"

    can be looked up like this:

    FooExample("fooBarBaz")

    """

    def __new__(cls: type["CamelCaseAliasEnum"], value: str) -> "CamelCaseAliasEnum":
        obj: "CamelCaseAliasEnum" = object.__new__(cls)
        parts = value.lower().split("_")
        camel = "".join(
            [(x.capitalize() if count != 0 else x) for count, x in enumerate(parts)]
        )
        
        # create a second object with the camelcase name
        # creating an alias only does not work out since
        # pydantic checks for the value in the enum and not only the name
        camel_obj= object.__new__(cls)
        camel_obj._value_ = camel
        cls._value2member_map_[camel] = camel_obj
        cls._member_map_[camel] = camel_obj
        cls._member_names_.append(camel)
        return obj


class Action(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/smarttap#action
    """

    ACTION_UNSPECIFIED = "ACTION_UNSPECIFIED"
    S2AP = "S2AP"
    SIGN_UP = "SIGN_UP"


class AnimationType(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/SecurityAnimation#animationtype
    """

    ANIMATION_UNSPECIFIED = "ANIMATION_UNSPECIFIED"
    FOIL_SHIMMER = "FOIL_SHIMMER"


class BarcodeRenderEncoding(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/BarcodeRenderEncoding
    """

    RENDER_ENCODING_UNSPECIFIED = "RENDER_ENCODING_UNSPECIFIED"
    UTF_8 = "UTF_8"


class BarcodeType(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/BarcodeType
    """

    BARCODE_TYPE_UNSPECIFIED = "BARCODE_TYPE_UNSPECIFIED"
    AZTEC = "AZTEC"
    CODE_39 = "CODE_39"
    CODE_128 = "CODE_128"
    CODABAR = "CODABAR"
    DATA_MATRIX = "DATA_MATRIX"
    EAN_8 = "EAN_8"
    EAN_13 = "EAN_13"
    ITF_14 = "ITF_14"
    PDF_417 = "PDF_417"
    QR_CODE = "QR_CODE"
    UPC_A = "UPC_A"
    TEXT_ONLY = "TEXT_ONLY"


class ConfirmationCodeLabel(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#confirmationcodelabel
    """

    CONFIRMATION_CODE_LABEL_UNSPECIFIED = "CONFIRMATION_CODE_LABEL_UNSPECIFIED"
    CONFIRMATION_CODE = "CONFIRMATION_CODE"
    CONFIRMATION_NUMBER = "CONFIRMATION_NUMBER"
    ORDER_NUMBER = "ORDER_NUMBER"
    RESERVATION_NUMBER = "RESERVATION_NUMBER"


class DateFormat(CamelCaseAliasEnum):
    DATE_FORMAT_UNSPECIFIED = "DATE_FORMAT_UNSPECIFIED"
    DATE_TIME = "DATE_TIME"
    DATE_ONLY = "DATE_ONLY"
    TIME_ONLY = "TIME_ONLY"
    DATE_TIME_YEAR = "DATE_TIME_YEAR"
    DATE_YEAR = "DATE_YEAR"


class DoorsOpenLabel(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#doorsopenlabel
    """

    DOORS_OPEN_LABEL_UNSPECIFIED = "DOORS_OPEN_LABEL_UNSPECIFIED"
    DOORS_OPEN = "DOORS_OPEN"
    GATES_OPEN = "GATES_OPEN"


class GateLabel(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#gatelabel
    """

    GATE_LABEL_UNSPECIFIED = "GATE_LABEL_UNSPECIFIED"
    GATE = "GATE"
    DOOR = "DOOR"
    ENTRANCE = "ENTRANCE"


class GenericType(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/genericobject#generictype
    """

    GENERIC_TYPE_UNSPECIFIED = "GENERIC_TYPE_UNSPECIFIED"  # Unspecified generic type.
    GENERIC_SEASON_PASS = "GENERIC_SEASON_PASS"  # Season pass
    GENERIC_UTILITY_BILLS = "GENERIC_UTILITY_BILLS"  # Utility bills
    GENERIC_PARKING_PASS = "GENERIC_PARKING_PASS"  # Parking pass
    GENERIC_VOUCHER = "GENERIC_VOUCHER"  # Voucher
    GENERIC_GYM_MEMBERSHIP = "GENERIC_GYM_MEMBERSHIP"  # Gym membership cards
    GENERIC_LIBRARY_MEMBERSHIP = (
        "GENERIC_LIBRARY_MEMBERSHIP"  # Library membership cards
    )
    GENERIC_RESERVATIONS = "GENERIC_RESERVATIONS"  # Reservations
    GENERIC_AUTO_INSURANCE = "GENERIC_AUTO_INSURANCE"  # Auto-insurance cards
    GENERIC_HOME_INSURANCE = "GENERIC_HOME_INSURANCE"  # Home-insurance cards
    GENERIC_ENTRY_TICKET = "GENERIC_ENTRY_TICKET"  # Entry tickets
    GENERIC_RECEIPT = "GENERIC_RECEIPT"  # Receipts
    GENERIC_OTHER = "GENERIC_OTHER"  # Other type


class MessageType(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/Message#messagetype
    """

    MESSAGE_TYPE_UNSPECIFIED = "MESSAGE_TYPE_UNSPECIFIED"
    TEXT = "TEXT"
    TEXT_AND_NOTIFY = "TEXT_AND_NOTIFY"
    EXPIRATION_NOTIFICATION = "EXPIRATION_NOTIFICATION"


class MultipleDevicesAndHoldersAllowedStatus(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/MultipleDevicesAndHoldersAllowedStatus
    """

    STATUS_UNSPECIFIED = "STATUS_UNSPECIFIED"
    MULTIPLE_HOLDERS = "MULTIPLE_HOLDERS"
    ONE_USER_ALL_DEVICES = "ONE_USER_ALL_DEVICES"
    ONE_USER_ONE_DEVICE = "ONE_USER_ONE_DEVICE"


class NfcConstraint(CamelCaseAliasEnum):
    """
    see:
    """

    NFC_CONSTRAINT_UNSPECIFIED = "NFC_CONSTRAINT_UNSPECIFIED"
    BLOCK_PAYMENT = "BLOCK_PAYMENT"
    BLOCK_CLOSED_LOOP_TRANSIT = "BLOCK_CLOSED_LOOP_TRANSIT"


class PredefinedItem(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/retail/offers/rest/v1/ClassTemplateInfo#predefineditem
    """

    PREDEFINED_ITEM_UNSPECIFIED = "PREDEFINED_ITEM_UNSPECIFIED"
    FREQUENT_FLYER_PROGRAM_NAME_AND_NUMBER = "FREQUENT_FLYER_PROGRAM_NAME_AND_NUMBER"
    FLIGHT_NUMBER_AND_OPERATING_FLIGHT_NUMBER = (
        "FLIGHT_NUMBER_AND_OPERATING_FLIGHT_NUMBER"
    )


class RedemptionChannel(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/retail/offers/rest/v1/offerclass#OfferClass.RedemptionChannel
    """

    REDEMPTION_CHANNEL_UNSPECIFIED = "REDEMPTION_CHANNEL_UNSPECIFIED"
    INSTORE = "INSTORE"
    ONLINE = "ONLINE"
    BOTH = "BOTH"
    TEMPORARY_PRICE_REDUCTION = "TEMPORARY_PRICE_REDUCTION"


class ReviewStatus(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/ReviewStatus
    """

    REVIEW_STATUS_UNSPECIFIED = "REVIEW_STATUS_UNSPECIFIED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DRAFT = "DRAFT"


class Role(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/permissions#role
    """

    ROLE_UNSPECIFIED = "ROLE_UNSPECIFIED"
    OWNER = "OWNER"
    READER = "READER"
    WRITER = "WRITER"


class RowLabel(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#rowlabel
    """

    ROW_LABEL_UNSPECIFIED = "ROW_LABEL_UNSPECIFIED"
    ROW = "ROW"


class ScreenshotEligibility(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/PassConstraints#screenshoteligibility
    """

    SCREENSHOT_ELIGIBILITY_UNSPECIFIED = "SCREENSHOT_ELIGIBILITY_UNSPECIFIED"
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"


class SeatLabel(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#seatlabel
    """

    SEAT_LABEL_UNSPECIFIED = "SEAT_LABEL_UNSPECIFIED"
    SEAT = "SEAT"


class SectionLabel(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#sectionlabel
    """

    SECTION_LABEL_UNSPECIFIED = "SECTION_LABEL_UNSPECIFIED"
    SECTION = "SECTION"
    THEATER = "THEATER"


class SharedDataType(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyclass#shareddatatype
    """

    SHARED_DATA_TYPE_UNSPECIFIED = "SHARED_DATA_TYPE_UNSPECIFIED"
    FIRST_NAME = "FIRST_NAME"
    LAST_NAME = "LAST_NAME"
    STREET_ADDRESS = "STREET_ADDRESS"  # single line address field
    ADDRESS_LINE_1 = "ADDRESS_LINE_1"  # multi line address fields
    ADDRESS_LINE_2 = "ADDRESS_LINE_2"
    ADDRESS_LINE_3 = "ADDRESS_LINE_3"
    CITY = "CITY"
    STATE = "STATE"
    ZIPCODE = "ZIPCODE"
    COUNTRY = "COUNTRY"
    EMAIL = "EMAIL"
    PHONE = "PHONE"


class State(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/State
         https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/State
    """

    STATE_UNSPECIFIED = "STATE_UNSPECIFIED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"
    INACTIVE = "INACTIVE"


class RetailState(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyclass#state
    """

    STATE_UNSPECIFIED = "STATE_UNSPECIFIED"
    TRUSTED_TESTERS = "TRUSTED_TESTERS"
    LIVE = "LIVE"
    DISABLED = "DISABLED"


class TotpAlgorithm(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/RotatingBarcode#totpalgorithm
    """

    TOTP_ALGORITHM_UNSPECIFIED = "TOTP_ALGORITHM_UNSPECIFIED"
    TOTP_SHA1 = "TOTP_SHA1"


class TransitOption(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#transitoption
    """

    TRANSIT_OPTION_UNSPECIFIED = "TRANSIT_OPTION_UNSPECIFIED"
    ORIGIN_AND_DESTINATION_NAMES = "ORIGIN_AND_DESTINATION_NAMES"
    ORIGIN_AND_DESTINATION_CODES = "ORIGIN_AND_DESTINATION_CODES"
    ORIGIN_NAME = "ORIGIN_NAME"


class ViewUnlockRequirement(CamelCaseAliasEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ViewUnlockRequirement
    """

    VIEW_UNLOCK_REQUIREMENT_UNSPECIFIED = "VIEW_UNLOCK_REQUIREMENT_UNSPECIFIED"
    UNLOCK_NOT_REQUIRED = "UNLOCK_NOT_REQUIRED"
    UNLOCK_REQUIRED_TO_VIEW = "UNLOCK_REQUIRED_TO_VIEW"
