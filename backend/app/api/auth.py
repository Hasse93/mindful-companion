"""/auth — registration and login (issues JWT access tokens)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth import create_access_token, hash_password, verify_password
from app.database import get_session
from app.models import User
from app.schemas import LoginRequest, RegisterRequest, TokenResponse, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(
    body: RegisterRequest,
    session: Session = Depends(get_session),
) -> User:
    email = body.email.lower().strip()
    existing = session.exec(select(User).where(User.email == email)).first()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    user = User(email=email, hashed_password=hash_password(body.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    session: Session = Depends(get_session),
) -> TokenResponse:
    email = body.email.lower().strip()
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Incorrect email or password"
        )
    return TokenResponse(access_token=create_access_token(str(user.id), user.email))
