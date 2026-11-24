
from contextlib import closing

from flask import Flask, jsonify, render_template

from database import DB_PATH, conectar
from indicadores import obtener_indicadores


def crear_app(db_path=DB_PATH):
    app = Flask(__name__)

    app.config["DATABASE"] = db_path

    def consultar(sql, parametros=()):
        with closing(
            conectar(app.config["DATABASE"])
        ) as conexion:
            registros = conexion.execute(
                sql, parametros
            ).fetchall()

            return [dict(registro) for registro in registros]

    @app.get("/")
    def inicio():
        return render_template("index.html")

    @app.get("/api/salud")
    def salud():
        with closing(
            conectar(app.config["DATABASE"])
        ) as conexion:

            integridad = conexion.execute(
                "PRAGMA integrity_check"
            ).fetchone()[0]

            errores_fk = conexion.execute(
                "PRAGMA foreign_key_check"
            ).fetchall()

        correcto = integridad == "ok" and not errores_fk

        return jsonify({
            "sistema": "SoftNova S.A.S.",
            "estado": "Operativo" if correcto else "Degradado",
            "base_datos": integridad,
            "errores_claves_foraneas": len(errores_fk),
            "entorno": "Simulacion academica",
        }), 200 if correcto else 503

    @app.get("/api/responsables")
    def responsables():
        datos = consultar("""
            SELECT id, rol, funcion
            FROM responsables
            ORDER BY id
        """)

        return jsonify(datos)

    @app.get("/api/auditorias")
    def auditorias():
        datos = consultar("""
            SELECT
                id,
                tipo,
                fundamento_normativo,
                objetivo,
                estado
            FROM auditorias
            ORDER BY id
        """)

        return jsonify(datos)

    @app.get("/api/no-conformidades")
    def no_conformidades():
        datos = consultar("""
            SELECT
                n.id,
                n.codigo,
                n.descripcion,
                n.numeral_iso,
                n.causa_probable,
                n.prioridad,
                n.estado,
                a.tipo AS auditoria,
                r.rol AS responsable
            FROM no_conformidades n
            INNER JOIN auditorias a
                ON n.auditoria_id = a.id
            INNER JOIN responsables r
                ON n.responsable_id = r.id
            ORDER BY n.id
        """)

        return jsonify(datos)

    @app.get("/api/indicadores")
    def indicadores():
        datos = obtener_indicadores(
            app.config["DATABASE"]
        )

        return jsonify(datos)

    @app.get("/api/acciones-pdca")
    def acciones_pdca():
        datos = consultar("""
            SELECT
                p.id,
                n.codigo AS no_conformidad,
                p.fase,
                p.accion,
                p.plazo,
                p.criterio_eficacia,
                p.evidencia,
                p.estado,
                r.rol AS responsable
            FROM acciones_pdca p
            INNER JOIN no_conformidades n
                ON p.no_conformidad_id = n.id
            INNER JOIN responsables r
                ON p.responsable_id = r.id
            ORDER BY n.id, p.id
        """)

        return jsonify(datos)

    @app.get("/api/resumen")
    def resumen():
        datos = consultar("""
            SELECT
                (SELECT COUNT(*) FROM auditorias)
                    AS auditorias,
                (SELECT COUNT(*) FROM responsables)
                    AS responsables,
                (SELECT COUNT(*) FROM no_conformidades)
                    AS no_conformidades,
                (SELECT COUNT(*) FROM no_conformidades
                    WHERE estado = 'Abierta')
                    AS no_conformidades_abiertas,
                (SELECT COUNT(*) FROM acciones_pdca)
                    AS acciones_pdca
        """)[0]

        indicadores = obtener_indicadores(
            app.config["DATABASE"]
        )

        evaluados = [
            item for item in indicadores
            if item["ultima_medicion"] is not None
        ]

        cumplidos = sum(
            1 for item in evaluados
            if item["ultima_medicion"]["estado"] == "Cumple"
        )

        datos["indicadores"] = len(indicadores)
        datos["indicadores_evaluados"] = len(evaluados)
        datos["indicadores_cumplidos"] = cumplidos
        datos["indicadores_fuera_meta"] = (
            len(evaluados) - cumplidos
        )
        datos["origen_mediciones"] = "Simulado"

        return jsonify(datos)

    @app.errorhandler(404)
    def recurso_no_encontrado(error):
        return jsonify({
            "error": "Recurso no encontrado",
            "codigo": 404,
        }), 404

    return app


app = crear_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False,
    )
