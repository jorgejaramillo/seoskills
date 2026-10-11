#!/usr/bin/env python3
"""Métricas de imágenes a partir de seo_extract (idealmente con --head-images) → sección seo-images.

Uso:
  python3 shared/seo_extract.py https://example.com --head-images -o pages.json
  python3 images/scripts/image_metrics.py pages.json
"""
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))
import report_io as rio  # noqa: E402

LEGACY = {"jpg", "jpeg", "png", "gif", "bmp"}
GENERIC_NAME = re.compile(r"^(img|dsc|image|photo|foto|screenshot|captura|untitled)[-_ ]?\d*", re.I)
GENERIC_ALT = {"image", "imagen", "foto", "photo", "logo", "img", "picture", "banner", "icon", "icono"}


def fmt(img):
    t = (img.get("head_type") or "").split("/")[-1].split(";")[0]
    return {"jpeg": "jpg", "svg+xml": "svg"}.get(t, t) or img.get("ext") or "?"


def kb(b):
    return round(b / 1024) if b else 0


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    pages = [p for p in rio.load_pages(sys.argv[1]) if not p.get("error")]
    site = rio.domain_of(pages[0]["url"])

    # Una imagen = una URL única; los problemas de marcado se cuentan por aparición
    tags = [(p, img) for p in pages for img in p["images"] if img.get("url")]
    unique = {}
    for _, img in tags:
        unique.setdefault(img["url"], img)
    n_tags, n_unique = len(tags), len(unique)
    if not n_tags:
        sys.exit("No se encontraron imágenes")
    has_sizes = any(i.get("head_bytes") for i in unique.values())

    no_alt = [(p, i) for p, i in tags if not i["has_alt"]]
    empty_alt = [(p, i) for p, i in tags if i["has_alt"] and not (i["alt"] or "").strip()]
    generic_alt = [(p, i) for p, i in tags if (i["alt"] or "").strip().lower() in GENERIC_ALT]
    no_dims = [(p, i) for p, i in tags if not (i["width"] and i["height"])]
    no_lazy = [(p, i) for p, i in tags if i["loading"] != "lazy" and i["zone"] not in ("header", "nav") and i["index"] > 2]
    # Candidata a LCP: primera imagen de contenido (fuera de header/nav) de cada página
    lcp = []
    for p in pages:
        first = next((i for i in p["images"] if i.get("url") and i["zone"] not in ("header", "nav")), None)
        if first:
            lcp.append((p, first))
    lcp_lazy = [(p, i) for p, i in lcp if i["loading"] == "lazy"]
    lcp_no_prio = [(p, i) for p, i in lcp if i["fetchpriority"] != "high"]
    no_srcset = [(p, i) for p, i in tags if not i["srcset"] and not i["in_picture"] and fmt(i) != "svg"]
    formats = Counter(fmt(i) for i in unique.values())
    legacy = [i for i in unique.values() if fmt(i) in LEGACY]
    bad_names = [i for i in unique.values() if GENERIC_NAME.match(Path(urlparse(i["url"]).path).name)]

    sec = rio.section("seo-images", "Imágenes", site,
                      f"{n_unique} imágenes únicas en {len(pages)} páginas"
                      + ("" if has_sizes else " · sin pesos (ejecuta seo_extract con --head-images)"))
    sec["kpis"] = [
        rio.kpi("Imágenes únicas", n_unique, hint=f"{n_tags} etiquetas <img>"),
        rio.kpi("Sin atributo alt", len(no_alt), rio.status_for(len(no_alt), n_tags)),
        rio.kpi("Sin width/height", len(no_dims), rio.status_for(len(no_dims), n_tags), "Riesgo de CLS"),
        rio.kpi("LCP con lazy-load", len(lcp_lazy), "bad" if lcp_lazy else "good", "Primera imagen de contenido"),
        rio.kpi("Formato legacy", len(legacy), rio.status_for(len(legacy), n_unique), "JPG/PNG/GIF → WebP/AVIF"),
        rio.kpi("Formatos distintos", len(formats), hint=" · ".join(f"{k} {v}" for k, v in formats.most_common())),
    ]
    if has_sizes:
        sizes = [i["head_bytes"] for i in unique.values() if i.get("head_bytes")]
        heavy = [i for i in unique.values() if (i.get("head_bytes") or 0) > 200 * 1024]
        sec["kpis"] += [
            rio.kpi("Peso total", f"{kb(sum(sizes)):,} KB".replace(",", ".")),
            rio.kpi("Más de 200 KB", len(heavy), rio.status_for(len(heavy), n_unique)),
        ]
        top = sorted(unique.values(), key=lambda i: i.get("head_bytes") or 0, reverse=True)[:25]
        sec["tables"].append(rio.table("Imágenes más pesadas", ["Imagen", "KB", "Formato", "Alt"],
                                       [[i["url"], kb(i.get("head_bytes")), fmt(i), i["alt"] or "—"] for i in top]))

    issues = [("Sin alt", len(no_alt)), ("Alt vacío", len(empty_alt)), ("Alt genérico", len(generic_alt)),
              ("Sin dimensiones", len(no_dims)), ("Sin srcset", len(no_srcset)), ("Sin lazy (bajo el pliegue)", len(no_lazy)),
              ("LCP sin fetchpriority", len(lcp_no_prio)), ("Nombre de archivo genérico", len(bad_names))]
    sec["charts"] = [rio.chart("hbar", "Problemas detectados (etiquetas <img>)", [k for k, _ in issues],
                                      [{"label": "Imágenes", "data": [v for _, v in issues]}])]

    sec["tables"].insert(0, rio.table("Imágenes sin alt", ["Página", "Imagen"],
                                      [[urlparse(p["url"]).path or "/", i["url"]] for p, i in no_alt]))
    sec["tables"].insert(1, rio.table("Imagen candidata a LCP por página", ["Página", "Imagen", "loading", "fetchpriority", "Dimensiones"],
                                      [[urlparse(p["url"]).path or "/", i["url"], i["loading"] or "—", i["fetchpriority"] or "—",
                                        f"{i['width']}×{i['height']}" if i["width"] and i["height"] else "—"] for p, i in lcp]))
    print(f"→ {rio.write_section(sec)}")


if __name__ == "__main__":
    main()
