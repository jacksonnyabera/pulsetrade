import uuid
from datetime import datetime

from backend.app.services.auth_service import log_security_event
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


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

@router.post("/2fa/setup", response_model=TwoFactorSetupResponse)
async def setup_2fa(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    secret = generate_totp_secret()
    current_user.totp_secret = secret
    await db.commit()
    return TwoFactorSetupResponse(secret=secret, provisioning_uri=get_totp_uri(secret, current_user.email))


@router.post("/2fa/enable")
async def enable_2fa(
    payload: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.totp_secret or not verify_totp_code(current_user.totp_secret, payload.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code")
    current_user.is_2fa_enabled = True
    await db.commit()
    await log_security_event(db, current_user.id, "2fa_enabled")
    return {"message": "2FA enabled"}


@router.post("/2fa/disable")
async def disable_2fa(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    current_user.is_2fa_enabled = False
    current_user.totp_secret = None
    await db.commit()
    await log_security_event(db, current_user.id, "2fa_disabled")
    return {"message": "2FA disabled"}