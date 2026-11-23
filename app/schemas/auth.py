import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from pydantic_core import PydanticCustomError

# Each rule is (regex, what's missing). Keep in sync with frontend/src/lib/password.ts.
PASSWORD_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"[a-z]"), "a lowercase letter"),
    (re.compile(r"[A-Z]"), "an uppercase letter"),
    (re.compile(r"\d"), "a digit"),
    (re.compile(r"[^A-Za-z0-9\s]"), "a special character"),
]
NO_WHITESPACE = re.compile(r"^\S+$")


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def check_password_strength(cls, value: str) -> str:
        if not NO_WHITESPACE.match(value):
            raise PydanticCustomError("password_whitespace", "Password must not contain spaces")
        missing = [label for pattern, label in PASSWORD_RULES if not pattern.search(value)]
        if missing:
            raise PydanticCustomError(
                "password_strength",
                "Password must contain {missing}",
                {"missing": ", ".join(missing)},
            )
        return value


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
