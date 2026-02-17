const CACHE_NAME = 'gantt-chart-v2';
const urlsToCache = [
  '/',
  '/static/manifest.json',
  '/static/styles.css'
];

// Install service worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
  // Force the waiting service worker to become the active service worker
  self.skipWaiting();
});

// Fetch from cache
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  
  // NEVER cache API requests - always fetch fresh data
  if (url.pathname.startsWith('/add_task') || 
      url.pathname.startsWith('/get_tasks') || 
      url.pathname.startsWith('/remove_task') || 
      url.pathname.startsWith('/clear_tasks') ||
      url.pathname.startsWith('/update_task') ||
      url.pathname.startsWith('/generate_chart') ||
      url.pathname.startsWith('/download_chart') ||
      url.pathname.includes('api') ||
      event.request.method !== 'GET') {
    // Always fetch fresh for API calls and non-GET requests
    event.respondWith(fetch(event.request));
    return;
  }
  
  // For static assets, try cache first, then network
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});

// Update service worker
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      // Take control of all clients immediately
      return self.clients.claim();
    })
  );
});
