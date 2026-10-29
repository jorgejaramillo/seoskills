# seo-skills

Skills de Claude Code para SEO. Cada skill recoge datos con un script, Claude los analiza
y todo termina en un único informe visual: `report/report.html` (Pico CSS + Chart.js).

| Skill | Carpeta | Qué hace |
|-------|---------|----------|
| `cloudflare-crawl` | `crawler/` | Descarga el HTML renderizado (lo que ve Google) con Cloudflare Browser Run |
| `robots-txt` | `robots/` | Audita, valida y genera robots.txt; política de bots de IA |
| `seo-audit` | `basic-audit/` | Auditoría técnica y on-page con puntuación y plan de acción |
| `internal-linking` | `internal-linking/` | Grafo de enlaces, huérfanas, profundidad, anchors |
| `seo-images` | `images/` | Alt, peso, formatos, LCP, CLS, responsive |
| `no-slop` | `no-slop/` | Analiza un artículo párrafo a párrafo y puntúa de 1 a 100 qué tan slop (relleno genérico de IA) es |
| `title-generator` | `title-generator/` | Propone titles SEO de 45–55 caracteres a partir de una consulta y su contexto |
| `description-generator` | `description-generator/` | Propone meta descriptions de 150–160 caracteres a partir de la consulta y el title |

## Uso rápido

`crawler` y `robots` no tienen script: su lógica (curl + jq) está en el propio SKILL.md.
`title-generator` y `description-generator` no tienen script ni sección de reporte: se invocan a demanda y devuelven JSON.

```bash
cp .env.example .env                     # credenciales de Cloudflare (solo para el crawler)
# rastreo: pasos de crawler/SKILL.md → crawler/output/example.com/_pages.json
# sin crawler: python3 shared/seo_extract.py --sitemap https://example.com/sitemap.xml -o crawler/output/example.com/_pages.json
P=crawler/output/example.com/_pages.json
python3 basic-audit/scripts/onpage_metrics.py $P
python3 internal-linking/scripts/link_graph.py $P --sitemap https://example.com/sitemap.xml
python3 report/build_report.py example.com --open
```

En Claude Code basta con pedir, por ejemplo, "haz una auditoría SEO de example.com":
el skill ejecuta los scripts, completa el análisis y genera el informe.

Contrato de datos del informe: [`report/SCHEMA.md`](report/SCHEMA.md).
