from .lexer import Lexer
from .parser import Parser
from .semantic import AnalizadorSemantico
from .codegen import GeneradorCodigo
from .lexico import agrupar_tokens_lexemas, tabla_expresiones_regulares
from .automatas import seleccionar_automatas
from .gramatica import (
    detectar_categorias,
    producciones_presentes,
    GLC_COMPLETA,
    arbol_a_mermaid,
)

def compilar(codigo):
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

    lexer = Lexer(codigo)
    tokens, errores_lex = lexer.analizar()
    resultado['tokens'] = [t.to_dict() for t in tokens]
    resultado['errores_lexicos'] = errores_lex

    if errores_lex:
        return resultado

    parser = Parser(tokens)
    arbol, errores_sin = parser.parsear()
    resultado['arbol'] = arbol.to_dict() if arbol else None
    resultado['errores_sintacticos'] = errores_sin

    if errores_sin:
        return resultado

    semantico = AnalizadorSemantico(arbol)
    errores_sem, advertencias = semantico.analizar()
    resultado['errores_semanticos'] = errores_sem
    resultado['advertencias'] = advertencias

    tabla = semantico.get_tabla_simbolos()
    orden = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5}
    tabla_ordenada = dict(sorted(tabla.items(), key=lambda x: orden.get(x[1].get('prioridad', 'V'), 5)))
    resultado['tabla_simbolos'] = tabla_ordenada

    if not errores_sem:
        gen = GeneradorCodigo(arbol, tabla_ordenada)
        resultado['codigo_generado'] = gen.generar()

    total_errores = len(errores_lex) + len(errores_sin) + len(errores_sem)
    resultado['exitoso'] = total_errores == 0

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
