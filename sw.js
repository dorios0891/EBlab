// EBIME service worker
const VERSION = '9.7';
const CACHE = 'ebime-v9.7';
// Precache COMPLETO -> funcionamiento offline total una vez instalada.
// Las fuentes van incrustadas (base64) dentro de index.html, así que se cachean con él.
const SHELL = [
  './', './index.html', './manifest.webmanifest',
  './farmacos.json', './farmacos_actualizado.xlsx',
  './ebime-logo.png', './ebime-logo-blanco.png',
  './icon-192.png', './icon-512.png', './icon-maskable-512.png', './apple-touch-icon.png',
  './prime-logo.png',
  './prime-vasos.jpg',
  './prime-zim.jpg',
  './xlsx.full.min.js',
  './splash/splash-1125x2436.png', './splash/splash-1170x2532.png', './splash/splash-1179x2556.png', './splash/splash-1242x2208.png', './splash/splash-1242x2688.png', './splash/splash-1284x2778.png', './splash/splash-1290x2796.png', './splash/splash-1536x2048.png', './splash/splash-1620x2160.png', './splash/splash-1668x2388.png', './splash/splash-2048x2732.png', './splash/splash-640x1136.png', './splash/splash-750x1334.png', './splash/splash-828x1792.png'
];
// Con red, estos reflejan siempre la última versión publicada (red primero).
const FRESH = ['index.html', 'farmacos_actualizado.xlsx', 'farmacos.json'];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => Promise.allSettled(SHELL.map(u => c.add(new Request(u, {cache: 'reload'})))))
      .then(() => self.skipWaiting())
  );
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
  }).catch(() => undefined));
}

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = e.request.url;
  const isNav = e.request.mode === 'navigate';
  const isFresh = isNav || FRESH.some(f => url.indexOf(f) !== -1) || url.endsWith('/');
  e.respondWith(isFresh ? networkFirst(e.request) : cacheFirst(e.request));
});
