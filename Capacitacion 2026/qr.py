# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 14:21:17 2026

@author: ALAN.MENDOZA
"""
##streamlit run "D:\alan.mendoza\Documents\Capacitacion 2026\qr.py"
import streamlit as st
import qrcode

st.set_page_config(
    page_title="Acceso a Evaluación",
    page_icon="📱",
    layout="centered"
)

URL = "http://192.168.100.62:8501"

qr = qrcode.make(URL)

qr.save("qr_acceso.png")

st.title("Capacitación 2026")

st.markdown("## Escanee el código QR para iniciar la evaluación")

st.image(
    "qr_acceso.png",
    width=500
)

st.code(URL)

st.info(
    f"Si no puede escanear el QR, ingrese a:\n\n{URL}"
)

st.success(
    "Puede utilizar celular, tableta o computadora."
)