"""Deterministic envelope encryption for sensitive fields stored at rest.

Why deterministic? DNI must remain UNIQUE (dedupe by DNI, see employee-import
spec) and queryable. A random-IV scheme would produce a different ciphertext
for the same plaintext, breaking the unique constraint and equality lookups.
Deterministic encryption (fixed nonce) means equal plaintext -> equal
ciphertext, preserving those guarantees while still encrypting the column at
rest.

SECURITY CAVEAT (MVP / pragmatic): a fixed nonce leaks plaintext equality. For
DNI this is acceptable at MVP because equality of identifiers is intentionally
known (dedupe). Before production, a security review MUST confirm the key
management and consider rotating to a non-deterministic scheme with a separate
deterministic lookup token if equality leakage becomes a concern.
"""
import base64
import hashlib

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from django.conf import settings

_FIXED_NONCE = b"\x00" * 12  # 96-bit zero nonce (deterministic for MVP)


def _derive_key() -> bytes:
    seed = getattr(settings, "DNI_ENCRYPTION_KEY", None) or settings.SECRET_KEY
    return hashlib.sha256(seed.encode("utf-8")).digest()  # 32 bytes for AES-256


def encrypt_value(plaintext: str) -> str:
    """Encrypt a string -> urlsafe-base64 ciphertext (deterministic)."""
    aes = AESGCM(_derive_key())
    ct = aes.encrypt(_FIXED_NONCE, plaintext.encode("utf-8"), None)
    return base64.urlsafe_b64encode(ct).decode("ascii")


def decrypt_value(token: str) -> str:
    """Decrypt a urlsafe-base64 ciphertext -> original string (verbatim)."""
    aes = AESGCM(_derive_key())
    raw = base64.urlsafe_b64decode(token.encode("ascii"))
    return aes.decrypt(_FIXED_NONCE, raw, None).decode("utf-8")
