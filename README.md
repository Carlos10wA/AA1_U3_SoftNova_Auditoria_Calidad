# SoftNova S.A.S. - Sistema de Auditoria de Calidad

## Informacion academica

- Institucion: Tecnologica del Oriente.
- Programa: Ingenieria de Software.
- Asignatura: Pruebas y Calidad de Software.
- Actividad: AA1 - Unidad 3.
- Estudiante: Carlos Alberto Ayala Larrahondo.
- Docente: Helio Ruber Lopez Carreno.
- Fecha: Noviembre de 2026.

## Descripcion

Prototipo academico para la gestion de auditorias,
no conformidades, indicadores de calidad y planes
de mejoramiento continuo mediante el ciclo PHVA.

El proyecto toma como referencia las normas
ISO 9001:2015 e ISO 19011:2018.

Los datos empresariales son simulados. Los resultados
de las pruebas corresponden a ejecuciones reales
sobre el prototipo desarrollado.

## Tecnologias utilizadas

- Python 3.10.11.
- Flask.
- SQLite.
- HTML, CSS y JavaScript.
- Pytest.
- Selenium.
- Ruff.
- Coverage.py.

## Funcionalidades

- Panel ejecutivo de calidad.
- Clasificacion de cuatro tipos de auditoria.
- Registro de cinco no conformidades.
- Seguimiento de tres indicadores KPI.
- Gestion de veinte acciones PHVA propuestas.
- Asignacion de responsables.
- Informe ejecutivo.

## Instalacion

Ejecutar desde la carpeta del proyecto:

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    python seed.py
    python app.py

Abrir en el navegador:

http://127.0.0.1:5000

## Validacion automatizada

Con Google Chrome instalado y sin otro servidor
ocupando el puerto 5000, ejecutar:

    python -m coverage run --branch --source=app,database,indicadores run_audit_coverage.py
    python -m coverage report -m

Analisis estatico:

    python -m ruff check app.py database.py seed.py indicadores.py tests

## Resultados obtenidos

| Metodo | Resultado |
| --- | --- |
| Pruebas API REST | 16 aprobadas |
| Validacion matematica | 47 aprobadas |
| Integridad y trazabilidad | 37 aprobadas |
| Pruebas Selenium | 31 aprobadas |
| Total de pruebas | 131 aprobadas |
| Fallos finales | 0 |
| Cobertura combinada | 74% |
| Cobertura de sentencias | 75.15% |
| Hallazgos iniciales Ruff | 10 |
| Hallazgos finales Ruff | 0 |

## Evidencias

La carpeta evidencias contiene 26 capturas de pantalla,
reportes HTML, resultados XML y reportes de cobertura
y analisis estatico.

## Alcance

Proyecto exclusivamente academico. No constituye
una certificacion de cumplimiento de ISO 9001:2015.
