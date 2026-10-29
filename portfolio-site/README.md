# Eddy Biegon Portfolio — Dynamic CMS Edition

This version adds a small FastAPI + SQLite backend to the existing portfolio.

## What the CMS manages

- Projects: title, short description, category, tags, live link, screenshot URL, featured status and publishing.
- Certifications: title, issuer, date, description, credential link and optional image.
- Cyber Lab / TryHackMe activity: room/activity name, type, status, completion date, description and evidence link.

Public pages fetch published records from the CMS automatically. The original GitHub live feed, theme switcher, animations, project filtering, quick views and WhatsApp contact remain.

## First run locally

1. Install Python 3.11+.
2. Open a terminal in this folder.
3. Install dependencies:

   `pip install -r requirements.txt`

4. Start the site:

   `uvicorn app:app --reload`

5. Open `http://127.0.0.1:8000/`.
6. Open `http://127.0.0.1:8000/admin`.
7. On first launch, create your administrator username and password. The setup screen is disabled after the first admin is created.

The SQLite database is created automatically as `portfolio.db` and is preloaded with the existing projects and certifications.

## Production deployment

This is no longer a purely static website, so GitHub Pages and Netlify static hosting alone are not enough for the CMS. Deploy it to a Python/container host such as Railway, Render with a persistent disk, Fly.io, a VPS, or Python-capable cPanel hosting.

Important production settings:

- Set `SECRET_KEY` to a long random value.
- Set `COOKIE_SECURE=1` when the site is served over HTTPS.
- Put `portfolio.db` on persistent storage. On hosts with ephemeral filesystems set `PORTFOLIO_DB` to a path on the mounted persistent disk.
- Back up the SQLite database periodically because it contains your CMS content.

A Dockerfile is included for container deployment.

## Admin URL

`/admin`

The admin is intentionally small: add/edit/delete/publish content, then view the public site immediately.

## v6 visual + interactive update
- Public site palette now uses a black base with blue primary elements and red accents.
- Homepage includes a lightweight “Packet Defender” cybersecurity mini-game.
- The game runs fully in the browser, stores only the visitor's best score in localStorage, and does not change the CMS/database.


## Render-hosted v6 portfolio — public read-only mode

This GitHub branch includes the **original user-provided v6 FastAPI site**, including the CMS public APIs, dark/light theme toggle, animations, live GitHub feed, filterable project pages, project quick-views, Cyber Lab, contact/WhatsApp, downloadable CV, and Packet Defender mini-game.

The initial project seed and existing database upgrades now include **SecureScan** and **NexusDesk** as featured projects, with GitHub source and hosted demo links.

The free Render deployment sets `PORTFOLIO_PUBLIC_READONLY=1`. This disables `/admin` and all CMS admin APIs on the public instance to prevent first-run admin takeover and lost edits on an ephemeral SQLite filesystem. Public read-only CMS APIs continue to work. For a *private* persistent CMS installation, you need a backed-up persistent disk/database, private admin credentials, CSRF protections and an explicit deployment/security review; don't simply disable read-only mode on the public free instance.

Test: `python -m unittest discover -s tests -v`; health: `/health`.
