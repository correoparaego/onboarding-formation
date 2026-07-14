from django.db import models

from employees.models import Employee


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
