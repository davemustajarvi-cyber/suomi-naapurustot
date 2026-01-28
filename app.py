import streamlit as st
import requests

st.set_page_config(page_title="Tampereen Aikamatka", page_icon="📸", layout="wide")

# --- APUFUNKTIO: Haetaan kaupunginosat livenä ---
@st.cache_data # Tallentaa listan muistiin, ettei sitä haeta joka kerta uudestaan
def hae_kaupunginosat():
    url = "https://api.finna.fi/v1/facets"
    params = {
        "lookfor": "Tampere",
        "facet[]": "geographic_facet", # Pyydetään maantieteelliset paikat
        "limit": 0 # Emme tarvitse itse tietueita, vain fasetit
    }
    try:
        res = requests.get(url, params=params)
        data = res.json()
        paikat = [f['value'] for f in data['facets']['geographic_facet']]
        
        # Suodatetaan pois liian yleiset sanat, jotta jäljelle jää kaupunginosat
        estolista = ["Tampere", "Suomi", "Pirkanmaa", "Tampereen seutu", "Pirkkala"]
        siivottu_lista = [p for p in paikat if p not in estolista]
        
        return sorted(siivottu_lista)
    except:
        # Jos haku epäonnistuu, palautetaan pieni varalista
        return ["Pispala", "Pyynikki", "Hervanta", "Tammela", "Amuri"]

# --- KÄYTTÖLIITTYMÄ ---
st.title("📸 Tampereen Aikamatka")
st.write("Kaupunginosat haetaan livenä Finna.fi-arkistosta.")

# Haetaan dynaaminen lista
kaupunginosat = hae_kaupunginosat()

# Sivupalkki
st.sidebar.header("Hakuehdot")
valittu_alue = st.sidebar.selectbox("Valitse alue:", kaupunginosat)

vuodet = st.sidebar.slider(
    "Valitse aikaväli:", 
    min_value=1850, 
    max_value=2025, 
    value=(1900, 1920)
)

# --- API-HAKU ---
if valittu_alue:
    api_url = "https://api.finna.fi/v1/search"
    params = {
        "lookfor": f'Tampere "{valittu_alue}"',
        "filter[]": ['format:0/Image/', 'online_boolean:1'],
        "sort": "main_date_str asc",
        "limit": 100,
        "field[]": ["title", "images", "year", "buildings", "id"]
    }

    with st.spinner(f"Haetaan kuvia: {valittu_alue}..."):
        try:
            response = requests.get(api_url, params=params)
            data = response.json()
            
            if "records" in data:
                # Vuosisuodatus Pythonilla
                valid_records = []
                for r in data["records"]:
                    vuo = r.get("year")
                    if vuo and str(vuo).isdigit():
                        y = int(vuo)
                        if vuodet[0] <= y <= vuodet[1]:
                            valid_records.append(r)
                
                if valid_records:
                    st.subheader(f"Löytyi {len(valid_records)} kuvaa väliltä {vuodet[0]}–{vuodet[1]}")
                    cols = st.columns(3)
                    for idx, record in enumerate(valid_records[:30]):
                        with cols[idx % 3]:
                            img_url = "https://api.finna.fi" + record["images"][0]
                            st.image(img_url, use_container_width=True)
                            st.write(f"**{record['title']}** ({record.get('year')})")
                            st.caption(f"Lähde: {record['buildings'][0]['translated'] if 'buildings' in record else 'Arkisto'}")
                            st.divider()
                else:
                    st.warning("Ei kuvia tällä aikavälillä.")
            else:
                st.info("Ei tuloksia.")
        except Exception as e:
            st.error(f"Virhe: {e}")
