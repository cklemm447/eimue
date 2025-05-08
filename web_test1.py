
import pandas as pd
import streamlit as st



# --- Datenverarbeitung ---
@st.cache_data
def load_data():
    # CSV laden
    df = pd.read_csv("E-B.csv", sep=";", encoding="iso-8859-1", header=None)

    # Header verarbeiten
    header = df.iloc[0:2]  # erste zwei Zeilen
    data = df.iloc[2:].reset_index(drop=True)  # Restliche Daten

    # Spaltennamen aus 2 Headerzeilen zusammenbauen
    combined_headers = []
    for i in range(df.shape[1]):
        main = str(header.iloc[0, i]).strip()
        sub = str(header.iloc[1, i]).strip()
        if sub and sub != 'nan':
            combined_headers.append(f"{main} | {sub}")
        else:
            combined_headers.append(main)

    # Neue Spaltennamen setzen
    data.columns = combined_headers

    # "x" in True, leer in False umwandeln
    data = data.fillna("")
    data = data.replace("x", True)
    data = data.applymap(lambda x: True if x == True else False if x == "" else x)

    # Kategorienstruktur für Filter erstellen
    kategorien = {}
    for col in data.columns:
        if "|" in col:
            kat, subkat = [s.strip() for s in col.split("|", 1)]
            if kat not in kategorien:
                kategorien[kat] = []
            kategorien[kat].append(subkat)

    return data, kategorien

# --- Streamlit UI ---
st.set_page_config(page_title="🐄 Eimü-Produktberater", layout="wide")
st.title("🐄 Eimü-Produktberater")
#st.set_page_config(
#    page_title="🐄 Eimü-Produktberater",
#    layout="wide",
#    page_icon="🐄",
#    initial_sidebar_state="expanded"
#)

# Daten laden
try:
    produkt_df, kategorien = load_data()
except Exception as e:
    st.error(f"Fehler beim Laden der Datei: {e}")
    st.stop()

# --- Sidebar Filter ---
st.sidebar.header("🔍 Filter")
filter_selection = {}

for kat, subkats in kategorien.items():
    auswahl = st.sidebar.multiselect(f"{kat}", subkats, key=f"filter_{kat}")
    if auswahl:
        filter_selection[kat] = auswahl

# --- Produktfilter anwenden ---
def filter_produkte(df, filter_selection):
    if not filter_selection:
        return df

    mask = pd.Series([True] * len(df))
    for kat, unterkats in filter_selection.items():
        submask = pd.Series([False] * len(df))
        for unterkat in unterkats:
            spaltenname = f"{kat} | {unterkat}"
            if spaltenname in df.columns:
                submask |= df[spaltenname] == True
        mask &= submask
    return df[mask]

# --- Ergebnisse anzeigen ---
gefiltert = filter_produkte(produkt_df, filter_selection)

st.subheader("🎯 Passende Empfehlungen")

if gefiltert.empty:
    st.warning("Keine passenden Produkte gefunden.")
else:
    #Dynamisch die Spaltennamen bestimmen
    produktname_col = [col for col in gefiltert.columns if "Produktname" in col][0]
    wirkstoff_col = [col for col in gefiltert.columns if "Wirkstoff" in col][0]
    pflegestoff_col = [col for col in gefiltert.columns if "Pflegestoff" in col][0]
    auslobung_col = [col for col in gefiltert.columns if "Auslobung" in col][0]

for _, row in gefiltert.iterrows():
    name = row[produktname_col]
    with st.expander(f"⭐ {name}"):
        col1, col2 = st.columns([1, 3])
        
        # Bild anzeigen
        with col1:
            bildpfad = f"img/{str(name).strip().replace(' ', '_')}.png"
            try:
                st.image(bildpfad, width=120, caption=name)
            except:
                st.warning("📷 Kein Bild gefunden.")
        
        # Produktinfos anzeigen
        with col2:
            st.markdown(f"**🧪 Wirkstoff:** {row[wirkstoff_col]}")
            st.markdown(f"**🌿 Pflegestoff:** {row[pflegestoff_col]}")
            st.markdown(f"**🎯 Auslobung:** {row[auslobung_col]}")

