#!/usr/bin/env python3
"""Une las secciones JSON de cada skill en report/report.html (Pico CSS + Chart.js).

Uso:
  python3 report/build_report.py example.com          # usa report/data/example.com/*.json
  python3 report/build_report.py                      # si solo hay un dominio, lo usa
  python3 report/build_report.py example.com --open   # y lo abre en el navegador
"""
import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
# Orden lógico del informe: primero cómo se rastrea, luego qué se ve en cada página
ORDER = ["cloudflare-crawl", "robots-txt", "seo-audit", "internal-linking", "seo-images"]
REQUIRED = ("skill", "title", "site")
SEVERITIES = {"critical", "high", "medium", "low"}
CHART_TYPES = {"bar", "hbar", "stacked", "doughnut", "pie", "radar", "line"}


def validate(sec, name):
    problems = [f"falta '{k}'" for k in REQUIRED if not sec.get(k)]
    for f in sec.get("findings", []):
        if f.get("severity") not in SEVERITIES:
            problems.append(f"severity inválida: {f.get('severity')!r} en '{f.get('title')}'")
        if not f.get("evidence"):
            problems.append(f"hallazgo sin evidencia: '{f.get('title')}'")
    for c in sec.get("charts", []):
        if c.get("type") not in CHART_TYPES:
            problems.append(f"tipo de gráfica inválido: {c.get('type')!r}")
        elif any(len(d.get("data", [])) != len(c.get("labels", [])) for d in c.get("datasets", [])):
            problems.append(f"gráfica '{c.get('title')}': labels y data no tienen el mismo largo")
    if len(sec.get("charts", [])) > 1:
        problems.append(f"{len(sec['charts'])} gráficas: máximo 1 por sección")
    s = sec.get("score")
    if s is not None and not (isinstance(s, (int, float)) and 0 <= s <= 100):
        problems.append(f"score fuera de rango: {s!r}")
    for p in problems:
        print(f"  ⚠ {name}: {p}", file=sys.stderr)
    return sec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("site", nargs="?")
    ap.add_argument("-o", "--out", default=str(HERE / "report.html"))
    ap.add_argument("--open", action="store_true")
    args = ap.parse_args()

    sites = sorted(p.name for p in DATA.iterdir() if p.is_dir()) if DATA.exists() else []
    site = args.site
    if site:
        site = site.split("://")[-1].split("/")[0].removeprefix("www.")
    elif len(sites) == 1:
        site = sites[0]
    else:
        sys.exit(f"Indica el dominio. Disponibles: {', '.join(sites) or '(ninguno)'}")
    folder = DATA / site
    files = sorted(folder.glob("*.json"))
    if not files:
        sys.exit(f"No hay secciones en {folder}")

    sections = [validate(json.loads(f.read_text()), f.name) for f in files]
    rank = {k: i for i, k in enumerate(ORDER)}
    sections.sort(key=lambda s: (rank.get(s["skill"], len(ORDER)), s["skill"]))
    payload = {"site": site, "generated": date.today().isoformat(), "sections": sections}
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    html = (HERE / "template.html").read_text().replace("/*__DATA__*/", data)
    out = Path(args.out)
    out.write_text(html)
    print(f"→ {out}  ({len(sections)} secciones: {', '.join(s['skill'] for s in sections)})")
    if args.open:
        subprocess.run(["open", str(out)], check=False)


if __name__ == "__main__":
    main()
