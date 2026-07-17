"""Construit trainer/static/sables_geo.json à partir de sables_src.json.

Positionne chaque lieu au centroïde de son pays / territoire (table locale
trainer/geo.py). Aucune dépendance réseau. Rejouer si le fichier source change.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from trainer.geo import fold, locate  # noqa: E402

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])

recs = json.loads(SRC.read_text(encoding="utf-8"))
out, miss = [], set()
for r in recs:
    coord = locate(r["country"])
    rec = dict(r)
    rec["lat"], rec["lon"] = coord if coord else (None, None)
    rec["precise"] = False
    if coord is None and fold(r["country"]):
        miss.add(fold(r["country"]))
    out.append(rec)

OUT.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
located = sum(1 for r in out if r["lat"] is not None)
print(f"{located}/{len(out)} lieux localises")
if miss:
    print("PAYS SANS CENTROIDE:", sorted(miss))
