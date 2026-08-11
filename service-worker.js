const CACHE_NAME = 'fathom-v15-nuke-2026-08-11';

// On install: clear all old caches and skip waiting so new SW activates immediately
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(keys.map(function(k) { return caches.delete(k); }));
    }).then(function() { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(keys.map(function(k) { if (k !== CACHE_NAME) return caches.delete(k); }));
    }).then(function() { return self.clients.claim(); })
  );
});

// Network-first strategy: always try fresh HTML from server, fall back to cache
self.addEventListener('fetch', function(event) {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    fetch(event.request).then(function(response) {
      // Cache successful responses for offline use
      if (response && response.status === 200) {
        var clone = response.clone();
        caches.open(CACHE_NAME).then(function(cache) { cache.put(event.request, clone); });
      }
      return response;
    }).catch(function() {
      return caches.match(event.request);
    })
  );
});