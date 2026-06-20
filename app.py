import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="CMS Monumentos Cantabria", layout="wide")

st.title("Sistema de consulta de monumentos")

# =========================================================
# 1. GOOGLE SHEETS
# =========================================================

SHEET_ID = "1ye3fiEJ35h_XRlzEZyZWm3UVTqjWjaxwREgnQsIMYCA"

URL_MONUMENTOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=monumentos"
URL_CONTENIDOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=contenidos"

# =========================================================
# 2. CARGA DE DATOS
# =========================================================

@st.cache_data
def load_data():
    df_mon = pd.read_csv(URL_MONUMENTOS)
    df_cont = pd.read_csv(URL_CONTENIDOS)

    df_mon.columns = df_mon.columns.str.strip().str.lower()
    df_cont.columns = df_cont.columns.str.strip().str.lower()

    return df_mon, df_cont


df_mon, df_cont = load_data()

# =========================================================
# 3. VALIDACIÓN MÍNIMA
# =========================================================

required_mon = {"monumento", "municipio"}
required_cont = {"monumento", "bloque", "subtipo", "contenido", "fecha_inicio", "fecha_fin"}

missing_mon = required_mon - set(df_mon.columns)
missing_cont = required_cont - set(df_cont.columns)

if missing_mon:
    st.error(f"Faltan columnas en monumentos: {missing_mon}")
    st.stop()

if missing_cont:
    st.error(f"Faltan columnas en contenidos: {missing_cont}")
    st.stop()

# =========================================================
# 4. SELECCIÓN MUNICIPIO
# =========================================================

municipios = sorted(df_mon["municipio"].dropna().unique())

municipio_sel = st.selectbox("Selecciona municipio", [""] + municipios)

if municipio_sel == "":
    st.info("Selecciona un municipio para comenzar")
    st.stop()

df_muni = df_mon[df_mon["municipio"] == municipio_sel]

# =========================================================
# 5. SELECCIÓN MONUMENTO
# =========================================================

monumentos = sorted(df_muni["monumento"].dropna().unique())

monumento_sel = st.selectbox("Selecciona monumento", [""] + monumentos)

if monumento_sel == "":
    st.info("Selecciona un monumento")
    st.stop()

# =========================================================
# 6. FECHA DE VISITA (VARIABLE DE REGLA)
# =========================================================

fecha_visita = st.date_input("Selecciona fecha de visita", value=date.today())
fecha_visita = pd.to_datetime(fecha_visita)

# =========================================================
# 7. FILTRAR CONTENIDO POR MONUMENTO
# =========================================================

df_info = df_cont[df_cont["monumento"] == monumento_sel].copy()

# =========================================================
# 8. MOTOR DE REGLAS POR FECHA
# =========================================================

df_info["fecha_inicio"] = pd.to_datetime(df_info["fecha_inicio"], errors="coerce")
df_info["fecha_fin"] = pd.to_datetime(df_info["fecha_fin"], errors="coerce")

df_info = df_info[
    (df_info["fecha_inicio"].isna() | (df_info["fecha_inicio"] <= fecha_visita)) &
    (df_info["fecha_fin"].isna() | (df_info["fecha_fin"] >= fecha_visita))
]

# =========================================================
# 9. FICHA FINAL
# =========================================================

st.markdown("---")
st.markdown(f"# {monumento_sel}")
st.markdown(f"📅 Fecha de visita: **{fecha_visita.date()}**")

# =========================================================
# 10. RENDER LIMPIO POR BLOQUES
# =========================================================

if df_info.empty:
    st.warning("No hay información disponible para esta fecha")
else:
    for bloque in df_info["bloque"].dropna().unique():

        st.markdown(f"## {bloque.capitalize()}")

        sub = df_info[df_info["bloque"] == bloque]

        for _, row in sub.iterrows():

            st.markdown(f"""
            **{row['subtipo']}**  
            {row['contenido']}
            """)

# =========================================================
# 11. DEBUG OPCIONAL
# =========================================================

with st.expander("Datos filtrados (debug)"):
    st.dataframe(df_info)
