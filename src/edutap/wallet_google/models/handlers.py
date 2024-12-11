"""
see https://developers.google.com/wallet/generic/use-cases/use-callbacks-for-saves-and-deletions
"""

from .bases import Model
from .datatypes.enums import CamelCaseAliasEnum


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
    expTimeMillis: int
    eventType: EventType


class ImageData(Model):
    mimetype: str
    data: bytes


class CallbackData(Model):
    signature: str
    intermediateSigningKey: IntermediateSigningKey
    protocolVersion: str
    signedMessage: (
        SignedMessage | str
    )  # google sends this as a string, but we want to parse it as a SignedMessage


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