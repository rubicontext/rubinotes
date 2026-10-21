"""Page privée « Gouvernance » : rendu des notes Markdown, protégé par mot de passe.

Les .md ne sont PAS dans le dépôt (public) : ils vivent dans GOUV_DOCS_DIR,
copiés uniquement sur le serveur. Sans GOUV_PASSWORD, la page n'existe pas (404).
"""
import hmac
import re
import time

from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render

COOKIE = "gouv_auth"
SALT = "gouvernance"
MAX_AGE = 30 * 24 * 3600
SLUG_RE = re.compile(r"^\d{2}_[A-Za-z0-9_]+$")
MD_LINK_RE = re.compile(r'href="(\d{2}_[A-Za-z0-9_]+)\.md(#[^"]*)?"')
HOME = "00_README"


def _is_authenticated(request):
    return request.get_signed_cookie(COOKIE, default=None, salt=SALT, max_age=MAX_AGE) == "1"


def _no_index(response):
    response["X-Robots-Tag"] = "noindex, nofollow"
    response["Cache-Control"] = "private, no-store"
    return response


def _docs():
    """Liste (slug, titre) des notes, dans l'ordre des numéros."""
    docs = []
    for path in sorted(settings.GOUV_DOCS_DIR.glob("*.md")):
        if SLUG_RE.match(path.stem):
            title = _title(path.read_text(encoding="utf-8"), path.stem)
            docs.append((path.stem, _short(title)))
    return docs


def _short(title):
    """Libellé de sommaire : le titre sans ses précisions (« — … », « (…) »)."""
    for sep in (" — ", " ("):
        title = title.split(sep)[0]
    return title


def _title(text, fallback):
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def _render(text):
    # import local : si la lib manque, seule cette page tombe, pas tout le site
    import markdown

    html = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists", "toc"])
    html = MD_LINK_RE.sub(lambda m: f'href="/gouvernance/{m.group(1)}{m.group(2) or ""}"', html)
    return html.replace("<li>[ ] ", "<li>☐ ").replace("<li>[x] ", "<li>☑ ")


def gouvernance(request, slug=HOME):
    if not settings.GOUV_PASSWORD:
        raise Http404

    if request.method == "POST":
        password = request.POST.get("password", "")
        if hmac.compare_digest(password.encode(), settings.GOUV_PASSWORD.encode()):
            response = HttpResponseRedirect(request.path)
            response.set_signed_cookie(
                COOKIE, "1", salt=SALT, max_age=MAX_AGE,
                httponly=True, secure=not settings.DEBUG, samesite="Lax",
            )
            return response
        time.sleep(1)  # freine les essais en rafale
        return _no_index(render(request, "trainer/gouvernance_login.html",
                                {"error": "Mot de passe incorrect."}, status=403))

    if not _is_authenticated(request):
        return _no_index(render(request, "trainer/gouvernance_login.html"))

    if not SLUG_RE.match(slug):
        raise Http404
    path = settings.GOUV_DOCS_DIR / f"{slug}.md"
    if not path.is_file():
        raise Http404

    text = path.read_text(encoding="utf-8")
    return _no_index(render(request, "trainer/gouvernance.html", {
        "docs": _docs(),
        "current": slug,
        "title": _title(text, slug),
        "content": _render(text),
    }))


def gouvernance_logout(request):
    response = HttpResponseRedirect("/gouvernance")
    response.delete_cookie(COOKIE)
    return response
