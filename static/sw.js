/* Simple service worker for LexGreen */
const CACHE_VERSION = 'v2';
const STATIC_CACHE = `static-${CACHE_VERSION}`;

// Core assets to pre-cache (keep tiny)
const PRECACHE_URLS = [
  '/',
  '/static/css/main.css',
  '/static/images/logo.png',
  '/static/images/favicon.ico',
  '/static/offline.html',
  '/static/fonts/Inter-Variable.woff2',
  '/static/fonts/Inter-Italic-Variable.woff2'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(PRECACHE_URLS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((k) => k !== STATIC_CACHE).map((k) => caches.delete(k))
    ))
  );
  self.clients.claim();
});

// Cache strategies
self.addEventListener('fetch', (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Only handle GET
  if (req.method !== 'GET') return;

  // HTML navigation requests: network first, offline fallback
  const accept = req.headers.get('accept') || '';
  if (req.mode === 'navigate' || accept.includes('text/html')) {
    event.respondWith(
      fetch(req).catch(() => caches.match('/static/offline.html'))
    );
    return;
  }

  // API: network-first to keep data fresh
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(req));
    return;
  }

  // Map tiles (OpenStreetMap): stale-while-revalidate
  if (url.host.includes('tile.openstreetmap.org')) {
    event.respondWith(staleWhileRevalidate(req));
    return;
  }

  // Static assets: cache-first
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(cacheFirst(req));
    return;
  }

  // Default: try network, fallback to cache
  event.respondWith(networkThenCache(req));
});

async function cacheFirst(req) {
  const cache = await caches.open(STATIC_CACHE);
  const cached = await cache.match(req);
  if (cached) return cached;
  const fresh = await fetch(req);
  cache.put(req, fresh.clone());
  return fresh;
}

async function staleWhileRevalidate(req) {
  const cache = await caches.open(STATIC_CACHE);
  const cached = await cache.match(req);
  const network = fetch(req).then((res) => { cache.put(req, res.clone()); return res; });
  return cached || network;
}

async function networkFirst(req) {
  const cache = await caches.open(STATIC_CACHE);
  try {
    const fresh = await fetch(req);
    cache.put(req, fresh.clone());
    return fresh;
  } catch (e) {
    const cached = await cache.match(req);
    if (cached) return cached;
    throw e;
  }
}

async function networkThenCache(req) {
  const cache = await caches.open(STATIC_CACHE);
  try {
    const fresh = await fetch(req);
    cache.put(req, fresh.clone());
    return fresh;
  } catch (e) {
    const cached = await cache.match(req);
    if (cached) return cached;
    throw e;
  }
}
