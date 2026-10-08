# GuestFlow

GuestFlow is a mobile-first Flask application for recording daily room bookings and revenue across two guest houses. It stores no guest names or payment details. Each booking snapshots the room's integer UGX price when recorded.

## Requirements

- Python 3.11+
- pip

## Setup and run

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python seed.py
python run.py
```

Open http://127.0.0.1:5000. Default demo credentials:

- Admin: `admin@guestflow.local` / `changeme123`
- Lodge A manager: `manager-a@guestflow.local` / `changeme123`
- Lodge B manager: `manager-b@guestflow.local` / `changeme123`

Replace the demo passwords and `SECRET_KEY` before deployment. For a production deployment set `COOKIE_SECURE=1` behind HTTPS. The app reads `DATABASE_URL`, `CURRENCY_CODE` (defaults to UGX), and `TIMEZONE` (defaults to Africa/Kampala) from the environment. SQLite is the local default; a PostgreSQL SQLAlchemy URL can be used for deployment.

## Seed data

`python seed.py` creates the two lodges, 18 rooms, an admin, one manager for each lodge, and up to 60 days of sample bookings. It skips seeding when properties already exist. The sample credentials are for local evaluation only.

## Tests

```powershell
python -m pytest
```

## Deployment

### Render

The root `render.yaml` defines free-tier Python 3.11 and managed PostgreSQL services, health checks, TLS-only cookies, and a first-admin setup on service startup. Connect this repository to Render as a Blueprint and provide `BOOTSTRAP_ADMIN_EMAIL` and a unique `BOOTSTRAP_ADMIN_PASSWORD` of at least 12 characters when prompted. The initializer creates the schema and the two blank lodge records; it does not copy local demo bookings or create demo managers. Add rooms and managers after signing in.

This follows your free-plan choice. Render's free web service spins down after 15 minutes idle and can take about a minute to wake; the free Postgres instance expires after 30 days and is deleted after its grace period unless upgraded. This setup is suitable for a preview, not ongoing guest-house records. See [Render's Flask guide](https://render.com/docs/deploy-flask), [Blueprint reference](https://render.com/docs/blueprint-spec), and [free plan limits](https://render.com/docs/free).

The `deploy_init.py` setup is idempotent for initial database creation. For future model changes, add and apply versioned Flask-Migrate migrations before deploying schema changes. Use `gunicorn run:app` to run the WSGI app outside Render.

## Features

- Login with admin and property-scoped manager accounts.
- Property and month filters, daily/monthly summary cards, revenue heatmap, last-30-day chart, and top rooms.
- Mobile booking entry with batch add, last-booking removal, and per-user undo.
- Date-range reports with CSV export and a copy-to-clipboard summary.
- Admin room price/property updates, soft deactivation, manager provisioning/deactivation, and property renaming.
- CSRF-protected forms, password hashing, audit records for booking changes, and installable PWA shell.

## Assumptions

- Admins see both lodges by default; selecting one lodge scopes all dashboard and report totals.
- A booking's amount never changes when its room's current price changes.
- Managers can view old dates but may add or remove bookings only for today; admins can remove any dated booking from the input screen.
- Chart.js 4.5.1 is bundled locally for offline charts. Tailwind is loaded from its development CDN; replace it with compiled CSS for a fully offline production frontend.
- Properties are the seeded two lodges and can be renamed; creating a third property is intentionally unavailable in v1.
- Date restrictions and dashboard day boundaries use the configured timezone through Python's timezone database.

## Screenshots

Screenshots can be added here after launching the app locally.

## What's next

1. Add administrator editing of booking date and snapshotted amount with an audit trail.
2. Compile and self-host Tailwind assets for a fully offline interface.
3. Add scheduled database backups and a guided production admin-password setup.

