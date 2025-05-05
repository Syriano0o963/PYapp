import streamlit as st
import csv, io

# ——— Hilfsfunktionen ———
def format_phone(phone):
    return "0" + phone if phone.startswith("0") else phone

def replace_umlauts(text):
    for o, r in {"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss"}.items():
        text = text.replace(o, r)
    return text

# ——— Session State für Einträge initialisieren ———
if "anzahl" not in st.session_state:
    st.session_state.anzahl = 1

# ——— Callback-Funktionen ———
def add_entry():
    st.session_state.anzahl += 1

def reset_entries():
    # zurücksetzen auf 1 Eintrag und alle dynamischen Keys löschen
    for key in list(st.session_state.keys()):
        if key.startswith(("vn_", "nn_", "tel_")): 
            del st.session_state[key]
    st.session_state.anzahl = 1

# ——— UI ———
st.image("logo.png", width=200)
st.title("📞 Telefonbuch‑Generator")

# Buttons für Neu/Plus
col1, col2 = st.columns([1,1])
col1.button("➕ Eintrag hinzufügen", on_click=add_entry)
col2.button("🔄 Neu", on_click=reset_entries)

st.markdown("---")

# Dynamische Eingabefelder
for i in range(st.session_state.anzahl):
    st.subheader(f"Eintrag {i+1}")
    st.text_input(f"Vorname #{i+1}", key=f"vn_{i}")
    st.text_input(f"Nachname #{i+1}", key=f"nn_{i}")
    st.text_input(f"Telefonnummer #{i+1}", key=f"tel_{i}")

# CSV-Erstellung
if st.button("📥 CSV-Datei erstellen"):
    eintraege = []
    # Sammle Daten
    for i in range(st.session_state.anzahl):
        vor = st.session_state.get(f"vn_{i}", "").strip()
        nah = st.session_state.get(f"nn_{i}", "").strip()
        tel = st.session_state.get(f"tel_{i}", "").strip()
        if not (vor and nah and tel):
            st.error(f"❗ Alle Felder in Eintrag {i+1} ausfüllen.")
            st.stop()
        eintraege.append({"vor": replace_umlauts(vor), "nah": replace_umlauts(nah), "tel": format_phone(tel)})

    # Schreibe CSV
    output = io.StringIO()
    writer = csv.writer(output)
    for e in eintraege:
        row = [e["vor"], e["nah"]] + [""]*16 + ["1","4","1", e["tel"], "-1", "V2"]
        writer.writerow(row)

    st.success("✅ CSV-Datei erfolgreich erstellt!")
    st.download_button(
        label="📄 CSV herunterladen",
        data=output.getvalue(),
        file_name="telefonnummern.csv",
        mime="text/csv"
    )
