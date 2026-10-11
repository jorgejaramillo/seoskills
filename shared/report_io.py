"""Helpers para que los scripts de cada skill escriban su sección del reporte.

Contrato completo en report/SCHEMA.md. Cada skill escribe
report/data/<dominio>/<skill>.json; report/build_report.py los une en report/report.html.
"""
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "report" / "data"


def domain_of(url_or_domain):
    s = url_or_domain if "://" in url_or_domain else f"https://{url_or_domain}"
    return urlparse(s).netloc.lower().removeprefix("www.")


def section(skill, title, site, source, **extra):
    """Esqueleto de sección. Los campos de análisis (summary, score, findings, actions)
    los completa Claude después de leer los datos."""
    base = {
        "skill": skill, "title": title, "site": domain_of(site),
        "generated": date.today().isoformat(), "source": source,
        "score": None, "summary": "", "kpis": [], "charts": [], "findings": [],
        "tables": [], "actions": [], "code": [],
    }
    base.update(extra)
    return base


def kpi(label, value, status="info", hint=None):
    k = {"label": label, "value": value, "status": status}
    if hint:
        k["hint"] = hint
    return k


def chart(type_, title, labels, datasets, **opts):
    """type_: bar | hbar | stacked | doughnut | pie | radar | line"""
    if datasets and not isinstance(datasets[0], dict):
        datasets = [{"label": title, "data": datasets}]
    return {"type": type_, "title": title, "labels": labels, "datasets": datasets, **opts}


def table(title, columns, rows, limit=200):
    return {"title": title, "columns": columns, "rows": rows[:limit],
            **({"truncated": len(rows)} if len(rows) > limit else {})}


def write_section(sec, keep_analysis=True):
    """Escribe la sección. Si ya existe y keep_analysis=True, conserva summary/score/
    findings/actions escritos antes por Claude para no perder análisis al re-ejecutar."""
    path = DATA / sec["site"] / f"{sec['skill']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    # Lo que genera el script se marca "auto"; lo que añade Claude a mano no lleva la marca
    for k in ("charts", "tables", "code"):
        for item in sec.get(k, []):
            item["auto"] = True
    if keep_analysis and path.exists():
        old = json.loads(path.read_text())
        for k in ("summary", "score", "findings", "actions"):
            if old.get(k) and not sec.get(k):
                sec[k] = old[k]
        # Gráficas, tablas y código añadidos por Claude (radar, robots.txt propuesto…) se conservan
        for k in ("charts", "tables", "code"):
            titles = {c["title"] for c in sec.get(k, [])}
            sec[k] = sec.get(k, []) + [c for c in old.get(k, []) if not c.get("auto") and c["title"] not in titles]
    path.write_text(json.dumps(sec, ensure_ascii=False, indent=2))
    return path


def load_pages(path):
    return json.loads(Path(path).read_text())


def pct(n, total):
    return round(100 * n / total) if total else 0


def status_for(bad, total, crit=0.3):
    """Estado de un KPI según cuántas páginas tienen el problema."""
    if not bad:
        return "good"
    return "warn" if total and bad / total < crit else "bad"
