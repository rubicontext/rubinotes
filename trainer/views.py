import json
from pathlib import Path

from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import render

from trainer.sables_io import parse_spreadsheet, record_key, with_coords

STATIC_DIR = Path(__file__).resolve().parent / "static"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
STORE = DATA_DIR / "sables_store.json"
BAKED = STATIC_DIR / "sables_geo.json"


def index(request):
    return render(request, "trainer/index.html")


def accords(request):
    return render(request, "trainer/accords.html")


def voiles(request):
    return render(request, "trainer/voiles.html")


def sables(request):
    return render(request, "trainer/sables.html")


def _load_records():
    """Store persistant s'il existe, sinon jeu de données d'origine (baked)."""
    path = STORE if STORE.exists() else BAKED
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def _save_store(recs):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps(recs, ensure_ascii=False), encoding="utf-8")


def sables_data(request):
    """Renvoie les lieux localisés (lat/lon connus), champs internes retirés."""
    out = [
        {k: r[k] for k in ("continent", "country", "place", "date", "who", "lat", "lon", "precise")}
        for r in _load_records()
        if r.get("lat") is not None
    ]
    return JsonResponse(out, safe=False)


def sables_upload(request):
    """Upload du tableur pour AJOUTER des sables (jamais de suppression)."""
    if request.method != "POST":
        return render(request, "trainer/sables_upload.html")

    f = request.FILES.get("file")
    if not f:
        return render(request, "trainer/sables_upload.html",
                      {"error": "Aucun fichier reçu."})
    try:
        recs = parse_spreadsheet(f.name, f.read())
    except Exception as exc:  # noqa: BLE001
        return render(request, "trainer/sables_upload.html",
                      {"error": f"Fichier illisible : {exc}"})

    existing = _load_records()
    keys = {record_key(r) for r in existing}
    added, dup, unlocated = 0, 0, 0
    for r in recs:
        k = record_key(r)
        if k in keys:
            dup += 1
            continue
        keys.add(k)
        rec = with_coords(r)
        if rec["lat"] is None:
            unlocated += 1
        existing.append(rec)
        added += 1
    _save_store(existing)

    total = sum(1 for r in existing if r.get("lat") is not None)
    return render(request, "trainer/sables_upload.html", {
        "result": {
            "read": len(recs), "added": added, "dup": dup,
            "unlocated": unlocated, "total": total,
        }
    })


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
const CACHE = "guitar-notes-v6";
const ASSETS = ["/", "/accords", "/voiles", "/sables", "/sables/upload", "/icon-192.png", "/icon-512.png"];

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
