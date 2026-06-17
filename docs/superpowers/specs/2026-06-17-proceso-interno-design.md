# Diseño: Sección "Proceso Interno" para VitalCheck

**Fecha:** 2026-06-17
**Proyecto:** compilador-triaje (VitalCheck) — Trabajo final de Compiladores, USIL
**Rama:** `feature/proceso-interno`

## Contexto

VitalCheck es una app Flask que compila un lenguaje propio (DSL) de triaje
hospitalario. Hoy ya tiene léxico, sintáctico (AST), semántico, generación de
código Python y una UI con pestañas (Resultados, Errores, Modo Técnico, Código .py).

El profesor (feedback en audio + prompt de referencia "Ing. Odin Delgado") pide
que el sistema muestre **el proceso interno completo** siguiendo la secuencia:

```
Imagen/Input → Lexemas → Tokens → Expresiones Regulares → AFND → AFD →
Tablas de Transición → Gramáticas Libres de Contexto → Árboles Sintácticos
```

Y enfatiza: tabla **Token ↔ Lexema**, tabla de **expresiones regulares**, por cada
regex un **AFND**, de cada AFND un **AFD**, de cada AFD una **tabla de transición**;
en sintáctico, mostrar de las **18 categorías de gramática** solo las que aparecen
en el formulario/input, con sus producciones y árboles.

## Principio rector (restricción dura)

**No se modifica nada de lo que ya funciona.** Se conservan intactos:
- El formulario y su lógica (`agregarPaciente`, `cargarArchivo`, etc.).
- Las pestañas superiores **Resultados**, **Errores**, **Código .py**.
- `renderResultados`, `renderErrores`, `renderCodigo` y el flujo de compilación.
- Los módulos `lexer.py`, `parser.py`, `semantic.py`, `codegen.py`, `preprocessor.py`.
- Las claves existentes del dict que devuelve `compilar()`.

Todo lo nuevo se **agrega** en módulos y funciones nuevas. La única estructura
existente que se extiende (no se reescribe) es el contenido de la pestaña
**Modo Técnico**, donde se añaden secciones nuevas debajo de lo actual.

## Decisiones de diseño (acordadas)

1. **Gramáticas presentes**: se determinan de forma **determinista** analizando los
   tokens/AST del input (qué campos/categorías aparecen). Sin llamada a LLM en runtime.
   El prompt del profe es la *especificación de referencia* de qué mostrar, no un
   servicio en vivo.
2. **Visualización de autómatas**: **diagrama Mermaid** (grafo de estados) + **tabla
   de transiciones** al lado. Mermaid.js se carga por **CDN**.
3. **Generación de autómatas**: **curada por token** (el conjunto de tokens del DSL es
   fijo y pequeño). Se definen a mano los AFND/AFD/tablas de cada categoría como datos;
   se seleccionan solo los de los tokens presentes en el input. Sin motor regex genérico.
4. **Ubicación en la UI**: todo el contenido nuevo va **dentro de la pestaña Modo
   Técnico**, en un **único scroll con secciones** (sin sub-tabs).
5. **Header de descripción**: se agrega un encabezado breve arriba del área de trabajo.

## Arquitectura

### Backend — módulos nuevos en `compiler/`

- **`compiler/lexico.py`**
  - `agrupar_tokens_lexemas(tokens)` → para la **tabla Token ↔ Lexemas**: por cada
    categoría de token presente, la lista de lexemas distintos encontrados.
  - `tabla_expresiones_regulares(categorias_presentes)` → filas
    `(token, descripcion, ejemplo_lexema, regex)` (regex curadas, legibles, no la
    regex cruda con `\b`).

- **`compiler/automatas.py`**
  - Catálogo **curado** `AUTOMATAS` con, por categoría de token relevante, la
    definición de AFND y AFD: `estados`, `inicial`, `finales`, `transiciones`
    (lista de `(origen, simbolo, destino)`), y `alfabeto`.
  - Categorías con autómata propio: `NUMERO`, `ID`, `CADENA`, `NIVEL_VAL`,
    `PALABRA_CLAVE` (ej. `PACIENTE`). Los tokens de un solo carácter (`=`,`{`,`}`,`;`)
    se representan solo como tabla trivial (2 estados), sin diagrama.
  - `seleccionar_automatas(categorias_presentes)` → solo los presentes en el input.
  - `a_mermaid(automata)` → string `stateDiagram-v2` para el front.
  - `tabla_transiciones(automata)` → matriz estados × símbolos para render HTML.

- **`compiler/gramatica.py`**
  - `CATEGORIAS_18` — las 18 categorías del prompt del profe, con su descripción.
  - `detectar_categorias(tokens, arbol)` → por cada una de las 18:
    `presencia ∈ {"directa","indirecta","no_aparece"}` + justificación.
  - `PRODUCCIONES` — reglas GLC (BNF) curadas por categoría + la **GLC completa del DSL**.
  - `arbol_a_mermaid(arbol)` → string `graph TD` del AST completo para diagrama.

### Integración en `compiler/__init__.py`

`compilar()` agrega **claves nuevas** al dict de resultado, sin tocar las existentes:

```python
resultado['analisis_lexico']     = { 'token_lexemas': [...], 'regex': [...] }
resultado['analisis_automatas']  = [ { 'token':..., 'afnd': {...}, 'afnd_mermaid':...,
                                       'afnd_tabla':..., 'afd': {...}, 'afd_mermaid':...,
                                       'afd_tabla':... }, ... ]
resultado['analisis_sintactico'] = { 'categorias': [...], 'producciones': [...],
                                      'glc_completa': "...", 'arbol_mermaid': "..." }
```

Solo se calculan si no hubo errores léxicos/sintácticos (igual que el resto del flujo).

### Frontend — `templates/index.html`

- **Header de descripción**: bloque nuevo arriba del `.main` (o dentro del panel de
  resultados, encima de los tabs) con texto estático sobre qué hace VitalCheck y la
  secuencia léxico→sintáctico→semántico→traducción. No se modifica el `<header>` del logo.
- **Modo Técnico (extensión)**: `renderTecnico(data)` se **amplía** para, después del
  bloque actual de Tokens + AST, agregar en el mismo scroll:
  1. **Análisis Léxico**: tabla Token ↔ Lexemas; tabla de Expresiones Regulares.
  2. **Autómatas**: por cada token presente, diagrama Mermaid del **AFND** y del **AFD**
     + sus **tablas de transición**.
  3. **Análisis Sintáctico**: tabla de las **18 categorías** (directa/indirecta/no
     aparece + justificación); producciones GLC de las presentes + GLC completa;
     **árbol sintáctico** completo en Mermaid.
- **Mermaid**: `<script src="…mermaid…">` por CDN; `mermaid.run()` tras inyectar el HTML.
- Funciones de render **nuevas** (`renderLexico`, `renderAutomatas`, `renderSintactico`);
  no se modifican las funciones de las otras pestañas.

## Categorías de gramática para VitalCheck (esperado)

De las 18 del prompt, para el DSL de VitalCheck:

- **Directas (✅):** Números, Identificadores, Asignaciones (`x = 110;`),
  Cadenas balanceadas (`"…"`), Declaraciones (bloque `PACIENTE` / `SIGNOS VITALES`),
  Lista de sentencias (varias asignaciones / varios pacientes).
- **Indirectas (🟡):** Paréntesis/llaves balanceados (`{ }`), Comentarios (si hay `//`).
- **No aparecen (❌):** Expresiones aritméticas, relacionales, lógicas, IF, IF-ELSE,
  WHILE, FOR, Funciones, Parámetros, Llamadas a funciones.

Las producciones y árboles se desarrollan solo para las presentes; las "no aparecen"
se listan en la tabla con su justificación pero sin desarrollo.

## Autómatas curados (definición de referencia)

- **NUMERO** `dígito+ ('.' dígito+)?` — AFD: `S0 -d-> S1(acc)`, `S1 -d-> S1`,
  `S1 -.-> S2`, `S2 -d-> S3(acc)`, `S3 -d-> S3`. AFND equivalente con ε.
- **ID** `letra (letra|dígito|'_')*` — AFD: `S0 -letra/_-> S1(acc)`,
  `S1 -letra/dígito/_-> S1`.
- **CADENA** `'"' [^"]* '"'` — AFD: `S0 -"-> S1`, `S1 -[^"]-> S1`, `S1 -"-> S2(acc)`.
- **NIVEL_VAL** `I|II|III|IV|V` — alternación finita; AFND con 5 ramas, AFD con
  prefijos fusionados.
- **PALABRA_CLAVE** (ej. `PACIENTE`) — cadena literal: AFD lineal de un estado por carácter.

## Flujo de datos

```
input → compilar()
  ├─ (existente) lexer → parser(AST) → semántico → codegen
  └─ (nuevo, si sin errores) lexico + automatas + gramatica
      → claves analisis_lexico / analisis_automatas / analisis_sintactico
  → JSON → front: renderTecnico amplía Modo Técnico con Mermaid + tablas
```

## Manejo de errores

- Si hay errores léxicos/sintácticos, las claves nuevas van vacías (igual que el
  flujo actual corta en errores). El front muestra estado vacío en esas secciones.
- Render del front es defensivo: si una clave nueva falta o viene vacía, se omite la
  sección sin romper Modo Técnico.

## Pruebas (pytest)

- `lexico`: agrupación token↔lexema correcta sobre el ejemplo del DSL.
- `automatas`: `seleccionar_automatas` devuelve solo los tokens presentes;
  `tabla_transiciones` consistente con las transiciones; `a_mermaid` produce string
  `stateDiagram-v2` válido (smoke).
- `gramatica`: `detectar_categorias` clasifica correctamente las categorías
  esperadas (Números/Identificadores/Asignaciones/Cadenas directas; control-flow
  "no_aparece") sobre el ejemplo.
- **No-regresión**: `compilar()` sigue devolviendo idénticas las claves antiguas
  (`tokens`, `arbol`, `tabla_simbolos`, `errores_*`, `codigo_generado`, `exitoso`).

## Fuera de alcance (YAGNI)

- Motor regex genérico (Thompson + subconjuntos) — se usa catálogo curado.
- Llamada a LLM en runtime.
- Reporte PDF de la traducción (queda como posible fase futura; no lo pidió este cambio).
- Traducción a SQL/JSON adicional (el codegen Python actual no se toca).
