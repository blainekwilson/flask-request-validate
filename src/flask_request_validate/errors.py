"""
errors.py

Handles error collection and formatting.
"""

HTML_400_PAGE = "<html><body><p>There was an issue validating the data with the errors listed below.</br>Hit the back button to try again.</p>{}</body></html>"
HTML_ERROR_ITEM = "{}</br>"


def add_error(result, field, message):
    """
    Add an error to the validation result at the field level.

    :param result: Validation result dict
    :param field: Field name (string). Use the field key associated with the error.
    :param message: Human-readable error message
    """
    result["valid"] = False

    # Ensure errors is a dict mapping field -> list
    if "errors" not in result or not isinstance(result["errors"], dict):
        result["errors"] = {}

    if field not in result["errors"]:
        result["errors"][field] = []

    result["errors"][field].append(message)

    # Maintain insertion order for formatting across fields
    seq = result.setdefault("_error_sequence", [])
    seq.append((field, message))


def format_error_response(result_or_errors):
    """
    Convert errors into HTML output. Accepts either:
      - the full result dict (preferred), or
      - an errors dict mapping field -> list, or
      - a list of message strings (legacy)
    """

    def _format_pair(field, message):
        if field is not None:
            return HTML_ERROR_ITEM.format(f"{field}: {message}")
        return HTML_ERROR_ITEM.format(message)

    # Full result dict
    if isinstance(result_or_errors, dict) and "valid" in result_or_errors:
        result = result_or_errors

        seq = result.get("_error_sequence")
        if seq:
            formatted = "".join(_format_pair(f, m) for (f, m) in seq)
            return HTML_400_PAGE.format(formatted)

        errors_dict = result.get("errors") or {}
        formatted = "".join(
            _format_pair(f, m)
            for f, msgs in errors_dict.items()
            for m in msgs
        )
        return HTML_400_PAGE.format(formatted)

    # Errors dict
    if isinstance(result_or_errors, dict):
        formatted = "".join(
            _format_pair(f, m)
            for f, msgs in result_or_errors.items()
            for m in msgs
        )
        return HTML_400_PAGE.format(formatted)

    # Legacy list
    formatted = "".join(_format_pair(None, e) for e in result_or_errors)
    return HTML_400_PAGE.format(formatted)