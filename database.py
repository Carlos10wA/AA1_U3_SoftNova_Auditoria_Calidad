
import sqlite3
from contextlib import closing
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "softnova.db"


def conectar(db_path=DB_PATH):
    conexion = sqlite3.connect(db_path)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def inicializar_db(db_path=DB_PATH):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    with closing(conectar(db_path)) as conexion:
        conexion.executescript("""
            CREATE TABLE IF NOT EXISTS responsables (
                id INTEGER PRIMARY KEY,
                rol TEXT NOT NULL UNIQUE,
                funcion TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS auditorias (
                id INTEGER PRIMARY KEY,
                tipo TEXT NOT NULL UNIQUE,
                fundamento_normativo TEXT NOT NULL,
                objetivo TEXT NOT NULL,
                estado TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS no_conformidades (
                id INTEGER PRIMARY KEY,
                codigo TEXT NOT NULL UNIQUE,
                auditoria_id INTEGER NOT NULL,
                responsable_id INTEGER NOT NULL,
                descripcion TEXT NOT NULL,
                numeral_iso TEXT NOT NULL,
                causa_probable TEXT NOT NULL,
                prioridad TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'Abierta',
                FOREIGN KEY (auditoria_id)
                    REFERENCES auditorias(id),
                FOREIGN KEY (responsable_id)
                    REFERENCES responsables(id)
            );

            CREATE TABLE IF NOT EXISTS indicadores (
                id INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL UNIQUE,
                formula TEXT NOT NULL,
                responsable_id INTEGER NOT NULL,
                meta REAL NOT NULL,
                sentido TEXT NOT NULL
                    CHECK (sentido IN ('Mayor', 'Menor')),
                periodicidad TEXT NOT NULL,
                fuente TEXT NOT NULL,
                FOREIGN KEY (responsable_id)
                    REFERENCES responsables(id)
            );

            CREATE TABLE IF NOT EXISTS mediciones (
                id INTEGER PRIMARY KEY,
                indicador_id INTEGER NOT NULL,
                sprint INTEGER NOT NULL CHECK (sprint > 0),
                numerador INTEGER NOT NULL CHECK (numerador >= 0),
                denominador INTEGER NOT NULL CHECK (denominador > 0),
                origen TEXT NOT NULL DEFAULT 'Simulado',
                UNIQUE (indicador_id, sprint),
                FOREIGN KEY (indicador_id)
                    REFERENCES indicadores(id)
            );

            CREATE TABLE IF NOT EXISTS acciones_pdca (
                id INTEGER PRIMARY KEY,
                no_conformidad_id INTEGER NOT NULL,
                responsable_id INTEGER NOT NULL,
                fase TEXT NOT NULL CHECK (
                    fase IN (
                        'Planificar', 'Hacer',
                        'Verificar', 'Actuar'
                    )
                ),
                accion TEXT NOT NULL,
                plazo TEXT NOT NULL,
                criterio_eficacia TEXT NOT NULL,
                evidencia TEXT NOT NULL DEFAULT 'Pendiente',
                estado TEXT NOT NULL DEFAULT 'Propuesta',
                FOREIGN KEY (no_conformidad_id)
                    REFERENCES no_conformidades(id),
                FOREIGN KEY (responsable_id)
                    REFERENCES responsables(id)
            );
        """)

        conexion.commit()


if __name__ == "__main__":
    inicializar_db()
    print("Base de datos SoftNova creada correctamente.")

    with closing(conectar()) as conexion:
        tablas = conexion.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
        """).fetchall()

        print("\nTablas creadas:")
        for tabla in tablas:
            print(f" - {tabla['name']}")

        integridad = conexion.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0]

        print(f"\nIntegridad de la base de datos: {integridad}")
        print(f"Ubicacion: {DB_PATH}")
