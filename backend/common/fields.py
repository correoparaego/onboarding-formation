"""Custom model fields.

EncryptedDNIField — stores the DNI encrypted at rest (random-nonce AES-GCM, see
common.crypto) while returning the EXACT verbatim value on read. This satisfies
BOTH the employee-import "stored verbatim, no transformation" rule AND the
RGPD encrypt-at-rest requirement (task 1.4). The random nonce means equal
plaintexts produce DIFFERENT ciphertexts, so this field is intentionally NOT
unique — dedupe / uniqueness is handled by HashedDNILookupField instead.

HashedDNILookupField — stores a deterministic HMAC-SHA256 of the DNI
(dni_lookup_hash). Used ONLY for equality lookups / dedupe, never displayed as
a DNI. It is unique=True, giving us stable per-DNI dedupe without leaking the
DNI and without a deterministic ciphertext.
"""
from django.db import models

from common.crypto import decrypt_value, dni_lookup_hash, encrypt_value

_LOOKUP_HASH_LEN = 64  # SHA-256 hexdigest


class EncryptedDNIField(models.CharField):
    description = "DNI stored encrypted at rest (random nonce) but returned verbatim."

    def __init__(self, *args, **kwargs):
        # Ciphertext is larger than the plaintext; allow generous storage.
        kwargs.setdefault("max_length", 255)
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value in (None, ""):
            return value
        return encrypt_value(value)

    def from_db_value(self, value, expression, connection):
        if value in (None, ""):
            return value
        return decrypt_value(value)


class HashedDNILookupField(models.CharField):
    description = (
        "Deterministic HMAC-SHA256 of the DNI for dedupe/equality lookups only."
    )

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", _LOOKUP_HASH_LEN)
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value in (None, ""):
            return value
        # Idempotent: if the value is already a 64-char hex hash (e.g. the
        # Employee.save() override pre-computed dni_lookup_hash), store it
        # as-is. Otherwise hash the plaintext. This keeps dedupe stable across
        # re-saves and matches the Employee.save() contract.
        if (
            isinstance(value, str)
            and len(value) == _LOOKUP_HASH_LEN
            and all(c in "0123456789abcdef" for c in value)
        ):
            return value
        return dni_lookup_hash(value)

    def from_db_value(self, value, expression, connection):
        return value
