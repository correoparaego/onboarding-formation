"""Retention policy hook (RGPD / LOPDGDD) — task 1.4.

Centralises retention windows so later phases (certificates, expediente, audit)
can ask "how long must this entity be kept?" without hard-coding constants.
Audit logs default to indefinite retention (compliance evidence).
"""
from django.conf import settings

_DEFAULTS = {
    "employee_record_days": 365 * 5,
    "certificate_days": 365 * 5,
    "audit_days": None,  # None == retain indefinitely
}


def get_retention_policy(entity: str):
    """Return retention window in days for ``entity`` (None = indefinite)."""
    policies = getattr(settings, "RETENTION_POLICY", _DEFAULTS)
    return policies.get(entity, _DEFAULTS.get(entity))
