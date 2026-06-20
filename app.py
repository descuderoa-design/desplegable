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
# 2. LOAD DATA
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
# 4. SELECCIÓN
# =========================================================

municipios = sorted(df_mon["municipio"].dropna().unique())

municipio_sel = st.selectbox("Selecciona municipio", [""] + municipios)

if municipio_sel == "":
    st.stop()

df_muni = df_mon[df_mon["municipio"] == municipio_sel]

monumentos = sorted(df_muni["monumento"].dropna().unique())

monumento_sel = st.selectbox("Selecciona monumento", [""] + monumentos)

if monumento_sel == "":
    st.stop()

# =========================================================
# 5. FECHA
# =========================================================

fecha_texto = st.text_input("Fecha de visita (dd/mm/aaaa)")

if fecha_texto == "":
    st.info("Introduce una fecha")
    st.stop()

try:
    fecha_dt = pd.to_datetime(fecha_texto, format="%d/%m/%Y")
except:
    st.error("Formato incorrecto (dd/mm/aaaa)")
    st.stop()

# =========================================================
# 6. DÍA DE LA SEMANA
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
# 7. CONTENIDO
# =========================================================

df_info = df_cont[df_cont["monumento"] == monumento_sel].copy()

# =========================================================
# 8. TEMPORADAS CÍCLICAS (MM-DD)
# =========================================================

def md(date):
    return (date.month, date.day)

hoy = md(fecha_dt)

# parse inicio/fin cíclico
if "inicio" in df_info.columns and "fin" in df_info.columns:

    df_info["inicio_dt"] = pd.to_datetime(df_info["inicio"], dayfirst=True, errors="coerce")
    df_info["fin_dt"] = pd.to_datetime(df_info["fin"], dayfirst=True, errors="coerce")

def es_aplicable(row):

    # si no hay temporada → aplica siempre
    if "inicio_dt" not in row or pd.isna(row.get("inicio_dt")):
        return True

    inicio = row.get("inicio_dt")
    fin = row.get("fin_dt")

    if pd.isna(inicio) and pd.isna(fin):
        return True

    hoy_md = md(fecha_dt)

    if pd.notna(inicio) and pd.notna(fin):
        ini = md(inicio)
        fn = md(fin)

        # rango normal
        if ini <= fn:
            return ini <= hoy_md <= fn

        # rango cruzado año
        return hoy_md >= ini or hoy_md <= fn

    return True


df_info["aplicable"] = df_info.apply(es_aplicable, axis=1)

df_ok = df_info[df_info["aplicable"]]

# =========================================================
# 9. OUTPUT
# =========================================================

st.markdown("---")
st.markdown(f"# {monumento_sel}")

st.markdown(f"📅 Fecha: **{fecha_texto}**")
st.markdown(f"📆 Día de la semana: **{dia_semana}**")

# =========================================================
# 10. RESULTADOS
# =========================================================

st.markdown("## 🟢 Condiciones aplicables")

if df_ok.empty:
    st.warning("No hay condiciones aplicables")
else:
    for bloque in df_ok["bloque"].dropna().unique():

        st.markdown(f"### {bloque.capitalize()}")

        sub = df_ok[df_ok["bloque"] == bloque]

        for _, row in sub.iterrows():

            texto = row["contenido"]

            # opcional: reglas por día de semana
            if "dias_semana" in row and pd.notna(row["dias_semana"]):
                dias = [d.strip().lower() for d in str(row["dias_semana"]).split("-")]
                if dia_semana not in dias:
                    continue

            st.write(f"**{row['subtipo']}**: {texto}")
