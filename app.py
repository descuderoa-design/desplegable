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
# 2. CARGA
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
    st.stop()

df_muni = df_mon[df_mon["municipio"] == municipio_sel]

# =========================================================
# 5. MONUMENTO
# =========================================================

monumentos = sorted(df_muni["monumento"].dropna().unique())

monumento_sel = st.selectbox("Selecciona monumento", [""] + monumentos)

if monumento_sel == "":
    st.stop()

# =========================================================
# 6. FECHA
# =========================================================

fecha_dt = pd.Timestamp(
    st.date_input(
        "Fecha de visita",
        value=date.today(),
        min_value=date.today(),
        max_value=date(date.today().year + 2, date.today().month, date.today().day),
        format="DD/MM/YYYY"
    )
)

fecha_txt = fecha_dt.strftime("%d/%m/%Y")

# =========================================================
# 7. DÍA DE LA SEMANA
# =========================================================

dias_es = {
    "Monday": "lunes",
    "Tuesday": "martes",
    "Wednesday": "miércoles",
    "Thursday": "jueves",
    "Friday": "viernes",
    "Saturday": "sábado",
    "Sunday": "domingo"
}

dia_semana = dias_es[fecha_dt.day_name()]

# =========================================================
# 8. CONTENIDO
# =========================================================

df_info = df_cont[df_cont["monumento"] == monumento_sel].copy()

# =========================================================
# 9. FECHAS (TEMPORADAS)
# =========================================================

if "fecha_inicio" in df_info.columns and "fecha_fin" in df_info.columns:

    df_info["fecha_inicio"] = pd.to_datetime(
        df_info["fecha_inicio"], dayfirst=True, errors="coerce"
    )

    df_info["fecha_fin"] = pd.to_datetime(
        df_info["fecha_fin"], dayfirst=True, errors="coerce"
    )

def cumple_fecha(row):

    inicio = row.get("fecha_inicio")
    fin = row.get("fecha_fin")

    if pd.isna(inicio) and pd.isna(fin):
        return True

    if pd.isna(inicio) and pd.notna(fin):
        return fecha_dt <= fin

    if pd.notna(inicio) and pd.isna(fin):
        return fecha_dt >= inicio

    return inicio <= fecha_dt <= fin

df_info = df_info[df_info.apply(cumple_fecha, axis=1)]

# =========================================================
# 10. FILTRO DÍAS DE LA SEMANA
# =========================================================

def cumple_dia(row):

    if "dias_semana" not in row or pd.isna(row["dias_semana"]):
        return True

    dias = [d.strip().lower() for d in str(row["dias_semana"]).split("-")]

    return dia_semana in dias


df_info = df_info[df_info.apply(cumple_dia, axis=1)]

# =========================================================
# 11. OUTPUT
# =========================================================

st.markdown("---")
st.markdown(f"# {monumento_sel}")

st.markdown(f"📅 Fecha: **{fecha_txt}**")
st.markdown(f"📆 Día de la semana: **{dia_semana}**")

st.markdown("## 🟢 Información aplicable")

if df_info.empty:
    st.warning("No hay información aplicable para esta fecha")
else:
    for bloque in df_info["bloque"].dropna().unique():

        st.markdown(f"### {bloque.capitalize()}")

        sub = df_info[df_info["bloque"] == bloque]

        for _, row in sub.iterrows():
            st.write(f"**{row['subtipo']}**: {row['contenido']}")
