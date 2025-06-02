import streamlit as st
import csv, io
import pandas as pd
from datetime import datetime
import re

# ——— Benutzer-Credentials aus Geheimnissen laden ———
CREDENTIALS = st.secrets.get("credentials", {})

# ——— Authentifizierung ———
def login():
    st.title("🔒 Login")
    username = st.text_input("Benutzername", key="login_usr")
    password = st.text_input("Passwort", type="password", key="login_pwd")
    if st.button("Anmelden"):
        if username in CREDENTIALS and CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success(f"Willkommen, {username}!")
        else:
            st.error("Ungültiger Benutzername oder Passwort.")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()

# ——— App-Inhalt nach Login ———
st.set_page_config(page_title="CSV-Telefon-Generator", layout="wide")
col1, col2 = st.columns([1, 4])
with col1:
    st.image("logo-without-bg.png", width=150)
with col2:
    st.markdown("# 📞Telefonbuch-Generator")
    st.markdown("Gib die Namen und Telefonnummern ein, lade eine bestehende CSV hoch oder exportiere dein Telefonbuch.")

# ——— Sidebar-Steuerung ———
st.sidebar.header("Steuerung")
if st.sidebar.button("🔄 Alles zurücksetzen"):
    for key in list(st.session_state.keys()):
        if key not in ("logged_in", "user"):
            del st.session_state[key]
    st.session_state.logged_in = False
    st.experimental_rerun()

# ——— Hilfsfunktionen ———
def replace_umlauts(text):
    for o, r in {"ä": "ae", "ö": "oe", "ü": "ue",
                 "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss"}.items():
        text = text.replace(o, r)
    return text

def has_whitespace(text):
    return bool(re.search(r"\s", text))

# ——— Initialisierung ———
cols = ["Vorname", "Nachname", "Telefonnummer"]
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame([["", "", ""]], columns=cols)

# ——— Hinweisbox mit Glühbirne ———
with st.container():
    st.markdown(
        '<div style="background-color: #fffbe6; padding: 10px; border-left: 6px solid #f1c40f; margin-bottom: 15px;">'
        '💡 <strong>Hinweis:</strong> Vorname, Nachname und Telefonnummer dürfen keine Leerzeichen enthalten. '
        'Verwende stattdessen Bindestriche (-) oder Unterstriche (_).'
        '</div>',
        unsafe_allow_html=True
    )

# ——— CSV-Upload ———
uploaded_file = st.file_uploader("Oder lade eine bestehende CSV-Datei hoch:", type=["csv"])
if uploaded_file:
    try:
        df_uploaded = pd.read_csv(uploaded_file, header=None, sep=",", quotechar='"', skipinitialspace=True)
        if df_uploaded.shape[1] >= 20:
            df_clean = pd.DataFrame({
                "Vorname": df_uploaded.iloc[:, 0],
                "Nachname": df_uploaded.iloc[:, 1],
                "Telefonnummer": df_uploaded.iloc[:, 18]
            })
            st.session_state.df = df_clean
            st.success("✅ CSV erfolgreich importiert und geladen!")
        else:
            st.error("❌ Die CSV-Datei hat nicht das erwartete Format (mind. 20 Spalten).")
    except Exception as e:
        st.error(f"❌ Fehler beim Einlesen der Datei: {e}")

# ——— Interaktive Tabelle ———
st.write("## Eingabefelder")
edited = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    key="editor"
)

# ——— Validierung ———
errors = []
for i, row in edited.iterrows():
    if has_whitespace(str(row["Vorname"])):
        errors.append(f"Zeile {i+1}: Vorname darf keine Leerzeichen enthalten.")
    if has_whitespace(str(row["Nachname"])):
        errors.append(f"Zeile {i+1}: Nachname darf keine Leerzeichen enthalten.")
    if has_whitespace(str(row["Telefonnummer"])):
        errors.append(f"Zeile {i+1}: Telefonnummer darf keine Leerzeichen enthalten.")

# ——— Fehleranzeige ———
if errors:
    st.error("❌ Bitte korrigiere die folgenden Eingaben, bevor du fortfährst:")
    for msg in errors:
        st.markdown(f"- {msg}")

# ——— CSV Export mit angepasster Telefonnummern-Logik ———
if st.button("📥 CSV erstellen und herunterladen", disabled=bool(errors)):
    buf = io.StringIO()
    writer = csv.writer(buf)

    from_upload = uploaded_file is not None  # Unterscheidung neue/alte Daten

    for _, row in edited.iterrows():
        vor = replace_umlauts(str(row["Vorname"]))
        nach = replace_umlauts(str(row["Nachname"]))
        tel = str(row["Telefonnummer"]).strip()

        if not from_upload:
            if tel.startswith("00"):
                pass  # unverändert lassen
            elif tel.startswith("0"):
                tel = "0" + tel  # weitere 0 voranstellen
            else:
                pass  # unverändert lassen
        # bei Upload bleiben die Nummern exakt so wie sie sind

        writer.writerow([vor, nach] + [""] * 15 + ["1", "4", "1", tel, "-1", "V2"])

    st.success("✅ CSV-Datei erfolgreich erstellt!")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"Telefonbuch-{timestamp}.csv"

    st.download_button(
        "Download CSV",
        data=buf.getvalue(),
        file_name=filename,
        mime="text/csv"
    )

# ——— Custom CSS zur UI-Anpassung ———
st.markdown(
    """
    <style>
    .css-18e3th9 { display: none; } /* Vollbild-Button */
    .css-1kyxreq { display: none; } /* Auge-Icon beim Passwortfeld */
    </style>
    """,
    unsafe_allow_html=True
)
