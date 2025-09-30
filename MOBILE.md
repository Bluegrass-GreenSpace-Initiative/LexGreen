# Mobile Packaging — LexGreen

This guide explains how to ship LexGreen to the Google Play Store (Android) and Apple App Store (iOS) while keeping a single web codebase.

## Prerequisites
- Live HTTPS site: `https://lexgreen.fly.dev` 
- PWA basics in place: Web App Manifest and Service Worker (already scaffolded in this repo)
- Accounts:
  - Google Play Console (one‑time $25)
  - Apple Developer Program ($99/year)

## 1) PWA Quality Checklist
- Manifest: `static/manifest.json`
  - `name`, `short_name`, `start_url: "/"`, `scope: "/"`, `display: "standalone"`, `theme_color`, `background_color`
  - Icons: provide crisp 192×192 and 512×512 PNGs
- Service Worker: `static/sw.js`
  - Caches `static/*` assets
  - Network‑first for `/api/*`
- Test installability
  - Chrome DevTools → Lighthouse → PWA → “Installable” should pass
  - Chrome/Android should offer “Install app”

## 2) Android — Trusted Web Activity (TWA)
TWA wraps your PWA into a Play‑store app that runs in Chrome.

- Install Bubblewrap
  - `npm i -g @bubblewrap/cli`
- Initialize from your live manifest
  - `bubblewrap init --manifest=https://lexgreen.fly.dev/static/manifest.json`
  - Set `applicationId` (e.g., keep existing if already issued, or choose a new one like `org.bluegrass.lexgreen`) and app details
- Build
  - `bubblewrap build` → outputs a signed AAB/APK (configure keystore when prompted)
- Digital Asset Links (DAL)
  - Bubblewrap prints an `assetlinks.json` snippet
  - Host it at `/.well-known/assetlinks.json` on your domain
    - Already wired: `app.py` serves `static/.well-known/assetlinks.json`
    - Replace placeholders in `static/.well-known/assetlinks.json` with your Bubblewrap output
- Publish to Play Console
  - Create app, upload the AAB, complete listing (icons/screenshots), content rating, privacy policy URL (see PRIVACY.md), rollout

### Lean maintenance model
- Keep Android wrapper minimal and separate:
  - Option A (simplest): generate the Bubblewrap project outside this repo (e.g., `~/code/lexgreen-android/`) and do not commit it here.
  - Option B: place it under `android/` in a separate repository and ignore build artifacts (`/app/build`, `/gradle`, etc.).
- Store keystore securely outside any repo. Record the SHA‑256 cert fingerprint in a safe place and in the Play Console.
- Treat the web app as the source of truth; only rebuild/publish Android when:
  - Manifest or icons change (name, theme, icons)
  - Play policies require an update
  - You need to bump the wrapper SDK or Bubblewrap template
- Handy commands:
  - `bubblewrap updateConfig --manifest=https://lexgreen.fly.dev/static/manifest.json`
  - `bubblewrap build && bubblewrap install` (for local device testing)

## 3) iOS — Capacitor Wrapper
Capacitor loads your HTTPS site in a WKWebView.

- Create a wrapper project
  - `npm create @capacitor/app@latest`
- Configure to point to your domain
  - In `capacitor.config.ts`:
    ```ts
    export default {
      appId: 'org.bluegrass.lexgreen', // 'org.bluegrass.lexgreen'
      appName: 'LexGreen',
      webDir: 'dist', // not used when loading by URL
      server: { url: 'https://lexgreen.fly.dev', cleartext: false }
    };
    ```
- Add iOS platform
  - `npm i @capacitor/ios`
  - `npx cap add ios`
- Permissions (Info.plist)
  - `NSCameraUsageDescription` (for camera uploads)
  - `NSPhotoLibraryAddUsageDescription` (saving/choosing photos)
- Build & submit
  - `npx cap open ios` → open Xcode, set signing, run on device
  - Archive and upload via Xcode to App Store Connect
  - Complete listing (icons, screenshots), privacy policy URL

## 4) Store Assets Checklist
- App name, description, keywords
- Icons and feature graphics (see platform size guides)
- Screenshots (phone + tablet where applicable)
- Privacy Policy URL: link to `PRIVACY.md` copy hosted on your domain
- Support email/website

## 5) Updates
- Web changes deploy to Fly → users get updates instantly
- Android TWA: only update when manifest/app metadata changes (icons, name) or Play policy requires
- iOS Capacitor: only update when wrapper or metadata changes; web app content updates automatically

## 6) Optional Enhancements
- Add “Add to Home Screen” in‑app prompt for non‑Chrome browsers
- Use a custom domain (CNAME to Fly) for stable branding in store listings
