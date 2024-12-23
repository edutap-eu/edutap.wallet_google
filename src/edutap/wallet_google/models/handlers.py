"""
see https://developers.google.com/wallet/generic/use-cases/use-callbacks-for-saves-and-deletions
"""

from .bases import Model
from .datatypes.enums import CamelCaseAliasEnum


# image fetching from data provider


class ImageData(Model):
    mimetype: str
    data: bytes


#  Callback


class EventType(CamelCaseAliasEnum):
    SAVE = "SAVE"
    DEL = "DEL"


class SignedKey(Model):
    keyValue: str
    keyExpiration: int


class IntermediateSigningKey(Model):
    signedKey: SignedKey | str
    signatures: list[str]


class SignedMessage(Model):
    classId: str
    objectId: str
    eventType: EventType
    expTimeMillis: int
    count: int
    nonce: str


class CallbackData(Model):
    signature: str
    intermediateSigningKey: IntermediateSigningKey
    protocolVersion: str
    signedMessage: str  # Google sends this as a string, this get verified and the returned as a SignedMessage


# keys for callback data validation


class RootSigningPublicKey(Model):
    """
    see https://developers.google.com/pay/api/android/guides/resources/payment-data-cryptography#root-signing-keys
    """

    keyValue: str
    protocolVersion: str
    keyExpiration: str | None = None


class RootSigningPublicKeys(Model):
    """
    see https://developers.google.com/pay/api/android/guides/resources/payment-data-cryptography#root-signing-keys
    """

    keys: list[RootSigningPublicKey]
