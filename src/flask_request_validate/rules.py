"""
rules.py

Reusable validation rules built on top of OWASP-based regex patterns.
"""

from .patterns import *
from .errors import add_error
import re

# Import patterns that conflict with rule names
from .patterns import USERNAME as USERNAME_PATTERN
from .patterns import US_STATE as US_STATE_PATTERN


# =========================
# RULE DEFINITIONS
# =========================

TEXT = {
    "type": "str",
    "min": 1,
    "max": 1024,
}

EMAIL = {
    "type": "str",
    "regex": EMAIL,
    "error": "Invalid email address",
}

URL = {
    "type": "str",
    "regex": URL,
    "error": "Invalid URL",
}

USERNAME = {
    "type": "str",
    "regex": USERNAME,
    "error": "Invalid username",
}

PASSWORD_STRONG = {
    "type": "str",
    "regex": PASSWORD_STRONG,
    "error": "Password must meet complexity requirements",
}

CREDIT_CARD = {
    "type": "str",
    "regex": CREDIT_CARD,
    "error": "Invalid credit card number format",
}

US_STATE = {
    "type": "str",
    "regex": US_STATE,
    "error": "Invalid US state",
}

US_ZIP = {
    "type": "str",
    "regex": US_ZIP,
    "error": "Invalid ZIP code",
}

US_PHONE = {
    "type": "str",
    "regex": US_PHONE,
    "error": "Invalid US phone number",
}

US_SSN = {
    "type": "str",
    "regex": US_SSN,
    "error": "Invalid US Social Security Number",
}

DATE = {
    "type": "str",
    "regex": DATE,
    "error": "Invalid date format",
}

GUID = {
    "type": "str",
    "regex": GUID,
    "error": "Invalid GUID format",
}

MAC_ADDRESS = {
    "type": "str",
    "regex": MAC_ADDRESS,
    "error": "Invalid MAC address format",
}

PERSON_NAME = {
    "type": "str",
    "regex": PERSON_NAME,
    "error": "Invalid person name",
}

DOMAIN_NAME = {
    "type": "str",
    "regex": DOMAIN_NAME,
    "error": "Invalid domain name",
}


# --- Compatibility with original validate.py (same patterns and messages) ---

SAFE_USERNAME = {
    "min": 6,
    "max": 20,
    "type": "str",
    "regex": ALPHANUMERIC,
    "error": "must be letters and/or numbers",
}

SAFE_TEXT = {
    "min": 1,
    "max": 1024,
    "type": "str",
    "regex": SAFE_TEXT,
    "error": "must be letters and spaces",
}

SAFE_US_STATE = {
    "min": 2,
    "max": 2,
    "type": "str",
    "regex": US_STATE_PATTERN,
    "error": "must be a US state",
}

SAFE_ALPHA = {
    "min": 2,
    "max": 10,
    "type": "str",
    "regex": ALPHA,
    "error": "must be letters",
}

HEX_COLOR = {
    "type": "str",
    "regex": HEX_COLOR,
    "error": "Invalid hex color format",
}

SLUG = {
    "type": "str",
    "regex": SLUG,
    "error": "Invalid slug format",
}

BASE64 = {
    "type": "str",
    "regex": BASE64,
    "error": "Invalid base64 format",
}

SEMVER = {
    "type": "str",
    "regex": SEMVER,
    "error": "Invalid semantic version format",
}

TIME_24H = {
    "type": "str",
    "regex": TIME_24H,
    "error": "Invalid 24-hour time format",
}

LATITUDE = {
    "type": "str",
    "regex": LATITUDE,
    "error": "Invalid latitude format",
}

LONGITUDE = {
    "type": "str",
    "regex": LONGITUDE,
    "error": "Invalid longitude format",
}

CURRENCY = {
    "type": "str",
    "regex": CURRENCY,
    "error": "Invalid currency format",
}


def set_min_max(base_dict, minimum=-1, maximum=-1) -> dict:
    temp_dict = {}
    for key in base_dict:
        temp_dict[key] = base_dict[key]
    temp_dict["min"] = minimum
    temp_dict["max"] = maximum
    return temp_dict


# =========================
# RULE ENGINE
# =========================

def check_rule(key, value, rule, result):
    rule_type = rule.get("type")

    if rule_type == "str":
        check_string(key, value, rule, result)
    elif rule_type == "int":
        check_int(key, value, rule, result)
    elif rule_type == "float":
        check_float(key, value, rule, result)
    elif rule_type == "bool":
        check_bool(key, value, result)
    else:
        add_error(result, key, f"{key} has unknown rule type")


def check_string(key, value, rule, result):
    if not isinstance(value, str):
        value = str(value)

    min_v = rule.get("min", -1)
    max_v = rule.get("max", -1)

    if min_v != -1 and len(value) < min_v:
        add_error(result, key, f"{key} must be longer than {min_v} characters")

    if max_v != -1 and len(value) > max_v:
        add_error(result, key, f"{key} must be shorter than {max_v} characters")

    if "regex" in rule:
        pattern = rule["regex"]
        if isinstance(pattern, str):
            matched = re.search(pattern, value)
        else:
            matched = pattern.search(value)
        if not matched:
            err = rule.get("error", "has invalid format")
            add_error(result, key, f"{key} {err}")


def check_int(key, value, rule, result):
    minimum = rule.get("min", -1)
    maximum = rule.get("max", -1)
    try:
        temp = int(value)
    except (ValueError, TypeError):
        add_error(result, key, f"{key} must be a whole number")
        return

    if minimum != -1 and temp < minimum:
        add_error(result, key, f"{key} cannot be less than {minimum}")

    if maximum != -1 and temp > maximum:
        add_error(result, key, f"{key} cannot be greater than {maximum}")


def check_float(key, value, rule, result):
    minimum = rule.get("min", -1.0)
    maximum = rule.get("max", -1.0)
    try:
        temp = float(value)
    except (ValueError, TypeError):
        add_error(result, key, f"{key} must be a number")
        return

    if minimum != -1 and temp < minimum:
        add_error(result, key, f"{key} cannot be less than {minimum}")

    if maximum != -1 and temp > maximum:
        add_error(result, key, f"{key} cannot be greater than {maximum}")


def check_bool(key, value, result):
    s = value if isinstance(value, str) else str(value)
    if s.lower() not in ("true", "false"):
        add_error(result, key, f"{key} must be true or false")
