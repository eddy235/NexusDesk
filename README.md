# NexusDesk — IT Management Platform (v0.5)

A local-first IT service desk and asset inventory application. Built using **Python, Django, SQLite, HTML/CSS**, with built-in login sessions and CSRF protection. Intended as an evolving full-stack portfolio project, not a publicly hosted multi-tenant SaaS service.

## Included in this milestone
- Authenticated IT dashboard with ticket status totals and overdue counts.
- Create, list, view and filter support tickets.
- Technician/admin updates to status, assignee and deadline, with basic audit events.
- Asset inventory; staff can register assets while employees see only assets assigned to them.
- Staff/employee permission boundaries and regression tests.
- Responsive dark command-center styling inspired by SecureScan, with keyboard focus and skip links.

## Quick start (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:DJANGO_DEBUG='true'
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

Visit `http://127.0.0.1:8000`. Sign in with the superuser account. Add non-staff users in Django Admin to test employee roles, and staff users to test technician controls. **Do not use these development settings for public deployment.**

Run tests: `python manage.py test`

## Security boundaries
- Private by default: no configured public hosting, no sample admin password and no user accounts pre-created.
- In non-debug mode, a strong `DJANGO_SECRET_KEY` must be set. Add valid hostnames, HTTPS, production database and deployment hardening before any real use.
- Employees only see tickets they report or have been assigned, and assets assigned to them. Staff can manage all tickets/assets.
- Standard Django CSRF protection and authentication. Audit trail currently captures ticket creation and ticket updates, **not every action**.
- This starter uses SQLite for development, not a production-ready shared database.
- SLA management is currently a simple deadline/overdue indicator rather than a full SLA policy engine.
- No public demo, email integration, attachments or API are included yet.

## Suggested iterations
- **v0.2:** Ticket comments, search and priorities, service category definitions.
- **v0.3:** Asset assignment history and audit coverage.
- **v0.4:** Configurable SLA policies, business hours and escalations.
- **v0.5:** PostgreSQL, secure deployment architecture and synthetic read-only portfolio demo.

## Portfolio description
NexusDesk is an IT operations dashboard supporting service requests, IT asset tracking, role-based permissions, and deadline monitoring. It demonstrates end-to-end Django development and practical security-focused application design.


## v0.2 — Helpdesk workflows

- Ticket search searches title, description and category **only among tickets the current user can access**.
- Status and priority filters can be combined with search.
- Reporters, assigned technicians and staff can comment on their visible tickets; comments and ticket-change events retain author and timestamp.
- Only staff users can change ticket status, assignment or deadline. Ticket comments and updates use separate CSRF-protected actions.
- Dashboard now surfaces active tickets without an assignee.

After pulling this release, run `python manage.py migrate` to create the comment table, then `python manage.py test`.

**Security note:** NexusDesk is currently intended for local/internal development, not a public deployment with real employee records. Do not publish a production instance without a deployment, permissions and data-protection review.


## v0.3 — Asset lifecycle and SLA monitoring

Asset inventory includes lifecycle states (Available, Assigned, Maintenance, Retired). Staff can edit assets and changes are logged as timestamped asset events with the actor and changed field names. Regular employees retain access only to assets assigned to them, and cannot modify inventory. The dashboard highlights active tickets overdue or due within the next 24 hours. These indicators are **calendar-hour deadline checks**, not a configurable business-hours SLA engine; notifications and escalations are out of scope.

Run `python manage.py migrate` after updating, then `python manage.py test`. This is still a local/internal prototype, not a production-hosted system.


## v0.4 — Configurable resolution deadlines and escalation audit

Administrators can define an optional resolution-time SLA policy for each ticket priority in Django Admin (priority, hours, start/end of the working day, enabled flag). New tickets matching a policy receive a calculated due date based on Monday–Friday business hours in the configured Django timezone. Policies do not retroactively change existing tickets; staff may still override ticket deadlines manually.

Run `python manage.py migrate` and `python manage.py test`. To record breaches, schedule `python manage.py check_sla` periodically with a trusted scheduler. This is an **audit-only escalation**: the command creates a ticket event and records the first breach. It does not send email or automatically assign tickets. Repeated runs avoid recording duplicate events unless the deadline is explicitly changed and reset. Overdue tickets with manually set deadlines are also audited.

Limitations: single fixed daily weekday working interval; no holiday calendars, overnight shifts, notifications, escalation recipient routing, or background scheduler. SQLite concurrency behavior is for local development; assess a production database and locking before multi-worker deployment.


## v0.5 — Secure portfolio demo foundation

The application now supports an **isolated, read-only public demonstration** selected by `NEXUSDESK_DEMO_MODE=true`. The demo page at `/demo/` displays hardcoded fictional tickets and inventory. All requests to login, admin, real tickets, real assets, and other internal routes are blocked in demo mode, including POST requests. The root URL redirects to the fictional overview. No demo user accounts or real records are exposed.

A `render.yaml` blueprint configures a Render web service with demo mode enabled and no database. You must connect the repository to Render yourself to deploy it; adding this file does not deploy a service. **Do not enable the internal application as a public service containing real data.**

For an internal/private installation, `DATABASE_URL` optionally selects PostgreSQL. Local development still uses SQLite unless `DATABASE_URL` is set. Production requires a secret key, explicit host/CSRF values, HTTPS and an independently reviewed deployment. Do not set `DJANGO_DEBUG=true` in demo mode. The public demo is stateless and does not run database migrations.

Local test commands:

```powershell
$env:DJANGO_DEBUG='true'
python manage.py migrate
python manage.py test
python manage.py runserver
```

After connecting a demo deployment, verify `/health/`, verify `/demo/` renders synthetic examples, and check that `/login/`, `/admin/`, `/tickets/` and POST requests do not expose write access. No claim of independent penetration testing or production certification is implied.
