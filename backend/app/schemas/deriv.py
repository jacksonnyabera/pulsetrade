from pydantic import BaseModel


class DerivCallbackRequest(BaseModel):
    code: str
    code_verifier: str


class DerivAccountOut(BaseModel):
    id: str
    deriv_loginid: str
    account_type: str
    currency: str
    is_active: bool


class WsUrlRequest(BaseModel):
    account_id: str | None = None


class WsUrlResponse(BaseModel):
    url: str