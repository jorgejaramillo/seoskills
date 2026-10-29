---
name: keyword-cluster
description: >
  Agrupa keywords en clusters por tema e intención de búsqueda, define el pilar de cada grupo y los
  cruza con las páginas del sitio (cubierto / parcial / hueco / canibalización) o, si el sitio aún no
  tiene contenido, propone la arquitectura de páginas a crear. No exige listado: si no hay, extrae términos del sitio y los expande con el LLM. Úsalo cuando el usuario pida
  "agrupar keywords", "clustering de keywords", "topic clusters", "qué contenido me falta",
  "mapear keywords a URLs", "canibalización de keywords", "plan de contenidos" o comparta una lista
  de keywords (CSV/Excel/texto), o un tema o sitio del que sacar las keywords.
---

# Clustering de keywords

Convertir una lista de keywords en un mapa de contenido: qué páginas existen, cuáles faltan y cuáles compiten entre sí.
Referentes: [Semrush](https://www.semrush.com/blog/keyword-clustering/) · [SEOcrawl](https://seocrawl.ai/blog/keyword-clustering) · [OpenSEO](https://openseo.so/docs/skills/keyword-clustering).

## Cuándo usar

- Quieres mapear keywords a páginas, ver qué contenido falta o detectar canibalización.
- **Hay listado** (GSC, Semrush, Ahrefs, Keyword Planner, a mano) → es lo ideal: trae volumen y KD reales.
- **No hay listado** → el skill lo construye: extrae términos del sitio (crawler) y/o los genera con el LLM desde un tema semilla.
- El sitio **no existe o la keyword no está en él** → todo cluster sale "hueco" y el entregable es la arquitectura de páginas a crear.

No sirve para optimizar el title/description de una página concreta (usa `title-generator` / `description-generator`) ni para auditar un sitio (`basic-audit`).

## Entradas

Pregunta solo lo que falte. Obligatorio: **dominio** y **una fuente de keywords** (cualquiera de las tres):

1. **Listado** CSV/TXT. Columnas reconocidas: `keyword/palabra clave/query`, `volume/volumen/impressions`, `kd/dificultad`.
2. **Sitio** (URL): se extraen candidatas de sus title y H1.
3. **Tema semilla** (p. ej. "medicamentos para la disfunción eréctil"): el LLM propone las keywords.

Útil: mercado e idioma (por defecto español de Colombia), público, objetivo (tráfico, leads, ventas) y competidores.

## Flujo

### 1. Datos

**Páginas del sitio** (si existe): HTML renderizado con `crawler/SKILL.md` (sitios con JS) o HTTP directo:

```bash
python3 shared/seo_extract.py --sitemap https://example.com/sitemap.xml --limit 50 -o crawler/output/<dominio>/_pages.json
```

Toma páginas de cada plantilla (categorías, productos, artículos); la home sola no basta.

**Keywords**, según lo que haya:

- *Listado del usuario* → úsalo tal cual.
- *Sin listado* → en `keywords.txt` (una por línea) junta:
  - candidatas del sitio: title y H1 de `_pages.json` (el script las extrae solo si no pasas listado);
  - términos que el LLM genere desde el tema semilla y lo que ve en las páginas: sinónimos, preguntas (qué es, cómo, para qué sirve),
    comparativas (mejor, vs, alternativas), transaccionales (comprar, precio) y variantes por público o uso;
  - opcional, con navegador: autocompletado y People Also Ask de Google, y competidores (sus title/H1 con `shared/seo_extract.py --url`).
- Las generadas **no traen volumen ni KD**: márcalas como "generadas por LLM, sin volumen" en el `summary` y no inventes cifras.
  Si el usuario puede, sugiérele validarlas con Keyword Planner o GSC.

### 2. Script → reporte

```bash
python3 keyword-cluster/scripts/cluster_keywords.py [keywords.csv|keywords.txt] --site <dominio> [--pages crawler/output/<dominio>/_pages.json] [--threshold 0.5]
```

El script limpia (minúsculas, tildes, stopwords, plurales), agrupa de forma
léxica (pilar = mayor volumen; une por tokens contenidos o Jaccard ≥ umbral), clasifica intención por patrones y,
con `--pages`, mide cobertura del pilar contra slug/title/H1. Escribe:

- `crawler/output/<dominio>/_keyword_clusters.json` → clusters completos para refinar.
- `report/data/<dominio>/keyword-cluster.json` → KPIs, gráfica de top clusters y tablas.

### 3. Análisis (Claude)

La agrupación léxica no entiende significado. Lee `_keyword_clusters.json` y corrige:

1. **Unir** sinónimos y variantes que el script separó (`sildenafil` / `sildenafilo`, `tenis` / `zapatillas`).
2. **Separar** falsos amigos y clusters con intenciones mezcladas (`mixed_intents` con más de una clase): *comprar X* y *qué es X* no van en la misma página.
3. **Intención**: confirma la de cada cluster (informacional, comercial, transaccional, navegacional). Los "Genéricos" suelen ser términos cabeza: decide por el contexto del negocio.
4. **Pilar y soporte**: pilar = término más amplio y de mayor volumen; el resto son subtemas o secciones de la misma página. Una página por intención, no por keyword.
5. **Mapa de URLs**: por cluster, define la acción:
   - *cubierto* → optimizar la página existente (title/H1/secciones para los soportes).
   - *parcial* → ampliar contenido o rehacer la página que casi encaja.
   - *hueco* → crear página nueva (tipo: categoría, producto, guía, comparativa, landing; slug propuesto).
   - *canibalización* (varias páginas cubren el pilar) → elegir canónica, consolidar o diferenciar por intención.
6. **Prioridad** solo con datos reales: volumen alto + KD bajo + intención alineada al objetivo + posición actual 8–20 (quick win). Sin volumen/KD → ordena por intención y cobertura, y dilo.
7. Si el usuario aporta los top 10 de la SERP por keyword, une también las que **comparten ≥3–4 URLs** en el top 10 (criterio SERP de Semrush/SEOcrawl, más fiable que la similitud léxica). Sin ese dato, no lo simules.

Completa en el JSON: `score` (solo si sigue la puntuación de abajo, si no `null`), `summary`, `findings`, `actions`, y añade a `tables`
el **mapa de contenido** con tus correcciones:

```json
{"title": "Mapa de contenido", "columns": ["Cluster (pilar)", "Intención", "Acción", "URL actual / propuesta", "Keywords de soporte"],
 "rows": [["tadalafilo", "Transaccional", "Optimizar", "/tadalafilo", "tadalafilo 20 mg, precio tadalafilo"],
          ["semaglutida", "Informacional", "Crear guía", "/blog/que-es-semaglutida (nueva)", "semaglutida para que sirve"]]}
```

Si hay que escribir titles o descriptions de las páginas nuevas o de las que se optimicen, invoca `title-generator` y `description-generator`; no los redactes a mano.

### 4. Reporte

`python3 report/build_report.py <dominio> --open`

## Qué evaluar / Puntuación

El skill diagnostica la **cobertura** de la demanda; solo puntúa con cruce de sitio (`--pages`) y volumen. Si falta alguno → `score: null`.

| Criterio | Peso | Qué mirar |
|----------|------|-----------|
| Cobertura | 50% | % del volumen total en clusters *cubiertos* (parcial cuenta 0.5) |
| Canibalización | 25% | 100 − 25 por cada cluster con varias páginas compitiendo (mín. 0), ponderado por volumen |
| Alineación de intención | 25% | % del volumen cuya página existente coincide con la intención del cluster (revisión manual de Claude) |

Bandas: 90+ excelente · 75–89 bueno · 60–74 mejorable · 40–59 pobre · <40 crítico.
Hallazgos típicos: cluster de alto volumen sin página, página transaccional sirviendo query informacional, dos URLs peleando por el mismo pilar, clusters de 1 keyword sin potencial (descartar o unir).
Acciones: crear > consolidar > optimizar, ordenadas por volumen × intención × esfuerzo.

## Reglas

- **Nunca WebFetch para el `<head>`** de las páginas del sitio: usa `shared/seo_extract.py`.
- No inventes volumen, KD, posiciones ni tráfico. Sin dato → "no evaluado" / `—`.
- Un cluster = una intención = una página principal. Si dudas entre unir o separar, separa y anótalo.
- Sin sitio (o keyword que no está en él) no es un error: la cobertura sale "hueco" y el entregable es la arquitectura de páginas propuesta; explícalo en el `summary`.
- No generes más de ~50 clusters en el mapa; agrupa el resto como "cola larga" con una nota.
- Re-ejecutar el script conserva `summary`, `findings`, `actions` y las tablas/gráficas añadidas a mano, pero **regenera los clusters**: copia tus correcciones al mapa de contenido antes de volver a correrlo con otros parámetros.
