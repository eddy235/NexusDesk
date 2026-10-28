# NexusDesk — Security Scope & Disclosure

NexusDesk is a **portfolio project**, not a production-certified enterprise
IT service management service.

## Public demo

The public demonstration uses hardcoded fictional tickets and equipment. It
must run with `NEXUSDESK_DEMO_MODE=true` and `DJANGO_DEBUG=false`. In that
mode, the route guard permits only the synthetic preview, health endpoint and
static resources; internal login, admin, ticket, asset, reporting and write
routes are unavailable. A restrictive Content Security Policy, anti-framing,
HTTPS-related settings and session-cookie protections are configured.

The public demo **must never be switched into internal mode** or connected to
real employees, users, tickets or production data.

## Internal application

Django authentication and CSRF protection apply to internal forms. Employees
can see their own or assigned tickets and equipment; staff technicians have
broader access to manage support operations. Ticket assignees selected through
the application and Django Admin must be active staff accounts.

Only IT staff may view operational reports or download ticket CSV exports.
Descriptions and comments are excluded from CSV exports. Formula-like
spreadsheet values are prefixed to reduce CSV injection risks.

Application-generated ticket and asset activity events are read-only **in
Django Admin**. They are **not cryptographically tamper-evident**: trusted
server code or database administrators can still change or delete records.

## Known limitations

- No password login throttling, multi-factor authentication or external
  identity provider integration is included.
- No multi-tenant isolation; employees share one organization-level database.
- SLA rules support a single weekday time window; holidays, automatic email
  alerts and background scheduling are not provided.
- The internal application's SQLite database is for local development only.
  Use PostgreSQL and an independently reviewed security architecture for
  an organization-wide deployment.
- No independent penetration test or formal third-party vulnerability
  assessment has been performed under this release.
- GitHub CI and demo smoke tests exercise specified behaviors, not all
  possible attacks or browser/device combinations.

## Environment safety checklist

Never commit secrets, local database files, personal data or user credentials.
For the public preview, use a generated `DJANGO_SECRET_KEY`, a specific
`DJANGO_ALLOWED_HOSTS` or Render host configuration, HTTPS, and HSTS where
appropriate. Validate that `NEXUSDESK_DEMO_MODE=true` before sharing the
deployment. On first deployment and every significant change, run:

```bash
python scripts/verify_demo_http.py https://YOUR-REAL-DEMO-ORIGIN
```

Run `python manage.py check --deploy` with production-like settings and
review warnings. The GitHub pipeline also checks selected critical security
settings through `scripts/check_release_config.py`.

## Reporting security issues

Please do not share credentials or real employee data in a public GitHub issue.
Contact the repository owner privately about potential security vulnerabilities
or use GitHub private vulnerability reporting if enabled. No security service
level agreement or public incident response commitment is implied.
