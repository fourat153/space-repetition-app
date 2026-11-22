from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin, TimestampMixin, UTCDateTime
from app.models.tag import card_tags

if TYPE_CHECKING:
    from app.models.deck import Deck
    from app.models.review_log import ReviewLog
    from app.models.tag import Tag

DEFAULT_EASE = 2.5
LEARNED_INTERVAL_DAYS = 21


class Card(IdMixin, TimestampMixin, Base):
    __tablename__ = "cards"

    deck_id: Mapped[str] = mapped_column(ForeignKey("decks.id", ondelete="CASCADE"), index=True)
    front: Mapped[str] = mapped_column(Text)
    back: Mapped[str] = mapped_column(Text)

    # SM-2 scheduling state
    interval_days: Mapped[int] = mapped_column(Integer, default=0)
    ease_factor: Mapped[float] = mapped_column(Float, default=DEFAULT_EASE)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)  # successful reviews in a row
    lapses: Mapped[int] = mapped_column(Integer, default=0)  # times rated Again after learning
    due_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), index=True)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(UTCDateTime())

    deck: Mapped["Deck"] = relationship(back_populates="cards")
    tags: Mapped[list["Tag"]] = relationship(secondary=card_tags, back_populates="cards")
    review_logs: Mapped[list["ReviewLog"]] = relationship(
        back_populates="card", cascade="all, delete-orphan", passive_deletes=True
    )

    @property
    def is_new(self) -> bool:
        """Never reviewed yet."""
        return self.last_reviewed_at is None

    @property
    def is_learned(self) -> bool:
        return self.interval_days >= LEARNED_INTERVAL_DAYS
