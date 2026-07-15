# Delta for audit-log

## ADDED Requirements

### Requirement: Append-Only Log

The system MUST record reading and exam events in an append-only audit log; records MUST NOT be editable or deletable by application users.

WHY: Compliance evidence trail for mandatory training (idea.txt §8). RGPD assumption 8 — WORM only if mandated; MVP requires append-only immutability.

#### Scenario: Event appended

- GIVEN an enrollment completes a section
- WHEN the gate passes
- THEN a new immutable audit row is appended

### Requirement: No Mutation

The system MUST reject any update or delete operation on audit records.

#### Scenario: Delete rejected

- GIVEN an existing audit row
- WHEN a delete is attempted
- THEN the operation is denied and the row persists

### Requirement: Cross-Device Context

Each audit event MUST record device/session context (device id, session id, timestamp, enrollment id) to support cross-device evidence correlation.

#### Scenario: Context captured

- GIVEN a reading heartbeat on device D1, session S1
- WHEN the event is logged
- THEN the row stores device=D1, session=S1, enrollment, timestamp

### Requirement: Event Coverage

The system SHALL log at minimum: section unlock/complete, attempt start/submit/result, and certificate issuance.

#### Scenario: Attempt logged

- GIVEN an employee submits test attempt 2
- WHEN the submission is processed
- THEN an audit row records attempt 2 result
