from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeckCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class DeckUpdate(BaseModel):
    """All fields optional: only the ones sent are changed (PATCH)."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None


class DeckRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None
    card_count: int
    created_at: datetime
    updated_at: datetime


class DeckDeleted(BaseModel):
    id: str
    deleted_cards: int
