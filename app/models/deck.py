from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.card import Card
    from app.models.user import User


class Deck(IdMixin, TimestampMixin, Base):
    __tablename__ = "decks"
    # Deck names are unique per user (two users can both have "Spanish").
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_deck_user_name"),)

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="decks")
    # Deleting a deck deletes all its cards (and, through Card, their review history).
    cards: Mapped[list["Card"]] = relationship(
        back_populates="deck", cascade="all, delete-orphan", passive_deletes=True
    )
