# seoskills

Skills de Claude Code para SEO. Se usan desde este directorio (no están registrados como skills globales).
Informes y comunicación en **español**.

## Estructura

```
<skill>/SKILL.md            instrucciones (mismo patrón en todos)
<skill>/scripts/*.py        script determinista → report/data/<dominio>/<skill>.json
                            (crawler y robots no tienen: su lógica curl + jq vive en el SKILL.md)
shared/seo_extract.py       extractor SEO (URL, archivo o carpeta del crawler) → JSON de páginas
shared/report_io.py         helpers para escribir secciones del reporte
report/SCHEMA.md            contrato JSON de cada sección
report/build_report.py      une las secciones → report/report.html (Pico CSS + Chart.js)
crawler/output/<dominio>/   HTML renderizado + _manifest.json + _pages.json   (ignorado en git)
report/data/<dominio>/      secciones JSON                                    (ignorado en git)
```

## Patrón obligatorio de un skill

Frontmatter (`name`, `description` en español con disparadores) y estas secciones, en este orden:
**Cuándo usar → Entradas → Flujo (1. Datos · 2. Script → reporte · 3. Análisis (Claude) · 4. Reporte) → Qué evaluar / Puntuación → Reglas**.

- El script mide (kpis, charts, tables). Claude interpreta (score, summary, findings, actions, code).
- Script solo cuando hay que procesar mucho HTML o contar con exactitud (extractor, grafo, imágenes).
  Si el dato es pequeño y Claude lo puede leer entero (robots.txt), la lógica va en el SKILL.md.
- Toda salida termina en `python3 report/build_report.py <dominio>`. No generar PDF ni otros formatos salvo que se pida.
- Re-ejecutar un script conserva el análisis ya escrito (`write_section` hace merge).
- Scripts solo con librería estándar de Python (certifi opcional).

## Reglas de datos

- **Nunca WebFetch para el `<head>`** (pierde title, meta, canonical, OG, hreflang). Usar `shared/seo_extract.py`.
- macOS: `grep` no soporta `-P`. Preferir los scripts a cadenas de `curl | grep`.
- Credenciales de Cloudflare solo en `.env` (`CF_ACCOUNT_ID`, `CF_API_TOKEN`). Nunca en comandos ni en settings.
- No inventar métricas (tráfico, CWV, posiciones). Sin datos → "no evaluado".

## Probar

```bash
python3 shared/seo_extract.py --dir crawler/output/<dominio> -o crawler/output/<dominio>/_pages.json
python3 basic-audit/scripts/onpage_metrics.py crawler/output/<dominio>/_pages.json
python3 report/build_report.py <dominio> --open
```
