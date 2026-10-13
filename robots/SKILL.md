---
name: robots-txt
description: >
  Valida, audita y genera archivos robots.txt para SEO y bots de IA. Úsalo cuando el
  usuario mencione robots.txt, directivas de rastreo, bloquear bots (GPTBot, ClaudeBot,
  PerplexityBot…), crawl budget, o pegue un robots.txt y pregunte "¿está bien?".
  Funciona con cualquier CMS.
---

# robots.txt

Tres modos: **auditar** el robots.txt publicado, **validar** un borrador, **generar** uno nuevo.
Los tres terminan en el reporte. robots.txt es pequeño: léelo entero, no hace falta script.

## Cuándo usar

- "Revisa mi robots.txt" / "¿por qué Google no rastrea X?" → auditar.
- El usuario pega un robots.txt → validar.
- "Hazme un robots.txt" / "bloquea los bots de IA" → generar y luego validar con los mismos pasos.

## Entradas

1. Dominio (o el texto del robots.txt si lo pega).
2. Para generar: plataforma (WordPress, Shopify, Next…) y **política de IA** (bloquear entrenamiento, bloquear todo, permitir todo). El robots.txt **solo niega acceso**: la opción "permitir" no se escribe, se omite — la ausencia de reglas ya lo permite todo. Si no la menciona, no agregues bloques de IA.
3. Opcional: rutas que el usuario quiere comprobar.

## Flujo

### 1. Datos

```bash
D=example.com
curl -sL -o /dev/null -w 'HTTP %{http_code} · %{size_download} bytes · %{url_effective}\n' "https://$D/robots.txt"
curl -sL "https://$D/robots.txt"
```

Por cada línea `Sitemap:`, comprueba que responda y toma una muestra de URLs para probar:

```bash
SM=https://example.com/sitemap.xml
curl -sL -o /dev/null -w '%{http_code}\n' "$SM"
curl -sL "$SM" | grep -oE '<loc>[^<]+' | sed 's/<loc>//' | head -30
```

Si es un sitemap index (`<sitemapindex>`), repite el segundo comando con 1–2 sitemaps hijos.

### 2. Cómo leerlo (semántica de Google, RFC 9309)

**Sintaxis**
- Directivas válidas: `User-agent`, `Allow`, `Disallow`, `Sitemap`, `Crawl-delay` (Google lo ignora). Cualquier otra es un error.
- Un grupo = una o varias líneas `User-agent` seguidas + sus reglas. Una regla antes de cualquier `User-agent` es un error.
- Directivas sin distinción de mayúsculas; las **rutas sí distinguen** (`/Admin/` ≠ `/admin/`).
- `Disallow:` vacío = permitir todo. `Sitemap:` es independiente de los grupos y debe ser URL absoluta.
- Estado HTTP: 404 = todo permitido · 5xx = Google deja de rastrear el sitio · >500 KiB = Google ignora el resto.

**Qué grupo aplica a un bot**
- Se usa el grupo cuyo `User-agent` coincide de forma más específica con el nombre del bot (sin distinguir mayúsculas).
- Si un bot tiene grupo propio, **ignora por completo** el grupo `*` (no se suman). Google sí une varios grupos con el mismo user-agent.

**Qué regla gana para una URL** (prueba ruta + query, p. ej. `/productos?orden=precio`)
1. Toma todas las reglas del grupo cuyo patrón coincide con el **inicio** de la ruta. `*` = cualquier secuencia; `$` al final = fin de la URL.
2. Gana la regla de **patrón más largo** (en caracteres).
3. En empate gana `Allow`. Sin reglas que coincidan → permitida.

Ejemplo: `Disallow: /cart` + `Allow: /cart/public$` → `/cart/x` bloqueada, `/cart/public` permitida, `/cart/public/x` bloqueada.

### 3. Análisis (Claude)

Revisa, en este orden:
1. **Indexación**: aplica las reglas de Googlebot a la muestra del sitemap y a las rutas del usuario. Cualquier URL del sitemap bloqueada es un hallazgo alto o crítico. ¿Se bloquean CSS/JS necesarios para renderizar?
2. **Sitemaps**: declarados, URL absoluta, responden 200, y contienen las páginas que existen.
3. **Crawl budget**: búsqueda interna, filtros/facetas y parámetros de orden sin bloquear en sitios grandes.
4. **Bots de IA**: para cada bot de la tabla de referencia, decide si queda **bloqueado** (`Disallow`) o sin regla propia (usa `*`). Nunca escribas reglas para "permitir" un bot: sin regla ya está permitido por defecto. Error típico: bloquear bots de búsqueda queriendo bloquear solo entrenamiento.
5. **Seguridad**: rutas sensibles expuestas (robots.txt es público).
6. **Malentendidos**: `Disallow` no es `noindex`; bloquear una URL impide que Google vea su canonical o noindex.

**Bots de referencia (2026)**

| Tipo | Bots |
|------|------|
| Entrenamiento IA | GPTBot, ClaudeBot, anthropic-ai, Google-Extended, Applebot-Extended, CCBot, Bytespider, Meta-ExternalAgent, FacebookBot, Amazonbot, cohere-training-data-crawler, Diffbot, AI2Bot |
| Búsqueda / usuario IA | OAI-SearchBot, ChatGPT-User, Claude-SearchBot, Claude-User, PerplexityBot, Perplexity-User, DuckAssistBot |
| Buscadores | Googlebot, Bingbot |

La tabla solo sirve para decidir **bloqueos**; no implica crear un grupo `User-agent` por cada bot. Solo se escriben reglas para lo que se quiere negar.

### 4. Sección del reporte

Escribe `report/data/<dominio>/robots-txt.json` (contrato en `report/SCHEMA.md`). Sin gráficas.

```json
{
  "skill": "robots-txt", "title": "robots.txt", "site": "example.com", "generated": "AAAA-MM-DD",
  "source": "https://example.com/robots.txt · HTTP 200",
  "score": 85, "summary": "2-4 frases.",
  "kpis": [
    {"label": "Estado HTTP", "value": 200, "status": "good", "hint": "404 = todo permitido; 5xx = Google deja de rastrear"},
    {"label": "Errores de sintaxis", "value": 0, "status": "good"},
    {"label": "Sitemaps declarados", "value": 1, "status": "good"},
    {"label": "URLs del sitemap bloqueadas", "value": 0, "status": "good", "hint": "de 30 probadas con Googlebot"},
    {"label": "Bots de IA de entrenamiento bloqueados", "value": "0 de 13", "status": "info"}
  ],
  "charts": [],
  "findings": [{"severity": "high", "title": "…", "evidence": "…", "impact": "…", "recommendation": "…", "urls": ["…"]}],
  "tables": [
    {"title": "Bots de IA y buscadores", "columns": ["Bot", "Tipo", "Estado"], "rows": [["GPTBot", "Entrenamiento", "Sin regla propia"]]},
    {"title": "Prueba de URLs (Googlebot)", "columns": ["Ruta", "Resultado", "Regla ganadora"], "rows": [["/carrito", "BLOQUEADA", "Disallow: /carrito"]]},
    {"title": "Sitemaps declarados", "columns": ["URL", "Estado"], "rows": [["https://example.com/sitemap.xml", 200]]}
  ],
  "actions": [{"priority": 1, "title": "…", "impact": "alto", "effort": "bajo"}],
  "code": [
    {"title": "robots.txt actual", "lang": "text", "content": "…texto completo…"},
    {"title": "robots.txt propuesto", "lang": "text", "content": "…solo si propones cambios…"}
  ]
}
```

Después: `python3 report/build_report.py <dominio> --open`.

## Puntuación

Empieza en 100: −40 si bloquea todo el sitio o URLs del sitemap importantes · −25 si responde 5xx ·
−15 por bloquear CSS/JS de render · −10 sin sitemap declarado o sitemap roto · −5 por cada error de sintaxis ·
−5 política de IA incoherente. Mínimo 0.

## Generar un robots.txt

- **Solo** `Disallow` para rutas confirmadas en el sitio (sitemap, navegación o el usuario). Nunca inventes rutas.
- El robots.txt **no invita ni permite bots**: solo niega acceso. Escribe `User-agent: *` y únicamente grupos `User-agent` para bots que vas a **bloquear** (`Disallow`). No agregues grupos para bots permitidos — sin reglas ya están permitidos.
- Sin comentarios ni cabeceras. Orden: `User-agent: *`, luego los grupos de bots bloqueados (entrenamiento y búsqueda según la política), `Sitemap:` al final.
- Antes de entregarlo, pásale los pasos 2 y 3 (sintaxis + prueba de la muestra del sitemap) y confirma que no bloquea nada indexable.

## Reglas

- No modificar el robots.txt del sitio: se entrega el propuesto en el reporte y en el chat para copiar.
- Al probar URLs, muestra en la tabla la regla ganadora: es la evidencia del hallazgo.
- Si la muestra es pequeña, dilo (p. ej. "30 de 1.200 URLs probadas").
