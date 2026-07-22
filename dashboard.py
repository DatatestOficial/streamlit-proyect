import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import polars as pl
import base64
import datetime
from datetime import datetime
from zoneinfo import ZoneInfo
from babel.dates import format_date
from datetime import date
import json

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN INICIAL
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.get("authentication_status"):
    st.set_page_config(page_title="PROBIEN",page_icon="🌽",layout="wide")

else:
    st.set_page_config(page_title="PROBIEN",page_icon="🌽",layout="centered")

# ═══════════════════════════════════════════════════════════════════════════════
# Cerrar sesión
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    authenticator = st.session_state.authenticator
    st.markdown(f"""<span style="font-size: 18px;"> Hola, {st.session_state.get("name").title() if "name" in st.session_state else "Invitado"} </span>""", unsafe_allow_html=True)

    authenticator.logout("Cerrar sesión", "sidebar")
    if st.session_state.get("authentication_status") is None:
        st.stop()
        st.rerun()


# Colores institucionales
GUINDA = "#621132"
GUINDA_CLARO = "#9F2241"
DORADO = "#D4C19C"
VERDE = "#285C4D"
AMARILLO = "#745526"
VERDE_CLARO = "#3A7D6B"
CREMA = "#F5F1EB"

# Paleta institucional
PALETA_INSTITUCIONAL = ["#10312B", "#691C32", "#C29E5C", "#235B4E", "#9F2241", "#D4C19C", "#44546A", "#52492E", "#52492E", "#f8f4ed"]
CREMA = "#f8f4ed"
# Fuente institucional
FONT_FAMILY = "Noto Sans"
FONT_SIZE_AXIS = 20
FONT_SIZE_TITLE = 22

# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════════

# Función para que Streamlit acepte tus logos locales
def img_to_b64(path):
    with open(path, "rb") as f:
        return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

# Convertimos tus logos
l1, l2, l3 = img_to_b64("logo1.png"), img_to_b64("logo2.png"), img_to_b64("logo3.png")


# Inyectamos TU código adaptado (sin html/head/body para no romper Streamlit)
st.markdown(f"""
    <style>
        /* Ajuste para que Streamlit use TODO el ancho de tu pantalla */
        [data-testid="stAppViewBlockContainer"] {{
            max-width: 100% !important;
            padding: 5 !important;
        }}
        
        /* AQUÍ VA TU CSS ORIGINAL */
        .header-logos {{
            width: 100%;
            display: flex;
            justify-content: flex-end; /* Lo movemos a la derecha como pediste */
            align-items: center;
            padding: 5px;
            gap: 10px;
        }}

        .logo {{
            width: 30%; /* Ajusta el % para el tamaño responsivo */
            height: auto;
            object-fit: contain;
        }}

        h1, h3 {{ 
            font-family: 'Noto Sans', sans-serif; 
            text-align: left; /* Títulos alineados a la derecha */
            color: #333;
        }}
    </style>

    <header class="header-logos">
        <img src="{l1}" class="logo" style="max-width: 300px;">
        <img src="{l2}" class="logo" style="max-width: 250px;"> 
        <img src="{l3}" class="logo" style="max-width: 150px;"> 
    </header>

    <!-- 
    <h1>Producción para el Bienestar (PROBIEN) 2026</h1>
    <h3>Proceso de Actualización</h3>
    -->

""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TÍTULO Y FECHA
# ═══════════════════════════════════════════════════════════════════════════════
# Obtiene la fecha actual usando la zona horaria de CDMX
hoy = datetime.now(ZoneInfo("America/Mexico_City")).strftime("%d-%m-%Y")
# hoy = date.today().strftime("%d-%m-%Y")

def crear_barras(df_barras, titulo, colores_lista=None, height=480):
    if colores_lista is None:
        colores_lista = PALETA_INSTITUCIONAL

    # Ajusta los colores según la cantidad de categorías
    colores = colores_lista[:len(df_barras)]

    # df_barras = df_barras.copy() # Evita modificar el DataFrame original fuera de la función
    
    # # Mantiene la misma lógica de etiquetas con porcentaje
    # df_barras['Categoria_Etiqueta'] = df_barras.apply(
    #     lambda r: f"<b>{r['Categoria']}</b> <br>({r['Personas'] / df_barras['Personas'].sum() * 100:.2f}%)", axis=1
    # )
    
    # Creación del gráfico de barras
    fig = px.bar(
        df_barras,
        x="Categoria",
        y="Personas",
        color="Categoria", # Permite aplicar la secuencia de colores por categoría
        color_discrete_sequence=colores,
    )

    # Configuración de los trazos (barras)
    fig.update_traces(
        texttemplate='%{y:,.0f}', # Muestra el valor absoluto sobre/dentro de la barra
        textposition='outside', # Coloca el texto afuera para mejor lectura
        textfont=dict(size=18, family="Noto Sans Black", color=VERDE),
        cliponaxis=False, # Permite que las etiquetas se muestren incluso si salen del área del gráfico
        # textangle=-45, 
        hovertemplate=(
            "<b>%{x}</b>:<br>"          # Categoría y porcentaje
            "%{y:,.0f}<br>"     # Valor absoluto
            "<extra></extra>"
        ),
        marker=dict(line=dict(color='white', width=1)),
    )

    v_bargap = 0.6 if df_barras["Categoria"].nunique() <= 4 else 0.15

    # Configuración del diseño global
    fig.update_layout(
        bargap=v_bargap,
        hoverlabel=dict(
            font_size=18, font_family=FONT_FAMILY,
            bgcolor="white", font_color=VERDE, bordercolor=DORADO
        ),
        title=dict(
            text=titulo,
            font=dict(size=FONT_SIZE_TITLE, color=GUINDA, family=FONT_FAMILY),
            x=0.5, xanchor="center"
        ),
        legend=dict(
            font=dict(size=18, family=FONT_FAMILY),
            orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5,
            title=None # Elimina el título automático de la leyenda
        ),
        xaxis=dict(
            title=None, # Quita el título del eje X porque la etiqueta es clara
            tickfont=dict(size=14, family=FONT_FAMILY, color="Black"),
            tickangle=-45
        ),
        yaxis=dict(
            # SOLUCIÓN: El texto y su fuente ahora van estructurados correctamente aquí
            title=dict(
                text="Personas",
                font=dict(size=18, family=FONT_FAMILY, color=GUINDA)
            ),
            tickfont=dict(size=14, family=FONT_FAMILY),
            gridcolor="rgba(0,0,0,0.1)", # Línea de cuadrícula sutil
            range=[0, df_barras['Personas'].max() * 1.10],
        ),
        height=height,
        margin=dict(t=60, b=80, l=40, r=20),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)" # Fondo del gráfico transparente
    )

    return fig

def crear_dona(
    df,
    titulo="",
    colores_lista=None,
    height=580,
    font_size_labels=20,
    hole=0.45,
    add_text_center = True,
):
    """
    Dona con etiquetas internas.

    DataFrame esperado:
        Columna 0 -> Categoría
        Columna 1 -> Valor

    Ejemplos:
        df[['Sexo','Personas']]
        df[['Edad','Personas']]
        df[['Escolaridad','Personas']]
    """

    if df is None or df.empty or len(df.columns) < 2:
        return px.pie(title="Sin datos")

    if colores_lista is None:
        colores_lista = PALETA_INSTITUCIONAL

    df = df.iloc[:, :2].copy()

    col_categoria = df.columns[0]
    col_valor = df.columns[1]
    total = df[col_valor].sum()

    # Etiquetas de 3 líneas
    df["Etiqueta"] = df.apply(
        lambda r: (
            f"<b>{r[col_categoria]}</b><br>"
            f"({r[col_valor]/total:.1%})"
        ),
        axis=1,
    )

    fig = px.pie(
        df,
        values=col_valor,
        names="Etiqueta",
        hole=hole,
        color_discrete_sequence=colores_lista[:len(df)],
    )

    # Total central
    if add_text_center:
        fig.add_annotation(
            x=0.5,
            y=0.5,
            showarrow=False,
            text=f"<b>{total:,.0f}</b><br>personas",
            font=dict(
                size=FONT_SIZE_TITLE,
                color=GUINDA,
                family=FONT_FAMILY
            ),
        )

    fig.update_traces(
        textposition="inside",
        textinfo="value+percent",
        textfont=dict(
            size=font_size_labels,
            color="white",
            family=FONT_FAMILY,
        ),
        # insidetextorientation="horizontal",
        marker=dict(
            line=dict(
                color="white",
                width=2
            )
        ),
        customdata=df[[col_categoria]],
        hovertemplate=(
            "<b>%{customdata[0]}:</b><br>"
            "%{value:,.0f} personas<br>"
            "%{percent}"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        title=dict(
            text=titulo,
            x=0.5,
            xanchor="center",
            font=dict(
                size=FONT_SIZE_TITLE,
                color=GUINDA,
                family=FONT_FAMILY,
            ),
        ),
        hoverlabel=dict(
            font_size=font_size_labels,
            font_family=FONT_FAMILY,
            bgcolor="white",
            font_color=VERDE,
            bordercolor=DORADO,
        ),
        legend=dict(
            font=dict(
                size=20,
                family=FONT_FAMILY
            ),
            orientation="h",
            yanchor="top",
            y=-0.10,
            xanchor="center",
            x=0.5,
        ),
        height=height,
        margin=dict(
            t=70,
            b=60,
            l=20,
            r=20,
        ),
        showlegend=True,
        paper_bgcolor="rgba(0,0,0,0)",
        uniformtext_minsize=12,
    )

    return fig

def crear_barras_porcentaje(
    df: pd.DataFrame,
    col_x: str,
    col_color: str,
    col_valores: str = "Personas",
    titulo: str = "Avance",
    lista_colores: list = None,
    orden_ascendente: bool = True,
    invertir_apilado: bool = True,
    height = 680,
) -> go.Figure:

    # ----------------------------
    # VALIDACIÓN SEGURA
    # ----------------------------
    if not isinstance(df, pd.DataFrame) or df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"{titulo} (Sin datos disponibles)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig

    # ----------------------------
    # AGRUPACIÓN BASE
    # ----------------------------
    df_agrupado = (
        df.groupby([col_x, col_color], as_index=False)[col_valores]
        .sum()
    )
    # ----------------------------
    # PORCENTAJES
    # ----------------------------
    totales = df_agrupado.groupby(col_x)[col_valores].transform("sum")
    df_agrupado["Porcentaje"] = (df_agrupado[col_valores] / totales * 100).round(1)
    # ----------------------------
    # ORDEN CORRECTO (CLAVE)
    # ordenado por TOTAL REAL del valor (ej: Actualizados)
    # ----------------------------
    categorias_color = list(df_agrupado[col_color].unique())
    # depues de este se puede aplicar la lógica para invertir el orden de las categorias en barras
    orden_x = (
        df_agrupado[df_agrupado[col_color]==categorias_color[0]]
        .sort_values("Porcentaje", ascending=orden_ascendente)
    )[col_x].tolist()
    # ----------------------------
    # ORDEN DE CATEGORÍAS (STACK)
    # ----------------------------
    categorias = df_agrupado[col_color].unique().tolist()
    if invertir_apilado:
        categorias = categorias[::-1]

    # ----------------------------
    # PALETA DE COLORES
    # ----------------------------
    if lista_colores:
        color_map = {
            cat: lista_colores[i % len(lista_colores)]
            for i, cat in enumerate(categorias)
        }
    else:
        color_map = {
            cat: ["#235B4E", "#D4C19C", "#621132", "#3A7D6B"][i % 4]
            for i, cat in enumerate(categorias)
        }

    # ----------------------------
    # GRÁFICA
    # ----------------------------
    fig = px.bar(
        df_agrupado,
        x=col_x,
        y="Porcentaje",
        color=col_color,
        text=df_agrupado["Porcentaje"].map("{:.1f}%".format),
        color_discrete_map=color_map,
        category_orders={
            col_x: orden_x,
            col_color: categorias
        },
        barmode="stack",
    )

    # ----------------------------
    # ESTILO DE BARRAS
    # ----------------------------
    fig.update_traces(
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(size=22, color="white"),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "<b>Categoría:</b> %{customdata[1]}<br>"
            "<b>Cantidad:</b> %{customdata[0]:,.0f}<br>"
            "<b>Porcentaje:</b> %{y:.1f}%"
            "<extra></extra>"
        ),
        customdata=df_agrupado[[col_valores, col_color]].values
    )

    v_bargap = 0.6 if df_agrupado[col_x].nunique() <= 4 else 0.15

    # ----------------------------
    # DISEÑO INSTITUCIONAL
    # ----------------------------
    fig.update_layout(
        title=dict(
            text=f"<b>{titulo}</b>",
            font=dict(size=34, color="#621132")
        ),
        xaxis=dict(
            title="",
            tickangle=-35,
            tickfont=dict(size=18, family=FONT_FAMILY,color="black"),
        ),
        yaxis=dict(
            title=dict(
                text="Porcentaje (%)",
                font=dict(
                size=22,          # Tamaño del título
                family=FONT_FAMILY,
                color="black"
                ),
            ),
            range=[0, 110],
            ticksuffix="%",
            tickfont=dict(size=18, family=FONT_FAMILY,color="black"),
        ),
        legend=dict(
            title=dict(
                text=f"<b>{str(col_color).upper()}</b>",
                font=dict(size=18, color="black", family=FONT_FAMILY)
            ),
            # y=1.02, 
            orientation="h",
            y=-0.4,
            x=0.5,
            # yanchor="bottom",
            xanchor="center",
            font=dict(
                size=22,   # <- tamaño de No / Si
                family=FONT_FAMILY,
                color="black"
            ),
        ),
        bargap=v_bargap,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=80, b=120),
        # uniformtext_minsize=14,
        # uniformtext_mode="hide",
    )

    return fig

def separador(texto="", color=DORADO):
    if texto:
        st.markdown(f"""
            
                {texto}
            
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            
        """, unsafe_allow_html=True)

def grafica_cumsum(
    df,
    periodo="semana",
    n=5,
    titulo=None,
    color="#3A7D6B",
    fill_color="rgba(58,125,107,0.15)",
    titulo_color="#691C32",
    text_color="#691C32",
    text_size=18,
    height=430,
):

    # Agrupar y ordenar
    df_plot = (
        df.groupby(periodo, as_index=False)["Personas"]
          .sum()
          .sort_values(periodo)
    )

    # Acumulado histórico
    df_plot["Acumulado"] = df_plot["Personas"].cumsum()

    # Últimos n periodos
    df_plot = df_plot.tail(n)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_plot[periodo],
            y=df_plot["Acumulado"],
            mode="lines+markers+text",

            text=df_plot["Acumulado"].map("{:,.0f}".format),
            textposition="top center",
            cliponaxis=False,

            textfont=dict(
                size=text_size,
                color=text_color,
                family=FONT_FAMILY
            ),

            line=dict(
                color=color,
                width=3
            ),

            marker=dict(
                size=14,
                color=color,
                line=dict(
                    color="white",
                    width=2
                )
            ),

            fill="tozeroy",
            fillcolor=fill_color,

            customdata=df_plot["Personas"],

            hovertemplate=(
                "<b>%{x}</b><br>"
                "Acumulado: %{y:,.0f}<br>"
                "Periodo: %{customdata:,.0f} personas"
                "<extra></extra>"
            ),
        )
    )

    y_max = df_plot["Acumulado"].max()
    y_min = df_plot["Acumulado"].min()

    y_padding = (y_max - y_min) * 0.25  # 25% de aire arriba


    fig.update_layout(

        title=dict(
            text=titulo or f"Acumulado por {periodo.capitalize()}",
            font=dict(
                size=FONT_SIZE_TITLE,
                color=titulo_color,
                family=FONT_FAMILY
            ),
            x=0
        ),

        height=height,

        template="plotly_white",

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        margin=dict(l=60, r=60, t=45, b=20),

        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_family=FONT_FAMILY
        ),

        xaxis=dict(
            title=" ",
            tickangle=-45,
            showgrid=False,
            zeroline=False,
            showline=False,
            tickfont=dict(
                size=text_size,
                family=FONT_FAMILY
            )
        ),

        yaxis=dict(
            title="Personas acumuladas",
            gridcolor="rgba(0,0,0,.08)",
            gridwidth=1,
            range=[y_min, y_max + y_padding],
            autorange=False,
            zeroline=False,
            showline=False,
            visible=False,
            tickfont=dict(
                size=18,
                family=FONT_FAMILY
            )
        ),
    )

    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# LOGOS + ESTILOS CSS
# ═══════════════════════════════════════════════════════════════════════════════
    # 1. Inyectas el estilo CSS personalizado
st.markdown(f"""
    <style>
    div.stDownloadButton > button:first-child {{
        background-color: {VERDE_CLARO}; /* Tu color de fondo (Verde) */
        color: white;              /* Color del texto */
        border: none;
    }}
    div.stDownloadButton > button:first-child:hover {{
        background-color: {VERDE}; /* Color cuando pasas el mouse */
        color: white;
    }}
        div.stButton > button:first-child {{
        background-color: {VERDE_CLARO}; /* Tu color de fondo (Verde) */
        color: white;              /* Color del texto */
        border: none;
    }}
    div.stButton > button:first-child:hover {{
        background-color: {VERDE}; /* Color cuando pasas el mouse */
        color: white;
    }}
    </style>
""", unsafe_allow_html=True)


st.markdown(f"""
    <style>
        @import url('https://googleapis.com');

        [data-testid="stAppViewBlockContainer"] {{
            max-width: 100% !important;
            padding: 5 !important;
        }}

        .header-logos {{
            width: 100%;
            display: flex;
            justify-content: flex-end;
            align-items: center;
            padding: 5px;
            gap: 10px;
        }}

        .logo {{
            width: 30%;
            height: auto;
            object-fit: contain;
        }}

        h1, h3 {{
            font-family: '{FONT_FAMILY}', sans-serif;
            text-align: left;
            color: #333;
        }}

        /* Métricas estilizadas */
        [data-testid="stMetric"] {{
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #ffffff 0%, {CREMA} 100%);
            border: 2px solid {DORADO};
            border-radius: 16px;
            padding: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            transition: transform 0.2s;
        }}
        [data-testid="stMetric"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.12);
        }}
        [data-testid="stMetricLabel"] {{
            display: flex;
            justify-content: center;
            color: {VERDE};
            font-family: '{FONT_FAMILY}';
            font-weight: 600;
            font-size: 16px !important;
        }}
        [data-testid="stMetricValue"] {{
            display: flex;
            justify-content: center;
            color: {GUINDA};
            font-weight: bold;
            font-family: '{FONT_FAMILY}';
        }}

        /* Segmented control */
        button[data-testid="stBaseButton-segmented_controlActive"] {{
            border-color: {VERDE} !important;
            background-color: {DORADO} !important;
            color: white !important;
        }}
        button[data-testid="stBaseButton-segmented_control"]:hover {{
            border-color: {VERDE} !important;
        }}

        /* Tabs - Color verde institucional */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
            border-bottom: 2px solid {DORADO};
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
            font-family: '{FONT_FAMILY}';
            font-weight: 600;
            font-size: 15px;
            color: #555;
            transition: all 0.2s ease;
        }}
        .stTabs [data-baseweb="tab"]:hover {{
            background-color: rgba(40, 92, 77, 0.1) !important;
            color: {VERDE} !important;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {VERDE} !important;
            color: white !important;
            border-color: {VERDE} !important;
        }}
        .stTabs [data-baseweb="tab-highlight"] {{
            background-color: {VERDE} !important;
        }}
        .stTabs [data-baseweb="tab-border"] {{
            background-color: {VERDE} !important;
        }}

        /* Multiselect tags */
        span[data-baseweb="tag"] {{
            background-color: {VERDE} !important;
        }}
        span[data-baseweb="tag"] span {{
            color: white !important;
        }}
        span[data-baseweb="tag"] svg {{
            fill: white !important;
        }}
        div[data-baseweb="select"] > div:focus-within {{
            border-color: {VERDE} !important;
            box-shadow: 0 0 0 1px {VERDE} !important;
        }}

        /* Calendar */
        div[data-baseweb="calendar"] div[aria-selected="true"] {{
            background-color: {VERDE} !important;
            color: white !important;
        }}
        div[data-baseweb="calendar"] div:hover:not([aria-selected="true"]) {{
            border-color: {VERDE} !important;
        }}

        /* Date input focus */
        div[data-baseweb="input"]:focus-within {{
            border-color: {VERDE} !important;
        }}

        /* DataFrame focus */
        [data-testid="stDataFrame"] > div:focus-within {{
            border: 0.5px solid {VERDE} !important;
            box-shadow: 0 0 0 0.5px {VERDE} !important;
        }}

        /* Sidebar institucional - Fondo guinda */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {GUINDA} 0%, {GUINDA_CLARO} 100%) !important;
        }}
        
        /* Modificado: Excluimos únicamente la etiqueta de entrada que está estrictamente dentro de un multiselect */
        [data-testid="stSidebar"] *:not(.stMultiSelect input) {{
            color: white !important;
        }}

        /* NUEVO: Aplica color negro en tiempo real solo al input interno del multiselect en la barra lateral */
        [data-testid="stSidebar"] .stMultiSelect input {{
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
        }}

        [data-testid="stSidebar"] div[data-baseweb="select"] svg {{
            fill: {DORADO} !important;
        }}
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4 {{
            color: {DORADO} !important;
            font-family: '{FONT_FAMILY}' !important;
        }}
        [data-testid="stSidebar"] label {{
            color: {DORADO} !important;
            font-weight: 600 !important;
            font-family: '{FONT_FAMILY}' !important;
        }}

        /* Selectbox, Multiselect, DateInput - fondo y borde */
        [data-testid="stSidebar"] .stSelectbox > div > div,
        [data-testid="stSidebar"] .stMultiSelect > div > div,
        [data-testid="stSidebar"] .stDateInput > div > div {{
            background-color: rgba(255,255,255,0.08) !important;
            border-color: rgba(212, 193, 156, 0.4) !important;
            border-radius: 8px !important;
        }}

        /* Borde verde al hacer focus/seleccionar */
        [data-testid="stSidebar"] .stSelectbox > div > div:focus-within,
        [data-testid="stSidebar"] .stMultiSelect > div > div:focus-within,
        [data-testid="stSidebar"] .stDateInput > div > div:focus-within,
        [data-testid="stSidebar"] div[data-baseweb="select"] > div:focus-within,
        [data-testid="stSidebar"] div[data-baseweb="input"]:focus-within {{
            border-color: {VERDE_CLARO} !important;
            box-shadow: 0 0 0 2px rgba(58, 125, 107, 0.4) !important;
        }}

        /* Tags del multiselect */
        [data-testid="stSidebar"] span[data-baseweb="tag"] {{
            background-color: {VERDE} !important;
            border-radius: 6px !important;
        }}
        [data-testid="stSidebar"] span[data-baseweb="tag"] span {{
            color: white !important;
            font-weight: bold !important;
        }}
        [data-testid="stSidebar"] span[data-baseweb="tag"] svg {{
            fill: white !important;
        }}

        /* Dropdown abierto - borde verde */
        [data-testid="stSidebar"] div[data-baseweb="popover"] {{
            border-color: {VERDE_CLARO} !important;
        }}

        /* Calendario - selección verde */
        [data-testid="stSidebar"] div[data-baseweb="calendar"] div[aria-selected="true"] {{
            background-color: {VERDE} !important;
            color: white !important;
        }}
        [data-testid="stSidebar"] div[data-baseweb="calendar"] div:hover:not([aria-selected="true"]) {{
            border-color: {VERDE_CLARO} !important;
            background-color: rgba(58, 125, 107, 0.15) !important;
        }}

        /* Texto descriptivo sidebar */
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
            color: rgba(255,255,255,0.8) !important;
        }}
    </style>

    <header>
    </header>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ═══════════════════════════════════════════════════════════════════════════════


@st.cache_data
def import_df(ruta):
    return pl.read_parquet(ruta).to_pandas()

df = import_df("concentrado_actualizados.parquet")

fecha_datos =format_date(df["dia"].max(), format="d 'de' MMMM 'de' yyyy", locale="es")

st.markdown(f"""
    <div style="line-height: 1;">
        <h3 style="margin-bottom: 0;">Actualización o Corroboración de Datos e Integración de Expedientes</h3>
        <p style="font-size: 1.2em; color: {AMARILLO}; margin-top: 0px; font-weight: bold;">
            Información actualizada al <span style="color: {VERDE}; font-weight: bold;">{fecha_datos}</span> 
        </p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# Definir usuarios y accesos
# ═══════════════════════════════════════════════════════════════════════════════
username = st.session_state["username"]
tipo = st.secrets["auth"]["credentials"]["usernames"][username].get("tipo") if username in st.secrets['auth']['credentials']['usernames'] else "operativo"
oref = st.secrets["auth"]["credentials"]["usernames"][username].get("oref") if username in st.secrets['auth']['credentials']['usernames'] else []

df = df[df["NOM_EDO_PROD"].isin(oref)]

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR - FILTROS
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.header("Filtros de información")
    if tipo == 'administrador':
        opcion = st.selectbox("Seleccionar proceso", ["NACIONAL", "8 OREF", "25 OREF", "CONADESUCA", "Reposición de tarjetas", "Enviados a OREF (corrección)"])
    else:
        opcion = None

filtros = {
    "NACIONAL": None,
    "CONADESUCA": df["CONADESUCA"] == "Si",
    "8 OREF": df["OCHO_ENT"]== "Si",
    "25 OREF": df["OCHO_ENT"]== "No",
    "Reposición de tarjetas": df["reposición_tarjeta"] == "Si",
    "Enviados a OREF (corrección)": df["enviados_incongruencias"] == "Si",
}


condicion = filtros.get(opcion)
if condicion is not None:
    df = df[condicion]

with st.sidebar:
    estados = st.multiselect(
        "Seleccionar estados",
        options=sorted(df["NOM_EDO_PROD"].dropna().unique()),
        default=[],
        placeholder="Todos los estados"
    )


# Guardar copia para el mapa
df_para_mapa = df.copy()
# estados_seleccionados = estados if len(estados) > 0 else None

if len(estados) > 0:
    df = df[df["NOM_EDO_PROD"].isin(estados)]

# Meta - protección contra DataFrame vacío
meta = df['Personas'].sum() if len(df) > 0 else 0

# Filtro por fecha
if len(df) > 0:
    inicio = df["dia"].min().date() if pd.notna(df["dia"].min()) else datetime.date(2025, 12, 3)
    fin = df["dia"].max().date() if pd.notna(df["dia"].max()) else datetime.date.today()
else:
    inicio = datetime.date(2025, 12, 3)
    fin = datetime.date.today()

with st.sidebar:
    clave_dinamica_ini = f"fecha_ini_{inicio}_{opcion}_{len(estados)}"
    clave_dinamica_fin = f"fecha_fin_{fin}_{opcion}_{len(estados)}"

    fecha_ini = st.date_input(
        "Fecha de inicio",
        value=inicio,
        format="DD/MM/YYYY",
        key=clave_dinamica_ini
    )
    fecha_fin = st.date_input(
        "Fecha de fin",
        value=fin,
        format="DD/MM/YYYY",
        key=clave_dinamica_fin
    )

if pd.notna(fecha_ini) and pd.notna(fecha_fin) and fecha_ini != "" and fecha_fin != "":
    if len(df) > 0:
        df = df[
            ((df["dia"] >= pd.to_datetime(fecha_ini)) &
            (df["dia"] <= pd.to_datetime(fecha_fin))) |
            (df["dia"].isna())
        ]
    if len(df_para_mapa) > 0:
        df_para_mapa = df_para_mapa[
            ((df_para_mapa["dia"] >= pd.to_datetime(fecha_ini)) &
            (df_para_mapa["dia"] <= pd.to_datetime(fecha_fin))) |
            (df_para_mapa["dia"].isna())
        ]



# ═══════════════════════════════════════════════════════════════════════════════
# KPIs
# ═══════════════════════════════════════════════════════════════════════════════

actualizados = df[df['ACTUALIZADO'] == 'Si']['Personas'].sum() if len(df) > 0 else 0
pendientes = meta - actualizados
pct_avance = actualizados / meta * 100 if meta > 0 else 0
pct_pago = (df[df['Pagados_2026'] > 0 & df['Pagados_2026'].notnull() ]['Personas'].sum() if len(df) > 0 else 0) / actualizados * 100 if actualizados > 0 else 0
actualizados_ultima_semana = df.loc[df['semana'] == df['semana'].max(), 'Personas'].sum()
actualizados_ultima_semana_pct = actualizados_ultima_semana/meta*100 if meta > 0 else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Meta de personas para actualización", f"{meta:,.0f}", "100%")
with col2:
    st.metric("Personas actualizadas", f"{actualizados:,.0f}", f"{pct_avance:.1f}%")
with col3:
    st.metric("Personas Pendientes de actualizar", f"{pendientes:,.0f}", f"{100 - pct_avance:.1f}%", delta_color="inverse")

if tipo == 'administrador' or tipo == 'ejecutivo':
    col6, col4, col5 = st.columns(3)
    with col6:
        st.metric("Personas actualizadas esta semana",f"{actualizados_ultima_semana:,.0f}"if not df.empty else "N/A",f"{actualizados_ultima_semana_pct:.3f}%")
    with col4:
        st.metric("Monto pagado para actualizados", f"${df['Pagados_2026'].sum():,.0f}" if len(df) > 0 else "N/A", f"{pct_pago*pct_avance/100:.1f}%")
    with col5:
        st.metric("Monto estimado para actualizados", f"${df['Monto_est_2026'].sum():,.0f}" if len(df) > 0 else "N/A", f"{pct_avance:.1f}%")

# ═══════════════════════════════════════════════════════════════════════════════
# TABS PRINCIPALES
# ═══════════════════════════════════════════════════════════════════════════════

tab_avance, tab_productivos, tab_perfil = st.tabs([
    "Avance General",
    "Aspectos productivos",
    "Aspectos demográficos",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: AVANCE GENERAL
# ═══════════════════════════════════════════════════════════════════════════════

with tab_avance:

    tab_avance_estados, tab_avance_cader, tab_avance_resumen, tab_temporal = st.tabs([
        "Por OREF",
        "Por CADER",
        "Resumen",
        "Por Periodo",
    ])


    with tab_avance_estados:

        tab_barras_avance_est, tab_detalle_avance_est = st.tabs(["Gráfico", "Detalle"])

        with tab_barras_avance_est:
            df_estado = df.groupby(["NOM_EDO_PROD", "ACTUALIZADO"])["Personas"].sum().reset_index()
            if df_estado["NOM_EDO_PROD"].nunique() == 1:
                st.plotly_chart(crear_dona(df_estado[["ACTUALIZADO","Personas"]],f"Actualizados en {df_estado['NOM_EDO_PROD'].unique()[0]}".upper()))
            else:
                st.plotly_chart(crear_barras_porcentaje(df_estado, "NOM_EDO_PROD", "ACTUALIZADO", "Personas", "Avance por OREF"), width='stretch')
        
        with tab_detalle_avance_est:
            config_df_oref = {
                "NOM_EDO_PROD": st.column_config.Column("OREF", width=150),
                "Personas": st.column_config.NumberColumn("Meta", format="accounting", step=1),
                "Personas_act": st.column_config.NumberColumn("Avance", format="accounting", step=1),
                "pct_act": st.column_config.NumberColumn("(%)", format="%.1f%%", step=0.01),
                "Personas_meta_caña": st.column_config.NumberColumn("Meta CONADESUCA", format="accounting", step=1),
                "Personas_act_caña": st.column_config.NumberColumn("Avance CONADESUCA", format="accounting", step=1),
                "pct_caña": st.column_config.NumberColumn("(%)", format="%.1f%%", step=0.01),
                "Personas_meta_tarjetas": st.column_config.NumberColumn("Meta R. Tarjetas", format="accounting", step=1),
                "Personas_act_tarjetas": st.column_config.NumberColumn("Avance R. Tarjetas", format="accounting", step=1),
                "pct_tarjetas": st.column_config.NumberColumn("(%)", format="%.1f%%", step=0.01)
            }
            cols = ["Etiqueta","NOM_EDO_PROD","Personas","Personas_act","pct_act","Personas_meta_caña","Personas_act_caña","pct_caña","Personas_meta_tarjetas","Personas_act_tarjetas","pct_tarjetas"]
            df_oref=(df.assign(
                Etiqueta = lambda x: np.where(x["OCHO_ENT"].eq("Si"),"8 oref","25 oref"),
                Personas_act=lambda x:x["Personas"].where(x["ACTUALIZADO"].eq("Si"),0),
                Personas_meta_caña=lambda x:x["Personas"].where(x["CONADESUCA"].eq("Si"),0),
                Personas_act_caña=lambda x:x["Personas"].where(x["CONADESUCA"].eq("Si")&x["ACTUALIZADO"].eq("Si"),0),
                Personas_meta_tarjetas=lambda x:x["Personas"].where(x["reposición_tarjeta"].eq("Si"),0),
                Personas_act_tarjetas=lambda x:x["Personas"].where(x["reposición_tarjeta"].eq("Si")&x["ACTUALIZADO"].eq("Si"),0))
                .groupby(["Etiqueta","NOM_EDO_PROD"],dropna=False,as_index=False)[["Personas","Personas_act","Personas_meta_caña","Personas_act_caña","Personas_meta_tarjetas","Personas_act_tarjetas"]].sum()
                .assign(
                    pct_act=lambda x:(x["Personas_act"]/x["Personas"]*100).fillna(0),
                    pct_caña=lambda x:(x["Personas_act_caña"]/x["Personas_meta_caña"]*100).fillna(0),
                    pct_tarjetas=lambda x:(x["Personas_act_tarjetas"]/x["Personas_meta_tarjetas"]*100).fillna(0)
                ).sort_values("pct_act",ascending=False)
                )[cols]
            
            df_oref_totales=df_oref.sum(numeric_only=True).to_frame().T.assign(
                NOM_EDO_PROD="TOTAL",Etiqueta=" ",
                pct_act=lambda x:(x["Personas_act"]/x["Personas"]*100).fillna(0),
                pct_caña=lambda x:(x["Personas_act_caña"]/x["Personas_meta_caña"]*100).fillna(0),
                pct_tarjetas=lambda x:(x["Personas_act_tarjetas"]/x["Personas_meta_tarjetas"]*100).fillna(0)
            )[cols]

            st.markdown(f"<span style='color: {GUINDA}; font-size: 28px; font-weight: bold;'>Avance por OREF</span>", unsafe_allow_html=True)
            st.dataframe(df_oref,width="stretch",column_config=config_df_oref, hide_index=True)
            st.dataframe(df_oref_totales,width="stretch",column_config=config_df_oref, hide_index=True)


    with tab_avance_cader:
        if "NOM_EDO_PROD" in df.columns:
            config_df_cader = {
                "OREF": st.column_config.Column(width=150),
                "DDR": st.column_config.Column(width=150),
                "CADER": st.column_config.Column(width=150),
                "Meta\n(personas)": st.column_config.NumberColumn(format="accounting", step=1),
                "Avance\n(personas)": st.column_config.NumberColumn(format="accounting", step=1),
                "Avance\n(%)": st.column_config.NumberColumn(format="%.1f%%", step=0.01),
            }
            config_df_cader_totales = {
                "OREF": st.column_config.Column(width=600),
                "Meta\n(personas)": st.column_config.NumberColumn(format="accounting", step=1),
                "Avance\n(personas)": st.column_config.NumberColumn(format="accounting", step=1),
                "Avance\n(%)": st.column_config.NumberColumn(format="%.1f%%", step=0.01),
            }
            df_cader = (df.assign(avance=lambda x: x["Personas"].where(x["ACTUALIZADO"] == "Si", 0))
                        .groupby(["NOM_EDO_PROD", "nombre_ddr_solicitud", "nombre_cader_solicitud",],dropna=False,as_index=False)[["Personas","avance"]]
                        .sum().reset_index(drop=True)
                        .assign(porcentaje=lambda x: (100 * x["avance"] / x["Personas"].sum()).round(2).fillna(0))
                        .sort_values(["NOM_EDO_PROD","porcentaje"],ascending=False)
                        .rename(columns={"NOM_EDO_PROD": "OREF", "nombre_ddr_solicitud": "DDR", "nombre_cader_solicitud": "CADER", "Personas": "Meta\n(personas)","avance": "Avance\n(personas)", "porcentaje": "Avance\n(%)"})
                        )[["OREF","DDR","CADER","Meta\n(personas)","Avance\n(personas)","Avance\n(%)"]]

            df_cader_totales=df_cader.sum(numeric_only=True).to_frame().T.assign(OREF="TOTAL")[["OREF","Meta\n(personas)","Avance\n(personas)","Avance\n(%)"]]

            st.markdown(f"<span style='color: {GUINDA}; font-size: 28px; font-weight: bold;'>Avance por OREF-DDR-CADER</span>", unsafe_allow_html=True)
            st.dataframe(df_cader, column_config=config_df_cader, width='stretch', hide_index=True)
            st.dataframe(df_cader_totales, column_config=config_df_cader_totales, width='stretch', hide_index=True)
        else:
            st.info("Columna 'NOM_EDO_PROD' no disponible.")

    with tab_avance_resumen:
        # ═══════════════════════════════════════════════════════════════════════════════
        # TAB 4: DETALLE DE REGISTROS
        # ═══════════════════════════════════════════════════════════════════════════════
        st.markdown(f"<span style='color: {GUINDA}; font-size: 28px; font-weight: bold;'>Detalle General</span>", unsafe_allow_html=True)


    with tab_temporal:
        periodo = st.segmented_control("Periodo:", options=["Semanal", "Mensual"], default="Mensual")

        df["dia"] = pd.to_datetime(df["dia"])
        df_temp = df.dropna(subset=["dia"]).copy()

        if len(df_temp) == 0:
            st.info("No hay datos con fecha de captura para el periodo y filtros seleccionados.")
        else:
            if periodo == "Semanal":
                df_agrupado = df_temp.groupby(df_temp["semana"].dt.strftime("%Y-%m-%d"))["Personas"].sum().reset_index().rename(columns={'semana': 'Categoria'}).sort_values("Categoria").assign(Porcentaje = lambda x: (x["Personas"]/x["Personas"].sum() * 100).round(2).fillna(0),
                    Acumulado = lambda x: x["Personas"].fillna(0).cumsum() )
                n = 7
            else:
                df_agrupado = df_temp.groupby(df_temp["mes"])["Personas"].sum().reset_index().rename(columns={'mes': 'Categoria'}).sort_values("Categoria").assign(Porcentaje = lambda x: (x["Personas"]/x["Personas"].sum() * 100).round(2).fillna(0),
                    Acumulado = lambda x: x["Personas"].fillna(0).cumsum() )
                periodo = "Mensual"
                n = 12

            tab_acum, tab_barras_t, tab_detalle_a_t = st.tabs(["Acumulado", "Barras", "Detalle"])

            with tab_acum:
                # 1. Creamos una lista para alternar la posición del texto y evitar que se encimen
                st.plotly_chart(grafica_cumsum(df_agrupado[["Categoria","Personas"]],periodo="Categoria",titulo=f'Avance Acumulado {periodo}',n=n,height=550))

            with tab_barras_t:
                st.plotly_chart(crear_barras(df_agrupado[["Categoria","Personas"]].tail(n),f"Avance {periodo}",colores_lista=[DORADO],height=500), width='stretch')

            with tab_detalle_a_t:
                st.markdown(f"<span style='color: {GUINDA}; font-size: 20px; font-weight: bold;'>Detalle del avance {periodo}</span>", unsafe_allow_html=True)
                st.dataframe(df_agrupado[["Categoria", "Personas", "Porcentaje","Acumulado"]]
                            .sort_values(by="Categoria", ascending=False)
                            .rename(columns={"Categoria": "Periodo", "Personas": "Personas actualizadas"}),
                            column_config={"Porcentaje": st.column_config.NumberColumn(format="%.2f%%"),
                                            "Personas actualizadas": st.column_config.NumberColumn(format="accounting",step=1),
                                            "Acumulado": st.column_config.NumberColumn(format="accounting",step=1)},
                            width='stretch',
                            hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: ASPECTOS PRODUCTIVOS
# ═══════════════════════════════════════════════════════════════════════════════

with tab_productivos:
    col1, col2 = st.columns(2)
    columnas_c = [col1, col2]
    variables_dona_1 = {
        "Cambio_sup": "Cambio de Superficie",
        "Cambio_cultivo": "Cambio de Cultivo",
    }

    for i, (variable, titulo) in enumerate(variables_dona_1.items()):
        df_dona = df.groupby(variable)["Personas"].sum().reset_index()
        df_dona["Porcentaje"] = (df_dona["Personas"] / df_dona["Personas"].sum() * 100).round(2) if df_dona["Personas"].sum() > 0 else 0
        df_dona.columns = ["Categoria", "Personas","Porcentaje"]
        df_dona = df_dona.sort_values("Personas", ascending=False).reset_index(drop=True)
        with columnas_c[i]:
            tab_d, tab_w = st.tabs(["Dona", "Detalle"])
            with tab_d:
                st.plotly_chart(crear_dona(df_dona[["Categoria", "Personas"]], titulo), width='stretch')
            with tab_w:
                st.dataframe(df_dona, width='stretch', hide_index=True, column_config={"Categoria": st.column_config.Column(titulo), "Personas": st.column_config.NumberColumn("Personas", format="accounting",step=1), "Porcentaje": st.column_config.NumberColumn("Porcentaje", format="%.2f %%", step=0.01)})

    col1, col2 = st.columns(2)
    columnas_c3 = [col1, col2]
    variables_barras_3 = {
        "Grupo_Superficie": "Grupos de superficie",
        "Estrategia_predominante": "Estrategia",
    }

    for i, (variable, titulo) in enumerate(variables_barras_3.items()):
        df_dona = df.groupby(variable)["Personas"].sum().reset_index()
        df_dona["Porcentaje"] = (df_dona["Personas"] / df_dona["Personas"].sum() * 100).round(2) if df_dona["Personas"].sum() > 0 else 0
        df_dona.columns = ["Categoria", "Personas","Porcentaje"]
        df_dona = df_dona.sort_values("Personas", ascending=False).reset_index(drop=True)
        with columnas_c3[i]:
            tab_d, tab_w = st.tabs(["Dona", "Detalle"])
            with tab_d:
                st.plotly_chart(crear_barras(df_dona[["Categoria", "Personas"]], titulo), width='stretch')
            with tab_w:
                st.dataframe(df_dona, width='stretch', hide_index=True, column_config={"Categoria": st.column_config.Column(titulo), "Personas": st.column_config.NumberColumn("Personas", format="accounting",step=1), "Porcentaje": st.column_config.NumberColumn("Porcentaje", format="%.2f %%", step=0.01)})

    col1, col2, col3 = st.columns(3)
    columnas_c2 = [col1, col2, col3]
    variables_dona_2 = {
        "regimen_predominante": "Régimen hídrico",
        "ciclo": "Ciclo productivo",
        "tipo_posesion": "Tipo de Posesión"
    }

    for i, (variable, titulo) in enumerate(variables_dona_2.items()):
        df_dona = df.groupby(variable)["Personas"].sum().reset_index()
        df_dona["Porcentaje"] = (df_dona["Personas"] / df_dona["Personas"].sum() * 100).round(2) if df_dona["Personas"].sum() > 0 else 0
        df_dona.columns = ["Categoria", "Personas","Porcentaje"]
        df_dona = df_dona.sort_values("Personas", ascending=False).reset_index(drop=True)
        # colores_var = ["#235B4E", "#691C32", "#C29E5C"]
        with columnas_c2[i]:
            tab_d2, tab_w2 = st.tabs(["Dona", "Detalle"])
            with tab_d2:
                st.plotly_chart(crear_dona(df_dona[["Categoria", "Personas"]], titulo, colores_lista=["#235B4E", "#691C32", "#C29E5C"]), width='stretch')
            with tab_w2:
                st.dataframe(df_dona, width='stretch', hide_index=True, column_config={"Categoria": st.column_config.Column(titulo), "Personas": st.column_config.NumberColumn("Personas", format="accounting",step=1), "Porcentaje": st.column_config.NumberColumn("Porcentaje", format="%.2f %%", step=0.01)})

    df_dona = df.groupby("cultivo_predominante")["Personas"].sum().reset_index()
    df_dona["Porcentaje"] = (df_dona["Personas"] / df_dona["Personas"].sum() * 100).round(2) if df_dona["Personas"].sum() > 0 else 0
    df_dona.columns = ["Categoria", "Personas","Porcentaje"]
    df_dona = df_dona.sort_values("Personas", ascending=False).reset_index(drop=True)
    tab_d0, tab_w0 = st.tabs(["Dona", "Detalle"])
    with tab_d0:
        st.plotly_chart(crear_barras(df_dona[["Categoria", "Personas"]], "Cultivos", colores_lista=["#235B4E", "#691C32", "#C29E5C"]), width='stretch')
    with tab_w0:
        st.dataframe(df_dona, width='stretch', hide_index=True, column_config={"Categoria": st.column_config.Column("Cultivo"), "Personas": st.column_config.NumberColumn("Personas", format="accounting",step=1), "Porcentaje": st.column_config.NumberColumn("Porcentaje", format="%.2f %%", step=0.01)})

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: PERFIL DEMOGRÁFICO
# ═══════════════════════════════════════════════════════════════════════════════
with tab_perfil:

    df_edad = df.groupby(["Ord_Grupos_Edad", "Grupos_Edad"])["Personas"].sum().reset_index()
    df_edad = df_edad.sort_values("Ord_Grupos_Edad").reset_index(drop=True)
    # total_personas_edad = df_edad["Personas"].sum()
    df_edad["Porcentaje"] = (df_edad["Personas"] / df_edad["Personas"].sum() * 100).round(1) if df_edad["Personas"].sum() > 0 else 0
    df_edad.columns = ["Orden Categoria","Categoria", "Personas","Porcentaje"]
    colores_edad = (PALETA_INSTITUCIONAL * 3)[:len(df_edad)]

    col1_tap_perfil, col2_tap_perfil = st.columns(2)

    with col1_tap_perfil:
        tab_edad_barras, tab_edad_detalle = st.tabs(["Barras", "Detalle"])

        with tab_edad_barras:
            # st.plotly_chart(fig_edad_v, width='stretch')
            st.plotly_chart(crear_barras(df_edad[["Categoria", "Personas"]], "Distribución por Grupos de Edad", colores_lista=colores_edad), width='stretch')

        with tab_edad_detalle:
            st.markdown(f"<span style='color: {GUINDA}; font-size: 24px; font-weight: bold;'>Detalle por grupos de edad</span>", unsafe_allow_html=True)
            st.dataframe(df_edad[["Categoria", "Personas", "Porcentaje"]], width='stretch', hide_index=True, column_config={"Categoria": st.column_config.Column("Grupos de Edad"), "Personas": st.column_config.NumberColumn("Personas actualizadas", format="accounting",step=1), "Porcentaje": st.column_config.NumberColumn("Porcentaje del total", format="%.2f %%", step=0.01)})

    with col2_tap_perfil:
        dona_genero, detalle_genero = st.tabs(["Dona", "Detalle"])

        df_genero = df.groupby("genero")["Personas"].sum().reset_index()
        df_genero["Porcentaje"] = (df_genero["Personas"] / df_genero["Personas"].sum() * 100).round(2) if df_genero["Personas"].sum() > 0 else 0
        df_genero.columns = ["Categoria", "Personas","Porcentaje"]

        with dona_genero:
            st.plotly_chart(crear_dona(df_genero[["Categoria", "Personas"]], "Distribución por género", colores_lista=["#235B4E", "#691C32"]), width='stretch')
        with detalle_genero:
            st.markdown(f"<span style='color: {GUINDA}; font-size: 18px; font-weight: bold;'>Detalle por género</span>", unsafe_allow_html=True)
            st.dataframe(df_genero, width='stretch', hide_index=True, column_config={"Categoria": st.column_config.Column("Género"), "Personas": st.column_config.NumberColumn("Personas actualizadas", format="accounting",step=1), "Porcentaje": st.column_config.NumberColumn("Porcentaje del total", format="%.2f %%", step=0.01)})


    st.markdown(f"<span style='color: {GUINDA}; font-size: 28px; font-weight: bold;'>Documentos de posesión/propiedad</span>", unsafe_allow_html=True)
    df_doc = df.groupby(["clave_documento_propiedad","EstatusDocProp","nombre_documento_propiedad"])[["Personas","Registros"]].sum().reset_index().sort_values("EstatusDocProp", ascending=True).reset_index(drop=True)
    df_doc = df_doc.rename(columns={"clave_documento_propiedad": "Clave", "nombre_documento_propiedad": "Nombre Documento", "EstatusDocProp": "Estatus Documento"})
    st.dataframe(df_doc, width='stretch', hide_index=True)





# ═══════════════════════════════════════════════════════════════════════════════
# BOTÓN DE DESCARGA EN EL SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    st.markdown(f"""<br>Generar presentación""", unsafe_allow_html=True)

    if st.button("Descargar informe", type="primary"):
        st.toast("Procesando presentación", icon="⚙️")

        from generar_archivo_pdf import generar_presentacion_pdf
        # 2. Tu botón (se pintará automáticamente con el CSS de arriba)
        st.download_button(
            label="Generar y Descargar PDF",
            data=lambda: generar_presentacion_pdf(df, meta, actualizados, pendientes, pct_avance, hoy),
            file_name=f"Presentacion_PROBIEN_{hoy}.pdf",
            mime="application/pdf",
            use_container_width=True,
            on_click=lambda: st.toast("¡Preparando descarga!", icon="📥")  # 👈 Mensaje flotante
        )


# =============================================================================
# FOOTER
# =============================================================================

st.divider() # Una línea sutil para separar el contenido
with st.expander("Información Legal y de Privacidad"):
    st.markdown(f"""
    **Aviso de Uso Interno e Informativo**  
    Esta plataforma es una herramienta de consulta exclusiva para el personal autorizado del Gobierno. Desarrollada por el Área de Estadística y Actualización, los resultados presentados son de carácter estrictamente informativo y no constituyen documentos oficiales, resoluciones ni actos administrativos vinculantes.<br> <br>
    Este software es de código abierto distribuido bajo la Licencia Apache 2.0. - Área de Estadística y Actualización.<br>
    {st.secrets["password"] if "password" in st.secrets else "Nada"}
    """, unsafe_allow_html=True)
