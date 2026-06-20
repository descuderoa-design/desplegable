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

    df_mon.columns = df_mon.columns.str.strip().str.lower()
    df_cont.columns = df_cont.columns.str.strip().str.lower()

    return df_mon, df_cont


df_mon, df_cont = load_data()

# =========================================================
# 3. VALIDACIONES BÁSICAS
# =========================================================

required_mon_cols = {"monumento", "municipio"}
required_cont_cols = {"monumento", "bloque", "subtipo", "contenido"}

if not required_mon_cols.issubset(df_mon.columns):
    st.error("Error: faltan columnas en 'monumentos'")
    st.stop()

if not required_cont_cols.issubset(df_cont.columns):
    st.error("Error: faltan columnas en 'contenidos'")
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

# =========================================================
# 8. DEBUG OPCIONAL
# =========================================================

with st.expander("Datos técnicos"):
    st.write("Monumentos filtrados")
    st.dataframe(df_muni)

    st.write("Contenido filtrado")
    st.dataframe(df_info)
