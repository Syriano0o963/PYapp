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
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
        else:
            st.error("Ungültiger Benutzername oder Passwort.")

# Initialisiere Login-Status
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Wenn nicht eingeloggt, zeige Login und beende
if not st.session_state["logged_in"]:
    login()
    st.stop()

# ——— Ab hier geschützte App ———
# Entferne Login-Inputs aus state
for key in ["login_usr", "login_pwd"]:
    if key in st.session_state:
        del st.session_state[key]

# ——— Layout ———
st.set_page_config(page_title="CSV-Telefon-Generator", layout="wide")
col1, col2 = st.columns([1, 4])
with col1:
    st.image("logo.png", width=150)
with col2:
    st.markdown("# 📞 CSV-Telefonnummern-Generator")
    st.markdown("Gib die Namen und Telefonnummern ein, und lade deine CSV herunter.")
st.markdown("---")

# ——— Hilfsfunktionen ———
def format_phone(phone):
    return "0" + phone if phone.startswith("0") else phone

def replace_umlauts(text):
    for o, r in {"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss"}.items():
        text = text.replace(o, r)
    return text

# ——— Anzahl-Steuerung in Sidebar ———
st.sidebar.header("Einstellungen")
if "anzahl" not in st.session_state:
    st.session_state["anzahl"] = 1

st.sidebar.number_input(
    "Anzahl Einträge",
    min_value=1, max_value=100, step=1,
    key="anzahl"
)
if st.sidebar.button("Alles zurücksetzen"):
    # lösche dynamische Felder
    for key in list(st.session_state.keys()):
        if key.startswith(("vn_", "nn_", "tel_")):
            del st.session_state[key]
    st.session_state["anzahl"] = 1

# ——— Tabelle editierbar ———
rows = []
for i in range(st.session_state["anzahl"]):
    vor = st.session_state.get(f"vn_{i}", "")
    nn = st.session_state.get(f"nn_{i}", "")
    tel = st.session_state.get(f"tel_{i}", "")
    rows.append({"Vorname": vor, "Nachname": nn, "Telefon": tel})
df = st.experimental_data_editor(
    data=rows,
    num_rows="related",
    key="editor"
)

# Schreibe zurück in session_state
for i, row in enumerate(df):
    st.session_state[f"vn_{i}"] = row["Vorname"]
    st.session_state[f"nn_{i}"] = row["Nachname"]
    st.session_state[f"tel_{i}"] = row["Telefon"]

# ——— CSV Export ———
st.markdown("---")
if st.button("📥 CSV erstellen"):
    output = io.StringIO()
    writer = csv.writer(output)
    for i in range(st.session_state["anzahl"]):
        vor = replace_umlauts(st.session_state[f"vn_{i}"])
        nah = replace_umlauts(st.session_state[f"nn_{i}"])
        tel = format_phone(st.session_state[f"tel_{i}"])
        writer.writerow([vor, nah] + [""]*16 + ["1","4","1", tel, "-1", "V2"])
    st.success("✅ CSV-Datei erfolgreich erstellt!")
    st.download_button("Download CSV", data=output.getvalue(), file_name="telefonnummern.csv", mime="text/csv")
