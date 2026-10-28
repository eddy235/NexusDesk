# NexusDesk — IT Management Platform (v0.1)

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
