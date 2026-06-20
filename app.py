import streamlit as st
import pandas as pd

st.set_page_config(page_title="CMS Monumentos Cantabria", layout="wide")

st.title("Sistema de consulta de monumentos")

# =========================================================
# 1. GOOGLE SHEETS (TU ID YA INTEGRADO)
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

    df_mon.columns = df_mon.columns.str.strip()
    df_cont.columns = df_cont.columns.str.strip()

    return df_mon, df_cont


df_mon, df_cont = load_data()


# =========================================================
# 3. FILTRO: MUNICIPIO
# =========================================================

if "municipio" not in df_mon.columns:
    st.error("Falta columna 'municipio' en hoja monumentos")
    st.stop()

municipios = sorted(df_mon["municipio"].dropna().unique())
municipio_sel = st.selectbox("Municipio", municipios)

df_muni = df_mon[df_mon["municipio"] == municipio_sel]


# =========================================================
# 4. FILTRO: MONUMENTO
# =========================================================

monumentos = sorted(df_muni["monumento"].dropna().unique())

if len(monumentos) == 0:
    st.warning("No hay monumentos en este municipio")
    st.stop()

monumento_sel = st.selectbox("Monumento", monumentos)


# =========================================================
# 5. FILTRAR CONTENIDO CMS
# =========================================================

df_info = df_cont[df_cont["monumento"] == monumento_sel]


# =========================================================
# 6. CABECERA FICHA
# =========================================================

st.markdown("---")
st.markdown(f"# {monumento_sel}")


# =========================================================
# 7. RENDER CMS (BLOQUES)
# =========================================================

if df_info.empty:
    st.warning("No hay contenidos para este monumento")
else:
    bloques = df_info["bloque"].dropna().unique()

    for bloque in bloques:
        st.markdown(f"## {bloque.upper()}")

        sub = df_info[df_info["bloque"] == bloque]

        for _, row in sub.iterrows():
            st.write(f"**{row['subtipo']}**: {row['contenido']}")


# =========================================================
# 8. DEBUG (OPCIONAL)
# =========================================================

with st.expander("Datos técnicos"):
    st.write("Monumentos filtrados")
    st.dataframe(df_muni)

    st.write("Contenido filtrado")
    st.dataframe(df_info)
