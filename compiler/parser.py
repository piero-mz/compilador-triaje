class NodoAST:
    def __init__(self, tipo, valor=None, hijos=None):
        self.tipo = tipo
        self.valor = valor
        self.hijos = hijos or []

    def to_dict(self):
        return {'tipo': self.tipo, 'valor': self.valor, 'hijos': [h.to_dict() for h in self.hijos]}

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errores = []

    def token_actual(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consumir(self, tipo_esperado):
        tok = self.token_actual()
        if tok and tok.tipo == tipo_esperado:
            self.pos += 1
            return tok
        else:
            valor_actual = tok.valor if tok else 'EOF'
            linea = tok.linea if tok else '?'
            self.errores.append({'tipo': 'Error Sintáctico', 'mensaje': f"Se esperaba '{tipo_esperado}', se encontró '{valor_actual}'", 'linea': linea, 'columna': tok.columna if tok else 0})
            return None

    def parsear(self):
        self.arbol = self.programa()
        return self.arbol, self.errores

    def programa(self):
        nodo = NodoAST('PROGRAMA')
        while self.token_actual() is not None:
            decl = self.declaracion()
            if decl:
                nodo.hijos.append(decl)
            else:
                break
        return nodo

    def declaracion(self):
        tok = self.token_actual()
        if tok and tok.tipo == 'PACIENTE':
            return self.decl_paciente()
        return None

    def decl_paciente(self):
        self.consumir('PACIENTE')
        id_tok = self.consumir('ID')
        self.consumir('LLAVE_AB')
        nodo = NodoAST('PACIENTE', valor=id_tok.valor if id_tok else 'desconocido')

        while self.token_actual() and self.token_actual().tipo != 'LLAVE_CI':
            tok = self.token_actual()
            if tok.tipo == 'SIGNOS':
                nodo.hijos.append(self.campo_signos())
            elif tok.tipo == 'SINTOMA':
                nodo.hijos.append(self.campo_sintoma())
            elif tok.tipo == 'PRIORIDAD':
                nodo.hijos.append(self.campo_prioridad())
            else:
                self.errores.append({'tipo': 'Error Sintáctico', 'mensaje': f"Token inesperado '{tok.valor}'", 'linea': tok.linea, 'columna': tok.columna})
                self.pos += 1

        self.consumir('LLAVE_CI')
        return nodo

    def campo_signos(self):
        self.consumir('SIGNOS')
        self.consumir('VITALES')
        self.consumir('LLAVE_AB')
        nodo = NodoAST('SIGNOS_VITALES')
        while self.token_actual() and self.token_actual().tipo == 'ID':
            signo = self.signo()
            if signo:
                nodo.hijos.append(signo)
        self.consumir('LLAVE_CI')
        return nodo

    def signo(self):
        id_tok = self.consumir('ID')
        self.consumir('ASIGNAR')
        num_tok = self.consumir('NUMERO')
        self.consumir('PUNTO_COMA')
        if id_tok and num_tok:
            return NodoAST('SIGNO', valor=f'{id_tok.valor}={num_tok.valor}')
        return None

    def campo_sintoma(self):
        self.consumir('SINTOMA')
        self.consumir('ASIGNAR')
        val = self.consumir('CADENA')
        self.consumir('PUNTO_COMA')
        return NodoAST('SINTOMA', valor=val.valor if val else '')

    def campo_prioridad(self):
        self.consumir('PRIORIDAD')
        self.consumir('ASIGNAR')
        self.consumir('NIVEL')
        nivel = self.consumir('NIVEL_VAL')
        self.consumir('PUNTO_COMA')
        return NodoAST('PRIORIDAD', valor=nivel.valor if nivel else '')

