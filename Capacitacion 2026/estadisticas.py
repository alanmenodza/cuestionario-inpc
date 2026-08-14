# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 15:18:59 2026

@author: ALAN.MENDOZA
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import os

st.set_page_config(
    page_title="Dashboard Capacitación",
    page_icon="📊",
    layout="wide"
)

st.title("Dashboard de Resultados")

st_autorefresh(
    interval=10000,
    key="dashboard"
)

BASE_DIR = r"D:\alan.mendoza\Documents\Capacitacion 2026"

archivo = os.path.join(
    BASE_DIR,
    "Resultados",
    "RESULTADOS.csv"
)

if not os.path.exists(archivo):
    st.warning("Aún no existen resultados.")
    st.stop()

resultados = pd.read_csv(archivo)

# ---------------- KPI ----------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Participantes",
    len(resultados)
)

col2.metric(
    "Promedio General",
    round(resultados["CALIFICACION"].mean(), 2)
)

col3.metric(
    "Máxima",
    resultados["CALIFICACION"].max()
)

col4.metric(
    "Mínima",
    resultados["CALIFICACION"].min()
)

st.divider()

# ---------------- HISTOGRAMA ----------------

fig = px.histogram(
    resultados,
    x="CALIFICACION",
    nbins=10,
    title="Distribución de Calificaciones"
)

st.plotly_chart(
    fig,
    width="stretch"
)

# ---------------- CIUDAD ----------------

por_ciudad = (
    resultados
    .groupby("CIUDAD")["CALIFICACION"]
    .mean()
    .reset_index()
)

fig = px.bar(
    por_ciudad,
    x="CIUDAD",
    y="CALIFICACION",
    title="Promedio por Ciudad"
)

st.plotly_chart(
    fig,
    width="stretch"
)

# ---------------- AREA ----------------

por_area = (
    resultados
    .groupby("AREA")["CALIFICACION"]
    .mean()
    .reset_index()
)

fig = px.bar(
    por_area,
    x="AREA",
    y="CALIFICACION",
    title="Promedio por Área"
)

st.plotly_chart(
    fig,
    width="stretch"
)

# ---------------- RANKING ----------------

st.subheader("Ranking de Participantes")

ranking = resultados.sort_values(
    by="CALIFICACION",
    ascending=False
)

st.dataframe(
    ranking[
        [
            "NOMBRE",
            "AREA",
            "CIUDAD",
            "CALIFICACION"
        ]
    ],
    width="stretch"
)

# ---------------- EXPORTAR ----------------

with open(archivo, "rb") as f:

    st.download_button(
        "📥 Descargar Resultados",
        f,
        file_name="RESULTADOS.csv",
        mime="text/csv"
    )