RANGOS_VITALES = {
    'frecuencia_cardiaca': (40, 200, 'lpm'),
    'presion_sistolica':   (60, 250, 'mmHg'),
    'presion_diastolica':  (40, 150, 'mmHg'),
    'saturacion':          (70, 100, '%'),
    'temperatura':         (34.0, 42.0, '°C'),
    'frecuencia_respiratoria': (8, 40, 'rpm'),
    'glucosa':             (30, 600, 'mg/dL'),
}

UMBRALES_CRITICOS = {
    'frecuencia_cardiaca': [(0, 50, 'I'), (50, 60, 'II'), (150, 200, 'II'), (200, 999, 'I')],
    'presion_sistolica':   [(0, 80, 'I'), (80, 90, 'II')],
    'saturacion':          [(0, 85, 'I'), (85, 90, 'II'), (90, 95, 'III')],
    'temperatura':         [(0, 35, 'II'), (39.5, 42, 'II'), (42, 99, 'I')],
}

class AnalizadorSemantico:
    def __init__(self, arbol):
        self.arbol = arbol
        self.errores = []
        self.advertencias = []
        self.tabla_simbolos = {}

    def analizar(self):
        if not self.arbol:
            return [], []
        for nodo in self.arbol.hijos:
            if nodo.tipo == 'PACIENTE':
                self._analizar_paciente(nodo)
        return self.errores, self.advertencias

    def _analizar_paciente(self, nodo):
        paciente_id = nodo.valor
        if paciente_id in self.tabla_simbolos:
            self.errores.append({'tipo': 'Error Semántico', 'mensaje': f"Paciente '{paciente_id}' ya fue declarado (ID duplicado)", 'linea': '-'})
            return

        signos = {}
        sintoma = None
        prioridad_declarada = None

        for hijo in nodo.hijos:
            if hijo.tipo == 'SIGNOS_VITALES':
                for signo in hijo.hijos:
                    if signo.valor:
                        clave, valor = signo.valor.split('=')
                        signos[clave.strip()] = float(valor.strip())
            elif hijo.tipo == 'SINTOMA':
                sintoma = hijo.valor.strip('"')
                if not sintoma:
                    self.errores.append({'tipo': 'Error Semántico', 'mensaje': f"El síntoma de '{paciente_id}' no puede estar vacío", 'linea': '-'})
            elif hijo.tipo == 'PRIORIDAD':
                prioridad_declarada = hijo.valor

        for nombre, valor in signos.items():
            if nombre in RANGOS_VITALES:
                minv, maxv, unidad = RANGOS_VITALES[nombre]
                if not (minv <= valor <= maxv):
                    self.errores.append({'tipo': 'Error Semántico', 'mensaje': f"'{nombre}' = {valor} fuera del rango [{minv}, {maxv}] {unidad} para '{paciente_id}'", 'linea': '-'})

        prioridad_sugerida = self._calcular_prioridad(signos)
        if prioridad_declarada and prioridad_sugerida:
            niveles = ['I', 'II', 'III', 'IV', 'V']
            idx_dec = niveles.index(prioridad_declarada) if prioridad_declarada in niveles else -1
            idx_sug = niveles.index(prioridad_sugerida) if prioridad_sugerida in niveles else -1
            if idx_dec > idx_sug:
                self.advertencias.append({'tipo': 'Advertencia Semántica', 'mensaje': f"Paciente '{paciente_id}': prioridad NIVEL {prioridad_declarada} podría ser insuficiente, se sugiere NIVEL {prioridad_sugerida}", 'linea': '-'})

        self.tabla_simbolos[paciente_id] = {'signos': signos, 'sintoma': sintoma, 'prioridad': prioridad_declarada, 'prioridad_sugerida': prioridad_sugerida}

    def _calcular_prioridad(self, signos):
        prioridad_max = 'V'
        niveles = ['I', 'II', 'III', 'IV', 'V']
        for nombre, valor in signos.items():
            if nombre in UMBRALES_CRITICOS:
                for min_u, max_u, nivel in UMBRALES_CRITICOS[nombre]:
                    if min_u <= valor < max_u:
                        if niveles.index(nivel) < niveles.index(prioridad_max):
                            prioridad_max = nivel
        return prioridad_max

    def get_tabla_simbolos(self):
        orden = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5}
        ordenado = dict(sorted(
            self.tabla_simbolos.items(),
            key=lambda x: orden.get(x[1].get('prioridad', 'V'), 5)
        ))
        return ordenado

