"""Envelope encryption for sensitive fields stored at rest (DNI).

SECURITY: AES-GCM with a FRESH, cryptographically-random 12-byte nonce per
encryption call. Reusing a nonce under the same key breaks AES-GCM's security
guarantees (plaintext XOR leakage + tag forgery). The previous design used a
FIXED zero nonce (nonce reuse) — an insecure scheme that is now REPLACED.

Every ciphertext embeds its own random nonce
(``nonce (12) || ciphertext || tag``) so decryption can recover it without
storing the nonce separately.

DNI is stored VERBATIM at the logical layer: ``decrypt_value`` returns the exact
original bytes. Equality / dedupe is handled by a SEPARATE deterministic HMAC
(``dni_lookup_hash``) — see ``common.fields.HashedDNILookupField`` — NOT by a
deterministic ciphertext. This gives us both non-deterministic (secure)
storage AND stable dedupe, without leaking the DNI beyond equality.
"""
import base64
import hashlib
import hmac
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from django.conf import settings

_NONCE_LEN = 12  # 96-bit nonce for AES-GCM


def _derive_key() -> bytes:
    seed = getattr(settings, "DNI_ENCRYPTION_KEY", None) or settings.SECRET_KEY
    return hashlib.sha256(seed.encode("utf-8")).digest()  # 32 bytes for AES-256


def _derive_lookup_key() -> bytes:
    # Distinct key material for the lookup HMAC so it is not the same key used
    # for AES-GCM encryption.
    return hashlib.sha256(b"dni-lookup-v1" + _derive_key()).digest()


def encrypt_value(plaintext: str) -> str:
    """Encrypt a string -> urlsafe-base64 ciphertext with a FRESH random nonce.

    Layout: ``base64.urlsafe_b64encode(nonce (12) || ciphertext || tag)``.
    Two calls with the same plaintext produce DIFFERENT ciphertexts.
    """
    if not isinstance(plaintext, str):
        raise TypeError("encrypt_value expects a str")
    nonce = os.urandom(_NONCE_LEN)
    aes = AESGCM(_derive_key())
    ct = aes.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.urlsafe_b64encode(nonce + ct).decode("ascii")


def decrypt_value(token: str) -> str:
    """Decrypt a urlsafe-base64 ciphertext -> original string (verbatim)."""
    if not isinstance(token, str):
        raise TypeError("decrypt_value expects a str")
    raw = base64.urlsafe_b64decode(token.encode("ascii"))
    nonce, ct = raw[:_NONCE_LEN], raw[_NONCE_LEN:]
    aes = AESGCM(_derive_key())
    return aes.decrypt(nonce, ct, None).decode("utf-8")


def dni_lookup_hash(plaintext: str) -> str:
    """Deterministic HMAC-SHA256 of a DNI, for equality / dedupe lookups ONLY.

    NOT reversible and does not leak the DNI beyond equality — exactly what
    dedupe needs. Stable across re-saves (same input -> same output).
    """
    if not isinstance(plaintext, str):
        raise TypeError("dni_lookup_hash expects a str")
    return hmac.new(
        _derive_lookup_key(), plaintext.encode("utf-8"), hashlib.sha256
    ).hexdigest()


# Back-compat / migration helper: the PRE-FIX scheme stored only the ciphertext
# under a FIXED zero nonce (NO nonce prepended). Used by the employees data
# migration to re-encrypt legacy rows. Do NOT use for new data.
_LEGACY_NONCE = b"\x00" * _NONCE_LEN


def decrypt_legacy_value(token: str) -> str:
    """Decrypt a PRE-FIX ciphertext (fixed zero nonce, no nonce prepended)."""
    if not isinstance(token, str):
        raise TypeError("decrypt_legacy_value expects a str")
    raw = base64.urlsafe_b64decode(token.encode("ascii"))
    aes = AESGCM(_derive_key())
    return aes.decrypt(_LEGACY_NONCE, raw, None).decode("utf-8")
