# NexusDesk v0.8 — Product UI design system

The v0.8 refresh gives NexusDesk a **distinct, modern light SaaS interface**, deliberately
different from SecureScan's dark cybersecurity command-center theme.

## Color system

| Purpose | Token | Hex |
| --- | --- | --- |
| App canvas | `--canvas` | `#F5F7FA` |
| Panels / sidebar | `--surface` | `#FFFFFF` |
| Headings | `--ink` | `#192B35` |
| Body text | `--text` | `#334155` |
| Muted labels | `--muted` | `#64748B` |
| Borders | `--border` | `#E3E9ED` |
| Primary brand + buttons | `--brand` | `#0F766E` |
| Active navigation background | `--brand-soft` | `#E5F4F0` |
| Secondary informational accent | `--blue` | `#2563EB` |
| Success | `--success` | `#137A56` |
| Warning | `--warning` | `#AD6413` |
| Danger / overdue | `--danger` | `#BD3F48` |

## Visual principles

- Simple white surfaces on a quiet off-white canvas, with restrained borders and shadows
- One consistent teal primary action; secondary blue reserved for informative states
- Cleaner sidebar navigation with visible active states and a compact profile header
- Four primary dashboard KPIs, followed by three operational alert indicators
- Tables with generous space, clear headers, and compact colored status pills
- Responsive single-column detail layout and horizontally scrollable mobile navigation
- Native system fonts and no JavaScript or remote assets; compatible with strict public demo CSP

## Updated templates

The design is shared by internal pages and the fictional portfolio demo through
`desk/static/desk/style.css`, with updates to the base app shell, overview, tickets,
asset inventory, ticket detail, forms, login, and public preview.

No models, migrations, endpoint permissions, SLA calculations or database records
are changed by this UI release.

## Review checklist

On desktop and mobile, verify the sign-in screen, overview cards, ticket search,
status chips, ticket discussion, technician controls, asset inventory, and the
synthetic public preview. Use keyboard Tab navigation to check focus states.
Only staff may see administration and ticket update controls; this is enforced
server-side and remains independently covered by application tests.
