import streamlit as st
import requests

st.set_page_config(page_title="Tampereen Aikamatka", page_icon="📸", layout="wide")

st.title("📸 Tampereen Aikamatka")
st.write("Valitse kaupunginosa ja aikaväli. Koodi suodattaa kuvat puolestasi.")

# --- SIVUPALKKI ---
st.sidebar.header("Hakuehdot")

kaupunginosat = [
    "Amuri", "Epilä", "Hatanpää", "Hervanta", "Kaleva", 
    "Keskustori", "Lielahti", "Messukylä", "Nekala", 
    "Pispala", "Pyynikki", "Ratina", "Tammela", "Viinikka"
]
valittu_alue = st.sidebar.selectbox("Alue:", kaupunginosat)

# Laajennetaan aikaväliä oletuksena
vuodet = st.sidebar.slider(
    "Aikaväli:", 
    min_value=1850, 
    max_value=2025, 
    value=(1900, 1930)
)

# --- API-HAKU ---
if valittu_alue:
    url = "https://api.finna.fi/v1/search"
    
    # Haetaan kuvat mahdollisimman laajasti, jotta voimme suodattaa ne itse
    params = {
        "lookfor": f"Tampere {valittu_alue}",
        "filter[]": ['format:0/Image/', 'online_boolean:1'],
        "limit": 100,
        "field[]": ["title", "images", "year", "buildings", "id"]
    }

    with st.spinner("Haetaan arkistoja..."):
        try:
            res = requests.get(url, params=params)
            data = res.json()
            
            if "records" in data:
                # --- TIUKKA SUODATUS PYTHONISSA ---
                valid_records = []
                for r in data["records"]:
                    vuo = r.get("year")
                    if vuo and str(vuo).isdigit():
                        y = int(vuo)
                        # TÄSSÄ TAPAHTUU TAIKA: Vain valitut vuodet pääsevät läpi
                        if vuodet[0] <= y <= vuodet[1]:
                            valid_records.append(r)
                
                # NÄYTETÄÄN TULOKSET
                if valid_records:
                    st.subheader(f"Löytyi {len(valid_records)} kuvaa väliltä {vuodet[0]}–{vuodet[1]}")
                    cols = st.columns(3)
                    for idx, record in enumerate(valid_records[:21]):
                        with cols[idx % 3]:
                            img_url = "https://api.finna.fi" + record["images"][0]
                            st.image(img_url, use_container_width=True)
                            st.write(f"**{record['title']}** ({record.get('year')})")
                            st.divider()
                else:
                    st.warning(f"Ei löytynyt kuvia väliltä {vuodet[0]}-{vuodet[1]}. Kokeile muuttaa vuosilukuja!")
            else:
                st.info("Alueelta ei löytynyt kuvia. Kokeile esim. Pispalaa tai Tammelaa.")
                
        except Exception as e:
            st.error(f"Yhteysvirhe: {e}")
