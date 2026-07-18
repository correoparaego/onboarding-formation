"""Notification delivery log (spec notifications §Delivery Logging).

Stores a record of every email send attempt: recipient, template, channel and
status. By design it NEVER stores the raw token, code, or any secret — only
enough to audit delivery (spec secure-access §Token Delivery, notifications §Logging).
"""
from django.db import models


class NotificationLog(models.Model):
    TEMPLATES = [
        ("access", "access"),
        ("reminder", "reminder"),
        ("completion", "completion"),
    ]
    CHANNELS = [("email", "email")]
    STATUSES = [
        ("sent", "sent"),
        ("failed", "failed"),
        ("skipped", "skipped"),  # e.g. no recipient address available
    ]

    recipient = models.EmailField()
    template = models.CharField(max_length=20, choices=TEMPLATES)
    channel = models.CharField(max_length=20, choices=CHANNELS, default="email")
    status = models.CharField(max_length=20, choices=STATUSES)
    detail = models.CharField(max_length=255, blank=True, default="")
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sent_at"]

    def __str__(self):
        return f"{self.template} -> {self.recipient} [{self.status}]"
