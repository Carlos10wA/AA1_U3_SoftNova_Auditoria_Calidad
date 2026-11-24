
import pytest


@pytest.mark.parametrize(
    "ruta",
    [
        "/api/salud",
        "/api/responsables",
        "/api/auditorias",
        "/api/no-conformidades",
        "/api/indicadores",
        "/api/acciones-pdca",
        "/api/resumen",
    ],
)
def test_disponibilidad_servicios(
    api_session, base_url, timeout, ruta
):
    """Verifica la disponibilidad de los servicios REST."""
    respuesta = api_session.get(
        f"{base_url}{ruta}", timeout=timeout
    )

    assert respuesta.status_code == 200
    assert "application/json" in respuesta.headers["Content-Type"]


def test_estado_salud(api_session, base_url, timeout):
    """Comprueba el estado operativo y la integridad SQLite."""
    respuesta = api_session.get(
        f"{base_url}/api/salud", timeout=timeout
    )
    datos = respuesta.json()

    assert respuesta.status_code == 200
    assert datos["sistema"] == "SoftNova S.A.S."
    assert datos["estado"] == "Operativo"
    assert datos["base_datos"] == "ok"
    assert datos["errores_claves_foraneas"] == 0


@pytest.mark.parametrize(
    "ruta, cantidad",
    [
        ("/api/responsables", 5),
        ("/api/auditorias", 4),
        ("/api/no-conformidades", 5),
        ("/api/indicadores", 3),
        ("/api/acciones-pdca", 20),
    ],
)
def test_cantidad_registros(
    api_session, base_url, timeout, ruta, cantidad
):
    """Comprueba la cantidad esperada de registros."""
    respuesta = api_session.get(
        f"{base_url}{ruta}", timeout=timeout
    )

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert isinstance(datos, list)
    assert len(datos) == cantidad


def test_resumen_ejecutivo(api_session, base_url, timeout):
    """Valida la consistencia del panel ejecutivo."""
    respuesta = api_session.get(
        f"{base_url}/api/resumen", timeout=timeout
    )

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert datos["auditorias"] == 4
    assert datos["responsables"] == 5
    assert datos["no_conformidades"] == 5
    assert datos["no_conformidades_abiertas"] == 5
    assert datos["acciones_pdca"] == 20
    assert datos["indicadores"] == 3
    assert datos["indicadores_evaluados"] == 3
    assert datos["indicadores_cumplidos"] == 0
    assert datos["indicadores_fuera_meta"] == 3
    assert datos["origen_mediciones"] == "Simulado"


def test_recurso_no_encontrado(
    api_session, base_url, timeout
):
    """Comprueba el manejo controlado de errores HTTP 404."""
    respuesta = api_session.get(
        f"{base_url}/api/recurso-inexistente",
        timeout=timeout,
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == 404
    assert respuesta.json()["error"] == "Recurso no encontrado"


def test_metodo_no_permitido(
    api_session, base_url, timeout
):
    """Comprueba que un servicio de consulta rechace POST."""
    respuesta = api_session.post(
        f"{base_url}/api/auditorias",
        json={},
        timeout=timeout,
    )

    assert respuesta.status_code == 405
