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
# 3. VALIDACIÓN BÁSICA
# =========================================================

required_mon = {"monumento", "municipio"}
required_cont = {"monumento", "bloque", "subtipo", "contenido"}

if not required_mon.issubset(df_mon.columns):
    st.error(f"Error columnas monumentos: {df_mon.columns}")
    st.stop()

if not required_cont.issubset(df_cont.columns):
    st.error(f"Error columnas contenidos: {df_cont.columns}")
    st.stop()

# =========================================================
# 4. FILTRO MUNICIPIO
# =========================================================

municipios = sorted(df_mon["municipio"].dropna().unique())

municipio_sel = st.selectbox(
    "Selecciona municipio",
    [""] + municipios
)

if municipio_sel == "":
    st.info("Selecciona un municipio para continuar")
    st.stop()

df_muni = df_mon[df_mon["municipio"] == municipio_sel]

# =========================================================
# 5. FILTRO MONUMENTO
# =========================================================

monumentos = sorted(df_muni["monumento"].dropna().unique())

monumento_sel = st.selectbox(
    "Selecciona monumento",
    [""] + monumentos
)

if monumento_sel == "":
    st.info("Selecciona un monumento")
    st.stop()

# =========================================================
# 6. FECHA DE VISITA (VARIABLE DE REGLA)
# =========================================================

fecha_visita = st.date_input("Selecciona fecha de visita", value=date.today())

fecha_visita = pd.to_datetime(fecha_visita)

# =========================================================
# 7. FILTRADO DE CONTENIDO
# =========================================================

df_info = df_cont[df_cont["monumento"] == monumento_sel].copy()

# =========================================================
# 8. MOTOR DE REGLAS POR FECHA (SI EXISTE)
# =========================================================

if "fecha_inicio" in df_info.columns and "fecha_fin" in df_info.columns:

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
st.markdown(f"📅 Fecha seleccionada: **{fecha_visita.date()}**")

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

            if "fuente" in row and pd.notna(row["fuente"]):
                st.caption(f"Fuente: {row['fuente']}")

# =========================================================
# 11. DEBUG (OCULTO EN EXPANDER)
# =========================================================

with st.expander("Datos técnicos"):
    st.write("Monumentos")
    st.dataframe(df_muni)

    st.write("Contenido filtrado por fecha")
    st.dataframe(df_info)
