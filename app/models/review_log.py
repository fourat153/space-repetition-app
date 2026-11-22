from datetime import datetime
from enum import IntEnum
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Float, ForeignKey, Integer, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin, UTCDateTime, utc_now

if TYPE_CHECKING:
    from app.models.card import Card


class Rating(IntEnum):
    AGAIN = 1
    HARD = 2
    GOOD = 3
    EASY = 4


class ReviewLog(IdMixin, Base):
    __tablename__ = "review_logs"
    __table_args__ = (CheckConstraint("rating BETWEEN 1 AND 4", name="ck_review_rating"),)

    card_id: Mapped[str] = mapped_column(ForeignKey("cards.id", ondelete="CASCADE"), index=True)
    rating: Mapped[int] = mapped_column(SmallInteger)
    reviewed_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now, index=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer)

    # Card state right after this review (lets stats and restores work without recomputing)
    interval_days: Mapped[int] = mapped_column(Integer)
    ease_factor: Mapped[float] = mapped_column(Float)

    card: Mapped["Card"] = relationship(back_populates="review_logs")
