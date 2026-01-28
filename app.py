import streamlit as st
import requests
import random

# Sivun asetukset
st.set_page_config(page_title="Tampereen Aikamatka", page_icon="📸", layout="wide")

st.title("📸 Tampereen Aikamatka")
st.write("Valitse alue ja aika tai anna sattuman päättää!")

# --- DATAN ALUSTUS ---
kaupunginosat = [
    "Amuri", "Epilä", "Hatanpää", "Hervanta", "Kaleva", 
    "Keskustori", "Lielahti", "Messukylä", "Nekala", 
    "Pispala", "Pyynikki", "Ratina", "Tammela", "Viinikka"
]

# Alustetaan muisti (Session State) jos se on tyhjä
if 'alue_valinta' not in st.session_state:
    st.session_state.alue_valinta = "Pispala"
if 'vuosi_valinta' not in st.session_state:
    st.session_state.vuosi_valinta = (1900, 1930)

# --- SIVUPALKKI ---
st.sidebar.header("Hakuehdot")

# "YLLÄTÄ MINUT" -NAPPI
if st.sidebar.button("🎲 Yllätä minut!", use_container_width=True):
    # Arvotaan satunnainen alue
    st.session_state.alue_valinta = random.choice(kaupunginosat)
    
    # Arvotaan satunnainen 30 vuoden jakso väliltä 1880-1990
    alku = random.randint(1880, 1990)
    st.session_state.vuosi_valinta = (alku, alku + 30)
    st.rerun() # Päivitetään sivu heti

# Valinnat käyttävät muistissa olevia arvoja
valittu_alue = st.sidebar.selectbox(
    "Valitse alue:", 
    kaupunginosat, 
    index=kaupunginosat.index(st.session_state.alue_valinta)
)

vuodet = st.sidebar.slider(
    "Valitse aikaväli:", 
    min_value=1850, 
    max_value=2025, 
    value=st.session_state.vuosi_valinta
)

# Päivitetään muisti vastaamaan valintoja (jos käyttäjä muuttaa niitä käsin)
st.session_state.alue_valinta = valittu_alue
st.session_state.vuosi_valinta = vuodet

# --- API-HAKU ---
if valittu_alue:
    url = "https://api.finna.fi/v1/search"
    
    params = {
        "lookfor": f'Tampere "{valittu_alue}"',
        "filter[]": [
            'format:0/Image/', 
            'online_boolean:1'
        ],
        "sort": "main_date_str asc", # LAJITTELU: Vanhimmasta uusimpaan
        "limit": 100,
        "field[]": ["title", "images", "year", "buildings", "id"]
    }

    with st.spinner(f"Kurkataan arkistoon: {valittu_alue}..."):
        try:
            res = requests.get(url, params=params)
            data = res.json()
            
            if "records" in data:
                # Suodatetaan tulokset Pythonilla (tuplavarmistus vuodelle)
                valid_records = []
                for r in data["records"]:
                    vuo = r.get("year")
                    if vuo and str(vuo).isdigit():
                        y = int(vuo)
                        if vuodet[0] <= y <= vuodet[1]:
                            valid_records.append(r)
                
                # NÄYTETÄÄN TULOKSET
                if valid_records:
                    st.subheader(f"Löytyi {len(valid_records)} helmeä alueelta {valittu_alue} ({vuodet[0]}–{vuodet[1]})")
                    
                    # Näytetään kuvat siistissä ruudukossa
                    cols = st.columns(3)
                    for idx, record in enumerate(valid_records[:21]):
                        with cols[idx % 3]:
                            img_url = "https://api.finna.fi" + record["images"][0]
                            st.image(img_url, use_container_width=True)
                            
                            vuosi_txt = record.get('year', 'N/A')
                            st.write(f"**{record['title']}** ({vuosi_txt})")
                            
                            if "buildings" in record:
                                lahde = record["buildings"][0].get("translated", "Arkisto")
                                st.caption(f"Lähde: {lahde}")
                            
                            # Linkki Finnan sivuille
                            st.caption(f"[Näytä Finnassa](https://finna.fi/Record/{record['id']})")
                            st.divider()
                else:
                    st.warning(f"Ei osumia väliltä {vuodet[0]}-{vuodet[1]}. Kokeile onneasi uudelleen tai muuta vuosia!")
            
        except Exception as e:
            st.error(f"Yhteysvirhe: {e}")

st.sidebar.markdown("---")
st.sidebar.caption("Data haetaan livenä Finna.fi-rajapinnasta.")
