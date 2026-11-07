// Offline-Speicher für die Hochlandrind-App.
// Online: immer die neueste Version vom Server holen und im Speicher ablegen.
// Offline: die gespeicherte Version zeigen.
const CACHE = 'hochlandrind-v2';
const FILES = ['./', 'index.html', 'qrcode.js', 'art.js', 'manifest.webmanifest', 'icon.svg', 'icon-192.png', 'icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin || url.pathname.endsWith('/info.json')) return;
  // Nach 3 Sekunden ohne Antwort (z. B. unterwegs ohne Heimnetz) die gespeicherte Version nehmen
  const ctl = new AbortController();
  setTimeout(() => ctl.abort(), 3000);
  e.respondWith(
    fetch(e.request, { signal: ctl.signal })
      .then(res => {
        if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
        return res;
      })
      .catch(() => caches.match(e.request, { ignoreSearch: true }).then(hit => hit || caches.match('index.html')))
  );
});
