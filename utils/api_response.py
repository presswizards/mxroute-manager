"""Safe JSON API responses for Flask routes."""

from flask import jsonify
from markupsafe import escape

GENERIC_ERROR = "The request could not be completed."
GENERIC_UPSTREAM_ERROR = "An upstream service error occurred."
INVALID_LOG_DATE_MESSAGE = "Invalid date format; expected YYYY-MM-DD"


def escape_client_text(value):
    if value is None:
        return ""
    return str(escape(value))


def json_error(message, status=400):
    if not isinstance(message, str) or not message.strip():
        message = GENERIC_ERROR
    return jsonify({"success": False, "error": {"message": message}}), status


def sanitize_upstream_payload(payload):
    if not isinstance(payload, dict):
        return {"success": False, "error": {"message": GENERIC_UPSTREAM_ERROR}}
    if payload.get("success") is not False:
        return payload
    err = payload.get("error")
    if not isinstance(err, dict):
        return {**payload, "error": {"message": GENERIC_UPSTREAM_ERROR}}
    msg = err.get("message")
    if msg is None:
        return payload
    return {
        **payload,
        "error": {**err, "message": escape_client_text(msg)},
    }


def mx_json_response(res, status):
    if status >= 500:
        return json_error(GENERIC_UPSTREAM_ERROR, status)
    if isinstance(res, dict) and res.get("success") is False:
        res = sanitize_upstream_payload(res)
    return jsonify(res), status


def log_and_json_error(logger, message=GENERIC_ERROR, status=500):
    logger.exception(message)
    return json_error(message, status)


def client_value_error_message(exc, *, default=GENERIC_ERROR):
    if not isinstance(exc, ValueError) or not exc.args:
        return default
    msg = str(exc.args[0])
    if msg == INVALID_LOG_DATE_MESSAGE:
        return INVALID_LOG_DATE_MESSAGE
    if len(msg) <= 200 and "\n" not in msg:
        return escape_client_text(msg)
    return default
