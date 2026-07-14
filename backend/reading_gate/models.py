from django.db import models

from courses.models import Course, Section
from employees.models import Employee


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ("assigned", "assigned"),
        ("in_progress", "in_progress"),
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="assigned")
    attempts_used = models.PositiveIntegerField(default=0)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("employee", "course")]  # idempotent import/enroll
        ordering = ["-enrolled_at"]

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
