# NexusDesk — Changelog

Releases are developed in feature branches and reviewed with automated Django
tests before merging into the main GitHub branch.

## v1.0 — First portfolio milestone (28 October 2026)

**Quality, security and release readiness**

- Staff assignment fields list only active IT technicians in the internal
  ticket update form and in the Django administration panel.
- Fixed the existing due-date input format for reliable editing of ticket
  deadlines using the browser's native date and time control.
- Made ticket and asset activity events read-only in Django Admin, while
  retaining the existing application-generated activity trail.
- Added integration tests for the complete employee-to-technician workflow:
  ticket creation, comments, access restrictions, assignment, resolution,
  reporting and export, as well as CSRF checks.
- Strengthened GitHub Actions with dependency-compatibility checks and
  a production-like configuration gate for the **synthetic read-only demo**.
- Published a release checklist, security scope and deployment verification
  guidance. No model changes or new database migrations.

**Important:** GitHub test success does not constitute independent security
certification, live-site verification or approval to hold real personal data.

## v0.9 — Operational reporting

Staff-only workload report and ticket CSV exports. Creation-date period
filters, status/priority/category summaries, asset counts and spreadsheet
formula-injection neutralization.

## v0.8 — Independent product UI

Refreshed the entire internal interface and public demo with a distinctive
light slate-and-teal SaaS design, responsive cards, tables and forms.

## v0.7 — Deployment verification

Added a Render health check, a deployed-demo verification script, deployment
guidance and the project portfolio case study.

## v0.6 — Interactive synthetic demo

Read-only public preview with fictional ticket search, priority/status filters
and asset lifecycle filters. Additional demo route restrictions and browser
content policy.

## v0.5 — Deployment foundation

Optional PostgreSQL configuration and a read-only synthetic Render Blueprint.
The publicly accessible demo is isolated from internal ticket routes.

## v0.4 — SLA policies

Priority-based weekday working-hours resolution deadlines and a command to
record repeat-safe overdue escalation audit events.

## v0.3 — Asset lifecycle

Track asset states and add staff-only updates with audit events, plus dashboard
deadline indicators.

## v0.2 — Helpdesk workflows

Ticket discussion, combined search and filters, technician assignment/status
controls and access regression coverage.

## v0.1 — Starter

Authenticated Django IT service desk with ticket requests, equipment inventory,
basic dashboard and initial tests.
