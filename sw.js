// EBIME service worker · v5.2
const VERSION = '5.2';
const CACHE = 'ebime-v5.2';
const SHELL = ['./manifest.webmanifest', './ebime-logo.png', './icon-192.png', './icon-512.png'];
// Recursos que deben reflejar siempre la última versión publicada (red primero)
const FRESH = ['index.html', 'farmacos_actualizado.xlsx', 'farmacos.json'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function networkFirst(req) {
  return fetch(req).then(res => {
    const copy = res.clone();
    caches.open(CACHE).then(c => c.put(req, copy)).catch(() => {});
    return res;
  }).catch(() => caches.match(req).then(m => m || caches.match('./index.html')));
}

function cacheFirst(req) {
  return caches.match(req).then(cached => cached || fetch(req).then(res => {
    const copy = res.clone();
    caches.open(CACHE).then(c => c.put(req, copy)).catch(() => {});
    return res;
  }));
}

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = e.request.url;
  const isNav = e.request.mode === 'navigate';
  const isFresh = isNav || FRESH.some(f => url.indexOf(f) !== -1) || url.endsWith('/');
  e.respondWith(isFresh ? networkFirst(e.request) : cacheFirst(e.request));
});
