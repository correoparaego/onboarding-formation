# Delta for timed-reading

## ADDED Requirements

### Requirement: Server-Gated Section Unlock

The system MUST enforce the reading-time gate server-side. A section MUST NOT be marked complete or unlocked until the server has accumulated validated active time >= `minTimePerSection`, where `minTimePerSection = sectionBase / 3` (configurable per course).

WHY: Server authority is the compliance artifact; client-only gating is trivially bypassed and leaves no trustworthy evidence (RGPD assumption 3 — "reasonable control").

#### Scenario: Advance blocked before minTime

- GIVEN section base time = 90s, so minTime = 30s
- WHEN the client requests unlock after 10s of active time
- THEN the server refuses unlock and returns remaining time

### Requirement: Active-Time Accumulation via Heartbeats

The system SHALL accumulate active reading time from client activity heartbeats, rejecting gaps/heartbeats without validated visibility.

#### Scenario: Heartbeat credited

- GIVEN an open section with active heartbeats
- WHEN heartbeats arrive within tolerance
- THEN accumulated time increases by the validated delta

### Requirement: Cross-Device Resume

The system MUST persist reading progress (accumulated time + reached section) per enrollment so an employee can resume on another device.

#### Scenario: Resume on new device

- GIVEN enrollment progress of section 2 at 20s/30s on device A
- WHEN the employee opens the same enrollment on device B
- THEN device B restores section 2 at 20s accumulated

### Requirement: Completion on Full Gate Pass

The system SHALL mark reading complete only when every section's gate is satisfied, then enable the comprehension test.

#### Scenario: All sections passed

- GIVEN all sections have met minTime
- WHEN the employee finishes
- THEN reading status becomes "complete" and the test unlocks
