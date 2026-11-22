from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import PasswordHasher, TokenService
from app.models import User
from app.repositories import UserRepository
from app.schemas.auth import Token, UserCreate


class AuthService:
    def __init__(self, session: Session, hasher: PasswordHasher, tokens: TokenService) -> None:
        self._session = session
        self._users = UserRepository(session)
        self._hasher = hasher
        self._tokens = tokens

    def register(self, data: UserCreate) -> User:
        email = data.email.lower()
        if self._users.email_exists(email):
            raise ConflictError("Email already registered")

        user = self._users.add(User(email=email, hashed_password=self._hasher.hash(data.password)))
        self._session.commit()
        return user

    def login(self, email: str, password: str) -> Token:
        user = self._users.get_by_email(email)
        # Same error whether the email or the password is wrong, so nobody can probe which emails exist.
        if user is None or not self._hasher.verify(password, user.hashed_password):
            raise AuthenticationError("Incorrect email or password")
        return Token(access_token=self._tokens.create(user.id))

    def get_user_from_token(self, token: str) -> User:
        user_id = self._tokens.decode(token)
        user = self._users.get(user_id) if user_id else None
        if user is None or not user.is_active:
            raise AuthenticationError("Could not validate credentials")
        return user
