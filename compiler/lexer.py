import re

TOKEN_SPEC = [
    ('PACIENTE',     r'\bPACIENTE\b'),
    ('SIGNOS',       r'\bSIGNOS\b'),
    ('VITALES',      r'\bVITALES\b'),
    ('SINTOMA',      r'\bSINTOMA\b'),
    ('PRIORIDAD',    r'\bPRIORIDAD\b'),
    ('NIVEL',        r'\bNIVEL\b'),
    ('FIN',          r'\bFIN\b'),
    ('NIVEL_VAL',    r'\b(I|II|III|IV|V)\b'),
    ('NUMERO',       r'\d+(\.\d+)?'),
    ('CADENA',       r'"[^"]*"'),
    ('ID',           r'[A-Za-záéíóúÁÉÍÓÚñÑ][A-Za-záéíóúÁÉÍÓÚñÑ0-9_]*'),
    ('ASIGNAR',      r'='),
    ('LLAVE_AB',     r'\{'),
    ('LLAVE_CI',     r'\}'),
    ('PUNTO_COMA',   r';'),
    ('DOS_PUNTOS',   r':'),
    ('COMA',         r','),
    ('COMENTARIO',   r'//[^\n]*'),
    ('NUEVA_LINEA',  r'\n'),
    ('ESPACIO',      r'[ \t]+'),
    ('ERROR',        r'.'),
]

TOKEN_REGEX = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)

class Token:
    def __init__(self, tipo, valor, linea, columna):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna

    def to_dict(self):
        return {'tipo': self.tipo, 'valor': self.valor, 'linea': self.linea, 'columna': self.columna}

class Lexer:
    def __init__(self, codigo):
        self.codigo = codigo
        self.tokens = []
        self.errores = []

    def analizar(self):
        self.tokens = []
        self.errores = []
        linea = 1
        inicio_linea = 0

        for mo in re.finditer(TOKEN_REGEX, self.codigo):
            kind = mo.lastgroup
            valor = mo.group()
            columna = mo.start() - inicio_linea + 1

            if kind == 'NUEVA_LINEA':
                linea += 1
                inicio_linea = mo.end()
            elif kind in ('ESPACIO', 'COMENTARIO'):
                pass
            elif kind == 'ERROR':
                self.errores.append({'tipo': 'Error Léxico', 'mensaje': f"Carácter no reconocido: '{valor}'", 'linea': linea, 'columna': columna})
            else:
                self.tokens.append(Token(kind, valor, linea, columna))

        return self.tokens, self.errores

