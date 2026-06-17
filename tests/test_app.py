import pytest
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    return flask_app.test_client()


def test_index_tiene_header_descripcion_y_mermaid(client):
    html = client.get('/').get_data(as_text=True)
    assert 'mermaid' in html.lower()           # script Mermaid por CDN
    assert 'Proceso Interno' in html or 'proceso interno' in html.lower()


def test_compilar_devuelve_secciones_nuevas(client):
    codigo = ('PACIENTE Garcia { SIGNOS VITALES { frecuencia_cardiaca = 110; } '
              'SINTOMA = "Dolor"; PRIORIDAD = NIVEL II; }')
    resp = client.post('/compilar', json={'codigo': codigo})
    data = resp.get_json()
    assert 'analisis_automatas' in data
    assert data['analisis_sintactico']['categorias']
