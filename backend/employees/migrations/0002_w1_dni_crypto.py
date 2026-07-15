from django.db import connection, migrations, models

import common.crypto
import common.fields


def populate_dni_lookup(apps, schema_editor):
    """Re-encrypt legacy dni rows in the NEW (random-nonce) format and compute
    the deterministic lookup hash.

    Existing rows were stored with the PRE-FIX scheme (fixed zero nonce, no
    nonce prepended). ``decrypt_value`` (new format) fails on them, so we fall
    back to ``decrypt_legacy_value``. Rows are read/written via raw SQL to avoid
    field-conversion surprises during the migration.
    """
    from common.crypto import (
        decrypt_legacy_value,
        decrypt_value,
        dni_lookup_hash,
        encrypt_value,
    )
    import hashlib

    with connection.cursor() as cur:
        cur.execute("SELECT id, dni FROM employees_employee")
        rows = cur.fetchall()

    for pk, raw_dni in rows:
        plaintext = None
        try:
            plaintext = decrypt_value(raw_dni)
        except Exception:
            try:
                plaintext = decrypt_legacy_value(raw_dni)
            except Exception:
                plaintext = None
        if plaintext is not None:
            new_dni = encrypt_value(plaintext)
            lookup = dni_lookup_hash(plaintext)
        else:
            # Unrecoverable legacy value: keep a unique stable token so the
            # unique constraint still holds (dedupe for this row is best-effort).
            new_dni = raw_dni
            lookup = hashlib.sha256(raw_dni.encode("utf-8")).hexdigest()
        with connection.cursor() as cur:
            cur.execute(
                "UPDATE employees_employee SET dni=%s, dni_lookup=%s WHERE id=%s",
                [new_dni, lookup, pk],
            )


def reverse_populate_dni_lookup(apps, schema_editor):
    # Best-effort no-op: we cannot recover the prior deterministic ciphertext.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0001_initial"),
    ]

    operations = [
        # 1) Add the lookup column nullable so existing rows can be populated.
        migrations.AddField(
            model_name="employee",
            name="dni_lookup",
            field=models.CharField(blank=True, max_length=64, null=True, unique=False),
        ),
        # 2) Re-encrypt legacy rows + compute the lookup hash.
        migrations.RunPython(populate_dni_lookup, reverse_populate_dni_lookup),
        # 3) Enforce uniqueness + NOT NULL on the lookup column.
        migrations.AlterField(
            model_name="employee",
            name="dni_lookup",
            field=common.fields.HashedDNILookupField(blank=False, max_length=64, unique=True),
        ),
        # 4) dni is no longer the uniqueness key (ciphertext is random now).
        migrations.AlterField(
            model_name="employee",
            name="dni",
            field=common.fields.EncryptedDNIField(max_length=255),
        ),
    ]
