import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Kommunales SDG-Dashboard", layout="wide")

# Daten einlesen
@st.cache_data
def load_data():
    df = pd.read_csv("./wegweiser_sdg_aufbereitet/wegweiser_sdg_panel_long.csv", sep=";")
    df["Jahr"] = df["Jahr"].astype(int)
    return df

df = load_data()

st.title("📊 Kommunales SDG-Indikatoren Dashboard")

# Filterleiste
col1, col2 = st.columns(2)
with col1:
    communes = df["Kommune"].unique().tolist()
    default_com = [c for c in ["Ratingen", "Nordrhein-Westfalen"] if c in communes]
    selected_communes = st.multiselect("Kommunen / Benchmark:", communes, default=default_com)

with col2:
    indicators = sorted(df["Indikator"].dropna().unique().tolist())
    selected_indicator = st.selectbox("Indikator:", indicators)

# Daten filtern
df_filtered = df[
    (df["Kommune"].isin(selected_communes)) & 
    (df["Indikator"] == selected_indicator) & 
    (df["Jahr"].between(2016, 2023))
].dropna(subset=["Wert"])

unit = df_filtered["Einheit"].dropna().iloc[0] if not df_filtered.empty and not df_filtered["Einheit"].dropna().empty else ""

# Interaktiver Zeitreihenplot mit Plotly
if not df_filtered.empty:
    fig = px.line(
        df_filtered,
        x="Jahr",
        y="Wert",
        color="Kommune",
        markers=True,
        title=f"{selected_indicator} ({unit})",
        labels={"Wert": f"Wert in {unit}" if unit else "Wert", "Jahr": "Erhebungsjahr"}
    )
    fig.update_xaxes(dtick=1)
    fig.update_layout(template="plotly_white", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
    
    # Datentabelle anzeigen
    with st.expander("Tabellarische Übersicht anzeigen"):
        st.dataframe(df_filtered[["Kommune", "Jahr", "Wert", "Einheit"]].sort_values(["Kommune", "Jahr"]))
else:
    st.info("Keine Daten für die gewählte Kombination im Zeitraum 2016–2023 vorhanden.")