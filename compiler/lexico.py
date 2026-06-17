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
