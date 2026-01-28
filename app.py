import streamlit as st
import requests

st.set_page_config(page_title="Tampereen Aikamatka", page_icon="📸", layout="wide")

# --- APUFUNKTIO: Haetaan kaupunginosat livenä + Varalista ---
@st.cache_data
def hae_alueet():
    # Perusteellinen varalista (sisältää Peltolammin ja kymmeniä muita)
    varalista = sorted([
        "Amuri", "Annala", "Atala", "Epilä", "Finlayson", "Hatanpää", "Haukiluoma", 
        "Hervanta", "Hiedanranta", "Hyhky", "Härmälä", "Ikuri", "Järvensivu", 
        "Kaleva", "Kaukajärvi", "Kauppi", "Keskustori", "Kissanmaa", "Koivistonkylä", 
        "Kyttälä", "Lappi", "Leinola", "Lielahti", "Linnainmaa", "Lukonmäki", 
        "Messukylä", "Multisilta", "Nekala", "Niemi", "Pappila", "Peltolammi", 
        "Petsamo", "Pispala", "Pohtola", "Pyynikki", "Rahola", "Ratina", 
        "Rautaharkko", "Ruotula", "Santalahti", "Sarankulma", "Särkänniemi", 
        "Takahuhti", "Tahmela", "Tammela", "Tammerkoski", "Tampella", "Tesoma", 
        "Tohloppi", "Tulli", "Uusikylä", "Vehmainen", "Viinikka", "Vuores"
    ])
    
    try:
        # Yritetään hakea fasetit Tampereen museoiden kokoelmista
        url = "https://api.finna.fi/v1/facets"
        params = {
            "lookfor": 'building:"0/Tampereen historialliset museot/"',
            "facet[]": "geographic_facet",
            "limit": 0
        }
        res = requests.get(url, params=params, timeout=5)
        data = res.json()
        api_paikat = [f['value'] for f in data['facets']['geographic_facet']]
        
        # Yhdistetään listat ja poistetaan duplikaatit
        yhdistetty = list(set(varalista + api_paikat))
        # Siivotaan pois liian yleiset termit
        estolista = ["Suomi", "Tampere", "Pirkanmaa", "Tampereen seutu"]
        lopullinen = [p for p in yhdistetty if p not in estolista and len(p) > 2]
        return sorted(lopullinen)
    except:
        return varalista

# --- KÄYTTÖLIITTYMÄ ---
st.title("📸 Tampereen Aikamatka")
st.write("Selaa arkistojen aarteita kaupunginosittain.")

alueet = hae_alueet()

# Sivupalkki
st.sidebar.header("Hakuehdot")
valittu_alue = st.sidebar.selectbox("Valitse alue:", alueet, index=alueet.index("Pispala") if "Pispala" in alueet else 0)

vuodet = st.sidebar.slider(
    "Valitse aikaväli:", 
    min_value=1850, 
    max_value=2025, 
    value=(1900, 1930)
)

# --- API-HAKU ---
if valittu_alue:
    api_url = "https://api.finna.fi/v1/search"
    params = {
        "lookfor": f'Tampere "{valittu_alue}"',
        "filter[]": ['format:0/Image/', 'online_boolean:1'],
        "sort": "main_date_str asc", # Tärkeä: hakee vanhimmat ensin
        "limit": 100,
        "field[]": ["title", "images", "year", "buildings", "id"]
    }

    with st.spinner(f"Haetaan kuvia: {valittu_alue}..."):
        try:
            response = requests.get(api_url, params=params)
            data = response.json()
            
            if "records" in data:
                # TIUKKA VUOSISUODATUS PYTHONISSA
                naytettavat = []
                for r in data["records"]:
                    vuo = r.get("year")
                    if vuo and str(vuo).isdigit():
                        y = int(vuo)
                        if vuodet[0] <= y <= vuodet[1]:
                            naytettavat.append(r)
                
                if naytettavat:
                    st.subheader(f"Löytyi {len(naytettavat)} kuvaa väliltä {vuodet[0]}–{vuodet[1]}")
                    
                    # Ruudukko: 3 saraketta
                    cols = st.columns(3)
                    for idx, record in enumerate(naytettavat[:30]):
                        with cols[idx % 3]:
                            img_url = "https://api.finna.fi" + record["images"][0]
                            st.image(img_url, use_container_width=True)
                            st.write(f"**{record['title']}** ({record.get('year')})")
                            
                            lahde = record['buildings'][0]['translated'] if 'buildings' in record else "Arkisto"
                            st.caption(f"Lähde: {lahde} | [Finna](https://finna.fi/Record/{record['id']})")
                            st.divider()
                else:
                    st.warning(f"Ei kuvia väliltä {vuodet[0]}-{vuodet[1]}. Kokeile siirtää aikajanaa!")
            else:
                st.info("Tällä hakusanalla ei löytynyt kuvia.")
        except Exception as e:
            st.error(f"Yhteysvirhe: {e}")

st.sidebar.markdown("---")
st.sidebar.caption(f"Löydetty {len(alueet)} eri paikkaa/hakusanaa.")
