from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings
import pyotp

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def create_refresh_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    payload = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])

def create_email_verification_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {"sub": user_id, "exp": expire, "type": "email_verify"}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def create_password_reset_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    payload = {"sub": user_id, "exp": expire, "type": "password_reset"}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")

def generate_totp_secret() -> str:
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str) -> str:
    return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name="PulseTrade")


def verify_totp_code(secret: str, code: str) -> bool:
    return pyotp.totp.TOTP(secret).verify(code, valid_window=1)