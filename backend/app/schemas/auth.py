import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str | None
    role: str
    is_email_verified: bool
    is_2fa_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class VerifyEmailRequest(BaseModel):
    token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class TwoFactorSetupResponse(BaseModel):
    secret: str
    provisioning_uri: str


class TwoFactorVerifyRequest(BaseModel):
    code: str


class LoginWith2FA(BaseModel):
    email: EmailStr
    password: str
    totp_code: str | None = None