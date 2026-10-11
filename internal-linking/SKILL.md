---
name: internal-linking
description: >
  Analiza y optimiza el enlazado interno: páginas huérfanas, profundidad de clics,
  distribución de enlaces, clusters temáticos y anchors. Úsalo cuando el usuario mencione
  enlazado interno, enlaces internos, páginas huérfanas, arquitectura, topic clusters,
  anchor text, o pregunte "¿qué páginas necesitan más enlaces?". Diagnostica y recomienda
  enlaces concretos; no modifica el sitio salvo que se pida.
---

# Enlazado interno

Los enlaces internos son una de las pocas palancas de ranking que el dueño del sitio
controla del todo: indican qué páginas importan, cómo se relacionan los temas y hacia
dónde fluye la autoridad.

## Cuándo usar

- Auditoría completa del enlazado de un sitio.
- Optimizar una página concreta (qué enlaces añadir desde y hacia ella).
- Planificar enlaces para contenido nuevo.

## Entradas

Dominio o URLs. Útil: sitemap (para detectar huérfanas que el rastreo no encuentra),
páginas de negocio prioritarias y, si existen, datos de tráfico (GSC/GA4) para priorizar.

## Flujo

### 1. Datos

Reutiliza `crawler/output/<dominio>/_pages.json` si existe. Si no:

```bash
python3 shared/seo_extract.py --sitemap https://example.com/sitemap.xml --limit 100 -o crawler/output/<dominio>/_pages.json
```

Cuantas más páginas, más fiable el grafo: con <20 páginas, las huérfanas son orientativas.

### 2. Script → reporte

```bash
python3 internal-linking/scripts/link_graph.py crawler/output/<dominio>/_pages.json --sitemap https://example.com/sitemap.xml
```

Escribe `report/data/<dominio>/internal-linking.json` con: enlaces entrantes por página
(orígenes únicos), profundidad de clics desde la home, huérfanas, páginas enlazadas solo
desde nav/footer, zonas de enlace, anchors genéricos y destinos fuera del rastreo.

### 3. Análisis (Claude)

Completa `score`, `summary`, `findings`, `actions`. El script da el grafo; tú das el criterio:

1. **Huérfanas** — la corrección de mayor prioridad. Para cada una: ¿enlazar (relevante), redirigir o eliminar (obsoleta/escasa)? Indica desde qué páginas enlazar.
2. **Páginas de negocio poco enlazadas** — compara las que más enlaces reciben con las que deberían recibirlos.
3. **Sin enlaces contextuales** — enlaces solo desde menú/footer transmiten poco contexto. Lee el texto de páginas relacionadas y propone dónde insertar enlaces.
4. **Clusters** — pilar ↔ artículos del cluster, en ambos sentidos, y artículos hermanos entre sí.
5. **Anchors** — genéricos ("ver más", "aquí"), sobre-optimizados (mismo exact match siempre) o que no describen el destino. Proporción orientativa: exacto 10–20 %, parcial 30–40 %, marca/natural 20–30 %, genérico 10–20 %.
6. **Profundidad** — páginas importantes a más de 3 clics.

Cada recomendación de enlace lleva **origen, destino, anchor sugerido y ubicación** (sección o párrafo).
Ponlas en `tables`:

```json
{"title": "Enlaces a añadir", "columns": ["Origen", "Destino", "Anchor sugerido", "Dónde", "Motivo"], "rows": [...]}
```

### 4. Reporte

`python3 report/build_report.py <dominio> --open`

## Priorización

1. Huérfanas con tráfico o rankings → ROI inmediato.
2. Páginas de negocio poco enlazadas, desde páginas con autoridad.
3. Cerrar clusters.
4. Sustituir anchors genéricos en enlaces importantes.
5. Enlaces contextuales en contenido con tráfico.
6. Ajustes de navegación/footer (alcance global, poco valor por enlace).

## Puntuación

100 − 5 por cada 5 % de páginas huérfanas · −10 si >10 % de páginas está a más de 3 clics ·
−10 si páginas de negocio no tienen enlaces contextuales · −5 si >10 % de anchors son genéricos ·
−10 si hay enlaces internos nofollow · −5 por destinos internos rotos. Mínimo 0.

## Reglas

- Nunca "añade más enlaces internos" en abstracto: siempre origen → destino → anchor.
- Indica la fuente de datos (rastreo, sitemap, analítica o inferencia).
- No recomiendes enlazar páginas con noindex o canonical a otra URL.
- No uses WebFetch para canonical/robots: está en `_pages.json`.
