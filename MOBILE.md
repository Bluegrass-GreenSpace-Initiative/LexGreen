# Mobile Packaging — LexGreen

This guide explains how to ship LexGreen to the Google Play Store (Android) and Apple App Store (iOS) while keeping a single web codebase.

## Prerequisites
- Live HTTPS site: `https://campus-greenspace-explorer.fly.dev` (or your custom domain)
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
  - `bubblewrap init --manifest=https://campus-greenspace-explorer.fly.dev/static/manifest.json`
  - Set `applicationId` (e.g., keep existing if already issued, or choose a new one like `org.bluegrass.lexgreen`) and app details
- Build
  - `bubblewrap build` → outputs a signed AAB/APK (configure keystore when prompted)
- Digital Asset Links (DAL)
  - Bubblewrap prints an `assetlinks.json` snippet
  - Host it at `/.well-known/assetlinks.json` on your domain
    - Easiest: create `static/.well-known/assetlinks.json` with the content Bubblewrap shows
    - Then add a tiny Flask route (example):
      ```python
      # in app.py
      @app.route('/.well-known/assetlinks.json')
      def assetlinks():
          return send_from_directory('static/.well-known', 'assetlinks.json')
      ```
- Publish to Play Console
  - Create app, upload the AAB, complete listing (icons/screenshots), content rating, privacy policy URL (see PRIVACY.md), rollout

## 3) iOS — Capacitor Wrapper
Capacitor loads your HTTPS site in a WKWebView.

- Create a wrapper project
  - `npm create @capacitor/app@latest`
- Configure to point to your domain
  - In `capacitor.config.ts`:
    ```ts
    export default {
      appId: 'edu.uky.campusgreen', // keep if already used; otherwise consider 'org.bluegrass.lexgreen'
      appName: 'LexGreen',
      webDir: 'dist', // not used when loading by URL
      server: { url: 'https://campus-greenspace-explorer.fly.dev', cleartext: false }
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
- Add an offline fallback page in the service worker for better UX when offline
- Add “Add to Home Screen” in‑app prompt for non‑Chrome browsers
- Use a custom domain (CNAME to Fly) for stable branding in store listings
