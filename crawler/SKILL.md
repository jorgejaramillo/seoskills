---
name: cloudflare-crawl
description: >
  Descarga el HTML renderizado (después de ejecutar JavaScript) de una o varias URLs
  con Cloudflare Browser Run: es lo que Google indexa. Úsalo cuando el usuario quiera
  crawlear un sitio, descargar páginas, ver cómo ve Google una URL, auditar un sitio
  hecho en React/Angular/Vue, o preparar datos para los demás skills SEO.
---

# Cloudflare Crawl

Base de datos de todos los skills: deja el HTML renderizado en disco para que la
auditoría, el enlazado interno y las imágenes trabajen sobre lo que Google ve, no
sobre el HTML inicial.

## Cuándo usar

- Sitio con JavaScript (SPA, Angular, Next sin SSR) → **obligatorio** antes de auditar.
- Sitio estático/WordPress → opcional; `shared/seo_extract.py` con HTTP basta.
- Para comparar HTML inicial vs. renderizado: usa los dos y compara title, H1 y enlaces.

## Entradas

Pregunta solo lo que falte:
1. URL de inicio.
2. **1 URL** o **varias** (si varias: máximo de páginas, default 10, y si descubrir por `sitemaps`, `links` o `all`).

Credenciales: `CF_ACCOUNT_ID` y `CF_API_TOKEN` (permiso *Browser Run – Edit*) en `.env`.
Si faltan, pide al usuario que copie `.env.example` a `.env`.

## Flujo

Cada llamada a Bash es una shell nueva: **empieza siempre con este bloque**. Carga el token
desde `.env` sin escribirlo nunca en el comando; no lo imprimas ni hagas `echo` de él.

```bash
set -a; source .env; set +a
D=example.com                                   # dominio sin www
OUT=crawler/output/$D; mkdir -p "$OUT"
API="https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/browser-run"
AUTH="Authorization: Bearer $CF_API_TOKEN"
SLUG='def slug: sub("^https?://[^/]+/?"; "") | gsub("[^A-Za-z0-9]+"; "-") | sub("^-+"; "") | sub("-+$"; "") | if . == "" then "home" else .[:150] end;'
```

### 1a. Descargar 1 o pocas URLs (`/content`)

Repite por URL:

```bash
URL=https://example.com/contacto
F=$(jq -rn --arg u "$URL" "$SLUG"'$u | slug').html
curl -s -X POST "$API/content" -H "$AUTH" -H "Content-Type: application/json" \
  -d "$(jq -n --arg u "$URL" '{url: $u, rejectResourceTypes: ["image","media","font","stylesheet"], gotoOptions: {waitUntil: "networkidle2", timeout: 30000}}')" \
  | jq -r 'if .success then .result else ("ERROR " + (.errors | tostring)) end' > "$OUT/$F"
head -c 200 "$OUT/$F"          # si empieza por "ERROR", reporta el error y no sigas con esa URL
M="$OUT/_manifest.json"; [ -f "$M" ] || echo '[]' > "$M"
jq --arg u "$URL" --arg f "$F" 'map(select(.url != $u)) + [{url: $u, status: 200, file: $f}]' "$M" > "$M.tmp" && mv "$M.tmp" "$M"
```

### 1b. Rastrear varias URLs (`/crawl`, asíncrono)

1. **Iniciar** y anotar el `JOB`:

```bash
curl -s -X POST "$API/crawl" -H "$AUTH" -H "Content-Type: application/json" \
  -d "$(jq -n --arg u "https://example.com" '{url: $u, limit: 50, source: "sitemaps", formats: ["html"], render: true, rejectResourceTypes: ["image","media","font","stylesheet"]}')" \
  | jq -r '.result // .errors'
```

`source`: `sitemaps` (lo que el sitio declara), `links` (lo que se descubre navegando) o `all`.
`render: false` es más rápido para sitios estáticos.

2. **Esperar**: consulta el estado (con `?limit=1` la respuesta es ligera). Repite cada ~10 s
   hasta que deje de ser `running`; si tarda, sigue consultando en llamadas separadas.

```bash
JOB=...   # el id del paso anterior
curl -s "$API/crawl/$JOB?limit=1" -H "$AUTH" | jq -r '.result | "\(.status) \(.finished)/\(.total)"'
```

Estados finales: `completed`, `errored`, `cancelled_due_to_limits`, `cancelled_due_to_timeout`.

3. **Descargar resultados** (paginados con `cursor` si superan 10 MB), separarlos en un `.html`
   por URL y crear el manifiesto:

```bash
JOB=...
: > "$OUT/_records.jsonl"; CUR=""
while :; do
  R=$(curl -s "$API/crawl/$JOB${CUR:+?cursor=$CUR}" -H "$AUTH")
  jq -c '.result.records[]' <<<"$R" >> "$OUT/_records.jsonl"
  CUR=$(jq -r '.result.cursor // empty' <<<"$R"); [ -n "$CUR" ] || break
done
while IFS= read -r rec; do
  f=$(jq -r "$SLUG"'select(.html) | (.url | slug) + ".html"' <<<"$rec")
  [ -n "$f" ] && jq -r '.html' <<<"$rec" > "$OUT/$f"
done < "$OUT/_records.jsonl"
jq -s "$SLUG"'[.[] | {url, status: (.metadata.status // .status), file: (if .html then (.url | slug) + ".html" else null end)}]' \
  "$OUT/_records.jsonl" > "$OUT/_manifest.json"
rm "$OUT/_records.jsonl"
jq -r 'group_by(.status) | map("\(.[0].status): \(length)") | .[]' "$OUT/_manifest.json"
```

### 2. Extracción + sección del reporte

```bash
python3 shared/seo_extract.py --dir "$OUT" -o "$OUT/_pages.json"
```

`_pages.json` es la entrada de `seo-audit`, `internal-linking` y `seo-images`.

Luego escribe `report/data/$D/cloudflare-crawl.json`. Si ya existe, este comando conserva
`summary`, `findings` y `actions`:

```bash
S=report/data/$D/cloudflare-crawl.json; mkdir -p "$(dirname "$S")"
OLD=$S; [ -f "$OLD" ] || OLD=/dev/null
jq -n --slurpfile p "$OUT/_pages.json" --slurpfile m "$OUT/_manifest.json" --slurpfile old "$OLD" \
  --arg site "$D" --arg date "$(date +%F)" '
  def st: tostring | if test("^[0-9]") then .[0:1] + "xx" else . end;
  $p[0] as $pages | ($pages | length) as $n | ($m[0] | map(.status | st)) as $s | ($old[0] // {}) as $o |
  def state($bad): if $bad == 0 then "good" elif $bad < $n * 0.3 then "warn" else "bad" end;
  ($s | map(select(test("^[45]") or . == "errored")) | length) as $err |
  ($s | map(select(test("^[0-9]|^errored$") | not)) | length) as $skip |
  ($pages | map(select(.word_count < 300)) | length) as $thin |
  ($pages | map(select((.headings.h1 | length) == 0)) | length) as $noh1 |
  {skill: "cloudflare-crawl", title: "Rastreo (HTML renderizado)", site: $site, generated: $date,
   source: "\($n) páginas renderizadas con Cloudflare Browser Run", score: null,
   summary: ($o.summary // ""), findings: ($o.findings // []), actions: ($o.actions // []), charts: [], code: [],
   kpis: [
     {label: "Páginas descargadas", value: $n, status: "info"},
     {label: "Errores (4xx/5xx)", value: $err, status: (if $err == 0 then "good" else "bad" end)},
     {label: "URLs no descargadas", value: $skip, status: "info", hint: "skipped / disallowed / cancelled"},
     {label: "Palabras promedio", value: (if $n > 0 then ($pages | map(.word_count) | add / $n | floor) else 0 end), status: "info"},
     {label: "Contenido escaso (<300 palabras)", value: $thin, status: state($thin)},
     {label: "Sin H1 tras render", value: $noh1, status: state($noh1), hint: "Si falta en el HTML renderizado, Google tampoco lo ve"}],
   tables: [{title: "Páginas rastreadas", columns: ["URL", "Estado", "Título", "Palabras", "Enlaces int."], auto: true,
     rows: ($pages | sort_by(.word_count) | map([.url, (.status // "-"), (.title // "—"), .word_count, .links_internal]))}]}
  ' > "$S.tmp" && mv "$S.tmp" "$S"
```

### 3. Análisis (Claude)

Completa en el JSON `summary`, `findings` y `actions` (sin `score`: este skill mide cobertura,
no calidad). Para no leer `_pages.json` entero, consúltalo con `jq`, p. ej.
`jq -r '.[] | select((.headings.h1 | length) == 0) | .url' "$OUT/_pages.json"`. Busca:
- Páginas con error o vacías tras render (sin title/H1) → contenido que depende de JS y falla.
- Contenido que solo aparece tras render (si comparaste con `seo_extract.py` por HTTP).
- Secciones del sitio que no aparecieron en el rastreo (¿bloqueadas, sin enlaces, fuera del sitemap?).
- URLs `disallowed`: el crawler respeta robots.txt; cruza con el skill `robots-txt`.

### 4. Reporte

```bash
python3 report/build_report.py <dominio> --open
```

## Reglas

- **El token nunca aparece en un comando, un archivo o la salida**: solo `$CF_API_TOKEN` cargado desde `.env`.
- Guarda siempre HTML, nunca markdown: el HTML es la fuente de verdad.
- El crawler respeta robots.txt y la protección anti-bots: si un sitio bloquea, dilo; no intentes evadirlo.
- Límites del plan gratuito: https://developers.cloudflare.com/browser-run/limits/ — revisa antes de rastreos grandes.
- Los resultados de `/crawl` quedan 14 días en Cloudflare: si el job ya terminó, basta repetir el paso 3 con el mismo `JOB`.
