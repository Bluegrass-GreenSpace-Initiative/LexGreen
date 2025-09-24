# Environment & Configuration — LexGreen

This app keeps configuration minimal. Below are the environment variables and runtime paths used in development and production.

## Required
- `SECRET_KEY`
  - Purpose: Flask session signing and CSRF protection for admin.
  - Dev: defaults to `dev` if unset; set explicitly in production.
  - Prod (Fly.io): `fly secrets set SECRET_KEY="$(openssl rand -hex 32)"`

## Optional
- `SLACK_WEBHOOK_URL`
  - Purpose: send Slack messages for high‑priority reports/work orders.
  - Format: Incoming Webhook URL (https://hooks.slack.com/services/…)
- `EMAIL`, `NAME`, `PASSWORD`
  - Purpose: one‑shot creation of a staff user via CLI.
  - Usage: `EMAIL=admin@example.com NAME="Admin" PASSWORD='strong' flask --app app create-staff`
- Export helpers (when using CLI commands):
  - `SINCE` (ISO date) and `OUT` path for `export-work-orders` (see `app.py` CLI commands).

## Files & Paths
- Database: `instance/UKTrees.db`
- Uploads root: `instance/uploads/` (per‑tree subfolders)
- Static assets: `static/`
- Templates: `templates/`

## Production Notes (Fly.io)
- Volume mount: `[[mounts]] source = "instance"; destination = "/app/instance"`
- Health check: GET `/healthz`
- Warm instance: in `fly.toml` → `[http_service].min_machines_running = 1`
- CORS: enabled broadly for development; tighten if you split frontend/domain later.
