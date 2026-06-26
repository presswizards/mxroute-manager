"""Tests for outbound SSRF guards."""

import pytest

from utils.apprise.url_utils import validate_apprise_url
from utils.ssrf_guard import (
    assert_public_outbound_host,
    validate_http_service_url,
    validate_smtp_host,
)


def test_blocks_loopback_http_url():
    with pytest.raises(ValueError, match="not allowed|private|internal"):
        validate_http_service_url("http://127.0.0.1/admin", require_https=False)


def test_blocks_metadata_hostname():
    with pytest.raises(ValueError, match="not allowed"):
        assert_public_outbound_host("metadata.google.internal")


def test_blocks_private_smtp_host():
    with pytest.raises(ValueError, match="private|internal|not allowed"):
        validate_smtp_host("10.0.0.5")


def test_allows_public_https_discovery_url():
    validate_http_service_url(
        "https://idp.example.com/.well-known/openid-configuration"
    )


def test_blocks_json_webhook_to_localhost():
    with pytest.raises(ValueError, match="not allowed|private|internal"):
        validate_apprise_url("json://127.0.0.1/hook")


def test_allows_mailto_apprise_url():
    validate_apprise_url("mailto://user@example.com")
