from django.urls import path

from trainer.views import (
    accords,
    icon,
    index,
    manifest,
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
    path("sables", sables),
    path("sables.json", sables_data),
    path("sables/upload", sables_upload),
    path("manifest.webmanifest", manifest),
    path("sw.js", service_worker),
    path("icon-192.png", icon, {"size": 192}),
    path("icon-512.png", icon, {"size": 512}),
]
