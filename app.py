import streamlit as st
import requests

st.set_page_config(page_title="Tampereen Aikamatka", page_icon="📸", layout="wide")

st.title("📸 Tampereen Aikamatka")
st.write("Valitse kaupunginosa ja aikakausi kurkistatksesi menneisyyteen.")

# --- SIVUPALKKI / VALINNAT ---
st.sidebar.header("Hakuehdot")

# 1. Kaupunginosat
kaupunginosat = [
    "Amuri", "Epilä", "Hatanpää", "Hervanta", "Järvensivu", 
    "Kaleva", "Keskustori", "Lielahti", "Messukylä", "Nekala", 
    "Pispala", "Pyynikki", "Ratina", "Tammela", "Viinikka"
]
valittu_alue = st.sidebar.selectbox("Valitse alue:", kaupunginosat)

# 2. Vuosisuodatin (Slider)
# Alkuarvona (1900, 1960)
vuodet = st.sidebar.slider(
    "Valitse aikaväli:", 
    min_value=1850, 
    max_value=2025, 
    value=(1900, 1960)
)

# --- API-HAKU ---
if valittu_alue:
    url = "https://api.finna.fi/v1/search"
    
    # Muodostetaan parametrit
    params = {
        "lookfor": f'Tampere "{valittu_alue}"',
        "filter[]": [
            'format:0/Image/',
            'online_boolean:1',
            f'search_daterange_mv:["{vuodet[0]}-{vuodet[1]}"]' # AIKASUODATIN
        ],
        "limit": 24,
        "field[]": ["title", "images", "year", "buildings", "id"]
    }

    with st.spinner(f"Etsitään kuvia: {valittu_alue}, vuodet {vuodet[0]}-{vuodet[1]}..."):
        response = requests.get(url, params=params)
        data = response.json()

    # --- TULOSTEN NÄYTTÄMINEN ---
    if "records" in data and data["records"]:
        st.subheader(f"Löytyi {data['resultCount']} kuvaa ajalta {vuodet[0]}–{vuodet[1]}")
        
        # Näytetään kuvat ruudukkona (3 kuvaa rinnakkain)
        cols = st.columns(3)
        for idx, record in enumerate(data["records"]):
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
        st.warning(f"Ei löytynyt kuvia valitulla aikavälillä {vuodet[0]}–{vuodet[1]}. Kokeile laajempaa haku-aluetta!")

st.sidebar.markdown("---")
st.sidebar.caption("Data: Finna.fi API")
