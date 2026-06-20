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
# 6. MOTOR DE REGLAS
# =========================================================

if "fecha_inicio" in df_info.columns and "fecha_fin" in df_info.columns:

    df_info["fecha_inicio"] = pd.to_datetime(df_info["fecha_inicio"], errors="coerce")
    df_info["fecha_fin"] = pd.to_datetime(df_info["fecha_fin"], errors="coerce")

    df_info = df_info[
        (df_info["fecha_inicio"].isna() | (df_info["fecha_inicio"] <= fecha_visita)) &
        (df_info["fecha_fin"].isna() | (df_info["fecha_fin"] >= fecha_visita))
    ]

# =========================================================
# 7. OUTPUT ESTRUCTURADO (CLAVE)
# =========================================================

st.markdown("---")
st.markdown(f"# {monumento_sel}")
st.markdown(f"📅 Fecha: {fecha_visita.date()}")

# =========================================================
# 8. TARIFAS Y HORARIOS SEPARADOS
# =========================================================

horarios = df_info[df_info["bloque"].str.lower() == "horarios"]
tarifas = df_info[df_info["bloque"].str.lower() == "tarifas"]

# =========================================================
# 9. MOSTRAR HORARIOS
# =========================================================

st.markdown("## 🕒 Horarios aplicables")

if horarios.empty:
    st.warning("No hay horarios para esta fecha")
else:
    for _, row in horarios.iterrows():
        st.write(f"**{row['subtipo']}**: {row['contenido']}")

# =========================================================
# 10. MOSTRAR TARIFAS
# =========================================================

st.markdown("## 💶 Tarifas aplicables")

if tarifas.empty:
    st.warning("No hay tarifas para esta fecha")
else:
    for _, row in tarifas.iterrows():
        st.write(f"**{row['subtipo']}**: {row['contenido']}")
