import streamlit as st
import csv, io
import pandas as pd
from datetime import datetime  # ✅ Neu für Zeitstempel im Dateinamen

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
    phone = phone.strip().replace(" ", "").replace("-", "")
    if not phone.startswith("0") and not phone.startswith("+"):
        phone = "0" + phone
    return phone

def replace_umlauts(text):
    for o, r in {"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss"}.items():
        text = text.replace(o, r)
    return text

# ——— Initialisierung ———
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

# ——— CSV Export mit Zeitstempel ———
if st.button("📥 CSV erstellen und herunterladen"):
    buf = io.StringIO()
    writer = csv.writer(buf)
    
    for _, row in edited.iterrows():
        vor = replace_umlauts(str(row["Vorname"]).strip())
        nach = replace_umlauts(str(row["Nachname"]).strip())
        
        raw_tel = row["Telefonnummer"]
        if pd.isna(raw_tel) or str(raw_tel).strip() == "":
            tel = ""
        else:
            try:
                # Konvertiere float oder int zu int, dann zu String (entfernt Nachkommastellen)
                tel_str = str(int(float(raw_tel))) if isinstance(raw_tel, (float, int)) else str(raw_tel)
                tel = format_phone(tel_str)
                
                # Optional: internationale Schreibweise (z. B. +49 statt 0)
                # if tel.startswith("0"):
                #     tel = "+49" + tel[1:]
                
            except Exception as e:
                tel = ""
        
        writer.writerow([vor, nach] + [""] * 17 + ["1", "4", "1", tel, "-1", "V2"])
    
    st.success("✅ CSV-Datei erfolgreich erstellt!")

    # ✅ Dateiname mit aktuellem Datum und Uhrzeit
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"Telefonbuch-{timestamp}.csv"

    st.download_button(
        "Download CSV",
        data=buf.getvalue(),
        file_name=filename,
        mime="text/csv"
    )
