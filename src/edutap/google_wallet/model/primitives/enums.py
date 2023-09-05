from enum import StrEnum


class Action(StrEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/smarttap#action
    """

    ACTION_UNSPECIFIED = "ACTION_UNSPECIFIED"
    S2AP = "S2AP"
    s2ap = "s2ap"  # deprecated value
    SIGN_UP = "SIGN_UP"
    signUp = "signUp"  # deprecated value


class AnimationType(StrEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/SecurityAnimation#animationtype
    """

    ANIMATION_UNSPECIFIED = "ANIMATION_UNSPECIFIED"
    animationUnspecified = "animationUnspecified"  # deprecated value
    FOIL_SHIMMER = "FOIL_SHIMMER"
    foilShimmer = "foilShimmer"  # deprecated value


class BarcodeRenderEncoding(StrEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/BarcodeRenderEncoding
    """

    RENDER_ENCODING_UNSPECIFIED = "RENDER_ENCODING_UNSPECIFIED"
    renderEncodingUnspecified = (
        "renderEncodingUnspecified"  # deprecated value - not documented
    )

    UTF_8 = "UTF_8"


class BarcodeType(StrEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/BarcodeType
    """

    BARCODE_TYPE_UNSPECIFIED = "BARCODE_TYPE_UNSPECIFIED"
    AZTEC = "AZTEC"
    aztec = "aztec"  # deprecated value
    CODE_39 = "CODE_39"
    code39 = "code39"  # deprecated value
    CODE_128 = "CODE_128"
    code128 = "code128"  # deprecated value
    CODABAR = "CODABAR"
    codabar = "codarbar"  # deprecated value
    DATA_MATRIX = "DATA_MATRIX"
    dataMatrix = "dataMatrix"  # deprecated value
    EAN_8 = "EAN_8"
    ean8 = "ean8"  # deprecated value
    EAN_13 = "EAN_13"
    ean13 = "ean13"  # deprecated value
    ITF_14 = "ITF_14"
    itf14 = "itf14"  # deprecated value
    PDF_417 = "PDF_417"
    pdf417 = "pdf417"  # deprecated value
    QR_CODE = "QR_CODE"
    qrCode = "qrCode"  # deprecated value
    UPC_A = "UPC_A"
    upcA = "upcA"  # deprecated value
    TEXT_ONLY = "TEXT_ONLY"
    textOnly = "textOnly"  # deprecated value


class ConfirmationCodeLabel(StrEnum):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#confirmationcodelabel
    """

    CONFIRMATION_CODE_LABEL_UNSPECIFIED = "CONFIRMATION_CODE_LABEL_UNSPECIFIED"
    CONFIRMATION_CODE = "CONFIRMATION_CODE"
    confirmationCode = "confirmationCode"
    CONFIRMATION_NUMBER = "CONFIRMATION_NUMBER"
    confirmationNumber = "confirmationNumber"
    ORDER_NUMBER = "ORDER_NUMBER"
    orderNumber = "orderNumber"
    RESERVATION_NUMBER = "RESERVATION_NUMBER"
    reservationNumber = "reservationNumb"


class DateFormat(StrEnum):
    DATE_FORMAT_UNSPECIFIED = "DATE_FORMAT_UNSPECIFIED"
    DATE_TIME = "DATE_TIME"
    DATE_ONLY = "DATE_ONLY"
    TIME_ONLY = "TIME_ONLY"
    DATE_TIME_YEAR = "DATE_TIME_YEAR"
    DATE_YEAR = "DATE_YEAR"


class DoorsOpenLabel(StrEnum):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#doorsopenlabel
    """

    DOORS_OPEN_LABEL_UNSPECIFIED = "DOORS_OPEN_LABEL_UNSPECIFIED"
    DOORS_OPEN = "DOORS_OPEN"
    doorsOpen = "doorsOpen"  # deprecated value
    GATES_OPEN = "GATES_OPEN"
    gatesOpen = "gatesOpen"  # deprecated value


class GateLabel(StrEnum):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#gatelabel
    """

    GATE_LABEL_UNSPECIFIED = "GATE_LABEL_UNSPECIFIED"
    GATE = "GATE"
    gate = "gate"
    DOOR = "DOOR"
    door = "door"
    ENTRANCE = "ENTRANCE"
    entrance = "entrance"


class GenericType(StrEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/genericobject#generictype
    """

    GENERIC_TYPE_UNSPECIFIED = "GENERIC_TYPE_UNSPECIFIED"  # Unspecified generic type.
    genericTypeUnspecified = (
        "genericTypeUnspecified"  # deprecated value - not documented
    )
    GENERIC_SEASON_PASS = "GENERIC_SEASON_PASS"  # Season pass
    GENERIC_UTILITY_BILLS = "GENERIC_UTILITY_BILLS"  # Utility bills
    GENERIC_PARKING_PASS = "GENERIC_PARKING_PASS"  # Parking pass
    GENERIC_VOUCHER = "GENERIC_VOUCHER"  # Voucher
    GENERIC_GYM_MEMBERSHIP = "GENERIC_GYM_MEMBERSHIP"  # Gym membership cards
    GENERIC_LIBRARY_MEMBERSHIP = (
        "GENERIC_LIBRARY_MEMBERSHIP"  # Library membership cards
    )
    genericLibraryMembership = "genericLibraryMembership"
    GENERIC_RESERVATIONS = "GENERIC_RESERVATIONS"  # Reservations
    GENERIC_AUTO_INSURANCE = "GENERIC_AUTO_INSURANCE"  # Auto-insurance cards
    GENERIC_HOME_INSURANCE = "GENERIC_HOME_INSURANCE"  # Home-insurance cards
    GENERIC_ENTRY_TICKET = "GENERIC_ENTRY_TICKET"  # Entry tickets
    GENERIC_RECEIPT = "GENERIC_RECEIPT"  # Receipts
    GENERIC_OTHER = "GENERIC_OTHER"  # Other type


class MessageType(StrEnum):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/Message#messagetype
    """

    MESSAGE_TYPE_UNSPECIFIED = "MESSAGE_TYPE_UNSPECIFIED"
    TEXT = "TEXT"
    text = "text"  # deprecated value
    EXPIRATION_NOTIFICATION = "EXPIRATION_NOTIFICATION"
    expirationNotification = "expirationNotification"  # deprecated value


class MultipleDevicesAndHoldersAllowedStatus(StrEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/MultipleDevicesAndHoldersAllowedStatus
    """

    STATUS_UNSPECIFIED = "STATUS_UNSPECIFIED"
    statusUnspecified = "statusUnspecified"  # deprecated value - not documented
    MULTIPLE_HOLDERS = "MULTIPLE_HOLDERS"
    multipleHolders = "multipleHolders"  # deprecated value
    ONE_USER_ALL_DEVICES = "ONE_USER_ALL_DEVICES"
    oneUserAllDevices = "oneUserAllDevices"  # deprecated value
    ONE_USER_ONE_DEVICE = "ONE_USER_ONE_DEVICE"
    oneUserOneDevice = "oneUserOneDevice"  # deprecated value


class NfcConstraint(StrEnum):
    """
    see:
    """

    NFC_CONSTRAINT_UNSPECIFIED = "NFC_CONSTRAINT_UNSPECIFIED"
    NfcConstraintUnspecified = (
        "NfcConstraintUnspecified"  # deprecated value - not documented
    )
    nfcConstraintUnspecified = (
        "nfcConstraintUnspecified"  # deprecated value - not documented
    )
    BLOCK_PAYMENT = "BLOCK_PAYMENT"
    blockPayment = "blockPayment"  # deprecated value
    BLOCK_CLOSED_LOOP_TRANSIT = "BLOCK_CLOSED_LOOP_TRANSIT"
    blockClosedLoopTransit = "blockClosedLoopTransit"  # deprecated value


class PredefinedItem(StrEnum):
    """
    see: https://developers.google.com/wallet/retail/offers/rest/v1/ClassTemplateInfo#predefineditem
    """

    PREDEFINED_ITEM_UNSPECIFIED = "PREDEFINED_ITEM_UNSPECIFIED"
    FREQUENT_FLYER_PROGRAM_NAME_AND_NUMBER = "FREQUENT_FLYER_PROGRAM_NAME_AND_NUMBER"
    frequentFlyerProgramNameAndNumber = (
        "frequentFlyerProgramNameAndNumber"  # deprecated value
    )
    FLIGHT_NUMBER_AND_OPERATING_FLIGHT_NUMBER = (
        "FLIGHT_NUMBER_AND_OPERATING_FLIGHT_NUMBER"
    )
    flightNumberAndOperatingFlightNumber = (
        "flightNumberAndOperatingFlightNumber"  # deprecated value
    )


class RedemptionChannel(StrEnum):
    """
    see: https://developers.google.com/wallet/retail/offers/rest/v1/offerclass#OfferClass.RedemptionChannel
    """

    REDEMPTION_CHANNEL_UNSPECIFIED = "REDEMPTION_CHANNEL_UNSPECIFIED"
    INSTORE = "INSTORE"
    instore = "instore"
    ONLINE = "ONLINE"
    online = "online"
    BOTH = "BOTH"
    both = "both"
    TEMPORARY_PRICE_REDUCTION = "TEMPORARY_PRICE_REDUCTION"
    temporaryPriceReduction = "temporaryPriceReduction"


class ReviewStatus(StrEnum):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/ReviewStatus
    """

    REVIEW_STATUS_UNSPECIFIED = "REVIEW_STATUS_UNSPECIFIED"
    UNDER_REVIEW = "UNDER_REVIEW"
    underReview = "underReview"
    APPROVED = "APPROVED"
    approved = "approved"  # deprecated value
    REJECTED = "REJECTED"
    rejected = "rejected"  # deprecated value
    DRAFT = "DRAFT"
    draft = "draft"  # deprecated value


class Role(StrEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/permissions#role
    """

    ROLE_UNSPECIFIED = "ROLE_UNSPECIFIED"
    OWNER = "OWNER"
    owner = "owner"  # deprecated value
    READER = "READER"
    reader = "reader"  # deprecated value
    WRITER = "WRITER"
    writer = "writer"  # deprecated value


class RowLabel(StrEnum):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#rowlabel
    """

    ROW_LABEL_UNSPECIFIED = "ROW_LABEL_UNSPECIFIED"
    ROW = "ROW"
    row = "row"  # deprecated value


class ScreenshotEligibility(StrEnum):
    SCREENSHOT_ELIGIBILITY_UNSPECIFIED = "SCREENSHOT_ELIGIBILITY_UNSPECIFIED"
    screenshotEligibilityUnspecified = "screenshotEligibilityUnspecified"
    ELIGIBLE = "ELIGIBLE"
    eligible = "eligible"  # deprecated value
    INELIGIBLE = "INELIGIBLE"
    inlegible = "ineligible"  # deprecated value


class SeatLabel(StrEnum):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#seatlabel
    """

    SEAT_LABEL_UNSPECIFIED = "SEAT_LABEL_UNSPECIFIED"
    SEAT = "SEAT"
    seat = "seat"  # deprecated value


class SectionLabel(StrEnum):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#sectionlabel
    """

    SECTION_LABEL_UNSPECIFIED = "SECTION_LABEL_UNSPECIFIED"
    SECTION = "SECTION"
    section = "section"  # deprecated value
    THEATER = "THEATER"
    theater = "theater"  # deprecated value


class SharedDataType(StrEnum):
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


class State(StrEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/State
         https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/State
    """

    STATE_UNSPECIFIED = "STATE_UNSPECIFIED"
    ACTIVE = "ACTIVE"
    active = "active"  # deprecated value
    COMPLETED = "COMPLETED"
    completed = "completed"  # deprecated value
    EXPIRED = "EXPIRED"
    expired = "expired"  # deprecated value
    INACTIVE = "INACTIVE"
    inactive = "inactive"  # deprecated value


class RetailState(StrEnum):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyclass#state
    """

    STATE_UNSPECIFIED = "STATE_UNSPECIFIED"
    TRUSTED_TESTERS = "TRUSTED_TESTERS"
    trustedTesters = "trustedTesters"  # deprecated value
    LIVE = "LIVE"
    live = "live"  # deprecated value
    DISABLED = "DISABLED"
    disabled = "disabled"  # deprecated value


class TotpAlgorithm(StrEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/RotatingBarcode#totpalgorithm
    """

    TOTP_ALGORITHM_UNSPECIFIED = "TOTP_ALGORITHM_UNSPECIFIED"
    TOTP_SHA1 = "TOTP_SHA1"


class TransitOption(StrEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#transitoption
    """

    TRANSIT_OPTION_UNSPECIFIED = "TRANSIT_OPTION_UNSPECIFIED"
    ORIGIN_AND_DESTINATION_NAMES = "ORIGIN_AND_DESTINATION_NAMES"
    ORIGIN_AND_DESTINATION_CODES = "ORIGIN_AND_DESTINATION_CODES"
    ORIGIN_NAME = "ORIGIN_NAME"


class ViewUnlockRequirement(StrEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ViewUnlockRequirement
    """

    VIEW_UNLOCK_REQUIREMENT_UNSPECIFIED = "VIEW_UNLOCK_REQUIREMENT_UNSPECIFIED"
    viewUnlockRequirementUnspecified = (
        "viewUnlockRequirementUnspecified"  # deprecated value - not documented
    )
    UNLOCK_NOT_REQUIRED = "UNLOCK_NOT_REQUIRED"
    unlockNotRequired = "unlockNotRequired"  # deprecated value - not documented
    UNLOCK_REQUIRED_TO_VIEW = "UNLOCK_REQUIRED_TO_VIEW"
    unlockRequiredToView = "unlockRequiredToView"  # deprecated value - not documented
