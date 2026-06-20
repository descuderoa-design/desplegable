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
# 6. FECHA DE VISITA
# =========================================================

fecha_visita = st.date_input("Fecha de visita", value=date.today())
fecha_visita_txt = fecha_visita.strftime("%d/%m/%Y")
fecha_visita_dt = pd.to_datetime(fecha_visita)

# =========================================================
# 7. CONTENIDO
# =========================================================

df_info = df_cont[df_cont["monumento"] == monumento_sel].copy()

# =========================================================
# 8. TEMPORADAS SIN AÑO (MMDD)
# =========================================================

def to_mmdd(dt):
    return int(dt.strftime("%m%d"))

hoy = to_mmdd(fecha_visita_dt)

if "fecha_inicio" in df_info.columns and "fecha_fin" in df_info.columns:

    df_info["fecha_inicio_dt"] = pd.to_datetime(df_info["fecha_inicio"], dayfirst=True, errors="coerce")
    df_info["fecha_fin_dt"] = pd.to_datetime(df_info["fecha_fin"], dayfirst=True, errors="coerce")

    df_info["inicio_mmdd"] = df_info["fecha_inicio_dt"].dt.strftime("%m%d")
    df_info["fin_mmdd"] = df_info["fecha_fin_dt"].dt.strftime("%m%d")

    def es_aplicable(row):
        if pd.isna(row["inicio_mmdd"]) and pd.isna(row["fin_mmdd"]):
            return True

        inicio = int(row["inicio_mmdd"]) if pd.notna(row["inicio_mmdd"]) else None
        fin = int(row["fin_mmdd"]) if pd.notna(row["fin_mmdd"]) else None

        # caso normal (no cruza año)
        if inicio is not None and fin is not None and inicio <= fin:
            return inicio <= hoy <= fin

        # caso temporada cruzando año (ej: invierno 11-03)
        if inicio is not None and fin is not None:
            return hoy >= inicio or hoy <= fin

        return True

    df_info["aplicable"] = df_info.apply(es_aplicable, axis=1)

else:
    df_info["aplicable"] = True

# =========================================================
# 9. SPLIT RESULTADOS
# =========================================================

df_ok = df_info[df_info["aplicable"] == True]
df_no = df_info[df_info["aplicable"] == False]

# =========================================================
# 10. OUTPUT
# =========================================================

st.markdown("---")
st.markdown(f"# {monumento_sel}")
st.markdown(f"📅 Fecha de visita: **{fecha_visita_txt}**")

# -----------------------------
# APLICABLES
# -----------------------------

st.markdown("## 🟢 Condiciones aplicables")

if df_ok.empty:
    st.warning("No hay condiciones aplicables")
else:
    for bloque in df_ok["bloque"].dropna().unique():

        st.markdown(f"### {bloque.capitalize()}")

        sub = df_ok[df_ok["bloque"] == bloque]

        for _, row in sub.iterrows():
            st.write(f"**{row['subtipo']}**: {row['contenido']}")

# -----------------------------
# NO APLICABLES
# -----------------------------

st.markdown("---")
st.markdown("## 🔴 Condiciones no aplicables")

if df_no.empty:
    st.info("No hay condiciones fuera de temporada")
else:
    for bloque in df_no["bloque"].dropna().unique():

        st.markdown(f"### {bloque.capitalize()}")

        sub = df_no[df_no["bloque"] == bloque]

        for _, row in sub.iterrows():
            st.write(f"**{row['subtipo']}**: {row['contenido']}")
