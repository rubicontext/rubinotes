"""Lecture des tableurs de sables (.ods et .xlsx) en pur stdlib — aucune dépendance.

Structure attendue (comme SABLES V2 VF.ods) :
  - une feuille par continent (nom de la feuille = continent)
  - colonnes : A vide, B région, C pays, D lieu, E date, F qui
"""
import io
import re
import zipfile
from xml.etree import ElementTree as ET

from trainer.geo import fold, locate

CONT = {
    "AFRIQUE": "Afrique",
    "AMERIQUE": "Amérique",
    "ASIE": "Asie",
    "EUROPE": "Europe",
    "OCEANIE": "Océanie",
}


def _continent(sheet_name):
    return CONT.get(fold(sheet_name).replace(" ", ""), sheet_name)


def _clean(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


# ----- ODS -----
_ODS_T = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
_ODS_X = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"


def _parse_ods(data):
    z = zipfile.ZipFile(io.BytesIO(data))
    root = ET.fromstring(z.read("content.xml"))
    sheets = []
    for tbl in root.iter(_ODS_T + "table"):
        name = tbl.get(_ODS_T + "name")
        rows = []
        for r in tbl.iter(_ODS_T + "table-row"):
            rep = int(r.get(_ODS_T + "number-rows-repeated", "1"))
            if rep > 50:  # lignes vides répétées en fin de feuille
                rep = 1
            cells = []
            for c in r.findall(_ODS_T + "table-cell"):
                cr = int(c.get(_ODS_T + "number-columns-repeated", "1"))
                txt = "".join(p.text or "" for p in c.iter(_ODS_X + "p")).strip()
                if cr > 50:
                    cr = 1
                cells.extend([txt] * cr)
            while cells and cells[-1] == "":
                cells.pop()
            for _ in range(rep):
                rows.append(cells)
        sheets.append((name, rows))
    return sheets


# ----- XLSX -----
_XL = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_XL_R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
_PKG_R = "{http://schemas.openxmlformats.org/package/2006/relationships}"


def _col_index(ref):
    """'C5' -> 2 (index de colonne 0-based)."""
    letters = re.match(r"[A-Z]+", ref or "A").group(0)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def _parse_xlsx(data):
    z = zipfile.ZipFile(io.BytesIO(data))
    # chaînes partagées
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        sst = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in sst.findall(_XL + "si"):
            shared.append("".join(t.text or "" for t in si.iter(_XL + "t")))
    # nom de feuille -> fichier via les relations
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid_target = {r.get("Id"): r.get("Target") for r in rels.iter(_PKG_R + "Relationship")}
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    sheets = []
    for sh in wb.iter(_XL + "sheet"):
        name = sh.get("name")
        rid = sh.get(_XL_R + "id")
        target = rid_target.get(rid, "")
        if target.startswith("/"):
            path = target.lstrip("/")          # chemin absolu depuis la racine du paquet
        elif target.startswith("xl/"):
            path = target
        else:
            path = "xl/" + target              # chemin relatif au dossier xl/
        if path not in z.namelist():
            continue
        ws = ET.fromstring(z.read(path))
        rows = []
        for row in ws.iter(_XL + "row"):
            cells = []
            for c in row.findall(_XL + "c"):
                idx = _col_index(c.get("r", "A1"))
                v = c.find(_XL + "v")
                txt = ""
                if v is not None and v.text is not None:
                    if c.get("t") == "s":
                        txt = shared[int(v.text)]
                    else:
                        txt = v.text
                elif c.find(_XL + "is") is not None:
                    txt = "".join(t.text or "" for t in c.find(_XL + "is").iter(_XL + "t"))
                while len(cells) <= idx:
                    cells.append("")
                cells[idx] = txt.strip()
            rows.append(cells)
        sheets.append((name, rows))
    return sheets


def parse_spreadsheet(filename, data):
    """Renvoie une liste de dicts {continent, region, country, place, date, who}."""
    lower = (filename or "").lower()
    is_xlsx = lower.endswith(".xlsx") or b"xl/workbook.xml" in data[:4000] or "xl/workbook.xml" in _peek(data)
    sheets = _parse_xlsx(data) if is_xlsx else _parse_ods(data)
    recs = []
    for name, rows in sheets:
        cont = _continent(name)
        for r in rows:
            r = (list(r) + [""] * 6)[:6]
            region, country, place, date, who = r[1], r[2], r[3], r[4], r[5]
            if not any([_clean(region), _clean(country), _clean(place)]):
                continue
            recs.append({
                "continent": cont,
                "region": _clean(region),
                "country": _clean(country),
                "place": _clean(place),
                "date": _clean(date),
                "who": _clean(who),
            })
    return recs


def _peek(data):
    try:
        return "\n".join(zipfile.ZipFile(io.BytesIO(data)).namelist())
    except Exception:
        return ""


def record_key(r):
    """Identité d'un sable pour dédoublonner (ajouts seulement, pas de suppression)."""
    return (fold(r.get("country")), fold(r.get("place")),
            _clean(r.get("date")).lower(), fold(r.get("who")))


def with_coords(r):
    """Ajoute lat/lon/precise à un enregistrement via la table de centroïdes."""
    coord = locate(r.get("country"))
    out = dict(r)
    out["lat"], out["lon"] = coord if coord else (None, None)
    out["precise"] = False
    return out
