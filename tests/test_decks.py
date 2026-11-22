from sqlalchemy import select

from app.models import Card, Deck, User
from tests.conftest import register_and_login

API = "/api/v1/decks"


def test_requires_login(client):
    assert client.get(API).status_code == 401


def test_create_and_list(client, auth_headers):
    r = client.post(API, json={"name": "Spanish", "description": "Vocab"}, headers=auth_headers)
    assert r.status_code == 201
    assert r.json()["card_count"] == 0

    decks = client.get(API, headers=auth_headers).json()
    assert [d["name"] for d in decks] == ["Spanish"]
    assert decks[0]["created_at"].endswith("Z")  # timezone kept after reading from SQLite


def test_duplicate_name_rejected(client, auth_headers):
    client.post(API, json={"name": "Spanish"}, headers=auth_headers)
    r = client.post(API, json={"name": "spanish"}, headers=auth_headers)
    assert r.status_code == 409


def test_update(client, auth_headers):
    deck_id = client.post(API, json={"name": "Spanish"}, headers=auth_headers).json()["id"]
    r = client.patch(f"{API}/{deck_id}", json={"name": "Español"}, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Español"


def test_get_missing_returns_404(client, auth_headers):
    assert client.get(f"{API}/nope", headers=auth_headers).status_code == 404


def test_users_cannot_see_each_others_decks(client, auth_headers):
    deck_id = client.post(API, json={"name": "Spanish"}, headers=auth_headers).json()["id"]
    other = register_and_login(client, "other@example.com")

    assert client.get(API, headers=other).json() == []
    assert client.get(f"{API}/{deck_id}", headers=other).status_code == 404
    assert client.delete(f"{API}/{deck_id}", headers=other).status_code == 404
    # Same name is fine for a different user
    assert client.post(API, json={"name": "Spanish"}, headers=other).status_code == 201


def test_delete_removes_only_its_cards(client, db_session, auth_headers):
    user = db_session.scalar(select(User))
    spanish = Deck(user=user, name="Spanish", cards=[Card(front="hola", back="hello"), Card(front="si", back="yes")])
    capitals = Deck(user=user, name="Capitals", cards=[Card(front="France", back="Paris")])
    db_session.add_all([spanish, capitals])
    db_session.commit()

    assert client.get(f"{API}/{spanish.id}", headers=auth_headers).json()["card_count"] == 2

    r = client.delete(f"{API}/{spanish.id}", headers=auth_headers)
    assert r.json() == {"id": spanish.id, "deleted_cards": 2}

    remaining = client.get(API, headers=auth_headers).json()
    assert [(d["name"], d["card_count"]) for d in remaining] == [("Capitals", 1)]
