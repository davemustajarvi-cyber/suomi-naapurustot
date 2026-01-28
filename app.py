import streamlit as st
import requests

# Sivun asetukset
st.set_page_config(page_title="Tampereen Aikamatka", page_icon="📸", layout="wide")

st.title("📸 Tampereen Aikamatka")
st.write("Valitse kaupunginosa ja aikakausi kurkistatksesi menneisyyteen.")

# --- SIVUPALKKI ---
st.sidebar.header("Hakuehdot")

kaupunginosat = [
    "Amuri", "Epilä", "Hatanpää", "Hervanta", "Järvensivu", 
    "Kaleva", "Keskustori", "Lielahti", "Messukylä", "Nekala", 
    "Pispala", "Pyynikki", "Ratina", "Tammela", "Viinikka"
]
valittu_alue = st.sidebar.selectbox("Valitse alue:", kaupunginosat)

# Vuosisuodatin
vuodet = st.sidebar.slider(
    "Valitse aikaväli:", 
    min_value=1850, 
    max_value=2025, 
    value=(1900, 1916)
)

# --- API-HAKU JA LOGIIKKA ---
if valittu_alue:
    url = "https://api.finna.fi/v1/search"
    
    # Tarkka haku API:sta
    params = {
        "lookfor": f'Tampere "{valittu_alue}"',
        "filter[]": [
            'format:0/Image/',
            'online_boolean:1',
            f'daterange:[{vuodet[0]} TO {vuodet[1]}]'
        ],
        "limit": 100,
        "field[]": ["title", "images", "year", "buildings", "id"]
    }

    with st.spinner("Haetaan arkistoja..."):
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if "records" in data and data["records"]:
                # TUPLAVARMISTUS: Suodatetaan tulokset vielä Pythonilla
                valid_records = []
                for r in data["records"]:
                    year_str = r.get("year")
                    if year_str and year_str.isdigit():
                        y = int(year_str)
                        # Vain jos vuosi on todella valitulla välillä
                        if vuodet[0] <= y <= vuodet[1]:
                            valid_records.append(r)
                
                # NÄYTETÄÄN TULOKSET
                st.subheader(f"Löytyi {len(valid_records)} tarkkaa osumaa väliltä {vuodet[0]}–{vuodet[1]}")
                
                if valid_records:
                    cols = st.columns(3)
                    for idx, record in enumerate(valid_records[:24]):
                        with cols[idx % 3]:
                            if "images" in record:
                                img_url = "https://api.finna.fi" + record["images"][0]
                                st.image(img_url, use_container_width=True)
                            
                            vuosi = record.get("year", "N/A")
                            st.write(f"**{record['title']}** ({vuosi})")
                            
                            if "buildings" in record:
                                lahde = record["buildings"][0].get("translated", "Arkisto")
                                st.caption(f"Lähde: {lahde}")
                            st.divider()
                else:
                    st.warning("Ei löytynyt kuvia, joiden vuosiluku täsmäisi valittuun aikaväliin.")
            else:
                st.info("Finna ei palauttanut tuloksia näillä hakuehdoilla.")
                
        except Exception as e:
            st.error(f"Yhteysvirhe: {e}")

st.sidebar.markdown("---")
st.sidebar.caption("Data: Finna.fi API")
