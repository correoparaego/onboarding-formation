# Delta for enrollment-assignment

## ADDED Requirements

### Requirement: Mandatory Assignment Per Position

When an employee is imported with a position, the system SHALL create one enrollment per mandatory course defined for that position in the catalog.

WHY: Compliance requires every employee to complete the legally mandated training for their role; assignment must be automatic and auditable.

#### Scenario: Auto-enrollment on import

- GIVEN position "Operario" maps to courses A and B
- WHEN an employee with position "Operario" is imported
- THEN two enrollments (A, B) are created in "assigned" state

### Requirement: Assignment Idempotency

The system MUST NOT create a duplicate enrollment when an employee is re-imported (idempotent by DNI+course).

#### Scenario: Re-import skips duplicates

- GIVEN an employee already enrolled in course A
- WHEN the same employee is re-imported
- THEN no second enrollment for course A is created
