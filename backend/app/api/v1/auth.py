import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_email_verification_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
    hash_password,
)
from app.models.user import User
from app.schemas.auth import (
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshRequest,
    TokenPair,
    UserLogin,
    UserOut,
    UserRegister,
    VerifyEmailRequest,
)
from app.services.auth_service import (
    authenticate_user,
    create_user,
    get_user_by_email,
    get_user_by_id,
)

from fastapi import Request

from app.core.security import generate_totp_secret, get_totp_uri, verify_totp_code
from app.services.auth_service import log_security_event

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_email(db, payload.email)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = await create_user(db, payload.email, payload.password, payload.full_name)

    token = create_email_verification_token(str(user.id))
    print(f"[DEV] Email verification link: http://localhost:3000/verify-email?token={token}")

    return user


@router.post("/login", response_model=TokenPair)
async def login(payload: LoginWith2FA, request: Request, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, payload.email, payload.password)
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    if user.is_2fa_enabled:
        if not payload.totp_code or not verify_totp_code(user.totp_secret, payload.totp_code):
            await log_security_event(db, user.id, "login_failed_2fa", ip, user_agent)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing 2FA code")

    await log_security_event(db, user.id, "login", ip, user_agent)

    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    return TokenPair(access_token=access_token, refresh_token=refresh_token)

@router.get("/me", response_model=UserOut)
async def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    invalid_token = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    try:
        decoded = decode_token(payload.refresh_token)
        if decoded.get("type") != "refresh":
            raise invalid_token
        user_id = decoded.get("sub")
    except JWTError:
        raise invalid_token

    user = await get_user_by_id(db, uuid.UUID(user_id))
    if user is None or not user.is_active:
        raise invalid_token

    new_access = create_access_token(subject=str(user.id))
    new_refresh = create_refresh_token(subject=str(user.id))
    return TokenPair(access_token=new_access, refresh_token=new_refresh)


@router.post("/verify-email")
async def verify_email(payload: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    invalid_token = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    try:
        decoded = decode_token(payload.token)
        if decoded.get("type") != "email_verify":
            raise invalid_token
        user_id = decoded.get("sub")
    except JWTError:
        raise invalid_token

    user = await get_user_by_id(db, uuid.UUID(user_id))
    if user is None:
        raise invalid_token

    user.is_email_verified = True
    await db.commit()
    return {"message": "Email verified successfully"}


@router.post("/forgot-password")
async def forgot_password(payload: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, payload.email)
    if user is not None:
        token = create_password_reset_token(str(user.id))
        print(f"[DEV] Password reset link: http://localhost:3000/reset-password?token={token}")
    # Always return the same response, whether or not the email exists,
    # so this endpoint can't be used to enumerate registered emails.
    return {"message": "If that email is registered, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(payload: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    invalid_token = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    try:
        decoded = decode_token(payload.token)
        if decoded.get("type") != "password_reset":
            raise invalid_token
        user_id = decoded.get("sub")
    except JWTError:
        raise invalid_token

    user = await get_user_by_id(db, uuid.UUID(user_id))
    if user is None:
        raise invalid_token

    user.hashed_password = hash_password(payload.new_password)
    await db.commit()
    return {"message": "Password reset successfully"}