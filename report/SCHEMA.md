# Contrato del reporte

Cada skill escribe **un** archivo `report/data/<dominio>/<skill>.json`.
`python3 report/build_report.py <dominio>` los une en `report/report.html`
(Pico CSS + Chart.js, un solo archivo, se abre con doble clic).

Flujo de dos manos:
1. **Script** del skill → rellena lo medible: `kpis`, `charts`, `tables` (y `source`).
2. **Claude** → lee los datos y completa lo interpretativo: `score`, `summary`, `findings`, `actions`, `code`.
   Re-ejecutar el script conserva estos campos (ver `shared/report_io.write_section`).
   Las `charts`/`tables`/`code` que genera el script llevan `"auto": true` y se regeneran;
   las que añade Claude (sin `auto`) se conservan.

## Estructura

```json
{
  "skill": "seo-audit",                 // id del skill (= nombre del archivo)
  "title": "Auditoría SEO",             // título visible de la sección
  "site": "example.com",                // dominio sin www
  "generated": "2026-10-11",
  "source": "6 páginas · HTML renderizado (Cloudflare)",   // de dónde salen los datos
  "score": 72,                          // 0-100 o null si el skill no puntúa
  "summary": "2-4 frases: estado, problema principal, primera acción.",

  "kpis": [
    {"label": "Páginas analizadas", "value": "6", "status": "info", "hint": "texto opcional"}
  ],                                    // status: good | warn | bad | info

  "charts": [
    {"type": "bar", "title": "Longitud de títulos",
     "labels": ["<30", "30-60", ">60"],
     "datasets": [{"label": "Páginas", "data": [1, 4, 1]}],
     "unit": "%"}                        // opcional, se añade a tooltips
  ],                                    // type: bar | hbar | stacked | doughnut | pie | radar | line

  "findings": [
    {"severity": "high",                // critical | high | medium | low
     "title": "Una frase con el problema",
     "evidence": "Qué se vio y dónde (dato concreto)",
     "impact": "Por qué importa",
     "recommendation": "Qué hacer",
     "urls": ["https://example.com/x"]}
  ],

  "tables": [
    {"title": "Páginas sin meta description", "columns": ["URL", "Título"], "rows": [["...", "..."]]}
  ],

  "actions": [
    {"priority": 1, "title": "Arreglar robots.txt", "impact": "alto", "effort": "bajo"}
  ],                                    // impact/effort: alto | medio | bajo

  "code": [
    {"title": "robots.txt propuesto", "lang": "text", "content": "User-agent: *\n..."}
  ]
}
```

## Reglas

- Todo en español.
- **Máximo 1 gráfica por sección**, y solo si muestra algo que una tabla o un número no dicen igual de bien.
  Si un dato cabe en un indicador (`kpis`), va ahí.
- El informe es siempre en modo claro, sin menú de navegación ni tarjetas: no añadir estilos ni HTML.
- `findings` siempre con `evidence` concreta. Sin evidencia → no es un hallazgo.
- `score` solo si el skill define cómo calcularlo en su SKILL.md. No inventar.
- No escribir HTML dentro de los textos: el reporte escapa todo.
- Las `actions` de todos los skills se consolidan en el **Plan de acción** del resumen,
  ordenadas por impacto/esfuerzo. Escríbelas como acciones, no como problemas.
