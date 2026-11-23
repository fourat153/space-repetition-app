"""Services tested directly, without HTTP: no client, no tokens, no JSON."""

import pytest

from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.core.security import PasswordHasher, TokenService
from app.models import Card
from app.schemas.auth import UserCreate
from app.schemas.deck import DeckCreate, DeckUpdate
from app.services import AuthService, DeckService


@pytest.fixture
def auth(db_session):
    return AuthService(db_session, PasswordHasher(), TokenService("test-secret-key-32-bytes-minimum!", "HS256", 5))


@pytest.fixture
def user(auth):
    return auth.register(UserCreate(email="ahmed@example.com", password="Secret123!"))


@pytest.fixture
def decks(db_session, user):
    return DeckService(db_session, user)


def test_register_hashes_password(user):
    assert user.hashed_password != "Secret123!"
    assert user.hashed_password.startswith("$argon2")


def test_login_and_token_roundtrip(auth, user):
    token = auth.login("AHMED@example.com", "Secret123!").access_token
    assert auth.get_user_from_token(token).id == user.id


def test_login_wrong_password(auth, user):
    with pytest.raises(AuthenticationError):
        auth.login("ahmed@example.com", "wrong-password")


def test_bad_token(auth):
    with pytest.raises(AuthenticationError):
        auth.get_user_from_token("not-a-token")


def test_deck_crud(decks):
    deck = decks.create(DeckCreate(name="  Spanish  "))
    assert deck.name == "Spanish"

    with pytest.raises(ConflictError):
        decks.create(DeckCreate(name="spanish"))

    assert decks.update(deck.id, DeckUpdate(name="Español")).name == "Español"
    assert [d.name for d in decks.list()] == ["Español"]


def test_delete_reports_card_count(db_session, decks):
    deck = decks.create(DeckCreate(name="Spanish"))
    db_session.add_all([Card(deck_id=deck.id, front="hola", back="hello"), Card(deck_id=deck.id, front="si", back="yes")])
    db_session.commit()

    assert decks.delete(deck.id).deleted_cards == 2
    with pytest.raises(NotFoundError):
        decks.get(deck.id)


def test_users_are_isolated(db_session, auth, decks):
    deck = decks.create(DeckCreate(name="Spanish"))
    other = auth.register(UserCreate(email="other@example.com", password="Secret123!"))
    other_decks = DeckService(db_session, other)

    assert other_decks.list() == []
    with pytest.raises(NotFoundError):
        other_decks.delete(deck.id)
