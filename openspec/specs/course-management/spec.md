# Delta for course-management

## ADDED Requirements

### Requirement: PDF Course Authoring

The system SHALL allow an admin to create a course by uploading a PDF and defining its ordered content sections used by the timed reader.

#### Scenario: Course created with sections

- GIVEN an admin uploads a PDF and splits it into 3 sections
- WHEN the course is saved
- THEN a course with 3 persisted sections exists and is listed in the catalog

### Requirement: Test and Question-Bank Authoring

The system SHALL allow an admin to author a question bank (single-correct-answer questions) and attach a bank to a course for comprehension testing.

WHY: The test must draw distinct subsets per attempt from a reusable bank (see comprehension-test).

#### Scenario: Bank attached to course

- GIVEN a bank of 20 single-correct questions
- WHEN the admin attaches it to a course
- THEN the course references the bank for attempt generation

### Requirement: Catalog by Position

The system SHALL maintain a catalog mapping each position to its list of mandatory courses.

#### Scenario: Position catalog lookup

- GIVEN position "Operario" mapped to courses A and B
- WHEN the catalog for "Operario" is requested
- THEN courses A and B are returned as mandatory
