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
