"""Apprise branding: MXroute Manager logo instead of default Apprise assets."""

import os
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from apprise import AppriseAsset

from app_meta import APP_NAME, GITHUB_URL

NOTIFICATION_LOGO_PATH = "/static/notification-logo.png"

# Schemes that accept avatar_url as a query parameter (Apprise wiki).
_AVATAR_URL_SCHEMES = frozenset(
    {
        "ntfy",
        "ntfys",
        "discord",
        "slack",
        "mattermost",
        "mmost",
        "mmosts",
    }
)


def get_manager_public_url():
    """Public origin for this manager (no trailing slash)."""
    explicit = (os.getenv("MANAGER_PUBLIC_URL") or "").strip().rstrip("/")
    if explicit:
        if "://" in explicit:
            return explicit
        scheme = (os.getenv("PUBLIC_URL_SCHEME") or "https").strip().rstrip(":")
        return f"{scheme}://{explicit}"

    host = (os.getenv("RESET_PORTAL_CNAME_TARGET") or "").strip().lower().rstrip(".")
    if host:
        scheme = (os.getenv("PUBLIC_URL_SCHEME") or "https").strip().rstrip(":")
        return f"{scheme}://{host}"
    return ""


def get_notification_avatar_url():
    """HTTPS URL to the PNG used in push notifications."""
    explicit = (os.getenv("NOTIFICATION_AVATAR_URL") or "").strip()
    if explicit:
        return explicit

    base = get_manager_public_url()
    if not base:
        return None
    return f"{base}{NOTIFICATION_LOGO_PATH}"


class MxmAppriseAsset(AppriseAsset):
    """Apprise asset bundle using the MXroute Manager logo."""

    def __init__(self, avatar_url=None, **kwargs):
        super().__init__(**kwargs)
        self.app_id = APP_NAME
        self.app_desc = APP_NAME
        self.app_url = GITHUB_URL
        if avatar_url:
            self.image_url_logo = avatar_url
            self.image_url_mask = avatar_url


def mxm_apprise_asset():
    return MxmAppriseAsset(avatar_url=get_notification_avatar_url())


def with_notification_avatar(url, avatar_url=None):
    """Append avatar_url to supported Apprise URLs when not already set."""
    url = str(url or "").strip()
    avatar = (avatar_url or get_notification_avatar_url() or "").strip()
    if not url or not avatar or "://" not in url:
        return url

    scheme = url.split("://", 1)[0].lower()
    if scheme not in _AVATAR_URL_SCHEMES:
        return url

    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if query.get("avatar_url"):
        return url

    query["avatar_url"] = avatar
    return urlunparse(parsed._replace(query=urlencode(query)))
