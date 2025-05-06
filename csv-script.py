import streamlit as st
import csv, io
import pandas as pd
from datetime import datetime
import re
from docx import Document

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
    return "0" + phone if not phone.startswith("0") else phone

def replace_umlauts(text):
    for o, r in {"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss"}.items():
        text = text.replace(o, r)
    return text

def find_whitespace_position(text):
    match = re.search(r"\s", text)
    return match.start() if match else -1

# ——— Initialisierung ———
cols = ["Vorname", "Nachname", "Telefonnummer"]
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame([["", "", ""]], columns=cols)

# ——— Hinweisbox ———
st.markdown(
    '<div style="background-color: #fffbe6; padding: 10px; border-left: 6px solid #f1c40f; margin-bottom: 15px;">'
    '💡 <strong>Hinweis:</strong> Vorname, Nachname und Telefonnummer dürfen keine Leerzeichen enthalten. '
    'Verwende stattdessen Bindestriche (-) oder Unterstriche (_).'
    '</div>',
    unsafe_allow_html=True
)

# ——— Word/Excel Upload ———
st.write("## 📂 Word/Excel-Datei hochladen")
upload_doc = st.file_uploader("Word (.docx) oder Excel (.xlsx)", type=["docx", "xlsx"], key="file_upload_docx_xlsx")
if upload_doc:
    try:
        new_rows = []
        if upload_doc.name.endswith(".xlsx"):
            df_upload = pd.read_excel(upload_doc)
            if all(col in df_upload.columns for col in cols):
                new_rows = df_upload[cols].values.tolist()
            else:
                st.warning("⚠️ Excel-Datei muss die Spalten 'Vorname', 'Nachname' und 'Telefonnummer' enthalten.")
        elif upload_doc.name.endswith(".docx"):
            doc = Document(upload_doc)
            for para in doc.paragraphs:
                line = para.text.strip()
                parts = line.split()
                if len(parts) >= 3:
                    vorname, nachname, telefon = parts[0], parts[1], parts[2]
                    new_rows.append([vorname, nachname, telefon])

        if new_rows:
            df_new = pd.DataFrame(new_rows, columns=cols)
            st.session_state.df = pd.concat([st.session_state.df, df_new], ignore_index=True)
            st.success(f"✅ {len(new_rows)} Zeile(n) aus Datei erfolgreich übernommen.")
        else:
            st.info("ℹ️ Keine gültigen Daten erkannt.")
    except Exception as e:
        st.error(f"❌ Fehler beim Verarbeiten der Datei: {e}")

# ——— Interaktive Tabelle ———
st.write("## Eingabefelder")
edited = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    key="editor"
)

# ——— Zeilen hinzufügen/löschen mit Bestätigung ———
def confirm_action(action):
    confirmation = st.radio(f"💬 Bist du sicher, dass du diese Zeile {action} möchtest?", ["Ja", "Nein"], index=1)
    return confirmation == "Ja"

if st.button("➕ Zeile hinzufügen"):
    if all(edited.iloc[-1] == ""):
        st.warning("⚠️ Die letzte Zeile ist leer und kann nicht hinzugefügt werden.")
    else:
        if confirm_action("hinzufügen"):
            new_row = pd.DataFrame([["", "", ""]], columns=cols)
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            st.success("✅ Neue Zeile wurde hinzugefügt!")

if st.button("➖ Letzte Zeile löschen"):
    if len(st.session_state.df) > 1 and not all(edited.iloc[-1] == ""):
        if confirm_action("löschen"):
            st.session_state.df = st.session_state.df[:-1]
            st.success("✅ Letzte Zeile wurde gelöscht!")
    else:
        st.warning("⚠️ Die letzte Zeile ist leer und kann nicht gelöscht werden.")

# ——— Tabelle leeren ———
if st.button("🧹 Tabelle leeren"):
    st.session_state.df = pd.DataFrame([["", "", ""]], columns=cols)
    st.success("✅ Tabelle wurde erfolgreich geleert.")

# ——— Validierung ———
errors = []
missing_cols = [col for col in cols if col not in edited.columns]
if missing_cols:
    st.error(f"❌ Fehlende Spalten in der Tabelle: {', '.join(missing_cols)}")
else:
    for i, row in edited.iterrows():
        for column in cols:
            text = str(row[column])
            pos = find_whitespace_position(text)
            if pos != -1:
                errors.append(f"Zeile {i+1}, Spalte '{column}': Leerzeichen an Position {pos+1}.")

if errors:
    st.error("❌ Bitte korrigiere die folgenden Eingaben, bevor du fortfährst:")
    for msg in errors:
        st.markdown(f"- {msg}")

# ——— CSV Export ———
if st.button("📥 CSV erstellen und herunterladen", disabled=bool(errors or missing_cols)):
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
        "⬇️ Download CSV",
        data=buf.getvalue(),
        file_name=filename,
        mime="text/csv"
    )

# ——— UI-Anpassung ———
st.markdown(
    """
    <style>
    .css-18e3th9 { display: none; }  /* Vollbild-Button */
    .css-1kyxreq { display: none; }  /* Auge-Icon Passwortfeld */
    </style>
    """,
    unsafe_allow_html=True
)
