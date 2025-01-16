"""
see https://developers.google.com/wallet/generic/use-cases/use-callbacks-for-saves-and-deletions
"""

from .datatypes.enums import CamelCaseAliasEnum
from pydantic import BaseModel


# image fetching from data provider


class ImageData(BaseModel):
    mimetype: str
    data: bytes


#  Callback


class EventType(CamelCaseAliasEnum):
    SAVE = "SAVE"
    DEL = "DEL"


class SignedKey(BaseModel):
    keyValue: str
    keyExpiration: int


class IntermediateSigningKey(BaseModel):
    signedKey: str
    signatures: list[str]


class SignedMessage(BaseModel):
    classId: str
    objectId: str
    eventType: EventType
    expTimeMillis: int
    count: int
    nonce: str


class CallbackData(BaseModel):
    signature: str
    intermediateSigningKey: IntermediateSigningKey
    protocolVersion: str
    signedMessage: str  # Google sends this as a string, this get verified and the returned as a SignedMessage


# keys for callback data validation


class RootSigningPublicKey(BaseModel):
    """
    see https://developers.google.com/pay/api/android/guides/resources/payment-data-cryptography#root-signing-keys
    """

    keyValue: str
    protocolVersion: str
    keyExpiration: str | None = None


class RootSigningPublicKeys(BaseModel):
    """
    see https://developers.google.com/pay/api/android/guides/resources/payment-data-cryptography#root-signing-keys
    """

    keys: list[RootSigningPublicKey]
