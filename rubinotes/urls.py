from django.urls import path

from trainer.gouvernance import gouvernance, gouvernance_logout
from trainer.views import (
    accordeur,
    accords,
    chant,
    echecs,
    icon,
    index,
    manifest,
    metronome,
    sables,
    sables_data,
    sables_upload,
    service_worker,
    voiles,
)

urlpatterns = [
    path("", index),
    path("accords", accords),
    path("voiles", voiles),
    path("echecs", echecs),
    path("chant", chant),
    path("metronome", metronome),
    path("accordeur", accordeur),
    path("sables", sables),
    path("sables.json", sables_data),
    path("gouvernance", gouvernance),
    path("gouvernance/sortir", gouvernance_logout),
    path("gouvernance/<str:slug>", gouvernance),
    path("sables/upload", sables_upload),
    path("manifest.webmanifest", manifest),
    path("sw.js", service_worker),
    path("icon-192.png", icon, {"size": 192}),
    path("icon-512.png", icon, {"size": 512}),
]
