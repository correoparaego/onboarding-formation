from django.db import models

from common.crypto import dni_lookup_hash
from common.fields import EncryptedDNIField, HashedDNILookupField


class Employee(models.Model):
    """An imported employee.

    DNI is stored VERBATIM (no trim/normalise/uppercase) per the employee-import
    spec, but encrypted at rest (RGPD, task 1.4). EncryptedDNIField returns the
    exact original bytes on read, so the verbatim guarantee holds at the logical
    layer while the column is encrypted.

    Because the ciphertext is now non-deterministic (random nonce), ``dni`` is
    NOT unique. Uniqueness / dedupe is enforced by ``dni_lookup`` (a
    deterministic HMAC of the DNI) — see HashedDNILookupField. This keeps the
    DNI verbatim AND rejects duplicate DNI imports without a deterministic
    ciphertext.
    """

    dni = EncryptedDNIField()
    dni_lookup = HashedDNILookupField(unique=True, blank=False)
    name = models.CharField(max_length=255)
    # Verbatim imported position label (reconciled to courses.Position later).
    position = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True, default="")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.dni})"

    def save(self, *args, **kwargs):
        # Keep the dedupe key in lockstep with the (verbatim) DNI.
        # dni_lookup_hash is deterministic, so re-saves stay stable.
        if self.dni:
            self.dni_lookup = dni_lookup_hash(self.dni)
        super().save(*args, **kwargs)
