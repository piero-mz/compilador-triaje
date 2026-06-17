class GeneradorCodigo:
    def __init__(self, arbol, tabla_simbolos):
        self.arbol = arbol
        self.tabla_simbolos = tabla_simbolos
        self.codigo = []

    def generar(self):
        self.codigo = []
        self.codigo.append('# Código generado')
        self.codigo.append('# Compilador de Triaje Hospitalario - VitalCheck')
        self.codigo.append('')
        self.codigo.append('from dataclasses import dataclass')
        self.codigo.append('from typing import List')
        self.codigo.append('')
        self.codigo.append('')
        self.codigo.append('@dataclass')
        self.codigo.append('class Paciente:')
        self.codigo.append('    id: str')
        self.codigo.append('    signos_vitales: dict')
        self.codigo.append('    sintoma: str')
        self.codigo.append('    prioridad: str')
        self.codigo.append('')
        self.codigo.append('')
        self.codigo.append('def clasificar_pacientes() -> List[Paciente]:')
        self.codigo.append('    pacientes = []')
        self.codigo.append('')

        orden = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5}
        tabla_ordenada = dict(sorted(
            self.tabla_simbolos.items(),
            key=lambda x: orden.get(x[1].get('prioridad', 'V'), 5)
        ))

        for id_paciente, datos in tabla_ordenada.items():
            self.codigo.append(f'    # Paciente: {id_paciente}')
            self.codigo.append(f'    pacientes.append(Paciente(')
            self.codigo.append(f'        id="{id_paciente}",')
            self.codigo.append(f'        signos_vitales={datos["signos"]},')
            self.codigo.append(f'        sintoma="{datos["sintoma"]}",')
            self.codigo.append(f'        prioridad="{datos["prioridad"]}"')
            self.codigo.append(f'    ))')
            self.codigo.append('')

        self.codigo.append('    return pacientes')
        self.codigo.append('')
        self.codigo.append('')
        self.codigo.append('if __name__ == "__main__":')
        self.codigo.append('    pacientes = clasificar_pacientes()')
        self.codigo.append('    for p in pacientes:')
        self.codigo.append('        print(f"Paciente: {p.id} | Prioridad: {p.prioridad} | Síntoma: {p.sintoma}")')

        return '\n'.join(self.codigo)
