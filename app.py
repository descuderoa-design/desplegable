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
# 4. SELECTOR MUNICIPIO (NO MUESTRA NADA SIN SELECCIÓN)
# =========================================================

municipios = sorted(df_mon["municipio"].dropna().unique())

municipio_sel = st.selectbox(
    "Selecciona municipio",
    [""] + municipios
)

if municipio_sel == "":
    st.info("Selecciona un municipio para comenzar")
    st.stop()

df_muni = df_mon[df_mon["municipio"] == municipio_sel]

# =========================================================
# 5. SELECTOR MONUMENTO
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
# 6. FILTRAR CONTENIDO
# =========================================================

df_info = df_cont[df_cont["monumento"] == monumento_sel]

# =========================================================
# 7. FICHA LIMPIA
# =========================================================

st.markdown("---")
st.markdown(f"# {monumento_sel}")

# =========================================================
# 8. RENDER CMS LIMPIO
# =========================================================

if df_info.empty:
    st.warning("No hay información disponible para este monumento")
else:
    bloques = df_info["bloque"].dropna().unique()

    for bloque in bloques:

        st.markdown(f"## {bloque.capitalize()}")

        sub = df_info[df_info["bloque"] == bloque]

        for _, row in sub.iterrows():

            st.markdown(
                f"""
                **{row['subtipo']}**  
                {row['contenido']}
                """
            )

# =========================================================
# 9. INFO OPCIONAL (OCULTA EN EXPANDER)
# =========================================================

with st.expander("Información técnica"):
    st.write("Monumentos filtrados")
    st.dataframe(df_muni)

    st.write("Contenido filtrado")
    st.dataframe(df_info)
