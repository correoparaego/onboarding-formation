# Delta for expediente

## ADDED Requirements

### Requirement: Result Storage Per Enrollment

The system SHALL store each employee's per-course result (status, attempts used, score, dates) in an expediente record linked to the employee and course.

#### Scenario: Result persisted

- GIVEN an employee passes course A on attempt 2
- WHEN the result is recorded
- THEN an expediente row stores status=passed, attempts=2, course=A

### Requirement: Admin Filter by Course Completion

The system SHALL let an admin filter employees by completion of a given course (e.g., "all who completed course X").

#### Scenario: Filter completed

- GIVEN employees E1 (passed X) and E2 (not passed X)
- WHEN the admin filters "completed course X"
- THEN only E1 is returned

### Requirement: Retention Policy

Expediente and certificate records MUST be retained per the configured retention policy (employee end + legal period) and MUST NOT be purged by application rollback.

#### Scenario: Rollback preserves

- GIVEN expediente records exist
- WHEN an app rollback occurs
- THEN the records remain intact
