from fastapi import APIRouter, status

from app.api.deps import DeckServiceDep
from app.schemas.deck import DeckCreate, DeckDeleted, DeckRead, DeckUpdate

router = APIRouter(prefix="/decks", tags=["decks"])


@router.get("", response_model=list[DeckRead])
def list_decks(service: DeckServiceDep):
    return service.list()


@router.post("", response_model=DeckRead, status_code=status.HTTP_201_CREATED)
def create_deck(payload: DeckCreate, service: DeckServiceDep):
    return service.create(payload)


@router.get("/{deck_id}", response_model=DeckRead)
def get_deck(deck_id: str, service: DeckServiceDep):
    return service.get(deck_id)


@router.patch("/{deck_id}", response_model=DeckRead)
def update_deck(deck_id: str, payload: DeckUpdate, service: DeckServiceDep):
    return service.update(deck_id, payload)


@router.delete("/{deck_id}", response_model=DeckDeleted)
def delete_deck(deck_id: str, service: DeckServiceDep):
    """Deletes the deck and all its cards. The client should confirm first,
    using `card_count` from GET /decks/{id} to tell the user what will be removed."""
    return service.delete(deck_id)
