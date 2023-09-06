from pydantic import BaseModel


class JwtResource(BaseModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/jwt
         https://developers.google.com/wallet/generic/web/javascript-button#google-pay-api-for-passes-jwt
    """

    jwt: str
