#!/usr/bin/env python3
"""Agrupa keywords por similitud léxica y las cruza con las páginas del sitio.

Uso:
  python3 keyword-cluster/scripts/cluster_keywords.py [keywords.csv] --site example.com [--pages _pages.json] [--threshold 0.5]

Entrada: CSV con columna keyword (opcional: volumen, kd) o TXT con una keyword por línea.
Sin listado y con --pages, usa como candidatas los title y H1 de las páginas del sitio.
Salida: crawler/output/<dominio>/_keyword_clusters.json y report/data/<dominio>/keyword-cluster.json
"""
import argparse
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))
import report_io as rio  # noqa: E402

STOP = set("a al con de del el en la las lo los para por que se sin un una y o the of for and to in".split())
ALIASES = {
    "keyword": ("keyword", "palabra clave", "query", "consulta"),
    "volume": ("volume", "volumen", "impressions", "impresiones"),
    "kd": ("kd", "dificultad", "difficulty"),
}
# Orden = prioridad; se evalúa sobre texto sin tildes
INTENTS = [
    ("Transaccional", r"\b(comprar|precio|precios|barato|oferta|domicilio|envio|buy|price)\b"),
    ("Comercial", r"\b(mejor|mejores|top|opiniones|review|vs|comparar|alternativas?|best)\b"),
    ("Informacional", r"\b(que|como|cual|por que|para que|guia|tutorial|ejemplos?|sirve|diferencia|what|how)\b"),
]


def fold(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def tokens(text):
    """Palabras sin stopwords y sin plural (-es, -s)."""
    words = (w for w in re.findall(r"[a-z0-9]+", fold(text)) if w not in STOP and len(w) > 1)
    return frozenset(re.sub(r"(?<=.{3})(es|s)$", "", w) for w in words)


def intent_of(kw):
    return next((name for name, rx in INTENTS if re.search(rx, fold(kw))), "Genérica")


def number(v):
    digits = re.sub(r"[^\d.]", "", (v or "").replace(",", ""))
    return float(digits) if digits else None


def read_keywords(path):
    if not path.lower().endswith(".csv"):
        return [{"keyword": l.strip()} for l in Path(path).read_text().splitlines() if l.strip()]
    rows = csv.DictReader(Path(path).read_text(encoding="utf-8-sig").splitlines())
    col = {k: next((f for f in rows.fieldnames if f.strip().lower() in names), None) for k, names in ALIASES.items()}
    col["keyword"] = col["keyword"] or rows.fieldnames[0]
    return [{"keyword": r[col["keyword"]].strip(), "volume": number(r.get(col["volume"])), "kd": number(r.get(col["kd"]))}
            for r in rows if r[col["keyword"]].strip()]


def candidates_from_pages(pages):
    """Title (sin marca tras | o -) y H1 de cada página, sin repetidos."""
    seen, out = set(), []
    for p in pages:
        for text in [re.split(r"\s[|–-]\s", p.get("title") or "")[0]] + p["headings"]["h1"]:
            if text.strip() and fold(text.strip()) not in seen:
                seen.add(fold(text.strip()))
                out.append({"keyword": text.strip()})
    return out


def cluster(items, threshold):
    """El de mayor volumen es el pilar; se une si contiene sus tokens o el Jaccard llega al umbral."""
    groups = []
    for it in sorted(items, key=lambda i: (-(i.get("volume") or 0), len(i["tokens"]))):
        score = lambda g: 1 if g["tokens"] <= it["tokens"] else len(g["tokens"] & it["tokens"]) / len(g["tokens"] | it["tokens"])
        best = max(groups, key=score, default=None)
        if best and it["tokens"] and score(best) >= threshold:
            best["items"].append(it)
        else:
            groups.append({"tokens": it["tokens"], "items": [it]})
    return groups


def pages_for(pillar, pages):
    """(cubre_todo, url) de las páginas cuyo slug, title o H1 contienen ≥50% de los tokens del pilar."""
    found = []
    for p in pages:
        slug = tokens(re.sub(r"[-_/]", " ", p["url"].split("//", 1)[-1].partition("/")[2]))
        head = tokens(" ".join([p.get("title") or ""] + p["headings"]["h1"]))
        ratio = max(len(pillar & slug), len(pillar & head)) / len(pillar)
        if ratio >= 0.5:
            found.append((ratio == 1, p["url"]))
    return sorted(found, reverse=True)


def fmt(n):
    return "—" if n is None else f"{int(n):,}".replace(",", ".")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("keywords", nargs="?")
    ap.add_argument("--site", required=True)
    ap.add_argument("--pages")
    ap.add_argument("--threshold", type=float, default=0.5)
    a = ap.parse_args()

    pages = [p for p in rio.load_pages(a.pages) if not p.get("error")] if a.pages else None
    if not a.keywords and pages is None:
        sys.exit("Indica un listado de keywords o --pages para extraer candidatas del sitio")
    items = read_keywords(a.keywords) if a.keywords else candidates_from_pages(pages)
    if not items:
        sys.exit("No hay keywords")
    for i in items:
        i["tokens"] = tokens(i["keyword"])
    has_vol = any(i.get("volume") for i in items)

    clusters = []
    for g in cluster(items, a.threshold):
        its = g["items"]
        intents = [intent_of(i["keyword"]) for i in its]
        known = [x for x in intents if x != "Genérica"]
        found = pages_for(g["tokens"], pages) if pages is not None and g["tokens"] else []
        clusters.append({
            "pillar": its[0]["keyword"],
            "intent": max(set(known), key=known.count) if known else "Genérica",
            "mixed_intents": sorted(set(known)),
            "volume": sum(i.get("volume") or 0 for i in its) if has_vol else None,
            "keywords": [{k: v for k, v in i.items() if k != "tokens" and v is not None} for i in its],
            "coverage": None if pages is None else "cubierto" if found and found[0][0] else "parcial" if found else "hueco",
            "pages": [u for _, u in found[:3]],
            "cannibalization": sum(1 for full, _ in found if full) > 1,
        })
    clusters.sort(key=lambda c: -(c["volume"] or len(c["keywords"])))

    out = rio.ROOT / "crawler" / "output" / rio.domain_of(a.site)
    out.mkdir(parents=True, exist_ok=True)
    (out / "_keyword_clusters.json").write_text(json.dumps(clusters, ensure_ascii=False, indent=2))

    singles = sum(len(c["keywords"]) == 1 for c in clusters)
    kpis = [rio.kpi("Keywords", str(len(items))), rio.kpi("Clusters", str(len(clusters))),
            rio.kpi("Clusters de 1 keyword", str(singles), "warn" if singles > len(clusters) / 2 else "info")]
    if has_vol:
        kpis.append(rio.kpi("Volumen total", fmt(sum(c["volume"] for c in clusters))))
    if pages is not None:
        gaps = sum(c["coverage"] == "hueco" for c in clusters)
        cann = sum(c["cannibalization"] for c in clusters)
        kpis += [rio.kpi("Sin página (hueco)", str(gaps), rio.status_for(gaps, len(clusters))),
                 rio.kpi("Posible canibalización", str(cann), "bad" if cann else "good")]

    top = clusters[:10]
    chart = rio.chart("hbar", "Top clusters por " + ("volumen" if has_vol else "nº de keywords"),
                      [c["pillar"] for c in top], [c["volume"] if has_vol else len(c["keywords"]) for c in top])
    cols = ["Cluster (pilar)", "Intención", "Keywords", "Volumen"] + (["Cobertura", "Página"] if pages is not None else [])
    rows = [[c["pillar"], c["intent"], len(c["keywords"]), fmt(c["volume"])]
            + ([c["coverage"] + (" · canibaliza" if c["cannibalization"] else ""), (c["pages"] or ["—"])[0]] if pages is not None else [])
            for c in clusters]

    source = f"{len(items)} keywords ({'listado' if a.keywords else 'extraídas del sitio'}) · umbral {a.threshold}" + (f" · {len(pages)} páginas" if pages is not None else " · sin cruce con el sitio")
    path = rio.write_section(rio.section("keyword-cluster", "Clustering de keywords", a.site, source,
                                         kpis=kpis, charts=[chart], tables=[rio.table("Clusters", cols, rows)]))
    print(f"{len(items)} keywords → {len(clusters)} clusters\n  {out / '_keyword_clusters.json'}\n  {path}")


if __name__ == "__main__":
    main()
