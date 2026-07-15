# Delta for comprehension-test

## ADDED Requirements

### Requirement: Maximum Three Attempts

The system MUST allow at most 3 attempts per enrollment to pass the comprehension test.

#### Scenario: Fourth attempt blocked

- GIVEN an employee has failed 3 attempts
- WHEN they request a new attempt
- THEN the system refuses and marks the enrollment as failed-exhausted

### Requirement: Distinct Question Subset Per Attempt

The system MUST present a distinct subset of questions drawn from the course question bank on each attempt, so no two attempts share the same set.

#### Scenario: Different subsets

- GIVEN a bank of 20 questions and subset size 5
- WHEN attempt 2 is generated after attempt 1
- THEN the 5 questions differ from attempt 1's 5 questions

### Requirement: Single Correct Answer

Every test question MUST have exactly one correct answer option.

#### Scenario: Validation on authoring

- GIVEN a question authored with two marked-correct options
- WHEN the bank is saved
- THEN validation rejects the question as having multiple correct answers

### Requirement: Fail Restarts Reading

On a failed attempt, the system MUST reset the employee's reading progress so the timed reader must be completed again before the next attempt.

#### Scenario: Fail triggers restart

- GIVEN an employee fails attempt 1
- WHEN they begin attempt 2
- THEN reading status returns to "in-progress" at section 1 with zero accumulated time

### Requirement: Pass Records Result

On a passing attempt, the system SHALL record the result and enable certificate generation.

#### Scenario: Pass enables cert

- GIVEN a passing score on attempt 2
- WHEN the result is saved
- THEN the enrollment status becomes "passed" and a certificate becomes available
