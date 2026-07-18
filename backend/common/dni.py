"""Spanish DNI format validation (structure + control letter).

Used by the employee-import validation report (spec employee-import
§Verbatim/§Report). This ONLY validates format; it does NOT transform the
value. The stored DNI is handled verbatim by EncryptedDNIField.
"""
import re

# 8 digits + 1 control letter. NIE (X/Y/Z prefix) is out of scope for MVP DNI.
_DNI_RE = re.compile(r"^(\d{8})([A-Za-z])$")
_CONTROL_LETTERS = "TRWAGMYFPDXBNJZSQVHLCKE"


def is_valid_dni(value) -> bool:
    """Return True if ``value`` is a structurally valid Spanish DNI.

    Checks: exactly 8 digits followed by a control letter whose position in
    the modulo-23 table matches the numeric part. Whitespace is NOT tolerated
    so callers decide explicitly whether/how to normalise (import stores DNI
    verbatim and must NOT trim).
    """
    if not isinstance(value, str):
        return False
    match = _DNI_RE.match(value)
    if not match:
        return False
    number = int(match.group(1))
    letter = match.group(2).upper()
    return _CONTROL_LETTERS[number % 23] == letter
