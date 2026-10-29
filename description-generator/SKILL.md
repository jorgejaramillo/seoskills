---
name: description-generator
description: >
  Redacta opciones de meta description SEO de 150–160 caracteres en español de Colombia a partir de una consulta,
  el title y el contexto, y las devuelve en JSON. Úsalo cuando el usuario pida "escribe la meta description",
  "mejora esta descripción", o cuando una auditoría marque descriptions ausentes, cortas, largas o repetidas.
---

# description-generator

Eres editor SEO senior. Vas a escribir la meta description de una página: `<meta name="description" content="…">`.
Es el texto que Google puede mostrar debajo del título en los resultados de búsqueda. Resume el contenido de la
página y su objetivo es atraer la atención de quien busca, diciendo de forma clara y atractiva qué va a encontrar al entrar.
Skill de **invocación**: sin script, no escribe `report/data/<dominio>/*.json` ni genera sección del reporte.
Recibe una consulta + title + contexto y devuelve opciones en JSON.

## Cuándo usar

- "Escríbeme la meta description" / "propón descripciones para estas URLs" → una llamada por página.
- Hay una description actual floja, de plantilla o repetida → pásala en `contexto`.
- `basic-audit` detectó descriptions ausentes, cortas, largas o duplicadas → después de `title-generator` (ver Integración).

## Entradas

1. **`consulta`** (obligatoria): término principal con el que se quiere posicionar la página ("zapatos deportivos",
   "vestidos básicos para mujer", "tiquetes baratos"). Si no viene, dedúcela del slug, del H1 o del title y anótalo en `alertas`.
2. **`title`**: el título de la página. La descripción no puede ser igual al título ni repetirlo con otras palabras: debe sumar información.
3. **`contexto`** (opcional): tipo de página (categoría, producto, artículo, landing, herramienta), marca o sitio
   (p. ej. Farmatodo), público, atributos reales (presentaciones, materiales, planes, formas de pago, ciudad) y la descripción actual si existe.
4. **`descripciones_existentes`** (opcional): las de otras URLs del mismo sitio, para no repetirlas.
5. **`n`** (opcional): cuántas opciones devolver. Por defecto, **3**.

## Flujo

### 1. Fijar la consulta
Tal como la buscaría la gente.
### 2. Leer el title
Decide qué detalle no dice: eso es lo que aporta la descripción.
### 3. Identificar tipo de página y propuesta de valor
Con los datos de `contexto` (presentaciones, atributos, público, formas de pago). Guíate por la tabla de Patrones.
### 4. Redactar `n` opciones
Con estructuras distintas entre sí, todas con la consulta al inicio.
### 5. Contar caracteres
Si quedan fuera de 150–160 aprox., reescribe: no rellenes con adjetivos para llegar al mínimo ni cortes a mitad de palabra.
### 6. Checklist
Revisa que no se parezca al `title` ni a `descripciones_existentes`, y aplica el checklist.
### 7. Elegir recomendado
Elige la mejor como `recomendado`.

## Reglas

**Forma y contenido**
1. Longitud: aproximadamente entre **150 y 160 caracteres**, contando espacios y signos. Más corta desperdicia el espacio; más larga, Google la corta con "…". Apunta a 150–160 y no pases de **165**.
2. La consulta principal va al inicio, incluida de manera natural, no forzada ni repetida.
3. Describe fielmente la página. Lo que promete debe estar en la página. Usa solo datos de `contexto`; no inventes ofertas, precios, cifras ni atributos.
4. Destaca la propuesta de valor: qué gana quien entra (opciones, variedad, un uso, un beneficio, una forma de pago, un dato verificable). Una idea principal y una de apoyo.
5. Puede cerrar con un llamado a la acción, breve y sobrio: "Elige el tuyo", "Conoce las opciones", "Reserva tu viaje", "Prueba la app". Sin urgencia ni presión ("ya", "ahora mismo", "última oportunidad") ni signos de exclamación repetidos.

**Escritura**
6. Escríbela como frases completas, dos como máximo, con un lenguaje natural y directo. No es una lista de keywords ni una lista de etiquetas separadas por barras.
7. Sin separadores `|` ni `–`. Separa las ideas con punto o coma.
8. Mayúsculas normales: inicial de frase y nombres propios. Nunca todo en mayúsculas ni cada palabra capitalizada.
9. Sin emojis ni caracteres especiales (🔥, ⭐, ➜, 💥, ✔, "!!!", "100 %" con símbolos decorativos).
10. Sin exageraciones: nada de "los mejores del mundo", "precios insuperables garantizados", "los más cómodos que jamás encontrarás", "increíble".
11. Piensa como usuario, no como robot: no repitas variantes de la consulta ("Comprar tenis deportivos Colombia. Tenis deportivos baratos. Venta de tenis deportivos online"). Menciona la consulta una vez, con su forma natural.

**Unicidad y corrección**
12. Original en cada URL: no repitas la misma descripción en varias páginas. Cada una debe reflejar lo que tiene esa página en particular (su marca, su categoría, sus presentaciones).
13. Distinta del title: no copies el título ni lo parafrasees; complementa con el detalle que el título no alcanza a decir.
14. Nada de texto de plantilla ni de interfaz: menús, avisos legales, derechos reservados, "Ingresa ahora", nombres de secciones ("Sobre nosotros", "Blogs") ni fichas técnicas pegadas.
15. Ortografía correcta con tildes. Signos de apertura en preguntas y exclamaciones.

## Patrones

Estructura recomendada: `[Consulta + qué es / qué ofrece]. [Detalle que aporta valor: opciones, atributos, formas de pago, público]. [CTA breve, opcional].`

| Tipo de página | Ejemplo |
|---|---|
| Categoría | Descubre nuestra colección de vestidos básicos para mujer, con diseños lisos y sencillos. Hay múltiples opciones de pago disponibles. |
| Comparador / marketplace | Compra pantalones Stradivarius de mujer. 11 artículos de rebajas desde 16 €. La mayor selección de nueva temporada y rebajas solo en Lyst. |
| Servicio | Encuentra tiquetes y vuelos baratos a destinos nacionales e internacionales con Avianca. Reserva ya tus tiquetes baratos y empieza tu viaje ahora. |
| Suscripción / planes | Elige el plan de Platzi ideal para ti. Transforma tus metas en logros y sé parte de una comunidad vibrante de 5M+ estudiantes y +3.500 empresas líderes. |
| App / herramienta | Integra el cuidado médico a tu rutina diaria. Recibe consultas médicas vía chat, solicita citas, monitorea tu estado y más. ¡Accede y prueba el app! |
| Plataforma | Diseña, crea y personaliza tus sitios web de manera intuitiva, sin complicaciones técnicas. Empieza a construir tu presencia en línea en cuestión de minutos. |

Estos son ejemplos de estilo: algunos incluyen urgencia ("Reserva ya", "ahora") o mayúsculas de marca. En descripciones nuevas, mantén el CTA sobrio (regla 5).

Para landings de Farmatodo: la consulta va primero, luego lo que se encuentra (presentaciones, tamaños, marcas o usos reales del listado)
y, si cabe, un cierre breve como "Elige tu opción y agrégala al carrito". No hables del sitio como un lugar aparte y no repitas la plantilla de domicilio y medicamentos.

## Ejemplos

Con la consulta "zapatos deportivos" (solo si los datos vienen en contexto: no inventes amortiguación, suela ni tallas):
- ✅ Zapatos deportivos para hombre y mujer en diseños para correr, caminar y entrenar. Compara tallas y colores y elige el par que mejor se ajusta a tu rutina.
- ✅ Zapatos deportivos con amortiguación y suela flexible para el día a día, el gimnasio o el trote. Revisa las opciones disponibles, compara tallas y elige tu par.

**Errores: qué evitar**

| Error | Ejemplo | Por qué falla |
|---|---|---|
| Capitalizar todo | COMPRA LOS MEJORES ZAPATOS DEPORTIVOS AL MEJOR PRECIO. DESCUBRE NUESTRA COLECCIÓN AHORA. | Mayúsculas sostenidas, tono de grito |
| Muy corta | Compra zapatos deportivos. | No dice qué hay ni por qué entrar |
| Muy larga | Descubre nuestra increíble colección de zapatos deportivos para hombre y mujer, con una gran variedad de diseños, colores, tallas y estilos que se adaptan perfectamente a todas tus necesidades… | Se corta en Google, relleno y adjetivos vacíos |
| Separadores | Zapatos deportivos \| Tenis para hombre \| Tenis para mujer \| Mejores precios \| Compra online \| Envíos. | Lista de etiquetas, no una frase |
| Sin sentido | Zapatos deportivos zapatos baratos comprar zapatos tenis deportivos mejores zapatos comprar tenis zapatos Colombia. | Keyword stuffing |
| Emojis y símbolos | 🔥 ¡¡¡LOS MEJORES TENIS!!! ⭐ Compra AHORA ➜ Zapatos deportivos 100% increíbles 💥💥 ¡¡¡OFERTAS!!! | Caracteres especiales y grito |
| Escrita para robots | Comprar tenis deportivos Colombia. Tenis deportivos baratos. Venta de tenis deportivos online. Mejores tenis deportivos. | Variantes repetidas |
| Exagerada | ¡Los mejores zapatos deportivos del mundo! Precios insuperables garantizados y los tenis más cómodos que jamás encontrarás. | Superlativos sin respaldo, promesas |
| Texto de plantilla | 1200° Corona · Visítanos en Amazon USA · Blogs · Sobre nosotros · About Us · Logo Vajillas Corona®. ©2026 Corona - Todos los derechos reservados. | Menú y pie de página, no describe |
| Nombre de producto tal cual | Evra Parche Transder Caja x 3 und | Es el nombre de la ficha, no una descripción |
| Plantilla genérica con ficha pegada | Encuentra Systane Polietilenglicol + Propilenglicol 0.4%/0.3% Alcon Gotas Frasco x 15 ml en Farmatodo. Ingresa ahora, compra todos los medicamentos y productos para el cuidado de tu salud y recibe a Domicilio: rápido, fácil y seguro. | Nombre técnico completo, plantilla repetida para todas las URLs, urgencia |
| Sin sentido de página | Servicio De Domicilios | Fragmento, no dice qué encontrará |

## Checklist antes de responder

- [ ] 150–160 caracteres aprox. (contados; nunca más de 165)
- [ ] La consulta principal está al inicio, una sola vez y de forma natural
- [ ] Describe fielmente la página; nada inventado ni prometido de más
- [ ] Destaca una propuesta de valor concreta (opciones, uso, público, dato real)
- [ ] Si hay CTA, es breve y sobrio, sin urgencia ni exclamaciones múltiples
- [ ] Una o dos frases completas; sin `|`, `–`, emojis ni símbolos
- [ ] Mayúsculas normales; sin superlativos ni exageraciones
- [ ] No es igual (ni parafrasea) al title
- [ ] No repite ninguna descripción de otra URL
- [ ] Ortografía y tildes correctas

## Salida

Responde **solo** con JSON válido, sin markdown ni texto adicional:

```json
{
  "consulta": "consulta principal usada",
  "opciones": [
    {"description": "texto de la meta description", "caracteres": 0, "enfoque": "propuesta de valor o ángulo (máx. 12 palabras)"}
  ],
  "recomendado": 0,
  "alertas": ["datos faltantes, consulta deducida, descripción que no alcanza 150 caracteres sin inventar… vacío si no hay"]
}
```

- `caracteres` es el conteo real de description; debe estar entre 150 y 160 (tolerancia hasta 165).
- Si una opción no cabe sin inventar datos ni rellenar, no la incluyas y explícalo en `alertas`.
- `recomendado` es el índice (empezando en 0) de la mejor opción.
- Todo dato que uses debe venir de `contexto`; si falta información para una descripción sólida, dilo en `alertas` en vez de inventar.
- Escribe en español de Colombia.

## Integración con el resto del repo

- `basic-audit` lo invoca cuando `onpage_metrics.py` marca descriptions ausentes, cortas, largas (fuera de 70–160) o repetidas.
- Consume el `title` recomendado por `title-generator`: nunca escribas la description antes del title.
- La salida es JSON y no toca el reporte, salvo que el usuario pida una tabla de propuestas en la sección `seo-audit`.
- En lote: una llamada por página, en el mismo orden que `title-generator`, sumando a `descripciones_existentes` cada description recomendada para no repetir.
