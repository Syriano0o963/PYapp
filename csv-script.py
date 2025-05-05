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
        if username in CREDENTIALS and CREDENTIALS[username] == password:ALS[username] == password:
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
# Reset-Button
if st.sidebar.button("🔄 Alles zurücksetzen"):
    # clear session state except credentials
    for key in list(st.session_state.keys()):
        if key not in ("logged_in", "user"):
            del st.session_state[key]
    st.session_state.logged_in = False
    st.rerun()

# Anzahl Einträge außerhalb des Formulars
st.sidebar.subheader("Anzahl Einträge")
if "anzahl" not in st.session_state:
    st.session_state.anzahl = 1
anzahl = st.sidebar.number_input(
    "", min_value=1, max_value=100,
    value=st.session_state.anzahl, step=1, key="anzahl_input",
    on_change=lambda: None
)
st.session_state.anzahl = anzahl

# ——— Tabelle zur Eingabe ———
def format_phone(phone):
    return "0" + phone if phone.startswith("0") else phone

def replace_umlauts(text):
    for o, r in {"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss"}.items():
        text = text.replace(o, r)
    return text

# DataFrame initialisieren oder aus session laden
if "df" not in st.session_state:
    cols = ["Vorname", "Nachname", "Telefonnummer"]
    st.session_state.df = pd.DataFrame(
        [["", "", ""] for _ in range(st.session_state.anzahl)],
        columns=cols
    )
else:
    df_existing = st.session_state.df
    target = st.session_state.anzahl
    if target > len(df_existing):
        for _ in range(target - len(df_existing)):
            df_existing.loc[len(df_existing)] = ["", "", ""]
    elif target < len(df_existing):
        df_existing = df_existing.iloc[:target]
    st.session_state.df = df_existing

# interaktive Tabelle
st.write("## Eingabefelder")
edited = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    key="editor"
)
st.session_state.df = edited

# CSV Export
if st.button("📥 CSV erstellen und herunterladen"):
    buf = io.StringIO()
    writer = csv.writer(buf)
    for _, row in st.session_state.df.iterrows():
        vor = replace_umlauts(row["Vorname"])
        nah = replace_umlauts(row["Nachname"])
        tel = format_phone(str(row["Telefonnummer"]))
        writer.writerow([
            vor, nah
        ] + [""] * 16 + ["1", "4", "1", tel, "-1", "V2"])
    st.success("✅ CSV-Datei erfolgreich erstellt!")
    st.download_button(
        "Download CSV", data=buf.getvalue(),
        file_name="telefonnummern.csv", mime="text/csv"
    )
