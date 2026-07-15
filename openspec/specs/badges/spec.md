# Delta for badges

## ADDED Requirements

### Requirement: Initial Badge Set

The system SHALL define the initial badge set: "Primer curso" (first course passed), "Catálogo completo" (all mandatory courses for the position passed), and "Sin fallos" (passed with zero failed attempts).

#### Scenario: Badge set present

- GIVEN the badge catalog is initialized
- THEN the three badges exist with stable identifiers

### Requirement: Award "Primer curso"

The system SHALL award "Primer curso" when an employee passes their first course.

#### Scenario: First pass awards badge

- GIVEN an employee with no prior passes
- WHEN they pass a course
- THEN "Primer curso" is awarded

### Requirement: Award "Catálogo completo"

The system SHALL award "Catálogo completo" when all mandatory courses for the employee's position are passed.

#### Scenario: All position courses passed

- GIVEN position "Operario" requires A and B, both passed
- WHEN the second pass is recorded
- THEN "Catálogo completo" is awarded

### Requirement: Award "Sin fallos"

The system SHALL award "Sin fallos" when an employee passes a course on the first attempt with no prior failed attempts.

#### Scenario: Clean first-pass

- GIVEN an employee passes on attempt 1
- WHEN the result is saved
- THEN "Sin fallos" is awarded
