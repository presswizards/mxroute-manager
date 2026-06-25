"""Tests for Apprise notification branding (custom logo URL)."""

from utils.apprise.secrets import resolve_target_url
from utils.notification_branding import (
    get_notification_avatar_url,
    get_manager_public_url,
    with_notification_avatar,
)


def test_with_notification_avatar_appends_ntfy(monkeypatch):
    monkeypatch.setenv(
        "NOTIFICATION_AVATAR_URL",
        "https://manager.example.com/static/notification-logo.png",
    )
    url = "ntfys://ntfy.example.com/alerts?auth=token&priority=high"
    result = with_notification_avatar(url)
    assert "avatar_url=https%3A%2F%2Fmanager.example.com" in result
    assert result.count("avatar_url=") == 1


def test_with_notification_avatar_skips_when_already_set(monkeypatch):
    monkeypatch.setenv(
        "NOTIFICATION_AVATAR_URL", "https://manager.example.com/logo.png"
    )
    url = "ntfys://ntfy.example.com/alerts?avatar_url=https://custom.example/icon.png"
    assert with_notification_avatar(url) == url


def test_with_notification_avatar_ignores_unsupported_scheme(monkeypatch):
    monkeypatch.setenv(
        "NOTIFICATION_AVATAR_URL", "https://manager.example.com/logo.png"
    )
    url = "mailto://user:pass@smtp.example.com:587"
    assert with_notification_avatar(url) == url


def test_get_notification_avatar_url_from_manager_public_url(monkeypatch):
    monkeypatch.delenv("NOTIFICATION_AVATAR_URL", raising=False)
    monkeypatch.setenv("MANAGER_PUBLIC_URL", "https://manager.example.com")
    assert (
        get_notification_avatar_url()
        == "https://manager.example.com/static/notification-logo.png"
    )


def test_get_manager_public_url_from_host_and_scheme(monkeypatch):
    monkeypatch.delenv("MANAGER_PUBLIC_URL", raising=False)
    monkeypatch.setenv("RESET_PORTAL_CNAME_TARGET", "manager.example.com")
    monkeypatch.setenv("PUBLIC_URL_SCHEME", "https")
    assert get_manager_public_url() == "https://manager.example.com"


def test_resolve_target_url_injects_avatar(monkeypatch):
    monkeypatch.setenv(
        "NOTIFICATION_AVATAR_URL",
        "https://manager.example.com/static/notification-logo.png",
    )
    url = resolve_target_url({"url": "ntfys://ntfy.example.com/alerts"})
    assert "avatar_url=" in url
