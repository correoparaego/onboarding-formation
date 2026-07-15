# Delta for notifications

## ADDED Requirements

### Requirement: Configurable Email Transport

The system SHALL send email via a configurable transport (Resend or SMTP) selected by configuration; no code change required to switch provider.

#### Scenario: Provider switch

- GIVEN config sets transport=Resend
- WHEN an email is sent
- THEN it is dispatched through the Resend API

### Requirement: Spanish Templates

The system SHALL use Spanish-language email templates for all employee-facing notifications (access link, reminders, completion).

#### Scenario: Access email in Spanish

- GIVEN an employee is issued an access token
- WHEN the notification fires
- THEN the email body is Spanish and contains the magic link

### Requirement: Delivery Logging

The system SHALL record a notification attempt (recipient, template, status) without including secrets or raw tokens in logs.

#### Scenario: Logged without token

- GIVEN an access email is sent
- WHEN the send is logged
- THEN the log shows recipient + status but not the raw token
