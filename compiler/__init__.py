from .lexer import Lexer
from .parser import Parser
from .semantic import AnalizadorSemantico

def compilar(codigo):
    resultado = {
        'tokens': [],
        'arbol': None,
        'tabla_simbolos': {},
        'errores_lexicos': [],
        'errores_sintacticos': [],
        'errores_semanticos': [],
        'advertencias': [],
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
    resultado['tabla_simbolos'] = semantico.get_tabla_simbolos()

    total_errores = len(errores_lex) + len(errores_sin) + len(errores_sem)
    resultado['exitoso'] = total_errores == 0

    return resultado
