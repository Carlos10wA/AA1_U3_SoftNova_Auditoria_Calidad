
import sqlite3
from contextlib import closing

import pytest

from database import DB_PATH, conectar, inicializar_db


@pytest.fixture
def conexion():
    """Establece una conexion para consultas de validacion."""
    assert DB_PATH.is_file()

    with closing(conectar()) as db:
        db.execute("PRAGMA query_only = ON")
        yield db


def test_integridad_base_datos(conexion):
    resultado = conexion.execute(
        "PRAGMA integrity_check"
    ).fetchone()[0]

    assert resultado == "ok"


def test_claves_foraneas_activas(conexion):
    resultado = conexion.execute(
        "PRAGMA foreign_keys"
    ).fetchone()[0]

    assert resultado == 1


def test_ausencia_errores_claves_foraneas(conexion):
    errores = conexion.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    assert len(errores) == 0


@pytest.mark.parametrize(
    "tabla, cantidad",
    [
        ("responsables", 5),
        ("auditorias", 4),
        ("no_conformidades", 5),
        ("indicadores", 3),
        ("mediciones", 9),
        ("acciones_pdca", 20),
    ],
)
def test_cantidad_registros(conexion, tabla, cantidad):
    resultado = conexion.execute(
        f"SELECT COUNT(*) FROM {tabla}"
    ).fetchone()[0]

    assert resultado == cantidad


def test_clasificacion_auditorias(conexion):
    registros = conexion.execute(
        "SELECT tipo FROM auditorias"
    ).fetchall()

    tipos = " ".join(
        registro["tipo"].casefold()
        for registro in registros
    )

    for categoria in (
        "interna",
        "externa",
        "certificaci",
        "seguimiento",
    ):
        assert categoria in tipos


def test_fundamentos_normativos(conexion):
    auditorias = conexion.execute(
        "SELECT * FROM auditorias"
    ).fetchall()

    for auditoria in auditorias:
        assert auditoria["fundamento_normativo"].strip()
        assert auditoria["objetivo"].strip()
        assert auditoria["estado"].strip()


def test_responsables_documentados(conexion):
    responsables = conexion.execute(
        "SELECT * FROM responsables"
    ).fetchall()

    for responsable in responsables:
        assert responsable["rol"].strip()
        assert responsable["funcion"].strip()


def test_codigos_no_conformidades(conexion):
    registros = conexion.execute(
        "SELECT codigo FROM no_conformidades"
    ).fetchall()

    codigos = {
        registro["codigo"]
        for registro in registros
    }

    assert codigos == {
        "NC-01",
        "NC-02",
        "NC-03",
        "NC-04",
        "NC-05",
    }


def test_documentacion_no_conformidades(conexion):
    registros = conexion.execute(
        "SELECT * FROM no_conformidades"
    ).fetchall()

    for registro in registros:
        assert registro["descripcion"].strip()
        assert registro["numeral_iso"].strip()
        assert registro["causa_probable"].strip()
        assert registro["prioridad"].strip()


def test_no_conformidades_abiertas(conexion):
    registros = conexion.execute("""
        SELECT COUNT(*)
        FROM no_conformidades
        WHERE estado = 'Abierta'
    """).fetchone()[0]

    assert registros == 5


def test_trazabilidad_auditorias(conexion):
    registros = conexion.execute("""
        SELECT n.codigo, a.tipo, r.rol
        FROM no_conformidades n
        INNER JOIN auditorias a
            ON n.auditoria_id = a.id
        INNER JOIN responsables r
            ON n.responsable_id = r.id
    """).fetchall()

    assert len(registros) == 5

    for registro in registros:
        assert registro["tipo"].strip()
        assert registro["rol"].strip()


@pytest.mark.parametrize(
    "codigo",
    ["NC-01", "NC-02", "NC-03", "NC-04", "NC-05"],
)
def test_ciclo_phva_completo(conexion, codigo):
    registros = conexion.execute("""
        SELECT p.fase
        FROM acciones_pdca p
        INNER JOIN no_conformidades n
            ON p.no_conformidad_id = n.id
        WHERE n.codigo = ?
    """, (codigo,)).fetchall()

    fases = {
        registro["fase"]
        for registro in registros
    }

    assert len(registros) == 4

    assert fases == {
        "Planificar",
        "Hacer",
        "Verificar",
        "Actuar",
    }


@pytest.mark.parametrize(
    "fase",
    ["Planificar", "Hacer", "Verificar", "Actuar"],
)
def test_distribucion_fases_phva(conexion, fase):
    cantidad = conexion.execute("""
        SELECT COUNT(*)
        FROM acciones_pdca
        WHERE fase = ?
    """, (fase,)).fetchone()[0]

    assert cantidad == 5


def test_documentacion_acciones_phva(conexion):
    acciones = conexion.execute("""
        SELECT p.*, r.rol
        FROM acciones_pdca p
        INNER JOIN responsables r
            ON p.responsable_id = r.id
    """).fetchall()

    assert len(acciones) == 20

    for accion in acciones:
        assert accion["accion"].strip()
        assert accion["plazo"].strip()
        assert accion["criterio_eficacia"].strip()
        assert accion["rol"].strip()


def test_estado_acciones_propuestas(conexion):
    acciones = conexion.execute(
        "SELECT estado, evidencia FROM acciones_pdca"
    ).fetchall()

    for accion in acciones:
        assert accion["estado"] == "Propuesta"
        assert accion["evidencia"].strip()


@pytest.mark.parametrize("indicador_id", [1, 2, 3])
def test_mediciones_por_indicador(conexion, indicador_id):
    registros = conexion.execute("""
        SELECT sprint, origen, numerador, denominador
        FROM mediciones
        WHERE indicador_id = ?
        ORDER BY sprint
    """, (indicador_id,)).fetchall()

    assert len(registros) == 3

    assert [
        registro["sprint"]
        for registro in registros
    ] == [1, 2, 3]

    for registro in registros:
        assert registro["origen"] == "Simulado"
        assert registro["numerador"] >= 0
        assert registro["denominador"] > 0

        if indicador_id in (2, 3):
            assert (
                registro["numerador"]
                <= registro["denominador"]
            )


def test_trazabilidad_indicadores(conexion):
    indicadores = conexion.execute("""
        SELECT i.*, r.rol
        FROM indicadores i
        INNER JOIN responsables r
            ON i.responsable_id = r.id
    """).fetchall()

    assert len(indicadores) == 3

    for indicador in indicadores:
        assert indicador["formula"].strip()
        assert indicador["periodicidad"].strip()
        assert indicador["fuente"].strip()
        assert indicador["rol"].strip()
        assert indicador["meta"] > 0
        assert indicador["sentido"] in (
            "Mayor", "Menor"
        )


@pytest.fixture
def base_temporal(tmp_path):
    """Crea una base aislada para pruebas negativas."""
    ruta = tmp_path / "softnova_pruebas.db"

    inicializar_db(ruta)

    with closing(conectar(ruta)) as db:
        db.execute("""
            INSERT INTO responsables
                (id, rol, funcion)
            VALUES
                (1, 'Responsable QA', 'Validar calidad')
        """)

        db.execute("""
            INSERT INTO indicadores (
                id, nombre, formula, responsable_id,
                meta, sentido, periodicidad, fuente
            )
            VALUES (
                1, 'Indicador temporal', 'N/D*100',
                1, 95, 'Mayor', 'Sprint', 'Pruebas'
            )
        """)

        db.commit()

        yield db


def test_rechazo_registro_huerfano(base_temporal):
    with pytest.raises(sqlite3.IntegrityError):
        base_temporal.execute("""
            INSERT INTO mediciones (
                indicador_id, sprint,
                numerador, denominador
            )
            VALUES (999, 1, 10, 100)
        """)


@pytest.mark.parametrize(
    "sprint, numerador, denominador",
    [
        (1, 10, 0),
        (1, 10, -100),
        (1, -10, 100),
        (0, 10, 100),
    ],
)
def test_restricciones_mediciones(
    base_temporal, sprint, numerador, denominador
):
    with pytest.raises(sqlite3.IntegrityError):
        base_temporal.execute("""
            INSERT INTO mediciones (
                indicador_id, sprint,
                numerador, denominador
            )
            VALUES (1, ?, ?, ?)
        """, (sprint, numerador, denominador))


def test_rechazo_mediciones_duplicadas(base_temporal):
    sentencia = """
        INSERT INTO mediciones (
            indicador_id, sprint,
            numerador, denominador
        )
        VALUES (1, 1, 95, 100)
    """

    base_temporal.execute(sentencia)

    with pytest.raises(sqlite3.IntegrityError):
        base_temporal.execute(sentencia)
