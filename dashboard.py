from generar_presentacion import descargar_presentacion

import streamlit as st
import psycopg 
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import base64

from datetime import datetime, date
from zoneinfo import ZoneInfo
from babel.dates import format_date
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
# hoy = datetime.now(ZoneInfo("America/Mexico_City")).strftime("%d-%m-%Y")
hoy = format_date(datetime.now(ZoneInfo("America/Mexico_City")).date(), format="d 'de' MMMM 'de' yyyy", locale="es")

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
            tickfont=dict(size=20, family=FONT_FAMILY, color="Black"),
            tickangle=-45
        ),
        yaxis=dict(
            # SOLUCIÓN: El texto y su fuente ahora van estructurados correctamente aquí
            title=dict(
                text="Personas",
                font=dict(size=20, family=FONT_FAMILY, color=GUINDA)
            ),
            tickfont=dict(size=20, family=FONT_FAMILY),
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
    height=600,
    font_size_labels=15,
    hole=0.50,
    add_text_center=True,
):
    """
    Dona con etiquetas externas y líneas guía.

    DataFrame esperado:
        Columna 0 -> Categoría
        Columna 1 -> Valor
    """

    if df is None or df.empty or len(df.columns) < 2:
        return px.pie()

    if colores_lista is None:
        colores_lista = PALETA_INSTITUCIONAL

    df = df.iloc[:, :2].copy()

    col_categoria = df.columns[0]
    col_valor = df.columns[1]

    total = df[col_valor].sum()

    # Etiquetas externas:
    # Categoría
    # Cantidad Personas
    # Porcentaje
    df["Etiqueta"] = df.apply(
        lambda r: (
            f"<b>{r[col_categoria]}</b><br>"
            f"{r[col_valor]:,.0f}<br>"
            f"{r[col_valor] / total:.1%}"
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

    # Total en el centro
    if add_text_center:
        fig.add_annotation(
            x=0.5,
            y=0.5,
            showarrow=False,
            text=(
                f"<b>{total:,.0f}</b><br>"
                "Personas<br>"
            ),
            font=dict(
                size=font_size_labels + 8,
                color=GUINDA,
                family=FONT_FAMILY,
            ),
        )

    fig.update_traces(
        textposition="outside",
        # Mostrar únicamente la etiqueta personalizada
        textinfo="label",
        textfont=dict(
            size=font_size_labels,
            color=GUINDA,
            family=FONT_FAMILY,
        ),
        marker=dict(
            line=dict(
                color="white",
                width=2,
            )
        ),
        customdata=df[[col_categoria]],
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "%{value:,.0f} Personas<br>"
            "%{percent}"
            "<extra></extra>"
        ),
        automargin=False,
        domain=dict(
        x=[0.1, 0.9],
        y=[0.1, 0.9],
    ),
    )

    if titulo:
        fig.add_annotation(
            x=0.5,
            y=0,
            xref="paper",
            yref="paper",
            showarrow=False,
            text=f"<b>{titulo}</b>",
            font=dict(
                size=font_size_labels + 10,
                color=VERDE,
                family=FONT_FAMILY,
            ),
            xanchor="center",
            yanchor="top",
        )



    # Configuración general
    fig.update_layout(
        # No mostrar título cuando está vacío
        title=None if not titulo else dict(
            text=" ",
            x=0.5,
            xanchor="center",
            font=dict(
                size=font_size_labels + 4,
                color=VERDE,
                family=FONT_FAMILY,
            ),
        ),
        hoverlabel=dict(
            font_size=18, font_family=FONT_FAMILY,
            bgcolor="white", font_color=VERDE, bordercolor=DORADO
        ),

        showlegend=False,

        height=height,

        # margin=dict(
        #     t=0,
        #     b=115 if titulo else 25,
        #     l=100,
        #     r=100,
        # ),

        paper_bgcolor="rgba(0,0,0,0)",

        uniformtext=dict(
            minsize=font_size_labels,
            mode="show",
        ),
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
            # "<b>%{customdata[0]}:</b><br>"
            # "%{value:,.0f} personas<br>"
            "<b>Porcentaje:</b> %{y:.1f}%"
            "<extra></extra>"
        ),
        customdata=df_agrupado[[col_valores]].values
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
        hoverlabel=dict(
            font_size=18,
            font_family=FONT_FAMILY,
            bgcolor="white",
            font_color=VERDE,
            bordercolor=DORADO,
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
                "Del periodo: %{customdata:,.0f} personas"
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
            font_size=18,
            font_family=FONT_FAMILY,
            bgcolor="white",
            font_color=VERDE,
            bordercolor=DORADO,
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
            title=dict(
                text="Personas",
                font=dict(
                    family=FONT_FAMILY,      # La variable de tu fuente institucional
                    size=22,                 # Tamaño de la letra del título
                    color=titulo_color       # Color del título (puedes usar tus variables como titulo_color, #691C32, etc.)
                )
            ),                      
            side="right",                       # Todo el componente al lado derecho
            visible=True,                       
            showticklabels=False,               # Oculta la escala de números
            ticks="",                           # CORREGIDO: Elimina los pequeños rasgos/pestañas del eje

            gridcolor="rgba(0,0,0,0)",
            gridwidth=1,
            range=[y_min, y_max + y_padding],
            autorange=False,
            zeroline=False,
            showline=False,
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

st.markdown("""
<style>
div[data-testid="stMultiSelect"] label p {
    font-size: 20px !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ═══════════════════════════════════════════════════════════════════════════════
# Funciones
@st.cache_data(ttl=60*5)
def cargar_datos(query, parametros=None):
    with psycopg.connect(st.secrets["supabase"]["DATABASE_URL"]) as conn:
        with conn.cursor() as cur:
            cur.execute(query, parametros)
            filas = cur.fetchall()
            columnas = [desc.name for desc in cur.description]
    return pd.DataFrame(filas, columns=columnas).reset_index(drop=True)

@st.cache_data(ttl=30)
def enviar_ingreso(username=None):
    with psycopg.connect(st.secrets["supabase"]["DATABASE_URL"]) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TIME ZONE 'America/Mexico_City'")
            cur.execute("""UPDATE public.usuarios SET ultimo_ingreso = NOW() WHERE username = %s """, (username,))
        conn.commit()

fecha_datos =format_date(cargar_datos("""SELECT MAX("dia") FROM concentrado""").iloc[0, 0], format="d 'de' MMMM 'de' yyyy", locale="es")

st.markdown(f"""
    <div style="line-height: 1;">
        <h3 style="margin-bottom: 0;">Actualización o Corroboración de Datos e Integración de Expedientes</h3>
        <p style="font-size: 1.2em; color: {AMARILLO}; margin-top: 0px; font-weight: bold;">
            Reporte del {hoy} con Información actualizada al <span style="color: {VERDE}; font-weight: bold;">{fecha_datos}</span> 
        </p>
    """, unsafe_allow_html=True)
    </div>

# ═══════════════════════════════════════════════════════════════════════════════
# Definir usuarios y accesos
# ═══════════════════════════════════════════════════════════════════════════════
username = st.session_state["username"]
enviar_ingreso(username)

tipo, oref_asignada = cargar_datos("""SELECT "tipo" , "oref" FROM usuarios WHERE "username" = ANY(%s)""",[[username]]).iloc[0]
print(tipo, oref_asignada)



if oref_asignada:
    condiciones = ['"CVE_REP_PROD" = ANY(%s)']
    parametros=[oref_asignada]


# # ═══════════════════════════════════════════════════════════════════════════════
# # SIDEBAR - FILTROS
# # ═══════════════════════════════════════════════════════════════════════════════


with st.sidebar:
    st.header("Filtros de información")
    if tipo == 'administrador':
        proceso = st.selectbox("Seleccionar proceso", ["NACIONAL", "8 OREF", "25 OREF", "FASE 1", "FASE 2"],
                               index = 4)
    else:
        proceso = None

if proceso == "8 OREF":
    condiciones.append('"OCHO_ENT" = ANY(%s)')
    parametros.append(["Si"])
elif proceso == "25 OREF":
    condiciones.append('"OCHO_ENT" = ANY(%s)')
    parametros.append(["No"])
elif proceso == "FASE 1":
    condiciones.append('"FASES" = ANY(%s)')
    parametros.append(["FASE 1"])
elif proceso == "FASE 2":
    condiciones.append('"FASES" = ANY(%s)')
    parametros.append(["FASE 2"])
else:
    pass

if tipo != 'administrador':
    condiciones.append('"FASES" = ANY(%s)')
    parametros.append(["FASE 2"])

where = "WHERE " + " AND ".join(condiciones)
query_rep = f"""SELECT DISTINCT "NOM_REP" FROM concentrado {where};"""


with st.sidebar:
    filtro_rep = st.multiselect(
        "Seleccionar estados",
        options=sorted(cargar_datos(query_rep, parametros)["NOM_REP"].dropna().unique()),
        default=[],
        placeholder="Todos los estados"
    )


# Aplicar filtro por representación
if len(filtro_rep)>0:
    condiciones.append('"NOM_REP" = ANY(%s)')
    parametros.append(filtro_rep)

where_oref ="WHERE " + " AND ".join(condiciones)
parametros_oref = list(parametros)
# Seleccionar fecha para filtro

query_rep = f"""SELECT MIN("dia"),MAX("dia") FROM concentrado {where_oref};"""

inicio, fin = cargar_datos(query_rep, parametros_oref).iloc[0]
inicio = inicio if pd.notna(inicio) else date(2025, 12, 3)
fin = fin if pd.notna(fin) else date.today()

with st.sidebar:
    clave_dinamica_ini = f"fecha_ini_{inicio}_{proceso}_{len(filtro_rep)}"
    clave_dinamica_fin = f"fecha_fin_{fin}_{proceso}_{len(filtro_rep)}"

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

# Aplicar el filtro por fecha
if fecha_ini is not None and fecha_fin is not None:
    # hacer algo
    condiciones.append('"dia" BETWEEN %s AND %s')
    parametros.extend([fecha_ini, fecha_fin])
where = "WHERE " + " AND ".join(condiciones)



# ═══════════════════════════════════════════════════════════════════════════════
# KPIs
# ═══════════════════════════════════════════════════════════════════════════════
kpis = cargar_datos(f""" SELECT 
    COALESCE(SUM("Personas") FILTER (WHERE "ACTUALIZADO" = 'Si' ), 0) AS "Avance",
    COALESCE(SUM("Personas") FILTER (WHERE "ACTUALIZADO" = 'Si' AND "semana" = (SELECT MAX("semana") FROM concentrado) ), 0) AS "act_max_semana"
    FROM concentrado  {where}
""",parametros).fillna(0).astype('float64').iloc[0]
meta = cargar_datos(f"""SELECT SUM("Personas") FROM concentrado  {where_oref}""",parametros_oref).fillna(0).astype('float64').iloc[0,0]
actualizados, actualizados_ultima_semana = kpis
pendientes = meta - actualizados
pct_avance = actualizados/meta*100 if meta > 0 else 0
actualizados_ultima_semana_pct = actualizados_ultima_semana/meta*100 if meta > 0 else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Meta de personas para actualización", f"{meta:,.0f}", "100%")
with col2:
    st.metric("Personas actualizadas", f"{actualizados:,.0f}", f"{pct_avance:.1f}%")
with col3:
    st.metric("Personas Pendientes de actualizar", f"{pendientes:,.0f}", f"{100 - pct_avance:.1f}%", delta_color="inverse")
with col4:
    st.metric("Personas actualizadas en la última semana",f"{actualizados_ultima_semana:,.0f}"if actualizados_ultima_semana else "0",f"{actualizados_ultima_semana_pct:.1f}%")

# # ═══════════════════════════════════════════════════════════════════════════════
# # TABS PRINCIPALES
# # ═══════════════════════════════════════════════════════════════════════════════

tab_avance, tab_productivos, tab_perfil, tab_graficos, tab_Consultador = st.tabs([
    "Avance General",
    "Aspectos productivos",
    "Aspectos demográficos",
    "Gráficos",
    "Consultador",
])


# # ═══════════════════════════════════════════════════════════════════════════════
# # TAB 1: AVANCE GENERAL
# # ═══════════════════════════════════════════════════════════════════════════════

with tab_avance:

    tab_avance_estados, tab_avance_cader, tab_temporal = st.tabs([
        "Por OREF",
        "Por CADER",
        "Por Periodo",
    ])


    with tab_avance_estados:

        tab_barras_avance_est, tab_detalle_avance_est = st.tabs(["Gráfico", "Detalle"])

        with tab_barras_avance_est:
            df_estado = cargar_datos(f"""SELECT "NOM_REP", "ACTUALIZADO", sum("Personas") AS "Personas" FROM concentrado {where_oref} GROUP BY "NOM_REP", "ACTUALIZADO";""",parametros_oref)
            if df_estado["NOM_REP"].nunique() == 1:
                st.plotly_chart(crear_dona(df_estado[["ACTUALIZADO","Personas"]],f"Actualizados en {df_estado['NOM_REP'].unique()[0]}".upper()))
            else:
                st.plotly_chart(crear_barras_porcentaje(df_estado, "NOM_REP", "ACTUALIZADO", "Personas", "Avance por OREF"), width='stretch')
        
        with tab_detalle_avance_est:
            config_df_oref = {
                "NOM_REP": st.column_config.Column("OREF", width=150),
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
            cols = ["Etiqueta","NOM_REP","Personas","Personas_act","pct_act","Personas_meta_caña","Personas_act_caña","pct_caña","Personas_meta_tarjetas","Personas_act_tarjetas","pct_tarjetas"]

            
            df_oref=(cargar_datos(f"""SELECT "NOM_REP","OCHO_ENT", "ACTUALIZADO","CONADESUCA","reposición_tarjeta", sum("Personas") AS "Personas" FROM concentrado {where_oref} GROUP BY "NOM_REP","OCHO_ENT", "ACTUALIZADO","CONADESUCA","reposición_tarjeta";""",parametros_oref).assign(
                Etiqueta = lambda x: np.where(x["OCHO_ENT"].eq("Si"),"Fase 1","Fase 2"),
                Personas_act=lambda x:x["Personas"].where(x["ACTUALIZADO"].eq("Si"),0),
                Personas_meta_caña=lambda x:x["Personas"].where(x["CONADESUCA"].eq("Si"),0),
                Personas_act_caña=lambda x:x["Personas"].where(x["CONADESUCA"].eq("Si")&x["ACTUALIZADO"].eq("Si"),0),
                Personas_meta_tarjetas=lambda x:x["Personas"].where(x["reposición_tarjeta"].eq("Si"),0),
                Personas_act_tarjetas=lambda x:x["Personas"].where(x["reposición_tarjeta"].eq("Si")&x["ACTUALIZADO"].eq("Si"),0))
                .groupby(["Etiqueta","NOM_REP"],dropna=False,as_index=False)[["Personas","Personas_act","Personas_meta_caña","Personas_act_caña","Personas_meta_tarjetas","Personas_act_tarjetas"]].sum()
                .assign(
                    pct_act=lambda x:(x["Personas_act"]/x["Personas"]*100).fillna(0).astype('float64'),
                    pct_caña=lambda x:(x["Personas_act_caña"]/x["Personas_meta_caña"]*100).fillna(0).astype('float64'),
                    pct_tarjetas=lambda x:(x["Personas_act_tarjetas"]/x["Personas_meta_tarjetas"]*100).fillna(0).astype('float64')
                ).sort_values("pct_act",ascending=False)
                )[cols]
            
            df_oref_totales=df_oref.sum(numeric_only=True).to_frame().T.assign(
                NOM_REP="TOTAL",Etiqueta=" ",
                pct_act=lambda x:(x["Personas_act"]/x["Personas"]*100).fillna(0).astype('float64'),
                pct_caña=lambda x:(x["Personas_act_caña"]/x["Personas_meta_caña"]*100).fillna(0).astype('float64'),
                pct_tarjetas=lambda x:(x["Personas_act_tarjetas"]/x["Personas_meta_tarjetas"]*100).fillna(0).astype('float64')
            )[cols]

            st.markdown(f"<span style='color: {GUINDA}; font-size: 28px; font-weight: bold;'>Avance por OREF</span>", unsafe_allow_html=True)
            st.dataframe(df_oref,width="stretch",column_config=config_df_oref, hide_index=True)
            st.dataframe(df_oref_totales,width="stretch",column_config=config_df_oref, hide_index=True)


    with tab_avance_cader:
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
        df_cader = (cargar_datos(f"""SELECT "NOM_REP","NOM_DDR_PROD","NOM_CAD_PROD","OCHO_ENT", "ACTUALIZADO", sum("Personas") AS "Personas" FROM concentrado {where_oref} GROUP BY "NOM_REP","NOM_DDR_PROD","NOM_CAD_PROD","OCHO_ENT", "ACTUALIZADO";""",parametros_oref)
                    .assign(avance=lambda x: x["Personas"].where(x["ACTUALIZADO"] == "Si", 0))
                    .groupby(["NOM_REP", "NOM_DDR_PROD", "NOM_CAD_PROD",],dropna=False,as_index=False)[["Personas","avance"]]
                    .sum().reset_index(drop=True)
                    .assign(porcentaje=lambda x: (100 * x["avance"] / x["Personas"]).round(2).fillna(0).astype('float64'))
                    .sort_values(["avance"],ascending=False)
                    .rename(columns={"NOM_REP": "OREF", "NOM_DDR_PROD": "DDR", "NOM_CAD_PROD": "CADER", "Personas": "Meta\n(personas)","avance": "Avance\n(personas)", "porcentaje": "Avance\n(%)"})
                    )[["OREF","DDR","CADER","Meta\n(personas)","Avance\n(personas)","Avance\n(%)"]]

        df_cader_totales=df_cader.sum(numeric_only=True).to_frame().T.assign(OREF="TOTAL",DDR="TOTAL",CADER="TOTAL",**{"Avance\n(%)": lambda x: (100 * x["Avance\n(personas)"] / x["Meta\n(personas)"]).round(2).fillna(0).astype('float64')})[["OREF","DDR","CADER","Meta\n(personas)","Avance\n(personas)","Avance\n(%)"]]

        st.markdown(f"<span style='color: {GUINDA}; font-size: 28px; font-weight: bold;'>Avance por OREF-DDR-CADER</span>", unsafe_allow_html=True)
        st.dataframe(df_cader, column_config=config_df_cader, width='stretch', hide_index=True)
        st.dataframe(df_cader_totales, column_config=config_df_cader, width='stretch', hide_index=True)


    with tab_temporal:
        periodo = st.segmented_control("Periodo:", options=["Diario","Semanal", "Mensual"], default="Diario")
        df_temp = cargar_datos(f"""SELECT "dia","semana","mes", sum("Personas") AS "Personas" FROM concentrado {where} GROUP BY "dia","semana","mes";""",parametros)

        if len(df_temp) == 0:
            st.info("No hay datos con fecha de captura para el periodo y filtros seleccionados.")
        else:
            if periodo == "Semanal":
                df_agrupado = df_temp.groupby(df_temp["semana"])["Personas"].sum().reset_index().rename(columns={'semana': 'Categoria'}).sort_values("Categoria").assign(Porcentaje = lambda x: (x["Personas"]/x["Personas"].sum() * 100).round(2).fillna(0).astype('float64'),
                    Acumulado = lambda x: x["Personas"].fillna(0).astype('float64').cumsum() )
                n = 5
            elif  periodo == "Mensual":
                df_agrupado = df_temp.groupby(df_temp["mes"])["Personas"].sum().reset_index().rename(columns={'mes': 'Categoria'}).sort_values("Categoria").assign(Porcentaje = lambda x: (x["Personas"]/x["Personas"].sum() * 100).round(2).fillna(0).astype('float64'),
                    Acumulado = lambda x: x["Personas"].fillna(0).astype('float64').cumsum() )
                periodo = "Mensual"
                n = 6
            else:
                df_agrupado = df_temp.groupby(df_temp["dia"])["Personas"].sum().reset_index().rename(columns={'dia': 'Categoria'}).sort_values("Categoria").assign(Porcentaje = lambda x: (x["Personas"]/x["Personas"].sum() * 100).round(2).fillna(0).astype('float64'),
                    Acumulado = lambda x: x["Personas"].fillna(0).astype('float64').cumsum() )
                periodo = "Diario"
                n = 7

            tab_acum, tab_barras_t, tab_detalle_a_t = st.tabs(["Acumulado", "Por periodo", "Detalle"])

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

# # ═══════════════════════════════════════════════════════════════════════════════
# # TAB 2: ASPECTOS PRODUCTIVOS
# # ═══════════════════════════════════════════════════════════════════════════════

with tab_productivos:
    df_estrategia_ciclo_rh_tipo =f"""
    SELECT
        "Estrategia_predominante" AS "Estrategia predominante",
        -- RH
        COALESCE(SUM("Personas") FILTER (WHERE "regimen_predominante" = 'TEMPORAL'), 0) AS "Temporal",
        COALESCE(SUM("Personas") FILTER (WHERE "regimen_predominante" = 'RIEGO'), 0) AS "Riego",
        COALESCE(SUM("Personas") FILTER (WHERE "regimen_predominante" = 'NO APLICA'), 0) AS "Sin régimen",
        -- Ciclo
        COALESCE(SUM("Personas") FILTER (WHERE "ciclo" = 'PE'), 0) AS "Perenne",
        COALESCE(SUM("Personas") FILTER (WHERE "ciclo" = 'OI'), 0) AS "OI",
        COALESCE(SUM("Personas") FILTER (WHERE "ciclo" = 'PV'), 0) AS "PV",
        SUM("Personas") AS "Total"
    FROM concentrado {where} GROUP BY "Estrategia predominante";
    """
    df_estrategia_ciclo_rh_tipo = cargar_datos(df_estrategia_ciclo_rh_tipo,parametros)
    # Dar formato de número a todo lo que parezca número
    df_estrategia_ciclo_rh_tipo_config = {
        col: st.column_config.NumberColumn(format="accounting",step=1)
        for col in df_estrategia_ciclo_rh_tipo.select_dtypes(include="number").columns
    }
    
    st.markdown(f"<span style='color: {GUINDA}; font-size: 28px; font-weight: bold;'>Personas actualizadas por estrategia</span>", unsafe_allow_html=True)

    st.dataframe(df_estrategia_ciclo_rh_tipo,column_config=df_estrategia_ciclo_rh_tipo_config,hide_index=True)
    if not df_estrategia_ciclo_rh_tipo.empty:
        st.dataframe(df_estrategia_ciclo_rh_tipo.select_dtypes(include="number").sum().to_frame().T.assign(**{"Estrategia_predominante":"Total"}).iloc[:,[-1,*range(0,7)]], column_config=df_estrategia_ciclo_rh_tipo_config, hide_index=True)

    # Falta agregar titulos
    query_grupo_superficie_escala_cambios =f"""
    SELECT
        "Grupo_Superficie" AS "Grupo de superficie",
        -- Escala
        COALESCE(SUM("Personas") FILTER (WHERE "escala" = 'Pequeña'), 0) AS "Pequeña escala",
        COALESCE(SUM("Personas") FILTER (WHERE "escala" = 'Mediana'), 0) AS "Mediana escala",
        -- Cambio Sup
        -- COALESCE(SUM("Personas") FILTER (WHERE "Cambio_sup" = 'A la baja'), 0) AS "Redujeron superficie",
        -- COALESCE(SUM("Personas") FILTER (WHERE "Cambio_sup" = 'Al alza'), 0) AS "Aumentaron superficie",
        -- COALESCE(SUM("Personas") FILTER (WHERE "Cambio_sup" = 'Se mantiene'), 0) AS "Mantienen superficie",
        -- Cambio_cultivo
        -- COALESCE(SUM("Personas") FILTER (WHERE "Cambio_cultivo" = 'Si'), 0) AS "Cambio cultivo(s)",
        -- COALESCE(SUM("Personas") FILTER (WHERE "Cambio_cultivo" = 'No'), 0) AS "Conserva cultivo(s)",
        -- Cambio_regimen
        -- COALESCE(SUM("Personas") FILTER (WHERE "Cambio_regimen" = 'Si'), 0) AS "Cambio régimen",
        -- COALESCE(SUM("Personas") FILTER (WHERE "Cambio_regimen" = 'No'), 0) AS "Conserva régimen",
        -- Cambio_predios
        -- COALESCE(SUM("Personas") FILTER (WHERE "Cambio_predios" = 'A la baja'), 0) AS "Redujeron n° de predios",
        -- COALESCE(SUM("Personas") FILTER (WHERE "Cambio_predios" = 'Al alza'), 0) AS "Aumentaron n° de predios",
        -- COALESCE(SUM("Personas") FILTER (WHERE "Cambio_predios" = 'Se mantiene'), 0) AS "Mantienen n° de predios",
        -- Posesión
        COALESCE(SUM("Personas") FILTER (WHERE "tipo_posesion" = 'PROPIA'), 0) AS "Posesión propia",
        COALESCE(SUM("Personas") FILTER (WHERE "tipo_posesion" = 'DERIVADA'), 0) AS "Posesión derivada",
        SUM("Personas") AS "Total"
    FROM concentrado {where} GROUP BY "Grupo de superficie" ORDER BY "Total" DESC;
    """
    df_grupo_superficie_escala_cambios = cargar_datos(query_grupo_superficie_escala_cambios,parametros)
    # # Dar formato de número a todo lo que parezca número
    df_grupo_superficie_escala_cambios_config = {
        col: st.column_config.NumberColumn(format="accounting",step=1)
        for col in df_grupo_superficie_escala_cambios.select_dtypes(include="number").columns
    }
    st.markdown(f"<span style='color: {GUINDA}; font-size: 28px; font-weight: bold;'>Personas actualizadas por grupo de superficie</span>", unsafe_allow_html=True)
    st.dataframe(df_grupo_superficie_escala_cambios,column_config=df_grupo_superficie_escala_cambios_config,hide_index=True)
    if not df_grupo_superficie_escala_cambios.empty:
        st.dataframe(df_grupo_superficie_escala_cambios.select_dtypes(include="number").sum().to_frame().T.assign(**{"Grupo de superficie":"Total"}).iloc[:,[-1,*range(0,5)]], column_config=df_grupo_superficie_escala_cambios_config, hide_index=True)


# # ═══════════════════════════════════════════════════════════════════════════════
# # TAB 3: PERFIL DEMOGRÁFICO
# # ═══════════════════════════════════════════════════════════════════════════════
with tab_perfil:

    # Falta agregar titulos
    query_grupos_edad_genero =f"""
    SELECT
        "Grupos_Edad" AS "Grupos de edad",
        -- Coordenadas
        COALESCE(SUM("Personas") FILTER (WHERE "Estatus_coordenadas" = 'Congruente'), 0) AS "Coordenada congruente",
        COALESCE(SUM("Personas") FILTER (WHERE "Estatus_coordenadas" = 'Incongruente'), 0) AS "Coordenada incongruente",
        -- Género
        COALESCE(SUM("Personas") FILTER (WHERE "genero" = 'Hombre'), 0) AS "Hombre",
        COALESCE(SUM("Personas") FILTER (WHERE "genero" = 'Mujer'), 0) AS "Mujer",
        -- Indiginas
        COALESCE(SUM("Personas") FILTER (WHERE "Pueblo_originario" = 'Si'), 0) AS "Población indígena",
        COALESCE(SUM("Personas") FILTER (WHERE "Pueblo_originario" = 'No'), 0) AS "Población no indígena",
        SUM("Personas") AS "Total"
    FROM concentrado {where} GROUP BY "Grupos de edad" ORDER BY "Total" DESC;
    """
    df_grupos_edad_genero = cargar_datos(query_grupos_edad_genero,parametros)
    # # Dar formato de número a todo lo que parezca número
    df_grupos_edad_genero_config = {
        col: st.column_config.NumberColumn(format="accounting",step=1)
        for col in df_grupos_edad_genero.select_dtypes(include="number").columns
    }
    st.markdown(f"<span style='color: {GUINDA}; font-size: 28px; font-weight: bold;'>Personas actualizadas por edad, estatus de georreferencia, género y tipo  de población </span>", unsafe_allow_html=True)
    st.dataframe(df_grupos_edad_genero,column_config=df_grupos_edad_genero_config,hide_index=True)
    if not df_grupos_edad_genero.empty:
        st.dataframe(df_grupos_edad_genero.select_dtypes(include="number").sum().to_frame().T.assign(**{"Grupos de edad":"Total"}).iloc[:,[-1,*range(0,7)]], column_config=df_grupos_edad_genero_config, hide_index=True)

with tab_graficos:
    st.markdown(f"<span style='color: {GUINDA}; font-size: 28px; font-weight: bold;'>Gráficos generales de personas actualizadas</span>", unsafe_allow_html=True)

    tab_estrategia , tab_superficies, tab_edades = st.tabs(["Estrategia","Superficies","Edades"])

    with tab_estrategia:
        categoria = "Estrategia_predominante"
        query_estrategia_barras = f"""
            SELECT "{categoria}" AS "Categoria", SUM("Personas") AS "Personas"
            FROM concentrado
            {where}
            GROUP BY "{categoria}"
            ORDER BY "Personas" DESC;
        """
        st.plotly_chart(crear_barras(cargar_datos(query_estrategia_barras,parametros),titulo="Estrategia"))
        

    with tab_superficies:
        categoria = "Grupo_Superficie"
        query_estrategia_barras = f"""
            SELECT "{categoria}" AS "Categoria", SUM("Personas") AS "Personas"
            FROM concentrado
            {where}
            GROUP BY "{categoria}"
            ORDER BY "Personas" DESC;
        """
        st.plotly_chart(crear_barras(cargar_datos(query_estrategia_barras,parametros),titulo="Grupos de superficie"))

    with tab_edades:
        categoria = "Grupos_Edad"
        query_estrategia_barras = f"""
            SELECT "{categoria}" AS "Categoria", SUM("Personas") AS "Personas"
            FROM concentrado
            {where}
            GROUP BY "{categoria}"
            ORDER BY "Personas" DESC;
        """
        st.plotly_chart(crear_barras(cargar_datos(query_estrategia_barras,parametros),titulo="Grupos de edad"))

    categorias = {
        "Ciclo": "ciclo",
        "Régimen hídrico": "regimen_predominante",
        "Escala": "escala",
        "Tipo de posesión": "tipo_posesion",
        "Pueblo originario": "Pueblo_originario",
        "Género": "genero",
    }
    items = list(categorias.items())
    for i in range(0, len(items), 3):
        cols = st.columns(3)
        for col, (titulo, categoria) in zip(cols, items[i:i + 3]):
            query_categoria_dona = f"""
                SELECT "{categoria}", SUM("Personas") AS "Personas"
                FROM concentrado
                {where}
                GROUP BY "{categoria}"
                ORDER BY "Personas" DESC;
            """
            with col:
                st.plotly_chart(crear_dona(cargar_datos(query_categoria_dona, parametros), titulo),width='content',key=f"dona_{categoria}")

with tab_Consultador:

    columnas_nombres = {
        "CVE_REP_PROD": "Clave de OREF",
        "NOM_REP": "Nombre de OREF",
        "NOM_DDR_PROD": "DDR",
        "NOM_CAD_PROD": "CADER",
        # "ACTUALIZADO": "Estatus Actualización",
        "OCHO_ENT": "Fase 1",
        "CONADESUCA": "CONADESUCA",
        "reposición_tarjeta": "Reposición de tarjeta",
        "Estatus_coordenadas": "Estatus de coordenadas",
        "Grupos_Edad": "Grupo de edad",
        "Pueblo_originario": "Pueblo originario",
        # "descripcion_pueblo": "Descripción del pueblo originario",
        "genero": "Género",
        "dia": "Día",
        "semana": "Semana",
        "mes": "Mes",
        # "clave_documento_propiedad": "Clave documento de propiedad",
        # "nombre_documento_propiedad": "Nombre documento de propiedad",
        # "EstatusDocProp": "Estatus documento de propiedad",
        "Grupo_Superficie": "Grupo de superficie",
        "tipo_posesion": "Tipo de posesión",
        "cultivo_predominante": "Cultivo predominante",
        "cultivo": "Cultivo",
        "Estrategia_predominante": "Estrategia predominante",
        "regimen_predominante": "Régimen predominante",
        "ciclo": "Ciclo agrícola",
        "escala": "Escala",
        # "Cambio_sup": "Cambio de superficie",
        # "Cambio_cultivo": "Cambio de cultivo",
        # "Cambio_regimen": "Cambio de régimen",
        # "Cambio_predios": "Cambio de predios",
    }

    st.markdown(f"<span style='color: {GUINDA}; font-size: 28px; font-weight: bold;'>Consultador general</span>", unsafe_allow_html=True)

    columnas_elegidas = st.multiselect(
        "Opciones:", 
        options=columnas_nombres.values(), 
        max_selections=3,
        width=400,
        placeholder="Selecciona hasta 3"
    )

    if columnas_elegidas:
        columnas_seleccionadas = [clave for clave, valor in columnas_nombres.items() if valor in columnas_elegidas]
        columnas = ", ".join([f'"{c}"' for c in columnas_seleccionadas])
        query_consulta = f"""
        SELECT
            {columnas}, "ACTUALIZADO",
            SUM("Personas") AS Personas,
            SUM("Superficie") AS Superficie,
            SUM("Registros") AS Registros
        FROM concentrado
        {where_oref}
        GROUP BY {columnas} , "ACTUALIZADO"
        """
    else:
        query_consulta = f"""
        SELECT
            "ACTUALIZADO",
            SUM("Personas") AS Personas,
            SUM("Superficie") AS Superficie,
            SUM("Registros") AS Registros
        FROM concentrado
        {where_oref} GROUP BY "ACTUALIZADO";
        """
    df_consultador = cargar_datos(query_consulta,parametros_oref)
    df_consultador_config = {
        col: st.column_config.NumberColumn(format="accounting",step=1)
        for col in df_consultador.select_dtypes(include="number").columns
    }
    st.dataframe(df_consultador,column_config=df_consultador_config,hide_index=True)


# # ═══════════════════════════════════════════════════════════════════════════════
# # BOTÓN DE DESCARGA EN EL SIDEBAR
# # ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    if filtro_rep:
        oref_pptx = cargar_datos("""SELECT DISTINCT "CVE_REP_PROD" FROM concentrado WHERE "NOM_REP" = ANY(%s)""",[filtro_rep])["CVE_REP_PROD"].tolist()
    else: 
        oref_pptx = oref_asignada

    if oref_pptx:
        version = (oref_pptx, fecha_datos)
        if st.button("📥 Preparar presentación"):
            with st.spinner("Generando presentación..."):
                st.session_state["presentacion"] = descargar_presentacion(oref_pptx,tipo)
                st.session_state["version"] = version
                st.rerun()
        if (
            st.session_state.get("presentacion") is not None
            and st.session_state.get("version") == version
        ):
            st.download_button(
                "Descargar",
                data=st.session_state["presentacion"],
                file_name=f"{hoy} Reporte Actualización.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )

# # =============================================================================
# # FOOTER
# # =============================================================================

st.divider() # Una línea sutil para separar el contenido
with st.expander("Información Legal y de Privacidad"):
    st.markdown(f"""
    **Aviso de Uso Interno e Informativo**  
    Esta plataforma es una herramienta de consulta exclusiva para el personal autorizado del Gobierno. Desarrollada por el Área de Actualización y Estadística, los resultados presentados son de carácter estrictamente informativo y no constituyen documentos oficiales, resoluciones ni actos administrativos vinculantes.<br> <br>
    © Todos los derechos reservados - Área de Actualización y Estadística.<br>
    """, unsafe_allow_html=True)


    # print(cargar_datos("""SELECT column_name FROM information_schema.columns WHERE table_name = 'concentrado';"""))
