# NexusDesk v1.0 — Release Verification Checklist

This checklist distinguishes **automated tests**, **human checks**, and
**live-deployment verification**. A passing CI run does not automatically
complete the other sections.

## 1. Automated release gate

- [ ] `python -m pip check` reports compatible installed dependencies
- [ ] `python manage.py makemigrations --check --dry-run` produces no changes
- [ ] `python manage.py check` reports no errors
- [ ] `python manage.py collectstatic --noinput` succeeds
- [ ] `python manage.py test` passes all regression and end-to-end tests
- [ ] Production-like demo settings satisfy `scripts/check_release_config.py`
- [ ] Django `check --deploy` warnings are reviewed; intentional exclusions
      such as domain-wide preload are not blindly enabled

## 2. Manual internal application checks

On a fresh **local or private** setup (never the public synthetic demo):

- [ ] Create a ticket as an employee; verify it appears in the employee queue
- [ ] Confirm a different employee cannot view that ticket by guessing the URL
- [ ] Add a comment; verify author and timestamp appear in the thread
- [ ] Sign in as IT staff and assign the ticket to an **active technician**
- [ ] Verify existing deadlines display properly in the date/time field
- [ ] Resolve the ticket; verify the audit event and dashboard counts
- [ ] Register and update equipment and check its lifecycle and activity history
- [ ] Visit the staff Reports page and export a safe ticket CSV
- [ ] Confirm non-staff accounts cannot view reports or exports
- [ ] Check keyboard focus, mobile navigation, readable labels and empty states

## 3. Live public demo checks

**Never attach the live demo to operational data or admin accounts.**

- [ ] Hosting service explicitly uses demo mode, `DEBUG=false`, HTTPS and a
      secure secret key
- [ ] `/health/` reports `demo_mode: true`
- [ ] `/demo/` shows only *fictional* tickets, assets and metrics
- [ ] Search, status/priority filters and equipment-state filters work
- [ ] Static CSS renders; header/sidebar are usable on desktop and mobile
- [ ] Private login, admin, ticket, asset and reporting URLs return 404
- [ ] POST requests are rejected and CSP/security headers remain present
- [ ] Run `python scripts/verify_demo_http.py https://ACTUAL-DEMO-ORIGIN`
- [ ] Record real deployment URL and verification date before publishing it
- [ ] Capture portfolio screenshots **only** from the synthetic demo

## 4. Upgrade / rollback

1. Back up the existing local `db.sqlite3` file before replacing any files.
2. Pull the release commit, install requirements, run migrations and tests.
3. Confirm the manual workflows above and only then replace your usual setup.
4. For a broken hosted demonstration, use your hosting provider's verified
   working prior deploy; don't disable demo safeguards as a workaround.

## Release status

The GitHub CI result is machine-verifiable; actual deployment status and
manual browser checks must be marked by the project owner. **Do not mark them
complete based solely on a successful merge**.

## Live demo smoke-test evidence (29 October 2026)

The v1.0 hosted preview at https://nexusdesk-demo.onrender.com/demo/ passed the [GitHub-hosted live verification run](https://github.com/eddy235/NexusDesk/actions/runs/40844351137): synthetic v1.0 page, status/priority and asset filters, CSS, expected security headers, private routes returning 404, and write requests being rejected. Separate manual mobile visual review and a portfolio-site update are **not implied** by this successful automated test.
