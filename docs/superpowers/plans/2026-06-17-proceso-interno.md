# Proceso Interno (Léxico / Autómatas / Gramática) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Agregar a VitalCheck una sección "Proceso Interno" que muestre, de forma determinista y curada, la cadena Token↔Lexema → Expresión Regular → AFND → AFD → Tabla de Transiciones → Gramáticas (18 categorías) → Árbol Sintáctico, todo dentro de la pestaña Modo Técnico, sin tocar lo existente.

**Architecture:** Tres módulos nuevos en `compiler/` (`lexico.py`, `automatas.py`, `gramatica.py`) producen datos puros; `compiler/__init__.py` los integra agregando claves nuevas al dict de `compilar()`; `templates/index.html` agrega un header de descripción y amplía `renderTecnico` para dibujar tablas + diagramas Mermaid (CDN). Autómatas curados por token; gramáticas detectadas desde los tokens/AST.

**Tech Stack:** Python 3.14, Flask 3.1.3, pytest (dev), Mermaid.js 11 (CDN, sin dependencia de build).

## Global Constraints

- Python 3.14; Flask 3.1.3 (no agregar dependencias de producción nuevas — Mermaid va por CDN; pytest es solo dev).
- NO modificar `lexer.py`, `parser.py`, `semantic.py`, `codegen.py`, `preprocessor.py`.
- En `compiler/__init__.py` solo se AGREGAN claves nuevas al dict resultado; las claves existentes (`tokens`, `arbol`, `tabla_simbolos`, `errores_lexicos`, `errores_sintacticos`, `errores_semanticos`, `advertencias`, `codigo_generado`, `exitoso`) quedan idénticas.
- En `templates/index.html` solo se AGREGA (header, script Mermaid, secciones nuevas y funciones de render nuevas); NO se modifican `renderResultados`, `renderErrores`, `renderCodigo`, ni las pestañas Resultados/Errores/Código .py.
- Estilo: PEP 8, type hints en firmas, datos inmutables (no mutar args de entrada), funciones pequeñas.
- Los módulos nuevos operan sobre la lista de tokens en forma de dicts (`{'tipo','valor','linea','columna'}`), igual que `resultado['tokens']`.
- Tests con pytest, ejecutados desde la raíz del repo.

---

### Task 1: Módulo `lexico.py` — tabla Token↔Lexemas y tabla de Expresiones Regulares

**Files:**
- Create: `compiler/lexico.py`
- Create: `tests/test_lexico.py`
- Create: `requirements-dev.txt`

**Interfaces:**
- Consumes: lista de tokens como `list[dict]` con claves `tipo`, `valor`.
- Produces:
  - `agrupar_tokens_lexemas(tokens: list[dict]) -> list[dict]` → `[{'token': str, 'lexemas': list[str]}]` (lexemas distintos, en orden de aparición).
  - `tabla_expresiones_regulares(tipos: set[str]) -> list[dict]` → `[{'token': str, 'descripcion': str, 'regex': str}]` solo para tipos con regex curada.
  - Constante `REGEX_CURADAS: dict[str, tuple[str, str]]` (tipo → (descripcion, regex)).

- [ ] **Step 1: Crear `requirements-dev.txt`**

```text
pytest==8.3.4
```

Instalar: `python -m pip install -r requirements-dev.txt`

- [ ] **Step 2: Escribir el test que falla** — `tests/test_lexico.py`

```python
from compiler.lexico import (
    agrupar_tokens_lexemas,
    tabla_expresiones_regulares,
    REGEX_CURADAS,
)

TOKENS = [
    {'tipo': 'PACIENTE', 'valor': 'PACIENTE', 'linea': 1, 'columna': 1},
    {'tipo': 'ID', 'valor': 'Garcia', 'linea': 1, 'columna': 10},
    {'tipo': 'ID', 'valor': 'frecuencia_cardiaca', 'linea': 2, 'columna': 5},
    {'tipo': 'ID', 'valor': 'frecuencia_cardiaca', 'linea': 3, 'columna': 5},
    {'tipo': 'NUMERO', 'valor': '110', 'linea': 2, 'columna': 25},
    {'tipo': 'CADENA', 'valor': '"Dolor"', 'linea': 4, 'columna': 5},
]


def test_agrupa_por_tipo_sin_duplicados():
    grupos = agrupar_tokens_lexemas(TOKENS)
    por_tipo = {g['token']: g['lexemas'] for g in grupos}
    assert por_tipo['ID'] == ['Garcia', 'frecuencia_cardiaca']  # distintos, en orden
    assert por_tipo['NUMERO'] == ['110']
    assert por_tipo['PACIENTE'] == ['PACIENTE']


def test_no_muta_entrada():
    copia = [dict(t) for t in TOKENS]
    agrupar_tokens_lexemas(TOKENS)
    assert TOKENS == copia


def test_tabla_regex_solo_tipos_presentes_y_curados():
    filas = tabla_expresiones_regulares({'NUMERO', 'ID', 'PUNTO_COMA'})
    tipos = {f['token'] for f in filas}
    assert 'NUMERO' in tipos and 'ID' in tipos
    assert 'PUNTO_COMA' not in tipos  # sin regex curada -> no aparece
    for f in filas:
        assert f['regex'] and f['descripcion']


def test_regex_curadas_tiene_categorias_clave():
    for t in ('NUMERO', 'ID', 'CADENA', 'NIVEL_VAL'):
        assert t in REGEX_CURADAS
```

- [ ] **Step 3: Ejecutar y verificar que falla**

Run: `python -m pytest tests/test_lexico.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'compiler.lexico'`

- [ ] **Step 4: Implementar `compiler/lexico.py`**

```python
"""Análisis léxico para visualización: tabla Token-Lexema y expresiones regulares."""

# tipo de token -> (descripción legible, expresión regular legible)
REGEX_CURADAS: dict[str, tuple[str, str]] = {
    'NUMERO':    ('Número entero o decimal', r'[0-9]+(\.[0-9]+)?'),
    'ID':        ('Identificador',           r'[A-Za-z_][A-Za-z0-9_]*'),
    'CADENA':    ('Cadena entre comillas',   r'"[^"]*"'),
    'NIVEL_VAL': ('Nivel de prioridad (romano)', r'I|II|III|IV|V'),
    'PACIENTE':  ('Palabra clave PACIENTE',  r'PACIENTE'),
    'SIGNOS':    ('Palabra clave SIGNOS',    r'SIGNOS'),
    'VITALES':   ('Palabra clave VITALES',   r'VITALES'),
    'SINTOMA':   ('Palabra clave SINTOMA',   r'SINTOMA'),
    'PRIORIDAD': ('Palabra clave PRIORIDAD', r'PRIORIDAD'),
    'NIVEL':     ('Palabra clave NIVEL',     r'NIVEL'),
    'FIN':       ('Palabra clave FIN',       r'FIN'),
    'ASIGNAR':   ('Operador de asignación',  r'='),
    'LLAVE_AB':  ('Llave de apertura',       r'\{'),
    'LLAVE_CI':  ('Llave de cierre',         r'\}'),
    'PUNTO_COMA': ('Fin de sentencia',       r';'),
    'DOS_PUNTOS': ('Dos puntos',             r':'),
    'COMA':      ('Coma',                    r','),
}


def agrupar_tokens_lexemas(tokens: list[dict]) -> list[dict]:
    """Agrupa los lexemas distintos por categoría de token, en orden de aparición."""
    grupos: dict[str, list[str]] = {}
    for token in tokens:
        tipo = token['tipo']
        valor = token['valor']
        lexemas = grupos.setdefault(tipo, [])
        if valor not in lexemas:
            lexemas.append(valor)
    return [{'token': tipo, 'lexemas': list(lexemas)} for tipo, lexemas in grupos.items()]


def tabla_expresiones_regulares(tipos: set[str]) -> list[dict]:
    """Filas (token, descripción, regex) solo para los tipos presentes con regex curada."""
    filas = []
    for tipo, (descripcion, regex) in REGEX_CURADAS.items():
        if tipo in tipos:
            filas.append({'token': tipo, 'descripcion': descripcion, 'regex': regex})
    return filas
```

- [ ] **Step 5: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_lexico.py -v`
Expected: PASS (4 tests)

- [ ] **Step 6: Commit**

```bash
git add requirements-dev.txt compiler/lexico.py tests/test_lexico.py
git commit -m "feat(lexico): tabla token-lexema y expresiones regulares"
```

---

### Task 2: Módulo `automatas.py` — AFND/AFD curados, tablas de transición y Mermaid

**Files:**
- Create: `compiler/automatas.py`
- Create: `tests/test_automatas.py`

**Interfaces:**
- Consumes: `tipos_presentes: set[str]`, `lexemas_por_tipo: dict[str, list[str]]`.
- Produces:
  - `seleccionar_automatas(tipos_presentes: set[str], lexemas_por_tipo: dict[str, list[str]]) -> list[dict]`
    → cada item: `{'token', 'descripcion', 'regex', 'afnd', 'afd', 'afnd_mermaid', 'afd_mermaid', 'afnd_tabla', 'afd_tabla'}`.
  - `a_mermaid(automata: dict) -> str` (stateDiagram-v2).
  - `tabla_transiciones(automata: dict) -> dict` → `{'simbolos': list[str], 'filas': list[dict]}`.
  - `automata_literal(palabra: str) -> dict` (cadena literal → autómata lineal).
  - Un `automata` es `{'estados': list[str], 'inicial': str, 'finales': list[str], 'alfabeto': list[str], 'transiciones': list[tuple[str,str,str]]}`.

- [ ] **Step 1: Escribir el test que falla** — `tests/test_automatas.py`

```python
from compiler.automatas import (
    seleccionar_automatas,
    a_mermaid,
    tabla_transiciones,
    automata_literal,
)


def test_selecciona_solo_tipos_presentes_con_automata():
    items = seleccionar_automatas(
        {'NUMERO', 'ID', 'PUNTO_COMA'},
        {'NUMERO': ['110'], 'ID': ['Garcia'], 'PUNTO_COMA': [';']},
    )
    tokens = {i['token'] for i in items}
    assert 'NUMERO' in tokens and 'ID' in tokens
    assert 'PUNTO_COMA' not in tokens  # puntuación -> sin diagrama


def test_item_tiene_afnd_afd_mermaid_y_tablas():
    item = seleccionar_automatas({'NUMERO'}, {'NUMERO': ['110']})[0]
    assert item['afnd_mermaid'].startswith('stateDiagram-v2')
    assert item['afd_mermaid'].startswith('stateDiagram-v2')
    assert item['afnd_tabla']['filas']
    assert item['afd_tabla']['filas']


def test_keyword_genera_automata_literal():
    items = seleccionar_automatas({'PACIENTE'}, {'PACIENTE': ['PACIENTE']})
    assert len(items) == 1
    afd = items[0]['afd']
    # un estado inicial + un estado por carácter de "PACIENTE"
    assert len(afd['estados']) == len('PACIENTE') + 1
    assert len(afd['finales']) == 1


def test_automata_literal_acepta_cadena():
    a = automata_literal('FIN')
    assert a['inicial'] == 'q0'
    assert a['finales'] == ['q3']
    assert ('q0', 'F', 'q1') in a['transiciones']
    assert ('q2', 'N', 'q3') in a['transiciones']


def test_tabla_transiciones_estructura():
    a = automata_literal('IF')
    tabla = tabla_transiciones(a)
    assert tabla['simbolos'] == ['I', 'F']
    assert len(tabla['filas']) == len(a['estados'])
    inicial = [f for f in tabla['filas'] if f['inicial']]
    assert len(inicial) == 1


def test_a_mermaid_incluye_inicial_y_final():
    a = automata_literal('F')
    diagrama = a_mermaid(a)
    assert '[*] --> q0' in diagrama
    assert 'q1 --> [*]' in diagrama  # estado final
    assert 'q0 --> q1: F' in diagrama
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python -m pytest tests/test_automatas.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'compiler.automatas'`

- [ ] **Step 3: Implementar `compiler/automatas.py`**

```python
"""Autómatas finitos (AFND/AFD) curados por categoría de token + utilidades de render."""

from compiler.lexico import REGEX_CURADAS

# Autómatas curados para los tokens con estructura regex.
# Símbolos: 'd' = dígito, 'L' = letra/_, 'D' = dígito (en ID), 'c' = carácter != "
_REGEX_AUTOMATAS: dict[str, dict] = {
    'NUMERO': {
        'afnd': {
            'estados': ['A0', 'A1', 'A2', 'A3', 'A4'],
            'inicial': 'A0',
            'finales': ['A4'],
            'alfabeto': ['d', '.', 'ε'],
            'transiciones': [
                ('A0', 'd', 'A1'), ('A1', 'd', 'A1'), ('A1', 'ε', 'A4'),
                ('A1', '.', 'A2'), ('A2', 'd', 'A3'), ('A3', 'd', 'A3'),
                ('A3', 'ε', 'A4'),
            ],
        },
        'afd': {
            'estados': ['S0', 'S1', 'S2', 'S3'],
            'inicial': 'S0',
            'finales': ['S1', 'S3'],
            'alfabeto': ['d', '.'],
            'transiciones': [
                ('S0', 'd', 'S1'), ('S1', 'd', 'S1'), ('S1', '.', 'S2'),
                ('S2', 'd', 'S3'), ('S3', 'd', 'S3'),
            ],
        },
    },
    'ID': {
        'afnd': {
            'estados': ['S0', 'S1'],
            'inicial': 'S0',
            'finales': ['S1'],
            'alfabeto': ['L', 'D'],
            'transiciones': [('S0', 'L', 'S1'), ('S1', 'L', 'S1'), ('S1', 'D', 'S1')],
        },
        'afd': {
            'estados': ['S0', 'S1'],
            'inicial': 'S0',
            'finales': ['S1'],
            'alfabeto': ['L', 'D'],
            'transiciones': [('S0', 'L', 'S1'), ('S1', 'L', 'S1'), ('S1', 'D', 'S1')],
        },
    },
    'CADENA': {
        'afnd': {
            'estados': ['S0', 'S1', 'S2'],
            'inicial': 'S0',
            'finales': ['S2'],
            'alfabeto': ['"', 'c'],
            'transiciones': [('S0', '"', 'S1'), ('S1', 'c', 'S1'), ('S1', '"', 'S2')],
        },
        'afd': {
            'estados': ['S0', 'S1', 'S2'],
            'inicial': 'S0',
            'finales': ['S2'],
            'alfabeto': ['"', 'c'],
            'transiciones': [('S0', '"', 'S1'), ('S1', 'c', 'S1'), ('S1', '"', 'S2')],
        },
    },
    'NIVEL_VAL': {
        'afnd': {
            'estados': ['S0', 'S1', 'S2', 'S3', 'S4', 'S5'],
            'inicial': 'S0',
            'finales': ['S1', 'S2', 'S3', 'S4', 'S5'],
            'alfabeto': ['I', 'V'],
            'transiciones': [
                ('S0', 'I', 'S1'), ('S1', 'I', 'S2'), ('S2', 'I', 'S3'),
                ('S1', 'V', 'S4'), ('S0', 'V', 'S5'),
            ],
        },
        'afd': {
            'estados': ['S0', 'S1', 'S2', 'S3', 'S4', 'S5'],
            'inicial': 'S0',
            'finales': ['S1', 'S2', 'S3', 'S4', 'S5'],
            'alfabeto': ['I', 'V'],
            'transiciones': [
                ('S0', 'I', 'S1'), ('S1', 'I', 'S2'), ('S2', 'I', 'S3'),
                ('S1', 'V', 'S4'), ('S0', 'V', 'S5'),
            ],
        },
    },
}

# Palabras clave: su autómata se genera como cadena literal.
_KEYWORDS = {'PACIENTE', 'SIGNOS', 'VITALES', 'SINTOMA', 'PRIORIDAD', 'NIVEL', 'FIN'}


def automata_literal(palabra: str) -> dict:
    """Autómata lineal que reconoce exactamente la cadena `palabra` (determinista)."""
    estados = [f'q{i}' for i in range(len(palabra) + 1)]
    transiciones = [
        (f'q{i}', palabra[i], f'q{i + 1}') for i in range(len(palabra))
    ]
    alfabeto: list[str] = []
    for ch in palabra:
        if ch not in alfabeto:
            alfabeto.append(ch)
    return {
        'estados': estados,
        'inicial': 'q0',
        'finales': [f'q{len(palabra)}'],
        'alfabeto': alfabeto,
        'transiciones': transiciones,
    }


def tabla_transiciones(automata: dict) -> dict:
    """Matriz estados x símbolos a partir de las transiciones del autómata."""
    simbolos = list(automata['alfabeto'])
    filas = []
    for estado in automata['estados']:
        destinos: dict[str, list[str]] = {s: [] for s in simbolos}
        for origen, simbolo, destino in automata['transiciones']:
            if origen == estado and simbolo in destinos:
                destinos[simbolo].append(destino)
        filas.append({
            'estado': estado,
            'inicial': estado == automata['inicial'],
            'final': estado in automata['finales'],
            'destinos': destinos,
        })
    return {'simbolos': simbolos, 'filas': filas}


def a_mermaid(automata: dict) -> str:
    """Convierte el autómata a un diagrama Mermaid stateDiagram-v2."""
    lineas = ['stateDiagram-v2', f'  [*] --> {automata["inicial"]}']
    for origen, simbolo, destino in automata['transiciones']:
        lineas.append(f'  {origen} --> {destino}: {simbolo}')
    for final in automata['finales']:
        lineas.append(f'  {final} --> [*]')
    return '\n'.join(lineas)


def _automata_para(tipo: str, lexema: str) -> dict | None:
    if tipo in _REGEX_AUTOMATAS:
        return _REGEX_AUTOMATAS[tipo]
    if tipo in _KEYWORDS:
        a = automata_literal(lexema)
        return {'afnd': a, 'afd': a}
    return None


def seleccionar_automatas(
    tipos_presentes: set[str],
    lexemas_por_tipo: dict[str, list[str]],
) -> list[dict]:
    """Construye los autómatas (AFND/AFD + mermaid + tablas) de los tokens presentes."""
    items = []
    # orden estable: primero los regex curados, luego keywords
    orden = list(_REGEX_AUTOMATAS.keys()) + sorted(_KEYWORDS)
    for tipo in orden:
        if tipo not in tipos_presentes:
            continue
        lexema = (lexemas_por_tipo.get(tipo) or [tipo])[0]
        par = _automata_para(tipo, lexema)
        if par is None:
            continue
        afnd, afd = par['afnd'], par['afd']
        descripcion, regex = REGEX_CURADAS.get(tipo, (f'Palabra clave {tipo}', tipo))
        items.append({
            'token': tipo,
            'descripcion': descripcion,
            'regex': regex,
            'afnd': afnd,
            'afd': afd,
            'afnd_mermaid': a_mermaid(afnd),
            'afd_mermaid': a_mermaid(afd),
            'afnd_tabla': tabla_transiciones(afnd),
            'afd_tabla': tabla_transiciones(afd),
        })
    return items
```

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_automatas.py -v`
Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
git add compiler/automatas.py tests/test_automatas.py
git commit -m "feat(automatas): AFND/AFD curados, tablas de transicion y Mermaid"
```

---

### Task 3: Módulo `gramatica.py` — 18 categorías, detección, producciones y árbol Mermaid

**Files:**
- Create: `compiler/gramatica.py`
- Create: `tests/test_gramatica.py`

**Interfaces:**
- Consumes: `tokens: list[dict]`, `arbol: dict | None` (AST con `{'tipo','valor','hijos'}`).
- Produces:
  - `CATEGORIAS_18: list[dict]` (`{'id','nombre'}`, 18 elementos).
  - `detectar_categorias(tokens: list[dict], arbol: dict | None) -> list[dict]`
    → `[{'id','nombre','presencia','justificacion'}]` con `presencia ∈ {'directa','indirecta','no_aparece'}`.
  - `producciones_presentes(categorias: list[dict]) -> list[dict]` → `[{'id','nombre','reglas': list[str]}]` solo para las no `no_aparece` que tengan producciones.
  - `GLC_COMPLETA: str`.
  - `arbol_a_mermaid(arbol: dict | None) -> str` (graph TD).

- [ ] **Step 1: Escribir el test que falla** — `tests/test_gramatica.py`

```python
from compiler.gramatica import (
    CATEGORIAS_18,
    detectar_categorias,
    producciones_presentes,
    arbol_a_mermaid,
    GLC_COMPLETA,
)

TOKENS = [
    {'tipo': 'PACIENTE', 'valor': 'PACIENTE'},
    {'tipo': 'ID', 'valor': 'Garcia'},
    {'tipo': 'LLAVE_AB', 'valor': '{'},
    {'tipo': 'ID', 'valor': 'frecuencia_cardiaca'},
    {'tipo': 'ASIGNAR', 'valor': '='},
    {'tipo': 'NUMERO', 'valor': '110'},
    {'tipo': 'PUNTO_COMA', 'valor': ';'},
    {'tipo': 'SINTOMA', 'valor': 'SINTOMA'},
    {'tipo': 'CADENA', 'valor': '"Dolor"'},
    {'tipo': 'LLAVE_CI', 'valor': '}'},
]
ARBOL = {'tipo': 'PROGRAMA', 'valor': None, 'hijos': [
    {'tipo': 'PACIENTE', 'valor': 'Garcia', 'hijos': [
        {'tipo': 'SINTOMA', 'valor': '"Dolor"', 'hijos': []},
    ]},
]}


def test_hay_18_categorias():
    assert len(CATEGORIAS_18) == 18


def test_detecta_directas_e_indirectas():
    res = {c['id']: c['presencia'] for c in detectar_categorias(TOKENS, ARBOL)}
    assert res['numeros'] == 'directa'
    assert res['identificadores'] == 'directa'
    assert res['asignaciones'] == 'directa'
    assert res['cadenas_balanceadas'] == 'directa'
    assert res['declaraciones'] == 'directa'
    assert res['lista_sentencias'] == 'directa'
    assert res['parentesis_balanceados'] == 'indirecta'  # usa llaves


def test_control_de_flujo_no_aparece():
    res = {c['id']: c['presencia'] for c in detectar_categorias(TOKENS, ARBOL)}
    for cid in ('if', 'if_else', 'while', 'for', 'funciones', 'expr_aritmeticas'):
        assert res[cid] == 'no_aparece'


def test_cada_categoria_tiene_justificacion():
    for c in detectar_categorias(TOKENS, ARBOL):
        assert c['justificacion']


def test_producciones_solo_de_presentes():
    cats = detectar_categorias(TOKENS, ARBOL)
    prods = producciones_presentes(cats)
    ids = {p['id'] for p in prods}
    assert 'numeros' in ids
    assert 'if' not in ids
    for p in prods:
        assert p['reglas']


def test_arbol_a_mermaid_graph_td():
    diagrama = arbol_a_mermaid(ARBOL)
    assert diagrama.startswith('graph TD')
    assert 'PROGRAMA' in diagrama
    assert '-->' in diagrama


def test_arbol_a_mermaid_none():
    assert arbol_a_mermaid(None) == ''


def test_glc_completa_no_vacia():
    assert GLC_COMPLETA.strip()
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python -m pytest tests/test_gramatica.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'compiler.gramatica'`

- [ ] **Step 3: Implementar `compiler/gramatica.py`**

```python
"""Análisis sintáctico para visualización: las 18 categorías del prompt de referencia,
detección de cuáles aparecen en el input, producciones GLC y árbol en Mermaid."""

CATEGORIAS_18: list[dict] = [
    {'id': 'numeros', 'nombre': 'Números'},
    {'id': 'identificadores', 'nombre': 'Identificadores'},
    {'id': 'expr_aritmeticas', 'nombre': 'Expresiones aritméticas'},
    {'id': 'expr_relacionales', 'nombre': 'Expresiones relacionales'},
    {'id': 'expr_logicas', 'nombre': 'Expresiones lógicas'},
    {'id': 'asignaciones', 'nombre': 'Asignaciones'},
    {'id': 'if', 'nombre': 'IF'},
    {'id': 'if_else', 'nombre': 'IF-ELSE'},
    {'id': 'while', 'nombre': 'WHILE'},
    {'id': 'for', 'nombre': 'FOR'},
    {'id': 'lista_sentencias', 'nombre': 'Lista de sentencias'},
    {'id': 'declaraciones', 'nombre': 'Declaraciones'},
    {'id': 'funciones', 'nombre': 'Funciones'},
    {'id': 'parametros', 'nombre': 'Parámetros'},
    {'id': 'llamadas_funciones', 'nombre': 'Llamadas a funciones'},
    {'id': 'cadenas_balanceadas', 'nombre': 'Cadenas balanceadas'},
    {'id': 'parentesis_balanceados', 'nombre': 'Paréntesis / llaves balanceados'},
    {'id': 'comentarios', 'nombre': 'Comentarios'},
]

# Producciones GLC (BNF) por categoría, solo las aplicables al DSL de VitalCheck.
_PRODUCCIONES: dict[str, list[str]] = {
    'numeros': ['<numero> ::= <digito>+ ( "." <digito>+ )?',
                '<digito> ::= "0" | "1" | ... | "9"'],
    'identificadores': ['<id> ::= <letra> ( <letra> | <digito> | "_" )*'],
    'asignaciones': ['<asignacion> ::= <id> "=" <valor> ";"',
                     '<valor> ::= <numero> | <cadena> | <nivel>'],
    'cadenas_balanceadas': ['<cadena> ::= "\\"" <caracter>* "\\""'],
    'declaraciones': ['<paciente> ::= "PACIENTE" <id> "{" <cuerpo> "}"',
                      '<signos> ::= "SIGNOS" "VITALES" "{" <asignacion>* "}"',
                      '<sintoma> ::= "SINTOMA" "=" <cadena> ";"',
                      '<prioridad> ::= "PRIORIDAD" "=" "NIVEL" <nivel> ";"'],
    'lista_sentencias': ['<programa> ::= <paciente>+',
                         '<cuerpo> ::= ( <signos> | <sintoma> | <prioridad> )*'],
    'parentesis_balanceados': ['<bloque> ::= "{" <contenido> "}"'],
    'comentarios': ['<comentario> ::= "//" <caracter>*'],
}

GLC_COMPLETA = """G = (N, T, P, S)
S = <programa>

<programa>   ::= <paciente>+
<paciente>   ::= "PACIENTE" <id> "{" <cuerpo> "}"
<cuerpo>     ::= ( <signos> | <sintoma> | <prioridad> )*
<signos>     ::= "SIGNOS" "VITALES" "{" <asignacion>* "}"
<asignacion> ::= <id> "=" <numero> ";"
<sintoma>    ::= "SINTOMA" "=" <cadena> ";"
<prioridad>  ::= "PRIORIDAD" "=" "NIVEL" <nivel> ";"
<nivel>      ::= "I" | "II" | "III" | "IV" | "V"
<numero>     ::= <digito>+ ( "." <digito>+ )?
<id>         ::= <letra> ( <letra> | <digito> | "_" )*
<cadena>     ::= "\\"" <caracter>* "\\""
"""


def _detectar(cid: str, tipos: set[str]) -> tuple[str, str]:
    """Devuelve (presencia, justificacion) para una categoría dado el conjunto de tipos."""
    if cid == 'numeros':
        if 'NUMERO' in tipos:
            return 'directa', 'Aparecen literales numéricos (signos vitales).'
        return 'no_aparece', 'No hay literales numéricos.'
    if cid == 'identificadores':
        if 'ID' in tipos:
            return 'directa', 'Nombres de paciente y de signos vitales.'
        return 'no_aparece', 'No hay identificadores.'
    if cid == 'asignaciones':
        if 'ASIGNAR' in tipos:
            return 'directa', 'Asignaciones del tipo signo = valor.'
        return 'no_aparece', 'No hay operador de asignación.'
    if cid == 'cadenas_balanceadas':
        if 'CADENA' in tipos:
            return 'directa', 'El síntoma es una cadena entre comillas.'
        return 'no_aparece', 'No hay cadenas.'
    if cid == 'declaraciones':
        if 'PACIENTE' in tipos or 'SIGNOS' in tipos:
            return 'directa', 'Bloques PACIENTE y SIGNOS VITALES.'
        return 'no_aparece', 'No hay declaraciones de bloque.'
    if cid == 'lista_sentencias':
        if 'PUNTO_COMA' in tipos:
            return 'directa', 'Secuencia de sentencias terminadas en ";".'
        return 'no_aparece', 'No hay secuencia de sentencias.'
    if cid == 'parentesis_balanceados':
        if 'LLAVE_AB' in tipos:
            return 'indirecta', 'Usa llaves balanceadas { } en lugar de paréntesis.'
        return 'no_aparece', 'No hay agrupadores balanceados.'
    if cid == 'comentarios':
        return 'no_aparece', 'El lexer descarta comentarios; no quedan tokens.'
    # Categorías de control de flujo / expresiones / funciones: no existen en el DSL.
    justificaciones = {
        'expr_aritmeticas': 'El DSL no tiene operadores aritméticos (+, -, *, /).',
        'expr_relacionales': 'No hay operadores relacionales en la sintaxis.',
        'expr_logicas': 'No hay operadores lógicos (AND/OR/NOT).',
        'if': 'El DSL no tiene condicionales.',
        'if_else': 'El DSL no tiene condicionales con alternativa.',
        'while': 'El DSL no tiene bucles.',
        'for': 'El DSL no tiene bucles for.',
        'funciones': 'El DSL no declara funciones.',
        'parametros': 'No hay listas de parámetros.',
        'llamadas_funciones': 'No hay llamadas a funciones en el lenguaje fuente.',
    }
    return 'no_aparece', justificaciones.get(cid, 'No aparece en el input.')


def detectar_categorias(tokens: list[dict], arbol: dict | None) -> list[dict]:
    """Clasifica cada una de las 18 categorías como directa / indirecta / no_aparece."""
    tipos = {t['tipo'] for t in tokens}
    resultado = []
    for categoria in CATEGORIAS_18:
        presencia, justificacion = _detectar(categoria['id'], tipos)
        resultado.append({
            'id': categoria['id'],
            'nombre': categoria['nombre'],
            'presencia': presencia,
            'justificacion': justificacion,
        })
    return resultado


def producciones_presentes(categorias: list[dict]) -> list[dict]:
    """Producciones GLC de las categorías presentes (directa/indirecta) que las tengan."""
    salida = []
    for categoria in categorias:
        if categoria['presencia'] == 'no_aparece':
            continue
        reglas = _PRODUCCIONES.get(categoria['id'])
        if reglas:
            salida.append({'id': categoria['id'], 'nombre': categoria['nombre'],
                           'reglas': list(reglas)})
    return salida


def arbol_a_mermaid(arbol: dict | None) -> str:
    """Convierte el AST a un diagrama Mermaid graph TD con ids únicos por nodo."""
    if not arbol:
        return ''
    lineas = ['graph TD']
    contador = [0]

    def visitar(nodo: dict, padre_id: str | None) -> None:
        nid = f'n{contador[0]}'
        contador[0] += 1
        valor = nodo.get('valor')
        etiqueta = nodo['tipo'] + (f": {valor}" if valor else '')
        etiqueta = etiqueta.replace('"', "'")
        lineas.append(f'  {nid}["{etiqueta}"]')
        if padre_id is not None:
            lineas.append(f'  {padre_id} --> {nid}')
        for hijo in nodo.get('hijos', []):
            visitar(hijo, nid)

    visitar(arbol, None)
    return '\n'.join(lineas)
```

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_gramatica.py -v`
Expected: PASS (8 tests)

- [ ] **Step 5: Commit**

```bash
git add compiler/gramatica.py tests/test_gramatica.py
git commit -m "feat(gramatica): 18 categorias, deteccion, producciones y arbol Mermaid"
```

---

### Task 4: Integrar en `compilar()` y verificar no-regresión

**Files:**
- Modify: `compiler/__init__.py`
- Create: `tests/test_integracion.py`

**Interfaces:**
- Consumes: `agrupar_tokens_lexemas`, `tabla_expresiones_regulares` (Task 1); `seleccionar_automatas` (Task 2); `detectar_categorias`, `producciones_presentes`, `GLC_COMPLETA`, `arbol_a_mermaid` (Task 3).
- Produces: `compilar(codigo)` con claves nuevas `analisis_lexico`, `analisis_automatas`, `analisis_sintactico`; claves antiguas intactas.

- [ ] **Step 1: Escribir el test que falla** — `tests/test_integracion.py`

```python
from compiler import compilar

CODIGO_OK = """PACIENTE Garcia {
    SIGNOS VITALES {
        frecuencia_cardiaca = 110;
        temperatura = 38.5;
    }
    SINTOMA = "Dolor toracico";
    PRIORIDAD = NIVEL II;
}"""

CLAVES_ANTIGUAS = {
    'tokens', 'arbol', 'tabla_simbolos', 'errores_lexicos',
    'errores_sintacticos', 'errores_semanticos', 'advertencias',
    'codigo_generado', 'exitoso',
}


def test_claves_antiguas_siguen_presentes():
    r = compilar(CODIGO_OK)
    assert CLAVES_ANTIGUAS.issubset(set(r.keys()))
    assert r['exitoso'] is True
    assert r['codigo_generado']  # codegen intacto


def test_agrega_claves_nuevas():
    r = compilar(CODIGO_OK)
    assert 'analisis_lexico' in r
    assert 'analisis_automatas' in r
    assert 'analisis_sintactico' in r


def test_lexico_y_automatas_poblados():
    r = compilar(CODIGO_OK)
    assert r['analisis_lexico']['token_lexemas']
    assert r['analisis_lexico']['regex']
    tokens_con_automata = {a['token'] for a in r['analisis_automatas']}
    assert {'NUMERO', 'ID', 'CADENA', 'NIVEL_VAL'} <= tokens_con_automata


def test_sintactico_poblado():
    r = compilar(CODIGO_OK)
    sint = r['analisis_sintactico']
    assert len(sint['categorias']) == 18
    assert sint['producciones']
    assert sint['arbol_mermaid'].startswith('graph TD')
    assert sint['glc_completa']


def test_claves_nuevas_vacias_en_error_lexico():
    r = compilar('@@@ caracter invalido')
    assert r['errores_lexicos']
    assert r['analisis_automatas'] == []
    assert r['analisis_lexico'] == {'token_lexemas': [], 'regex': []}
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python -m pytest tests/test_integracion.py -v`
Expected: FAIL (`KeyError: 'analisis_lexico'` o assert sobre claves nuevas)

- [ ] **Step 3: Modificar `compiler/__init__.py`**

Agregar imports al inicio (después de los imports existentes):

```python
from .lexico import agrupar_tokens_lexemas, tabla_expresiones_regulares
from .automatas import seleccionar_automatas
from .gramatica import (
    detectar_categorias,
    producciones_presentes,
    GLC_COMPLETA,
    arbol_a_mermaid,
)
```

Agregar las claves nuevas al dict `resultado` inicial (junto a las existentes), con valores por defecto vacíos:

```python
    resultado = {
        'tokens': [],
        'arbol': None,
        'tabla_simbolos': {},
        'errores_lexicos': [],
        'errores_sintacticos': [],
        'errores_semanticos': [],
        'advertencias': [],
        'codigo_generado': '',
        'exitoso': False,
        'analisis_lexico': {'token_lexemas': [], 'regex': []},
        'analisis_automatas': [],
        'analisis_sintactico': {
            'categorias': [], 'producciones': [],
            'glc_completa': '', 'arbol_mermaid': '',
        },
    }
```

Justo **antes** de la línea final `return resultado`, y **después** de calcular `tabla_ordenada` / `codigo_generado`, agregar el cálculo de las secciones nuevas (se ejecuta solo si llegamos aquí, es decir sin errores léxicos ni sintácticos porque esos hacen `return` antes):

```python
    tokens_dict = resultado['tokens']
    tipos_presentes = {t['tipo'] for t in tokens_dict}
    grupos = agrupar_tokens_lexemas(tokens_dict)
    lexemas_por_tipo = {g['token']: g['lexemas'] for g in grupos}

    resultado['analisis_lexico'] = {
        'token_lexemas': grupos,
        'regex': tabla_expresiones_regulares(tipos_presentes),
    }
    resultado['analisis_automatas'] = seleccionar_automatas(tipos_presentes, lexemas_por_tipo)

    categorias = detectar_categorias(tokens_dict, resultado['arbol'])
    resultado['analisis_sintactico'] = {
        'categorias': categorias,
        'producciones': producciones_presentes(categorias),
        'glc_completa': GLC_COMPLETA,
        'arbol_mermaid': arbol_a_mermaid(resultado['arbol']),
    }

    return resultado
```

Nota: las dos primeras returns tempranas (por `errores_lex` y `errores_sin`) dejan las claves nuevas con su valor por defecto vacío — justo lo que pide el test de error.

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_integracion.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Ejecutar toda la suite (no-regresión global)**

Run: `python -m pytest -v`
Expected: PASS (todos los tests de las Tasks 1-4)

- [ ] **Step 6: Commit**

```bash
git add compiler/__init__.py tests/test_integracion.py
git commit -m "feat: integrar analisis lexico/automatas/sintactico en compilar()"
```

---

### Task 5: Frontend — header de descripción + Mermaid + ampliar Modo Técnico

**Files:**
- Modify: `templates/index.html` (solo agregados: header, script Mermaid, render nuevos, llamada desde `renderTecnico`)
- Create: `tests/test_app.py`

**Interfaces:**
- Consumes: claves `analisis_lexico`, `analisis_automatas`, `analisis_sintactico` del JSON de `/compilar` (Task 4).
- Produces: UI en pestaña Modo Técnico con tablas + diagramas Mermaid. Sin firmas nuevas para otras tareas.

- [ ] **Step 1: Escribir el test de endpoint que falla** — `tests/test_app.py`

```python
import pytest
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    return flask_app.test_client()


def test_index_tiene_header_descripcion_y_mermaid(client):
    html = client.get('/').get_data(as_text=True)
    assert 'mermaid' in html.lower()           # script Mermaid por CDN
    assert 'Proceso Interno' in html or 'proceso interno' in html.lower()


def test_compilar_devuelve_secciones_nuevas(client):
    codigo = ('PACIENTE Garcia { SIGNOS VITALES { frecuencia_cardiaca = 110; } '
              'SINTOMA = "Dolor"; PRIORIDAD = NIVEL II; }')
    resp = client.post('/compilar', json={'codigo': codigo})
    data = resp.get_json()
    assert 'analisis_automatas' in data
    assert data['analisis_sintactico']['categorias']
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python -m pytest tests/test_app.py -v`
Expected: FAIL en `test_index_tiene_header_descripcion_y_mermaid` (no existe el header/script aún)

- [ ] **Step 3: Agregar el script de Mermaid (CDN) en el `<head>`**

En `templates/index.html`, justo antes de `</head>`, agregar:

```html
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
        mermaid.initialize({ startOnLoad: false, theme: 'dark', securityLevel: 'loose' });
        window.__mermaid = mermaid;
    </script>
```

- [ ] **Step 4: Agregar el header de descripción**

Justo después de `<body>` y antes de `<header>`, NO; en su lugar, inmediatamente después del `<header>...</header>` existente y antes de `<div class="main">`, agregar:

```html
<section style="padding:.8rem 2rem;border-bottom:1px solid var(--border);background:rgba(0,212,255,.04)">
    <strong style="color:var(--accent)">VitalCheck — Compilador de Triaje Hospitalario.</strong>
    <span style="color:var(--text-dim);font-size:.82rem">
        Procesa un lenguaje propio de triaje ejecutando <em>análisis léxico → sintáctico → semántico</em>
        y traduce a código Python. El <strong>Proceso Interno</strong> (pestaña Modo Técnico) muestra la
        cadena Lexemas → Tokens → Expresiones Regulares → AFND → AFD → Tablas de Transición →
        Gramáticas → Árbol Sintáctico.
    </span>
</section>
```

- [ ] **Step 5: Ampliar `renderTecnico` para invocar los renders nuevos**

Localizar la función `renderTecnico(data)` (su última línea es `c.innerHTML=h;`). Reemplazar **solo esa última línea** por el bloque siguiente (mantiene todo lo anterior de la función igual):

```javascript
    h += renderLexicoHTML(data.analisis_lexico||{});
    h += renderAutomatasHTML(data.analisis_automatas||[]);
    h += renderSintacticoHTML(data.analisis_sintactico||{});
    c.innerHTML=h;
    if(window.__mermaid){
        const nodos=c.querySelectorAll('.mermaid');
        if(nodos.length) window.__mermaid.run({nodes:nodos});
    }
```

- [ ] **Step 6: Agregar las funciones de render nuevas**

Justo antes de `function showTab(name){` en el `<script>`, agregar:

```javascript
function renderTablaTransiciones(tabla){
    let h='<table style="border-collapse:collapse;font-size:.7rem;margin:.4rem 0">';
    h+='<tr><th style="border:1px solid var(--border);padding:.3rem .5rem">Estado</th>';
    tabla.simbolos.forEach(s=>{h+=`<th style="border:1px solid var(--border);padding:.3rem .5rem">${esc(s)}</th>`;});
    h+='</tr>';
    tabla.filas.forEach(f=>{
        const marca=(f.inicial?'→':'')+(f.final?'*':'');
        h+=`<tr><td style="border:1px solid var(--border);padding:.3rem .5rem">${marca} ${esc(f.estado)}</td>`;
        tabla.simbolos.forEach(s=>{
            const d=(f.destinos[s]||[]).join(', ');
            h+=`<td style="border:1px solid var(--border);padding:.3rem .5rem">${esc(d)||'—'}</td>`;
        });
        h+='</tr>';
    });
    return h+'</table>';
}

function renderLexicoHTML(lex){
    const grupos=lex.token_lexemas||[];
    const regex=lex.regex||[];
    if(!grupos.length) return '';
    let h='<div class="section-title" style="margin-top:1.5rem">Análisis Léxico · Tokens y Lexemas</div>';
    h+='<table style="border-collapse:collapse;font-size:.72rem;width:100%"><tr>'
      +'<th style="border:1px solid var(--border);padding:.4rem;text-align:left">Token (agrupador)</th>'
      +'<th style="border:1px solid var(--border);padding:.4rem;text-align:left">Lexemas</th></tr>';
    grupos.forEach(g=>{
        h+=`<tr><td style="border:1px solid var(--border);padding:.4rem"><strong>${esc(g.token)}</strong></td>`
          +`<td style="border:1px solid var(--border);padding:.4rem">${g.lexemas.map(esc).join(', ')}</td></tr>`;
    });
    h+='</table>';
    if(regex.length){
        h+='<div class="section-title" style="margin-top:1rem">Expresiones Regulares</div>';
        h+='<table style="border-collapse:collapse;font-size:.72rem;width:100%"><tr>'
          +'<th style="border:1px solid var(--border);padding:.4rem;text-align:left">Token</th>'
          +'<th style="border:1px solid var(--border);padding:.4rem;text-align:left">Descripción</th>'
          +'<th style="border:1px solid var(--border);padding:.4rem;text-align:left">Expresión Regular</th></tr>';
        regex.forEach(r=>{
            h+=`<tr><td style="border:1px solid var(--border);padding:.4rem">${esc(r.token)}</td>`
              +`<td style="border:1px solid var(--border);padding:.4rem">${esc(r.descripcion)}</td>`
              +`<td style="border:1px solid var(--border);padding:.4rem"><code>${esc(r.regex)}</code></td></tr>`;
        });
        h+='</table>';
    }
    return h;
}

function renderAutomatasHTML(items){
    if(!items.length) return '';
    let h='<div class="section-title" style="margin-top:1.5rem">Autómatas (AFND → AFD)</div>';
    items.forEach(it=>{
        h+=`<div style="margin:1rem 0;padding:.8rem;border:1px solid var(--border);border-radius:8px">`;
        h+=`<div style="font-weight:600;color:var(--accent)">${esc(it.token)} <code style="color:var(--text-dim)">${esc(it.regex)}</code></div>`;
        h+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:.6rem">';
        h+=`<div><div class="signo-result-nombre">AFND</div><pre class="mermaid">${esc(it.afnd_mermaid)}</pre>${renderTablaTransiciones(it.afnd_tabla)}</div>`;
        h+=`<div><div class="signo-result-nombre">AFD</div><pre class="mermaid">${esc(it.afd_mermaid)}</pre>${renderTablaTransiciones(it.afd_tabla)}</div>`;
        h+='</div></div>';
    });
    return h;
}

function renderSintacticoHTML(sint){
    const cats=sint.categorias||[];
    if(!cats.length) return '';
    const color={'directa':'var(--accent2)','indirecta':'var(--warn)','no_aparece':'var(--text-dim)'};
    let h='<div class="section-title" style="margin-top:1.5rem">Análisis Sintáctico · Categorías de Gramática (18)</div>';
    h+='<table style="border-collapse:collapse;font-size:.72rem;width:100%"><tr>'
      +'<th style="border:1px solid var(--border);padding:.4rem;text-align:left">Categoría</th>'
      +'<th style="border:1px solid var(--border);padding:.4rem;text-align:left">Presencia</th>'
      +'<th style="border:1px solid var(--border);padding:.4rem;text-align:left">Justificación</th></tr>';
    cats.forEach(c=>{
        h+=`<tr><td style="border:1px solid var(--border);padding:.4rem">${esc(c.nombre)}</td>`
          +`<td style="border:1px solid var(--border);padding:.4rem;color:${color[c.presencia]||'var(--text)'}">${esc(c.presencia)}</td>`
          +`<td style="border:1px solid var(--border);padding:.4rem">${esc(c.justificacion)}</td></tr>`;
    });
    h+='</table>';
    const prods=sint.producciones||[];
    if(prods.length){
        h+='<div class="section-title" style="margin-top:1rem">Producciones de las categorías presentes</div>';
        prods.forEach(p=>{
            h+=`<div style="margin:.4rem 0"><strong style="color:var(--accent)">${esc(p.nombre)}</strong>`
              +`<div class="code-block">${p.reglas.map(esc).join('\n')}</div></div>`;
        });
    }
    if(sint.glc_completa){
        h+='<div class="section-title" style="margin-top:1rem">Gramática Libre de Contexto completa</div>';
        h+=`<div class="code-block">${esc(sint.glc_completa)}</div>`;
    }
    if(sint.arbol_mermaid){
        h+='<div class="section-title" style="margin-top:1rem">Árbol Sintáctico</div>';
        h+=`<pre class="mermaid">${esc(sint.arbol_mermaid)}</pre>`;
    }
    return h;
}
```

- [ ] **Step 7: Ejecutar y verificar que el test de endpoint pasa**

Run: `python -m pytest tests/test_app.py -v`
Expected: PASS (2 tests)

- [ ] **Step 8: Verificación manual en el navegador**

Run: `python app.py` (en otra terminal) y abrir `http://localhost:5000`.
Verificar:
1. Aparece el header de descripción "VitalCheck — Compilador de Triaje Hospitalario".
2. Agregar un paciente (o usar el ejemplo) → **Procesar Triaje**.
3. Pestaña **Resultados**, **Errores** y **Código .py** funcionan **igual que antes** (sin cambios).
4. Pestaña **Modo Técnico**: además de Tokens + AST, aparecen las secciones nuevas:
   tabla Token↔Lexemas, tabla de Expresiones Regulares, diagramas Mermaid de AFND y AFD
   con sus tablas de transición, tabla de las 18 categorías, producciones, GLC y árbol sintáctico.
5. Los diagramas Mermaid se renderizan como grafos (no como texto plano).

- [ ] **Step 9: Ejecutar la suite completa**

Run: `python -m pytest -v`
Expected: PASS (todos los tests).

- [ ] **Step 10: Commit**

```bash
git add templates/index.html tests/test_app.py
git commit -m "feat(ui): header de descripcion y Proceso Interno en Modo Tecnico (Mermaid)"
```

---

## Self-Review

**Spec coverage:**
- Header de descripción → Task 5 Step 4. ✓
- No tocar lo existente → Global Constraints + Task 4/5 solo agregan; test de no-regresión Task 4 Step 1/5. ✓
- `lexico.py` (token↔lexema + regex) → Task 1. ✓
- `automatas.py` curado (AFND/AFD/tablas/Mermaid, selección por presentes) → Task 2. ✓
- `gramatica.py` (18 categorías, detección, producciones, GLC, árbol Mermaid) → Task 3. ✓
- Integración con claves nuevas en `compilar()` → Task 4. ✓
- Modo Técnico en un solo scroll con secciones (Léxico, Autómatas, Sintáctico) → Task 5 Steps 5-6. ✓
- Mermaid por CDN → Task 5 Step 3. ✓
- Tests pytest + no-regresión → Tasks 1-5. ✓
- Categorías esperadas (directas/indirectas/no_aparece) → Task 3 tests. ✓

**Placeholder scan:** Sin TBD/TODO; todo el código está completo en cada step. ✓

**Type consistency:** Las firmas usadas en Task 4 (`agrupar_tokens_lexemas`, `tabla_expresiones_regulares`, `seleccionar_automatas`, `detectar_categorias`, `producciones_presentes`, `GLC_COMPLETA`, `arbol_a_mermaid`) coinciden exactamente con las definidas en Tasks 1-3. Las claves del JSON consumidas en Task 5 (`token_lexemas`, `regex`, `afnd_mermaid`, `afd_mermaid`, `afnd_tabla`, `afd_tabla`, `categorias`, `producciones`, `glc_completa`, `arbol_mermaid`) coinciden con las producidas en Task 4. ✓
