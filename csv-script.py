import streamlit as st
import csv, io
import pandas as pd

# ——— Benutzer-Credentials aus Geheimnissen laden ———
CREDENTIALS = st.secrets.get("credentials", {})

# ——— Authentifizierung mit Spinner & Fehlerbehandlung ———
def login():
    st.set_page_config(page_title="Login", layout="centered")
    st.title("🔒 Login")
    username = st.text_input("Benutzername", key="login_usr")
    password = st.text_input("Passwort", type="password", key="login_pwd")

    if st.button("Anmelden") or st.session_state.get("trying_login"):
        st.session_state.trying_login = True
        with st.spinner("🔐 Anmeldung wird überprüft..."):
            if username in CREDENTIALS and CREDENTIALS[username] == password:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.success(f"Willkommen, {username}!")
            else:
                st.session_state.logged_in = False
                st.error("❌ Ungültiger Benutzername oder Passwort.")
        st.session_state.trying_login = False

# ——— Login-Check ———
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
    st.markdown("# 📞 Telefonbuch-Generator")
    st.markdown("Gib die Namen und Telefonnummern ein, und lade deine CSV-Datei herunter.")

# ——— Sidebar: Steuerung ———
st.sidebar.header("Steuerung")
if st.sidebar.button("🔄 Alles zurücksetzen"):
    for key in list(st.session_state.keys()):
        if key not in ("logged_in", "user"):
            del st.session_state[key]
    st.session_state.logged_in = False
    st.experimental_rerun()

# ——— Hilfsfunktionen ———
def format_phone(phone):
    phone = phone.strip()
    return phone if phone.startswith("0") else "0" + phone

def replace_umlauts(text):
    if not isinstance(text, str):
        return ""
    for o, r in {"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss"}.items():
        text = text.replace(o, r)
    return text

# ——— Tabelle initialisieren ———
cols = ["Vorname", "Nachname", "Telefonnummer"]
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame([["", "", ""]], columns=cols)

# ——— Interaktive Tabelle ———
st.write("## Eingabefelder")
edited = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    key="editor"
)
st.session_state.df = edited

# ——— CSV Export ———
if st.button("📥 CSV erstellen und herunterladen"):
    buf = io.StringIO()
    writer = csv.writer(buf)
    for _, row in edited.iterrows():
        vor = replace_umlauts(row["Vorname"])
        nach = replace_umlauts(row["Nachname"])
        tel = format_phone(str(row["Telefonnummer"]))
        writer.writerow([vor, nach] + [""] * 16 + ["1", "4", "1", tel, "-1", "V2"])
    st.success("✅ CSV-Datei erfolgreich erstellt!")
    st.download_button(
        "Download CSV",
        data=buf.getvalue(),
        file_name="telefonnummern.csv",
        mime="text/csv"
    )
