from django.urls import path

from trainer.views import accords, icon, index, manifest, service_worker, voiles

urlpatterns = [
    path("", index),
    path("accords", accords),
    path("voiles", voiles),
    path("manifest.webmanifest", manifest),
    path("sw.js", service_worker),
    path("icon-192.png", icon, {"size": 192}),
    path("icon-512.png", icon, {"size": 512}),
]
