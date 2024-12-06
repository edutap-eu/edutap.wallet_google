"""
see https://developers.google.com/wallet/generic/use-cases/use-callbacks-for-saves-and-deletions
"""

from .bases import GoogleWalletModel
from .primitives.enums import CamelCaseAliasEnum


class EventType(CamelCaseAliasEnum):
    SAVE = "SAVE"
    DEL = "DEL"


class SignedKey(GoogleWalletModel):
    keyValue: str
    keyExpiration: int


class IntermediateSigningKey(GoogleWalletModel):
    signedKey: SignedKey | str
    signatures: list[str]


class SignedMessage(GoogleWalletModel):
    classId: str
    objectId: str
    expTimeMillis: int
    eventType: EventType


class CallbackData(GoogleWalletModel):
    signature: str
    intermediateSigningKey: IntermediateSigningKey
    protocolVersion: str
    signedMessage: (
        SignedMessage | str
    )  # google sends this as a string, but we want to parse it as a SignedMessage
