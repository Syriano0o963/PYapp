import streamlit as st
import csv, io

# ——— Benutzer-Credentials aus Geheimnissen laden ———
# In .streamlit/secrets.toml oder über Streamlit Cloud Secrets konfigurieren:
# [credentials]
# abal = "Lassm!chnei02"
# hebe = "Lauertal13!"
CREDENTIALS = st.secrets.get("credentials", {})

# ——— Authentifizierung ———
def login():
    st.title("🔒 Login")
    username = st.text_input("Benutzername", key="login_usr")
    password = st.text_input("Passwort", type="password", key="login_pwd")
    if st.button("Anmelden"):
        # Überprüfe gegen Secrets
        if username in CREDENTIALS and password == CREDENTIALS[username]:
            st.session_state["logged_in"] = True
        else:
            st.error("🚫 Ungültiger Benutzername oder Passwort")

# Wenn nicht eingeloggt, zeige Login und beende Ausführung
if not st.session_state.get("logged_in", False):
    login()
    st.stop()

def login():
    st.title("🔒 Login")
    username = st.text_input("Benutzername", key="login_usr")
    password = st.text_input("Passwort", type="password", key="login_pwd")
    if st.button("Anmelden"):
        if username in CREDENTIALS and CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success(f"Willkommen, {username}!")
            # Nach erfolgreichem Login neu laden
            st.experimental_rerun()
        else:
            st.error("Ungültiger Benutzername oder Passwort.")

# Initialisiere Login-Status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Wenn nicht eingeloggt, zeige Login-Screen und stoppe
if not st.session_state.logged_in:
    login()
    st.stop()

# ——— Ab hier die geschützte App ———
# Löschen alter Login-Inputs
if "login_usr" in st.session_state:
    del st.session_state["login_usr"]
if "login_pwd" in st.session_state:
    del st.session_state["login_pwd"]

# App-Inhalt
st.image("logo.png", width=200)
st.title("📞 CSV‑Telefonnummern‑Generator")

# ——— Hilfsfunktionen ———
def format_phone(phone):
    return "0" + phone if phone.startswith("0") else phone

def replace_umlauts(text):
    for o, r in {"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss"}.items():
        text = text.replace(o, r)
    return text

# ——— Session State für Einträge initialisieren ———
if "anzahl" not in st.session_state:
    st.session_state["anzahl"] = 1

# ——— Callback-Funktionen ———
def inc_anzahl():
    st.session_state["anzahl"] += 1

def dec_anzahl():
    if st.session_state["anzahl"] > 1:
        st.session_state["anzahl"] -= 1

# ——— Layout für Anzahl-Steuerung ———
col_count, col_reset = st.columns([2,1])
with col_count:
    st.write("**Anzahl Einträge:**")
    st.button("－", on_click=dec_anzahl)
    st.button("＋", on_click=inc_anzahl)
    st.write(st.session_state["anzahl"])

# ——— Formular für Einträge ———
with st.form("form", clear_on_submit=False):
    eintraege = []
    for i in range(st.session_state["anzahl"]):
        st.markdown(f"**Eintrag {i+1}**")
        vor = st.text_input(f"Vorname {i+1}", key=f"vn_{i}")
        nach = st.text_input(f"Nachname {i+1}", key=f"nn_{i}")
        tel = st.text_input(f"Telefon {i+1}", key=f"tel_{i}")
        eintraege.append({"vor": vor, "nach": nach, "tel": tel})
    submitted = st.form_submit_button("📥 CSV erstellen")

if submitted:
    if all(e["vor"] and e["nach"] and e["tel"] for e in eintraege):
        buf = io.StringIO()
        wr = csv.writer(buf)
        for e in eintraege:
            wr.writerow([
                replace_umlauts(e["vor"]), replace_umlauts(e["nach"])
            ] + [""]*16 + ["1","4","1", format_phone(e["tel"]),"-1","V2"])
        st.success("✅ CSV-Datei erfolgreich erstellt!")
        st.download_button("Download CSV", data=buf.getvalue(), file_name="telefonnummern.csv", mime="text/csv")
    else:
        st.error("❗ Bitte alle Felder ausfüllen.")
