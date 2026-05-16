"""
patterns.py

Precompiled regex patterns based on OWASP Validation Regex Repository.
https://owasp.org/www-community/OWASP_Validation_Regex_Repository

These patterns are intended for reuse in validation rules.
"""

import re

# =========================
# BASIC INPUT TYPES
# =========================

EMAIL = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

URL = re.compile(
    r"^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$"
)

IPV4 = re.compile(
    r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$"
)

IPV6 = re.compile(
    r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$"
)

# =========================
# USER INPUT
# =========================

USERNAME = re.compile(r"^[a-zA-Z0-9._-]{3,32}$")

PASSWORD_STRONG = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"
)

# =========================
# NUMERIC / FINANCIAL
# =========================

CREDIT_CARD = re.compile(r"^\d{13,19}$")

# =========================
# LOCATION / ADDRESS
# =========================

US_ZIP = re.compile(r"^\d{5}(-\d{4})?$")

US_STATE = re.compile(
    r"^(AE|AL|AK|AP|AS|AZ|AR|CA|CO|CT|DE|DC|FM|FL|GA|GU|HI|ID|IL|IN|IA|KS|KY|LA|ME|MH|MD"
    r"|MA|MI|MN|MS|MO|MP|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PW|PA|PR|RI|SC|SD|TN|TX|UT"
    r"|VT|VI|VA|WA|WV|WI|WY)$"
)

US_PHONE = re.compile(r"^\D?(\d{3})\D?\D?(\d{3})\D?(\d{4})$")

US_SSN = re.compile(r"^\d{3}-\d{2}-\d{4}$")

# =========================
# DATE / TIME
# =========================

DATE = re.compile(
    r"^(?:(?:(?:0?[13578]|1[02])(\/|-|\.)31)\1|(?:(?:0?[1,3-9]|1[0-2])(\/|-|\.)(?:29|30)\2))"
    r"(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:0?2(\/|-|\.)29\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|"
    r"(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:(?:0?[1-9])|(?:1[0-2]))(\/|-|\.)(?:0?[1-9]|1\d|2[0-8])\4"
    r"(?:(?:1[6-9]|[2-9]\d)?\d{2})$"
)

# =========================
# IDENTIFIERS
# =========================

GUID = re.compile(r"^[A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12}$")

MAC_ADDRESS = re.compile(r"^([0-9a-fA-F][0-9a-fA-F]:){5}([0-9a-fA-F][0-9a-fA-F])$")

# =========================
# SAFE TEXT
# =========================

ALPHA = re.compile(r"^[A-Za-z]+$")  # Alphabetic characters only
SAFE_TEXT = re.compile(r"^[a-zA-Z0-9 .-]+$")  # OWASP safetext pattern
SAFE_TEXT_EXTENDED = re.compile(r"^[a-zA-Z0-9\s.,\-_'\"!?()]*$")  # Extended safe text
PERSON_NAME = re.compile(r"^[a-zA-Z]+(([',. -][a-zA-Z ])?[a-zA-Z]*)*$")

DOMAIN_NAME = re.compile(r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$")

# =========================
# TOKENS
# =========================

ALPHANUMERIC = re.compile(r"^[A-Za-z0-9]+$")  # Simple alphanumeric

# =========================
# WEB DEVELOPMENT
# =========================

HEX_COLOR = re.compile(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")  # #RRGGBB or #RGB
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")  # URL-friendly slug

# =========================
# DATA FORMATS
# =========================

BASE64 = re.compile(r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$")  # Base64 encoded data
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$")  # Semantic versioning

# =========================
# TIME
# =========================

TIME_24H = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?$")  # HH:MM or HH:MM:SS (24-hour)

# =========================
# GEOGRAPHIC
# =========================

LATITUDE = re.compile(r"^(-?[1-8]?\d(?:\.\d{1,6})?|90(?:\.0{1,6})?)$")  # -90 to 90 with up to 6 decimal places
LONGITUDE = re.compile(r"^(-?(?:1[0-7]|[1-9])?\d(?:\.\d{1,6})?|180(?:\.0{1,6})?)$")  # -180 to 180 with up to 6 decimal places

# =========================
# FINANCIAL
# =========================

CURRENCY = re.compile(r"^\d+(?:\.\d{1,2})?$")  # Currency amount with optional cents