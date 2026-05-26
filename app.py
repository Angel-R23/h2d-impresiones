import streamlit as st
import pandas as pd
import time

# 1. Ajustes de la interfaz visual estilo Dark Mode Profesional
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

st.title("🚀 ¡Hola, soy Angel!")
st.write("Bienvenido, esta es la lista en tiempo real para las impresiones.")
st.success("Si deseas añadir tu impresión en la cola, escribe al 926 719 339")

st.markdown("---")

# 2. Conexión usando el ID verificado de tu hoja "Hoja de cálculo sin título"
ID_DOCUMENTO = "1G9JXP3i_c40sZpdJdMT6rCJTCq5ESDwAgB5u05YOb8"
GOOGLE_SHEETS_URL = f"https://docs.google.com/spreadsheets/d/{ID_DOCUMENTO}/export?format=csv&gid=0"

def cargar_datos_frescos():
    return pd.read_csv(GOOGLE_SHEETS_URL, header=None, encoding='utf-8')

try:
    df_completo = cargar_datos_frescos()
    
    # Empezamos a mapear desde la fila 9 (índice 8 en Python)
    df_datos = df_completo.iloc[8:].copy()
    
    lista_final = []
    
    for idx, fila in df_datos.iterrows():
        # Columna A (índice 0): Cotizador base original para validar si la fila tiene un registro
        cotizador_base = str(fila[0]).strip() if pd.notna(fila[0]) else ""
        
        # Si la fila no contiene un cliente válido o tiene ceros de relleno, la ignoramos para limpiar la web
        if not cotizador_base or cotizador_base in ["0", "0.0", "COTIZADOR"]:
            continue
            
        # Minitabla de Interfaz basada en tu última captura:
        # Columna S (índice 18): Nombre de usuario del cliente
        cliente = str(fila[18]).strip() if pd.notna(fila[18]) else ""
        # Si la celda de usuario de la interfaz está vacía, usamos el Cotizador base de la columna A como respaldo
        if cliente == "":
            cliente = str(fila[17]).strip() if pd.notna(fila[17]) else cotizador_base

        # Tiempos base desde las columnas B, C y D (Índices 1, 2, 3) para alimentar la cuenta regresiva real
        try:
            h = int(float(fila[1])) if pd.notna(fila[1]) else 0
            m = int(float(fila[2])) if pd.notna(fila[2]) else 0
            s = int(float(fila[3])) if pd.notna(fila[3]) else 0
        except:
            h, m, s = 0, 0, 0
            
        # Columna T (índice 19): Tu texto limpio de tiempo (ej: "26m 46s")
        tiempo_excel = str(fila[19]).strip() if pd.notna(fila[19]) else f"{h}h {m}m {s}s"
        
        # Columna U (índice 20): Tu menú desplegable de ESTADO
        estado = str(fila[20]).strip().upper() if pd.notna(fila[20]) else "EN ESPERA"
        
        # Cálculo matemático del tiempo total en segundos
        segundos_totales = (h * 3600) + (m * 60) + s
        
        # 3. Motor del Reloj Dinámico en base al Estado
        if "LISTO" in estado or "FINALIZADO" in estado:
            tiempo_mostrar = "✅ ¡Listo para recoger!"
        elif "IMPRIMIENDO" in estado or "IMPR..." in estado:
            # Descuento en vivo interactivo restando el segundero del servidor
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
            # Estado "En espera" o celdas vacías
            tiempo_mostrar = f"💤 En cola ({tiempo_excel})"
            
        lista_final.append({
            "CLIENTE": cliente,
            "ESTADO DE TU PIEZA": tiempo_mostrar
        })
        
    df_publico = pd.DataFrame(lista_final)

    # Motor de búsqueda interactiva
    buscador = st.text_input("", placeholder="🔍 Escribe tu nombre para buscar tu orden...").strip().upper()
    if buscador:
        df_publico = df_publico[df_publico["CLIENTE"].str.upper().str.contains(buscador)]
        
    # 4. Pintar la tabla limpia en la pantalla del usuario
    st.dataframe(
        df_publico, 
        use_container_width=True,
        hide_index=True
    )
    
    # Ciclo infinito de refresco en tiempo real (1 segundo) para mover los relojes
    time.sleep(1)
    st.rerun()

except Exception as e:
    st.info("🔄 Sincronizando datos con la cola de producción H2D...")