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

def normalize_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df


@st.cache_data
def load_data():
    df_mon = pd.read_csv(URL_MONUMENTOS)
    df_cont = pd.read_csv(URL_CONTENIDOS)

    df_mon = normalize_columns(df_mon)
    df_cont = normalize_columns(df_cont)

    return df_mon, df_cont


df_mon, df_cont = load_data()

# =========================================================
# 3. DEBUG (OPCIONAL PERO ÚTIL)
# =========================================================

with st.expander("Ver columnas detectadas"):
    st.write("Monumentos:", list(df_mon.columns))
    st.write("Contenidos:", list(df_cont.columns))

# =========================================================
# 4. VALIDACIÓN FLEXIBLE
# =========================================================

required_mon = {"monumento", "municipio"}
required_cont = {"monumento", "bloque", "subtipo", "contenido"}

missing_mon = required_mon - set(df_mon.columns)
missing_cont = required_cont - set(df_cont.columns)

if missing_mon:
    st.error(f"Faltan columnas en 'monumentos': {missing_mon}")
    st.stop()

if missing_cont:
    st.error(f"Faltan columnas en 'contenidos': {missing_cont}")
    st.stop()

# =========================================================
# 5. FILTRO MUNICIPIO
# =========================================================

municipios = sorted(df_mon["municipio"].dropna().unique())
municipio_sel = st.selectbox("Municipio", municipios)

df_muni = df_mon[df_mon["municipio"] == municipio_sel]

# =========================================================
# 6. FILTRO MONUMENTO
# =========================================================

monumentos = sorted(df_muni["monumento"].dropna().unique())

if len(monumentos) == 0:
    st.warning("No hay monumentos en este municipio")
    st.stop()

monumento_sel = st.selectbox("Monumento", monumentos)

# =========================================================
# 7. CONTENIDO CMS
# =========================================================

df_info = df_cont[df_cont["monumento"] == monumento_sel]

st.markdown("---")
st.markdown(f"# {monumento_sel}")

# =========================================================
# 8. RENDER CMS
# =========================================================

if df_info.empty:
    st.warning("No hay información disponible para este monumento")
else:
    for bloque in df_info["bloque"].dropna().unique():
        st.markdown(f"## {bloque.upper()}")

        sub = df_info[df_info["bloque"] == bloque]

        for _, row in sub.iterrows():
            st.write(f"**{row['subtipo']}**: {row['contenido']}")

# =========================================================
# 9. DEBUG DATOS
# =========================================================

with st.expander("Datos filtrados"):
    st.write("Monumentos")
    st.dataframe(df_muni)

    st.write("Contenido")
    st.dataframe(df_info)
