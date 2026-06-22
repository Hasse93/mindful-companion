"""Authentication: password hashing (bcrypt) + JWT issue/verify.

`get_current_user` returns the user id (string) used as `user_id` across the
app's tables. `current_auth` additionally exposes the email so we can recognise
the shared read-only demo account, and `require_writable` blocks writes from it.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings

_security = HTTPBearer(auto_error=True)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False


def create_access_token(subject: str, email: str = "") -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "email": email, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _decode(creds: HTTPAuthorizationCredentials) -> dict:
    settings = get_settings()
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            creds.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except jwt.PyJWTError:
        raise error
    if not payload.get("sub"):
        raise error
    return payload


@dataclass
class AuthUser:
    id: str
    email: str

    @property
    def is_demo(self) -> bool:
        return bool(self.email) and self.email.lower() == get_settings().demo_email.lower()


def current_auth(creds: HTTPAuthorizationCredentials = Depends(_security)) -> AuthUser:
    payload = _decode(creds)
    return AuthUser(id=str(payload["sub"]), email=str(payload.get("email", "")))


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(_security)) -> str:
    return str(_decode(creds)["sub"])


def require_writable(auth: AuthUser = Depends(current_auth)) -> str:
    """Like current_user, but rejects the shared read-only demo account."""
    if auth.is_demo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This is a read-only demo account. Create your own account to save entries.",
        )
    return auth.id
