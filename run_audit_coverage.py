
from threading import Thread

import pytest
from werkzeug.serving import make_server

from app import app


def main():
    servidor = make_server(
        "127.0.0.1",
        5000,
        app,
        threaded=True,
    )

    hilo = Thread(
        target=servidor.serve_forever,
        daemon=True,
    )

    hilo.start()

    print("\nServidor SoftNova iniciado.")
    print("Ejecutando validacion consolidada.\n")

    try:
        resultado = pytest.main([
            "tests",
            "-v",
            "--html=evidencias/Reporte_Final_Pruebas.html",
            "--self-contained-html",
            "--junitxml=evidencias/Resultados_Finales.xml",
        ])
    finally:
        servidor.shutdown()
        hilo.join()
        servidor.server_close()

    return resultado


if __name__ == "__main__":
    raise SystemExit(main())
