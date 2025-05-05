import streamlit as st
import csv
import io

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

st.title("📞 CSV-Telefonnummern-Generator")

anzahl = st.number_input("Wie viele Einträge möchtest du erfassen?", min_value=1, max_value=100, step=1)

eintraege = []

for i in range(anzahl):
    st.subheader(f"Eintrag {i + 1}")
    vorname = st.text_input(f"Vorname #{i + 1}", key=f"vn_{i}")
    nachname = st.text_input(f"Nachname #{i + 1}", key=f"nn_{i}")
    telefon = st.text_input(f"Telefonnummer #{i + 1}", key=f"tel_{i}")

    if vorname and nachname and telefon:
        eintraege.append({
            "vorname": replace_umlauts(vorname),
            "nachname": replace_umlauts(nachname),
            "telefon": format_phone(telefon)
        })

if len(eintraege) == anzahl and anzahl > 0:
    if st.button("📥 CSV-Datei erstellen"):
        output = io.StringIO()
        writer = csv.writer(output)

        for eintrag in eintraege:
            zeile = [eintrag["vorname"], eintrag["nachname"]] + [""] * 16 + ["1", "4", "1", eintrag["telefon"], "-1", "V2"]
            writer.writerow(zeile)

        st.success("✅ CSV-Datei erfolgreich erstellt!")
        st.download_button(
            label="📄 CSV herunterladen",
            data=output.getvalue(),
            file_name="telefonnummern.csv",
            mime="text/csv"
        )
