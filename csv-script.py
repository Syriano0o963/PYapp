import streamlit as st
import csv, io

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
            st.experimental_rerun()
        else:
            st.error("Ungültiger Benutzername oder Passwort.")

# Initialisiere Login-Status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Zeige Login, wenn nicht eingeloggt
if not st.session_state.logged_in:
    login()
    st.stop()

# ——— Haupt-Layout ———
st.set_page_config(page_title="CSV-Telefon-Generator", layout="wide")
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.image("logo.png", width=120)
with col_title:
    st.markdown("# 📞 CSV-Telefonnummern-Generator")
    st.markdown("Gib die Namen und Telefonnummern ein und lade die CSV direkt herunter.")
st.divider()

# ——— Eingabe-Steuerung in Sidebar ———
st.sidebar.header("Einstellungen")
anzahl = st.sidebar.number_input(
    "Anzahl Einträge",
    min_value=1,
    max_value=50,
    value=st.session_state.get("anzahl", 1),
    step=1,
    key="anzahl_input",
    help="Wähle die Anzahl der Einträge"
)
st.session_state["anzahl"] = anzahl
if st.sidebar.button("🔄 Alles zurücksetzen"):
    for key in list(st.session_state.keys()):
        if key.startswith(("vn_", "nn_", "tel_")) or key == "anzahl_input":
            del st.session_state[key]
    st.experimental_rerun()

# ——— Formular mit Expandern für jede Zeile ———
with st.form("telefon_form", clear_on_submit=False):
    entries = []
    for i in range(anzahl):
        with st.expander(f"Eintrag {i+1}", expanded=True):
            col1, col2, col3 = st.columns(3)
            vor = col1.text_input("Vorname", key=f"vn_{i}")
            nach = col2.text_input("Nachname", key=f"nn_{i}")
            tel = col3.text_input("Telefonnummer", key=f"tel_{i}")
            entries.append({"vor": vor, "nach": nach, "tel": tel})
    submitted = st.form_submit_button("📥 CSV erstellen")

# ——— CSV-Generierung ———
def format_phone(phone):
    return "0" + phone if phone.startswith("0") else phone

def replace_umlauts(text):
    for o, r in {"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss"}.items():
        text = text.replace(o, r)
    return text

if submitted:
    if all(e["vor"] and e["nach"] and e["tel"] for e in entries):
        buf = io.StringIO()
        writer = csv.writer(buf)
        for e in entries:
            writer.writerow([
                replace_umlauts(e["vor"]), replace_umlauts(e["nach"])
            ] + [""]*16 + ["1", "4", "1", format_phone(e["tel"]), "-1", "V2"])
        st.success("✅ CSV-Datei erstellt!")
        st.download_button(
            label="Download CSV",
            data=buf.getvalue(),
            file_name="telefonnummern.csv",
            mime="text/csv"
        )
    else:
        st.error("Bitte alle Felder ausfüllen.")
