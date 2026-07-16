from pathlib import Path

from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import render

STATIC_DIR = Path(__file__).resolve().parent / "static"


def index(request):
    return render(request, "trainer/index.html")


def accords(request):
    return render(request, "trainer/accords.html")


def voiles(request):
    return render(request, "trainer/voiles.html")


def manifest(request):
    return JsonResponse(
        {
            "name": "Rubinotes — lecture de notes guitare",
            "short_name": "Rubinotes",
            "description": "Entraînement à la lecture de notes en 1ère position",
            "start_url": "/",
            "scope": "/",
            "display": "standalone",
            "background_color": "#faf8f4",
            "theme_color": "#2563eb",
            "icons": [
                {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
                {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
            ],
        },
        content_type="application/manifest+json",
    )


SW_JS = """
const CACHE = "guitar-notes-v3";
const ASSETS = ["/", "/accords", "/voiles", "/icon-192.png", "/icon-512.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// network-first : page a jour quand le serveur repond, cache en secours (offline)
self.addEventListener("fetch", (e) => {
  e.respondWith(
    fetch(e.request)
      .then((resp) => {
        const copy = resp.clone();
        caches.open(CACHE).then((c) => c.put(e.request, copy));
        return resp;
      })
      .catch(() => caches.match(e.request))
  );
});
"""


def service_worker(request):
    return HttpResponse(SW_JS, content_type="application/javascript")


def icon(request, size):
    return FileResponse(open(STATIC_DIR / f"icon-{size}.png", "rb"), content_type="image/png")
