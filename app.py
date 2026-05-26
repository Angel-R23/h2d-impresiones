import streamlit as st
import pandas as pd
import time
import random

# 1. Ajustes visuales de la interfaz (Tema Oscuro GitHub)
st.set_page_config(
    page_title="H2D 3D Printing Status",
    page_icon="🖨️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        .stApp { background-color: #0d1117; color: #c9d1d9; }
        h1 { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-weight: 600; color: #f0f6fc; }
        .stTextInput input {
            background-color: #161b22 !important;
            color: #c9d1d9 !important;
            border: 1px solid #30363d !important;
            border-radius: 6px !important;
        }
        .stTextInput input:focus { border-color: #58a6ff !important; box-shadow: none !important; }
        .stDataFrame { border: 1px solid #30363d; border-radius: 6px; background-color: #161b22; }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 IMPRESIONES CEDIM")
st.write("Bienvenido, esta es la lista en tiempo real para las impresiones.")
st.success("Si deseas añadir tu impresión en la cola, escribe al 902 441 990")

st.info("Nota: Las impresiones Soccer no estarán disponibles hasta nuevo aviso.")

st.markdown("---")

# 🛠️ Inicializar la memoria de los cronómetros en el servidor si no existe
if "cronometros" not in st.session_state:
    st.session_state.cronometros = {}

# 2. Conexión directa a la hoja utilizando tu link verificado
ID_DOCUMENTO = "1NakggbHZbtXNiueW316bHAo8wpDkQdS_"

# 🎯 FUNCIÓN CRÍTICA: Descarga el Excel ignorando la caché del servidor
def cargar_datos_frescos():
    # Agregamos un parámetro aleatorio al final del link (?v=12345) para obligar a descargar el archivo real
    rompe_cache = random.randint(1, 999999)
    url_realtime = f"https://docs.google.com/spreadsheets/d/{ID_DOCUMENTO}/export?format=csv&gid=907422749&v={rompe_cache}"
    return pd.read_csv(url_realtime, header=None, encoding='utf-8')

try:
    df_completo = cargar_datos_frescos()
    
    # Empezamos el procesamiento desde la fila 9 (índice 8 en Python)
    df_datos = df_completo.iloc[8:].copy()
    
    lista_final = []
    tiempo_actual_sistema = time.time()
    
    for idx, fila in df_datos.iterrows():
        # Valores base de las columnas clave
        cotizador_base = str(fila[0]).strip() if pd.notna(fila[0]) else ""
        cliente = str(fila[18]).strip() if pd.notna(fila[18]) else "" # Columna S (Usuario)
        
        if (not cotizador_base or cotizador_base in ["0", "0.0", "COTIZADOR"]) and not cliente:
            continue
            
        if cliente == "":
            cliente = str(fila[17]).strip() if pd.notna(fila[17]) else cotizador_base

        # Tiempos de las columnas B, C, D para el cálculo total
        try:
            h = int(float(fila[1])) if pd.notna(fila[1]) else 0
            m = int(float(fila[2])) if pd.notna(fila[2]) else 0
            s = int(float(fila[3])) if pd.notna(fila[3]) else 0
        except:
            h, m, s = 0, 0, 0
            
        tiempo_excel = str(fila[19]).strip() if pd.notna(fila[19]) else f"{h}h {m}m {s}s"
        estado = str(fila[20]).strip().upper() if pd.notna(fila[20]) else "EN ESPERA"
        
        segundos_totales_excel = (h * 3600) + (m * 60) + s
        identificador_pieza = f"{cliente}_{idx}"
        
        # 3. Motor de Memoria con REINICIO ESTRICTO por cambio de valor
        if "LISTO" in estado or "FINALIZADO" in estado:
            tiempo_mostrar = "✅ ¡Listo para recoger!"
            if identificador_pieza in st.session_state.cronometros:
                del st.session_state.cronometros[identificador_pieza]
        elif "IMPRIMIENDO" in estado or "IMPR..." in estado:
            
            # Si el usuario no existía en memoria, o si el tiempo en el Excel cambió de verdad, reseteamos a cero.
            if (identificador_pieza not in st.session_state.cronometros) or (st.session_state.cronometros[identificador_pieza]["tiempo_inicial_excel"] != segundos_totales_excel):
                st.session_state.cronometros[identificador_pieza] = {
                    "tiempo_inicial_excel": segundos_totales_excel,
                    "hora_registro_servidor": tiempo_actual_sistema
                }
            
            # Calcular cuánto tiempo real ha transcurrido desde el cambio detectado
            tiempo_transcurrido = tiempo_actual_sistema - st.session_state.cronometros[identificador_pieza]["hora_registro_servidor"]
            segundos_restantes = max(0, segundos_totales_excel - int(tiempo_transcurrido))
            
            if segundos_restantes == 0:
                tiempo_mostrar = "✅ Finalizando componentes..."
            else:
                hrs = segundos_restantes // 3600
                mins = (segundos_restantes % 3600) // 60
                segs = segundos_restantes % 60
                
                if hrs > 0:
                    tiempo_mostrar = f"⏳ Imprimiendo: {hrs}h {mins}m {segs}s"
                elif mins > 0:
                    tiempo_mostrar = f"⏳ Imprimiendo: {mins}m {segs}s"
                else:
                    tiempo_mostrar = f"⏳ ¡Faltan solo {segs}s!"
        else:
            tiempo_mostrar = f"💤 En cola ({tiempo_excel})"
            if identificador_pieza in st.session_state.cronometros:
                del st.session_state.cronometros[identificador_pieza]
            
        lista_final.append({
            "CLIENTE": cliente,
            "ESTADO DE TU PIEZA": tiempo_mostrar
        })
        
    df_publico = pd.DataFrame(lista_final)

    # Buscador interactivo
    buscador = st.text_input("", placeholder="🔍 Escribe tu nombre para buscar tu orden...").strip().upper()
    if buscador:
        df_publico = df_publico[df_publico["CLIENTE"].str.upper().str.contains(buscador)]
    else:
        df_publico = df_publico.head(10)
        
    st.dataframe(
        df_publico, 
        use_container_width=True,
        hide_index=True
    )
    
    # Refresco continuo cada 1 segundo
    time.sleep(1)
    st.rerun()

except Exception as e:
    st.info("🔄 Sincronizando la cola de impresión CEDIM en tiempo real...")




















































































































































































































































































