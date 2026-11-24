
import pytest

from indicadores import (
    calcular_desviacion,
    calcular_indicador,
    evaluar_meta,
    obtener_indicadores,
)


@pytest.mark.parametrize(
    "numerador, denominador, esperado",
    [
        (5, 100, 5.0),
        (15, 200, 7.5),
        (10, 100, 10.0),
        (95, 100, 95.0),
        (90, 100, 90.0),
        (85, 100, 85.0),
        (80, 100, 80.0),
        (75, 100, 75.0),
        (0, 100, 0.0),
        (100, 100, 100.0),
        (150, 100, 150.0),
    ],
)
def test_calculo_indicadores(
    numerador, denominador, esperado
):
    """Verifica la exactitud de las formulas."""
    resultado = calcular_indicador(
        numerador, denominador
    )

    assert resultado == pytest.approx(esperado)



@pytest.mark.parametrize(
    "numerador, denominador, excepcion",
    [
        (10, 0, ValueError),
        (10, -100, ValueError),
        (-5, 100, ValueError),
        ("10", 100, TypeError),
        (10, "100", TypeError),
        (None, 100, TypeError),
        (True, 100, TypeError),
        (10, False, TypeError),
        (float("nan"), 100, ValueError),
        (float("inf"), 100, ValueError),
        (10, float("inf"), ValueError),
    ],
)
def test_mediciones_invalidas(
    numerador, denominador, excepcion
):
    """Comprueba el rechazo de datos incorrectos."""
    with pytest.raises(excepcion):
        calcular_indicador(
            numerador, denominador
        )



@pytest.mark.parametrize(
    "resultado, meta, sentido, esperado",
    [
        (95, 95, "Mayor", "Cumple"),
        (100, 95, "Mayor", "Cumple"),
        (85, 95, "Mayor", "No cumple"),
        (5, 5, "Menor", "Cumple"),
        (3, 5, "Menor", "Cumple"),
        (10, 5, "Menor", "No cumple"),
    ],
)
def test_evaluacion_metas(
    resultado, meta, sentido, esperado
):
    """Comprueba el cumplimiento de las metas."""
    assert evaluar_meta(
        resultado, meta, sentido
    ) == esperado


@pytest.mark.parametrize(
    "resultado, meta, sentido, esperado",
    [
        (85, 95, "Mayor", 10),
        (75, 95, "Mayor", 20),
        (95, 95, "Mayor", 0),
        (100, 95, "Mayor", 0),
        (10, 5, "Menor", 5),
        (7.5, 5, "Menor", 2.5),
        (5, 5, "Menor", 0),
        (3, 5, "Menor", 0),
    ],
)
def test_calculo_desviaciones(
    resultado, meta, sentido, esperado
):
    """Valida las desviaciones desfavorables."""
    assert calcular_desviacion(
        resultado, meta, sentido
    ) == pytest.approx(esperado)


def test_sentido_meta_invalido():
    """Rechaza sentidos de evaluacion incorrectos."""
    with pytest.raises(ValueError):
        evaluar_meta(90, 95, "Incorrecto")


def test_sentido_desviacion_invalido():
    """Rechaza sentidos de desviacion incorrectos."""
    with pytest.raises(ValueError):
        calcular_desviacion(90, 95, "Incorrecto")


@pytest.mark.parametrize(
    "identificador, esperado",
    [
        (1, [5.0, 7.5, 10.0]),
        (2, [95.0, 90.0, 85.0]),
        (3, [85.0, 80.0, 75.0]),
    ],
)
def test_historico_indicadores(
    identificador, esperado
):
    """Verifica los resultados historicos de SQLite."""
    indicadores = obtener_indicadores()

    indicador = next(
        item
        for item in indicadores
        if item["id"] == identificador
    )

    resultados = [
        medicion["resultado"]
        for medicion in indicador["mediciones"]
    ]

    assert resultados == pytest.approx(esperado)
    assert len(indicador["mediciones"]) == 3


def test_duplicacion_tasa_defectos():
    """Confirma el incremento del 100% en defectos."""
    indicadores = obtener_indicadores()

    defectos = next(
        item
        for item in indicadores
        if item["id"] == 1
    )

    inicial = defectos["mediciones"][0]["resultado"]
    final = defectos["mediciones"][-1]["resultado"]

    incremento = (
        (final - inicial) / inicial
    ) * 100

    assert incremento == pytest.approx(100.0)
    assert final == pytest.approx(inicial * 2)


def test_indicadores_fuera_de_meta():
    """Comprueba el diagnostico del ultimo sprint."""
    indicadores = obtener_indicadores()

    assert len(indicadores) == 3

    for indicador in indicadores:
        ultima = indicador["ultima_medicion"]

        assert ultima is not None
        assert ultima["estado"] == "No cumple"
        assert ultima["desviacion"] > 0


@pytest.mark.parametrize(
    "identificador, desviacion",
    [
        (1, 5.0),
        (2, 10.0),
        (3, 20.0),
    ],
)
def test_desviacion_ultimo_sprint(
    identificador, desviacion
):
    """Comprueba las desviaciones del sprint final."""
    indicadores = obtener_indicadores()

    indicador = next(
        item
        for item in indicadores
        if item["id"] == identificador
    )

    assert indicador["ultima_medicion"][
        "desviacion"
    ] == pytest.approx(desviacion)


def test_responsables_indicadores():
    """Verifica la asignacion de responsables."""
    indicadores = obtener_indicadores()

    for indicador in indicadores:
        assert indicador["responsable"].strip()
        assert indicador["formula"].strip()
        assert indicador["periodicidad"].strip()
        assert indicador["fuente"].strip()
