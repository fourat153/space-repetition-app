"""Dependency injection: how FastAPI builds the objects routes need.

A route declares what it needs, e.g. `service: DeckServiceDep`, and FastAPI builds
the whole chain for each request:

    get_db ─┬─> AuthService ──> CurrentUser ─┐
            └────────────────────────────────┴─> DeckService
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import PasswordHasher, TokenService
from app.db.session import get_db
from app.models import User
from app.services import AuthService, DeckService

DbSession = Annotated[Session, Depends(get_db)]

# Reads "Authorization: Bearer <token>". tokenUrl powers Swagger's "Authorize" button.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{get_settings().api_prefix}/auth/login")


# Stateless helpers: built once and shared by every request.
@lru_cache
def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


@lru_cache
def get_token_service() -> TokenService:
    return TokenService.from_settings(get_settings())


# Services: built per request, because they hold that request's DB session.
def get_auth_service(
    db: DbSession,
    hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    tokens: Annotated[TokenService, Depends(get_token_service)],
) -> AuthService:
    return AuthService(db, hasher, tokens)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], auth: AuthServiceDep) -> User:
    return auth.get_user_from_token(token)


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_deck_service(db: DbSession, user: CurrentUser) -> DeckService:
    return DeckService(db, user)


DeckServiceDep = Annotated[DeckService, Depends(get_deck_service)]
