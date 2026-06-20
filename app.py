import streamlit as st
import pandas as pd

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

    # limpieza ligera (sin romper nombres reales)
    df_mon.columns = df_mon.columns.str.strip()
    df_cont.columns = df_cont.columns.str.strip()

    return df_mon, df_cont


df_mon, df_cont = load_data()

# =========================================================
# 3. VALIDACIÓN BÁSICA
# =========================================================

required_mon = {"monumento", "municipio", "tipo", "activo", "prioridad"}
required_cont = {"monumento", "bloque", "subtipo", "contenido", "fuente", "actualizado"}

if not required_mon.issubset(set(df_mon.columns)):
    st.error(f"Error en 'monumentos'. Columnas detectadas: {list(df_mon.columns)}")
    st.stop()

if not required_cont.issubset(set(df_cont.columns)):
    st.error(f"Error en 'contenidos'. Columnas detectadas: {list(df_cont.columns)}")
    st.stop()

# =========================================================
# 4. FILTRO MUNICIPIO
# =========================================================

municipios = sorted(df_mon["municipio"].dropna().unique())
municipio_sel = st.selectbox("Municipio", municipios)

df_muni = df_mon[df_mon["municipio"] == municipio_sel]

# =========================================================
# 5. FILTRO MONUMENTO
# =========================================================

monumentos = sorted(df_muni["monumento"].dropna().unique())

if len(monumentos) == 0:
    st.warning("No hay monumentos en este municipio")
    st.stop()

monumento_sel = st.selectbox("Monumento", monumentos)

# =========================================================
# 6. CONTENIDO CMS
# =========================================================

df_info = df_cont[df_cont["monumento"] == monumento_sel]

st.markdown("---")
st.markdown(f"# {monumento_sel}")

# =========================================================
# 7. RENDER CMS
# =========================================================

if df_info.empty:
    st.warning("No hay información disponible")
else:
    for bloque in df_info["bloque"].dropna().unique():

        st.markdown(f"## {bloque.upper()}")

        sub = df_info[df_info["bloque"] == bloque]

        for _, row in sub.iterrows():
            st.write(f"**{row['subtipo']}**: {row['contenido']}")

            # info extra opcional (solo si existe)
            if "fuente" in row and pd.notna(row["fuente"]):
                st.caption(f"Fuente: {row['fuente']}")

            if "actualizado" in row and pd.notna(row["actualizado"]):
                st.caption(f"Actualizado: {row['actualizado']}")

# =========================================================
# 8. DEBUG
# =========================================================

with st.expander("Datos técnicos"):
    st.write("Monumentos filtrados")
    st.dataframe(df_muni)

    st.write("Contenido filtrado")
    st.dataframe(df_info)
