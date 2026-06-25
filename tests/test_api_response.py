from utils.api_response import escape_client_text, sanitize_upstream_payload
from utils.safe_path import path_under_base, safe_filename


def test_escape_client_text_escapes_markup():
    assert escape_client_text("<script>") == "&lt;script&gt;"


def test_sanitize_upstream_payload_escapes_error_message():
    payload = {"success": False, "error": {"message": "<bad>"}}
    sanitized = sanitize_upstream_payload(payload)
    assert sanitized["error"]["message"] == "&lt;bad&gt;"


def test_path_under_base_rejects_escape(tmp_path):
    base = tmp_path / "branding"
    base.mkdir()
    safe = path_under_base(str(base), "example.com", "logo.png")
    assert safe.endswith("logo.png")
    try:
        path_under_base(str(base), "..", "etc", "passwd")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_safe_filename_strips_directory_components():
    assert safe_filename("../secret") == "secret"
    assert safe_filename("logo.png") == "logo.png"
