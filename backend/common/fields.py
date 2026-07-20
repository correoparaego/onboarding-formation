"""Custom model fields.

EncryptedDNIField — stores the DNI encrypted at rest (deterministic, see
common.crypto) while returning the EXACT verbatim value on read. This satisfies
BOTH the employee-import "stored verbatim, no transformation" rule (the logical
value is byte-for-byte identical) AND the RGPD encrypt-at-rest requirement
(task 1.4). The unique constraint is preserved because encryption is
deterministic (same DNI -> same ciphertext).
"""
from django.db import models

from common.crypto import decrypt_value, encrypt_value


class EncryptedDNIField(models.CharField):
    description = "DNI stored encrypted at rest but returned verbatim."

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
