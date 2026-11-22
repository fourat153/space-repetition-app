from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models import Deck, User
from app.repositories import DeckRepository
from app.schemas.deck import DeckCreate, DeckDeleted, DeckRead, DeckUpdate


class DeckService:
    """Deck use cases for one user. Every method only sees that user's decks."""

    def __init__(self, session: Session, user: User) -> None:
        self._session = session
        self._decks = DeckRepository(session)
        self._user = user

    def list(self) -> list[DeckRead]:
        return [self._to_read(deck, count) for deck, count in self._decks.list_with_card_counts(self._user.id)]

    def get(self, deck_id: str) -> DeckRead:
        deck = self._get_owned(deck_id)
        return self._to_read(deck, self._decks.count_cards(deck.id))

    def create(self, data: DeckCreate) -> DeckRead:
        name = data.name.strip()
        self._ensure_name_free(name)

        deck = self._decks.add(Deck(user_id=self._user.id, name=name, description=data.description))
        self._session.commit()
        return self._to_read(deck, 0)

    def update(self, deck_id: str, data: DeckUpdate) -> DeckRead:
        deck = self._get_owned(deck_id)
        changes = data.model_dump(exclude_unset=True)

        if "name" in changes:
            changes["name"] = changes["name"].strip()
            self._ensure_name_free(changes["name"], exclude_id=deck.id)

        for field, value in changes.items():
            setattr(deck, field, value)
        self._session.commit()
        return self._to_read(deck, self._decks.count_cards(deck.id))

    def delete(self, deck_id: str) -> DeckDeleted:
        """Deletes the deck and all its cards (cascade)."""
        deck = self._get_owned(deck_id)
        card_count = self._decks.count_cards(deck.id)
        self._decks.delete(deck)
        self._session.commit()
        return DeckDeleted(id=deck_id, deleted_cards=card_count)

    # --- helpers -------------------------------------------------------------

    def _get_owned(self, deck_id: str) -> Deck:
        deck = self._decks.get_for_user(deck_id, self._user.id)
        # Another user's deck is "not found" too, so nobody can tell which ids exist.
        if deck is None:
            raise NotFoundError("Deck not found")
        return deck

    def _ensure_name_free(self, name: str, exclude_id: str | None = None) -> None:
        if self._decks.name_taken(self._user.id, name, exclude_id):
            raise ConflictError(f"A deck named '{name}' already exists")

    @staticmethod
    def _to_read(deck: Deck, card_count: int) -> DeckRead:
        return DeckRead(
            id=deck.id,
            name=deck.name,
            description=deck.description,
            card_count=card_count,
            created_at=deck.created_at,
            updated_at=deck.updated_at,
        )
