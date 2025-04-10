import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="HTTP Status Checker", layout="wide")
st.title("HTTP Status Checker")

st.markdown("Prüfe den HTTP-Status deiner URL – entweder einzeln oder für mehrere Seiten gleichzeitig.")

def check_url_status(url):
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        history = [(r.status_code, r.url) for r in response.history]
        return {
            "Eingabe-URL": url,
            "Finale URL": response.url,
            "Statuscode": response.status_code,
            "Weiterleitungen": " → ".join([f"{code} {u}" for code, u in history]) if history else "-",
            "Ladezeit (ms)": int(response.elapsed.total_seconds() * 1000)
        }
    except requests.exceptions.RequestException as e:
        return {
            "Eingabe-URL": url,
            "Finale URL": "-",
            "Statuscode": "Fehler",
            "Weiterleitungen": str(e),
            "Ladezeit (ms)": "-"
        }

# Modusauswahl
mode = st.radio("Modus wählen", ["Einzel-Check", "Bulk-Check"])

if mode == "Einzel-Check":
    url = st.text_input("URL eingeben (inkl. https://)", "")
    if st.button("Prüfen") and url:
        result = check_url_status(url)

        st.subheader("Ergebnis")
        st.markdown(f"""
        **Eingabe-URL:** `{result['Eingabe-URL']}`  
        **Finale URL:** `{result['Finale URL']}`  
        **Statuscode:** `{result['Statuscode']}`  
        **Weiterleitungen:** {result['Weiterleitungen']}  
        **Ladezeit:** {result['Ladezeit (ms)']} ms  
        """)

else:
    st.markdown("Mehrere URLs eingeben (eine pro Zeile):")
    bulk_input = st.text_area("URLs", height=200)
    if st.button("Bulk prüfen") and bulk_input:
        urls = [u.strip() for u in bulk_input.splitlines() if u.strip()]
        results = [check_url_status(url) for url in urls]
        df = pd.DataFrame(results)
        st.subheader("Ergebnisse")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Ergebnisse als CSV herunterladen",
            data=csv,
            file_name="http_status_results.csv",
            mime="text/csv"
        )
