"""Enrollment assignment service (spec enrollment-assignment, Phase 7).

When an employee is imported with a position, one enrollment is created per
mandatory course mapped to that position in the catalog. Assignment is
idempotent by DNI+course (Enrollment.unique_together), so re-imports never
create duplicates.

The catalog uses `courses.Position` (a curated, named catalog). Employee.position
is the verbatim imported label, reconciled to a Position by case-insensitive
name or slug match.
"""
from django.utils.text import slugify

from courses.models import Position
from reading_gate.models import Enrollment


def assign_mandatory_courses(employee) -> int:
    """Create assigned enrollments for the employee's position.

    Returns the number of NEW enrollments created (skips pre-existing ones).
    """
    positions = list(Position.objects.filter(name__iexact=employee.position))
    if not positions:
        positions = list(Position.objects.filter(slug__iexact=slugify(employee.position)))
    if not positions:
        return 0

    created_total = 0
    for pos in positions:
        for course in pos.courses.all():
            _, was_created = Enrollment.objects.get_or_create(
                employee=employee,
                course=course,
                defaults={"status": "assigned"},
            )
            if was_created:
                created_total += 1
    return created_total
