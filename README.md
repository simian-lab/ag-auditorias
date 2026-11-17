# ag-auditorias

> **En una línea:** le das a Claude la URL del sitio web de un prospecto y te entrega un micrositio con las 5 a 10 mejoras más importantes de ese sitio, con evidencia real, para que alguien de Simian lo presente en una reunión y convenza al cliente de trabajar con nosotros.

Este repositorio tiene dos cosas:

- **El plugin `simian-web-audit`** para Claude Code (`plugins/simian-web-audit/`), que hace la auditoría.
- **Las auditorías ya hechas** (`audits/<dominio>/`), que se publican como sitio web.

Sitio publicado: https://auditorias-simian.space.fast/ (también https://simian-lab.github.io/ag-auditorias/).

---

## Contenido

1. [Qué hace y para quién](#qué-hace-y-para-quién)
2. [Requisitos](#requisitos)
3. [Instalación](#instalación)
4. [Cómo hacer una auditoría](#cómo-hacer-una-auditoría)
5. [Cómo funciona por dentro](#cómo-funciona-por-dentro)
6. [Cómo se calcula el puntaje](#cómo-se-calcula-el-puntaje)
7. [Qué contiene el micrositio](#qué-contiene-el-micrositio)
8. [Estructura de una auditoría](#estructura-de-una-auditoría)
9. [Publicar una auditoría](#publicar-una-auditoría)
10. [Estructura del repositorio](#estructura-del-repositorio)
11. [Desarrollo del plugin](#desarrollo-del-plugin)
12. [Reglas que el plugin siempre respeta](#reglas-que-el-plugin-siempre-respeta)

---

## Qué hace y para quién

**Para quién:** el equipo comercial y de diseño de Simian, antes de reunirse con un prospecto.

**Qué produce:** un micrositio (`report/index.html`) que funciona sin conexión a internet y que:

- Le da al sitio un puntaje general y uno por área: experiencia de usuario (UX), accesibilidad, diseño visual y calidad técnica.
- Presenta un **Top N** (mínimo 5, máximo 10) de mejoras, ordenadas por impacto, con capturas reales del sitio.
- Compara el sitio con su competencia.
- Propone un rediseño y un plan de trabajo.
- Opcionalmente agrega una página que compara cómo carga el sitio frente a la competencia y un módulo **Extra** de SEO, visibilidad en buscadores con IA y presencia en línea.

El objetivo es **persuadir**, no solo informar. Pero nunca se inventan datos: lo que no se pudo medir se omite o se marca como `[dato por confirmar]`.

## Requisitos

- macOS (los scripts usan `sips` para procesar imágenes).
- Python 3. Solo usa la librería estándar, así que no hay que hacer `pip install`.
- Google Chrome instalado en `/Applications/Google Chrome.app`.
- Lighthouse CLI: `npm i -g lighthouse`.
- [Claude Code](https://claude.com/claude-code).
- Opcional: conexión a OpenSEO en Claude, para obtener respuestas reales de buscadores con IA. **Consume créditos pagos**; el tope por auditoría es de 50 créditos (`config/settings.json`).

Al inicio de cada auditoría el plugin corre una verificación (`preflight.py`) y te dice qué falta.

## Instalación

```bash
git clone https://github.com/simian-lab/ag-auditorias.git
cd ag-auditorias
claude
```

Dentro de Claude Code, registra este repositorio como marketplace e instala el plugin:

```
/plugin marketplace add ./
/plugin install simian-web-audit@ag-auditorias
```

Si la skill no aparece de inmediato, reinicia Claude Code.

## Cómo hacer una auditoría

Abre Claude Code **siempre desde la raíz del repositorio**, porque las auditorías se guardan en `./audits/`. Luego escribe:

```
audita https://example.com
```

Claude te hace una pregunta a la vez:

1. La URL del prospecto (obligatoria).
2. El contexto del negocio: qué vende, a quién y en qué ciudad o país. Es opcional; si lo omites, Claude lo deduce del sitio y avisa que es una deducción.
3. Capturas o material adicional (opcional).
4. Los competidores: puedes darle nombres o URL, o decirle "búscalos tú".
5. Los bloques opcionales, uno por uno:
   - Página de comparación de carga ("Mira cómo carga tu sitio frente a tu competencia").
   - Módulo Extra (SEO, visibilidad en buscadores con IA y presencia en línea).
   - Solo si elegiste el Extra: respuestas reales de IA con OpenSEO (pago; Claude pide aprobación antes de gastar créditos).

Al terminar, Claude abre el micrositio y te deja un resumen: el puntaje general, los títulos del Top N, los bloques incluidos, lo que no se pudo verificar, los textos entre `[...]` del rediseño que debes confirmar con el cliente y los créditos de OpenSEO que se gastaron.

**Auditoría interna:** para auditar un sitio de Simian, la auditoría se marca como `internal`. Así el reporte oculta la sección "Por qué Simian" y no se genera la propuesta de rediseño.

## Cómo funciona por dentro

El flujo completo está en `plugins/simian-web-audit/skills/simian-web-audit/SKILL.md`. Tiene 9 pasos:

| Paso | Qué pasa | Quién lo hace |
| --- | --- | --- |
| 1. Verificación | Revisa que estén instalados Chrome, Lighthouse y lo demás. | `preflight.py` |
| 2. Entrevista | Recoge la URL, el contexto, los competidores y las opciones, y crea la carpeta de la auditoría con su `BRIEF.md`. | Claude + `init_audit.py` |
| 3. Evidencia | Descarga el HTML, corre Lighthouse en móvil y escritorio, y toma capturas. Se hace una sola vez y todos los agentes la comparten. | `collect_evidence.py` |
| 4. Ola 1: áreas | Cuatro agentes en paralelo evalúan UX, accesibilidad (`a11y`), diseño visual y calidad técnica (`tech`). Cada uno escribe `findings/<área>.json`. | Agentes + `validate_findings.py` |
| 5. Síntesis | Claude elige y ordena las mejoras del Top N (`findings/top10.json`). | Claude (`references/synthesis.md`) |
| 6. Ola 2: persuasión | Agentes en paralelo hacen la crítica de diseño (`ui-critique`), el rediseño (`redesign`) y la comparación con la competencia (`benchmark`). Si se eligió el Extra, también `seo` y `presence`, y OpenSEO cuando aplica. | Agentes |
| 7. Puntaje y construcción | Calcula los puntajes, construye la página de carga (si se eligió) y luego el micrositio. | `score.py`, `build_load_page.py`, `build_report.py` |
| 8. Revisión visual | Toma una captura del micrositio con Chrome sin interfaz y corrige problemas como textos desbordados o recortes rotos. | Claude |
| 9. Entrega | Presenta el resumen al usuario. | Claude |

Las instrucciones de cada agente están en `skills/simian-web-audit/references/agents/`. La forma exacta de cada archivo de hallazgos está definida en `schemas/`, y el validador rechaza los archivos que no la cumplen.

## Cómo se calcula el puntaje

El puntaje es **determinista**: el mismo sitio da el mismo puntaje sin importar cuántos hallazgos escriba un agente. La versión actual del cálculo es la 3 (`config/scoring.json`).

- Cada área tiene una **rúbrica fija** de criterios con peso (`config/rubric.json`): 11 criterios para UX, accesibilidad, diseño visual y calidad técnica, y 10 para SEO.
- Por cada criterio, el agente responde si el sitio **cumple**, **cumple en parte** (cuenta la mitad del peso) o **no cumple**.
- El puntaje del área es el porcentaje del peso que el sitio obtuvo.
- En **accesibilidad** y **calidad técnica** ese porcentaje se promedia con Lighthouse: con la categoría *accessibility* en la primera, y con *performance* y *best-practices* en la segunda.
- El **puntaje general** es el promedio de las cuatro áreas. La meta de referencia es 80.
- SEO tiene su propio puntaje y **no** entra en el general.

## Qué contiene el micrositio

Las secciones se generan en este orden (`scripts/report/sections/`). Si una sección no tiene datos, se omite.

1. **Portada:** el logo de Simian, el título de la auditoría y una frase de introducción.
2. **El sitio hoy:** el sitio actual dentro de un marco de navegador, con los errores detectados señalados con marcadores, y su versión móvil.
3. **Puntaje:** el puntaje general y las cuatro áreas frente al nivel recomendado, con la explicación del cálculo y la lista de criterios que se cumplen (✓), se cumplen en parte (◐) o no se cumplen (✕).
4. **Dato grande:** la cifra medida que más duele, en una cuadrícula de 100 celdas, y el enlace a la página de comparación de carga si se generó.
5. **Top N:** las mejoras priorizadas. Cada una se puede desplegar y muestra su titular, su impacto, su esfuerzo, un recorte real del sitio y la comparación entre lo que hay hoy y lo que se propone.
6. **Crítica de diseño:** el veredicto, recortes reales del sitio y una paleta propuesta.
7. **Competencia:** la prueba de los cinco segundos, con la primera pantalla del cliente junto a la de sus competidores y los mismos criterios para todos.
8. **Rediseño:** un deslizador de antes y después entre la página de inicio actual y el concepto de rediseño de Simian.
9. **Extra (si se eligió):** pruebas de búsqueda, vista previa en Google y WhatsApp, consistencia de nombre, dirección y teléfono, respuestas reales de IA y correcciones para buscadores con IA.
10. **Plan:** tres etapas base con todas las mejoras del Top, una cuarta etapa opcional y una tabla con todos los puntos.
11. **Por qué Simian:** casos del portafolio de Simian elegidos porque sus etiquetas coinciden con los problemas del Top (`assets/simian/cases.json`). Se oculta en auditorías internas.

La **página de comparación de carga** (`report/feature-carga.html`) es aparte. Muestra fotogramas reales de Lighthouse de cómo carga el sitio frente a la competencia. Si una pantalla de bienvenida o un pop-up hacen que el tiempo medido no coincida con lo que ve el visitante, se muestra una aclaración (`load_caveat_es`).

El diseño sigue el manual de identidad de Simian: verde bosque `#0B785D`, Vollkorn para los títulos y Source Sans 3 para el texto. Las fuentes van incluidas en el reporte para que funcione sin conexión.

## Estructura de una auditoría

```
audits/<dominio>/
├── BRIEF.md       Contexto del negocio y opciones elegidas; los agentes lo leen primero
├── raw/           Evidencia sin procesar: HTML, reportes de Lighthouse
├── screenshots/   Capturas de escritorio y móvil
├── findings/      Hallazgos en JSON: meta, un archivo por área, top10, benchmark, etc.
└── report/        El micrositio: index.html, assets/ y feature-carga.html (opcional)
```

Solo se publica `report/`. Las demás carpetas se quedan en `main` como respaldo y evidencia.

## Publicar una auditoría

1. Haz commit de la carpeta `audits/<dominio>/` y haz push a `main`.
2. El workflow `Publish reports` (`.github/workflows/publish-reports.yml`) se ejecuta solo:
   - Construye el sitio con `tools/build_site.py`, que reúne todas las carpetas `audits/*/report/` y genera un `index.html` con la lista de auditorías, su dominio y su puntaje general.
   - Sube ese sitio, con push forzado, a la rama `reports`.
3. Spacefast está conectado a la rama `reports` y actualiza https://auditorias-simian.space.fast/ en cada cambio.

Para revisar el sitio en tu equipo antes de publicarlo:

```bash
python3 tools/build_site.py _site
open _site/index.html
```

Si una auditoría fue solo de prueba, **no** la subas: borra la carpeta o déjala sin commit.

## Estructura del repositorio

```
.
├── .claude-plugin/marketplace.json     Registra este repo como marketplace de plugins
├── .github/workflows/                  Publicación automática de reportes
├── audits/                             Auditorías realizadas, una carpeta por dominio
├── tools/build_site.py                 Construye el sitio con todas las auditorías
└── plugins/simian-web-audit/
    ├── .claude-plugin/plugin.json      Nombre y versión del plugin
    ├── CHANGELOG.md                    Historial de cambios
    ├── skills/simian-web-audit/
    │   ├── SKILL.md                    El flujo de trabajo que sigue Claude
    │   └── references/                 Instrucciones de cada agente, síntesis, OpenSEO y plantilla del brief
    ├── scripts/                        Verificación, recolección de evidencia, validación, puntaje y construcción
    │   ├── lib/                        Utilidades compartidas: rutas, imágenes, unidades y validación
    │   └── report/                     Generador del micrositio y sus secciones
    ├── config/                         Rúbrica, puntaje y ajustes (Top N de 5 a 10, tope de créditos)
    ├── schemas/                        Esquemas JSON de cada tipo de hallazgo
    ├── templates/load-page.html        Plantilla de la página de comparación de carga
    ├── assets/                         Fuentes, logo y casos de Simian
    └── tests/                          Pruebas automáticas con datos de ejemplo
```

## Desarrollo del plugin

**Hacer cambios:**

1. Edita los archivos dentro de `plugins/simian-web-audit/`.
2. Sube el número de `version` en `plugins/simian-web-audit/.claude-plugin/plugin.json`.
3. Anota el cambio en `plugins/simian-web-audit/CHANGELOG.md`.
4. En Claude Code, ejecuta `/plugin marketplace update ag-auditorias` para cargar la nueva versión.

**Correr las pruebas:**

```bash
cd plugins/simian-web-audit
python3 -m unittest
```

**Actualizar los casos de Simian:** cuando cambie el portafolio, ejecuta `python3 -I plugins/simian-web-audit/scripts/refresh_simian_cases.py`. Luego etiqueta a mano los casos nuevos en el campo `matches` de `assets/simian/cases.json`.

## Reglas que el plugin siempre respeta

- **No inventa** cifras, competidores, resultados de búsqueda ni respuestas de IA. Lo que no se pudo medir se omite o se marca como `[dato por confirmar]`.
- **No expone** detalles técnicos sensibles, como nombres de usuario o versiones de software, en los textos que ve el cliente.
- Escribe para el cliente en español neutro y profesional, tratándolo de "tú".
- El micrositio **no tiene** botón de contacto y funciona **sin conexión**.
- El Top N tiene como máximo 10 mejoras. Si hay menos de 5, se acepta y **nunca se rellena**.
- Las capturas móviles salen de Lighthouse o de emulación de dispositivo, nunca de una ventana de Chrome angosta.
- Para convertir tamaños se usa MB = KiB / 1024.
