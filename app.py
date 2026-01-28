import streamlit as st
import requests

# 1. Sivun asetukset
st.set_page_config(page_title="Tampereen Aikamatka", page_icon="📸", layout="wide")

st.title("📸 Tampereen Aikamatka")
st.write("Valitse kaupunginosa ja aikakausi selataksesi historiallisia kuvia.")

# --- SIVUPALKKI ---
st.sidebar.header("Hakuehdot")

# 2. Kattava lista Tampereen kaupunginosista
kaupunginosat = sorted([
    "Aitolahti", "Amuri", "Annala", "Atala", "Epilä", "Finlayson", "Hallila", 
    "Hatanpää", "Haukiluoma", "Hervanta", "Hyhky", "Härmälä", "Ikuri", "Järvensivu", 
    "Kaleva", "Kaukajärvi", "Kauppi", "Keskustori", "Koivistonkylä", "Kämmenniemi", 
    "Lappi", "Leinola", "Lielahti", "Linnainmaa", "Lukonmäki", "Messukylä", "Multisilta", 
    "Nalkala", "Nekala", "Niemenranta", "Niihama", "Nirva", "Pappila", "Petsamo", 
    "Pispala", "Pohtola", "Pyynikki", "Rahola", "Ratina", "Rautaharkko", "Ruotula", 
    "Santalahti", "Sarankulma", "Takahuhti", "Tahmela", "Tammela", "Tammerkoski", 
    "Tampella", "Tesoma", "Tohloppi", "Tulli", "Uusikylä", "Vehmainen", "Viinikka"
])

valittu_alue = st.sidebar.selectbox("Valitse alue:", kaupunginosat)

# 3. Aikasuodatin (Slider)
vuodet = st.sidebar.slider(
    "Valitse aikaväli:", 
    min_value=1850, 
    max_value=2025, 
    value=(1900, 1920) # Oletuksena vanha Tampere
)

# --- API-HAKU JA NÄYTTÄMINEN ---
if valittu_alue:
    url = "https://api.finna.fi/v1/search"
    
    # Hakuparametrit
    params = {
        "lookfor": f'Tampere "{valittu_alue}"',
        "filter[]": [
            'format:0/Image/', 
            'online_boolean:1'
        ],
        "sort": "main_date_str asc", # Järjestetään vanhimmasta alkaen
        "limit": 100,
        "field[]": ["title", "images", "year", "buildings", "id"]
    }

    with st.spinner("Haetaan kuvia arkistoista..."):
        try:
            res = requests.get(url, params=params)
            data = res.json()
            
            if "records" in data:
                # TOIMIVA AIKASUODATUS:
                # Käydään tulokset läpi ja näytetään vain ne, joiden vuosi on valitulla välillä
                valid_records = []
                for r in data["records"]:
                    vuo_str = r.get("year")
                    if vuo_str and str(vuo_str).isdigit():
                        vuo_int = int(vuo_str)
                        if vuodet[0] <= vuo_int <= vuodet[1]:
                            valid_records.append(r)
                
                # Tulosten näyttäminen
                if valid_records:
                    st.subheader(f"Löytyi {len(valid_records)} kuvaa alueelta {valittu_alue} ({vuodet[0]}–{vuodet[1]})")
                    
                    cols = st.columns(3)
                    for idx, record in enumerate(valid_records[:30]): # Näytetään max 30 kuvaa kerralla
                        with cols[idx % 3]:
                            img_url = "https://api.finna.fi" + record["images"][0]
                            st.image(img_url, use_container_width=True)
                            
                            vuosi = record.get('year', 'N/A')
                            st.write(f"**{record['title']}** ({vuosi})")
                            
                            if "buildings" in record:
                                lahde = record["buildings"][0].get("translated", "Arkisto")
                                st.caption(f"Lähde: {lahde}")
                            st.divider()
                else:
                    st.warning(f"Ei löytynyt kuvia väliltä {vuodet[0]}-{vuodet[1]}. Kokeile muuttaa aikaväliä!")
            else:
                st.info("Kuvia ei löytynyt. Kokeile toista kaupunginosaa.")
                
        except Exception as e:
            st.error(f"Yhteysvirhe: {e}")

st.sidebar.markdown("---")
st.sidebar.caption("Data: Finna.fi API")
