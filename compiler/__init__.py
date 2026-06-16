from .lexer import Lexer
from .parser import Parser
from .semantic import AnalizadorSemantico
from .codegen import GeneradorCodigo

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
        'exitoso': False
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

    return resultado
