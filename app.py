import streamlit as st
import base64
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import polars as pl
import datetime
from datetime import date
import json


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN INICIAL
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="PROBIEN",
    page_icon="🌽",
    layout="wide"
)

# Colores institucionales
GUINDA = "#621132"
GUINDA_CLARO = "#9F2241"
DORADO = "#D4C19C"
VERDE = "#285C4D"
AMARILLO = "#745526"
VERDE_CLARO = "#3A7D6B"
CREMA = "#F5F1EB"

# Paleta institucional
PALETA_INSTITUCIONAL = ["#10312B", "#691C32", "#D4C19C", "#235B4E", "#9F2241", "#44546A", "#52492E", "#52492E", "#C29E5C"]

# Fuente institucional
FONT_FAMILY = "Noto Sans"
FONT_SIZE_AXIS = 16
FONT_SIZE_TITLE = 18

# Mapeo de nombres: DataFrame (MAYÚSCULAS) → GeoJSON (Title Case)
MAPEO_ESTADOS = {
    "AGUASCALIENTES": "Aguascalientes",
    "BAJA CALIFORNIA": "Baja California",
    "BAJA CALIFORNIA SUR": "Baja California Sur",
    "CAMPECHE": "Campeche",
    "CHIAPAS": "Chiapas",
    "CHIHUAHUA": "Chihuahua",
    "CIUDAD DE MEXICO": "Ciudad de México",
    "COAHUILA DE ZARAGOZA": "Coahuila de Zaragoza",
    "COLIMA": "Colima",
    "DURANGO": "Durango",
    "GUANAJUATO": "Guanajuato",
    "GUERRERO": "Guerrero",
    "HIDALGO": "Hidalgo",
    "JALISCO": "Jalisco",
    "MEXICO": "México",
    "MICHOACAN DE OCAMPO": "Michoacán de Ocampo",
    "MORELOS": "Morelos",
    "NAYARIT": "Nayarit",
    "NUEVO LEON": "Nuevo León",
    "OAXACA": "Oaxaca",
    "PUEBLA": "Puebla",
    "QUERETARO": "Querétaro",
    "QUERETARO DE ARTEAGA": "Querétaro",
    "QUINTANA ROO": "Quintana Roo",
    "SAN LUIS POTOSI": "San Luis Potosí",
    "SINALOA": "Sinaloa",
    "SONORA": "Sonora",
    "TABASCO": "Tabasco",
    "TAMAULIPAS": "Tamaulipas",
    "TLAXCALA": "Tlaxcala",
    "VERACRUZ DE IGNACIO DE LA LLAVE": "Veracruz de Ignacio de la Llave",
    "VERACRUZ": "Veracruz de Ignacio de la Llave",
    "YUCATAN": "Yucatán",
    "ZACATECAS": "Zacatecas",
}


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

hoy = date.today().strftime("%d-%m-%Y")

st.markdown(f"""
    <div style="line-height: 1;">
        <h3 style="margin-bottom: 0;">Proceso de Actualización</h3>
        <p style="font-size: 1.2em; color: {AMARILLO}; margin-top: 0px; font-weight: bold;">
            Fecha del reporte: <span style="color: {VERDE}; font-weight: bold;">{hoy}</span> 
        </p>
    </div>
    """, unsafe_allow_html=True)


@st.cache_data
def cargar_geojson(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def crear_dona(df_dona, titulo, colores_lista=None, height=420):
    if colores_lista is None:
        colores_lista = PALETA_INSTITUCIONAL

    colores = colores_lista[:len(df_dona)]

    fig = px.pie(
        df_dona,
        values="Personas",
        names="Categoria",
        hole=0.45,
        color_discrete_sequence=colores,
    )

    fig.add_annotation(
        text=f"{df_dona['Personas'].sum():,.0f}",
        x=0.5, y=0.5,
        font=dict(size=22, color=GUINDA, family=FONT_FAMILY),
        showarrow=False
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent',
        textfont=dict(size=14, color="white", family=FONT_FAMILY),
        hovertemplate=(
            "%{label}: "
            "%{value:,.0f} "
            "(%{percent}) personas actualizadas"
            "<extra></extra>"
        ),
        marker=dict(line=dict(color='white', width=2))
    )

    fig.update_layout(
        hoverlabel=dict(
            font_size=14, font_family=FONT_FAMILY,
            bgcolor="white", font_color=VERDE, bordercolor=DORADO
        ),
        title=dict(
            text=titulo,
            font=dict(size=FONT_SIZE_TITLE, color=GUINDA, family=FONT_FAMILY),
            x=0.5, xanchor="center"
        ),
        legend=dict(
            font=dict(size=14, family=FONT_FAMILY),
            orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5
        ),
        height=height,
        margin=dict(t=60, b=60, l=10, r=10),
        showlegend=True,
        paper_bgcolor="rgba(0,0,0,0)"
    )

    return fig


def crear_waffle(df_waffle, titulo, colores_lista=None, n_cols=10, n_rows=10, height=420):
    """Waffle simple: cuadros grandes con líneas blancas mínimas."""
    if colores_lista is None:
        colores_lista = PALETA_INSTITUCIONAL

    total = df_waffle["Personas"].sum()

    # Protección: si no hay datos, mostrar gráfico vacío
    if total == 0 or len(df_waffle) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Sin datos disponibles",
            x=0.5, y=0.5, xref="paper", yref="paper",
            font=dict(size=16, color=GUINDA, family=FONT_FAMILY),
            showarrow=False
        )
        fig.update_layout(
            title=dict(text=titulo, font=dict(size=FONT_SIZE_TITLE, color=GUINDA, family=FONT_FAMILY), x=0.5, xanchor="center"),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, showline=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, showline=False),
            height=height,
            margin=dict(t=60, b=60, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig

    df_w = df_waffle.copy().reset_index(drop=True)
    df_w["Cuadros"] = (df_w["Personas"] / total * (n_cols * n_rows)).round().astype(int)

    diff = (n_cols * n_rows) - df_w["Cuadros"].sum()
    if diff != 0:
        # Usar el índice con mayor valor, protegiendo contra series vacías
        df_w_positivo = df_w[df_w["Personas"] > 0]
        if len(df_w_positivo) > 0:
            idx_max = df_w_positivo["Personas"].idxmax()
        else:
            idx_max = 0
        df_w.loc[idx_max, "Cuadros"] += diff

    labels = []
    for idx, row in df_w.iterrows():
        for _ in range(max(0, int(row["Cuadros"]))):
            labels.append(row["Categoria"])

    # Protección si labels quedó vacío
    if len(labels) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Sin datos suficientes",
            x=0.5, y=0.5, xref="paper", yref="paper",
            font=dict(size=16, color=GUINDA, family=FONT_FAMILY),
            showarrow=False
        )
        fig.update_layout(
            title=dict(text=titulo, font=dict(size=FONT_SIZE_TITLE, color=GUINDA, family=FONT_FAMILY), x=0.5, xanchor="center"),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, showline=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, showline=False),
            height=height,
            margin=dict(t=60, b=60, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig

    x_coords = [i % n_cols for i in range(len(labels))]
    y_coords = [n_rows - 1 - i // n_cols for i in range(len(labels))]

    categorias_unicas = df_w["Categoria"].tolist()

    fig = go.Figure()

    for cat_idx, cat in enumerate(categorias_unicas):
        cat_x = [x_coords[i] for i in range(len(labels)) if labels[i] == cat]
        cat_y = [y_coords[i] for i in range(len(labels)) if labels[i] == cat]

        if len(cat_x) == 0:
            continue

        pct = df_w[df_w["Categoria"] == cat]["Personas"].values[0] / total * 100
        personas = df_w[df_w["Categoria"] == cat]["Personas"].values[0]

        fig.add_trace(go.Scatter(
            x=cat_x,
            y=cat_y,
            mode="markers",
            marker=dict(
                size=42,
                symbol="square",
                color=colores_lista[cat_idx % len(colores_lista)],
                line=dict(color="white", width=0.4)
            ),
            name=f"{cat} ( {pct:.1f}% )",
            hovertemplate=(
                f"{cat}: "
                f"{personas:,.0f} "
                f"({pct:.1f}%) personas actualizadas"
                "<extra></extra>"
            ),
            showlegend=True
        ))

    fig.update_layout(
        title=dict(text=titulo, font=dict(size=FONT_SIZE_TITLE, color=GUINDA, family=FONT_FAMILY), x=0.5, xanchor="center"),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, n_cols - 0.5], showline=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, n_rows - 0.5], scaleanchor="x", showline=False),
        hoverlabel=dict(font_size=14, font_family=FONT_FAMILY, bgcolor="white", font_color=VERDE, bordercolor=DORADO),
        legend=dict(font=dict(size=12, family=FONT_FAMILY), orientation="h", yanchor="top", y=-0.05, xanchor="center", x=0.5),
        height=height,
        margin=dict(t=60, b=60, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    return fig

def crear_mapa_calor(df_original, geojson_data, estados_filtrados=None):
    df_estado_meta = df_original.groupby("NOM_EDO_PROD")["Personas"].sum().reset_index()
    df_estado_meta.columns = ["NOM_EDO_PROD", "Meta"]

    df_act_filtro = df_original[df_original["ACTUALIZADO"] == "Si"]
    if len(df_act_filtro) > 0:
        df_act = df_act_filtro.groupby("NOM_EDO_PROD")["Personas"].sum().reset_index()
        df_act.columns = ["NOM_EDO_PROD", "Actualizados"]
    else:
        df_act = pd.DataFrame(columns=["NOM_EDO_PROD", "Actualizados"])

    df_estado_mapa = df_estado_meta.merge(df_act, on="NOM_EDO_PROD", how="left").fillna(0)
    df_estado_mapa["Pendientes"] = df_estado_mapa["Meta"] - df_estado_mapa["Actualizados"]
    df_estado_mapa["Pct_Avance"] = np.where(
        df_estado_mapa["Meta"] > 0,
        (df_estado_mapa["Actualizados"] / df_estado_mapa["Meta"] * 100).round(1),
        0
    )
    df_estado_mapa["Pct_Pendientes"] = (100 - df_estado_mapa["Pct_Avance"]).round(1)
    df_estado_mapa["NOMGEO"] = df_estado_mapa["NOM_EDO_PROD"].map(MAPEO_ESTADOS)

    todos_estados_geo = [f["properties"]["NOMGEO"] for f in geojson_data["features"]]
    df_completo = pd.DataFrame({"NOMGEO": todos_estados_geo})
    df_completo = df_completo.merge(df_estado_mapa, on="NOMGEO", how="left").fillna(0)

    hay_filtro = estados_filtrados is not None and len(estados_filtrados) > 0

    if hay_filtro:
        estados_filtrados_geo = [MAPEO_ESTADOS.get(e, e) for e in estados_filtrados]
        df_completo["Es_Filtrado"] = df_completo["NOMGEO"].isin(estados_filtrados_geo)
    else:
        df_completo["Es_Filtrado"] = df_completo["Meta"] > 0

    df_completo["hover_text"] = df_completo.apply(
        lambda r: (
            f"{r['NOMGEO']}: "
            f"Meta : {r['Meta']:,.0f} (100%), "
            f"Actualizados: {r['Actualizados']:,.0f} ({r['Pct_Avance']:.1f}%), "
            f"Pendientes: {r['Pendientes']:,.0f} ({r['Pct_Pendientes']:.1f}%)"
        ) if r["Meta"] > 0 else f"{r['NOMGEO']}: sin datos en este filtro",
        axis=1
    )

    colorscale_institucional = [
        [0.0, "#691C32"],
        [0.2, "#9F2241"],
        [0.4, "#C29E5C"],
        [0.5, "#52492E"],
        [0.6, "#44546A"],
        [0.8, "#235B4E"],
        [1.0, "#10312B"],
    ]

    fig = go.Figure()

    if hay_filtro:
        df_no_filtrado = df_completo[~df_completo["Es_Filtrado"]].copy()
        df_filtrado_mapa = df_completo[df_completo["Es_Filtrado"]].copy()

        if len(df_no_filtrado) > 0:
            fig.add_trace(go.Choroplethmap(
                geojson=geojson_data,
                locations=df_no_filtrado["NOMGEO"],
                z=[0] * len(df_no_filtrado),
                featureidkey="properties.NOMGEO",
                colorscale=[[0, "#E0E0E0"], [1, "#BDBDBD"]],
                showscale=False,
                text=df_no_filtrado["hover_text"],
                hoverinfo="text",
                marker=dict(opacity=0.5, line=dict(width=0.8, color="white"))
            ))

        if len(df_filtrado_mapa) > 0:
            fig.add_trace(go.Choroplethmap(
                geojson=geojson_data,
                locations=df_filtrado_mapa["NOMGEO"],
                z=df_filtrado_mapa["Pct_Avance"],
                featureidkey="properties.NOMGEO",
                colorscale=colorscale_institucional,
                zmin=0, zmax=100,
                showscale=True,
                colorbar=dict(
                    title=dict(text="% Avance", font=dict(size=14, family=FONT_FAMILY)),
                    tickfont=dict(size=12, family=FONT_FAMILY),
                    ticksuffix="%", len=0.8, thickness=12, x=1.0, xpad=2
                ),
                text=df_filtrado_mapa["hover_text"],
                hoverinfo="text",
                marker=dict(opacity=0.9, line=dict(width=1.2, color="white"))
            ))
    else:
        df_con_datos = df_completo[df_completo["Meta"] > 0].copy()
        df_sin_datos = df_completo[df_completo["Meta"] == 0].copy()

        if len(df_sin_datos) > 0:
            fig.add_trace(go.Choroplethmap(
                geojson=geojson_data,
                locations=df_sin_datos["NOMGEO"],
                z=[0] * len(df_sin_datos),
                featureidkey="properties.NOMGEO",
                colorscale=[[0, "#E0E0E0"], [1, "#BDBDBD"]],
                showscale=False,
                text=df_sin_datos["hover_text"],
                hoverinfo="text",
                marker=dict(opacity=0.5, line=dict(width=0.8, color="white"))
            ))

        if len(df_con_datos) > 0:
            fig.add_trace(go.Choroplethmap(
                geojson=geojson_data,
                locations=df_con_datos["NOMGEO"],
                z=df_con_datos["Pct_Avance"],
                featureidkey="properties.NOMGEO",
                colorscale=colorscale_institucional,
                zmin=0, zmax=100,
                showscale=True,
                colorbar=dict(
                    title=dict(text="% Avance", font=dict(size=14, family=FONT_FAMILY)),
                    tickfont=dict(size=12, family=FONT_FAMILY),
                    ticksuffix="%", len=0.8, thickness=12, x=1.0, xpad=2
                ),
                text=df_con_datos["hover_text"],
                hoverinfo="text",
                marker=dict(opacity=0.9, line=dict(width=1, color="white"))
            ))

    fig.update_layout(
        map=dict(
            style="white-bg",
            zoom=4.2,
            center=dict(lat=23.6345, lon=-102.5528),
        ),
        title=dict(
            text="Mapa de Avance por Entidad Federativa",
            font=dict(size=FONT_SIZE_TITLE, color=GUINDA, family=FONT_FAMILY),
            x=0.5, xanchor="center"
        ),
        hoverlabel=dict(
            font_size=16, font_family=FONT_FAMILY,
            bgcolor="white", font_color=VERDE, bordercolor=DORADO
        ),
        height=800,
        margin=dict(t=50, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)"
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


# ═══════════════════════════════════════════════════════════════════════════════
# LOGOS + ESTILOS CSS
# ═══════════════════════════════════════════════════════════════════════════════

l1, l2, l3 = img_to_b64("logo1.png"), img_to_b64("logo2.png"), img_to_b64("logo3.png")

st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@300;400;600;700;900&display=swap');

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
        /* Botón clear del multiselect visible */
        [data-testid="stSidebar"] * {{
            color: white !important;
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
geojson_data = cargar_geojson("Mapa_estatal_2022_INEGI.geojson")


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR - FILTROS
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(f"""
        
            Panel de Control
        
    """, unsafe_allow_html=True)

    opcion = st.selectbox("Seleccionar proceso", ["Nacional", "Prueba piloto (8 estados)", "Caña","Reposición de tarjetas"])

filtros = {
    "Nacional": None,
    "Caña": df["CONADESUCA"] == "Si",
    "Prueba piloto (8 estados)": df["NOM_EDO_PROD"].isin([
        "CIUDAD DE MEXICO", "DURANGO", "MORELOS", "NAYARIT",
        "PUEBLA", "QUERETARO DE ARTEAGA", "TLAXCALA", "ZACATECAS"
    ])
}

condicion = filtros.get(opcion)
if condicion is not None:
    df = df[condicion]

with st.sidebar:
    estados = st.multiselect(
        "Seleccionar estados",
        options=sorted(df["NOM_EDO_PROD"].unique()),
        default=[],
        placeholder="Todos los estados"
    )

# Guardar copia para el mapa
df_para_mapa = df.copy()
estados_seleccionados = estados if len(estados) > 0 else None

if len(estados) > 0:
    df = df[df["NOM_EDO_PROD"].isin(estados)]

# Meta - protección contra DataFrame vacío
meta = df['Personas'].sum() if len(df) > 0 else 0

# Filtro por fecha
if len(df) > 0:
    inicio = df["fecha_captura"].min().date() if pd.notna(df["fecha_captura"].min()) else datetime.date(2025, 12, 3)
    fin = df["fecha_captura"].max().date() if pd.notna(df["fecha_captura"].max()) else datetime.date.today()
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
            ((df["fecha_captura"] >= pd.to_datetime(fecha_ini)) &
             (df["fecha_captura"] <= pd.to_datetime(fecha_fin))) |
            (df["fecha_captura"].isna())
        ]
    if len(df_para_mapa) > 0:
        df_para_mapa = df_para_mapa[
            ((df_para_mapa["fecha_captura"] >= pd.to_datetime(fecha_ini)) &
             (df_para_mapa["fecha_captura"] <= pd.to_datetime(fecha_fin))) |
            (df_para_mapa["fecha_captura"].isna())
        ]

# ═══════════════════════════════════════════════════════════════════════════════
# KPIs
# ═══════════════════════════════════════════════════════════════════════════════

actualizados = df[df['ACTUALIZADO'] == 'Si']['Personas'].sum() if len(df) > 0 else 0
pendientes = meta - actualizados
pct_avance = actualizados / meta * 100 if meta > 0 else 0

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Meta de actualización", f"{meta:,.0f}", "100%")

with col2:
    st.metric("Personas actualizadas", f"{actualizados:,.0f}", f"{pct_avance:.1f}%")

with col3:
    st.metric("Pendientes de actualizar", f"{pendientes:,.0f}", f"{100 - pct_avance:.1f}%", delta_color="inverse")


# ═══════════════════════════════════════════════════════════════════════════════
# TABS PRINCIPALES
# ═══════════════════════════════════════════════════════════════════════════════

tab_avance, tab_cambios, tab_perfil, tab_detalle = st.tabs([
    "Avance General",
    "Indicadores",
    "Perfil Demográfico",
    "Detalle de Registros"
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: AVANCE GENERAL
# ═══════════════════════════════════════════════════════════════════════════════

with tab_avance:

    tab_mapa, tab_barras_estado, tab_temporal = st.tabs([
        "Mapa de calor",
        "Avance por Estado",
        "Avance Temporal"
    ])

    with tab_mapa:
        fig_mapa = crear_mapa_calor(df_para_mapa, geojson_data, estados_seleccionados)
        st.plotly_chart(fig_mapa, width='stretch')

    with tab_barras_estado:
        df_estado = df.groupby(["NOM_EDO_PROD", "ACTUALIZADO"])["Personas"].sum().reset_index()
        df_total = df_estado.groupby("NOM_EDO_PROD")["Personas"].sum().reset_index()
        df_total.columns = ["NOM_EDO_PROD", "Total"]
        df_estado = df_estado.merge(df_total, on="NOM_EDO_PROD")
        df_estado["Porcentaje"] = (df_estado["Personas"] / df_estado["Total"] * 100).round(1)
        df_estado["Estatus"] = df_estado["ACTUALIZADO"].map({"Si": "actualizadas", "No": "pendientes"})

        df_actualizado_e = df_estado[df_estado["Estatus"] == "actualizadas"].copy()
        df_orden = pd.DataFrame({"NOM_EDO_PROD": df_total["NOM_EDO_PROD"].unique()})
        df_orden = df_orden.merge(df_actualizado_e[["NOM_EDO_PROD", "Porcentaje"]], on="NOM_EDO_PROD", how="left").fillna(0)
        orden_estados = df_orden.sort_values("Porcentaje", ascending=False)["NOM_EDO_PROD"].tolist()

        color_map = {"actualizadas": "#235B4E", "pendientes": "#D4C19C"}

        fig_estado = px.bar(
            df_estado, x="NOM_EDO_PROD", y="Porcentaje", color="Estatus",
            text=df_estado["Porcentaje"].apply(lambda x: f"{x:.1f}%"),
            custom_data=["NOM_EDO_PROD", "Personas", "Porcentaje", "Estatus"],
            color_discrete_map=color_map,
            category_orders={"NOM_EDO_PROD": orden_estados, "Estatus": ["actualizadas", "pendientes"]},
            barmode="stack",
        )
        fig_estado.update_traces(
            textposition='inside', insidetextanchor='middle',
            textfont=dict(size=11, color="white", family=FONT_FAMILY),
            hovertemplate="%{customdata[0]}: %{customdata[1]:,.0f} (%{customdata[2]:.1f}%) personas %{customdata[3]} <extra></extra>"
        )
        fig_estado.update_layout(
            title=dict(text="Avance por Entidad Federativa", font=dict(size=FONT_SIZE_TITLE, color=GUINDA, family=FONT_FAMILY)),
            hoverlabel=dict(font_size=14, font_family=FONT_FAMILY, bgcolor="white", font_color=VERDE, bordercolor=DORADO),
            xaxis=dict(title=dict(text="Entidad Federativa", font=dict(size=FONT_SIZE_AXIS, color="black", family=FONT_FAMILY)), tickfont=dict(size=11, color="black", family=FONT_FAMILY), tickangle=-45),
            yaxis=dict(title=dict(text="Porcentaje (%)", font=dict(size=FONT_SIZE_AXIS, color="black", family=FONT_FAMILY)), tickfont=dict(size=14, color="black", family=FONT_FAMILY), range=[0, 115], ticksuffix="%", dtick=20),
            bargap=0.15, height=560, template="plotly_white",
            legend=dict(title=dict(text="Estatus", font=dict(size=14, color="black", family=FONT_FAMILY)), font=dict(size=14, family=FONT_FAMILY), orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            margin=dict(l=50, t=80, r=30, b=130), uniformtext_minsize=9, uniformtext_mode='hide', paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_estado, width='stretch')

    with tab_temporal:
        periodo = st.segmented_control("Periodo:", options=["Semanal", "Mensual"], default="Mensual")

        df["fecha_captura"] = pd.to_datetime(df["fecha_captura"])
        df_temp = df.dropna(subset=["fecha_captura"]).copy()

        if len(df_temp) == 0:
            st.info("No hay datos con fecha de captura para el periodo y filtros seleccionados.")
        else:
            if periodo == "Semanal":
                df_agrupado = df_temp.groupby(df_temp["semana"].dt.strftime("%Y-%m-%d"))["Personas"].sum().reset_index()
                df_agrupado.columns = ["Fecha", "Cantidad"]
            else:
                df_agrupado = df_temp.groupby(df_temp["mes"])["Personas"].sum().reset_index()
                df_agrupado.columns = ["Fecha", "Cantidad"]
                periodo = "Mensual"

            df_filtrado = df_agrupado.copy()
            total_personas = df_filtrado["Cantidad"].sum()
            df_filtrado["Porcentaje"] = (df_filtrado["Cantidad"] / total_personas * 100).round(1) if total_personas > 0 else 0
            df_filtrado["Acumulado"] = df_filtrado["Cantidad"].cumsum()

            tab_barras_t, tab_acum, tab_linea = st.tabs(["Barras", "Acumulado", "Línea"])

            with tab_barras_t:
                fig_b = px.bar(df_filtrado, x="Fecha", y="Cantidad", text="Cantidad", custom_data=["Fecha", "Cantidad", "Porcentaje"], color_discrete_sequence=[DORADO])
                fig_b.update_traces(texttemplate='%{text:,.0f}', textposition='outside', textfont=dict(size=14, color=VERDE, family=FONT_FAMILY), hovertemplate="%{customdata[0]}: %{customdata[1]:,.0f} (%{customdata[2]:.1f}%) personas actualizadas<extra></extra>", marker_line_color="#52492E", marker_line_width=1.5, cliponaxis=False)
                fig_b.update_layout(title=dict(text=f"Avance {periodo}", font=dict(size=FONT_SIZE_TITLE, color=GUINDA, family=FONT_FAMILY)), hoverlabel=dict(font_size=14, font_family=FONT_FAMILY, bgcolor="white", font_color=VERDE, bordercolor=DORADO), xaxis=dict(title=dict(text="Periodo", font=dict(size=FONT_SIZE_AXIS, color="black", family=FONT_FAMILY)), tickfont=dict(size=14, color="black", family=FONT_FAMILY), tickangle=-45), yaxis=dict(title=dict(text="Personas", font=dict(size=FONT_SIZE_AXIS, color="black", family=FONT_FAMILY)), tickfont=dict(size=14, color="black", family=FONT_FAMILY), range=[0, df_filtrado["Cantidad"].max() * 1.25]), height=500, template="plotly_white", margin=dict(t=80, b=100), paper_bgcolor="rgba(0,0,0,0)", bargap=0.15)
                st.plotly_chart(fig_b, width='stretch')

            with tab_acum:
                fig_a = go.Figure()
                fig_a.add_trace(go.Scatter(x=df_filtrado["Fecha"], y=df_filtrado["Acumulado"], mode="lines+markers+text", text=df_filtrado["Acumulado"].apply(lambda x: f"{x:,.0f}"), textposition="top center", textfont=dict(size=13, color=GUINDA, family=FONT_FAMILY), line=dict(color="#235B4E", width=3), marker=dict(size=10, color="#235B4E", line=dict(color="white", width=2)), fill="tozeroy", fillcolor="rgba(35, 91, 78, 0.08)", customdata=np.column_stack([df_filtrado["Fecha"], df_filtrado["Acumulado"], df_filtrado["Cantidad"]]), hovertemplate="%{customdata[0]}: %{customdata[1]:,.0f} personas actualizadas (%{customdata[2]:,.0f} del periodo)<extra></extra>"))
                fig_a.update_layout(title=dict(text=f"Acumulado {periodo}", font=dict(size=FONT_SIZE_TITLE, color=GUINDA, family=FONT_FAMILY)), hoverlabel=dict(font_size=14, font_family=FONT_FAMILY, bgcolor="white", font_color=VERDE, bordercolor=DORADO), xaxis=dict(tickangle=-45, title=dict(text="Periodo", font=dict(size=FONT_SIZE_AXIS, color="black", family=FONT_FAMILY)), tickfont=dict(size=14, color="black", family=FONT_FAMILY)), yaxis=dict(title=dict(text="Personas acumuladas", font=dict(size=FONT_SIZE_AXIS, color="black", family=FONT_FAMILY)), tickfont=dict(size=14, color="black", family=FONT_FAMILY)), height=500, template="plotly_white", margin=dict(t=80, b=100), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_a, width='stretch')

            with tab_linea:
                fig_l = go.Figure()
                fig_l.add_trace(go.Scatter(x=df_filtrado["Fecha"], y=df_filtrado["Cantidad"], mode="lines+markers+text", text=df_filtrado["Cantidad"].apply(lambda x: f"{x:,.0f}"), textposition="top center", textfont=dict(size=13, color=GUINDA, family=FONT_FAMILY), line=dict(color="#C29E5C", width=3, shape="spline"), marker=dict(size=10, color="#691C32", line=dict(color="white", width=2)), customdata=np.column_stack([df_filtrado["Fecha"], df_filtrado["Cantidad"], df_filtrado["Porcentaje"]]), hovertemplate="%{customdata[0]}: %{customdata[1]:,.0f} (%{customdata[2]:.1f}%) personas actualizadas<extra></extra>"))
                fig_l.update_layout(title=dict(text=f"Tendencia {periodo}", font=dict(size=FONT_SIZE_TITLE, color=GUINDA, family=FONT_FAMILY)), hoverlabel=dict(font_size=14, font_family=FONT_FAMILY, bgcolor="white", font_color=VERDE, bordercolor=DORADO), xaxis=dict(tickangle=-45, title=dict(text="Periodo", font=dict(size=FONT_SIZE_AXIS, color="black", family=FONT_FAMILY)), tickfont=dict(size=14, color="black", family=FONT_FAMILY)), yaxis=dict(title=dict(text="Personas", font=dict(size=FONT_SIZE_AXIS, color="black", family=FONT_FAMILY)), tickfont=dict(size=14, color="black", family=FONT_FAMILY), range=[0, df_filtrado["Cantidad"].max() * 1.3]), height=500, template="plotly_white", margin=dict(t=80, b=100), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_l, width='stretch')


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: ANÁLISIS DE CAMBIOS
# ═══════════════════════════════════════════════════════════════════════════════

with tab_cambios:
    separador("Análisis de cambios detectados")

    col1, col2, col3 = st.columns(3)
    columnas_c = [col1, col2, col3]

    variables_dona_1 = {
        "Cambio_sup": "Cambio de Superficie",
        "Cambio_cultivo": "Cambio de Cultivo",
        "tipo_posesion": "Tipo de Posesión"
    }

    for i, (variable, titulo) in enumerate(variables_dona_1.items()):
        df_dona = df.groupby(variable)["Personas"].sum().reset_index()
        df_dona.columns = ["Categoria", "Personas"]
        with columnas_c[i]:
            tab_d, tab_w = st.tabs(["Dona", "Waffle"])
            with tab_d:
                st.plotly_chart(crear_dona(df_dona, titulo), width='stretch')
            with tab_w:
                st.plotly_chart(crear_waffle(df_dona, titulo), width='stretch')

    separador()

    col1, col2, col3 = st.columns(3)
    columnas_c2 = [col1, col2, col3]

    variables_dona_2 = {
        "regimen": "Régimen hídrico",
        "ciclo": "Ciclo productivo",
        "genero": "Género",
    }

    for i, (variable, titulo) in enumerate(variables_dona_2.items()):
        df_dona = df.groupby(variable)["Personas"].sum().reset_index()
        df_dona.columns = ["Categoria", "Personas"]
        if variable == "genero":
            colores_var = ["#235B4E", "#691C32", "#C29E5C"]
        else:
            colores_var = None
        with columnas_c2[i]:
            tab_d2, tab_w2 = st.tabs(["Dona", "Waffle"])
            with tab_d2:
                st.plotly_chart(crear_dona(df_dona, titulo, colores_lista=colores_var), width='stretch')
            with tab_w2:
                st.plotly_chart(crear_waffle(df_dona, titulo, colores_lista=colores_var), width='stretch')


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: PERFIL DEMOGRÁFICO
# ═══════════════════════════════════════════════════════════════════════════════

with tab_perfil:
    separador("Distribución por Edad")

    df_edad = df.groupby(["Ord_Grupos_Edad", "Grupos_Edad"])["Personas"].sum().reset_index()
    df_edad = df_edad.sort_values("Ord_Grupos_Edad").reset_index(drop=True)
    total_personas_edad = df_edad["Personas"].sum()
    df_edad["Porcentaje"] = (df_edad["Personas"] / total_personas_edad * 100).round(1) if total_personas_edad > 0 else 0
    colores_edad = (PALETA_INSTITUCIONAL * 3)[:len(df_edad)]

    tab_edad_barras, tab_edad_waffle = st.tabs(["Barras por Edad", "Waffle por Edad"])

    with tab_edad_barras:
        fig_edad_v = px.bar(df_edad, x="Grupos_Edad", y="Personas", text="Personas", color="Grupos_Edad", custom_data=["Grupos_Edad", "Personas", "Porcentaje"], color_discrete_sequence=colores_edad, category_orders={"Grupos_Edad": df_edad["Grupos_Edad"].tolist()})
        fig_edad_v.update_traces(texttemplate='%{text:,.0f}', textposition='outside', textfont=dict(size=13, color=VERDE, family=FONT_FAMILY), hovertemplate="%{customdata[0]} años: %{customdata[1]:,.0f} (%{customdata[2]:.1f}%) personas actualizadas<extra></extra>", cliponaxis=False, marker_line_color="white", marker_line_width=1.5)
        fig_edad_v.update_layout(title=dict(text="Distribución por Grupos de Edad", font=dict(size=FONT_SIZE_TITLE, color=GUINDA, family=FONT_FAMILY)), xaxis=dict(title=dict(text="Grupo de Edad", font=dict(size=FONT_SIZE_AXIS, color="black", family=FONT_FAMILY)), tickangle=-45, tickfont=dict(size=12, color="black", family=FONT_FAMILY)), yaxis=dict(title=dict(text="Personas", font=dict(size=FONT_SIZE_AXIS, color="black", family=FONT_FAMILY)), tickfont=dict(size=14, color="black", family=FONT_FAMILY), range=[0, df_edad["Personas"].max() * 1.25] if len(df_edad) > 0 else [0, 1]), hoverlabel=dict(font_size=14, font_family=FONT_FAMILY, bgcolor="white", font_color=VERDE, bordercolor=DORADO), showlegend=False, bargap=0.2, height=500, template="plotly_white", margin=dict(t=60, b=100, l=50, r=20), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_edad_v, width='stretch')

    with tab_edad_waffle:
        df_edad_waffle = df_edad[["Grupos_Edad", "Personas"]].copy()
        df_edad_waffle.columns = ["Categoria", "Personas"]
        st.plotly_chart(crear_waffle(df_edad_waffle, "Proporción por Edad", colores_lista=colores_edad, height=500), width='stretch')

    separador("Estatus documental y geográfico")

    col1, col2 = st.columns(2)

    df_coord = df.groupby("Estatus_coordenadas")["Personas"].sum().reset_index()
    df_coord.columns = ["Categoria", "Personas"]

    with col1:
        tab_coord_dona, tab_coord_waffle = st.tabs(["Dona - Coordenadas", "Waffle - Coordenadas"])
        with tab_coord_dona:
            st.plotly_chart(crear_dona(df_coord, "Estatus de coordenadas", height=420), width='stretch')
        with tab_coord_waffle:
            st.plotly_chart(crear_waffle(df_coord, "Estatus de coordenadas", height=420), width='stretch')

    df_doc = df.groupby("EstatusDocProp")["Personas"].sum().reset_index()
    df_doc.columns = ["Categoria", "Personas"]

    with col2:
        tab_doc_dona, tab_doc_waffle = st.tabs(["Dona - Documento", "Waffle - Documento"])
        with tab_doc_dona:
            st.plotly_chart(crear_dona(df_doc, "Documento de posesión", height=420), width='stretch')
        with tab_doc_waffle:
            st.plotly_chart(crear_waffle(df_doc, "Documento de posesión", height=420), width='stretch')


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: DETALLE DE REGISTROS
# ═══════════════════════════════════════════════════════════════════════════════

with tab_detalle:
    separador("Detalle de Registros")

    tab_cultivo, tab_entidad, tab_cader = st.tabs(["Resumen por cultivo","Resumen por entidad federativa", "Resumen por cader"])

    with tab_cultivo:
        if "NOM_CULTIVO" in df.columns:
            df_cultivo = df.groupby("NOM_CULTIVO")["Personas"].sum().reset_index()
            df_cultivo = df_cultivo.sort_values("Personas", ascending=False).head(20)
            df_cultivo["Porcentaje"] = (df_cultivo["Personas"] / df_cultivo["Personas"].sum() * 100).round(1)

            fig_cultivo = px.bar(df_cultivo.sort_values("Personas", ascending=True), y="NOM_CULTIVO", x="Personas", text=df_cultivo.sort_values("Personas", ascending=True).apply(lambda r: f"{r['Personas']:,.0f}", axis=1), color_discrete_sequence=["#235B4E"], orientation="h")
            fig_cultivo.update_traces(textposition='outside', textfont=dict(size=13, color=VERDE, family=FONT_FAMILY), hovertemplate="%{y}  Personas : %{x:,.0f} <extra></extra>", cliponaxis=False, marker_line_color="white", marker_line_width=1)
            fig_cultivo.update_layout(title=dict(text="Top 20 Cultivos", font=dict(size=FONT_SIZE_TITLE, color=GUINDA, family=FONT_FAMILY)), yaxis=dict(title=dict(text="Cultivo", font=dict(size=FONT_SIZE_AXIS, color="black", family=FONT_FAMILY)), tickfont=dict(size=12, color="black", family=FONT_FAMILY)), xaxis=dict(title=dict(text="Personas", font=dict(size=FONT_SIZE_AXIS, color="black", family=FONT_FAMILY)), tickfont=dict(size=14, color="black", family=FONT_FAMILY)), hoverlabel=dict(font_size=14, font_family=FONT_FAMILY, bgcolor="white", font_color=VERDE, bordercolor=DORADO), height=600, template="plotly_white", margin=dict(t=60, b=40, l=180, r=80), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_cultivo, width='stretch')
            st.dataframe(df_cultivo[["NOM_CULTIVO", "Personas", "Porcentaje"]].rename(columns={"NOM_CULTIVO": "Cultivo", "Porcentaje": "% del total"}), width='stretch', hide_index=True)
        else:
            st.info("Columna 'NOM_CULTIVO' no disponible.")

    with tab_entidad:
        if "NOM_EDO_PROD" in df.columns:
            df_pivot = df.groupby(["NOM_EDO_PROD", "genero", "regimen"])["Personas"].sum().reset_index()

            tabla_pivot = df_pivot.pivot_table(
                index="NOM_EDO_PROD",
                columns=["genero", "regimen"],
                values="Personas",
                aggfunc="sum",
                fill_value=0,
                margins=True,
                margins_name="Total"
            )

            tabla_pivot.columns = [f"{g} - {r}" if g != "Total" else "Total" for g, r in tabla_pivot.columns]

            if "Total" in tabla_pivot.index:
                fila_total = tabla_pivot.loc[["Total"]]
                tabla_sin_total = tabla_pivot.drop("Total").sort_values("Total", ascending=False)
                tabla_pivot = pd.concat([tabla_sin_total, fila_total])

            tabla_pivot = tabla_pivot.reset_index().rename(columns={"NOM_EDO_PROD": "Entidad Federativa"})

            st.dataframe(tabla_pivot, width='stretch', hide_index=True)
        else:
            st.info("Columna 'NOM_EDO_PROD' no disponible.")

    with tab_cader:
        if "NOM_CADER" in df.columns:
            df_cader = df.groupby(["NOM_EDO_PROD", "NOM_CADER"])["Personas"].sum().reset_index()
            df_cader = df_cader.sort_values("Personas", ascending=False).head(30)
            st.dataframe(df_cader.rename(columns={"NOM_EDO_PROD": "Estado", "NOM_CADER": "CADER", "Personas": "Total Personas"}), width='stretch', hide_index=True)
        else:
            st.info("Columna 'NOM_CADER' no disponible.")


# ═══════════════════════════════════════════════════════════════════════════════
# BOTÓN DE DESCARGA EN EL SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown(f"""
    Generar presentación en PDF
    
""", unsafe_allow_html=True)

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

if st.button("Descargar informe", type="primary"):
    st.toast("Procesando presentación", icon="⚙️")

# from generar_archivo_pdf import generar_presentacion_pdf
# 2. Tu botón (se pintará automáticamente con el CSS de arriba)
# st.download_button(
#     label="Generar y Descargar PDF",
#     data=lambda: generar_presentacion_pdf(df, meta, actualizados, pendientes, pct_avance, hoy),
#     file_name=f"Presentacion_PROBIEN_{hoy}.pdf",
#     mime="application/pdf",
#     use_container_width=True,
#     on_click=lambda: st.toast("¡Preparando descarga!", icon="📥")  # 👈 Mensaje flotante
# )


# =============================================================================
# FOOTER
# =============================================================================

st.divider() # Una línea sutil para separar el contenido
with st.expander("Información Legal y de Privacidad"):
    st.markdown("""
    **Aviso de Uso Interno e Informativo**  
    Esta plataforma es una herramienta de consulta exclusiva para el personal autorizado del Gobierno. Desarrollada por el Área de Estadística y Actualización, los resultados presentados son de carácter estrictamente informativo y no constituyen documentos oficiales, resoluciones ni actos administrativos vinculantes.

    Este software es de código abierto distribuido bajo la Licencia MIT. - Área de Estadística y Actualización.
    """)
