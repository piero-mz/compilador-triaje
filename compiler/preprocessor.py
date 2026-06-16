import json

def json_a_triaje(contenido_json):
    """
    Convierte un archivo JSON con datos de pacientes
    al lenguaje de triaje del compilador VitalCheck.
    """
    try:
        datos = json.loads(contenido_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON inválido: {e}")

    if isinstance(datos, dict):
        datos = [datos]

    if not isinstance(datos, list):
        raise ValueError("El JSON debe ser un objeto o lista de pacientes")

    lineas = []

    for paciente in datos:
        id_paciente = paciente.get('id', 'Paciente')
        sintoma = paciente.get('sintoma', 'Sin sintoma')
        prioridad = paciente.get('prioridad', 'V')

        lineas.append(f'PACIENTE {id_paciente} {{')
        lineas.append('    SIGNOS VITALES {')

        campos_signos = [
            'frecuencia_cardiaca',
            'presion_sistolica',
            'presion_diastolica',
            'saturacion',
            'temperatura',
            'frecuencia_respiratoria',
            'glucosa'
        ]

        for campo in campos_signos:
            if campo in paciente:
                lineas.append(f'        {campo} = {paciente[campo]};')

        lineas.append('    }')
        lineas.append(f'    SINTOMA = "{sintoma}";')
        lineas.append(f'    PRIORIDAD = NIVEL {prioridad};')
        lineas.append('}')
        lineas.append('')

    return '\n'.join(lineas)
