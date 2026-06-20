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
        # AFND: alternación I|II|III|IV|V con ε-transiciones a cada rama (estilo Thompson).
        'afnd': {
            'estados': ['N0', 'a1', 'a2', 'b1', 'b2', 'b3',
                        'c1', 'c2', 'c3', 'c4', 'd1', 'd2', 'd3', 'e1', 'e2'],
            'inicial': 'N0',
            'finales': ['a2', 'b3', 'c4', 'd3', 'e2'],
            'alfabeto': ['I', 'V', 'ε'],
            'transiciones': [
                ('N0', 'ε', 'a1'), ('a1', 'I', 'a2'),                                 # I
                ('N0', 'ε', 'b1'), ('b1', 'I', 'b2'), ('b2', 'I', 'b3'),              # II
                ('N0', 'ε', 'c1'), ('c1', 'I', 'c2'), ('c2', 'I', 'c3'), ('c3', 'I', 'c4'),  # III
                ('N0', 'ε', 'd1'), ('d1', 'I', 'd2'), ('d2', 'V', 'd3'),              # IV
                ('N0', 'ε', 'e1'), ('e1', 'V', 'e2'),                                 # V
            ],
        },
        # AFD: determinización con prefijos fusionados.
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
        # AFND y AFD son objetos distintos aunque reconozcan el mismo literal,
        # para que un consumidor no pueda corromper uno al mutar el otro.
        return {'afnd': automata_literal(lexema), 'afd': automata_literal(lexema)}
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
