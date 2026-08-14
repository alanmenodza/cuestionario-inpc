# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 10:03:14 2026

@author: ALAN.MENDOZA
"""
##streamlit run "D:\alan.mendoza\Documents\Capacitacion 2026\app.py"
import streamlit as st
import pandas as pd
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import qrcode

# ---------- CONFIGURACION ----------

st.set_page_config(
    page_title="Sistema de Evaluación",
    page_icon="📊",
    layout="wide"
)

# ---------- CARGA DE DATOS ----------

usuarios = pd.read_excel(
    r"D:\alan.mendoza\Documents\Capacitacion 2026\Datos\participantes.xlsx"
)

preguntas = pd.read_excel(
    r"D:\alan.mendoza\Documents\Capacitacion 2026\Datos\preguntas.xlsx"
)

##preguntas la azar--
if "preguntas_examen" not in st.session_state:

    st.session_state.preguntas_examen = (
        preguntas.sample(
            n=10,
            random_state=None
        ).reset_index(drop=True)
    )
    
############----------- donde se guarda-----------
BASE_DIR = r"D:\alan.mendoza\Documents\Capacitacion 2026"

archivo = os.path.join(
    BASE_DIR,
    "Resultados",
    "RESULTADOS.csv"
)

# ---------- variables de sesion----------
if "pagina" not in st.session_state:
    st.session_state.pagina = "login"

if "usuario" not in st.session_state:
    st.session_state.usuario = ""

if "nombre" not in st.session_state:
    st.session_state.nombre = ""

if "area" not in st.session_state:
    st.session_state.area = ""

if "ciudad" not in st.session_state:
    st.session_state.ciudad = ""

if "pregunta_actual" not in st.session_state:
    st.session_state.pregunta_actual = 0

if "respuestas" not in st.session_state:
    st.session_state.respuestas = {}

if "inicio_examen" not in st.session_state:
    st.session_state.inicio_examen = None
    



# ---------- LOGIN ----------

if st.session_state.pagina == "login":

    st.title("Sistema de Evaluación")

    usuario = st.text_input("Usuario")

    if st.button("Entrar"):

        existe = usuario in usuarios["NOMBRE_USUARIO"].astype(str).values

        if existe:

            datos = usuarios[
                usuarios["NOMBRE_USUARIO"].astype(str) == usuario
            ]

            st.session_state.usuario = usuario
            st.session_state.nombre = datos["NOMBRE"].values[0]
            st.session_state.area = datos["AREA"].values[0]
            st.session_state.ciudad = datos["NOMBRE_CIUDAD"].values[0]

            st.session_state.pagina = "bienvenida"

            st.rerun()

        else:
            st.error("Usuario no encontrado")

        archivo = os.path.join(
            BASE_DIR,
            "Resultados",
            "RESULTADOS.csv"
            )
        
        if os.path.exists(archivo):
        
            historial = pd.read_csv(archivo)
        
            if usuario in historial["USUARIO"].astype(str).values:
        
                st.error(
                    "Este usuario ya realizó la evaluación."
                )
        
                st.stop()
# ---------- BIENVENIDA ----------

elif st.session_state.pagina == "bienvenida":

    st.title("Bienvenido")

    st.success(st.session_state.nombre)

    st.write("Área:", st.session_state.area)
    st.write("Ciudad:", st.session_state.ciudad)

    if st.button("Iniciar Evaluación"):

        st.session_state.preguntas_examen = (
            preguntas.sample(
                n=10
            ).reset_index(drop=True)
        )
    
        st.session_state.inicio_examen = datetime.now()
        st.session_state.pagina = "evaluacion"
    
        st.rerun()


# ---------- EVALUACION ----------

elif st.session_state.pagina == "evaluacion":
    st_autorefresh(interval=1000, key="timer")

    duracion = 15 * 60

    transcurrido = (
        datetime.now() -
        st.session_state.inicio_examen
    ).seconds

    restante = duracion - transcurrido

    minutos = max(0, restante // 60)
    segundos = max(0, restante % 60)

    st.error(
        f"⏰ Tiempo restante: {minutos:02}:{segundos:02}"
    )

    if restante <= 0:

        st.session_state.pagina = "finalizar"

        st.rerun()

    total = len(st.session_state.preguntas_examen)

    avance = (
        st.session_state.pregunta_actual + 1
    ) / total

    st.progress(avance)

    indice = st.session_state.pregunta_actual

    pregunta = (
    st.session_state.preguntas_examen
    .iloc[indice]
)

    st.subheader(
        f"Pregunta {indice + 1} de {total}"
    )

    st.write(pregunta["Pregunta"])

    opciones = [
        pregunta["A"],
        pregunta["B"],
        pregunta["C"],
        pregunta["D"]
    ]

    respuesta = st.radio(
        "Seleccione una opción",
        opciones,
        key=f"pregunta_{indice}"
    )

    if st.button("Siguiente"):

        st.session_state.respuestas[indice] = respuesta

        if indice < total - 1:

            st.session_state.pregunta_actual += 1

        else:

            st.session_state.pagina = "finalizar"

        st.rerun()


# ---------- FINALIZAR ----------
if "resultado_guardado" not in st.session_state:
    st.session_state.resultado_guardado = False
    
elif st.session_state.pagina == "finalizar":
    st.write("Estoy en FINALIZAR")
    aciertos = 0

    for i, fila in (
    st.session_state.preguntas_examen
    .iterrows()
):

        if i in st.session_state.respuestas:

            respuesta_usuario = st.session_state.respuestas[i]

            correcta = fila[fila["Correcta"]]

            if respuesta_usuario == correcta:

                aciertos += 1

    calificacion = (
    aciertos /
    len(st.session_state.preguntas_examen)
) * 100

    st.title("Resultado")

    st.metric(
        "Calificación",
        f"{calificacion:.2f}%"
    )
            
    resultado = pd.DataFrame({
        "USUARIO": [st.session_state.usuario],
        "NOMBRE": [st.session_state.nombre],
        "AREA": [st.session_state.area],
        "CIUDAD": [st.session_state.ciudad],
        "ACIERTOS": [aciertos],
        "TOTAL": [
    len(
        st.session_state.preguntas_examen
    )
],
        "CALIFICACION": [round(calificacion, 2)],
        "FECHA": [datetime.now()]
    })
    
    st.write(os.getcwd())
    st.write(os.path.abspath("Resultados/RESULTADOS.csv"))
    if not st.session_state.resultado_guardado:
            
    
        os.makedirs(os.path.dirname(archivo), exist_ok=True)
    
        if os.path.exists(archivo):
    
            resultado.to_csv(
                archivo,
                mode="a",
                header=False,
                index=False
            )
    
        else:
    
            resultado.to_csv(
                archivo,
                index=False
            )
    
        st.session_state.resultado_guardado = True
        
        st.success("Resultado guardado")
    



    if st.button("Cerrar Sesión"):
    
        st.session_state.pagina = "login"
        st.session_state.pregunta_actual = 0
        st.session_state.respuestas = {}
        st.session_state.inicio_examen = None
        st.session_state.resultado_guardado = False
        
        if "preguntas_examen" in st.session_state:
            del st.session_state.preguntas_examen

        st.rerun()
