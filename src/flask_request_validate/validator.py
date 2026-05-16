"""
validator.py

Core validation engine.

This module:
- processes validation rules
- evaluates request data
- returns structured validation results

NOTE: This module is framework-agnostic (no Flask imports).
"""

from .rules import check_rule
from .errors import add_error


def validate_request_data(rules, request_data):
    """
    Validate incoming request data against rules.

    :param rules: Validation rules
    :param request_data: Dict containing form, args, etc.
    :return: dict with validation result
    """

    result = {
        "valid": True,
        "errors": {}
    }

    for section in ["form", "query_string", "cookie", "header"]:
        if section not in request_data:
            continue

        if section == "form" and request_data.get("method") != "POST":
            continue

        section_data = request_data[section]
        section_rules = rules.get(section, {})

        # Check required fields
        for key, rule in section_rules.items():
            if rule.get("required") and key not in section_data:
                add_error(result, key, f"Missing {section} data: {key}")

        # Original validate.py only rejects undeclared keys for form and query_string.
        if section in ("form", "query_string"):
                for key, value in section_data.items():
                    # Ignore internal CSRF token field injected by flask-request-validate when enabled
                    if key == 'flask_validate_csrf_token':
                        continue
                    if key not in section_rules:
                        add_error(result, key, "Unexpected data received")
                        continue

                    rule = section_rules[key]["rules"]
                    check_rule(key, value, rule, result)
        else:
            for key in section_rules:
                if key not in section_data:
                    continue
                value = section_data[key]
                rule = section_rules[key]["rules"]
                check_rule(key, value, rule, result)

    return result