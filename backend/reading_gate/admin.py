"""Read-only admin for the append-only audit log (spec audit-log §No Mutation).

Registering ``AuditEvent`` here (with add/change/delete all disabled) makes
the Django admin honour the compliance requirement: even a superuser cannot
edit or delete an audit row through ``/admin``. Immutability therefore holds
both at the JSON API (no create/update/delete endpoint) and in the admin UI.
"""
from django.contrib import admin

from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("id", "event_type", "enrollment", "device_id", "timestamp")
    list_filter = ("event_type",)
    search_fields = ("event_type", "device_id", "session_id")
    readonly_fields = (
        "enrollment",
        "event_type",
        "device_id",
        "session_id",
        "timestamp",
        "payload",
    )
    ordering = ("-timestamp",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
