# Delta for secure-access

## ADDED Requirements

### Requirement: Access Token/Code Issuance

The system SHALL issue a single-use, time-limited access token (delivered as a magic link and/or code) for an employee's assigned training.

WHY: Email possession is accepted as identity binding for MVP (RGPD assumption 4); the token gates entry without exposing admin credentials.

#### Scenario: Token issued on assignment

- GIVEN an employee with a pending enrollment
- WHEN access is triggered
- THEN a single-use token valid for a configured TTL is generated and associated with the employee

### Requirement: Token Delivery

The system SHALL deliver the token via the configured notification channel (email link/code) and MUST NOT log the raw token in plain audit text.

#### Scenario: Link delivered by email

- GIVEN a valid token and employee email
- WHEN delivery runs
- THEN the employee receives an email containing the magic link/code

### Requirement: Token Consumption

The system MUST invalidate the token after first successful use or TTL expiry, whichever occurs first.

#### Scenario: Reuse blocked

- GIVEN a token already consumed
- WHEN it is presented again
- THEN access is denied and a new token must be issued
