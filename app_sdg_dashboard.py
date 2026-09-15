from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Kommunales SDG-Dashboard", layout="wide")

# Exakter Pfad zur Datei im selben Ordner wie das Skript
DATA_PATH = Path(__file__).resolve().parent / "wegweiser_sdg_panel_long.csv"


@st.cache_data
def load_data():
    if not DATA_PATH.is_file():
        st.error(f"Datei nicht gefunden unter: {DATA_PATH}")
        st.stop()

    df = pd.read_csv(DATA_PATH, sep=";")
    df["Jahr"] = pd.to_numeric(df["Jahr"], errors="coerce").fillna(0).astype(int)
    return df


df = load_data()

st.title("📊 Kommunales SDG-Indikatoren Dashboard")

# Filterleiste
col1, col2 = st.columns(2)
with col1:
    communes = sorted(df["Kommune"].dropna().unique().tolist())
    default_com = [c for c in ["Ratingen", "Nordrhein-Westfalen"] if c in communes]
    if not default_com and communes:
        default_com = [communes[0]]
    selected_communes = st.multiselect("Kommunen / Benchmark:", communes, default=default_com)

with col2:
    indicators = sorted(df["Indikator"].dropna().unique().tolist())
    selected_indicator = st.selectbox("Indikator:", indicators)

# Daten filtern
df_filtered = df[
    (df["Kommune"].isin(selected_communes))
    & (df["Indikator"] == selected_indicator)
    & (df["Jahr"].between(2016, 2023))
].dropna(subset=["Wert"])

unit = ""
if not df_filtered.empty:
    valid_units = df_filtered["Einheit"].dropna()
    if not valid_units.empty:
        unit = valid_units.iloc[0]

# Interaktiver Zeitreihenplot mit Plotly
if not df_filtered.empty:
    fig = px.line(
        df_filtered,
        x="Jahr",
        y="Wert",
        color="Kommune",
        markers=True,
        title=f"{selected_indicator} ({unit})" if unit else selected_indicator,
        labels={"Wert": f"Wert in {unit}" if unit else "Wert", "Jahr": "Erhebungsjahr"},
    )
    fig.update_xaxes(dtick=1, range=[2015.5, 2023.5])
    fig.update_layout(template="plotly_white", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Tabellarische Übersicht anzeigen"):
        st.dataframe(
            df_filtered[["Kommune", "Jahr", "Wert", "Einheit"]].sort_values(["Kommune", "Jahr"]),
            use_container_width=True,
        )
else:
    st.info("Keine Daten für die gewählte Kombination im Zeitraum 2016–2023 vorhanden.")
