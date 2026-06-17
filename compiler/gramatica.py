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
    'cadenas_balanceadas': ['<cadena> ::= \'"\' <caracter>* \'"\''],
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
<cadena>     ::= '"' <caracter>* '"'
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
    if arbol is None:
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
