from datetime import timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import Settings
from app.db.base import utc_now


class PasswordHasher:
    """Hashes and checks passwords (Argon2)."""

    def __init__(self) -> None:
        self._hasher = PasswordHash.recommended()

    def hash(self, password: str) -> str:
        return self._hasher.hash(password)

    def verify(self, password: str, hashed: str) -> bool:
        return self._hasher.verify(password, hashed)


class TokenService:
    """Creates and reads JWT access tokens."""

    def __init__(self, secret_key: str, algorithm: str, expire_minutes: int) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expire_minutes = expire_minutes

    @classmethod
    def from_settings(cls, settings: Settings) -> "TokenService":
        return cls(settings.jwt_secret_key, settings.jwt_algorithm, settings.access_token_expire_minutes)

    def create(self, subject: str) -> str:
        now = utc_now()
        payload = {
            "sub": subject,  # who the token belongs to (the user id)
            "iat": now,  # issued at
            "exp": now + timedelta(minutes=self._expire_minutes),
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode(self, token: str) -> str | None:
        """Returns the subject, or None if the token is invalid or expired."""
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except jwt.InvalidTokenError:
            return None
        return payload.get("sub")
