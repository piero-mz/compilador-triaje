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


def test_sin_llaves_no_aparece():
    tokens_sin_llaves = [t for t in TOKENS if t['tipo'] not in ('LLAVE_AB', 'LLAVE_CI')]
    res = {c['id']: c['presencia'] for c in detectar_categorias(tokens_sin_llaves, ARBOL)}
    assert res['parentesis_balanceados'] == 'no_aparece'


def test_glc_completa_no_vacia():
    assert GLC_COMPLETA.strip()
