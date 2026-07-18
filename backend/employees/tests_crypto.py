"""Security-fix tests for W1: DNI crypto (random nonce) + verbatim + dedupe.

Covers the four acceptance checks from the fix brief:
  (a) DNI round-trips VERBATIM (no trim/normalize);
  (b) equal DNIs -> DIFFERENT ciphertext but the SAME dni_lookup;
  (c) importing a duplicate DNI is rejected via dni_lookup;
  (d) the old fixed-nonce scheme is gone (no _FIXED_NONCE).
Plus a back-compat check that PRE-FIX (fixed-nonce) ciphertexts are still
recoverable by the migration helper.
"""
import inspect
import io

import pandas as pd
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

import common.crypto as crypto
from common.crypto import (
    _derive_key,
    decrypt_legacy_value,
    decrypt_value,
    dni_lookup_hash,
    encrypt_value,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from employees.models import Employee


class DniCryptoTests(TestCase):
    def test_dni_roundtrip_verbatim(self):
        # (a) verbatim — including spaces and a lowercase control letter.
        e = Employee.objects.create(
            dni="  Spaced DNI 12345678z ",
            name="A",
            position="X",
            email="a@e.com",
        )
        e.refresh_from_db()
        self.assertEqual(e.dni, "  Spaced DNI 12345678z ")

    def test_equal_dnis_diff_ciphertext_same_lookup(self):
        # (b) same plaintext -> different ciphertext, same lookup hash.
        c1 = encrypt_value("12345678Z")
        c2 = encrypt_value("12345678Z")
        self.assertNotEqual(c1, c2)
        self.assertEqual(dni_lookup_hash("12345678Z"), dni_lookup_hash("12345678Z"))
        self.assertNotEqual(
            dni_lookup_hash("12345678Z"), dni_lookup_hash("12345678Y")
        )

    def test_duplicate_dni_rejected_via_lookup(self):
        # (c) model-level: a second Employee with the same DNI collides on the
        # unique dni_lookup, not on the (now random) dni ciphertext.
        Employee.objects.create(
            dni="12345678Z", name="A", position="X", email="a@e.com"
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Employee.objects.create(
                    dni="12345678Z", name="B", position="Y", email="b@e.com"
                )

    def test_import_rejects_duplicate_dni(self):
        # (c) end-to-end: the import view dedupes via dni_lookup.
        User = get_user_model()
        admin = User.objects.create_user("adm_w1", "adm_w1@x.com", "pw", is_staff=True)
        self.client.force_login(admin)

        df = pd.DataFrame(
            [
                {"dni": "12345678Z", "name": "Juan", "position": "X", "email": "j@e.com"},
                {"dni": "12345678Z", "name": "Juan2", "position": "X", "email": "j2@e.com"},
            ]
        )
        buf = io.BytesIO()
        df.to_excel(buf, index=False)
        buf.seek(0)

        resp = self.client.post("/api/import", data={"file": buf}, format="multipart")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["created"], 1)
        self.assertEqual(body["duplicates"], 1)
        self.assertEqual(Employee.objects.count(), 1)

        # The surviving row's DNI is verbatim and its lookup is stable.
        emp = Employee.objects.get()
        self.assertEqual(emp.dni, "12345678Z")
        self.assertEqual(emp.dni_lookup, dni_lookup_hash("12345678Z"))

    def test_fixed_nonce_gone(self):
        # (d) the insecure fixed-nonce scheme is removed.
        self.assertFalse(hasattr(crypto, "_FIXED_NONCE"))
        src = inspect.getsource(crypto)
        self.assertNotIn("_FIXED_NONCE", src)
        # New scheme embeds a fresh random nonce: two encryptions differ AND
        # the raw ciphertext is longer than the plaintext (nonce prepended).
        ct = encrypt_value("12345678Z")
        raw = __import__("base64").urlsafe_b64decode(ct.encode("ascii"))
        self.assertGreater(len(raw), 12)  # nonce(12) + ct + tag
        # Random nonce => distinct ciphertexts even for identical plaintext.
        self.assertNotEqual(encrypt_value("12345678Z"), encrypt_value("12345678Z"))

    def test_legacy_ciphertext_recoverable(self):
        # Back-compat: PRE-FIX fixed-zero-nonce ciphertexts are still readable
        # by the migration helper, and re-encryption + hashing stays consistent.
        aes = AESGCM(_derive_key())
        legacy_ct = __import__("base64").urlsafe_b64encode(
            aes.encrypt(b"\x00" * 12, b"12345678Z", None)
        ).decode("ascii")
        self.assertEqual(decrypt_legacy_value(legacy_ct), "12345678Z")
        # New path round-trips and hashes deterministically.
        new_ct = encrypt_value("12345678Z")
        self.assertEqual(decrypt_value(new_ct), "12345678Z")
        self.assertEqual(dni_lookup_hash("12345678Z"), dni_lookup_hash("12345678Z"))
