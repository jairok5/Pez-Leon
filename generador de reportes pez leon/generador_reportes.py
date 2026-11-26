"""
report_generator.py
Generador de reportes HTML con IA para la base bibliométrica del pez león (CICY).

Qué hace:
  1. Lee la configuración del archivo .env (conexión a MySQL y clave de Claude).
  2. Consulta las vistas y procedimientos de pez_leon_bibliometria con pandas.
  3. Genera las gráficas con matplotlib (quedan incrustadas dentro del HTML).
  4. Manda un resumen de las estadísticas a Claude y recibe el análisis escrito.
  5. Arma un HTML autocontenido con Jinja2 y lo abre en el navegador.

Uso:
  python report_generator.py              reporte completo (con análisis de IA)
  python report_generator.py --sin-ia     solo estadísticas y gráficas
  python report_generator.py --no-abrir   no abre el navegador al terminar
"""

from __future__ import annotations

import argparse
import base64
import io
import os
import sys
import time
import webbrowser
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # dibuja las gráficas sin abrir ventanas

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import MaxNLocator
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine
from sqlalchemy.exc import SQLAlchemyError

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# ----------------------------------------------------------------------
# Configuración (se puede cambiar en el archivo .env)
# ----------------------------------------------------------------------
MODELO_CLAUDE = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
# Precio en USD por millón de tokens (entrada, salida), según la página de precios de Claude (nov. 2026)
PRECIOS_USD = {"claude-sonnet-5-5": (2.00, 10.00), "claude-haiku-5-5": (0.10, 0.50)}
INSTITUCION_FOCO = os.getenv("INSTITUCION_FOCO", "CICY")  # se busca en nombre o afiliación
PAIS_RESALTADO = "MEX"       # país que se resalta en la gráfica de países
ANIO_INICIO_GRAFICAS = 2000  # antes de este año hay muy pocas publicaciones
CARPETA_SALIDA = BASE_DIR / "reportes"

# Paleta de colores (validada para personas con daltonismo)
AZUL = "#2a78d6"
NARANJA = "#eb6834"
AZUL_TENUE = "#9ec5f4"     # año incompleto
GRIS_CONTEXTO = "#c3c2b7"  # barras de contexto cuando se resalta una
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
TINTA_TENUE = "#898781"
REJILLA = "#e1e0d9"
RAMPA_AZUL = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#2a78d6", "#1c5cab", "#104281", "#0d366b"]

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


# ----------------------------------------------------------------------
# 1. Base de datos
# ----------------------------------------------------------------------
def conectar() -> Engine:
    """Crea la conexión a MySQL con los datos del archivo .env y la prueba."""
    url = URL.create(
        "mysql+pymysql",
        username=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "pez_leon_bibliometria"),
        query={"charset": "utf8mb4"},
    )
    engine = create_engine(url)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return engine


def consultar(engine: Engine, sql: str, **params) -> pd.DataFrame:
    """Ejecuta una consulta (o un CALL a un procedimiento) y la regresa como DataFrame."""
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or None)


def cargar_datos(engine: Engine) -> dict:
    """Lee todo lo que necesita el reporte. Solo usa las vistas y procedimientos de la base."""
    q = lambda sql, **p: consultar(engine, sql, **p)
    return {
        "kpis": q("CALL sp_kpis_generales()").iloc[0].to_dict(),
        "carga": q("SELECT * FROM carga ORDER BY fecha_carga DESC LIMIT 1").iloc[0].to_dict(),
        "anual": q("SELECT * FROM v_resumen_anual ORDER BY anio"),
        "quinquenio": q("SELECT * FROM v_resumen_quinquenio ORDER BY anio_inicio"),
        "tipos": q("SELECT * FROM v_resumen_tipo_documento ORDER BY publicaciones DESC"),
        "temas": q("SELECT * FROM v_resumen_tema ORDER BY publicaciones DESC"),
        "tema_quinquenio": q("SELECT * FROM v_tema_quinquenio"),
        "paises": q("SELECT * FROM v_resumen_pais ORDER BY publicaciones DESC, citas_totales DESC"),
        "regiones": q("SELECT * FROM v_resumen_region ORDER BY publicaciones DESC"),
        "colaboracion": q("SELECT * FROM v_resumen_colaboracion ORDER BY anio_inicio"),
        "instituciones": q("CALL sp_top_por_parametro('institucion', 10)"),
        "autores": q("CALL sp_top_por_parametro('autor', 10)"),
        "fuentes": q("CALL sp_top_por_parametro('fuente', 10)"),
        "mas_citadas": q("CALL sp_top_por_parametro('citas', 10)"),
        "palabras": q("CALL sp_top_por_parametro('palabra_clave', 15)"),
        "acceso": q("SELECT * FROM v_resumen_acceso_abierto"),
        "idiomas": q("SELECT * FROM v_resumen_idioma ORDER BY publicaciones DESC"),
        "mexico_inst": q("SELECT * FROM v_resumen_institucion_mexico "
                         "ORDER BY publicaciones DESC, citas_totales DESC LIMIT 10"),
        "mexico_pubs": q("SELECT anio, titulo, fuente, primer_autor, paises, citas, url_doi "
                         "FROM v_publicaciones_mexico ORDER BY anio DESC, citas DESC"),
        "foco": q("CALL sp_publicaciones_institucion(:patron)", patron=INSTITUCION_FOCO),
    }


def fecha_larga(f) -> str:
    return f"{f.day} de {MESES[f.month - 1]} de {f.year}"


def contexto(datos: dict) -> dict:
    """Datos de contexto: fecha de los datos y si el último año está incompleto."""
    fecha = pd.Timestamp(datos["kpis"]["fecha_datos"])
    anio_final = int(datos["kpis"]["anio_final"])
    incompleto = anio_final == fecha.year and (fecha.month, fecha.day) != (12, 31)
    return {
        "fecha_datos": fecha,
        "fecha_datos_txt": fecha_larga(fecha),
        "anio_final": anio_final,
        "anio_incompleto": anio_final if incompleto else None,
        "generado": datetime.now(),
    }


def etiqueta_quinquenio(inicio: int, ctx: dict) -> str:
    """'2015–2019', o '2025–2026*' si el periodo todavía no termina."""
    fin = min(inicio + 4, ctx["anio_final"])
    parcial = fin < inicio + 4 or ctx["anio_incompleto"] == fin
    return f"{inicio}–{fin}" + ("*" if parcial else "")


# ----------------------------------------------------------------------
# 2. Gráficas (matplotlib -> PNG incrustado en el HTML)
# ----------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "text.color": TINTA,
    "axes.labelcolor": TINTA_2,
    "xtick.color": TINTA_2,
    "ytick.color": TINTA_2,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
})


def a_imagen(fig) -> dict:
    """Convierte la figura en una imagen PNG (base64) lista para el HTML."""
    ancho_px = int(fig.get_figwidth() * 96)  # tamaño con el que se muestra en pantalla
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=192, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    codigo = base64.b64encode(buffer.getvalue()).decode("ascii")
    return {"src": f"data:image/png;base64,{codigo}", "ancho": ancho_px}


def limpiar_ejes(ax, base: str = "bottom") -> None:
    """Quita el marco: deja solo la línea base y sin marcas de los ejes."""
    for lado in ("top", "right", "left", "bottom"):
        ax.spines[lado].set_visible(lado == base)
    ax.spines[base].set_color(GRIS_CONTEXTO)
    ax.tick_params(length=0)


def grafica_anual(anual: pd.DataFrame, ctx: dict) -> dict | None:
    """Columnas: publicaciones por año (el año incompleto va en un tono más claro)."""
    if anual.empty:
        return None
    desde = max(ANIO_INICIO_GRAFICAS, int(anual["anio"].min()))
    hasta = int(anual["anio"].max())
    serie = (anual.set_index("anio")["publicaciones"]
                  .reindex(range(desde, hasta + 1), fill_value=0))
    colores = [AZUL] * len(serie)
    if ctx["anio_incompleto"] == hasta:
        colores[-1] = AZUL_TENUE

    fig, ax = plt.subplots(figsize=(9, 3.2))
    ax.bar(serie.index, serie.values, width=0.68, color=colores, zorder=2)
    ax.yaxis.grid(True, color=REJILLA, linewidth=0.8, zorder=0)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=5))
    limpiar_ejes(ax)
    ax.set_xticks(range(desde, hasta + 1, 2))
    ax.set_xlim(desde - 0.7, hasta + 0.7)
    pico = int(serie.idxmax())
    ax.annotate(f"{serie[pico]}", (pico, serie[pico]), xytext=(0, 3),
                textcoords="offset points", ha="center", va="bottom", fontsize=9)
    return a_imagen(fig)


def grafica_temas(temas: pd.DataFrame) -> dict | None:
    """Barras horizontales: publicaciones por tema de investigación."""
    t = temas[temas["tema"] != "Sin clasificar"].sort_values("publicaciones")
    if t.empty:
        return None
    fig, ax = plt.subplots(figsize=(9, 0.36 * len(t) + 0.3))
    ax.barh(t["tema"].tolist(), t["publicaciones"], height=0.62, color=AZUL)
    tope = t["publicaciones"].max()
    for i, (n, pct) in enumerate(zip(t["publicaciones"], t["pct_publicaciones"])):
        ax.text(n + tope * 0.012, i, f"{n}  ({pct:.1f} %)", va="center", fontsize=9, color=TINTA_2)
    ax.set_xlim(0, tope * 1.22)
    ax.set_ylim(-0.6, len(t) - 0.4)
    ax.set_xticks([])
    limpiar_ejes(ax, base="left")
    ax.tick_params(axis="y", labelsize=10, labelcolor=TINTA)
    return a_imagen(fig)


def grafica_temas_quinquenio(tq: pd.DataFrame, orden: list, ctx: dict) -> tuple[dict | None, pd.DataFrame]:
    """Mapa de calor: publicaciones por tema y quinquenio (más oscuro = más publicaciones)."""
    tq = tq[tq["anio_inicio"] >= ANIO_INICIO_GRAFICAS]
    if tq.empty:
        return None, pd.DataFrame()
    tabla = tq.pivot_table(index="tema", columns="anio_inicio", values="publicaciones",
                           aggfunc="sum", fill_value=0)
    tabla = tabla.reindex([t for t in orden if t in tabla.index])
    tabla.columns = [etiqueta_quinquenio(int(c), ctx) for c in tabla.columns]
    valores = tabla.to_numpy()
    tope = valores.max()

    # celdas en cero: gris muy claro, para distinguir "nada" de "poco"
    mapa = LinearSegmentedColormap.from_list("azules", RAMPA_AZUL).with_extremes(bad="#f3f2ee")
    fig, ax = plt.subplots(figsize=(9, 0.38 * len(tabla) + 0.6))
    ax.imshow(np.ma.masked_equal(valores, 0), cmap=mapa, vmin=0, vmax=tope, aspect="auto")
    for i in range(valores.shape[0]):
        for j in range(valores.shape[1]):
            v = valores[i, j]
            color = "white" if v >= tope * 0.55 else (TINTA_TENUE if v == 0 else TINTA)
            ax.text(j, i, f"{v}" if v else "–", ha="center", va="center", fontsize=9, color=color)
    ax.set_xticks(range(valores.shape[1]), tabla.columns)
    ax.set_yticks(range(valores.shape[0]), tabla.index.tolist())
    ax.xaxis.tick_top()
    ax.set_xticks(np.arange(valores.shape[1] + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(valores.shape[0] + 1) - 0.5, minor=True)
    ax.grid(which="minor", color="white", linewidth=2)  # separación entre celdas
    ax.tick_params(which="both", length=0)
    ax.tick_params(axis="y", labelcolor=TINTA)
    for lado in ax.spines.values():
        lado.set_visible(False)
    return a_imagen(fig), tabla


def grafica_paises(paises: pd.DataFrame, n: int = 15) -> dict | None:
    """Barras horizontales: países de afiliación (el país foco va resaltado)."""
    top = paises.head(n).iloc[::-1]
    if top.empty:
        return None
    colores = [AZUL if str(iso) == PAIS_RESALTADO else GRIS_CONTEXTO for iso in top["iso3"]]
    fig, ax = plt.subplots(figsize=(9, 0.36 * len(top) + 0.3))
    ax.barh(top["pais"].tolist(), top["publicaciones"], height=0.62, color=colores)
    tope = top["publicaciones"].max()
    for i, (n_pub, pct) in enumerate(zip(top["publicaciones"], top["pct_publicaciones"])):
        ax.text(n_pub + tope * 0.012, i, f"{n_pub}  ({pct:.1f} %)", va="center", fontsize=9, color=TINTA_2)
    ax.set_xlim(0, tope * 1.2)
    ax.set_ylim(-0.6, len(top) - 0.4)
    ax.set_xticks([])
    limpiar_ejes(ax, base="left")
    ax.tick_params(axis="y", labelsize=10, labelcolor=TINTA)
    return a_imagen(fig)


def grafica_colaboracion(colab: pd.DataFrame, ctx: dict) -> dict | None:
    """Columnas apiladas: colaboración nacional vs. internacional por quinquenio."""
    c = colab[colab["anio_inicio"] >= ANIO_INICIO_GRAFICAS].reset_index(drop=True)
    if c.empty:
        return None
    x = np.arange(len(c))
    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    ax.bar(x, c["nacional"], width=0.32, color=AZUL, edgecolor="white", linewidth=1.5,
           label="Nacional (autores de un solo país)", zorder=2)
    ax.bar(x, c["internacional"], bottom=c["nacional"], width=0.32, color=NARANJA,
           edgecolor="white", linewidth=1.5, label="Internacional (dos o más países)", zorder=2)
    for xi, fila in c.iterrows():
        alto = fila["nacional"] + fila["internacional"]
        ax.annotate(f"{fila['pct_internacional']:.0f} %", (xi, alto), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=9, color=TINTA_2)
    ax.set_xticks(x, [etiqueta_quinquenio(int(a), ctx) for a in c["anio_inicio"]])
    ax.yaxis.grid(True, color=REJILLA, linewidth=0.8, zorder=0)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=5))
    ax.set_ylim(0, (c["nacional"] + c["internacional"]).max() * 1.15)
    limpiar_ejes(ax)
    ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.02), ncol=2, fontsize=9,
              borderaxespad=0, handlelength=1.2)  # leyenda arriba, fuera del área de datos
    return a_imagen(fig)


def generar_graficas(datos: dict, ctx: dict) -> dict:
    orden_temas = datos["temas"].loc[datos["temas"]["tema"] != "Sin clasificar", "tema"].tolist()
    mapa_calor, tabla_tq = grafica_temas_quinquenio(datos["tema_quinquenio"], orden_temas, ctx)
    datos["pivote_temas"] = tabla_tq  # se reutiliza en la tabla del reporte y en el prompt
    return {
        "anual": grafica_anual(datos["anual"], ctx),
        "temas": grafica_temas(datos["temas"]),
        "temas_quinquenio": mapa_calor,
        "paises": grafica_paises(datos["paises"]),
        "colaboracion": grafica_colaboracion(datos["colaboracion"], ctx),
    }


# ----------------------------------------------------------------------
# 3. Análisis con IA (una sola llamada a Claude)
# ----------------------------------------------------------------------
INSTRUCCIONES_SISTEMA = (
    "Eres un analista de bibliometría que redacta reportes para investigadores del Centro de "
    "Investigación Científica de Yucatán (CICY) que estudian al pez león (Pterois volitans), "
    "especie invasora en el Gran Caribe. Escribes en español de México, con tono técnico pero claro."
)


def _csv(df: pd.DataFrame, columnas: list | None = None) -> str:
    """Tabla en formato CSV; los conteos que MySQL regresa como 13831.0 se escriben como 13831."""
    if columnas:
        df = df[[c for c in columnas if c in df.columns]]
    df = df.copy()
    for columna in df.select_dtypes("float").columns:
        if (df[columna].dropna() % 1 == 0).all():
            df[columna] = df[columna].astype("Int64")
    return df.to_csv(index=False, float_format="%.1f").strip()


def resumen_para_ia(d: dict, ctx: dict) -> str:
    """Convierte las tablas del reporte en un texto compacto (CSV) para Claude."""
    kpis = {k: (int(v) if isinstance(v, float) and v.is_integer() else v) for k, v in d["kpis"].items()}
    bloques = {
        "Indicadores generales": "\n".join(f"{k}: {v}" for k, v in kpis.items()),
        "Publicaciones por año": _csv(d["anual"], ["anio", "publicaciones", "citas_totales", "pct_acceso_abierto"]),
        "Por quinquenio": _csv(d["quinquenio"], ["quinquenio", "publicaciones", "citas_promedio",
                                                 "pct_acceso_abierto", "pct_colaboracion_internacional"]),
        "Tipos de documento": _csv(d["tipos"], ["tipo_documento", "publicaciones", "pct_publicaciones", "citas_promedio"]),
        "Temas (asignados por reglas; un artículo puede tener varios)":
            _csv(d["temas"], ["tema", "publicaciones", "pct_publicaciones", "citas_promedio", "primer_anio"]),
        f"Temas por quinquenio desde {ANIO_INICIO_GRAFICAS} (publicaciones)": d["pivote_temas"].to_csv().strip(),
        "Países de afiliación, top 15 (conteo completo)":
            _csv(d["paises"].head(15), ["pais", "region", "publicaciones", "pct_publicaciones",
                                         "como_pais_primer_autor", "citas_promedio", "primer_anio"]),
        "Regiones": _csv(d["regiones"], ["region", "paises", "publicaciones", "pct_publicaciones", "citas_promedio"]),
        "Colaboración por quinquenio": _csv(d["colaboracion"], ["quinquenio", "nacional", "internacional",
                                                                "sin_afiliacion", "pct_internacional"]),
        "Instituciones top 10": _csv(d["instituciones"], ["institucion", "pais", "publicaciones",
                                                          "citas_totales", "primer_anio", "ultimo_anio"]),
        "Autores top 10 (índice h calculado solo con este corpus)":
            _csv(d["autores"], ["autor", "publicaciones", "como_primer_autor", "citas_totales",
                                "indice_h_corpus", "primer_anio", "ultimo_anio"]),
        "Revistas top 10": _csv(d["fuentes"], ["fuente", "publicaciones", "citas_totales", "citas_promedio"]),
        "Publicaciones más citadas": _csv(d["mas_citadas"], ["posicion", "titulo", "anio", "fuente",
                                                              "pais_primer_autor", "citas", "citas_por_anio"]),
        "Palabras clave de autor más usadas (sin términos genéricos)":
            _csv(d["palabras"], ["termino", "como_palabra_autor", "publicaciones", "primer_anio", "ultimo_anio"]),
        "Acceso abierto": _csv(d["acceso"]),
        "Idiomas": _csv(d["idiomas"]),
        "Instituciones mexicanas top 10": _csv(d["mexico_inst"], ["institucion", "publicaciones",
                                                                  "citas_totales", "primer_anio", "ultimo_anio"]),
        f"Publicaciones con participación de {INSTITUCION_FOCO}": _csv(d["foco"], ["anio", "titulo", "fuente", "citas"]),
    }
    return "\n\n".join(f"### {titulo}\n{contenido}" for titulo, contenido in bloques.items())


def analizar_con_ia(datos: dict, ctx: dict) -> tuple[dict | None, str]:
    """Pide a Claude el análisis escrito. Regresa (analisis, motivo si no se pudo)."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        return None, "no hay ANTHROPIC_API_KEY en el archivo .env"
    try:
        import anthropic
        from pydantic import BaseModel, Field
    except ImportError:
        return None, "falta instalar el paquete anthropic (pip install -r requirements.txt)"

    class AnalisisReporte(BaseModel):
        resumen_ejecutivo: str = Field(description="Un párrafo de 4 a 6 oraciones con lo más importante del corpus.")
        hallazgos: list[str] = Field(description="De 3 a 5 hallazgos clave, una oración cada uno, con cifras.")
        produccion: str = Field(description="Evolución de las publicaciones por año y quinquenio.")
        temas: str = Field(description="Temas dominantes, cuáles crecen o decrecen por quinquenio y cuáles tienen más citas.")
        geografia: str = Field(description="Países y regiones de afiliación, liderazgo como primer autor y colaboración internacional.")
        actores: str = Field(description="Instituciones y autores más productivos y más citados.")
        impacto: str = Field(description="Citas, revistas, publicaciones más citadas, acceso abierto e idiomas.")
        palabras_clave: str = Field(description="Qué revelan las palabras clave de autor más usadas.")
        mexico: str = Field(description=f"Participación de México, sus instituciones y {INSTITUCION_FOCO}.")
        vacios: list[str] = Field(description="De 2 a 4 temas o enfoques poco estudiados que podrían ser "
                                              "oportunidades de investigación, justificados con los datos.")

    anio_incompleto = (f"- El año {ctx['anio_incompleto']} está incompleto (datos al {ctx['fecha_datos_txt']}); "
                       "no lo interpretes como una caída.\n") if ctx["anio_incompleto"] else ""
    instrucciones = (
        "Con base ÚNICAMENTE en las estadísticas de abajo, redacta el análisis del reporte bibliométrico.\n\n"
        "Reglas:\n"
        "- Usa solo cifras que aparezcan en los datos; no inventes números, tendencias ni causas. "
        "Si propones una explicación, preséntala como posibilidad.\n"
        "- 'País' es el país de la institución de los autores (afiliación), no el sitio donde se estudió al pez.\n"
        "- Los porcentajes por país, región y tema no suman 100 % porque una publicación puede contar en varios.\n"
        f"{anio_incompleto}"
        "- Las publicaciones recientes tienen menos citas porque han tenido menos tiempo para acumularlas.\n"
        "- Cada sección es un párrafo de 3 a 5 oraciones, sin viñetas ni formato Markdown.\n\n"
        f"DATOS\n\n{resumen_para_ia(datos, ctx)}"
    )

    try:
        cliente = anthropic.Anthropic(timeout=180)
        respuesta = cliente.messages.parse(
            model=MODELO_CLAUDE,
            max_tokens=6000,
            system=INSTRUCCIONES_SISTEMA,
            messages=[{"role": "user", "content": instrucciones}],
            output_format=AnalisisReporte,
        )
    except anthropic.AuthenticationError:
        return None, "la clave ANTHROPIC_API_KEY no es válida"
    except anthropic.NotFoundError:
        return None, f"el modelo '{MODELO_CLAUDE}' no está disponible (revisa CLAUDE_MODEL en .env)"
    except anthropic.APIConnectionError:
        return None, "no se pudo conectar con la API de Claude (revisa tu conexión a internet)"
    except Exception as error:  # límite de uso, saldo insuficiente, respuesta inválida, etc.
        return None, f"la llamada a Claude falló ({error.__class__.__name__}: {error})"

    if respuesta.stop_reason == "max_tokens" or respuesta.parsed_output is None:
        return None, f"Claude no completó la respuesta (stop_reason={respuesta.stop_reason})"
        uso = respuesta.usage
    precio = PRECIOS_USD.get(MODELO_CLAUDE)
    costo = (uso.input_tokens * precio[0] + uso.output_tokens * precio[1]) / 1_000_000 if precio else None
    print(f"      Claude usó {uso.input_tokens:,} tokens de entrada y {uso.output_tokens:,} de salida"
          + (f" (costo aproximado: {costo:.4f} USD)." if costo is not None else "."))
    return respuesta.parsed_output.model_dump(), ""


# ----------------------------------------------------------------------
# 4. HTML (Jinja2)
# ----------------------------------------------------------------------
def entero(v) -> str:
    return "–" if pd.isna(v) else f"{int(round(float(v))):,}"


def decimal1(v) -> str:
    return "–" if pd.isna(v) else f"{float(v):,.1f}"


def porcentaje(v) -> str:
    return "–" if pd.isna(v) else f"{float(v):.1f} %"


FORMATOS = {
    "texto": lambda v: "–" if pd.isna(v) else str(v),
    "nombre": lambda v: "–" if pd.isna(v) else str(v),  # como texto, pero sin partir la línea
    "anio": lambda v: "–" if pd.isna(v) else str(int(v)),
    "entero": entero,
    "decimal": decimal1,
    "pct": porcentaje,
}
CLASE_CSS = {"entero": "num", "decimal": "num", "pct": "num", "nombre": "nw"}


def tabla(df: pd.DataFrame, columnas: list[tuple[str, str, str]]) -> dict:
    """Prepara una tabla para la plantilla. columnas = [(columna, encabezado, formato), ...]"""
    encabezados = [(encabezado, CLASE_CSS.get(formato, "")) for _, encabezado, formato in columnas]
    filas = []
    for _, registro in df.iterrows():
        fila = []
        for columna, _, formato in columnas:
            valor = registro.get(columna)
            if formato == "enlace":
                url = None if pd.isna(valor) else str(valor)
                fila.append({"texto": "Ver" if url else "–", "url": url, "clase": ""})
            else:
                fila.append({"texto": FORMATOS[formato](valor), "url": None, "clase": CLASE_CSS.get(formato, "")})
        filas.append(fila)
    return {"encabezados": encabezados, "filas": filas}


def preparar_tablas(d: dict, ctx: dict) -> dict:
    pivote = d["pivote_temas"].reset_index().rename(columns={"index": "tema"})
    quinquenios = d["quinquenio"].assign(
        quinquenio=[etiqueta_quinquenio(int(a), ctx) for a in d["quinquenio"]["anio_inicio"]])
    colaboracion = d["colaboracion"].assign(
        quinquenio=[etiqueta_quinquenio(int(a), ctx) for a in d["colaboracion"]["anio_inicio"]])
    return {
        "anual": tabla(d["anual"], [("anio", "Año", "anio"), ("publicaciones", "Publicaciones", "entero"),
                                    ("publicaciones_acumuladas", "Acumuladas", "entero"),
                                    ("citas_totales", "Citas", "entero"),
                                    ("pct_acceso_abierto", "Acceso abierto", "pct")]),
        "quinquenio": tabla(quinquenios, [("quinquenio", "Quinquenio", "nombre"),
                                              ("publicaciones", "Publicaciones", "entero"),
                                              ("citas_promedio", "Citas promedio", "decimal"),
                                              ("pct_acceso_abierto", "Acceso abierto", "pct"),
                                              ("pct_colaboracion_internacional", "Colab. internacional", "pct")]),
        "tipos": tabla(d["tipos"], [("tipo_documento", "Tipo de documento", "texto"),
                                    ("publicaciones", "Publicaciones", "entero"),
                                    ("pct_publicaciones", "% del total", "pct"),
                                    ("citas_promedio", "Citas promedio", "decimal")]),
        "temas": tabla(d["temas"], [("tema", "Tema", "texto"), ("descripcion", "Qué incluye", "texto"),
                                    ("publicaciones", "Publicaciones", "entero"),
                                    ("pct_publicaciones", "% del total", "pct"),
                                    ("citas_promedio", "Citas promedio", "decimal"),
                                    ("primer_anio", "Desde", "anio")]),
        "temas_quinquenio": tabla(pivote, [("tema", "Tema", "texto")] +
                                  [(c, c, "entero") for c in pivote.columns if c != "tema"]),
        "paises": tabla(d["paises"], [("pais", "País", "texto"), ("region", "Región", "texto"),
                                      ("publicaciones", "Publicaciones", "entero"),
                                      ("pct_publicaciones", "% del total", "pct"),
                                      ("como_pais_primer_autor", "Como primer autor", "entero"),
                                      ("citas_promedio", "Citas promedio", "decimal")]),
        "regiones": tabla(d["regiones"], [("region", "Región", "texto"), ("paises", "Países", "entero"),
                                          ("publicaciones", "Publicaciones", "entero"),
                                          ("pct_publicaciones", "% del total", "pct"),
                                          ("citas_promedio", "Citas promedio", "decimal")]),
        "colaboracion": tabla(colaboracion, [("quinquenio", "Quinquenio", "nombre"),
                                                  ("nacional", "Nacional", "entero"),
                                                  ("internacional", "Internacional", "entero"),
                                                  ("sin_afiliacion", "Sin afiliación", "entero"),
                                                  ("pct_internacional", "% internacional", "pct")]),
        "instituciones": tabla(d["instituciones"], [("institucion", "Institución", "texto"), ("pais", "País", "texto"),
                                                    ("publicaciones", "Publicaciones", "entero"),
                                                    ("citas_totales", "Citas", "entero"),
                                                    ("primer_anio", "Desde", "anio"), ("ultimo_anio", "Hasta", "anio")]),
        "autores": tabla(d["autores"], [("autor", "Autor", "nombre"), ("publicaciones", "Publicaciones", "entero"),
                                        ("como_primer_autor", "Como primer autor", "entero"),
                                        ("citas_totales", "Citas", "entero"),
                                        ("indice_h_corpus", "Índice h*", "entero")]),
        "fuentes": tabla(d["fuentes"], [("fuente", "Revista o fuente", "texto"),
                                        ("publicaciones", "Publicaciones", "entero"),
                                        ("citas_totales", "Citas", "entero"),
                                        ("citas_promedio", "Citas promedio", "decimal")]),
        "mas_citadas": tabla(d["mas_citadas"], [("posicion", "#", "anio"), ("titulo", "Título", "texto"),
                                                ("anio", "Año", "anio"), ("primer_autor", "Primer autor", "nombre"),
                                                ("citas", "Citas", "entero"), ("citas_por_anio", "Citas por año", "decimal"),
                                                ("url_doi", "DOI", "enlace")]),
        "palabras": tabla(d["palabras"], [("termino", "Palabra clave", "texto"),
                                          ("como_palabra_autor", "Como palabra de autor", "entero"),
                                          ("publicaciones", "Total (autor + índice)", "entero"),
                                          ("primer_anio", "Desde", "anio")]),
        "acceso": tabla(d["acceso"], [("categoria", "Categoría", "texto"), ("modalidad", "Modalidad", "texto"),
                                      ("publicaciones", "Publicaciones", "entero"),
                                      ("pct_publicaciones", "% del total", "pct")]),
        "idiomas": tabla(d["idiomas"], [("idioma", "Idioma", "texto"), ("publicaciones", "Publicaciones", "entero"),
                                        ("pct_publicaciones", "% del total", "pct")]),
        "mexico_inst": tabla(d["mexico_inst"], [("institucion", "Institución", "texto"),
                                                ("publicaciones", "Publicaciones", "entero"),
                                                ("citas_totales", "Citas", "entero"),
                                                ("primer_anio", "Desde", "anio"), ("ultimo_anio", "Hasta", "anio")]),
        "mexico_pubs": tabla(d["mexico_pubs"], [("anio", "Año", "anio"), ("titulo", "Título", "texto"),
                                                ("primer_autor", "Primer autor", "nombre"), ("paises", "Países", "texto"),
                                                ("citas", "Citas", "entero"), ("url_doi", "DOI", "enlace")]),
        "foco": tabla(d["foco"], [("anio", "Año", "anio"), ("titulo", "Título", "texto"),
                                  ("fuente", "Revista", "texto"), ("citas", "Citas", "entero")]),
    }


def indicadores(d: dict) -> list[tuple[str, str, str]]:
    """Las tarjetas de la portada: (etiqueta, valor, detalle)."""
    k = d["kpis"]
    total = float(k["total_publicaciones"]) or 1
    con_mexico = float(k["publicaciones_con_mexico"])
    return [
        ("Publicaciones", entero(k["total_publicaciones"]), f"{int(k['anio_inicial'])}–{int(k['anio_final'])}"),
        ("Citas totales", entero(k["citas_totales"]),
         f"Promedio {decimal1(k['citas_promedio'])} · mediana {entero(k['citas_mediana'])}"),
        ("Autores únicos", entero(k["autores_unicos"]), f"{entero(k['fuentes'])} revistas y otras fuentes"),
        ("Países de afiliación", entero(k["paises"]), f"{entero(k['instituciones'])} instituciones"),
        ("Acceso abierto", porcentaje(k["pct_acceso_abierto"]), "de las publicaciones"),
        ("Colaboración internacional", porcentaje(k["pct_colaboracion_internacional"]),
         "autores de dos o más países"),
        ("Con participación de México", entero(con_mexico), f"{porcentaje(100 * con_mexico / total)} del total"),
        (f"Con participación de {INSTITUCION_FOCO}", entero(len(d["foco"])), "según la afiliación de sus autores"),
    ]


def generar_html(d: dict, ctx: dict, graficas: dict, analisis: dict | None, motivo_sin_ia: str) -> Path:
    entorno = Environment(loader=FileSystemLoader(BASE_DIR / "templates"),
                          autoescape=select_autoescape(["html"]))
    anual = d["anual"]
    previas = anual[anual["anio"] < ANIO_INICIO_GRAFICAS]
    html = entorno.get_template("reporte.html").render(
        ctx=ctx,
        carga=d["carga"],
        indicadores=indicadores(d),
        graficas=graficas,
        tablas=preparar_tablas(d, ctx),
        ia=analisis or {},
        motivo_sin_ia=motivo_sin_ia,
        modelo=MODELO_CLAUDE,
        institucion_foco=INSTITUCION_FOCO,
        anio_inicio=ANIO_INICIO_GRAFICAS,
        previas_n=int(previas["publicaciones"].sum()),
        previas_rango=(f"{int(previas['anio'].min())}–{int(previas['anio'].max())}" if len(previas) else ""),
        sin_clasificar=int(d["temas"].loc[d["temas"]["tema"] == "Sin clasificar", "publicaciones"].sum()),
        metodos_tema=", ".join(sorted({m for ms in d["temas"]["metodos"].dropna() for m in str(ms).split(",")})),
        generado_txt=f"{fecha_larga(ctx['generado'])}, {ctx['generado']:%H:%M}",
    )
    CARPETA_SALIDA.mkdir(exist_ok=True)
    sufijo = "con_ia" if analisis else "sin_ia"  # así un reporte no reemplaza al otro
    ruta = CARPETA_SALIDA / f"reporte_pez_leon_{ctx['generado']:%Y-%m-%d_%H%M}_{sufijo}.html"
    ruta.write_text(html, encoding="utf-8")
    return ruta


# ----------------------------------------------------------------------
# Programa principal
# ----------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Genera el reporte HTML de la base bibliométrica del pez león.")
    parser.add_argument("--sin-ia", action="store_true", help="no llama a Claude; solo estadísticas y gráficas")
    parser.add_argument("--no-abrir", action="store_true", help="no abre el reporte en el navegador")
    args = parser.parse_args()
    inicio = time.perf_counter()

    print("[1/5] Conectando a MySQL...")
    try:
        engine = conectar()
    except SQLAlchemyError as error:
        print(f"\nNo pude conectarme a la base de datos:\n  {getattr(error, 'orig', error)}\n"
              "Revisa DB_HOST, DB_PORT, DB_USER, DB_PASSWORD y DB_NAME en el archivo .env")
        sys.exit(1)

    print("[2/5] Leyendo vistas y procedimientos...")
    try:
        datos = cargar_datos(engine)
    except SQLAlchemyError as error:
        print(f"\nFalló una consulta:\n  {getattr(error, 'orig', error)}\n"
              "Verifica que ejecutaste el script SQL completo (tablas, datos, vistas y procedimientos) "
              "y que el usuario tiene permisos SELECT y EXECUTE.")
        sys.exit(1)
    ctx = contexto(datos)

    print("[3/5] Generando gráficas...")
    graficas = generar_graficas(datos, ctx)

    if args.sin_ia:
        print("[4/5] Análisis con IA omitido (--sin-ia).")
        analisis, motivo = None, "se ejecutó con la opción --sin-ia"
    else:
        print(f"[4/5] Pidiendo el análisis a Claude ({MODELO_CLAUDE})...")
        analisis, motivo = analizar_con_ia(datos, ctx)
        if analisis is None:
            print(f"      Aviso: el reporte saldrá sin análisis de IA porque {motivo}.")

    print("[5/5] Armando el HTML...")
    ruta = generar_html(datos, ctx, graficas, analisis, motivo)
    print(f"\nListo en {time.perf_counter() - inicio:.1f} s. Reporte: {ruta}")
    if not args.no_abrir:
        webbrowser.open(ruta.as_uri())


if __name__ == "__main__":
    main()