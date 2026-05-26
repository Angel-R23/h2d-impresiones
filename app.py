import streamlit as st
import pandas as pd
import time

# 1. Configuración visual estilo Dark Mode Profesional (GitHub Theme)
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

# 2. CONEXIÓN DEFINITIVA: Usando el ID y GID exactos de tu link proporcionado
ID_DOCUMENTO = "1NakggbHZbtXNiueW316bHAo8wpDkQdS_"
GOOGLE_SHEETS_URL = f"https://docs.google.com/spreadsheets/d/{ID_DOCUMENTO}/export?format=csv&gid=907422749"

def cargar_datos_frescos():
    return pd.read_csv(GOOGLE_SHEETS_URL, header=None, encoding='utf-8')

try:
    df_completo = cargar_datos_frescos()
    
    # Mapeo desde la fila 9 en adelante (índice 8 en Python)
    df_datos = df_completo.iloc[8:].copy()
    
    lista_final = []
    
    for idx, fila in df_datos.iterrows():
        # Columna A (índice 0): Cotizador base original para validar la fila
        cotizador_base = str(fila[0]).strip() if pd.notna(fila[0]) else ""
        
        # Filtro para limpiar filas vacías o con ceros de relleno
        if not cotizador_base or cotizador_base in ["0", "0.0", "COTIZADOR"]:
            continue
            
        # Minitabla de Interfaz en ese documento:
        # Columna S (índice 18): Nombre del Usuario en la interfaz
        cliente = str(fila[18]).strip() if pd.notna(fila[18]) else ""
        if cliente == "":
            # Respaldo en Columna R (índice 17) o Cotizador base si está vacío
            cliente = str(fila[17]).strip() if pd.notna(fila[17]) else cotizador_base

        # Tiempos base desde las columnas B, C y D (Índices 1, 2, 3) para la cuenta regresiva en vivo
        try:
            h = int(float(fila[1])) if pd.notna(fila[1]) else 0
            m = int(float(fila[2])) if pd.notna(fila[2]) else 0
            s = int(float(fila[3])) if pd.notna(fila[3]) else 0
        except:
            h, m, s = 0, 0, 0
            
        # Columna T (índice 19): Tu texto limpio de tiempo estructurado (ej: "26m 46s")
        tiempo_excel = str(fila[19]).strip() if pd.notna(fila[19]) else f"{h}h {m}m {s}s"
        
        # Columna U (índice 20): Menú desplegable de ESTADO de este archivo
        estado = str(fila[20]).strip().upper() if pd.notna(fila[20]) else "EN ESPERA"
        
        # Segundos totales de la pieza
        segundos_totales = (h * 3600) + (