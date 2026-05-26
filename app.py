import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# 1. Configuración visual estilo GitHub Dark Mode
st.set_page_config(
    page_title="H2D 3D Printing Status",
    page_icon="🖨️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos visuales para que la interfaz se vea pro e ingenieril
st.markdown("""
    <style>
        .stApp { background-color: #0d1117; color: #c9d1d9; }
        h1 { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-weight: 600; color: #f0f6fc; }
        .stCaption { color: #8b949e !important; }
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

st.title("📋 Cola de Impresiones - H2D")
st.caption("Control de tiempos de impresión 3D en tiempo real desde Google Sheets.")

# 2. Enlace de exportación de tu Google Sheets (ID de tu captura)
ID_DOCUMENTO = "1G9JXP3i_c40sSZpdJdMT6rCJTCq5ESDwAgBuS05YOb8"
GOOGLE_SHEETS_URL = f"https://docs.google.com/spreadsheets/d/{ID_DOCUMENTO}/export?format=xlsx"

@st.cache_data(ttl=5)  # Sincroniza y actualiza la data cada 5 segundos de forma automática
def cargar_datos():
    response = requests.get(GOOGLE_SHEETS_URL)
    return pd.read_excel(BytesIO(response.content), sheet_name=0, header=None)

try:
    df_crudo = cargar_datos()
    
    # 3. Escaneo dinámico para encontrar la fila de cabeceras (Fila 8 "COTIZADOR")
    fila_cabecera = None
    for idx, valor in enumerate(df_crudo[0]):
        if str(valor).strip().upper() == "COTIZADOR":
            fila_cabecera = idx
            break

    if fila_cabecera is not None:
        # Cortamos el DataFrame para tomar solo las filas de datos reales hacia abajo
        df_datos = df_crudo.iloc[fila_cabecera + 1:].copy()
        
        # Extraemos las columnas por su posición en tu Sheets:
        # Columna A (Posición 0) -> COTIZADOR (Nombres)
        # Columna B (Posición 1) -> HORAS
        # Columna C (Posición 2) -> MINS
        nombres = df_datos[0].fillna("").astype(str).str.strip()
        horas = pd.to_numeric(df_datos[1], errors='coerce').fillna(0).astype(int)
        minutos = pd.to_numeric(df_datos[2], errors='coerce').fillna(0).astype(int)
        
        # 4. Formatear el tiempo restante fila por fila de forma limpia
        tiempos_formateados = []
        for h, m in zip(horas, minutos):
            if h > 0:
                tiempos_formateados.append(f"⏳ {h}h {m}m restante")
            elif m > 0:
                tiempos_formateados.append(f"⏳ {m}m restante")
            else:
                tiempos_formateados.append("✅ Finalizado / Listo")

        # Construimos la estructura final de dos columnas que tú quieres mostrar
        df_final = pd.DataFrame({
            "NOMBRE / COTIZADOR": nombres,
            "TIEMPO RESTANTE": tiempos_formateados
        })
        
        # Filtramos celdas vacías y ceros de relleno que mete el Excel por defecto
        df_final = df_final[df_final["NOMBRE / COTIZADOR"] != ""]
        df_final = df_final[df_final["NOMBRE / COTIZADOR"] != "0"]
        df_final = df_final[df_final["NOMBRE / COTIZADOR"] != "0.0"]
        df_final = df_final[~df_final["NOMBRE / COTIZADOR"].str.upper().isin(["FALSE", "FALSO", "TRUE", "VERDADERO"])]
        
        # 5. Buscador en tiempo real
        buscador = st.text_input("", placeholder="🔍 Escribe tu nombre para ver cuánto le falta a tu pieza...").strip().upper()
        
        if buscador:
            df_final = df_final[df_final["NOMBRE / COTIZADOR"].str.upper().str.contains(buscador)]
            
        # 6. Desplegar la tabla limpia en la web
        st.dataframe(
            df_final, 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Estructurando la interfaz... Esperando datos bajo la cabecera 'COTIZADOR'.")

except Exception as e:
    st.error("🔄 Conectando con la base de datos de Google Sheets... Si el mensaje persiste, verifica que el archivo esté compartido como 'Cualquier persona con el enlace'.")