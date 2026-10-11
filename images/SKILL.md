---
name: seo-images
description: >
  Auditoría de imágenes para SEO y rendimiento: alt, peso, formatos (WebP/AVIF),
  imágenes responsive, lazy loading, imagen LCP y prevención de CLS. Úsalo cuando el
  usuario diga "optimizar imágenes", "alt text", "SEO de imágenes", "imágenes pesadas"
  o "auditoría de imágenes".
---

# Imágenes

Las imágenes suelen ser el mayor peso de una página y la causa más común de LCP lento
y CLS. También son una fuente de tráfico (Google Imágenes) si tienen buen alt y nombre.

## Cuándo usar

Auditoría de imágenes de una página o una muestra del sitio. Si el usuario pide una
auditoría general, este skill se ejecuta además de `seo-audit`.

## Entradas

URL(s) o dominio. Útil: qué plantillas importan (home, producto, artículo).

## Flujo

### 1. Datos

Hace falta `--head-images` para obtener peso y tipo real de cada imagen:

```bash
python3 shared/seo_extract.py https://example.com https://example.com/producto-x --head-images -o crawler/output/<dominio>/_pages_img.json
# o sobre lo ya rastreado:
python3 shared/seo_extract.py --dir crawler/output/<dominio> --head-images -o crawler/output/<dominio>/_pages_img.json
```

### 2. Script → reporte

```bash
python3 images/scripts/image_metrics.py crawler/output/<dominio>/_pages_img.json
```

Escribe `report/data/<dominio>/seo-images.json` con: formatos, distribución de peso,
problemas por tipo, imágenes sin alt, imágenes más pesadas y candidata a LCP por página
(primera imagen de contenido fuera de header/nav).

### 3. Análisis (Claude)

Completa `score`, `summary`, `findings`, `actions`. Revisa:

1. **Alt**: describe la imagen, 10–125 caracteres, sin relleno de keywords. Decorativas: `alt=""`. Propón alt concretos para las que no lo tienen (mira el contexto de la página).
2. **LCP**: la imagen principal no lleva `loading="lazy"`, sí `fetchpriority="high"`, dimensiones y formato moderno. Confirma que la candidata del script sea realmente la principal.
3. **Peso** (orientativo): miniaturas <50 KB · contenido <100 KB · hero <200 KB. Crítico si >500 KB.
4. **Formato**: JPG/PNG → WebP o AVIF (`<picture>` con fallback si hace falta). SVG para logos e iconos.
5. **CLS**: `width` y `height` (o `aspect-ratio`) en todas.
6. **Responsive**: `srcset`/`sizes` en imágenes >400 px de ancho.
7. **Lazy**: `loading="lazy"` y `decoding="async"` bajo el pliegue.
8. **Nombre de archivo**: descriptivo, en minúsculas, con guiones (no `IMG_1234.jpg`).

Para correcciones de marcado, añade a `code` un antes/después:

```json
{"title": "Imagen LCP corregida", "lang": "html", "content": "<img src=\"hero.webp\" fetchpriority=\"high\" width=\"1200\" height=\"630\" alt=\"...\">"}
```

### 4. Reporte

`python3 report/build_report.py <dominio> --open`

## Puntuación

100 − 20 si la imagen LCP tiene lazy-load · −15 si >30 % sin dimensiones · −10 si >20 % sin alt ·
−10 si hay imágenes >500 KB · −5 si >50 % en formato legacy · −5 sin srcset en imágenes grandes ·
−3 nombres de archivo genéricos. Mínimo 0.

## Reglas

- **No uses WebFetch**: pierde `alt`, `loading`, `srcset` y `<picture>`. Usa `seo_extract.py`.
- No estimes mejoras de LCP en segundos ni ahorros que no puedas calcular. El ahorro por conversión a WebP es aproximado (25–35 % vs. JPG): dilo así.
- Las imágenes cargadas por CSS (`background-image`) no aparecen en el extractor; menciónalo si la página parece usar hero por CSS.
