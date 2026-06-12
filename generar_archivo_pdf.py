# ═══════════════════════════════════════════════════════════════════════════════
# GENERADOR DE PRESENTACIÓN PDF INSTITUCIONAL CON GRÁFICOS
# ═══════════════════════════════════════════════════════════════════════════════

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    Image, PageBreak, Frame, PageTemplate, BaseDocTemplate
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics import renderPDF
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
import os
import numpy as np

def generar_presentacion_pdf(df, meta, actualizados, pendientes, pct_avance, hoy, geojson_data=None):
    """Genera presentación PDF institucional con gráficos visuales."""

    buffer = BytesIO()

    # Colores
    verde = HexColor("#285C4D")
    guinda = HexColor("#621132")
    dorado = HexColor("#D4C19C")
    verde_claro = HexColor("#3A7D6B")
    crema = HexColor("#F5F1EB")
    gris_oscuro = HexColor("#333333")
    gris_claro = HexColor("#F0F0F0")

    # Colores matplotlib
    VERDE_MPL = "#285C4D"
    GUINDA_MPL = "#621132"
    DORADO_MPL = "#D4C19C"
    VERDE_CLARO_MPL = "#3A7D6B"
    PALETA_MPL = ["#10312B", "#691C32", "#D4C19C", "#235B4E", "#9F2241", "#44546A", "#52492E", "#C29E5C"]

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=0.4 * inch,
        leftMargin=0.4 * inch,
        topMargin=0.35 * inch,
        bottomMargin=0.35 * inch
    )

    styles = getSampleStyleSheet()

    # ─── ESTILOS ───
    estilo_titulo_portada = ParagraphStyle(
        'TituloPortada', fontName='Helvetica-Bold', fontSize=36,
        textColor=verde, alignment=TA_CENTER, spaceAfter=4
    )
    estilo_subtitulo_portada = ParagraphStyle(
        'SubtituloPortada', fontName='Helvetica', fontSize=20,
        textColor=guinda, alignment=TA_CENTER, spaceAfter=4
    )
    estilo_seccion = ParagraphStyle(
        'Seccion', fontName='Helvetica-Bold', fontSize=24,
        textColor=verde, alignment=TA_LEFT, spaceAfter=8, spaceBefore=4
    )
    estilo_subseccion = ParagraphStyle(
        'Subseccion', fontName='Helvetica-Bold', fontSize=16,
        textColor=guinda, alignment=TA_LEFT, spaceAfter=6
    )
    estilo_texto = ParagraphStyle(
        'Texto', fontName='Helvetica', fontSize=12,
        textColor=gris_oscuro, alignment=TA_LEFT, spaceAfter=6, leading=16
    )
    estilo_texto_blanco = ParagraphStyle(
        'TextoBlanco', fontName='Helvetica', fontSize=12,
        textColor=white, alignment=TA_LEFT, spaceAfter=4, leading=16
    )
    estilo_destacado = ParagraphStyle(
        'Destacado', fontName='Helvetica-Bold', fontSize=14,
        textColor=verde, alignment=TA_LEFT, spaceAfter=8, leading=18
    )
    estilo_kpi_valor = ParagraphStyle(
        'KPIValor', fontName='Helvetica-Bold', fontSize=36,
        textColor=guinda, alignment=TA_CENTER, spaceAfter=0
    )
    estilo_kpi_label = ParagraphStyle(
        'KPILabel', fontName='Helvetica', fontSize=11,
        textColor=verde, alignment=TA_CENTER, spaceAfter=2
    )
    estilo_pie = ParagraphStyle(
        'Pie', fontName='Helvetica-Oblique', fontSize=8,
        textColor=HexColor("#999999"), alignment=TA_RIGHT
    )

    elements = []

    # ─── FUNCIÓN: Crear gráfico como imagen ───
    def fig_to_image(fig, width=9, height=4.5):
        """Convierte una figura matplotlib a imagen para el PDF."""
        img_buffer = BytesIO()
        fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        img_buffer.seek(0)
        plt.close(fig)
        return Image(img_buffer, width=width * inch, height=height * inch)

    def crear_linea_tricolor():
        """Línea decorativa tricolor."""
        data = [['', '', '']]
        t = Table(data, colWidths=[3.3 * inch, 3.3 * inch, 3.3 * inch])
        t.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (0, 0), 4, verde),
            ('LINEBELOW', (1, 0), (1, 0), 4, dorado),
            ('LINEBELOW', (2, 0), (2, 0), 4, guinda),
        ]))
        return t

    def crear_separador():
        """Separador de sección."""
        data = [['', '']]
        t = Table(data, colWidths=[2.5 * inch, 7 * inch])
        t.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (0, 0), 2.5, verde),
            ('LINEBELOW', (1, 0), (1, 0), 1, dorado),
        ]))
        return t

    # ═══════════════════════════════════════════════════════════════════════
    # PORTADA
    # ═══════════════════════════════════════════════════════════════════════

    elements.append(Spacer(1, 1.2 * inch))
    elements.append(crear_linea_tricolor())
    elements.append(Spacer(1, 0.4 * inch))

    elements.append(Paragraph("Producción para el Bienestar", estilo_titulo_portada))
    elements.append(Paragraph("PROBIEN 2026", estilo_subtitulo_portada))
    elements.append(Spacer(1, 0.5 * inch))

    # Caja destacada en la portada
    portada_data = [[Paragraph(
        "Proceso de Actualización del Padrón de Beneficiarios",
        ParagraphStyle('PortadaCaja', fontName='Helvetica-Bold', fontSize=18,
                       textColor=white, alignment=TA_CENTER)
    )]]
    portada_table = Table(portada_data, colWidths=[7 * inch], rowHeights=[0.6 * inch])
    portada_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), verde),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (0, 0), 12),
        ('BOTTOMPADDING', (0, 0), (0, 0), 12),
        ('ROUNDEDCORNERS', [10, 10, 10, 10]),
    ]))
    elements.append(portada_table)

    elements.append(Spacer(1, 0.6 * inch))
    elements.append(Paragraph(
        f"Fecha del reporte: {hoy}",
        ParagraphStyle('FechaPortada', fontName='Helvetica', fontSize=14,
                       textColor=guinda, alignment=TA_CENTER)
    ))
    elements.append(Spacer(1, 1.0 * inch))
    elements.append(crear_linea_tricolor())
    elements.append(Spacer(1, 0.5 * inch))

    elements.append(Paragraph(
        "Secretaría de Agricultura y Desarrollo Rural",
        ParagraphStyle('SADER', fontName='Helvetica-Bold', fontSize=13, textColor=verde, alignment=TA_CENTER)
    ))
    elements.append(Paragraph(
        "Subsecretaría de Autosuficiencia Alimentaria",
        ParagraphStyle('Sub', fontName='Helvetica', fontSize=11, textColor=gris_oscuro, alignment=TA_CENTER)
    ))

    elements.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════
    # PÁGINA 2: RESUMEN EJECUTIVO
    # ═══════════════════════════════════════════════════════════════════════

    elements.append(Paragraph("Resumen Ejecutivo", estilo_seccion))
    elements.append(crear_separador())
    elements.append(Spacer(1, 0.2 * inch))

    # KPIs con cajas de color
    kpi_data = [[
        Paragraph(f"{meta:,.0f}", ParagraphStyle('V1', fontName='Helvetica-Bold', fontSize=28, textColor=white, alignment=TA_CENTER)),
        Paragraph(f"{actualizados:,.0f}", ParagraphStyle('V2', fontName='Helvetica-Bold', fontSize=28, textColor=white, alignment=TA_CENTER)),
        Paragraph(f"{pendientes:,.0f}", ParagraphStyle('V3', fontName='Helvetica-Bold', fontSize=28, textColor=white, alignment=TA_CENTER)),
        Paragraph(f"{pct_avance:.1f}%", ParagraphStyle('V4', fontName='Helvetica-Bold', fontSize=28, textColor=white, alignment=TA_CENTER)),
    ], [
        Paragraph("Meta Total", ParagraphStyle('L1', fontName='Helvetica', fontSize=10, textColor=white, alignment=TA_CENTER)),
        Paragraph("Actualizados", ParagraphStyle('L2', fontName='Helvetica', fontSize=10, textColor=white, alignment=TA_CENTER)),
        Paragraph("Pendientes", ParagraphStyle('L3', fontName='Helvetica', fontSize=10, textColor=white, alignment=TA_CENTER)),
        Paragraph("Avance", ParagraphStyle('L4', fontName='Helvetica', fontSize=10, textColor=white, alignment=TA_CENTER)),
    ]]

    kpi_table = Table(kpi_data, colWidths=[2.35 * inch] * 4, rowHeights=[0.55 * inch, 0.3 * inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), verde),
        ('BACKGROUND', (1, 0), (1, -1), verde_claro),
        ('BACKGROUND', (2, 0), (2, -1), dorado),
        ('BACKGROUND', (3, 0), (3, -1), guinda),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Gráfico de barras: Avance por estado (Top 10)
    df_estado_pdf = df.groupby("NOM_EDO_PROD")["Personas"].sum().reset_index()
    df_estado_pdf.columns = ["Estado", "Meta"]
    df_act_pdf = df[df["ACTUALIZADO"] == "Si"].groupby("NOM_EDO_PROD")["Personas"].sum().reset_index()
    df_act_pdf.columns = ["Estado", "Actualizados"]
    df_estado_pdf = df_estado_pdf.merge(df_act_pdf, on="Estado", how="left").fillna(0)
    df_estado_pdf["Pct"] = np.where(df_estado_pdf["Meta"] > 0, (df_estado_pdf["Actualizados"] / df_estado_pdf["Meta"] * 100).round(1), 0)
    df_estado_pdf = df_estado_pdf.sort_values("Pct", ascending=True).tail(15)

    fig_barras, ax = plt.subplots(figsize=(10, 4.5))
    bars = ax.barh(df_estado_pdf["Estado"], df_estado_pdf["Pct"], color=VERDE_MPL, edgecolor='white', linewidth=0.5)
    ax.set_xlim(0, 110)
    ax.set_xlabel("% Avance", fontsize=11, color=VERDE_MPL, fontweight='bold')
    ax.set_title("Top 15 Entidades con Mayor Avance", fontsize=14, color=GUINDA_MPL, fontweight='bold', pad=10)
    ax.axvline(x=100, color=DORADO_MPL, linestyle='--', linewidth=1, alpha=0.7)
    ax.tick_params(axis='y', labelsize=9, colors='#333')
    ax.tick_params(axis='x', labelsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#DDD')
    ax.spines['bottom'].set_color('#DDD')

    for bar, pct in zip(bars, df_estado_pdf["Pct"]):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                f'{pct:.1f}%', va='center', fontsize=8, color=GUINDA_MPL, fontweight='bold')

    fig_barras.tight_layout()
    elements.append(fig_to_image(fig_barras, width=9.5, height=4.2))

    elements.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════
    # PÁGINA 3: MAPA Y TABLA DE ESTADOS
    # ═══════════════════════════════════════════════════════════════════════

    elements.append(Paragraph("Avance por Entidad Federativa", estilo_seccion))
    elements.append(crear_separador())
    elements.append(Spacer(1, 0.15 * inch))

    # Tabla completa de estados
    df_tabla_estados = df.groupby("NOM_EDO_PROD")["Personas"].sum().reset_index()
    df_tabla_estados.columns = ["Estado", "Meta"]
    df_tabla_estados = df_tabla_estados.merge(df_act_pdf, on="Estado", how="left").fillna(0)
    df_tabla_estados["Pendientes"] = df_tabla_estados["Meta"] - df_tabla_estados["Actualizados"]
    df_tabla_estados["% Avance"] = np.where(df_tabla_estados["Meta"] > 0, (df_tabla_estados["Actualizados"] / df_tabla_estados["Meta"] * 100).round(1), 0)
    df_tabla_estados = df_tabla_estados.sort_values("% Avance", ascending=False)

    # Dividir en dos columnas para mejor uso del espacio
    mitad = len(df_tabla_estados) // 2 + len(df_tabla_estados) % 2
    df_izq = df_tabla_estados.iloc[:mitad].reset_index(drop=True)
    df_der = df_tabla_estados.iloc[mitad:].reset_index(drop=True)

    def crear_tabla_estados(df_t):
        header = ["Estado", "Meta", "Actual.", "% Av."]
        data = [header]
        for _, r in df_t.iterrows():
            data.append([r["Estado"], f"{r['Meta']:,.0f}", f"{r['Actualizados']:,.0f}", f"{r['% Avance']:.1f}%"])
        t = Table(data, colWidths=[2.2 * inch, 0.9 * inch, 0.9 * inch, 0.7 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), verde),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.3, HexColor("#DDDDDD")),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, verde),
            *[('BACKGROUND', (0, i), (-1, i), crema) for i in range(2, len(data), 2)],
        ]))
        return t

    col_data = [[crear_tabla_estados(df_izq), Spacer(0.2 * inch, 0), crear_tabla_estados(df_der)]]
    col_table = Table(col_data, colWidths=[4.8 * inch, 0.2 * inch, 4.8 * inch])
    col_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(col_table)

    # Fila total
    elements.append(Spacer(1, 0.15 * inch))
    total_data = [[
        Paragraph(f"TOTAL NACIONAL", ParagraphStyle('TN', fontName='Helvetica-Bold', fontSize=11, textColor=white, alignment=TA_CENTER)),
        Paragraph(f"Meta: {meta:,.0f}", ParagraphStyle('TM', fontName='Helvetica-Bold', fontSize=11, textColor=white, alignment=TA_CENTER)),
        Paragraph(f"Actualizados: {actualizados:,.0f}", ParagraphStyle('TA', fontName='Helvetica-Bold', fontSize=11, textColor=white, alignment=TA_CENTER)),
        Paragraph(f"Avance: {pct_avance:.1f}%", ParagraphStyle('TV', fontName='Helvetica-Bold', fontSize=11, textColor=white, alignment=TA_CENTER)),
    ]]
    total_table = Table(total_data, colWidths=[2.4 * inch] * 4, rowHeights=[0.4 * inch])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), guinda),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
    ]))
    elements.append(total_table)

    elements.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════
    # PÁGINA 4: PERFIL DEMOGRÁFICO (GRÁFICOS)
    # ═══════════════════════════════════════════════════════════════════════

    elements.append(Paragraph("Perfil Demográfico", estilo_seccion))
    elements.append(crear_separador())
    elements.append(Spacer(1, 0.15 * inch))

    # Gráfico doble: Género + Edad
    fig_demo, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Dona de Género
    df_genero = df.groupby("genero")["Personas"].sum().reset_index()
    colores_genero = [VERDE_MPL, GUINDA_MPL, DORADO_MPL][:len(df_genero)]
    wedges, texts, autotexts = ax1.pie(
        df_genero["Personas"], labels=df_genero["genero"],
        colors=colores_genero, autopct='%1.1f%%',
        startangle=90, pctdistance=0.75,
        wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
    )
    for t in autotexts:
        t.set_fontsize(10)
        t.set_fontweight('bold')
    for t in texts:
        t.set_fontsize(9)
    ax1.set_title("Distribución por Género", fontsize=13, color=GUINDA_MPL, fontweight='bold', pad=15)
    centro = plt.Circle((0, 0), 0.55, fc='white')
    ax1.add_patch(centro)
    ax1.text(0, 0, f"{df_genero['Personas'].sum():,.0f}", ha='center', va='center',
             fontsize=14, fontweight='bold', color=GUINDA_MPL)

    # Barras de Edad
    if "Grupos_Edad" in df.columns:
        df_edad_pdf = df.groupby(["Ord_Grupos_Edad", "Grupos_Edad"])["Personas"].sum().reset_index()
        df_edad_pdf = df_edad_pdf.sort_values("Ord_Grupos_Edad")
        colores_edad_mpl = (PALETA_MPL * 3)[:len(df_edad_pdf)]

        bars_edad = ax2.bar(range(len(df_edad_pdf)), df_edad_pdf["Personas"],
                            color=colores_edad_mpl, edgecolor='white', linewidth=0.5)
        ax2.set_xticks(range(len(df_edad_pdf)))
        ax2.set_xticklabels(df_edad_pdf["Grupos_Edad"], rotation=45, ha='right', fontsize=7)
        ax2.set_title("Distribución por Edad", fontsize=13, color=GUINDA_MPL, fontweight='bold', pad=10)
        ax2.set_ylabel("Personas", fontsize=9, color=VERDE_MPL)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_color('#DDD')
        ax2.spines['bottom'].set_color('#DDD')
        ax2.tick_params(axis='y', labelsize=8)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))

    fig_demo.tight_layout(pad=2)
    elements.append(fig_to_image(fig_demo, width=9.5, height=3.8))
    elements.append(Spacer(1, 0.2 * inch))

    # Tabla resumen género
    genero_resumen = [[
        Paragraph(f"{row['genero']}", ParagraphStyle('G', fontName='Helvetica-Bold', fontSize=11, textColor=verde, alignment=TA_CENTER)),
        Paragraph(f"{row['Personas']:,.0f}", ParagraphStyle('GV', fontName='Helvetica', fontSize=11, textColor=gris_oscuro, alignment=TA_CENTER)),
        Paragraph(f"{row['Personas']/df_genero['Personas'].sum()*100:.1f}%", ParagraphStyle('GP', fontName='Helvetica-Bold', fontSize=11, textColor=guinda, alignment=TA_CENTER)),
    ] for _, row in df_genero.iterrows()]

    genero_header = [[
        Paragraph("Género", ParagraphStyle('GH', fontName='Helvetica-Bold', fontSize=10, textColor=white, alignment=TA_CENTER)),
        Paragraph("Personas", ParagraphStyle('GH2', fontName='Helvetica-Bold', fontSize=10, textColor=white, alignment=TA_CENTER)),
        Paragraph("Porcentaje", ParagraphStyle('GH3', fontName='Helvetica-Bold', fontSize=10, textColor=white, alignment=TA_CENTER)),
    ]]

    genero_table = Table(genero_header + genero_resumen, colWidths=[3 * inch, 3 * inch, 3 * inch])
    genero_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), verde),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#EEE")),
        *[('BACKGROUND', (0, i), (-1, i), crema) for i in range(2, len(genero_resumen) + 1, 2)],
    ]))
    elements.append(genero_table)

    elements.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════
    # PÁGINA 5: ANÁLISIS DE CAMBIOS (GRÁFICOS)
    # ═══════════════════════════════════════════════════════════════════════

    elements.append(Paragraph("Análisis de Cambios Detectados", estilo_seccion))
    elements.append(crear_separador())
    elements.append(Spacer(1, 0.15 * inch))

    # Gráfico triple: Superficie, Cultivo, Posesión
    fig_cambios, axes = plt.subplots(1, 3, figsize=(10, 3.5))

    variables_cambios = [
        ("Cambio_sup", "Cambio Superficie"),
        ("Cambio_cultivo", "Cambio Cultivo"),
        ("tipo_posesion", "Tipo Posesión"),
    ]

    for idx, (var, titulo_v) in enumerate(variables_cambios):
        if var in df.columns:
            df_var = df.groupby(var)["Personas"].sum().reset_index()
            colores_v = PALETA_MPL[:len(df_var)]

            wedges, texts, autotexts = axes[idx].pie(
                df_var["Personas"], labels=None,
                colors=colores_v, autopct='%1.1f%%',
                startangle=90, pctdistance=0.78,
                wedgeprops=dict(width=0.45, edgecolor='white', linewidth=1.5)
            )
            for t in autotexts:
                t.set_fontsize(8)
                t.set_fontweight('bold')
                t.set_color('white')

            axes[idx].set_title(titulo_v, fontsize=11, color=GUINDA_MPL, fontweight='bold', pad=8)

            # Leyenda compacta
            axes[idx].legend(df_var[var].tolist(), loc='lower center',
                             fontsize=7, frameon=False, ncol=1,
                             bbox_to_anchor=(0.5, -0.15))

    fig_cambios.tight_layout(pad=1.5)
    elements.append(fig_to_image(fig_cambios, width=9.5, height=3.5))
    elements.append(Spacer(1, 0.2 * inch))

    # Segunda fila: Régimen + Ciclo
    fig_cambios2, (ax_reg, ax_cic) = plt.subplots(1, 2, figsize=(10, 3.5))

    for ax_c, (var_c, titulo_c) in zip([ax_reg, ax_cic], [("regimen", "Régimen Hídrico"), ("ciclo", "Ciclo Productivo")]):
        if var_c in df.columns:
            df_vc = df.groupby(var_c)["Personas"].sum().reset_index().sort_values("Personas", ascending=True)
            colores_vc = PALETA_MPL[:len(df_vc)]

            ax_c.barh(df_vc[var_c], df_vc["Personas"], color=colores_vc, edgecolor='white', linewidth=0.5)
            ax_c.set_title(titulo_c, fontsize=12, color=GUINDA_MPL, fontweight='bold', pad=8)
            ax_c.spines['top'].set_visible(False)
            ax_c.spines['right'].set_visible(False)
            ax_c.spines['left'].set_color('#DDD')
            ax_c.spines['bottom'].set_color('#DDD')
            ax_c.tick_params(labelsize=9)
            ax_c.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}k'))
            ax_c.set_xlabel("Personas (miles)", fontsize=9, color=VERDE_MPL)

    fig_cambios2.tight_layout(pad=2)
    elements.append(fig_to_image(fig_cambios2, width=9.5, height=3.3))

    elements.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════
    # PÁGINA 6: TOP CULTIVOS
    # ═══════════════════════════════════════════════════════════════════════

    if "NOM_CULTIVO" in df.columns:
        elements.append(Paragraph("Principales Cultivos", estilo_seccion))
        elements.append(crear_separador())
        elements.append(Spacer(1, 0.15 * inch))

        df_cultivo_pdf = df.groupby("NOM_CULTIVO")["Personas"].sum().reset_index()
        df_cultivo_pdf = df_cultivo_pdf.sort_values("Personas", ascending=False).head(12)
        df_cultivo_pdf["Pct"] = (df_cultivo_pdf["Personas"] / df_cultivo_pdf["Personas"].sum() * 100).round(1)

        fig_cult, ax_cult = plt.subplots(figsize=(10, 5))
        df_plot = df_cultivo_pdf.sort_values("Personas", ascending=True)
        colores_cult = PALETA_MPL * 2

        bars_cult = ax_cult.barh(
            range(len(df_plot)), df_plot["Personas"],
            color=[colores_cult[i % len(colores_cult)] for i in range(len(df_plot))],
            edgecolor='white', linewidth=0.5
        )
        ax_cult.set_yticks(range(len(df_plot)))
        ax_cult.set_yticklabels(df_plot["NOM_CULTIVO"], fontsize=9)
        ax_cult.set_title("Top 12 Cultivos por Número de Personas", fontsize=14, color=GUINDA_MPL, fontweight='bold', pad=12)
        ax_cult.set_xlabel("Personas", fontsize=10, color=VERDE_MPL, fontweight='bold')
        ax_cult.spines['top'].set_visible(False)
        ax_cult.spines['right'].set_visible(False)
        ax_cult.spines['left'].set_color('#DDD')
        ax_cult.spines['bottom'].set_color('#DDD')
        ax_cult.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))

        for bar, (_, row) in zip(bars_cult, df_plot.iterrows()):
            ax_cult.text(bar.get_width() + df_plot["Personas"].max() * 0.01,
                         bar.get_y() + bar.get_height() / 2,
                         f'{row["Personas"]:,.0f} ({row["Pct"]:.1f}%)',
                         va='center', fontsize=8, color=GUINDA_MPL)

        fig_cult.tight_layout()
        elements.append(fig_to_image(fig_cult, width=9.5, height=4.5))

    elements.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════
    # PÁGINA 7: ESTATUS DOCUMENTAL
    # ═══════════════════════════════════════════════════════════════════════

    elements.append(Paragraph("Estatus Documental y Geográfico", estilo_seccion))
    elements.append(crear_separador())
    elements.append(Spacer(1, 0.15 * inch))

    fig_doc, (ax_coord, ax_doc) = plt.subplots(1, 2, figsize=(10, 4))

    # Coordenadas
    if "Estatus_coordenadas" in df.columns:
        df_coord_pdf = df.groupby("Estatus_coordenadas")["Personas"].sum().reset_index()
        colores_coord = PALETA_MPL[:len(df_coord_pdf)]
        wedges, texts, autotexts = ax_coord.pie(
            df_coord_pdf["Personas"], labels=df_coord_pdf["Estatus_coordenadas"],
            colors=colores_coord, autopct='%1.1f%%', startangle=90,
            pctdistance=0.75, wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
        )
        for t in autotexts:
            t.set_fontsize(9)
            t.set_fontweight('bold')
        for t in texts:
            t.set_fontsize(8)
        ax_coord.set_title("Estatus de Coordenadas", fontsize=12, color=GUINDA_MPL, fontweight='bold', pad=12)
        centro_c = plt.Circle((0, 0), 0.55, fc='white')
        ax_coord.add_patch(centro_c)
        ax_coord.text(0, 0, f"{df_coord_pdf['Personas'].sum():,.0f}", ha='center', va='center',
                      fontsize=12, fontweight='bold', color=GUINDA_MPL)

    # Documento
    if "EstatusDocProp" in df.columns:
        df_doc_pdf = df.groupby("EstatusDocProp")["Personas"].sum().reset_index()
        colores_doc = PALETA_MPL[:len(df_doc_pdf)]
        wedges2, texts2, autotexts2 = ax_doc.pie(
            df_doc_pdf["Personas"], labels=df_doc_pdf["EstatusDocProp"],
            colors=colores_doc, autopct='%1.1f%%', startangle=90,
            pctdistance=0.75, wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
        )
        for t in autotexts2:
            t.set_fontsize(9)
            t.set_fontweight('bold')
        for t in texts2:
            t.set_fontsize(8)
        ax_doc.set_title("Documento de Posesión", fontsize=12, color=GUINDA_MPL, fontweight='bold', pad=12)
        centro_d = plt.Circle((0, 0), 0.55, fc='white')
        ax_doc.add_patch(centro_d)
        ax_doc.text(0, 0, f"{df_doc_pdf['Personas'].sum():,.0f}", ha='center', va='center',
                    fontsize=12, fontweight='bold', color=GUINDA_MPL)

    fig_doc.tight_layout(pad=2)
    elements.append(fig_to_image(fig_doc, width=9.5, height=3.8))

    elements.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════
    # PÁGINA FINAL: CIERRE
    # ═══════════════════════════════════════════════════════════════════════

    elements.append(Spacer(1, 1.8 * inch))
    elements.append(crear_linea_tricolor())
    elements.append(Spacer(1, 0.6 * inch))

    elements.append(Paragraph(
        "Secretaría de Agricultura y Desarrollo Rural",
        ParagraphStyle('Cierre1', fontName='Helvetica-Bold', fontSize=20, textColor=verde, alignment=TA_CENTER)
    ))
    elements.append(Spacer(1, 0.15 * inch))
    elements.append(Paragraph(
        "Subsecretaría de Autosuficiencia Alimentaria",
        ParagraphStyle('Cierre2', fontName='Helvetica', fontSize=15, textColor=guinda, alignment=TA_CENTER)
    ))
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph(
        "Dirección General de Producción para el Bienestar",
        ParagraphStyle('Cierre3', fontName='Helvetica', fontSize=12, textColor=gris_oscuro, alignment=TA_CENTER)
    ))
    elements.append(Spacer(1, 0.8 * inch))

    # Caja de contacto
    contacto_data = [[Paragraph(
        f"Documento generado automáticamente el {hoy}"
        f"Datos actualizados al momento de la consulta",
        ParagraphStyle('Contacto', fontName='Helvetica', fontSize=10, textColor=HexColor("#666"), alignment=TA_CENTER, leading=14)
    )]]
    contacto_table = Table(contacto_data, colWidths=[6 * inch], rowHeights=[0.6 * inch])
    contacto_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), crema),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ('BOX', (0, 0), (0, 0), 1, dorado),
    ]))
    elements.append(contacto_table)

    elements.append(Spacer(1, 0.5 * inch))
    elements.append(crear_linea_tricolor())

    # Construir
    doc.build(elements)
    buffer.seek(0)
    return buffer
