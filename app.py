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
st.success("Si deseas añadir tu impresión en la cola, escribe al 926 719 339")
st.success("Nota> Las impresiones Soccer no estaran hasta nuevo aviso.")

st.markdown("---")

# 2. Conexión directa a la hoja y pestaña correcta utilizando tu link original
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
        # Validar fila usando la columna A (índice 0)
        cotizador_base = str(fila[0]).strip() if pd.notna(fila[0]) else ""
        
        # Ignorar celdas vacías o con ceros de relleno
        if not cotizador_base or cotizador_base in ["0", "0.0", "COTIZADOR"]:
            continue
            
        # Mapeo de columnas de interfaz
        # Columna S (índice 18): Nombre del usuario en la interfaz
        cliente = str(fila[18]).strip() if pd.notna(fila[18]) else ""
        if cliente == "":
            # Respaldo en columna R (índice 17) o columna A
            cliente = str(fila[17]).strip() if pd.notna(fila[17]) else cotizador_base

        # Tiempos base originales (Columnas B, C, D) para alimentar la cuenta regresiva real
        try:
            h = int(float(fila[1])) if pd.notna(fila[1]) else 0
            m = int(float(fila[2])) if pd.notna(fila[2]) else 0
            s = int(float(fila[3])) if pd.notna(fila[3]) else 0
        except:
            h, m, s = 0, 0, 0
            
        # Columna T (índice 19): Tu texto de tiempo precalculado (ej: "26m 46s")
        tiempo_excel = str(fila[19]).strip() if pd.notna(fila[19]) else f"{h}h {m}m {s}s"
        
        # Columna U (índice 20): Menú desplegable de ESTADO
        estado = str(fila[20]).strip().upper() if pd.notna(fila[20]) else "EN ESPERA"
        
        # Cálculo de segundos totales asignados
        segundos_totales = (h * 3600) + (m * 60) + s
        
        # 3. Lógica del motor de estados interactivo
        if "LISTO" in estado or "FINALIZADO" in estado:
            tiempo_mostrar = "✅ ¡Listo para recoger!"
        elif "IMPRIMIENDO" in estado or "IMPR..." in estado:
            # Cuenta regresiva en tiempo real descontando el segundero del servidor
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
            # Estado "En espera" o si la celda está vacía
            tiempo_mostrar = f"💤 En cola ({tiempo_excel})"
            
        lista_final.append({
            "CLIENTE": cliente,
            "ESTADO DE TU PIEZA": tiempo_mostrar
        })
        
    df_publico = pd.DataFrame(lista_final)

    # Buscador en tiempo real
    buscador = st.text_input("", placeholder="🔍 Escribe tu nombre para buscar tu orden...").strip().upper()
    if buscador:
        df_publico = df_publico[df_publico["CLIENTE"].str.upper().str.contains(buscador)]
        
    # 4. Mostrar la tabla de cara al cliente
    st.dataframe(
        df_publico, 
        use_container_width=True,
        hide_index=True
    )
    
    # Forzar refresco automático cada 1 segundo para actualizar los relojes
    time.sleep(1)
    st.rerun()

except Exception as e:
    st.info("🔄 Sincronizando la cola de impresión H2D en tiempo real...")