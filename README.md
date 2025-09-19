# CampusGreen: Interactive Green Space Explorer

## Live Site
- https://campus-greenspace-explorer.fly.dev

## Overview
CCampusGreen is a mobile-friendly web application designed to help university students and staff discover and learn about green spaces on campus. It provides an interactive map, official UK tree data, community features (adoptions, reports), and an admin portal.

## Features
- **Interactive Campus Map**: Explore green spaces with a touch-friendly interface.
- **Green Space Details**: Learn about different types of green areas (gardens, groves, lawns).
- **Tree detail pages**: with photo gallery and uploads
- Tree APIs: list, GeoJSON, by area/species, nearby
- Adoptions, damage reports, and work orders APIs
- Admin portal (login, amenities, volunteers, CSV exports)
- PWA scaffold (installable; basic offline caching)

## Technology Stack
- Backend: Python 3 + Flask
- Templates/UI: Jinja2 + HTML/CSS + Vanilla JS
- Mapping: Leaflet.js
- Database: SQLite (instance/UKTrees.db) via a light wrapper
- Data import: Pandas (from data/UKTrees.csv)
- Production server: Gunicorn
- Compression: Flask-Compress

## Data Sources
The application uses two main data sources:
1. **UK Tree Inventory**: Official tree data from the University of Kentucky's Urban Forest Initiative
2. **User Submissions**: Custom tree identifications submitted by users

### Resource Links
- [ExploreUK](https://exploreuk.uky.edu/) - Historical campus data
- [UKY UFI](https://ufi.ca.uky.edu/) - Urban Forest Initiative
- [PG Cloud UKY](https://pg-cloud.com/UKY/) - Additional campus resources

## Getting Started

### Prerequisites
- Python 3.10+
- pip (Python package installer)

### Local setup
1) Clone and create virtualenv
```bash
git clone https://github.com/niveusgh/campus-greenspace-explorer.git
cd campus-greenspace-explorer
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2) Install dependencies
```bash
pip install -r requirements.txt
```

3) Initialize the database and import official trees (one-time)
```bash
# Option A: Flask CLI
flask --app app init-db
flask --app app import-trees

# Option B: One-shot script
python init_db.py
```

4) Run the app (development)
```bash
python app.py
```

Open http://localhost:5000

### Admin & Slack (optional)
- Create a staff user (for the internal admin portal):
  - Interactive: `flask --app app create-staff`
  - Or via env vars: `EMAIL=admin@example.com NAME="Admin" PASSWORD='yourpass' flask --app app create-staff`
  - Login at `/admin/login` (linked in the site footer)
- Slack notifications for high-priority reports (P≥3):
  - Set `SLACK_WEBHOOK_URL` in your environment before starting the app

## Deployment (for self‑hosting)

This app is already deployed at the Live Site above. The steps below are only needed if you want to host your own copy (e.g., a fork or private instance). The repo includes a Dockerfile and Fly configuration. The app uses a persistent volume mounted at `/app/instance` for the SQLite DB and uploaded photos.

1) Install and log in to Fly
```bash
brew install flyctl  
fly auth login
```

2) Initialize (no deploy yet)
```bash
fly launch --no-deploy
# Choose a region close to users (e.g., ord for Chicago)
```

3) Create a volume for SQLite + uploads
```bash
fly volumes create instance --region ord --size 3
# Use a region code (ord for Chicago). Do not use an IP.
```

4) Mount the volume (fly.toml)
Ensure this section exists (already added):
```
[[mounts]]
  source = "instance"
  destination = "/app/instance"
```

5) Set secrets (Flask session key)
```bash
fly secrets set SECRET_KEY="$(openssl rand -hex 32)"
# Alternatively generate first, then paste:
# python -c "import secrets; print(secrets.token_hex(32))"
```

6) Deploy
```bash
fly deploy
```

7) Initialize the database on the live machine (one-time)
```bash
fly ssh console -C 'export FLASK_APP=app; flask init-db; flask import-trees'
```

8) Keep exactly one machine for SQLite
```bash
fly scale count 1
# Optional to avoid cold starts: set in fly.toml under [http_service]
# min_machines_running = 1  (then `fly deploy`)
```

9) Optional performance indexes (SQLite)
```bash
fly ssh console -C "python - <<'PY'\nimport sqlite3\nconn=sqlite3.connect('instance/UKTrees.db'); c=conn.cursor()\nc.execute('CREATE INDEX IF NOT EXISTS idx_trees_lat_lon ON trees(latitude, longitude)')\nc.execute('CREATE INDEX IF NOT EXISTS idx_trees_latin_name ON trees(latin_name)')\nconn.commit(); print('indexes added')\nPY"
```

Notes
- Dockerfile runs Gunicorn on port 8080 in production.
- Flask-Compress is enabled for faster responses.
- Health checks: `/healthz` is implemented and referenced in `fly.toml` checks.
- Warm instance: `min_machines_running = 1` is set to avoid cold starts.


## Mobile (PWA, Android, iOS)
- Progressive Web App (planned): add `manifest.json` + `service worker` to enable installability and offline caching.
- Android: Trusted Web Activity (Bubblewrap) to publish the PWA to Play Store.
- iOS: Capacitor wrapper (WKWebView) to publish to App Store.

## Contributing
We welcome contributions to CampusGreen! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- University of Kentucky for providing data on campus green spaces.
- Urban Forest Initiative

## Contact
- [ambe303@uky.edu](mailto:ambe303@uky.edu)
- [neha230@uky.edu](mailto:neha230@uky.edu)
- [jtbr281@uky.edu](mailto:jtbr281@uky.edu)
- [Thea.Francis@uky.edu](mailto:Thea.Francis@uky.edu)

Project Link: https://github.com/Niveusgh/Campus-greenspace-explorer
