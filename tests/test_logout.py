"""Tests for POST-only logout."""

from tests.helpers import (
    csrf_token_from_response,
    logout_session,
    prime_authenticated_session,
)


def test_logout_get_returns_405(client):
    response = client.get("/logout")
    assert response.status_code == 405


def test_logout_post_requires_csrf(fresh_db, client, db_connection):
    prime_authenticated_session(client, "admin@local")
    response = client.post("/logout")
    assert response.status_code == 400


def test_logout_post_clears_session(fresh_db, client, db_connection):
    db_connection.execute(
        "INSERT INTO users (email, password_hash, is_admin) VALUES (?, ?, 1)",
        ("admin@local", "unused-hash"),
    )
    db_connection.commit()
    token = prime_authenticated_session(client, "admin@local")

    response = logout_session(client, token)
    assert response.status_code == 302

    with client.session_transaction() as sess:
        assert sess.get("user") is None

    assert client.get("/api/domains").status_code == 401
