# Operations — LexGreen (Fly.io)

This document captures routine ops for the production deployment on Fly.io.

Note: The live Fly app currently runs under the existing app slug and domain used by the original project name. Keep the `app` value and references below as-is to avoid disrupting the deployed instance. You can migrate/rename later when ready.

## Quick Facts
- App: `campus-greenspace-explorer`
- Primary region: `ord` (Chicago)
- Internal port: `8080` (Gunicorn)
- Volume name: `instance` → mounted at `/app/instance`
- Health check: `GET /healthz`
- Warm instance: `[http_service].min_machines_running = 1`
- One machine only (SQLite)

## First‑Time Setup (already done for main app)
- Create volume
  - `fly volumes create instance --region ord --size 3`
- Mount in `fly.toml`
  - `[[mounts]] source = "instance"; destination = "/app/instance"`
- Set secrets
  - `fly secrets set SECRET_KEY="$(openssl rand -hex 32)"`
- Deploy
  - `fly deploy`
- Initialize DB and import trees
  - `fly ssh console -C 'export FLASK_APP=app; flask init-db; flask import-trees'`
- Keep a single machine
  - `fly scale count 1`

## Day‑to‑Day
- Deploy latest code
  - `fly deploy`
- View logs
  - `fly logs`
- Check machines/volume
  - `fly machines list`
  - `fly volumes list`
- Run one‑off admin commands
  - Staff user: `fly ssh console -C 'export FLASK_APP=app; EMAIL="you@example.com" NAME="Admin" PASSWORD="strong" flask create-staff'`
  - Export work orders: `fly ssh console -C 'export FLASK_APP=app; SINCE=2025-01-01 OUT=instance/exports/work_orders.csv flask export-work-orders'`
- Database indexes (one‑time optimization)
  - `fly ssh console -C "python - <<'PY'\nimport sqlite3\nconn=sqlite3.connect('instance/UKTrees.db'); c=conn.cursor()\nc.execute('CREATE INDEX IF NOT EXISTS idx_trees_lat_lon ON trees(latitude, longitude)')\nc.execute('CREATE INDEX IF NOT EXISTS idx_trees_latin_name ON trees(latin_name)')\nconn.commit(); print('indexes added')\nPY"`

## Scaling & Availability
- Keep count at 1 for SQLite
  - `fly scale count 1`
- Memory/CPU size (example)
  - `fly scale vm shared-cpu-1x --memory 1024`
- If you ever need >1 instance, migrate to a networked database (e.g., Fly Postgres) first.

## Health & Restarts
- Health status and machine actions
  - `fly status`
  - `fly machines restart <id>`
- HTTP health check is defined in `fly.toml` and targets `/healthz`.

## Backups & Snapshots
- Volumes are encrypted and have snapshot retention configured on Fly.
- List snapshots (replace with your volume ID):
  - `fly volumes snapshots list vol_XXXX`
- Restore is performed by creating a new volume from a snapshot (see Fly docs).

## Custom Domain (optional)
- Add cert
  - `fly certs add app.example.edu`
- Point DNS
  - Create CNAME/ALIAS to `campus-greenspace-explorer.fly.dev` (or A/AAAA as instructed)
- Verify
  - `fly certs list`

## Secrets Management
- List secrets
  - `fly secrets list`
- Rotate secret (will restart the app)
  - `fly secrets set SECRET_KEY="$(openssl rand -hex 32)"`
- Note: rotating `SECRET_KEY` invalidates existing admin sessions.

## Troubleshooting
- App boot issues: `fly logs` for stack traces
- Volume attachment: ensure `VOLUME` column in `fly machines list` shows the volume id
- Region mismatch: set primary region to `ord`
  - `fly regions list`
  - `fly regions set ord`
- Stuck deploy: `fly deploy --strategy immediate`
