#!/usr/bin/env python3
"""Métricas on-page/técnicas a partir de la salida de seo_extract → sección seo-audit.

Uso:
  python3 basic-audit/scripts/onpage_metrics.py pages.json
  python3 basic-audit/scripts/onpage_metrics.py crawler/output/example.com/_pages.json
"""
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))
import report_io as rio  # noqa: E402


def issues_of(p):
    out = []
    if not p["title"]:
        out.append("sin title")
    elif not 30 <= p["title_len"] <= 60:
        out.append(f"title {p['title_len']}c")
    if not p["meta_description"]:
        out.append("sin meta description")
    elif not 70 <= p["meta_description_len"] <= 160:
        out.append(f"description {p['meta_description_len']}c")
    h1 = len(p["headings"]["h1"])
    if h1 != 1:
        out.append(f"{h1} H1")
    if not p["canonical"]:
        out.append("sin canonical")
    elif not p.get("canonical_self"):
        out.append("canonical a otra URL")
    if p["canonical_count"] > 1:
        out.append(f"{p['canonical_count']} canonicals")
    if p["noindex"]:
        out.append("noindex")
    if not p["viewport"]:
        out.append("sin viewport")
    if not p["lang"]:
        out.append("sin lang")
    if not p["schema_types"]:
        out.append("sin schema")
    if p["jsonld_errors"]:
        out.append("JSON-LD inválido")
    if p["word_count"] < 300:
        out.append(f"{p['word_count']} palabras")
    if p.get("ssl_error"):
        out.append("certificado SSL inválido")
    if p.get("redirects"):
        out.append(f"{len(p['redirects'])} redirecciones")
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    pages = [p for p in rio.load_pages(sys.argv[1]) if not p.get("error")]
    if not pages:
        sys.exit("No hay páginas válidas en el archivo")
    n = len(pages)
    site = rio.domain_of(pages[0]["url"])

    titles = defaultdict(list)
    descs = defaultdict(list)
    for p in pages:
        if p["title"]:
            titles[p["title"].strip().lower()].append(p["url"])
        if p["meta_description"]:
            descs[p["meta_description"].strip().lower()].append(p["url"])
    dup_titles = {k: v for k, v in titles.items() if len(v) > 1}
    dup_descs = {k: v for k, v in descs.items() if len(v) > 1}

    def count(pred):
        return sum(1 for p in pages if pred(p))

    checks = [
        ("Title 30–60 caracteres", count(lambda p: p["title"] and 30 <= p["title_len"] <= 60)),
        ("Meta description 70–160", count(lambda p: p["meta_description"] and 70 <= p["meta_description_len"] <= 160)),
        ("Un solo H1", count(lambda p: len(p["headings"]["h1"]) == 1)),
        ("Canonical auto-referente", count(lambda p: p.get("canonical_self"))),
        ("Schema JSON-LD", count(lambda p: p["schema_types"])),
        ("Open Graph completo", count(lambda p: all(k in p["og"] for k in ("title", "description", "image")))),
        ("Viewport", count(lambda p: p["viewport"])),
        ("Atributo lang", count(lambda p: p["lang"])),
        ("Indexable (sin noindex)", count(lambda p: not p["noindex"])),
        ("≥300 palabras", count(lambda p: p["word_count"] >= 300)),
    ]
    ttfbs = [p["ttfb_ms"] for p in pages if p.get("ttfb_ms")]
    https = count(lambda p: p.get("final_url", p["url"]).startswith("https://"))
    no_desc = n - count(lambda p: p["meta_description"])
    bad_h1 = n - checks[2][1]

    sec = rio.section("seo-audit", "Auditoría SEO", site,
                      f"{n} páginas · {'HTML renderizado' if pages[0].get('source') == 'cloudflare-render' else 'HTML sin renderizar (HTTP)'}")
    sec["kpis"] = [
        rio.kpi("Páginas analizadas", n),
        rio.kpi("Títulos duplicados", sum(len(v) for v in dup_titles.values()),
                rio.status_for(sum(len(v) for v in dup_titles.values()), n)),
        rio.kpi("Sin meta description", no_desc, rio.status_for(no_desc, n)),
        rio.kpi("H1 ausente o múltiple", bad_h1, rio.status_for(bad_h1, n)),
        rio.kpi("Con noindex", count(lambda p: p["noindex"]), "warn" if count(lambda p: p["noindex"]) else "good",
                "Revisar que sea intencional"),
        rio.kpi("HTTPS", f"{rio.pct(https, n)}%", "good" if https == n else "bad"),
    ]
    if ttfbs:
        avg = round(sum(ttfbs) / len(ttfbs))
        sec["kpis"].append(rio.kpi("TTFB medio", f"{avg} ms", "good" if avg < 600 else "warn" if avg < 1500 else "bad",
                                   "Medido desde esta máquina, orientativo"))

    sec["charts"] = [rio.chart("hbar", "Cobertura de elementos on-page", [c[0] for c in checks],
                               [{"label": "% de páginas", "data": [rio.pct(c[1], n) for c in checks]}], unit="%", max=100)]

    rows = [[p["url"], ", ".join(iss)] for p in pages if (iss := issues_of(p))]
    sec["tables"] = [rio.table("Problemas por página", ["URL", "Problemas"], rows)]
    if dup_titles:
        sec["tables"].append(rio.table("Títulos duplicados", ["Título", "URLs"],
                                       [[t, "\n".join(u)] for t, u in dup_titles.items()]))
    if dup_descs:
        sec["tables"].append(rio.table("Meta descriptions duplicadas", ["Description", "URLs"],
                                       [[d[:120], "\n".join(u)] for d, u in dup_descs.items()]))
    sec["tables"].append(rio.table("Detalle on-page", ["URL", "Title (c)", "Desc (c)", "H1", "Palabras", "Schema"],
                                   [[urlparse(p["url"]).path or "/", p["title_len"], p["meta_description_len"],
                                     len(p["headings"]["h1"]), p["word_count"], ", ".join(p["schema_types"]) or "—"]
                                    for p in pages]))
    print(f"→ {rio.write_section(sec)}")


if __name__ == "__main__":
    main()
