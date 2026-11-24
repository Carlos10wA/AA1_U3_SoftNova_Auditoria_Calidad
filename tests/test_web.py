
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait


@pytest.fixture(scope="module")
def navegador():
    """Inicializa Google Chrome para pruebas funcionales."""
    opciones = Options()
    opciones.add_argument("--headless=new")
    opciones.add_argument("--window-size=1920,1080")
    opciones.add_argument("--disable-extensions")

    driver = webdriver.Chrome(options=opciones)
    driver.set_page_load_timeout(30)

    try:
        yield driver
    finally:
        driver.quit()


@pytest.fixture
def pagina(navegador):
    """Carga el tablero antes de cada prueba."""
    navegador.get("http://127.0.0.1:5000/")

    WebDriverWait(navegador, 20).until(
        lambda driver: "Mostrando 20 de 20"
        in driver.find_element(
            By.ID, "contador-acciones"
        ).text
    )

    return navegador


def obtener_filas(driver, identificador):
    return driver.find_elements(
        By.CSS_SELECTOR, f"#{identificador} tr"
    )


def test_acceso_sistema(pagina):
    assert "SoftNova" in pagina.title

    estado = pagina.find_element(
        By.ID, "estado-sistema"
    ).text

    assert "Sistema Operativo" in estado
    assert "Integridad SQLite: ok" in estado
    assert "Errores referenciales: 0" in estado


def test_aviso_simulacion_academica(pagina):
    aviso = pagina.find_element(
        By.CLASS_NAME, "aviso"
    ).text

    assert "Simulación académica" in aviso
    assert "simuladas" in aviso
    assert "no acredita una certificación ISO" in aviso


def test_ausencia_errores_interfaz(pagina):
    mensaje = pagina.find_element(
        By.ID, "mensaje-error"
    )

    assert not mensaje.is_displayed()


@pytest.mark.parametrize(
    "identificador, esperado",
    [
        ("total-auditorias", "4"),
        ("total-no-conformidades", "5"),
        ("total-fuera-meta", "3"),
        ("total-acciones", "20"),
        ("total-responsables", "5"),
    ],
)
def test_panel_ejecutivo(
    pagina, identificador, esperado
):
    elemento = pagina.find_element(
        By.ID, identificador
    )

    assert elemento.text == esperado


@pytest.mark.parametrize(
    "seccion",
    [
        "inicio",
        "auditorias",
        "no-conformidades",
        "indicadores",
        "pdca",
        "responsables",
        "informe",
    ],
)
def test_navegacion_secciones(pagina, seccion):
    enlace = pagina.find_element(
        By.CSS_SELECTOR,
        f'nav a[href="#{seccion}"]'
    )

    enlace.click()

    WebDriverWait(pagina, 10).until(
        lambda driver: driver.current_url.endswith(
            f"#{seccion}"
        )
    )

    assert pagina.find_element(
        By.ID, seccion
    ).is_displayed()


def test_tabla_auditorias(pagina):
    filas = obtener_filas(
        pagina, "cuerpo-auditorias"
    )

    assert len(filas) == 4

    contenido = " ".join(
        fila.text.lower() for fila in filas
    )

    for tipo in (
        "interna",
        "externa",
        "certificaci",
        "seguimiento",
    ):
        assert tipo in contenido


def test_tabla_no_conformidades(pagina):
    filas = obtener_filas(
        pagina, "cuerpo-no-conformidades"
    )

    assert len(filas) == 5

    codigos = {
        fila.find_elements(By.TAG_NAME, "td")[0].text
        for fila in filas
    }

    assert codigos == {
        "NC-01",
        "NC-02",
        "NC-03",
        "NC-04",
        "NC-05",
    }


def test_tarjetas_indicadores(pagina):
    tarjetas = pagina.find_elements(
        By.CSS_SELECTOR,
        "#contenedor-indicadores .indicador-card"
    )

    assert len(tarjetas) == 3

    for tarjeta, codigo in zip(
        tarjetas,
        ["KPI-01", "KPI-02", "KPI-03"]
    ):
        assert codigo in tarjeta.text
        assert "Responsable:" in tarjeta.text
        assert "Meta:" in tarjeta.text
        assert "Fuente de datos:" in tarjeta.text


def test_resultados_actuales_indicadores(pagina):
    valores = pagina.find_elements(
        By.CSS_SELECTOR,
        "#contenedor-indicadores .indicador-valor"
    )

    assert [valor.text for valor in valores] == [
        "10 defectos/100 historias",
        "85%",
        "75%",
    ]


def test_graficas_indicadores(pagina):
    graficas = pagina.find_elements(
        By.CSS_SELECTOR,
        "#contenedor-indicadores svg"
    )

    assert len(graficas) == 3

    for grafica in graficas:
        assert grafica.is_displayed()

        puntos = grafica.find_elements(
            By.CSS_SELECTOR, "circle"
        )

        assert len(puntos) == 3

        assert grafica.find_elements(
            By.CSS_SELECTOR, "polyline"
        )

        assert grafica.find_elements(
            By.CSS_SELECTOR,
            "line[stroke-dasharray]"
        )


def test_historial_mediciones(pagina):
    tablas = pagina.find_elements(
        By.CSS_SELECTOR,
        ".tabla-mediciones"
    )

    assert len(tablas) == 3

    for tabla in tablas:
        filas = tabla.find_elements(
            By.CSS_SELECTOR, "tbody tr"
        )

        assert len(filas) == 3

        for numero, fila in enumerate(
            filas, start=1
        ):
            assert f"Sprint {numero}" in fila.text


def test_plan_phva_completo(pagina):
    filas = obtener_filas(
        pagina, "cuerpo-pdca"
    )

    assert len(filas) == 20

    assert "Mostrando 20 de 20" in (
        pagina.find_element(
            By.ID, "contador-acciones"
        ).text
    )


@pytest.mark.parametrize(
    "fase",
    ["Planificar", "Hacer", "Verificar", "Actuar"],
)
def test_filtro_por_fase(pagina, fase):
    selector = Select(
        pagina.find_element(
            By.ID, "filtro-fase"
        )
    )

    selector.select_by_value(fase)

    filas = obtener_filas(
        pagina, "cuerpo-pdca"
    )

    assert len(filas) == 5

    for fila in filas:
        celdas = fila.find_elements(
            By.TAG_NAME, "td"
        )

        assert celdas[1].text == fase


def test_filtro_por_hallazgo(pagina):
    Select(
        pagina.find_element(
            By.ID, "filtro-nc"
        )
    ).select_by_value("NC-04")

    filas = obtener_filas(
        pagina, "cuerpo-pdca"
    )

    assert len(filas) == 4

    for fila in filas:
        celdas = fila.find_elements(
            By.TAG_NAME, "td"
        )

        assert celdas[0].text == "NC-04"


def test_filtros_combinados_phva(pagina):
    Select(
        pagina.find_element(
            By.ID, "filtro-fase"
        )
    ).select_by_value("Verificar")

    Select(
        pagina.find_element(
            By.ID, "filtro-nc"
        )
    ).select_by_value("NC-04")

    filas = obtener_filas(
        pagina, "cuerpo-pdca"
    )

    assert len(filas) == 1

    celdas = filas[0].find_elements(
        By.TAG_NAME, "td"
    )

    assert celdas[0].text == "NC-04"
    assert celdas[1].text == "Verificar"

    assert "Mostrando 1 de 20" in (
        pagina.find_element(
            By.ID, "contador-acciones"
        ).text
    )



def test_limpiar_filtros(pagina):
    Select(
        pagina.find_element(
            By.ID, "filtro-fase"
        )
    ).select_by_value("Verificar")

    Select(
        pagina.find_element(
            By.ID, "filtro-nc"
        )
    ).select_by_value("NC-04")

    assert len(
        obtener_filas(pagina, "cuerpo-pdca")
    ) == 1

    boton = pagina.find_element(
        By.ID, "limpiar-filtros"
    )

    pagina.execute_script(
        "arguments[0].scrollIntoView("
        "{block: 'center', behavior: 'instant'});",
        boton
    )

    WebDriverWait(pagina, 10).until(
        lambda driver: driver.execute_script(
            """
            const boton = arguments[0];
            const rect = boton.getBoundingClientRect();
            const elemento = document.elementFromPoint(
                rect.left + rect.width / 2,
                rect.top + rect.height / 2
            );
            return elemento === boton ||
                boton.contains(elemento);
            """,
            boton
        )
    )

    boton.click()

    WebDriverWait(pagina, 10).until(
        lambda driver: len(
            obtener_filas(driver, "cuerpo-pdca")
        ) == 20
    )

    for identificador in (
        "filtro-fase", "filtro-nc"
    ):
        seleccionado = Select(
            pagina.find_element(
                By.ID, identificador
            )
        ).first_selected_option

        assert seleccionado.get_attribute(
            "value"
        ) == "Todas"

    assert "Mostrando 20 de 20" in (
        pagina.find_element(
            By.ID, "contador-acciones"
        ).text
    )


def test_tabla_responsables(pagina):
    filas = obtener_filas(
        pagina, "cuerpo-responsables"
    )

    assert len(filas) == 5

    for fila in filas:
        celdas = fila.find_elements(
            By.TAG_NAME, "td"
        )

        assert len(celdas) == 3
        assert celdas[1].text.strip()
        assert celdas[2].text.strip()


def test_informe_ejecutivo(pagina):
    diagnostico = pagina.find_element(
        By.ID, "diagnostico-ejecutivo"
    ).text

    assert "5 no conformidades abiertas" in diagnostico
    assert "3 indicadores fuera de meta" in diagnostico
    assert "20 acciones de mejora" in diagnostico

    informe = pagina.find_element(
        By.ID, "informe"
    )

    assert len(
        informe.find_elements(
            By.CLASS_NAME, "metodo"
        )
    ) == 4

    assert len(
        informe.find_elements(
            By.CSS_SELECTOR, "ol li"
        )
    ) == 5

