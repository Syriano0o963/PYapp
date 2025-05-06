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
    st.markdown("Gib die Namen und Telefonnummern ein, und lade deine CSV herunter.")

# ——— Sidebar-Steuerung ———
st.sidebar.header("Steuerung")
if st.sidebar.button("🔄 Alles zurücksetzen"):
    for key in list(st.session_state.keys()):
        if key not in ("logged_in", "user"):
            del st.session_state[key]
    st.session_state.logged_in = False
    st.rerun()

# ——— Hilfsfunktionen ———
def format_phone(phone):
    return "0" + phone if phone.startswith("0") else phone

def replace_umlauts(text):
    for o, r in {"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss"}.items():
        text = text.replace(o, r)
    return text

def find_whitespace_position(text):
    match = re.search(r"\s", text)  # prüft auf Leerzeichen
    return match.start() if match else -1  # Gibt die Position des ersten Leerzeichens zurück, sonst -1

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

# ——— Drag-and-Drop für CSV-Dateien ———
uploaded_file = st.file_uploader("Wähle eine CSV-Datei zum Hochladen", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state.df = df  # Läd die hochgeladene CSV in das DataFrame
    st.success("CSV-Datei erfolgreich hochgeladen!")

# ——— Interaktive Tabelle ———
st.write("## Eingabefelder")
edited = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",  # Beibehalten der dynamischen Zeilenanzahl
    key="editor"
)

# ——— Zeilen hinzufügen/löschen ———
if st.button("Zeile hinzufügen"):
    new_row = pd.DataFrame([["", "", ""]], columns=cols)
    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)

if st.button("Letzte Zeile löschen"):
    if len(st.session_state.df) > 1:  # Verhindert, dass die letzte Zeile gelöscht wird
        st.session_state.df = st.session_state.df[:-1]

# ——— Validierung ———
errors = []
for i, row in edited.iterrows():
    for column in ["Vorname", "Nachname", "Telefonnummer"]:
        text = str(row[column])
        whitespace_position = find_whitespace_position(text)
        if whitespace_position != -1:  # Wenn ein Leerzeichen gefunden wurde
            errors.append(f"Zeile {i+1}, Spalte '{column}': Leerzeichen an Position {whitespace_position+1}.")

# ——— Fehleranzeige ———
if errors:
    st.error("❌ Bitte korrigiere die folgenden Eingaben, bevor du fortfährst:")
    for msg in errors:
        st.markdown(f"- {msg}")

# ——— CSV Export mit Zeitstempel ———
if st.button("📥 CSV erstellen und herunterladen", disabled=bool(errors)):
    buf = io.StringIO()
    writer = csv.writer(buf)
    for _, row in edited.iterrows():
        vor = replace_umlauts(str(row["Vorname"]))
        nah = replace_umlauts(str(row["Nachname"]))
        tel = format_phone(str(row["Telefonnummer"]))
        writer.writerow([vor, nah] + [""] * 15 + ["1", "4", "1", tel, "-1", "V2"])
    st.success("✅ CSV-Datei erfolgreich erstellt!")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"Telefonbuch-{timestamp}.csv"

    st.download_button(
        "Download CSV",
        data=buf.getvalue(),
        file_name=filename,
        mime="text/csv"
    )

# ——— Custom CSS zur UI-Anpassung (Vollbild-Button und Auge-Icon ausblenden) ———
st.markdown(
    """
    <style>
    /* Verstecke den Vollbild-Button und das Auge-Icon in der oberen rechten Ecke */
    .css-18e3th9 { display: none; } /* Vollbild-Button */
    .css-1kyxreq { display: none; } /* Auge-Icon für das Passwortfeld */
    </style>
    """,
    unsafe_allow_html=True
)
