---
name: cloudflare-crawl
description: >
  Descarga el HTML renderizado por Cloudflare de una o varias URLs.
  Esto representa exactamente lo que Google lee de un sitio web.
  Usar cuando el usuario quiera descargar páginas, crawlear un sitio,
  ver cómo ve Google una URL, o recopilar HTML de múltiples páginas.
---

# Cloudflare Crawler

## Al invocar este skill

Pregunta siempre al inicio:

> ¿Quieres descargar **1 URL** o **buscar y descargar varias**?

---

## Opción A — 1 URL

1. Pide la URL
2. Usa el endpoint `/content` de Cloudflare Browser Rendering para obtener el HTML renderizado
3. Guarda el resultado como archivo `.html` en `crawler/output/`
4. El archivo guardado es el HTML que Google realmente lee

### Cómo descargar 1 URL

```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/{account_id}/browser-rendering/content" \
  -H "Authorization: Bearer {api_token}" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "rejectResourceTypes": ["image", "media", "font", "stylesheet"]}'
```

- Usa `render: true` (por defecto) para que Cloudflare ejecute JavaScript con Chrome headless antes de devolver el HTML — esto es exactamente lo que Google Caffeine indexa
- `rejectResourceTypes` excluye imágenes, fuentes y CSS para acelerar la descarga sin perder contenido indexable
- Guarda siempre como `.html`, nunca como `.md`

---

## Opción B — Buscar y descargar varias

1. Pide la URL de inicio (o patrón de URLs)
2. Pregunta cuántas páginas como máximo (default: 10)
3. Usa el endpoint `/crawl` con el flujo async: POST → poll → GET resultados
4. Muestra un resumen con todas las URLs descargadas

### Cómo crawlear varias URLs

Guarda cada página como `{slug}.html` en `crawler/output/`.

```bash
# 1. Iniciar el crawl
curl -X POST "https://api.cloudflare.com/client/v4/accounts/{account_id}/browser-rendering/crawl" \
  -H "Authorization: Bearer {api_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "limit": 10,
    "formats": ["html"],
    "render": true,
    "rejectResourceTypes": ["image", "media", "font", "stylesheet"]
  }'

# 2. Obtener el job_id de la respuesta y hacer polling
curl "https://api.cloudflare.com/client/v4/accounts/{account_id}/browser-rendering/crawl/{job_id}?limit=1" \
  -H "Authorization: Bearer {api_token}"

# 3. Cuando status = "completed", obtener todos los resultados
curl "https://api.cloudflare.com/client/v4/accounts/{account_id}/browser-rendering/crawl/{job_id}" \
  -H "Authorization: Bearer {api_token}"
```

El polling se repite cada 5 segundos hasta que `status` cambie de `"running"` a `"completed"`.

---

## Qué devuelve Cloudflare

Cloudflare ejecuta el JS de la página con Chrome headless y devuelve el **HTML final del DOM** — el mismo HTML que Google Caffeine recibe al indexar. Esto incluye:

- Contenido generado por JavaScript (React, Vue, etc.)
- Todo el `<head>`: meta description, canonical, OG tags, hreflang, structured data
- Texto visible en el DOM después del render
- Links presentes en el DOM final

**No incluye**: lo que está en `<noscript>`, iframes externos, ni contenido detrás de login/captchas.

**Formato de salida**: siempre `.html`. Nunca usar markdown — el HTML es la fuente de verdad.

---

## Credenciales necesarias

El usuario debe tener:
- `account_id` de Cloudflare
- API token con permiso **"Browser Rendering – Edit"**

Si no los tiene, pide que los obtengan desde el dashboard de Cloudflare → My Profile → API Tokens.

---

## Límites importantes

- Plan gratuito: 5 crawls/día, máx 100 páginas por crawl
- Plan de pago ($5/mes): crawls ilimitados, hasta 100,000 páginas
- El crawler **no** puede bypassear protección bot de Cloudflare (Turnstile, WAF). Para crawlear tu propio sitio protegido, crear una regla WAF skip rule.
