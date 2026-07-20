from django.db import models

from employees.models import Employee
from reading_gate.models import Enrollment


class Badge(models.Model):
    slug = models.SlugField(max_length=80, unique=True)
    label = models.CharField(max_length=160)

    class Meta:
        ordering = ["slug"]

    def __str__(self):
        return self.label


class EmployeeBadge(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="badges"
    )
    badge = models.ForeignKey(
        Badge, on_delete=models.CASCADE, related_name="awards"
    )
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("employee", "badge")]

    def __str__(self):
        return f"{self.employee_id} <- {self.badge.slug}"


class Certificate(models.Model):
    """One active certificate per passed enrollment (spec certificate §One Per).

    The PDF is rendered on demand (deterministic) when an admin requests it, so
    this row mainly records issuance and a hash of the core fields to prove
    idempotent regeneration (spec certificate §Regeneration).
    """

    enrollment = models.OneToOneField(
        Enrollment, on_delete=models.CASCADE, related_name="certificate"
    )
    issued_at = models.DateTimeField(auto_now_add=True)
    core_fields_hash = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-issued_at"]

    def __str__(self):
        return f"cert for enrollment {self.enrollment_id}"
