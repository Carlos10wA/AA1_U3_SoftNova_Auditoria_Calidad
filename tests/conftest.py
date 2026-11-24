
import pytest
import requests

BASE_URL = "http://127.0.0.1:5000"
TIMEOUT = 10


@pytest.fixture(scope="session")
def base_url():
    """Direccion base del sistema SoftNova."""
    return BASE_URL


@pytest.fixture(scope="session")
def api_session(base_url):
    """Sesion HTTP compartida para las pruebas REST."""
    with requests.Session() as session:
        respuesta = session.get(
            f"{base_url}/api/salud",
            timeout=TIMEOUT,
        )

        assert respuesta.status_code == 200, (
            "El servidor SoftNova no esta operativo."
        )

        assert respuesta.json()["sistema"] == "SoftNova S.A.S."

        yield session


@pytest.fixture(scope="session")
def timeout():
    """Tiempo maximo de espera de las solicitudes."""
    return TIMEOUT
