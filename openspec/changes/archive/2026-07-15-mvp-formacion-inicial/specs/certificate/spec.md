# Delta for certificate

## ADDED Requirements

### Requirement: Printable PDF Certificate

On passing, the system SHALL generate a printable PDF certificate containing: employee full name and DNI, issue date, course title, evaluation/result, and a summary index of the training received.

WHY: Internal compliance record (RGPD assumption 2 — printable PDF, NO e-signature; formal legal validity not required at MVP).

#### Scenario: Certificate generated on pass

- GIVEN an employee passed course A
- WHEN the certificate is generated
- THEN the PDF includes name, DNI, date, "Course A", evaluation, and summary index

### Requirement: DNI Verbatim on Certificate

The certificate MUST print the DNI exactly as stored (verbatim, no formatting).

#### Scenario: DNI reproduced

- GIVEN stored DNI "12345678Z"
- WHEN the certificate renders
- THEN the printed DNI reads "12345678Z"

### Requirement: One Certificate Per Passed Enrollment

The system MUST issue at most one active certificate per passed enrollment; regeneration MUST reproduce the same content.

#### Scenario: Regeneration

- GIVEN an existing certificate for enrollment E
- WHEN the admin regenerates it
- THEN a new PDF with identical core fields is produced
