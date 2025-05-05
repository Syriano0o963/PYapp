import streamlit as st
import csv, io

# ——— Hilfsfunktionen ———
def format_phone(phone):
    return "0"+phone if phone.startswith("0") else phone

def replace_umlauts(text):
    for o, r in {"ä":"ae","ö":"oe","ü":"ue","Ä":"Ae","Ö":"Oe","Ü":"Ue","ß":"ss"}.items():
        text = text.replace(o, r)
    return text

# ——— Reset‑Callback ———
def reset_and_refresh():
    # alle user‑Keys löschen
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    # Seite neu laden
    st.experimental_rerun()

# ——— UI ———
st.image("logo.png", width=200)
st.title("📞 CSV‑Generator")

# ganz oben: “Neu”‑Button
st.button("🔄 Neu", on_click=reset_and_refresh)

with st.form("form", clear_on_submit=False):
    anzahl = st.number_input("Anzahl Einträge", min_value=1, max_value=100, step=1, key="anzahl")
    eintraege = []
    for i in range(anzahl):
        vor = st.text_input(f"Vorname {i+1}", key=f"vn{i}")
        nach = st.text_input(f"Nachname {i+1}", key=f"nn{i}")
        tel = st.text_input(f"Telefon {i+1}", key=f"tel{i}")
        eintraege.append({"vor":vor,"nach":nach,"tel":tel})
    submitted = st.form_submit_button("📥 CSV erstellen")

if submitted:
    if all(e["vor"] and e["nach"] and e["tel"] for e in eintraege):
        buf=io.StringIO(); wr=csv.writer(buf)
        for e in eintraege:
            wr.writerow([
                replace_umlauts(e["vor"]), replace_umlauts(e["nach"])
            ] + [""]*16 + ["1","4","1", format_phone(e["tel"]),"-1","V2"])
        st.success("CSV fertig!")
        st.download_button("Download CSV", data=buf.getvalue(),
                           file_name="telefon.csv", mime="text/csv")
    else:
        st.error("Bitte alle Felder ausfüllen.")
