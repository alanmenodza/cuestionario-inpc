# -*- coding: utf-8 -*-
##streamlit run "D:\alan.mendoza\Documents\Capacitacion 2026\CUESTIONARIO_capaC.py"
##streamlit run "D:\alan.mendoza\Documents\Capacitacion 2026\CUESTIONARIO_capaC.py"  --server.address 0.0.0.0 --server.port 8501
# -*- coding: utf-8 -*-
"""
Tratamiento de la Información - Sistema de Evaluación INPC
"""
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import qrcode
import plotly.express as px
import socket
import streamlit.components.v1 as components

# ---------- CONFIGURACION DE PAGINA ----------
st.set_page_config(
    page_title="Sistema de Evaluación INPC",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- ESTILOS Y DISEÑO CORPORATIVO ----------
st.markdown("""
    <style>
        .main { background-color: #f8f9fa; }
        .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
        h1, h2, h3 { color: #1f4e78; }
    </style>
""", unsafe_allow_html=True)

# ---------- DIRECTORIO Y RUTAS (COMPATIBLE CON LA NUBE) ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DIR_DATOS = os.path.join(BASE_DIR, "Datos")
DIR_RESULTADOS = os.path.join(BASE_DIR, "Resultados")
os.makedirs(DIR_RESULTADOS, exist_ok=True)

archivo_csv = os.path.join(DIR_RESULTADOS, "RESULTADOS_NORTE.csv")
archivo_preguntas_ip_resul = os.path.join(DIR_RESULTADOS, "PREGUNTAS_IP_RESUL.csv")

# ---------- CARGA DE DATOS CON NORMALIZACIÓN Y CODIFICACIÓN SEGURA ----------
@st.cache_data
def cargar_datos():
    try:
        df_usuarios = pd.read_excel(os.path.join(DIR_DATOS, "participantesNORTE.xlsx"))
    except Exception:
        df_usuarios = pd.DataFrame(columns=["NOMBRE_USUARIO", "NOMBRE", "AREA", "NOMBRE_CIUDAD"])
        
    try:
        df_preguntas = pd.read_excel(os.path.join(DIR_DATOS, "preguntas_INPC.xlsx"))
        df_preguntas.columns = df_preguntas.columns.astype(str).str.strip()
        
        renombres = {}
        for col in df_preguntas.columns:
            col_upper = col.upper()
            if "PREGUNTA" in col_upper:
                renombres[col] = "Pregunta"
            elif col_upper in ["A", "OPCION_A", "OPCIÓN A"]:
                renombres[col] = "A"
            elif col_upper in ["B", "OPCION_B", "OPCIÓN B"]:
                renombres[col] = "B"
            elif col_upper in ["C", "OPCION_C", "OPCIÓN C"]:
                renombres[col] = "C"
            elif col_upper in ["D", "OPCION_D", "OPCIÓN D"]:
                renombres[col] = "D"
            elif "CORRECTA" in col_upper:
                renombres[col] = "Correcta"
                
        df_preguntas = df_preguntas.rename(columns=renombres)
        
        for c in ["Pregunta", "A", "B", "C", "D", "Correcta"]:
            if c in df_preguntas.columns:
                df_preguntas[c] = df_preguntas[c].astype(str).str.encode("utf-8", "ignore").str.decode("utf-8")
                
    except Exception:
        df_preguntas = pd.DataFrame(columns=["Pregunta", "A", "B", "C", "D", "Correcta"])
        
    return df_usuarios, df_preguntas

usuarios, preguntas = cargar_datos()

# ---------- INICIALIZACIÓN DE VARIABLES DE SESIÓN ----------
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
if "resultado_guardado" not in st.session_state:
    st.session_state.resultado_guardado = False

# ---------- BARRA LATERAL ----------
with st.sidebar:
    logo_path = os.path.join(BASE_DIR, "logo_inegi.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=200)
    else:
        st.warning("⚠️ No se encontró 'logo_inegi.png' en la ruta especificada.")

    st.markdown("### Acceso Rápido")
    st.write("Escanee el código QR para ingresar desde su dispositivo:")
    
    url = "https://cuestionario-inpc-norte.streamlit.app"
    qr_path = os.path.join(BASE_DIR, "qr_acceso.png")
    
    try:
        qr = qrcode.QRCode(version=1, box_size=12, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")
        img_qr.save(qr_path)
    except Exception as e:
        st.error(f"Error al generar QR: {e}")

    if os.path.exists(qr_path):
        st.image(qr_path, width=220, caption="Portal Web En Línea")
    else:
        st.warning("⚠️ No se pudo generar la imagen QR.")
    
    if st.button("🔍 Código QR grande", use_container_width=True):
        st.session_state.pagina = "qr_gigante"
        st.rerun()

    st.markdown("---")
    st.info("💡 **Capacitación INPC 2026**")
    st.info("📍 **ZONA NORTE**")

# ---------- 0. PANTALLA: QR GIGANTE ----------
if st.session_state.pagina == "qr_gigante":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo_path = os.path.join(BASE_DIR, "logo_inegi.png")
        if os.path.exists(logo_path):
            st.image(logo_path, width=280)
            
        st.markdown("<h1 style='text-align: center; color: #1f4e78;'>Portal de Acceso Móvil</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 20px;'>Escanee el siguiente código QR con su dispositivo móvil para ingresar directamente a la evaluación:</p>", unsafe_allow_html=True)
        
        qr_path = os.path.join(BASE_DIR, "qr_acceso.png")
        if os.path.exists(qr_path):
            st.image(qr_path, width=450)
            st.markdown(f"<h3 style='text-align: center; color: #333;'>Enlace directo: <code>{url}</code></h3>", unsafe_allow_html=True)
            
        st.markdown("---")
        if st.button("⬅️ Regresar al Sistema", use_container_width=True):
            es_admin_previo = st.session_state.usuario and (st.session_state.usuario.lower() == "alan.mendoza" or st.session_state.area.lower() in ["admin", "administrador", "sistemas"])
            st.session_state.pagina = "admin_panel" if es_admin_previo else "login"
            st.rerun()

# ---------- 1. LOGIN ----------
elif st.session_state.pagina == "login":
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        logo_path = os.path.join(BASE_DIR, "logo_inegi.png")
        if os.path.exists(logo_path):
            st.image(logo_path, width=220)
            
        st.markdown("<h1 style='text-align: center;'>Sistema de Evaluación INPC</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Acceso para Personal Operativo</p>", unsafe_allow_html=True)
        
        with st.form("form_login"):
            usuario_input = st.text_input("👤 Ingrese su Nombre de Usuario").strip()
            submit = st.form_submit_button("Entrar al Sistema", use_container_width=True)
            
            if submit:
                usuario_busq = usuario_input.lower()
                usuarios_lower = usuarios["NOMBRE_USUARIO"].astype(str).str.lower().values

                if usuario_busq in usuarios_lower:
                    datos = usuarios[usuarios["NOMBRE_USUARIO"].astype(str).str.lower() == usuario_busq]
                    st.session_state.usuario = usuario_input
                    st.session_state.nombre = datos["NOMBRE"].values[0]
                    st.session_state.area = str(datos["AREA"].values[0]).strip()
                    st.session_state.ciudad = datos["NOMBRE_CIUDAD"].values[0]
                    
                    es_admin_usuario = (usuario_busq == "alan.mendoza" or st.session_state.area.lower() in ["admin", "administrador", "sistemas"])
                    
                    if es_admin_usuario:
                        st.session_state.pagina = "admin_panel"
                        st.rerun()

                    if os.path.exists(archivo_csv):
                        try:
                            historial = pd.read_csv(archivo_csv, encoding="utf-8-sig")
                            if not historial.empty and "USUARIO" in historial.columns:
                                if usuario_input in historial["USUARIO"].astype(str).values:
                                    st.error("⚠️ Este usuario ya concluyó la evaluación anteriormente.")
                                    st.stop()
                        except Exception:
                            pass

                    total_disponible = len(preguntas)
                    n_preguntas = min(10, total_disponible)
                    
                    if n_preguntas > 0:
                        df_exam = preguntas.sample(n=n_preguntas).reset_index(drop=True)
                        
                        pregunta_comentario = pd.DataFrame([{
                            "Pregunta": "Expresa tus dudas o comentarios acerca del proceso o dificultades con el sistema.",
                            "A": "", "B": "", "C": "", "D": "", "Correcta": "COMENTARIO"
                        }])
                        df_exam = pd.concat([df_exam, pregunta_comentario], ignore_index=True)
                        
                        st.session_state.preguntas_examen = df_exam
                        st.session_state.pregunta_actual = 0
                        st.session_state.respuestas = {}
                    else:
                        st.error("No hay preguntas configuradas en el sistema.")
                        st.stop()

                    st.session_state.pagina = "bienvenida"
                    st.rerun()
                else:
                    st.error("❌ Usuario no encontrado en el padrón autorizado.")

# ---------- 2. BIENVENIDA ----------
elif st.session_state.pagina == "bienvenida":
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        logo_path = os.path.join(BASE_DIR, "logo_inegi.png")
        if os.path.exists(logo_path):
            st.image(logo_path, width=200)
            
        st.markdown(f"# ¡Bienvenido, {st.session_state.nombre}!")
        st.success("Tus credenciales han sido verificadas exitosamente.")
        
        st.markdown("### Información del Investigador de Precios")
        st.write(f"🏢 **Área:** {st.session_state.area}")
        st.write(f"📍 **Ciudad:** {st.session_state.ciudad}")
        st.markdown("---")
        st.warning("⚠️ **Instrucciones:** Una vez iniciado el examen, dispondrá de **5 minutos** para completarlo (incluye 10 preguntas de opción múltiple y un espacio final obligatorio para sus comentarios). El sistema finalizará automáticamente al cumplirse el tiempo.")
        
        if st.button("🚀 Iniciar Evaluación", use_container_width=True):
            st.session_state.inicio_examen = datetime.now()
            st.session_state.pagina = "evaluacion"
            st.rerun()

# ---------- 3. EVALUACION (INTERACTIVA CON CRONÓMETRO) ----------
elif st.session_state.pagina == "evaluacion":
    # Logotipo institucional centrado/alineado en la encuesta
    col_img1, col_img2, col_img3 = st.columns([1, 1, 1])
    with col_img2:
        logo_path = os.path.join(BASE_DIR, "logo_inegi.png")
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)

    st.subheader("📝 Cuestionario de Evaluación")
    
    # Validación de tiempo transcurrido (5 minutos = 300 segundos)
    if st.session_state.inicio_examen:
        tiempo_transcurrido = (datetime.now() - st.session_state.inicio_examen).seconds
        tiempo_restante_inicial = max(0, 300 - tiempo_transcurrido)
        
        if tiempo_transcurrido >= 300:
            st.warning("⏱️ El tiempo reglamentario ha finalizado.")
            st.session_state.pagina = "finalizar"
            st.rerun()
    else:
        tiempo_restante_inicial = 300

    # Cronómetro flotante en JavaScript
    timer_html = f"""
    <div style="font-family: sans-serif; background-color: #f0f2f6; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
        <span style="font-size: 16px; color: #31333F; font-weight: bold;">⏱️ Tiempo restante: </span>
        <span id="timer" style="font-size: 20px; color: #d9534f; font-weight: bold;">05:00</span>
    </div>
    <script>
        var timeLeft = {tiempo_restante_inicial};
        function updateTimer() {{
            var minutes = Math.floor(timeLeft / 60);
            var seconds = timeLeft % 60;
            document.getElementById('timer').innerText = 
                (minutes < 10 ? "0" : "") + minutes + ":" + (seconds < 10 ? "0" : "") + seconds;
            if (timeLeft <= 0) {{
                clearInterval(timerInterval);
                window.location.reload();
            }} else {{
                timeLeft--;
            }}
        }}
        updateTimer();
        var timerInterval = setInterval(updateTimer, 1000);
    </script>
    """
    components.html(timer_html, height=70)

    df_exam = st.session_state.preguntas_examen
    idx = st.session_state.pregunta_actual
    total_preguntas = len(df_exam)

    # Barra de progreso
    st.progress((idx + 1) / total_preguntas)
    st.markdown(f"**Pregunta {idx + 1} de {total_preguntas}**")

    fila_actual = df_exam.iloc[idx]
    texto_p = fila_actual.get("Pregunta", "")
    es_comentario = (str(fila_actual.get("Correcta", "")).strip().upper() == "COMENTARIO")

    st.markdown(f"### {texto_p}")

    # Mostrar opciones o campo de texto libre para el comentario final
    respuesta_actual = st.session_state.respuestas.get(idx, "")

    if es_comentario:
        val_resp = st.text_area("Escriba sus comentarios o dudas aquí:", value=respuesta_actual, height=150)
        st.session_state.respuestas[idx] = val_resp
    else:
        opciones = []
        opciones_letras = ["A", "B", "C", "D"]
        labels_map = {}
        for letra in opciones_letras:
            if letra in fila_actual and pd.notna(fila_actual[letra]) and str(fila_actual[letra]).strip() != "":
                val_opc = str(fila_actual[letra])
                opciones.append(val_opc)
                labels_map[val_opc] = letra

        # Determinar índice preseleccionado si ya respondió
        index_default = 0
        if respuesta_actual in opciones:
            index_default = opciones.index(respuesta_actual)

        sel_opcion = st.radio("Seleccione una opción:", opciones, index=index_default, key=f"radio_p_{idx}")
        st.session_state.respuestas[idx] = sel_opcion

    st.markdown("---")
    col_ant, col_sig = st.columns(2)

    with col_ant:
        if idx > 0:
            if st.button("⬅️ Anterior", use_container_width=True):
                st.session_state.pregunta_actual -= 1
                st.rerun()

    with col_sig:
        if idx < total_preguntas - 1:
            if st.button("Siguiente ➡️", use_container_width=True):
                st.session_state.pregunta_actual += 1
                st.rerun()
        else:
            if st.button("✅ Finalizar y Enviar Evaluación", use_container_width=True):
                st.session_state.pagina = "finalizar"
                st.rerun()

# ---------- 4. FINALIZAR ----------
elif st.session_state.pagina == "finalizar":
    if not st.session_state.resultado_guardado:
        aciertos = 0
        total_preguntas_calificadas = 0
        
        lista_detalles = []
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for i, fila in st.session_state.preguntas_examen.iterrows():
            texto_pregunta = str(fila.get("Pregunta", ""))
            respuesta_usuario = str(st.session_state.respuestas.get(i, "Sin responder")).strip()
            respuesta_correcta_raw = str(fila.get("Correcta", "")).strip()
            
            es_comentario = (respuesta_correcta_raw.upper() == "COMENTARIO")

            if es_comentario:
                estatus_txt = "Comentario / Retroalimentación"
                es_correcta = False
            else:
                total_preguntas_calificadas += 1
                es_correcta = False
                
                if pd.notna(fila["Correcta"]) and respuesta_correcta_raw != "":
                    resp_usuario_clean = respuesta_usuario.lower().strip()
                    corr_clean = respuesta_correcta_raw.lower().strip()
                    
                    texto_opcion_correcta_real = ""
                    if corr_clean in ["a", "b", "c", "d"] and corr_clean.upper() in fila:
                        texto_opcion_correcta_real = str(fila[corr_clean.upper()]).lower().strip()
                    
                    coincide_por_letra = (corr_clean in ["a", "b", "c", "d"] and resp_usuario_clean == texto_opcion_correcta_real)
                    coincide_por_texto_directo = (resp_usuario_clean == corr_clean)
                    
                    coincide_texto_opciones = False
                    for letra_opc in ["a", "b", "c", "d"]:
                        if letra_opc in fila and pd.notna(fila[letra_opc]):
                            if resp_usuario_clean == str(fila[letra_opc]).lower().strip() and corr_clean == str(fila[letra_opc]).lower().strip():
                                coincide_texto_opciones = True
                                break

                    if coincide_por_letra or coincide_por_texto_directo or coincide_texto_opciones:
                        aciertos += 1
                        es_correcta = True
                
                estatus_txt = "Correcta" if es_correcta else "Incorrecta"

            texto_resp_corr_audit = respuesta_correcta_raw
            if respuesta_correcta_raw.upper() in ["A", "B", "C", "D"] and respuesta_correcta_raw.upper() in fila:
                texto_resp_corr_audit = f"{respuesta_correcta_raw.upper()}: {fila[respuesta_correcta_raw.upper()]}"

            lista_detalles.append({
                "USUARIO": st.session_state.usuario,
                "NOMBRE": st.session_state.nombre,
                "AREA": st.session_state.area,
                "CIUDAD": st.session_state.ciudad,
                "FECHA": fecha_actual,
                "PREGUNTA": texto_pregunta,
                "RESPUESTA_DADA": respuesta_usuario,
                "RESPUESTA_CORRECTA": texto_resp_corr_audit if not es_comentario else "N/A",
                "ESTATUS": estatus_txt
            })

        calificacion_calculada = (aciertos / total_preguntas_calificadas) * 100 if total_preguntas_calificadas > 0 else 0

        resultado = pd.DataFrame({
            "USUARIO": [st.session_state.usuario],
            "NOMBRE": [st.session_state.nombre],
            "AREA": [st.session_state.area],
            "CIUDAD": [st.session_state.ciudad],
            "ACIERTOS": [int(aciertos)],
            "TOTAL": [int(total_preguntas_calificadas)],
            "CALIFICACION": [round(float(calificacion_calculada), 2)],
            "FECHA": [fecha_actual]
        })
        
        file_exists = os.path.exists(archivo_csv)
        resultado.to_csv(archivo_csv, mode="a", header=not file_exists, index=False, encoding="utf-8-sig")

        df_detalles_nuevo = pd.DataFrame(lista_detalles)
        file_det_exists = os.path.exists(archivo_preguntas_ip_resul)
        df_detalles_nuevo.to_csv(archivo_preguntas_ip_resul, mode="a", header=not file_det_exists, index=False, encoding="utf-8-sig")
            
        st.session_state.resultado_guardado = True

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo_path = os.path.join(BASE_DIR, "logo_inegi.png")
        if os.path.exists(logo_path):
            st.image(logo_path, width=200)

        st.markdown("<h1 style='text-align: center; color: #1f4e78;'>¡Muchas Gracias!</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 18px;'>Su evaluación y comentarios han sido registrados exitosamente en el sistema.</p>", unsafe_allow_html=True)
        st.success("✨ Puede cerrar esta ventana o salir de la sesión de manera segura.")
        
        if st.button("🚪 Salir / Cerrar Sesión", use_container_width=True):
            st.session_state.pagina = "login"
            st.session_state.pregunta_actual = 0
            st.session_state.respuestas = {}
            st.session_state.inicio_examen = None
            st.session_state.resultado_guardado = False
            if "preguntas_examen" in st.session_state:
                del st.session_state.preguntas_examen
            st.rerun()

# ---------- 5. PANEL DE ADMINISTRACIÓN ----------
elif st.session_state.pagina == "admin_panel":
    st.title("🔒 Panel de Administración y Estadísticas INPC")
    st.success(f"Bienvenido al panel de control, **{st.session_state.nombre}** (Administrador).")
    
    col_salir, col_borrar = st.columns([2, 1])
    with col_salir:
        if st.button("🚪 Cerrar Sesión de Administrador"):
            st.session_state.pagina = "login"
            st.session_state.usuario = ""
            st.session_state.nombre = ""
            st.session_state.area = ""
            st.rerun()
            
    with col_borrar:
        if st.button("🗑️ Borrar Todas las Estadísticas", type="primary"):
            st.session_state.confirmar_borrado = True

    if st.session_state.get("confirmar_borrado", False):
        st.warning("⚠️ **¿Estás completamente seguro?** Esta acción eliminará permanentemente todos los resultados, calificaciones y comentarios registrados hasta el momento.")
        col_si, col_no = st.columns(2)
        with col_si:
            if st.button("Sí, borrar todo", use_container_width=True):
                try:
                    if os.path.exists(archivo_csv):
                        os.remove(archivo_csv)
                    if os.path.exists(archivo_preguntas_ip_resul):
                        os.remove(archivo_preguntas_ip_resul)
                    st.success("✅ Los registros y estadísticas han sido eliminados correctamente.")
                    st.session_state.confirmar_borrado = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar los archivos: {e}")
        with col_no:
            if st.button("Cancelar", use_container_width=True):
                st.session_state.confirmar_borrado = False
                st.rerun()

    st.markdown("---")
    
    if os.path.exists(archivo_csv):
        try:
            resultados = pd.read_csv(archivo_csv, encoding="utf-8-sig")
        except Exception:
            resultados = pd.DataFrame()
        
        if not resultados.empty:
            resultados["ACIERTOS"] = pd.to_numeric(resultados["ACIERTOS"], errors="coerce").fillna(0)
            resultados["TOTAL"] = pd.to_numeric(resultados["TOTAL"], errors="coerce").fillna(10)
            resultados["CALIFICACION"] = (resultados["ACIERTOS"] / resultados["TOTAL"]) * 100

            st.subheader("📋 Concentrado General de Participantes")
            st.dataframe(resultados, use_container_width=True)
            
            total_aciertos_general = int(resultados["ACIERTOS"].sum())
            total_preguntas_general = int(resultados["TOTAL"].sum())
            promedio_general = float(resultados["CALIFICACION"].mean())
            max_calificacion = float(resultados["CALIFICACION"].max())

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Evaluados", len(resultados))
            m2.metric("Aciertos Totales", f"{total_aciertos_general} / {total_preguntas_general}")
            m3.metric("Promedio General", f"{promedio_general:.2f}%")
            m4.metric("Calificación Máxima", f"{max_calificacion:.2f}%")
            
            st.markdown("---")
            c1, c2 = st.columns(2)
            
            with c1:
                fig_hist = px.histogram(
                    resultados, 
                    x="CALIFICACION", 
                    nbins=10, 
                    title="Distribución de Calificaciones", 
                    color_discrete_sequence=["#1f4e78"],
                    range_x=[0, 100]
                )
                fig_hist.update_layout(xaxis_title="Calificación (%)", yaxis_title="Cantidad de Investigadores")
                st.plotly_chart(fig_hist, use_container_width=True)
                
            with c2:
                aprobados = len(resultados[resultados["CALIFICACION"] >= 70])
                reprobados_cant = len(resultados[resultados["CALIFICACION"] < 70])
                
                fig_pie = px.pie(
                    names=["Aprobados (≥70%)", "Reprobados (<70%)"],
                    values=[aprobados, reprobados_cant],
                    title="Estatus General de Aprobación",
                    color_discrete_sequence=["#2ca02c", "#d9534f"]
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            c3, c4 = st.columns(2)
            with c3:
                if "CIUDAD" in resultados.columns:
                    por_ciudad = resultados.groupby("CIUDAD")["CALIFICACION"].mean().reset_index()
                    fig_bar_c = px.bar(por_ciudad, x="CIUDAD", y="CALIFICACION", title="Rendimiento Promedio por Ciudad", color="CIUDAD", range_y=[0, 100])
                    st.plotly_chart(fig_bar_c, use_container_width=True)
                    
            with c4:
                if os.path.exists(archivo_preguntas_ip_resul):
                    try:
                        df_detalles_err = pd.read_csv(archivo_preguntas_ip_resul, encoding="utf-8-sig")
                        if not df_detalles_err.empty and "ESTATUS" in df_detalles_err.columns:
                            df_errores = df_detalles_err[df_detalles_err["ESTATUS"] == "Incorrecta"]
                            if not df_errores.empty:
                                top_errores = df_errores.groupby("PREGUNTA").size().reset_index(name="TOTAL_ERRORES")
                                top_errores = top_errores.sort_values(by="TOTAL_ERRORES", ascending=False).head(5)
                                
                                top_errores["PREGUNTA_CORTA"] = top_errores["PREGUNTA"].apply(lambda x: x[:45] + "..." if len(str(x)) > 45 else str(x))
                                
                                fig_bar_err = px.bar(
                                    top_errores, 
                                    x="TOTAL_ERRORES", 
                                    y="PREGUNTA_CORTA", 
                                    orientation="h",
                                    title="Top 5 - Preguntas con Más Errores",
                                    labels={"TOTAL_ERRORES": "Cantidad de Errores", "PREGUNTA_CORTA": "Pregunta"},
                                    color="TOTAL_ERRORES",
                                    color_continuous_scale="Reds"
                                )
                                fig_bar_err.update_layout(yaxis=dict(autorange="reversed"))
                                st.plotly_chart(fig_bar_err, use_container_width=True)
                            else:
                                st.info("✨ Aún no hay registros de respuestas incorrectas.")
                        else:
                            st.info("Aún no hay datos de auditoría suficientes.")
                    except Exception:
                        st.info("No se pudo procesar la gráfica de errores.")
                else:
                    st.info("Esperando registros en PREGUNTAS_IP_RESUL.csv para generar la gráfica de errores.")                
            
            st.markdown("---")
            st.subheader("💬 Buzón de Dudas y Comentarios Obligatorios del Personal IP")
            if os.path.exists(archivo_preguntas_ip_resul):
                try:
                    df_comentarios = pd.read_csv(archivo_preguntas_ip_resul, encoding="utf-8-sig")
                    df_comentarios = df_comentarios[df_comentarios["ESTATUS"] == "Comentario / Retroalimentación"]
                    if not df_comentarios.empty:
                        for _, row in df_comentarios.iterrows():
                            with st.container():
                                st.markdown(f"**👤 {row['NOMBRE']}** *({row['AREA']} - {row['CIUDAD']})* / Fecha: {row['FECHA']}")
                                st.info(f"\"{row['RESPUESTA_DADA']}\"")
                    else:
                        st.success("Aún no hay comentarios o dudas registradas por los participantes.")
                except Exception:
                    st.info("Sin comentarios registrados todavía.")
            
            st.markdown("---")
            st.subheader("⚠️ Análisis de Áreas de Oportunidad y Errores")
            reprobados_df = resultados[resultados["CALIFICACION"] < 70]
            if not reprobados_df.empty:
                st.warning(f"Se detectaron {len(reprobados_df)} evaluaciones con calificación menor al 70%.")
                st.dataframe(reprobados_df[["USUARIO", "NOMBRE", "AREA", "CIUDAD", "CALIFICACION"]], use_container_width=True)
            else:
                st.success("✨ ¡Excelente desempeño! Ningún participante se encuentra por debajo del 70% de calificación.")
        else:
            st.info("Aún no hay registros en el concentrado de resultados.")
    else:
        st.info("El archivo de resultados todavía no ha sido generado. Esperando a que el primer usuario realice la evaluación.")
