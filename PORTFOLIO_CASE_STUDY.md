# NexusDesk — Portfolio Case Study

**Project:** NexusDesk — IT Service Management Platform  
**Developer:** Eddy Cheruiyot Biegon  
**Repository:** https://github.com/eddy235/NexusDesk  
**Live demo:** Add the verified Render URL after deployment (not yet verified).

## The challenge

An internal IT team needs one consistent place to log helpdesk issues, prioritize work,
manage service deadlines and keep track of equipment. A portfolio demonstration must
show the workflow without leaking real employee records or enabling anonymous writes.

## The solution

NexusDesk is a responsive Django application with authenticated, role-scoped helpdesk
and asset-management workflows. Employees can submit and comment on their own or assigned
tickets; staff technicians manage assignments and status. An inventory tracks lifecycle
states and audit events. Priority-based SLA policies calculate weekday business-hour
resolution deadlines, and a separate management command logs overdue escalation events.

A **separate, synthetic read-only demo** presents sample ticket search, filters,
dashboard metrics and equipment states. The demo deliberately does not use the
production/internal database, and blocks authentication, admin and write routes.

## Interface design

NexusDesk uses a distinct modern light SaaS identity: warm off-white canvas, white surfaces, slate text and restrained teal actions. The simplified dashboard, clear status pills and mobile-friendly navigation intentionally differ from the darker SecureScan cybersecurity project. See [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md) for tokens and UI principles.

## Technical stack

- Backend: Python, Django, Django ORM
- Database: SQLite for local development; PostgreSQL option via `DATABASE_URL`
- Frontend: Django templates, HTML, CSS, responsive accessible controls
- Security: Django sessions and CSRF, permission-filtered querysets, secure
  environment configuration, restrictive public-demo route allowlist and CSP
- Delivery: GitHub pull-request workflow and Django tests, Render Blueprint
  configuration for the standalone synthetic demo

## Features implemented

1. Support-ticket creation, statuses, assignments, staff controls, comments and timelines
2. Secure per-user visibility, search and priority/status filtering
3. Asset registration, lifecycle updates and actor/time-stamped change history
4. Optional SLA resolution policies, due-soon monitoring and audit-only breach recording
5. Synthetic read-only portfolio demonstration with search, filters and sample KPIs
6. Repeatable offline regression tests and optional external HTTP release checks

## Security design decisions

**Separate public demonstration from operational workflows.** The demo contains
hardcoded fictional records; it cannot read real tickets or user accounts.
Public routes are allowlisted; POST actions and internal URLs are rejected.
The browser uses a restrictive Content Security Policy in demo mode.

**Keep authorization on the server.** A regular employee cannot view other people's
tickets or modify the inventory. Technicians have additional privileges.

**Make service-level claims precise.** SLA calculations currently assume one
weekday work window and have no holiday calendar, email notification or automated
background scheduler. The application is a portfolio project, not a certified
production ITSM platform or a penetration-tested commercial product.

## Deployment / demo review

Before sharing the URL, verify that it shows only synthetic data; that
`/health/` reports demo mode; that CSS and filtering render correctly; and that
login/admin/private ticket URLs return 404. Run the checked-in helper:

```bash
python scripts/verify_demo_http.py https://YOUR-VERIFIED-SERVICE.onrender.com
```

Never use screenshots of real staff tickets or serial numbers for the portfolio.
Capture the demo dashboard, filtered ticket queue and synthetic asset inventory.

## Short version for the portfolio website

**NexusDesk — IT Service Management Platform**  
A full-stack Django helpdesk application for managing support requests, asset
lifecycles and service-level deadlines. Includes role-based authorization,
ticket discussions and searchable queues, audit records, automated business-hour
deadline calculations, GitHub CI and a separate synthetic read-only portfolio demo.

**Tags:** Full-Stack Development · Python · Django · IT Operations · Security · DevOps
