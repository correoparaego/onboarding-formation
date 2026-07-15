# Delta for authentication

## ADDED Requirements

### Requirement: Admin Password Session

The system SHALL authenticate admins via username/password and maintain an authenticated server session (e.g., Django session).

WHY: Admin actions (import, authoring, expediente) require a privileged, server-validated session distinct from employee access.

#### Scenario: Admin login

- GIVEN valid admin credentials
- WHEN the admin logs in
- THEN a server session is created and protected routes become accessible

### Requirement: Employee Magic-Link/Code Access

The system SHALL authenticate employees solely via the issued magic-link/code token (see secure-access); no password is required.

WHY: RGPD assumption 4 — email possession ≈ identity for MVP; weak binding accepted, flagged for phase-2 strengthening.

#### Scenario: Employee enters code

- GIVEN a valid unused token for employee E
- WHEN E submits the code
- THEN E is authenticated to their training scope only

### Requirement: Session Isolation

Admin sessions and employee token sessions MUST be isolated; an employee token MUST NOT grant admin routes.

#### Scenario: Employee blocked from admin

- GIVEN an authenticated employee session
- WHEN it requests an admin route
- THEN access is denied (403)

### Requirement: Admin Logout

The system SHALL invalidate the admin session on logout.

#### Scenario: Logout clears session

- GIVEN an active admin session
- WHEN logout occurs
- THEN subsequent protected requests require re-authentication
