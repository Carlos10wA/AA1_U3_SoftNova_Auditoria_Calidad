
"use strict";

/* =========================================
   SOFTNOVA S.A.S.
   Sistema de Gestion de Calidad
   Unidad 3 - Actividad AA1
   ========================================= */

let accionesPDCA = [];

const formatoNumero = new Intl.NumberFormat("es-CO", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
});

/* FUNCIONES GENERALES */

function elemento(id) {
    return document.getElementById(id);
}

function crearNodo(tipo, contenido = "", clase = "") {
    const nodo = document.createElement(tipo);

    nodo.textContent = contenido;

    if (clase) {
        nodo.className = clase;
    }

    return nodo;
}

function normalizarClase(texto) {
    return String(texto)
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-");
}

function crearEtiqueta(texto) {
    const valor = texto || "Sin registrar";

    return crearNodo(
        "span",
        valor,
        `etiqueta ${normalizarClase(valor)}`
    );
}

function mostrarError(error) {
    const mensaje = elemento("mensaje-error");

    mensaje.textContent =
        `No fue posible completar la consulta: ${error.message}`;

    mensaje.hidden = false;
}

async function consultarAPI(ruta) {
    const respuesta = await fetch(ruta, {
        method: "GET",
        headers: {
            "Accept": "application/json"
        },
        cache: "no-store"
    });

    if (!respuesta.ok) {
        throw new Error(
            `${ruta} - HTTP ${respuesta.status}`
        );
    }

    return respuesta.json();
}

/* CONSTRUCCION SEGURA DE TABLAS */

function agregarFila(cuerpo, valores) {
    const fila = document.createElement("tr");

    valores.forEach(valor => {
        const celda = document.createElement("td");

        if (valor instanceof Node) {
            celda.appendChild(valor);
        } else {
            celda.textContent = valor ?? "Sin registrar";
        }

        fila.appendChild(celda);
    });

    cuerpo.appendChild(fila);
}

/* ESTADO DEL SISTEMA */

async function cargarEstadoSistema() {
    const estado = elemento("estado-sistema");

    try {
        const datos = await consultarAPI("/api/salud");

        estado.textContent =
            `Sistema ${datos.estado} | ` +
            `Integridad SQLite: ${datos.base_datos} | ` +
            `Errores referenciales: ${datos.errores_claves_foraneas}`;

        estado.className =
            `estado-sistema ${normalizarClase(datos.estado)}`;

    } catch (error) {
        estado.textContent =
            "Sistema no disponible o con problemas de integridad.";

        estado.className = "estado-sistema degradado";

        throw error;
    }
}

/* PANEL EJECUTIVO */

function mostrarResumen(datos) {
    elemento("total-auditorias").textContent =
        datos.auditorias;

    elemento("total-no-conformidades").textContent =
        datos.no_conformidades_abiertas;

    elemento("total-fuera-meta").textContent =
        datos.indicadores_fuera_meta;

    elemento("total-acciones").textContent =
        datos.acciones_pdca;

    elemento("total-responsables").textContent =
        datos.responsables;

    elemento("diagnostico-ejecutivo").textContent =
        `El diagnostico inicial registra ` +
        `${datos.no_conformidades_abiertas} no conformidades abiertas, ` +
        `${datos.indicadores_fuera_meta} indicadores fuera de meta ` +
        `y ${datos.acciones_pdca} acciones de mejora propuestas. ` +
        `Se requiere fortalecer el seguimiento, la trazabilidad ` +
        `y los controles preventivos mediante el ciclo PHVA.`;
}

/* CLASIFICACION DE AUDITORIAS */

function mostrarAuditorias(datos) {
    const cuerpo = elemento("cuerpo-auditorias");

    cuerpo.replaceChildren();

    datos.forEach(auditoria => {
        agregarFila(cuerpo, [
            auditoria.tipo,
            auditoria.fundamento_normativo,
            auditoria.objetivo,
            crearEtiqueta(auditoria.estado)
        ]);
    });
}

/* NO CONFORMIDADES */

function mostrarNoConformidades(datos) {
    const cuerpo = elemento("cuerpo-no-conformidades");

    cuerpo.replaceChildren();

    datos.forEach(hallazgo => {
        agregarFila(cuerpo, [
            hallazgo.codigo,
            hallazgo.descripcion,
            hallazgo.numeral_iso,
            hallazgo.causa_probable,
            hallazgo.responsable,
            crearEtiqueta(hallazgo.prioridad),
            crearEtiqueta(hallazgo.estado)
        ]);
    });
}

/* RESPONSABILIDADES */

function mostrarResponsables(datos) {
    const cuerpo = elemento("cuerpo-responsables");

    cuerpo.replaceChildren();

    datos.forEach(responsable => {
        agregarFila(cuerpo, [
            `ROL-${String(responsable.id).padStart(2, "0")}`,
            responsable.rol,
            responsable.funcion
        ]);
    });
}

/* GENERACION DE GRAFICAS SVG */

function crearSVG(tipo, atributos = {}) {
    const nodo = document.createElementNS(
        "http://www.w3.org/2000/svg",
        tipo
    );

    Object.entries(atributos).forEach(([clave, valor]) => {
        nodo.setAttribute(clave, valor);
    });

    return nodo;
}

function textoSVG(contenido, atributos) {
    const nodo = crearSVG("text", atributos);
    nodo.textContent = contenido;
    return nodo;
}

function generarGrafica(indicador) {
    const contenedor = crearNodo("div", "", "grafica");
    const datos = indicador.mediciones;

    if (!datos.length) {
        contenedor.textContent =
            "No existen mediciones disponibles.";

        return contenedor;
    }

    const ancho = 360;
    const alto = 220;

    const margen = {
        superior: 25,
        inferior: 45,
        izquierdo: 42,
        derecho: 25
    };

    const valores = datos.map(
        medicion => medicion.resultado
    );

    let maximo = indicador.id === 1
        ? Math.max(
            15,
            Math.ceil(
                Math.max(...valores, indicador.meta) / 5
            ) * 5
        )
        : 100;

    const anchoUtil =
        ancho - margen.izquierdo - margen.derecho;

    const altoUtil =
        alto - margen.superior - margen.inferior;

    function posicionX(indice) {
        if (datos.length === 1) {
            return margen.izquierdo + anchoUtil / 2;
        }

        return margen.izquierdo +
            (indice / (datos.length - 1)) * anchoUtil;
    }

    function posicionY(valor) {
        return margen.superior +
            altoUtil - (valor / maximo) * altoUtil;
    }

    const svg = crearSVG("svg", {
        viewBox: `0 0 ${ancho} ${alto}`,
        role: "img",
        "aria-label":
            `Grafica de ${indicador.nombre} por sprint`
    });

    const titulo = crearSVG("title");
    titulo.textContent = indicador.nombre;
    svg.appendChild(titulo);

    /* Cuadricula y escala vertical */

    for (let i = 0; i <= 5; i++) {
        const valor = (maximo / 5) * i;
        const y = posicionY(valor);

        svg.appendChild(crearSVG("line", {
            x1: margen.izquierdo,
            x2: ancho - margen.derecho,
            y1: y,
            y2: y,
            stroke: "#e2e8f0",
            "stroke-width": 1
        }));

        svg.appendChild(textoSVG(
            formatoNumero.format(valor),
            {
                x: margen.izquierdo - 8,
                y: y + 4,
                fill: "#64748b",
                "font-size": 10,
                "text-anchor": "end"
            }
        ));
    }

    /* Linea de referencia de la meta */

    const yMeta = posicionY(indicador.meta);

    svg.appendChild(crearSVG("line", {
        x1: margen.izquierdo,
        x2: ancho - margen.derecho,
        y1: yMeta,
        y2: yMeta,
        stroke: "#b91c1c",
        "stroke-width": 2,
        "stroke-dasharray": "6 4"
    }));

    /* Linea de resultados */

    const puntos = datos.map((medicion, indice) => {
        return `${posicionX(indice)},` +
            `${posicionY(medicion.resultado)}`;
    }).join(" ");

    svg.appendChild(crearSVG("polyline", {
        points: puntos,
        fill: "none",
        stroke: "#2563eb",
        "stroke-width": 3,
        "stroke-linejoin": "round"
    }));

    /* Puntos, valores y etiquetas */

    datos.forEach((medicion, indice) => {
        const x = posicionX(indice);
        const y = posicionY(medicion.resultado);

        const punto = crearSVG("circle", {
            cx: x,
            cy: y,
            r: 5,
            fill: medicion.estado === "Cumple"
                ? "#15803d"
                : "#b91c1c",
            stroke: "#ffffff",
            "stroke-width": 1.5
        });

        const detalle = crearSVG("title");

        detalle.textContent =
            `Sprint ${medicion.sprint}: ` +
            `${formatoNumero.format(medicion.resultado)} - ` +
            medicion.estado;

        punto.appendChild(detalle);
        svg.appendChild(punto);

        svg.appendChild(textoSVG(
            formatoNumero.format(medicion.resultado),
            {
                x: x,
                y: y - 12,
                fill: "#142b49",
                "font-size": 12,
                "font-weight": "bold",
                "text-anchor": "middle"
            }
        ));

        svg.appendChild(textoSVG(
            `Sprint ${medicion.sprint}`,
            {
                x: x,
                y: alto - 18,
                fill: "#64748b",
                "font-size": 11,
                "text-anchor": "middle"
            }
        ));
    });

    contenedor.appendChild(svg);

    const leyenda = crearNodo(
        "div", "", "leyenda-grafica"
    );

    const referenciaResultado = crearNodo("span");

    referenciaResultado.append(
        crearNodo("i", "", "linea-resultado"),
        document.createTextNode("Resultado")
    );

    const referenciaMeta = crearNodo("span");

    referenciaMeta.append(
        crearNodo("i", "", "linea-meta"),
        document.createTextNode("Meta")
    );

    leyenda.append(
        referenciaResultado,
        referenciaMeta
    );

    contenedor.appendChild(leyenda);

    return contenedor;
}

/* TARJETAS DE INDICADORES */

function agregarDetalle(contenedor, titulo, valor) {
    const parrafo = document.createElement("p");

    parrafo.append(
        crearNodo("strong", `${titulo}: `),
        document.createTextNode(String(valor))
    );

    contenedor.appendChild(parrafo);
}

function crearTarjetaIndicador(indicador) {
    const tarjeta = crearNodo(
        "article", "", "indicador-card"
    );

    const codigo =
        `KPI-${String(indicador.id).padStart(2, "0")}`;

    const unidad = indicador.id === 1
        ? " defectos/100 historias"
        : "%";

    const operador = indicador.sentido === "Mayor"
        ? "≥"
        : "≤";

    const ultima = indicador.ultima_medicion;

    tarjeta.appendChild(
        crearNodo(
            "h3",
            `${codigo}. ${indicador.nombre}`
        )
    );

    tarjeta.appendChild(
        crearNodo(
            "div",
            ultima
                ? `${formatoNumero.format(ultima.resultado)}${unidad}`
                : "Sin datos",
            "indicador-valor"
        )
    );

    tarjeta.appendChild(
        crearEtiqueta(
            ultima ? ultima.estado : "Sin datos"
        )
    );

    tarjeta.appendChild(
        crearNodo(
            "div",
            indicador.formula,
            "formula"
        )
    );

    agregarDetalle(
        tarjeta,
        "Responsable",
        indicador.responsable
    );

    agregarDetalle(
        tarjeta,
        "Meta",
        `${operador} ${indicador.meta}${unidad}`
    );

    agregarDetalle(
        tarjeta,
        "Periodicidad",
        indicador.periodicidad
    );

    agregarDetalle(
        tarjeta,
        "Fuente de datos",
        indicador.fuente
    );

    if (ultima) {
        const unidadDesviacion = indicador.id === 1
            ? " defectos/100 historias"
            : " puntos porcentuales";

        agregarDetalle(
            tarjeta,
            "Desviacion desfavorable",
            formatoNumero.format(ultima.desviacion) +
                unidadDesviacion
        );
    }

    tarjeta.appendChild(
        generarGrafica(indicador)
    );

    /* Tabla de mediciones historicas */

    const tabla = crearNodo(
        "table", "", "tabla-mediciones"
    );

    const encabezado = document.createElement("thead");

    const filaEncabezado = document.createElement("tr");

    ["Sprint", "Resultado", "Estado"].forEach(titulo => {
        filaEncabezado.appendChild(
            crearNodo("th", titulo)
        );
    });

    encabezado.appendChild(filaEncabezado);

    const cuerpo = document.createElement("tbody");

    indicador.mediciones.forEach(medicion => {
        agregarFila(cuerpo, [
            `Sprint ${medicion.sprint}`,
            `${formatoNumero.format(medicion.resultado)}` +
                (indicador.id === 1 ? "" : "%"),
            crearEtiqueta(medicion.estado)
        ]);
    });

    tabla.append(encabezado, cuerpo);
    tarjeta.appendChild(tabla);

    return tarjeta;
}

function mostrarIndicadores(datos) {
    const contenedor = elemento(
        "contenedor-indicadores"
    );

    contenedor.replaceChildren();

    datos.forEach(indicador => {
        contenedor.appendChild(
            crearTarjetaIndicador(indicador)
        );
    });
}

/* PLAN DE MEJORA PHVA */

function mostrarAccionesPDCA() {
    const fase = elemento("filtro-fase").value;
    const hallazgo = elemento("filtro-nc").value;

    const filtradas = accionesPDCA.filter(accion => {
        const cumpleFase =
            fase === "Todas" || accion.fase === fase;

        const cumpleHallazgo =
            hallazgo === "Todas" ||
            accion.no_conformidad === hallazgo;

        return cumpleFase && cumpleHallazgo;
    });

    const cuerpo = elemento("cuerpo-pdca");

    cuerpo.replaceChildren();

    filtradas.forEach(accion => {
        agregarFila(cuerpo, [
            accion.no_conformidad,
            accion.fase,
            accion.accion,
            accion.responsable,
            accion.plazo,
            accion.criterio_eficacia,
            accion.evidencia || "Pendiente de ejecucion",
            crearEtiqueta(accion.estado)
        ]);
    });

    elemento("contador-acciones").textContent =
        `Mostrando ${filtradas.length} de ` +
        `${accionesPDCA.length} acciones propuestas.`;

    if (!filtradas.length) {
        const fila = document.createElement("tr");
        const celda = crearNodo(
            "td",
            "No existen acciones para los filtros seleccionados."
        );

        celda.colSpan = 8;

        fila.appendChild(celda);
        cuerpo.appendChild(fila);
    }
}

/* EVENTOS DE LOS FILTROS */

function configurarFiltros() {
    elemento("filtro-fase").addEventListener(
        "change",
        mostrarAccionesPDCA
    );

    elemento("filtro-nc").addEventListener(
        "change",
        mostrarAccionesPDCA
    );

    elemento("limpiar-filtros").addEventListener(
        "click",
        () => {
            elemento("filtro-fase").value = "Todas";
            elemento("filtro-nc").value = "Todas";

            mostrarAccionesPDCA();
        }
    );
}

/* CARGA INTEGRAL DEL SISTEMA */

async function inicializarDashboard() {
    try {
        elemento("mensaje-error").hidden = true;

        configurarFiltros();

        await cargarEstadoSistema();

        const [
            resumen,
            auditorias,
            noConformidades,
            indicadores,
            acciones,
            responsables
        ] = await Promise.all([
            consultarAPI("/api/resumen"),
            consultarAPI("/api/auditorias"),
            consultarAPI("/api/no-conformidades"),
            consultarAPI("/api/indicadores"),
            consultarAPI("/api/acciones-pdca"),
            consultarAPI("/api/responsables")
        ]);

        mostrarResumen(resumen);
        mostrarAuditorias(auditorias);
        mostrarNoConformidades(noConformidades);
        mostrarIndicadores(indicadores);
        mostrarResponsables(responsables);

        accionesPDCA = acciones;

        mostrarAccionesPDCA();

        console.info(
            "SoftNova: tablero cargado correctamente."
        );

    } catch (error) {
        mostrarError(error);

        console.error(
            "SoftNova: error de inicializacion.",
            error
        );
    }
}

document.addEventListener(
    "DOMContentLoaded",
    inicializarDashboard
);
