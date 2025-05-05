import streamlit as st
import csv, io

# ——— Hilfsfunktionen ———
def format_phone(phone):
    return "0" + phone if phone.startswith("0") else phone

def replace_umlauts(text):
    for o, r in {"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss"}.items():
        text = text.replace(o, r)
    return text

# ——— Session State initialisieren ———
if "anzahl" not in st.session_state:
    st.session_state["anzahl"] = 1

# ——— UI ———
st.image("logo.png", width=200)
st.title("📞 CSV‑Telefonnummern‑Generator")

# Steuerung der Anzahl mit Buttons und Input
col1, col2, col3 = st.columns([1,2,1])
with col1:
    if st.button("➖", key="minus") and st.session_state["anzahl"] > 1:
        st.session_state["anzahl"] -= 1
with col2:
    st.number_input(
        "Anzahl Einträge",
        min_value=1,
        max_value=100,
        step=1,
        key="anzahl",
        label_visibility="collapsed"
    )
with col3:
    if st.button("➕", key="plus"):
        st.session_state["anzahl"] += 1

# Dynamische Eingabefelder
entries = []
for i in range(st.session_state["anzahl"]):
    st.subheader(f"Eintrag {i+1}")
    vor = st.text_input(f"Vorname {i+1}", key=f"vn_{i}")
    nah = st.text_input(f"Nachname {i+1}", key=f"nn_{i}")
    tel = st.text_input(f"Telefon {i+1}", key=f"tel_{i}")
    entries.append({"vor": vor, "nach": nah, "tel": tel})

# CSV erstellen
if st.button("📥 CSV erstellen"):
    if all(e["vor"] and e["nach"] and e["tel"] for e in entries):
        buf = io.StringIO()
        writer = csv.writer(buf)
        for e in entries:
            writer.writerow([
                replace_umlauts(e["vor"]),
                replace_umlauts(e["nach"])
            ] + [""] * 16 + ["1", "4", "1", format_phone(e["tel"]), "-1", "V2"])
        st.success("✅ CSV-Datei erfolgreich erstellt!")
        st.download_button(
            label="📄 CSV herunterladen",
            data=buf.getvalue(),
            file_name="telefonnummern.csv",
            mime="text/csv"
        )
    else:
        st.error("❗ Bitte alle Felder ausfüllen.")
