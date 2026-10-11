#!/usr/bin/env python3
"""Grafo de enlaces internos a partir de seo_extract → sección internal-linking.

Calcula enlaces entrantes por página, profundidad de clics desde la home, huérfanas
(contra el sitemap si se pasa), zonas de enlace (nav/footer/contenido) y anchors genéricos.

Uso:
  python3 internal-linking/scripts/link_graph.py pages.json [--sitemap https://example.com/sitemap.xml]
"""
import argparse
import re
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))
import report_io as rio  # noqa: E402
import seo_extract  # noqa: E402

GENERIC = re.compile(r"^(click aqu[ií]|haz clic( aqu[ií])?|aqu[ií]|leer m[aá]s|ver m[aá]s|m[aá]s|saber m[aá]s|"
                     r"read more|click here|here|more|learn more|ver|link|enlace|este art[ií]culo|this page)\.?$", re.I)
CONTENT_ZONES = {"main", "body"}


def norm(u):
    p = urlparse(u)
    host = p.netloc.lower().removeprefix("www.")
    path = re.sub(r"/(index\.html?)?$", "", p.path) or "/"
    return f"{host}{path}" + (f"?{p.query}" if p.query else "")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pages")
    ap.add_argument("--sitemap", help="Sitemap para detectar huérfanas que no salen en el rastreo")
    ap.add_argument("--home", help="URL de inicio para medir profundidad (default: la home del dominio)")
    args = ap.parse_args()

    pages = [p for p in rio.load_pages(args.pages) if not p.get("error")]
    site = rio.domain_of(pages[0]["url"])
    by_key = {norm(p["url"]): p for p in pages}
    known = set(by_key)
    sitemap = {norm(u): u for u in seo_extract.sitemap_urls(args.sitemap)} if args.sitemap else {}
    universe = known | set(sitemap)

    inlinks = defaultdict(set)          # destino → páginas origen (únicas)
    content_inlinks = defaultdict(set)  # solo enlaces en el contenido
    anchors = defaultdict(Counter)
    edges = defaultdict(set)
    zones = Counter()
    generic, nofollow_int, unknown_targets = [], [], Counter()
    for p in pages:
        src = norm(p["url"])
        for ln in p["links"]:
            if not ln["internal"]:
                continue
            dst = norm(ln["url"])
            zones[ln["zone"]] += 1
            if dst == src:
                continue
            edges[src].add(dst)
            inlinks[dst].add(src)
            if ln["zone"] in CONTENT_ZONES:
                content_inlinks[dst].add(src)
            text = ln["text"].strip()
            anchors[dst][text or "(vacío)"] += 1
            if not text or GENERIC.match(text):
                generic.append((p["url"], ln["url"], text or "(vacío)"))
            if ln["nofollow"]:
                nofollow_int.append((p["url"], ln["url"]))
            if dst not in universe:
                unknown_targets[dst] += 1

    home = norm(args.home or f"https://{site}/")
    if home not in known:
        home = min(known, key=len)
    depth = {home: 0}
    q = deque([home])
    while q:
        cur = q.popleft()
        for nxt in edges.get(cur, ()):
            if nxt not in depth and nxt in universe:
                depth[nxt] = depth[cur] + 1
                q.append(nxt)

    orphans = sorted(k for k in universe if k != home and not inlinks.get(k))
    unreachable = sorted(k for k in universe if k not in depth and k not in orphans)
    only_nav = sorted(k for k in known if k != home and inlinks.get(k) and not content_inlinks.get(k))
    n = len(known)
    in_counts = {k: len(inlinks.get(k, ())) for k in universe}
    total_links = sum(len(v) for v in edges.values())

    sec = rio.section("internal-linking", "Enlazado interno", site,
                      f"{n} páginas rastreadas" + (f" + {len(set(sitemap) - known)} solo en sitemap" if sitemap else ""))
    deep = sum(1 for d in depth.values() if d > 3)
    sec["kpis"] = [
        rio.kpi("Páginas en el grafo", len(universe)),
        rio.kpi("Enlaces internos únicos", total_links, hint=f"{round(total_links / n, 1) if n else 0} por página"),
        rio.kpi("Huérfanas", len(orphans), rio.status_for(len(orphans), len(universe)), "Sin enlaces entrantes"),
        rio.kpi("Más de 3 clics", deep + len(unreachable), rio.status_for(deep + len(unreachable), len(universe))),
        rio.kpi("Solo enlazadas desde nav/footer", len(only_nav), "warn" if only_nav else "good",
                "Sin enlaces contextuales"),
        rio.kpi("Anchors genéricos o vacíos", len(generic), rio.status_for(len(generic), max(total_links, 1))),
    ]
    in_content = sum(v for k, v in zones.items() if k in CONTENT_ZONES)
    sec["kpis"].append(rio.kpi("Enlaces dentro del contenido", f"{rio.pct(in_content, sum(zones.values()))}%",
                               hint="El resto está en menú, cabecera o footer"))
    if nofollow_int:
        sec["kpis"].append(rio.kpi("Enlaces internos nofollow", len(nofollow_int), "bad"))

    dcount = Counter(min(d, 5) for d in depth.values())
    dlabels = ["0 (home)", "1", "2", "3", "4", "5+"]
    if unreachable:
        dlabels.append("Inalcanzable")
    sec["charts"] = [
        rio.chart("bar", "Profundidad de clics desde la home", dlabels,
                  [{"label": "Páginas", "data": [dcount.get(i, 0) for i in range(6)] + ([len(unreachable)] if unreachable else [])}],
                  colors=["good", "good", "good", "good", "warn", "bad", "bad"][:len(dlabels)]),
    ]
    sec["tables"] = [
        rio.table("Páginas huérfanas", ["URL", "En sitemap"], [[sitemap.get(k, k), "sí" if k in sitemap else "no"] for k in orphans]),
        rio.table("Enlaces entrantes y anchors por página", ["Página", "Entrantes", "Contextuales", "Profundidad", "Anchors más usados"],
                  [[k, in_counts[k], len(content_inlinks.get(k, ())), depth.get(k, "∞"),
                    " · ".join(f"{a} ({c})" for a, c in anchors[k].most_common(3))]
                   for k in sorted(universe, key=lambda k: in_counts[k])]),
        rio.table("Anchors genéricos o vacíos", ["Origen", "Destino", "Anchor"], generic),
    ]
    if only_nav:
        sec["tables"].append(rio.table("Sin enlaces contextuales (solo nav/header/footer)", ["URL"], [[k] for k in only_nav]))
    if unknown_targets:
        sec["tables"].append(rio.table("Destinos enlazados que no están en el rastreo ni el sitemap",
                                       ["URL", "Veces enlazada"], unknown_targets.most_common(50)))
    print(f"→ {rio.write_section(sec)}")


if __name__ == "__main__":
    main()
