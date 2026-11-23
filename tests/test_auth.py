from datetime import timedelta

import jwt
import pytest

from app.core.config import get_settings
from app.db.base import utc_now

AUTH = "/api/v1/auth"


def test_register_login_me(client):
    r = client.post(f"{AUTH}/register", json={"email": "Ahmed@Example.com", "password": "Secret123!"})
    assert r.status_code == 201
    assert r.json()["email"] == "ahmed@example.com"
    assert "password" not in r.text and "hashed" not in r.text

    r = client.post(f"{AUTH}/login", data={"username": "ahmed@example.com", "password": "Secret123!"})
    assert r.status_code == 200
    token = r.json()["access_token"]

    r = client.get(f"{AUTH}/me", headers={"Authorization": f"Bearer {token}"})
    assert r.json()["email"] == "ahmed@example.com"


def test_duplicate_email(client):
    body = {"email": "a@example.com", "password": "Secret123!"}
    client.post(f"{AUTH}/register", json=body)
    assert client.post(f"{AUTH}/register", json=body).status_code == 409


def test_wrong_password(client):
    client.post(f"{AUTH}/register", json={"email": "a@example.com", "password": "Secret123!"})
    r = client.post(f"{AUTH}/login", data={"username": "a@example.com", "password": "nope-nope"})
    assert r.status_code == 401


def test_short_password_rejected(client):
    r = client.post(f"{AUTH}/register", json={"email": "a@example.com", "password": "123"})
    assert r.status_code == 422


@pytest.mark.parametrize(
    ("password", "missing"),
    [
        ("secret123!", "an uppercase letter"),
        ("SECRET123!", "a lowercase letter"),
        ("Secretabc!", "a digit"),
        ("Secret1234", "a special character"),
        ("secretsecret", "an uppercase letter, a digit, a special character"),
    ],
)
def test_weak_password_rejected(client, password, missing):
    r = client.post(f"{AUTH}/register", json={"email": "a@example.com", "password": password})
    assert r.status_code == 422
    assert r.json()["detail"][0]["msg"] == f"Password must contain {missing}"


def test_password_with_space_rejected(client):
    r = client.post(f"{AUTH}/register", json={"email": "a@example.com", "password": "Secret 123!"})
    assert r.status_code == 422
    assert r.json()["detail"][0]["msg"] == "Password must not contain spaces"


def test_me_requires_token(client):
    assert client.get(f"{AUTH}/me").status_code == 401
    assert client.get(f"{AUTH}/me", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_expired_token_rejected(client, auth_headers):
    user_id = client.get(f"{AUTH}/me", headers=auth_headers).json()["id"]
    s = get_settings()
    expired = jwt.encode(
        {"sub": user_id, "exp": utc_now() - timedelta(minutes=1)}, s.jwt_secret_key, algorithm=s.jwt_algorithm
    )
    r = client.get(f"{AUTH}/me", headers={"Authorization": f"Bearer {expired}"})
    assert r.status_code == 401
