from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import AuthServiceDep, CurrentUser
from app.schemas.auth import Token, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, auth: AuthServiceDep):
    return auth.register(payload)


@router.post("/login", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], auth: AuthServiceDep):
    """OAuth2 form login: send `username` (your email) and `password` as form data."""
    return auth.login(form.username, form.password)


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser):
    return user
