"""Block outbound requests to private/internal networks."""

import ipaddress
import socket
from urllib.parse import urlparse

_BLOCKED_HOSTNAMES = frozenset(
    {
        "localhost",
        "metadata.google.internal",
        "metadata.google",
    }
)

_SKIP_NETWORK_SCHEMES = frozenset({"mailto", "mailtos"})


def hostname_from_service_url(url):
    """Extract hostname from an Apprise-style or HTTP URL."""
    url = str(url or "").strip()
    if "://" not in url:
        return None
    _, rest = url.split("://", 1)
    if "@" in rest:
        rest = rest.split("@", 1)[1]
    host_part = rest.split("/", 1)[0]
    if not host_part:
        return None
    if host_part.startswith("[") and "]" in host_part:
        return host_part[1 : host_part.index("]")].lower()
    if host_part.count(":") == 1:
        host_part = host_part.rsplit(":", 1)[0]
    return host_part.lower() or None


def _is_blocked_ip(addr):
    try:
        ip = ipaddress.ip_address(addr)
    except ValueError:
        return True
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
    )


def _try_parse_ip(host):
    try:
        return ipaddress.ip_address(host)
    except ValueError:
        return None


def assert_public_outbound_host(host, *, require_resolvable=False):
    """Raise ValueError when host targets a private or internal network."""
    host = str(host or "").strip().lower().rstrip(".")
    if not host:
        raise ValueError("URL must include a hostname")
    if host in _BLOCKED_HOSTNAMES:
        raise ValueError("URL host is not allowed")
    if host.endswith(".local") or host.endswith(".internal"):
        raise ValueError("URL host is not allowed")

    literal_ip = _try_parse_ip(host)
    if literal_ip is not None:
        if _is_blocked_ip(str(literal_ip)):
            raise ValueError("URL must not target private or internal networks")
        return

    if not require_resolvable:
        return
    resolve_outbound_host(host)


def resolve_outbound_host(host):
    """Resolve host and reject private/link-local addresses (call before fetching)."""
    host = str(host or "").strip().lower().rstrip(".")
    if not host:
        raise ValueError("URL must include a hostname")
    try:
        infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise ValueError("URL hostname could not be resolved") from exc
    if not infos:
        raise ValueError("URL hostname could not be resolved")
    for info in infos:
        if _is_blocked_ip(info[4][0]):
            raise ValueError("URL must not target private or internal networks")


def _parse_service_url(url):
    url = str(url or "").strip()
    if "://" in url:
        return urlparse(url)
    return urlparse("//" + url.lstrip("/"), scheme="https")


def validate_http_service_url(url, *, require_https=False):
    """Validate http(s) or Apprise json URL targets a public host."""
    parsed = _parse_service_url(url)
    scheme = (parsed.scheme or "").lower()
    if scheme not in ("http", "https", "json", "jsons"):
        raise ValueError("URL must use http or https")
    if require_https and scheme not in ("https", "jsons"):
        raise ValueError("URL must use https")
    host = parsed.hostname or hostname_from_service_url(url)
    assert_public_outbound_host(host)
    return url


def validate_apprise_outbound_url(url):
    """Validate Apprise targets that reach network hosts."""
    url = str(url or "").strip()
    if not url or "://" not in url:
        return url
    scheme = url.split("://", 1)[0].lower()
    if scheme in _SKIP_NETWORK_SCHEMES:
        return url
    host = hostname_from_service_url(url)
    if host:
        assert_public_outbound_host(host)
    return url


def validate_smtp_host(host):
    """Validate SMTP host is not a private/internal address."""
    host = str(host or "").strip()
    if not host:
        raise ValueError("SMTP host is required")
    assert_public_outbound_host(host, require_resolvable=False)
    return host
