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
