import streamlit as st
import base64
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import geopandas as gpd
import numpy as np
import json
import polars as pl
import datetime 
from datetime import date


# Configuración inicial obligatoria
st.set_page_config(
    page_title="PROBIEN",
    page_icon="🌽",
    layout="wide"
)


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


# Colores SADER
GUINDA = "#621132"
DORADO = "#D4C19C"
VERDE = "#285C4D"
AMARILLO = "#745526"
hoy = date.today().strftime("%d-%m-%Y")

st.markdown(f"""
    <div style="line-height: 1;">
        <h3 style="margin-bottom: 0;">Proceso de Actualización</h3>
        <p style="font-size: 1.2em; color: {AMARILLO}; margin-top: 0px; font-weight: bold;">
            Fecha del reporte: <span style="color: {VERDE}; font-weight: bold;">{hoy}</span> 
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
    <style>
    button[data-testid="stBaseButton-segmented_controlActive"] {{
        border-color: {VERDE} !important;
        background-color: {DORADO} !important;
        color: white !important;
    }}
    button[data-testid="stBaseButton-segmented_control"]:hover {{
        border-color: {VERDE} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# 4. Contenido de Streamlit (Aquí van tus gráficas y filtros)

@st.cache_data
def import_df(ruta):
    return pl.read_parquet(ruta).to_pandas()

df = import_df("concentrado_actualizados.parquet")


color_foco = "#285C4D"  # Rojo Streamlit o usa tu Hexadecimal

st.markdown(f"""
    <style>
    /* --- MULTISELECT (Tus estilos actuales) --- */
    span[data-baseweb="tag"] {{
        background-color: {color_foco} !important;
    }}
    span[data-baseweb="tag"] span {{
        color: white !important;
    }}
    span[data-baseweb="tag"] svg {{
        fill: white !important;
    }}
    div[data-baseweb="select"] > div:focus-within {{
        border-color: {color_foco} !important;
        box-shadow: 0 0 0 1px {color_foco} !important;
    }}

    /* --- DATE INPUT (Círculos del calendario) --- */
    /* Cambia el color del círculo del día seleccionado y el rango */
    div[data-baseweb="calendar"] div[aria-selected="true"] {{
        background-color: {color_foco} !important;
        color: white !important;
    }}
    
    /* Cambia el color del círculo al pasar el mouse sobre un día */
    div[data-baseweb="calendar"] div:hover:not([aria-selected="true"]) {{
        border-color: {color_foco} !important;
    }}

    /* --- DATAFRAME (Foco de celdas) --- */
    /* Para el componente interactivo (Glide Data Grid) */
    [data-testid="stDataFrame"] > div:focus-within {{
        border: 0.5px solid {color_foco} !important;
        box-shadow: 0 0 0 0.5px {color_foco} !important;
    }}

    /* --- ESTILO EXTRA PARA EL INPUT DE FECHA --- */
    div[data-baseweb="input"]:focus-within {{
        border-color: {color_foco} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# Filtrar por proceso
# Definimos los criterios de filtrado en un diccionario
with st.sidebar:
    st.header("Filtros")
    opcion = st.selectbox("Seleccionar proceso", ["Nacional", "Prueba piloto (8 estados)", "Caña"])

# 1. Definimos las condiciones 
filtros = {
    "Nacional": None,  # No aplicamos filtro, queda el original
    "Caña": df["CONADESUCA"] == "Si",
    "Prueba piloto (8 estados)": df["NOM_EDO_PROD"].isin([
        "CIUDAD DE MEXICO", "DURANGO", "MORELOS", "NAYARIT", 
        "PUEBLA", "QUERETARO DE ARTEAGA", "TLAXCALA", "ZACATECAS"
    ])
}
# 2. Aplicamos la lógica de filtrado
condicion = filtros.get(opcion)
if condicion is not None:
    df = df[condicion]

#####################################
# Filtros por estado
with st.sidebar:
    estados = st.multiselect(
        "Seleccionar estados",
            options=sorted(df["NOM_EDO_PROD"].unique()),
            default=[],
            placeholder="Todos los estados"
    )

if len(estados) > 0:
    df = df[df["NOM_EDO_PROD"].isin(estados)]

# Filtro por fecha de captura
inicio = df["fecha_captura"].min().date() if pd.notna(df["fecha_captura"].min()) else datetime.date(2025, 12, 3)
fin = df["fecha_captura"].max().date() if pd.notna(df["fecha_captura"].max()) else datetime.date.today()

with st.sidebar:
    # 2. Generamos una clave única basada en los datos filtrados
    # Esto fuerza el refresco cada vez que inicio o fin cambian
    clave_dinamica = f"fecha_{inicio}_{fin}_{opcion}_{len(estados)}"
    
    fecha = st.date_input(
        "Filtrar información por fecha", 
        value=(inicio, fin),
        format="DD/MM/YYYY",
        key=clave_dinamica  # <--- Esta es la clave
    )

if len(fecha)==2:
    df = df[
        ((df["fecha_captura"] >= pd.to_datetime(fecha[0])) &
        (df["fecha_captura"] <= pd.to_datetime(fecha[1]))) | 
        (df["fecha_captura"].isna())
    ]

st.markdown(f"""
    <style>
    [data-testid="stMetric"] {{
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background-color: #f8f9fa;
        border: 3px solid {DORADO};
        border-radius: 20px;
        padding: 2px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    [data-testid="stMetricLabel"] {{
        display: flex;
        justify-content: center;
        color: {VERDE};
    }}
    [data-testid="stMetricValue"] {{
        display: flex;
        justify-content: center;
        color: {GUINDA};
        font-weight: bold;
    }}
    </style>
""", unsafe_allow_html=True)

# Métricas rápidas (KPIs) de la PO y actualizados
col1, col2, col3,  = st.columns(3)
# col1.metric(f"Meta de actualización de personas", f"{df['Personas'].sum():,.0f}", "100%")
# col2.metric("Personas actualizadas", f"{df[df['ACTUALIZADO'] == 'Si']['Personas'].sum():,.0f}", f"{df[df['ACTUALIZADO'] == 'Si']['Personas'].sum()/df['Personas'].sum()*100:,.1f}%")
# col3.metric("Personas pendientes de actualizar", f"{df[df['ACTUALIZADO'] == 'No']['Personas'].sum():,.0f}", f"{df[df['ACTUALIZADO'] == 'No']['Personas'].sum()/df['Personas'].sum()*100:,.1f}%",delta_color="inverse")

with col1:
    st.metric("Meta de actualización", f"{df['Personas'].sum():,.0f}", "100%")

with col2:
    st.metric("Personas actualizadas", 
              f"{df[df['ACTUALIZADO'] == 'Si']['Personas'].sum():,.0f}", 
              f"{df[df['ACTUALIZADO'] == 'Si']['Personas'].sum()/df['Personas'].sum()*100:,.1f}%")

with col3:
    pendientes = df[df['ACTUALIZADO'] == 'No']['Personas'].sum()
    porcentaje_pend = pendientes / df['Personas'].sum() * 100
    # delta_color="inverse" hace que positivo sea rojo y negativo verde
    st.metric("Pendientes de actualizar", 
              f"{pendientes:,.0f}", 
              f"{porcentaje_pend:,.1f}%",
              delta_color="inverse")    # <-- Valor positivo se muestra en ROJO

# Información de fechas para el gráfico
col1, col2 = st.columns(2)

with col1:
    # --- Gráfico por Estado y Estatus de Actualización ---
    # Agrupar por estado y estatus
    df_estado = df.groupby(["NOM_EDO_PROD", "ACTUALIZADO"])["Personas"].sum().reset_index()

    # Calcular total por estado
    df_total = df_estado.groupby("NOM_EDO_PROD")["Personas"].sum().reset_index()
    df_total.columns = ["NOM_EDO_PROD", "Total"]

    # Merge para calcular porcentaje
    df_estado = df_estado.merge(df_total, on="NOM_EDO_PROD")
    df_estado["Porcentaje"] = (df_estado["Personas"] / df_estado["Total"] * 100).round(1)

    # Renombrar estatus
    df_estado["Estatus"] = df_estado["ACTUALIZADO"].map({
        "Si": "Actualizado",
        "No": "Pendiente",
    })

    # --- Ordenar: incluir TODOS los estados ---
    todos_estados = df_total["NOM_EDO_PROD"].unique()
    df_actualizado = df_estado[df_estado["Estatus"] == "Actualizado"].copy()

    df_orden = pd.DataFrame({"NOM_EDO_PROD": todos_estados})
    df_orden = df_orden.merge(
        df_actualizado[["NOM_EDO_PROD", "Porcentaje"]],
        on="NOM_EDO_PROD",
        how="left"
    ).fillna(0)

    orden_estados = df_orden.sort_values("Porcentaje", ascending=False)["NOM_EDO_PROD"].tolist()

    # Colores
    VERDE = "#285C4D"
    DORADO = "#D4C19C"
    color_map = {"Actualizado": VERDE, "Pendiente": DORADO}

    # ✅ CLAVE: Agregar "Estatus" a custom_data para usarlo en el hover
    fig_estado = px.bar(
        df_estado,
        y="NOM_EDO_PROD",
        x="Porcentaje",
        color="Estatus",
        text=df_estado["Porcentaje"].apply(lambda x: f"{x:.1f}%"),
        custom_data=["NOM_EDO_PROD", "Personas", "Porcentaje", "Estatus"],  # 👈 Agregamos Estatus
        color_discrete_map=color_map,
        category_orders={
            "NOM_EDO_PROD": orden_estados,
            "Estatus": ["Actualizado", "Pendiente"]
        },
        barmode="stack",
        orientation="h"
    )

    # ✅ HOVER MEJORADO: Incluye el nombre del estado, cantidad, porcentaje y estatus
    fig_estado.update_traces(
        textposition='inside',
        insidetextanchor='middle',
        textfont=dict(size=16, color="white"),
        hovertemplate=(
            "%{customdata[0]}: "
            "%{customdata[1]:,.0f} (%{customdata[2]:.1f}%) %{customdata[3]}"
            "<extra></extra>"
        )
    )

    # Layout
    fig_estado.update_layout(
        title=dict(
            text=f"Avance por Estado",
            font=dict(size=16, color=GUINDA)
        ),
        hoverlabel=dict(
            font_size=16,
            font_family="Noto Sans",
            bgcolor="rgba(40, 92, 77, 0.95)",
            font_color="white",
            bordercolor="#D4C19C"
        ),
        xaxis=dict(
            range=[0, 115],
            ticksuffix="%",
            dtick=20,
            title=None,
            tickfont=dict(size=16)
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(size=10)
        ),
        bargap=0.15,
        height=600,
        template="plotly_white",
        legend=dict(
            title=dict(
                text="Estatus",
                font=dict(size=18),
                font_family="Noto Sans",
                font_color="black",
            ),
            font=dict(size=16),
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=150, t=80, r=80),
        uniformtext_minsize=9,
        uniformtext_mode='hide'
    )

    # --- Anotaciones: usar df_total para TODOS los estados ---
    for _, row in df_total.iterrows():
        fig_estado.add_annotation(
            y=row["NOM_EDO_PROD"],
            x=105,
            text=f"{row['Total']:,.0f}",
            showarrow=False,
            font=dict(size=16, color="#285C4D"),
            xref="x",
            xanchor="left"
        )

    st.plotly_chart(fig_estado, width='stretch')

# Grafico de avance semanal o mensual
with col2:
    col_i_1, col_i_2 = st.columns([2, 1])

    with col_i_2:
        periodo = st.segmented_control(
            "Periodo:",
            options=["Semanal", "Mensual"],
            default="Mensual"
        )
    # --- Asegurar que la columna sea datetime ---
    df["fecha_captura"] = pd.to_datetime(df["fecha_captura"])
    df = df.dropna(subset=["fecha_captura"])

    # Redondeo al alza (ceiling) por semana y mes
    semana_fin = df["fecha_captura"].dt.to_period("W").dt.end_time.dt.normalize()
    mes_fin = df["fecha_captura"].dt.to_period("M").dt.end_time.dt.normalize()

    # Dense rank: factorize sobre valores ordenados
    df["semana"] = pd.Categorical(semana_fin).codes + 1
    df["semana"] = df["semana"].where(df["fecha_captura"].notna()).map(lambda x: f"Semana {int(x):02d}")

    df["mes"] = pd.Categorical(mes_fin).codes + 1
    df["mes"] = df["mes"].where(df["fecha_captura"].notna()).map(lambda x: f"Mes {int(x):02d}")


    # --- Agrupar según selección ---
    if periodo == "Semanal":
        df_agrupado = df.groupby(df["semana"])["Personas"].sum().reset_index()
        df_agrupado.columns = ["Fecha", "Cantidad"]
    elif periodo == "Mensual":
        df_agrupado = df.groupby(df["mes"])["Personas"].sum().reset_index()
        df_agrupado.columns = ["Fecha", "Cantidad"]
    else:
        df_agrupado = df.groupby(df["mes"])["Personas"].sum().reset_index()
        df_agrupado.columns = ["Fecha", "Cantidad"]
        periodo = "Mensual"

    df_filtrado = df_agrupado

    # --- Gráfico de barras con valores ---
    fig = px.bar(
        df_filtrado,
        x="Fecha",
        y="Cantidad",
        text="Cantidad",  # <-- Agrega los valores como texto en las barras
        labels={"Fecha": periodo, "Cantidad": "Personas"},
        color_discrete_sequence=["#D4C19C"]
    )

    fig.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='outside',
        textfont=dict(
            size=18,
            color="#285C4D",
            family="Noto Sans Black",
        ),
        hovertemplate=(
                "text: "
                "%{value:,.0f} "          # <-- Usar %{value} en lugar de customdata
                "(%{percent}) "
                "<extra></extra>"
            ),
        cliponaxis=False  # <-- Permite que el texto se dibuje fuera del área del eje
        )

    fig.update_layout(
        xaxis_tickangle=-45,
        bargap=0.1,
        height=480,  # <-- Un poco más de altura
        template="plotly_white",
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        margin=dict(t=80),  # <-- Más margen superior
        title=dict(
            text=f"Avance {periodo}",
            font=dict(size=16, color=GUINDA)    # <-- Título más grande
        ),
        yaxis=dict(
            range=[0, df_filtrado["Cantidad"].max() * 1.1]  # <-- 20% extra
        )
    )
    st.plotly_chart(fig, width='stretch')


# Crear columnas para mostrar las donas lado a lado
col1, col2, col3 = st.columns(3)
columnas = [col1, col2, col3]
# Configuración de las variables para las donas
variables_dona = {
    "Cambio_sup": "Cambio de Superficie",
    "Cambio_cultivo": "Cambio de Cultivo",
    "genero": "Género"
}

for i, (variable, titulo) in enumerate(variables_dona.items()):
    # Agrupar por la variable sumando personas
    df_dona = df.groupby(variable)["Personas"].sum().reset_index()
    df_dona.columns = ["Categoria", "Personas"]
    
    # Calcular porcentaje
    df_dona["Porcentaje"] = (df_dona["Personas"] / df_dona["Personas"].sum() * 100).round(1)
    
    # Colores alternados
    colores = [VERDE, DORADO, GUINDA] * (len(df_dona) // 2 + 1)
    colores = colores[:len(df_dona)]
    
    # Crear gráfico de dona
    fig_dona = px.pie(
        df_dona,
        values="Personas",
        names="Categoria",
        title=titulo,
        hole=0.4,  # <-- Esto lo convierte en dona
        color_discrete_sequence=colores,
        custom_data=["Personas", "Porcentaje"]
    )
    
    # Para agregar texto en el centro de la dona:
    fig_dona.add_annotation(
            text=f"{df_dona['Personas'].sum():,.0f}",
            x=0.5, y=0.5,
            font=dict(size=20, color=GUINDA),
            showarrow=False
        )

    fig_dona.update_traces(
        textposition='inside',
        textinfo='label+percent',
        textfont=dict(size=14, color="white",family="Noto Sans Black"),
        hovertemplate=(
            "Personas: "
            "%{value:,.0f} "          # <-- Usar %{value} en lugar de customdata
            "(%{percent})"
            "<extra></extra>"
        )
    )
    
    fig_dona.update_layout(
        hoverlabel=dict(
            font_size=16,
            font_family="Arial",
            bgcolor="rgba(40, 92, 77, 0.95)",
            font_color="white",
            bordercolor="#D4C19C"
        ),
        title=dict(
            text=titulo,
            font=dict(size=16, color=GUINDA),
            x=0.5,
            xanchor="center"
        ),
        legend=dict(
            font=dict(size=16),
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
        height=400,
        margin=dict(t=80, b=80, l=20, r=20),
        showlegend=True
    )
    
    # Mostrar en la columna correspondiente
    with columnas[i]:
        st.plotly_chart(fig_dona, width='stretch')



# =============================================================================
# FILA 4: ANÁLISIS DE CAMBIOS (Superficie, Cultivo, Género, Edad)
# =============================================================================

st.markdown(
    'Análisis de Cambios Detectados',
    unsafe_allow_html=True
)


# =============================================================================
# FILA 5: TABLAS DE DATOS
# =============================================================================

st.markdown(
    'Detalle de Registros',
    unsafe_allow_html=True
)

tab_resumen_cultivo, tab_resumen_municipio, tab_resumen_cader = st.tabs(["Resumen por cultivo", "Resumen por municipio", "Resumen por cader"])

# --- Tabla 1: Resumen por estado ---
# with tab_resumen:
#     resumen = (
#         df.groupby("Estado")
#         .agg(
#             Total=("ID", "count"),
#             Actualizados=("Actualizado", "sum"),
#             Mujeres=("Género", lambda x: (x == "Femenino").sum()),
#             Edad_Promedio=("Edad", "mean"),
#             Cambio_Cultivo=("Cambió_Cultivo", "sum"),
#             Sup_Alza=("Cambio_Superficie", lambda x: (x == "Al alza").sum()),
#             Sup_Baja=("Cambio_Superficie", lambda x: (x == "A la baja").sum()),
#             Sup_Igual=("Cambio_Superficie", lambda x: (x == "Se mantuvo").sum()),
#         )
#         .reset_index()
#     )
#     resumen["% Avance"] = round(
#         resumen["Actualizados"] / resumen["Total"] * 100, 1
#     )
#     resumen["% Mujeres"] = round(
#         resumen["Mujeres"] / resumen["Total"] * 100, 1
#     )
#     resumen["Edad_Promedio"] = round(resumen["Edad_Promedio"], 0).astype(int)
#     resumen = resumen.sort_values("% Avance", ascending=False)

#     # Mostrar con formato
#     st.dataframe(
#         resumen,
#         width='stretch',
#         hide_index=True,
#         height=400,
#         column_config={
#             "Estado": st.column_config.TextColumn("Estado", width="medium"),
#             "Total": st.column_config.NumberColumn("Total", format="%d"),
#             "Actualizados": st.column_config.NumberColumn(
#                 "Actualizados", format="%d"
#             ),
#             "% Avance": st.column_config.ProgressColumn(
#                 "% Avance", min_value=0, max_value=100, format="%.1f%%"
#             ),
#             "Mujeres": st.column_config.NumberColumn("Mujeres", format="%d"),
#             "% Mujeres": st.column_config.NumberColumn(
#                 "% Mujeres", format="%.1f%%"
#             ),
#             "Edad_Promedio": st.column_config.NumberColumn(
#                 "Edad Prom.", format="%d"
#             ),
#             "Cambio_Cultivo": st.column_config.NumberColumn(
#                 "Cambio Cultivo", format="%d"
#             ),
#             "Sup_Alza": st.column_config.NumberColumn(
#                 "Sup. ↑", format="%d"
#             ),
#             "Sup_Baja": st.column_config.NumberColumn(
#                 "Sup. ↓", format="%d"
#             ),
#             "Sup_Igual": st.column_config.NumberColumn(
#                 "Sup. =", format="%d"
#             ),
#         }
#     )

# --- Tabla 2: Detalle de registros ---
# with tab_detalle:
#     # Columnas a mostrar
#     cols_mostrar = [
#         "ID", "Estado", "Género", "Edad", "Grupo_Edad",
#         "Cultivo_Anterior", "Cultivo_Nuevo", "Cambió_Cultivo",
#         "Superficie_Anterior_Ha", "Superficie_Nueva_Ha",
#         "Cambio_Superficie", "Actualizado"
#     ]

#     st.dataframe(
#         df[cols_mostrar].sort_values("Estado"),
#         width='stretch',
#         hide_index=True,
#         height=400,
#         column_config={
#             "ID": "ID",
#             "Estado": "Estado",
#             "Género": "Género",
#             "Edad": st.column_config.NumberColumn("Edad", format="%d"),
#             "Grupo_Edad": "Grupo Edad",
#             "Cultivo_Anterior": "Cultivo Ant.",
#             "Cultivo_Nuevo": "Cultivo Nuevo",
#             "Cambió_Cultivo": st.column_config.CheckboxColumn(
#                 "¿Cambió?", default=False
#             ),
#             "Superficie_Anterior_Ha": st.column_config.NumberColumn(
#                 "Sup. Ant. (Ha)", format="%.1f"
#             ),
#             "Superficie_Nueva_Ha": st.column_config.NumberColumn(
#                 "Sup. Nueva (Ha)", format="%.1f"
#             ),
#             "Cambio_Superficie": "Cambio Sup.",
#             "Actualizado": st.column_config.CheckboxColumn(
#                 "Actualizado", default=False
#             ),
#         }
#     )

#     # Botón de descarga
#     csv = df[cols_mostrar].to_csv(index=False).encode("utf-8")
#     st.download_button(
#         label="📥 Descargar datos filtrados (CSV)",
#         data=csv,
#         file_name="padron_filtrado.csv",
#         mime="text/csv"
#     )


# =============================================================================
# FOOTER
# =============================================================================

# st.divider() # Una línea sutil para separar el contenido
#with st.expander("Información Legal y de Privacidad"):

st.markdown("""
Esta plataforma es una herramienta de consulta técnica interna desarrollada por la DGPP. Los resultados presentados son informativos y no constituyen documentos oficiales ni actos administrativos vinculantes.     
Este software es de código abierto bajo la licencia [MIT/Apache] - AHH 2026
""")
