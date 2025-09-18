# Privacy Policy — CampusGreen

Effective: 2025-09-18

This document explains what data CampusGreen collects, how it’s used, and your choices. CampusGreen is a small, university‑oriented project with minimal data collection by design.

## What We Collect
- Usage and server logs
  - Standard web server logs (IP address, user‑agent, timestamps, request paths, error traces) for diagnosis and security.
- Cookies and sessions
  - A session cookie is used for the staff/admin area authentication and quality‑of‑life features. No third‑party tracking cookies.
- User‑submitted content
  - Tree adoptions (adopter name, optional health input, user identifier you provide in the UI).
  - Damage reports (tree id, issue type, severity, free‑text description, optional user identifier).
  - Uploaded photos (image files tied to a tree id, upload timestamp).
- Official tree data
  - Public data imported from the UK tree inventory (CSV). No personal information.

## How We Use Data
- Operate and improve the service (render pages, map data, respond to API calls).
- Diagnose issues and secure the service (review logs, rate‑limit abuse).
- Display user‑submitted content in the app (adoptions, reports, photos) and in the admin portal for moderation and work order management.
- Optional notifications: If a Slack webhook is configured, high‑priority items may generate a message to a private Slack channel used by maintainers.

## Data Sharing
- We do not sell or share personal data with third parties.
- Photos and submissions are visible to other users in the context of this app (e.g., a photo on a tree’s page), and to authorized staff in the admin area.
- Hosting provider access: The app runs on Fly.io. Operational staff at the host may have access to infrastructure‑level logs and metrics as part of normal operations.

## Retention
- Database content (SQLite) and uploads are stored on a persistent volume until removed by an admin. We may periodically prune obvious test data or spam.
- Server logs are retained for a limited time sufficient for diagnostics and security, then discarded.

## Security
- Transport security: All traffic is served over HTTPS.
- Secrets are stored as platform secrets (not in source control).
- Data at rest: Fly volumes are encrypted at rest by the platform.
- Access control: Admin area requires staff login; sessions expire after inactivity.

## Your Choices
- Do not submit personal information if you prefer to remain anonymous; use the app’s features without personal identifiers where possible.
- To request removal of a photo or submission, contact the maintainer below with sufficient detail (URL, tree ID, timestamp).

## Children’s Privacy
- This app is intended for general campus audiences. We do not knowingly collect personal information from children under 13. If you believe we have, contact us to delete it.

## Changes to This Policy
- We may update this policy as the app evolves. Material changes will be noted in the repository and the app footer.

## Contact
- Maintainer: Thea Francis — thea.francis@uky.edu
- Project repository: https://github.com/Niveusgh/Campus-greenspace-explorer

