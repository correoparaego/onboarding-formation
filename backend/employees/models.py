from django.db import models

from common.fields import EncryptedDNIField


class Employee(models.Model):
    """An imported employee.

    DNI is stored VERBATIM (no trim/normalise/uppercase) per the employee-import
    spec, but encrypted at rest (RGPD, task 1.4). EncryptedDNIField returns the
    exact original bytes on read, so the verbatim guarantee holds at the logical
    layer while the column is encrypted.
    """

    dni = EncryptedDNIField(unique=True)
    name = models.CharField(max_length=255)
    # Verbatim imported position label (reconciled to courses.Position later).
    position = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True, default="")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.dni})"
