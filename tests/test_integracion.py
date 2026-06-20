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
    assert r['analisis_sintactico'] == {
        'categorias': [], 'producciones': [], 'glc_completa': '', 'arbol_mermaid': '',
    }
