
from contextlib import closing
from math import isfinite

from database import DB_PATH, conectar


def calcular_indicador(numerador, denominador):
    """Calcula un indicador como razón multiplicada por 100."""

    for valor in (numerador, denominador):
        if isinstance(valor, bool):
            raise TypeError("Los valores deben ser numericos.")

        if not isinstance(valor, (int, float)):
            raise TypeError("Los valores deben ser numericos.")

        if not isfinite(valor):
            raise ValueError("Los valores deben ser finitos.")

    if numerador < 0:
        raise ValueError("El numerador no puede ser negativo.")

    if denominador <= 0:
        raise ValueError("El denominador debe ser mayor que cero.")

    return (numerador / denominador) * 100


def evaluar_meta(resultado, meta, sentido):
    """Determina si una medición cumple su meta."""

    if sentido == "Mayor":
        return "Cumple" if resultado >= meta else "No cumple"

    if sentido == "Menor":
        return "Cumple" if resultado <= meta else "No cumple"

    raise ValueError("Sentido de evaluacion no valido.")


def calcular_desviacion(resultado, meta, sentido):
    """Calcula la distancia desfavorable respecto a la meta."""

    if sentido == "Mayor":
        return round(max(0, meta - resultado), 2)

    if sentido == "Menor":
        return round(max(0, resultado - meta), 2)

    raise ValueError("Sentido de evaluacion no valido.")


def obtener_indicadores(db_path=DB_PATH):
    """Consulta indicadores, responsables y mediciones."""

    with closing(conectar(db_path)) as conexion:

        indicadores = conexion.execute("""
            SELECT
                i.id,
                i.nombre,
                i.formula,
                i.meta,
                i.sentido,
                i.periodicidad,
                i.fuente,
                r.rol AS responsable
            FROM indicadores i
            INNER JOIN responsables r
                ON i.responsable_id = r.id
            ORDER BY i.id
        """).fetchall()

        resultados = []

        for registro in indicadores:
            indicador = dict(registro)

            mediciones = conexion.execute("""
                SELECT
                    sprint,
                    numerador,
                    denominador,
                    origen
                FROM mediciones
                WHERE indicador_id = ?
                ORDER BY sprint
            """, (indicador["id"],)).fetchall()

            historial = []

            for registro_medicion in mediciones:
                medicion = dict(registro_medicion)

                numerador = medicion["numerador"]
                denominador = medicion["denominador"]

              
                if indicador["id"] in (2, 3) and numerador > denominador:
                    raise ValueError(
                        "Medicion porcentual inconsistente."
                    )

                valor = calcular_indicador(
                    numerador,
                    denominador
                )


                medicion["resultado"] = round(valor, 2)

                medicion["estado"] = evaluar_meta(
                    valor,
                    indicador["meta"],
                    indicador["sentido"]
                )

                medicion["desviacion"] = calcular_desviacion(
                    valor,
                    indicador["meta"],
                    indicador["sentido"]
                )

                historial.append(medicion)

            indicador["mediciones"] = historial
            indicador["ultima_medicion"] = (
                historial[-1] if historial else None
            )

            resultados.append(indicador)

    return resultados


def mostrar_reporte():
    """Presenta los resultados de los KPI en la terminal."""

    indicadores = obtener_indicadores()

    print("=" * 65)
    print("SOFTNOVA S.A.S. - INDICADORES DE CALIDAD")
    print("DATOS SIMULADOS CON FINES ACADEMICOS")
    print("=" * 65)

    for indicador in indicadores:

        unidad = (
            " defectos/100 historias"
            if indicador["id"] == 1
            else "%"
        )

        operador = (
            ">=" if indicador["sentido"] == "Mayor" else "<="
        )

        print(
            f"\nKPI-{indicador['id']:02d}: "
            f"{indicador['nombre']}"
        )

        print(f"Formula: {indicador['formula']}")
        print(f"Responsable: {indicador['responsable']}")
        print(f"Periodicidad: {indicador['periodicidad']}")
        print(f"Fuente: {indicador['fuente']}")
        print(f"Meta: {operador} {indicador['meta']}{unidad}")

        print("-" * 65)

        for medicion in indicador["mediciones"]:
            print(
                f"Sprint {medicion['sprint']}: "
                f"{medicion['resultado']:.2f}{unidad} | "
                f"{medicion['estado']}"
            )

        ultima = indicador["ultima_medicion"]

        if ultima:
            print(f"Estado actual: {ultima['estado']}")
            print(
                f"Desviacion desfavorable: "
                f"{ultima['desviacion']:.2f} puntos"
            )

    evaluados = [
        item for item in indicadores
        if item["ultima_medicion"] is not None
    ]

    cumplidos = sum(
        1 for item in evaluados
        if item["ultima_medicion"]["estado"] == "Cumple"
    )

    print("\n" + "=" * 65)
    print(f"Indicadores definidos: {len(indicadores)}")
    print(f"Indicadores evaluados: {len(evaluados)}")
    print(f"Indicadores que cumplen: {cumplidos}")
    print(
        f"Indicadores fuera de meta: "
        f"{len(evaluados) - cumplidos}"
    )
    print("=" * 65)


if __name__ == "__main__":
    mostrar_reporte()
