// A SLIPERY CLIMB - minimal service worker.
// It only exists so browsers offer "install / add to home screen".
// The game updates itself through the normal HTTP cache.
self.addEventListener("install", function () { self.skipWaiting(); });
self.addEventListener("activate", function (event) {
    event.waitUntil(self.clients.claim());
});
self.addEventListener("fetch", function (event) {
    event.respondWith(fetch(event.request));
});
