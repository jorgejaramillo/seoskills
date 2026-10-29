---
name: seo-audit
description: >
  Auditoría SEO técnica y on-page de un sitio: rastreo e indexación, técnica, on-page,
  contenido/E-E-A-T y autoridad, con puntuación 0-100 y plan de acción priorizado.
  Úsalo cuando el usuario pida "auditoría SEO", "revisa el SEO de mi web", "¿por qué no
  posiciono?", "health check SEO" o comparta una URL preguntando por problemas SEO.
  Diagnostica y prioriza; no implementa cambios salvo que se pida.
---

# Auditoría SEO

Encontrar problemas → explicar el impacto → priorizar por esfuerzo vs. beneficio.
Es el skill paraguas: para profundizar usa `robots-txt`, `internal-linking` y `seo-images`.

## Cuándo usar

Auditoría general de un dominio o de un grupo de páginas. Para una sola página o un tema
concreto (imágenes, enlaces, robots), usa el skill específico.

## Entradas

Obligatorio: URL/dominio. Útil: tipo de sitio (e-commerce, SaaS, blog, negocio local),
objetivo y problemas conocidos. Si falta contexto, asume y dilo en el `summary`.

## Flujo

### 1. Datos

Elige la fuente según el sitio (si dudas, mira si el HTML inicial trae el contenido):

```bash
# Sitio con JS → HTML renderizado: sigue crawler/SKILL.md (/crawl con source=sitemaps, limit 30)
#   → crawler/output/<dominio>/_pages.json

# Sitio estático/WordPress → HTTP directo (incluye estado, redirecciones, TTFB, cabeceras)
python3 shared/seo_extract.py --sitemap https://example.com/sitemap.xml --limit 30 -o crawler/output/<dominio>/_pages.json
```

Muestra: home + 3–5 páginas por plantilla (categoría, producto, artículo, servicio).

### 2. Script → reporte

```bash
python3 basic-audit/scripts/onpage_metrics.py crawler/output/<dominio>/_pages.json
```

robots.txt y sitemap forman parte de la categoría 1: revísalos con los pasos de `robots/SKILL.md`.

`onpage_metrics.py` escribe `report/data/<dominio>/seo-audit.json` con cobertura de elementos
on-page, longitudes de title/description, duplicados, schema y problemas por página.

### 3. Análisis (Claude)

Lee `_pages.json` y las tablas generadas. Revisa a mano lo que el script no puede juzgar:
intención de búsqueda, calidad del contenido, E-E-A-T, coherencia title↔H1↔contenido.
Para Core Web Vitals usa PageSpeed Insights (`https://pagespeed.web.dev/`) si el usuario
lo pide o el sitio es lento; si no hay datos, márcalo como no evaluado.
Si hay titles fuera de 30–60 o descriptions fuera de 70–160 / duplicadas, **no reescribas a mano**: invoca
`title-generator` (`../title-generator/SKILL.md`) y luego `description-generator` (`../description-generator/SKILL.md`).

Completa en el JSON: `score`, `summary`, `findings`, `actions` y añade a `tables` la puntuación
por categoría (no como gráfica: la sección ya tiene una):

```json
{"title": "Puntuación por categoría", "columns": ["Categoría", "Peso", "Puntuación", "Nota"],
 "rows": [["Rastreo e indexación", "30%", 75, "Sitemap incompleto"], ["Autoridad", "10%", "—", "Fuera de alcance"]]}
```

### 4. Reporte

Ejecuta también `internal-linking` y `seo-images` sobre el mismo `_pages.json` si el usuario
quiere el informe completo. Luego: `python3 report/build_report.py <dominio> --open`.

## Qué evaluar

| # | Categoría | Peso | Qué mirar |
|---|-----------|------|-----------|
| 1 | Rastreo e indexación | 30% | robots.txt, sitemap (existe, completo, solo URLs 200 indexables), canonical auto-referente, noindex, redirecciones en cadena, profundidad |
| 2 | Técnico | 25% | HTTPS y certificado, viewport, `lang`, TTFB, Core Web Vitals (si hay datos), JSON-LD válido y del tipo correcto, render (HTML inicial vs. renderizado) |
| 3 | On-page | 20% | title único 30–60 c, description 70–160 c, un H1, jerarquía H2/H3, Open Graph, alt (resumen; detalle en `seo-images`), enlaces internos (resumen; detalle en `internal-linking`) |
| 4 | Contenido / E-E-A-T | 15% | contenido escaso (<300 palabras en páginas clave), intención, autor y credenciales (crítico en YMYL: salud, finanzas, legal), página "sobre", contacto, fechas |
| 5 | Autoridad | 10% | Solo con datos (GSC, Ahrefs, Semrush). Sin datos → fuera de alcance |

## Puntuación

Cada categoría empieza en 100 y resta por hallazgo: Crítico −15 a −30 · Alto −8 a −12 · Medio −4 a −6 · Bajo −1 a −3.
Multiplica por confianza: alta ×1 · media ×0.5 · baja ×0.25.
Global = suma ponderada. Si una categoría queda fuera de alcance (típico: Autoridad), reparte su peso
proporcionalmente y dilo en el `summary`. Un score alto con un hallazgo crítico abierto no es válido: menciónalo.

Bandas: 90+ excelente · 75–89 bueno · 60–74 mejorable · 40–59 pobre · <40 crítico.

## Hallazgos y acciones

- Cada hallazgo: severidad, título de una frase, **evidencia concreta** (URL + dato), por qué importa, recomendación.
- Acciones en 4 niveles: bloqueos críticos → alto impacto → quick wins → largo plazo. `impact`/`effort`: alto | medio | bajo.
- Lenguaje claro, sin jerga innecesaria. "Arregla X en Y", nunca "mejora el SEO".

## Reglas

- **Nunca uses WebFetch para el `<head>`**: lo convierte a markdown y pierde title, meta, canonical, OG, hreflang. Usa `shared/seo_extract.py`.
- No reportes un elemento como ausente sin verificarlo en `_pages.json`.
- No inventes métricas (tráfico, posiciones, CWV). Si no hay datos, se dice.
- Si el usuario pide implementar, pasa a modo prescriptivo con pasos concretos.
