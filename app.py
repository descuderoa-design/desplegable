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
# 2. CARGA DE DATOS (SIN CACHE)
# =========================================================

def load_data():
    df_mon = pd.read_csv(URL_MONUMENTOS)
    df_cont = pd.read_csv(URL_CONTENIDOS)

    df_mon.columns = df_mon.columns.str.strip().str.lower()
    df_cont.columns = df_cont.columns.str.strip().str.lower()

    return df_mon, df_cont


df_mon, df_cont = load_data()

# =========================================================
# 3. VALIDACIÓN
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
# 4. MUNICIPIO
# =========================================================

municipios = sorted(df_mon["municipio"].dropna().unique())

municipio_sel = st.selectbox("Selecciona municipio", [""] + municipios)

if municipio_sel == "":
    st.info("Selecciona un municipio para comenzar")
    st.stop()

df_muni = df_mon[df_mon["municipio"] == municipio_sel]

# =========================================================
# 5. MONUMENTO
# =========================================================

monumentos = sorted(df_muni["monumento"].dropna().unique())

monumento_sel = st.selectbox("Selecciona monumento", [""] + monumentos)

if monumento_sel == "":
    st.info("Selecciona un monumento")
    st.stop()

# =========================================================
# 6. FECHA
# =========================================================

fecha_visita = st.date_input("Fecha de visita", value=date.today())
fecha_visita_txt = fecha_visita.strftime("%d/%m/%Y")
fecha_visita_dt = pd.to_datetime(fecha_visita)

# =========================================================
# 7. CONTENIDO
# =========================================================

df_info = df_cont[df_cont["monumento"] == monumento_sel].copy()

# =========================================================
# 8. REGLAS POR FECHA (SI EXISTEN)
# =========================================================

if "fecha_inicio" in df_info.columns and "fecha_fin" in df_info.columns:

    df_info["fecha_inicio"] = pd.to_datetime(df_info["fecha_inicio"], dayfirst=True, errors="coerce")
    df_info["fecha_fin"] = pd.to_datetime(df_info["fecha_fin"], dayfirst=True, errors="coerce")

    def es_aplicable(row):
        inicio = row.get("fecha_inicio")
        fin = row.get("fecha_fin")

        if pd.isna(inicio) and pd.isna(fin):
            return True
        if pd.isna(inicio):
            return fecha_visita_dt <= fin
        if pd.isna(fin):
            return fecha_visita_dt >= inicio
        return inicio <= fecha_visita_dt <= fin

    df_info["aplicable"] = df_info.apply(es_aplicable, axis=1)
else:
    df_info["aplicable"] = True

df_ok = df_info[df_info["aplicable"] == True]
df_no = df_info[df_info["aplicable"] == False]

# =========================================================
# 9. SALIDA
# =========================================================

st.markdown("---")
st.markdown(f"# {monumento_sel}")
st.markdown(f"📅 Fecha de visita: **{fecha_visita_txt}**")

st.markdown("## 🟢 Condiciones aplicables")

if df_ok.empty:
    st.warning("No hay condiciones aplicables")
else:
    for bloque in df_ok["bloque"].dropna().unique():
        st.markdown(f"### {bloque.capitalize()}")
        sub = df_ok[df_ok["bloque"] == bloque]

        for _, row in sub.iterrows():
            st.write(f"**{row['subtipo']}**: {row['contenido']}")

st.markdown("---")
st.markdown("## 🔴 Condiciones no aplicables")

if df_no.empty:
    st.info("No hay condiciones fuera de esta fecha")
else:
    for bloque in df_no["bloque"].dropna().unique():
        st.markdown(f"### {bloque.capitalize()}")
        sub = df_no[df_no["bloque"] == bloque]

        for _, row in sub.iterrows():
            st.write(f"**{row['subtipo']}**: {row['contenido']}")
