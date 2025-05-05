import streamlit as st
import csv
import io

# ——— Benutzer-Credentials aus Geheimnissen laden ———
CREDENTIALS = st.secrets.get("credentials", {})

# ——— Authentifizierung ———
def login():
    st.title("🔒 Login")
    username = st.text_input("Benutzername", key="login_usr")
    password = st.text_input("Passwort", type="password", key="login_pwd")
    if st.button("Anmelden"):
        if username in CREDENTIALS and CREDENTIALS[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
            # nach erfolgreichem Login App neu rendern
            st.experimental_rerun()
        else:
            st.error("🚫 Ungültiger Benutzername oder Passwort.")

# Initialisiere Login-Status
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Wenn nicht eingeloggt, zeige Login und stoppe
if not st.session_state["logged_in"]:
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

# Sidebar-Steuerung
st.sidebar.header("Steuerung")
# Reset-Button
if st.sidebar.button("🔄 Alles zurücksetzen"):
    # clear session state except credentials
    for key in list(st.session_state.keys()):
        if key not in ("logged_in", "user"):
            del st.session_state[key]
    st.session_state["logged_in"] = False
    st.experimental_rerun()

# Anzahl Einträge
if "anzahl" not in st.session_state:
    st.session_state["anzahl"] = 1
st.sidebar.subheader("Anzahl Einträge")
st.session_state["anzahl"] = st.sidebar.number_input(
    "", min_value=1, max_value=100,
    value=st.session_state["anzahl"], step=1, key="anzahl_input"
)

# ——— Hilfsfunktionen ———
def format_phone(phone):
    return "0" + phone if phone.startswith("0") else phone

def replace_umlauts(text):
    for o, r in {"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss"}.items():
        text = text.replace(o, r)
    return text

# ——— Eingabefelder als Expander ———
st.write("## Eingabefelder")

# Liste in session_state
if "entries" not in st.session_state:
    st.session_state["entries"] = [
        {"Vorname": "", "Nachname": "", "Telefonnummer": ""}
        for _ in range(st.session_state["anzahl"])
    ]
else:
    # Liste anpassen bei Mengenänderung
    entries = st.session_state["entries"]
    target = st.session_state["anzahl"]
    if target > len(entries):
        for _ in range(target - len(entries)):
            entries.append({"Vorname": "", "Nachname": "", "Telefonnummer": ""})
    elif target < len(entries):
        entries = entries[:target]
    st.session_state["entries"] = entries

# Expander pro Eintrag
for i, entry in enumerate(st.session_state["entries"]):
    with st.expander(f"Eintrag {i+1}", expanded=True):
        cols = st.columns([3,3,4])
        entry["Vorname"] = cols[0].text_input("Vorname", value=entry["Vorname"], key=f"vn_{i}")
        entry["Nachname"] = cols[1].text_input("Nachname", value=entry["Nachname"], key=f"nn_{i}")
        entry["Telefonnummer"] = cols[2].text_input("Telefonnummer", value=entry["Telefonnummer"], key=f"tel_{i}")

# ——— CSV Export ———
if st.button("📥 CSV erstellen und herunterladen"):
    buf = io.StringIO()
    writer = csv.writer(buf)
    for entry in st.session_state["entries"]:
        vor = replace_umlauts(entry["Vorname"])
        nah = replace_umlauts(entry["Nachname"])
        tel = format_phone(entry["Telefonnummer"])
        writer.writerow([vor, nah] + [""]*16 + ["1", "4", "1", tel, "-1", "V2"])
    st.success("✅ CSV-Datei erfolgreich erstellt!")
    st.download_button(
        "Download CSV", data=buf.getvalue(),
        file_name="telefonnummern.csv", mime="text/csv"
    )
