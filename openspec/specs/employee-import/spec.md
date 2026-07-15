# Delta for employee-import

## ADDED Requirements

### Requirement: Excel Employee Parsing

The system SHALL accept an Excel (.xlsx) file and parse employee rows into the employee model (name, DNI, position, email, phone).

#### Scenario: Valid file imports employees

- GIVEN an uploaded .xlsx with well-formed columns
- WHEN the admin submits the import
- THEN the system creates one employee record per row and returns success count

### Requirement: DNI Stored Verbatim (RGPD)

The system MUST store the DNI exactly as entered, with NO transformation, normalization, or case-folding.

WHY: RGPD/LOPDGDD — DNI is sensitive PII; the company provides a lawful basis and Art.13/14 privacy notice. Verbatim storage ensures the recorded identifier matches the source document and any later verification.

#### Scenario: DNI preserved byte-for-byte

- GIVEN a row with DNI "12345678Z"
- WHEN the row is imported
- THEN the persisted DNI equals "12345678Z" (no trimming, no uppercasing)

### Requirement: Validation Report

The system MUST produce a per-row validation report listing accepted rows and rejected rows with reasons (missing field, malformed email, invalid DNI format).

#### Scenario: Rejected rows reported

- GIVEN a row missing email
- WHEN the import runs
- THEN that row is rejected and the report states "missing email" for it

### Requirement: Dedupe by DNI

The system MUST deduplicate rows by DNI; a second row with an existing DNI MUST be rejected or merged as a duplicate, never create a second employee.

#### Scenario: Duplicate DNI rejected

- GIVEN an existing employee with DNI "12345678Z"
- WHEN a new row with the same DNI is imported
- THEN no second employee is created and the report flags a duplicate
