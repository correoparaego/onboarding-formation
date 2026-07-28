from django.db import models

from courses.models import Course, CourseVersion, Section
from employees.models import Employee


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ("assigned", "assigned"),
        ("in_progress", "in_progress"),
        ("paused", "paused"),
        ("cancelled", "cancelled"),
        ("complete", "complete"),
        ("passed", "passed"),
        ("failed_exhausted", "failed_exhausted"),
    ]

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    course_version = models.ForeignKey(
        CourseVersion,
        on_delete=models.PROTECT,
        related_name="enrollments",
        null=True,
        blank=True,
    )
    cycle = models.PositiveIntegerField(default=1)
    source = models.CharField(max_length=30, default="position")
    assigned_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        related_name="assigned_enrollments",
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="assigned")
    attempts_used = models.PositiveIntegerField(default=0)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    paused_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-enrolled_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "course", "cycle"],
                name="unique_employee_course_cycle",
            )
        ]

    def __str__(self):
        return f"{self.employee_id} -> {self.course_id} [{self.status}]"


class ReadingProgress(models.Model):
    """Per-(enrollment, section) accumulated reading time.

    Cross-device resume is supported by keying on enrollment; device/session
    context is captured per progress row. ``reached_section`` is a denormalised
    highest-section-reached marker updated when a section completes (Phase 9
    owns the gating logic).
    """

    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name="progress"
    )
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="progress"
    )
    accumulated_time = models.PositiveIntegerField(
        default=0, help_text="Accumulated active reading time, seconds"
    )
    reached_section = models.PositiveIntegerField(default=1)
    device_id = models.CharField(max_length=120, blank=True, default="")
    session_id = models.CharField(max_length=120, blank=True, default="")

    class Meta:
        unique_together = [("enrollment", "section")]
        ordering = ["enrollment", "section"]

    def __str__(self):
        return f"progress {self.enrollment_id} s{self.section_id}: {self.accumulated_time}s"


class AuditEvent(models.Model):
    """Append-only compliance log (RGPD/LOPDGDD evidence trail).

    No update/delete API is exposed (audit-log spec); immutability is enforced at
    the API layer in later phases. The model itself only stores the record.
    """

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="audit_events",
        null=True,
        blank=True,
    )
    event_type = models.CharField(max_length=60)
    device_id = models.CharField(max_length=120, blank=True, default="")
    session_id = models.CharField(max_length=120, blank=True, default="")
    timestamp = models.DateTimeField(auto_now_add=True)
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name_plural = "audit events"

    def __str__(self):
        return f"{self.event_type} @ {self.timestamp}"


class Expediente(models.Model):
    """Per-enrollment training result (spec expediente §Result Storage).

    Linked to the employee + course. Created/updated on pass or exhaustion.
    Retained per RETENTION_POLICY; application rollback never deletes it
    (spec expediente §Retention — records survive rollback).
    """

    enrollment = models.OneToOneField(
        Enrollment, on_delete=models.CASCADE, related_name="expediente"
    )
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="expediente"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="expediente"
    )
    status = models.CharField(max_length=20, choices=Enrollment.STATUS_CHOICES)
    attempts_used = models.PositiveIntegerField(default=0)
    score = models.PositiveIntegerField(null=True, blank=True)
    total = models.PositiveIntegerField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def retention_days(self):
        from common.retention import get_retention_policy

        return get_retention_policy("employee_record_days")

    def __str__(self):
        return f"expediente {self.employee_id} / {self.course_id} [{self.status}]"
