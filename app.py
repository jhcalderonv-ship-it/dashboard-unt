

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard UNT - Plantilla", layout="wide")

st.title("📊 Dashboard (Plantilla en Streamlit)")
st.caption("Carga tu CSV o usa el ejemplo. Filtra por fechas y categorías. Exporta vistas filtradas.")

@st.cache_data
def cargar_csv(file):
    return pd.read_csv(file, parse_dates=["fecha"])

ejemplo = st.toggle("Usar datos de ejemplo", value=True)
if ejemplo:
    df = cargar_csv("D:/Plantilla_python/datos_ejemplo.csv")
else:
    file = st.file_uploader("Sube un CSV con columnas: fecha, area, valor", type=["csv"])
    if file is None:
        st.stop()
    df = cargar_csv(file)

# Sidebar filtros
st.sidebar.header("Filtros")
min_d, max_d = df["fecha"].min(), df["fecha"].max()
rango = st.sidebar.date_input("Rango de fechas", (min_d, max_d), min_value=min_d, max_value=max_d)
if isinstance(rango, tuple):
    d1, d2 = rango
else:
    d1, d2 = rango, rango
areas = sorted(df["area"].dropna().unique().tolist())
sel_areas = st.sidebar.multiselect("Área", options=areas, default=areas)

df_f = df[(df["fecha"].between(pd.Timestamp(d1), pd.Timestamp(d2))) & (df["area"].isin(sel_areas))]

# KPIs
total = int(df_f["valor"].sum())
prom = float(df_f["valor"].mean()) if not df_f.empty else 0.0
maximo = int(df_f["valor"].max()) if not df_f.empty else 0
col1, col2, col3 = st.columns(3)
col1.metric("Total", f"{total:,.0f}")
col2.metric("Promedio", f"{prom:,.1f}")
col3.metric("Máximo", f"{maximo:,.0f}")

# Gráficos
c1, c2 = st.columns(2)
with c1:
    st.subheader("Serie temporal")
    fig_line = px.line(df_f, x="fecha", y="valor", color="area", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)
with c2:
    st.subheader("Barras por área")
    agg = df_f.groupby("area", as_index=False)["valor"].sum().sort_values("valor", ascending=False)
    fig_bar = px.bar(agg, x="area", y="valor", text="valor")
    fig_bar.update_traces(texttemplate="%{text:.0f}", textposition="outside")
    st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("Tabla (datos filtrados)")
st.dataframe(df_f.sort_values("fecha"), use_container_width=True)

# Descarga
csv = df_f.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Descargar CSV filtrado", data=csv, file_name="datos_filtrados.csv", mime="text/csv")

st.info("Consejo: despliega gratis en Streamlit Community Cloud. Incluye este `requirements.txt` y este `app.py`.")
