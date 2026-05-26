import streamlit as st
import pandas as pd
import time

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

# Subtexto fijo informativo para tus clientes
st.info("Nota: Las impresiones Soccer no estarán disponibles hasta nuevo aviso.")

st.markdown("---")

# 2. Conexión directa a la hoja utilizando tu link verificado
ID_DOCUMENTO = "1NakggbHZbtXNiueW316bHAo8wpDkQdS_"
GOOGLE_SHEETS_URL = f"https://docs.google.com/spreadsheets/d/{ID_DOCUMENTO}/export?format=csv&gid=907422749"

def cargar_datos_frescos():
    return pd.read_csv(GOOGLE_SHEETS_URL, header=None, encoding='utf-8')

try:
    df_completo = cargar_datos_frescos()
    
    # Empezamos el procesamiento desde la fila 9 (índice 8 en Python)
    df_datos = df_completo.iloc[8:].copy()
    
    lista_final = []
    
    for idx, fila in df_datos.iterrows():
        # Valores base de las columnas clave
        cotizador_base = str(fila[0]).strip() if pd.notna(fila[0]) else ""
        cliente = str(fila[18]).strip() if pd.notna(fila[18]) else "" # Columna S (Usuario)
        
        # Si no hay cotizador ni nombre de usuario, es una fila vacía
        if (not cotizador_base or cotizador_base in ["0", "0.0", "COTIZADOR"]) and not cliente:
            continue
            
        # Si el campo de usuario tiene texto, ese es nuestro cliente principal
        if cliente == "":
            cliente = str(fila[17]).strip() if pd.notna(fila[17]) else cotizador_base

        # Tiempos de las columnas B, C, D para el reloj interno
        try:
            h = int(float(fila[1])) if pd.notna(fila[1]) else 0
            m = int(float(fila[2])) if pd.notna(fila[2]) else 0
            s = int(float(fila[3])) if pd.notna(fila[3]) else 0
        except:
            h, m, s = 0, 0, 0
            
        # Columna T (índice 19): Tiempo precalculado limpio de tu Excel
        tiempo_excel = str(fila[19]).strip() if pd.notna(fila[19]) else f"{h}h {m}m {s}s"
        
        # Columna U (índice 20): Menú desplegable de ESTADO
        estado = str(fila[20]).strip().upper() if pd.notna(fila[20]) else "EN ESPERA"
        
        # Cálculo de segundos totales
        segundos_totales = (h * 3600) + (m * 60) + s
        
        # 3. Lógica del motor de estados interactivo
        if "LISTO" in estado or "FINALIZADO" in estado:
            tiempo_mostrar = "✅ ¡Listo para recoger!"
        elif "IMPRIMIENDO" in estado or "IMPR..." in estado:
            segundos_actuales = int(time.time()) % 60
            segundos_restantes = max(0, segundos_totales - segundos_actuales)
            
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
            
        lista_final.append({
            "CLIENTE": cliente,
            "ESTADO DE TU PIEZA": tiempo_mostrar
        })
        
    df_publico = pd.DataFrame(lista_final)

    # Buscador interactivo en tiempo real
    buscador = st.text_input("", placeholder="🔍 Escribe tu nombre para buscar tu orden...").strip().upper()
    if buscador:
        # Si busca algo, filtramos sobre la lista completa para que encuentre su orden esté donde esté
        df_publico = df_publico[df_publico["CLIENTE"].str.upper().str.contains(buscador)]
    else:
        # 🎯 Si no hay búsqueda, limitamos la vista de la tabla a los primeros 10 elementos activos
        df_publico = df_publico.head(10)
        
    # 4. Mostrar la tabla final en la pantalla del usuario
    st.dataframe(
        df_publico, 
        use_container_width=True,
        hide_index=True
    )
    
    # Auto-refresco en vivo cada 1 segundo
    time.sleep(1)
    st.rerun()

except Exception as e:
    st.info("🔄 Sincronizando la cola de impresión H2D en tiempo real...")