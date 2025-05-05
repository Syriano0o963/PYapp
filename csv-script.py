import streamlit as st
import csv, io
import pandas as pd

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
    st.image("logo.png", width=150)
with col2:
    st.markdown("# 📞 CSV-Telefonnummern-Generator")
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
    return "0" + phone if not phone.startswith("0") else phone

def replace_umlauts(text):
    for o, r in {"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss"}.items():
        text = text.replace(o, r)
    return text

# ——— Initial-DF ———
cols = ["Vorname", "Nachname", "Telefonnummer"]
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame([["", "", "1"]], columns=cols).astype("object")

# Neue Zeile hinzufügen, wenn nötig
prev_len = len(st.session_state.df)
edited = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    key="editor",
    column_config={
        "Vorname": st.column_config.TextColumn("Vorname"),
        "Nachname": st.column_config.TextColumn("Nachname"),
        "Telefonnummer": st.column_config.TextColumn("Telefonnummer"),
    }
)
# Falls neue Zeile hinzugefügt wurde, automatische Nummer setzen
if len(edited) > prev_len:
    new_row_index = len(edited) - 1
    edited.iloc[new_row_index, 2] = str(new_row_index + 1)  # Telefonnummer
st.session_state.df = edited.astype("object")

# ——— Tabelle anzeigen ———
st.write("## Eingabefelder")
st.dataframe(st.session_state.df)

# ——— CSV Export ———
if st.button("📥 CSV erstellen und herunterladen"):
    buf = io.StringIO()
    writer = csv.writer(buf)
    for _, row in st.session_state.df.iterrows():
        vor = replace_umlauts(row["Vorname"])
        nah = replace_umlauts(row["Nachname"])
        tel = format_phone(str(row["Telefonnummer"]))
        writer.writerow([vor, nah] + [""] * 16 + ["1", "4", "1", tel, "-1", "V2"])
    st.success("✅ CSV-Datei erfolgreich erstellt!")
    st.download_button(
        "Download CSV", data=buf.getvalue(),
        file_name="telefonnummern.csv", mime="text/csv"
    )
