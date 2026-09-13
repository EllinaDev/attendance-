const CACHE = 'qrassist-v1';
const STATIC = [
  '/',
  '/static/css/style.css',
];

self.addEventListener('install', evt => {
  evt.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(STATIC))
  );
  self.skipWaiting();
});

self.addEventListener('activate', evt => {
  evt.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
});

self.addEventListener('fetch', evt => {
  const url = new URL(evt.request.url);
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/scan/')) {
    evt.respondWith(fetch(evt.request));
    return;
  }
  if (url.pathname.startsWith('/static/') || url.pathname === '/') {
    evt.respondWith(
      caches.match(evt.request).then(cached => cached || fetch(evt.request))
    );
    return;
  }
  evt.respondWith(fetch(evt.request));
});
