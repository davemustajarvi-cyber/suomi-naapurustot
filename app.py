import streamlit as st
import requests

# 1. Sivun asetukset
st.set_page_config(page_title="Tampereen Aikamatka", page_icon="📸", layout="wide")

st.title("📸 Tampereen Aikamatka")
st.write("Selaa historiallisia kuvia kaupunginosittain.")

# --- KATTAVA LISTA KAUPUNGINOSISTA (Kovakoodattu varmuuden vuoksi) ---
kaupunginosat = sorted([
    "Aitolahti", "Amuri", "Annala", "Atala", "Epilä", "Finlayson", "Hallila", 
    "Hatanpää", "Haukiluoma", "Hervanta", "Hiedanranta", "Holvasti", "Hyhky", 
    "Härmälä", "Ikuri", "Järvensivu", "Kaleva", "Kaukajärvi", "Kauppi", "Keskustori", 
    "Kissanmaa", "Koivistonkylä", "Korkinmäki", "Kyttälä", "Kämmenniemi", "Lappi", 
    "Leinola", "Lentävänniemi", "Lielahti", "Linnainmaa", "Lukonmäki", "Messukylä", 
    "Multisilta", "Muotiala", "Nekala", "Niemi", "Niihama", "Nirva", "Pappila", 
    "Petsamo", "Pispala", "Pohtola", "Pyynikki", "Rahola", "Ratina", "Rautaharkko", 
    "Ruotula", "Rusko", "Santalahti", "Sarankulma", "Särkänniemi", "Takahuhti", 
    "Tahmela", "Tammela", "Tammerkoski", "Tampella", "Tesoma", "Tohloppi", "Tulli", 
    "Turtola", "Uusikylä", "Vehmainen", "Viiala", "Viinikka", "Villilä", "Vuores"
])

# --- SIVUPALKKI ---
st.sidebar.header("Hakuehdot")
valittu_alue = st.sidebar.selectbox("Valitse alue:", kaupunginosat)

# Aikasuodatin
vuodet = st.sidebar.slider(
    "Valitse aikaväli:", 
    min_value=1850, 
    max_value=2025, 
    value=(1900, 1930)
)

# --- API-HAKU JA LOGIIKKA ---
if valittu_alue:
    api_url = "https://api.finna.fi/v1/search"
    
    # Haetaan reilusti kuvia (limit 100) ja järjestetään ne vanhimmasta alkaen
    params = {
        "lookfor": f'Tampere "{valittu_alue}"',
        "filter[]": ['format:0/Image/', 'online_boolean:1'],
        "sort": "main_date_str asc",
        "limit": 100,
        "field[]": ["title", "images", "year", "buildings", "id"]
    }

    with st.spinner(f"Etsitään arkistoista: {valittu_alue}..."):
        try:
            res = requests.get(api_url, params=params)
            data = res.json()
            
            if "records" in data:
                # TIUKKA SUODATUS: Tarkistetaan vuosi jokaisesta kuvasta erikseen
                valid_records = []
                for r in data["records"]:
                    vuo = r.get("year")
                    if vuo and str(vuo).isdigit():
                        y = int(vuo)
                        # Vain jos vuosi on TÄSMÄLLEEN valitulla välillä
                        if vuodet[0] <= y <= vuodet[1]:
                            valid_records.append(r)
                
                # Tulosten näyttäminen
                if valid_records:
                    st.subheader(f"Löytyi {len(valid_records)} kuvaa väliltä {vuodet[0]}–{vuodet[1]}")
                    
                    # 3 kuvaa rinnakkain
                    cols = st.columns(3)
                    for idx, record in enumerate(valid_records[:30]):
                        with cols[idx % 3]:
                            img_url = "https://api.finna.fi" + record["images"][0]
                            st.image(img_url, use_container_width=True)
                            
                            vuosi_txt = record.get('year', 'N/A')
                            st.write(f"**{record['title']}** ({vuosi_txt})")
                            
                            if "buildings" in record:
                                lahde = record["buildings"][0].get("translated", "Arkisto")
                                st.caption(f"Lähde: {lahde}")
                            
                            st.caption(f"[Katso Finnassa](https://finna.fi/Record/{record['id']})")
                            st.divider()
                else:
                    st.warning(f"Ei löytynyt kuvia vuosilta {vuodet[0]}-{vuodet[1]}. Kokeile muuttaa aikaväliä!")
            else:
                st.info("Hakusanalla ei löytynyt kuvia.")
                
        except Exception as e:
            st.error(f"Yhteysvirhe: {e}")

st.sidebar.markdown("---")
st.sidebar.caption("Data: Finna.fi API")
