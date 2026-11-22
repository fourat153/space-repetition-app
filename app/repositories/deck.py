from sqlalchemy import func, select

from app.models import Card, Deck
from app.repositories.base import BaseRepository


class DeckRepository(BaseRepository[Deck]):
    model = Deck

    def get_for_user(self, deck_id: str, user_id: str) -> Deck | None:
        deck = self.get(deck_id)
        return deck if deck is not None and deck.user_id == user_id else None

    def list_with_card_counts(self, user_id: str) -> list[tuple[Deck, int]]:
        """Every deck of the user with its number of cards, in one query (empty decks included)."""
        rows = self.session.execute(
            select(Deck, func.count(Card.id))
            .outerjoin(Card, Card.deck_id == Deck.id)
            .where(Deck.user_id == user_id)
            .group_by(Deck.id)
            .order_by(Deck.name)
        ).all()
        return [(deck, count) for deck, count in rows]

    def count_cards(self, deck_id: str) -> int:
        return self.session.scalar(select(func.count()).select_from(Card).where(Card.deck_id == deck_id)) or 0

    def name_taken(self, user_id: str, name: str, exclude_id: str | None = None) -> bool:
        query = select(Deck.id).where(Deck.user_id == user_id, func.lower(Deck.name) == name.lower())
        if exclude_id is not None:
            query = query.where(Deck.id != exclude_id)
        return self.session.scalar(query) is not None
