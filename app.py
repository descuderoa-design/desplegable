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
# 2. LOAD DATA
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
# 3. SELECCIÓN
# =========================================================

municipios = sorted(df_mon["municipio"].dropna().unique())
municipio_sel = st.selectbox("Municipio", [""] + municipios)

if municipio_sel == "":
    st.stop()

df_muni = df_mon[df_mon["municipio"] == municipio_sel]

monumentos = sorted(df_muni["monumento"].dropna().unique())
monumento_sel = st.selectbox("Monumento", [""] + monumentos)

if monumento_sel == "":
    st.stop()

# =========================================================
# 4. FECHA
# =========================================================

fecha_visita = st.date_input("Fecha de visita", value=date.today())
fecha_visita = pd.to_datetime(fecha_visita)

# =========================================================
# 5. FILTRO BASE
# =========================================================

df_info = df_cont[df_cont["monumento"] == monumento_sel].copy()

# =========================================================
# 6. FECHAS A DATETIME
# =========================================================

if "fecha_inicio" in df_info.columns and "fecha_fin" in df_info.columns:

    df_info["fecha_inicio"] = pd.to_datetime(df_info["fecha_inicio"], errors="coerce")
    df_info["fecha_fin"] = pd.to_datetime(df_info["fecha_fin"], errors="coerce")

# =========================================================
# 7. DIVISIÓN APLICABLE / NO APLICABLE
# =========================================================

def es_aplicable(row):
    inicio = row.get("fecha_inicio")
    fin = row.get("fecha_fin")

    if pd.isna(inicio) and pd.isna(fin):
        return True

    if pd.isna(inicio):
        return fecha_visita <= fin

    if pd.isna(fin):
        return fecha_visita >= inicio

    return inicio <= fecha_visita <= fin


df_info["aplicable"] = df_info.apply(es_aplicable, axis=1)

df_ok = df_info[df_info["aplicable"] == True]
df_no = df_info[df_info["aplicable"] == False]

# =========================================================
# 8. CABECERA
# =========================================================

st.markdown("---")
st.markdown(f"# {monumento_sel}")
st.markdown(f"📅 Fecha: {fecha_visita.date()}")

# =========================================================
# 9. APLICABLES
# =========================================================

st.markdown("## 🟢 Condiciones aplicables")

if df_ok.empty:
    st.warning("No hay condiciones aplicables")
else:
    for bloque in df_ok["bloque"].dropna().unique():

        st.markdown(f"### {bloque.capitalize()}")

        sub = df_ok[df_ok["bloque"] == bloque]

        for _, row in sub.iterrows():
            st.write(f"**{row['subtipo']}**: {row['contenido']}")

# =========================================================
# 10. NO APLICABLES
# =========================================================

st.markdown("---")
st.markdown("## 🔴 Condiciones no aplicables")

if df_no.empty:
    st.info("No hay condiciones fuera de la fecha seleccionada")
else:
    for bloque in df_no["bloque"].dropna().unique():

        st.markdown(f"### {bloque.capitalize()}")

        sub = df_no[df_no["bloque"] == bloque]

        for _, row in sub.iterrows():
            st.write(f"**{row['subtipo']}**: {row['contenido']}")

            if "fecha_inicio" in row and "fecha_fin" in row:
                st.caption(f"Vigencia: {row['fecha_inicio']} → {row['fecha_fin']}")
