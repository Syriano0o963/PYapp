import streamlit as st
import csv
import io

# ----------- Hilfsfunktionen ------------
def format_phone(phone):
    return "0" + phone if phone.startswith("0") else phone

def replace_umlauts(text):
    replacements = {
        "ä": "ae", "ö": "oe", "ü": "ue",
        "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
        "ß": "ss"
    }
    for original, replaced in replacements.items():
        text = text.replace(original, replaced)
    return text

# ----------- Firmenlogo anzeigen ------------
st.image("logo.png", width=200)  # Logo-Datei im gleichen Ordner

st.title("📞 CSV-Telefonnummern-Generator")

# ----------- SessionState zurücksetzen ------------
def reset_app():
    for key in st.session_state.keys():
        del st.session_state[key]

# Reset-Button
if st.button("🔁 Alles zurücksetzen"):
    reset_app()
    st.experimental_rerun()

# ----------- Formular ------------
st.subheader("➕ Neue Telefonnummern eingeben")

with st.form("telefon_formular", clear_on_submit=False):
    anzahl = st.number_input("Wie viele Einträge möchtest du erfassen?", min_value=1, max_value=100, step=1, key="anzahl")

    eintraege = []
    for i in range(anzahl):
        st.markdown(f"**Eintrag {i + 1}**")
        vorname = st.text_input(f"Vorname #{i + 1}", key=f"vn_{i}")
        nachname = st.text_input(f"Nachname #{i + 1}", key=f"nn_{i}")
        telefon = st.text_input(f"Telefonnummer #{i + 1}", key=f"tel_{i}")

        eintraege.append({
            "vorname": vorname,
            "nachname": nachname,
            "telefon": telefon
        })

    submitted = st.form_submit_button("📥 CSV-Datei erstellen")

# ----------- CSV exportieren ------------
if submitted:
    if all(e["vorname"] and e["nachname"] and e["telefon"] for e in eintraege):
        output = io.StringIO()
        writer = csv.writer(output)

        for eintrag in eintraege:
            zeile = [
                replace_umlauts(eintrag["vorname"]),
                replace_umlauts(eintrag["nachname"])
            ] + [""] * 16 + [
                "1", "4", "1", format_phone(eintrag["telefon"]), "-1", "V2"
            ]
            writer.writerow(zeile)

        st.success("✅ CSV-Datei erfolgreich erstellt!")
        st.download_button(
            label="📄 CSV herunterladen",
            data=output.getvalue(),
            file_name="telefonnummern.csv",
            mime="text/csv"
        )
    else:
        st.error("❗ Bitte alle Felder ausfüllen, bevor du die CSV erstellst.")
