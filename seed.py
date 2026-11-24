
from contextlib import closing

from database import DB_PATH, conectar, inicializar_db


def cargar_datos(db_path=DB_PATH):
    inicializar_db(db_path)

    responsables = [
        (1, "Director de calidad",
         "Aprobar el sistema de gestión y asignar responsabilidades."),
        (2, "Líder de calidad",
         "Gestionar auditorías, indicadores y no conformidades."),
        (3, "Analista QA",
         "Diseñar, ejecutar y documentar pruebas de software."),
        (4, "Líder de desarrollo",
         "Gestionar defectos y fortalecer la cobertura del código."),
        (5, "Auditor interno",
         "Evaluar objetivamente la conformidad y eficacia de las mejoras."),
    ]

    auditorias = [
        (
            1,
            "Interna",
            "ISO 9001:2015, numeral 9.2",
            ("Evaluar el cumplimiento del sistema de gestión de calidad "
            "e identificar no conformidades."),
            "Realizada según el caso",
        ),
        (
            2,
            "Externa",
            "ISO 19011:2018, directrices de auditoría",
            ("Proponer una evaluación independiente por parte "
            "del cliente u otra organización externa."),
            "Propuesta",
        ),
        (
            3,
            "Certificación",
            "ISO 9001:2015 e ISO/IEC 17021-1:2015",
            ("Evaluar la conformidad del sistema mediante "
            "un organismo certificador competente."),
            "Propuesta futura",
        ),
        (
            4,
            "Seguimiento",
            "ISO 9001:2015, numerales 9.2 y 10.2",
            ("Verificar la implementación y eficacia de las "
            "acciones correctivas."),
            "Planificada",
        ),
    ]

    no_conformidades = [
        (
            1, "NC-01", 1, 1,
            "Ausencia de responsables definidos.",
            "5.3",
            "Posible falta de definición formal de roles y autoridades.",
            "Alta", "Abierta",
        ),
        (
            2, "NC-02", 1, 2,
            "Falta de seguimiento a los indicadores de producto.",
            "9.1.1 y 9.1.3",
            "Posible ausencia de un procedimiento de medición periódica.",
            "Alta", "Abierta",
        ),
        (
            3, "NC-03", 1, 2,
            "Poca trazabilidad de las no conformidades.",
            "7.5 y 10.2.2",
            "Posible ausencia de un registro centralizado de hallazgos.",
            "Alta", "Abierta",
        ),
        (
            4, "NC-04", 1, 4,
            "Duplicación de la tasa de defectos en los últimos tres sprints.",
            "9.1.3 y 10.2",
            "Posibles deficiencias en las pruebas y controles de calidad.",
            "Crítica", "Abierta",
        ),
        (
            5, "NC-05", 1, 2,
            "Ausencia de registros documentados de acciones correctivas.",
            "10.2.2",
            "Posible falta de procedimientos documentados de seguimiento.",
            "Alta", "Abierta",
        ),
    ]

    indicadores = [
        (
            1,
            "Tasa de defectos por sprint",
            "(Defectos confirmados / Historias evaluadas) x 100",
            2, 5.0, "Menor", "Cada sprint",
            "Registro de defectos e historias de usuario",
        ),
        (
            2,
            "Tasa de aprobación de pruebas",
            "(Pruebas aprobadas / Pruebas ejecutadas) x 100",
            3, 95.0, "Mayor", "Cada sprint",
            "Informes de ejecución de pruebas automatizadas",
        ),
        (
            3,
            "Cobertura de sentencias",
            "(Sentencias ejecutadas / Sentencias totales) x 100",
            4, 95.0, "Mayor", "Cada sprint",
            "Informes generados mediante Coverage.py",
        ),
    ]

    # Datos exclusivamente simulados con fines académicos.
    mediciones = [
        (1, 1, 1, 2, 40, "Simulado"),
        (2, 1, 2, 3, 40, "Simulado"),
        (3, 1, 3, 4, 40, "Simulado"),
        (4, 2, 1, 95, 100, "Simulado"),
        (5, 2, 2, 90, 100, "Simulado"),
        (6, 2, 3, 85, 100, "Simulado"),
        (7, 3, 1, 85, 100, "Simulado"),
        (8, 3, 2, 80, 100, "Simulado"),
        (9, 3, 3, 75, 100, "Simulado"),
    ]

    acciones = [
        # NC-01: Responsabilidades.
        (1, 1, 1, "Planificar",
         "Identificar roles, autoridades y responsabilidades.",
         "Día 1", "Matriz de responsabilidades diseñada."),

        (2, 1, 1, "Hacer",
         "Aprobar y comunicar la matriz RACI al equipo.",
         "Día 3", "100% de los roles asignados y comunicados."),

        (3, 1, 5, "Verificar",
         "Comprobar que cada actividad tenga un responsable.",
         "Día 7", "100% de actividades con responsable definido."),

        (4, 1, 1, "Actuar",
         "Actualizar responsabilidades ante cambios organizacionales.",
         "Cada sprint", "Matriz de responsabilidades vigente."),

        # NC-02: Seguimiento de indicadores.
        (5, 2, 2, "Planificar",
         "Definir indicadores, fórmulas, metas y responsables.",
         "Día 2", "Tres fichas de indicadores completas."),

        (6, 2, 3, "Hacer",
         "Implementar el tablero de seguimiento por sprint.",
         "Día 5", "Tres indicadores disponibles en el tablero."),

        (7, 2, 5, "Verificar",
         "Contrastar cálculos y registros con las fuentes.",
         "Cada sprint", "100% de mediciones verificadas."),

        (8, 2, 2, "Actuar",
         "Establecer revisión periódica y alertas por desviación.",
         "Cada sprint", "100% de desviaciones analizadas."),

        # NC-03: Trazabilidad.
        (9, 3, 2, "Planificar",
         "Definir los campos del registro de no conformidades.",
         "Día 2", "Formato de registro aprobado."),

        (10, 3, 4, "Hacer",
         "Implementar un registro centralizado con códigos únicos.",
         "Día 5", "100% de hallazgos identificados y registrados."),

        (11, 3, 5, "Verificar",
         "Revisar la relación entre hallazgos, responsables y acciones.",
         "Día 10", "100% de hallazgos con acciones trazables."),

        (12, 3, 2, "Actuar",
         "Estandarizar el registro y establecer controles periódicos.",
         "Cada sprint", "Ningún hallazgo nuevo sin registro."),

        # NC-04: Incremento de defectos.
        (13, 4, 4, "Planificar",
         "Analizar causas mediante los cinco porqués y los datos disponibles.",
         "Día 2", "Causas verificadas y defectos priorizados."),

        (14, 4, 3, "Hacer",
         "Ampliar pruebas de API, interfaz y regresión.",
         "Día 10", "Casos críticos cubiertos por pruebas."),

        (15, 4, 5, "Verificar",
         "Medir defectos, aprobación de pruebas y cobertura.",
         "Próximos 2 sprints",
         "Defectos <= 5 por 100 historias; pruebas y cobertura >= 95%."),

        (16, 4, 4, "Actuar",
         "Incorporar pruebas de regresión y controles antes de liberar.",
         "Cada sprint", "Metas sostenidas durante dos sprints."),

        # NC-05: Acciones correctivas.
        (17, 5, 2, "Planificar",
         "Definir el procedimiento de acciones correctivas.",
         "Día 2", "Procedimiento documentado y aprobado."),

        (18, 5, 2, "Hacer",
         "Registrar acciones, responsables, plazos y evidencias.",
         "Día 5", "100% de acciones formalmente registradas."),

        (19, 5, 5, "Verificar",
         "Evaluar la eficacia antes de cerrar cada no conformidad.",
         "Día 15", "Ningún cierre sin evidencia de eficacia."),

        (20, 5, 1, "Actuar",
         "Actualizar procedimientos y compartir lecciones aprendidas.",
         "Cada sprint", "Revisión de reincidencias documentada."),
    ]

    with closing(conectar(db_path)) as conexion, conexion:
        conexion.executemany("""
                INSERT INTO responsables
                (id, rol, funcion)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO NOTHING
            """, responsables)

        conexion.executemany("""
                INSERT INTO auditorias
                (id, tipo, fundamento_normativo, objetivo, estado)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO NOTHING
            """, auditorias)

        conexion.executemany("""
                INSERT INTO no_conformidades
                (id, codigo, auditoria_id, responsable_id,
                 descripcion, numeral_iso, causa_probable,
                 prioridad, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO NOTHING
            """, no_conformidades)

        conexion.executemany("""
                INSERT INTO indicadores
                (id, nombre, formula, responsable_id,
                 meta, sentido, periodicidad, fuente)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO NOTHING
            """, indicadores)

        conexion.executemany("""
                INSERT INTO mediciones
                (id, indicador_id, sprint, numerador,
                 denominador, origen)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO NOTHING
            """, mediciones)

        conexion.executemany("""
                INSERT INTO acciones_pdca
                (id, no_conformidad_id, responsable_id,
                 fase, accion, plazo, criterio_eficacia)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO NOTHING
            """, acciones)


def verificar_datos(db_path=DB_PATH):
    consultas = {
        "Responsables": "SELECT COUNT(*) FROM responsables",
        "Auditorias": "SELECT COUNT(*) FROM auditorias",
        "No conformidades": "SELECT COUNT(*) FROM no_conformidades",
        "Indicadores": "SELECT COUNT(*) FROM indicadores",
        "Mediciones": "SELECT COUNT(*) FROM mediciones",
        "Acciones PDCA": "SELECT COUNT(*) FROM acciones_pdca",
    }

    print("=" * 55)
    print("SOFTNOVA S.A.S. - SISTEMA DE GESTION DE CALIDAD")
    print("=" * 55)

    with closing(conectar(db_path)) as conexion:
        total = 0

        for nombre, consulta in consultas.items():
            cantidad = conexion.execute(consulta).fetchone()[0]
            total += cantidad
            print(f"{nombre:<25}: {cantidad}")

        integridad = conexion.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0]

        errores_fk = conexion.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        print("-" * 55)
        print(f"Total de registros: {total}")
        print(f"Integridad SQLite: {integridad}")
        print(f"Errores de claves foraneas: {len(errores_fk)}")
        print("Mediciones: SIMULADAS CON FINES ACADEMICOS")
        print("=" * 55)


if __name__ == "__main__":
    cargar_datos()
    verificar_datos()
