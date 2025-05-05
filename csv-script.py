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

# ——— Callback-Funktionen ———
def increment_anzahl():
    st.session_state["anzahl"] += 1

def decrement_anzahl():
    if st.session_state["anzahl"] > 1:
        st.session_state["anzahl"] -= 1

def reset_fields():
    # Anzahl zurücksetzen
    st.session_state["anzahl"] = 1
    # alle Eingabefelder löschen
    for key in list(st.session_state.keys()):
        if key.startswith(("vn_", "nn_", "tel_")):
            del st.session_state[key]

# ——— UI ———
st.image("logo.png", width=200)
st.title("📞 CSV‑Generator mit dynamischer Anzahl")

# Reset-Button
st.button("🔄 Neu", on_click=reset_fields)

# Steuerung der Anzahl per Buttons und Number Input in einer Zeile
col_minus, col_input, col_plus = st.columns([1, 2, 1])
with col_minus:
    st.button("－", on_click=decrement_anzahl)
with col_input:
    st.number_input(
        "Anzahl Einträge", min_value=1, max_value=100, step=1,
        key="anzahl", label_visibility="collapsed"
    )
with col_plus:
    st.button("＋", on_click=increment_anzahl)

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

# ——— CSV Export ———
if submitted:
    if all(e["vor"] and e["nach"] and e["tel"] for e in eintraege):
        buf = io.StringIO()
        wr = csv.writer(buf)
        for e in eintraege:
            wr.writerow(
                [replace_umlauts(e["vor"]), replace_umlauts(e["nach"])]
                + [""] * 16 + ["1", "4", "1", format_phone(e["tel"]), "-1", "V2"]
            )
        st.success("✅ CSV fertig!")
        st.download_button(
            "Download CSV", data=buf.getvalue(),
            file_name="telefon.csv", mime="text/csv"
        )
    else:
        st.error("❗ Bitte alle Felder ausfüllen.")
