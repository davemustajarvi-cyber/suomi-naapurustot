import streamlit as st
import requests
import urllib.parse  # Tarvitaan linkkien korjaamiseen

# 1. Sivun asetukset
st.set_page_config(page_title="Tampereen Aikamatka", page_icon="📸", layout="wide")

st.title("📸 Tampereen Aikamatka")
st.write("Selaa historiallisia kuvia kaupunginosittain. Linkit vievät nyt oikeisiin arkistosivuihin.")

# --- KATTAVA LISTA KAUPUNGINOSISTA (Lisätty Peltolammi ym.) ---
kaupunginosat = sorted([
    "Aitolahti", "Amuri", "Annala", "Atala", "Epilä", "Finlayson", "Hallila", 
    "Hatanpää", "Haukiluoma", "Hervanta", "Hiedanranta", "Holvasti", "Hyhky", 
    "Härmälä", "Ikuri", "Järvensivu", "Kaleva", "Kaukajärvi", "Kauppi", "Keskustori", 
    "Kissanmaa", "Koivistonkylä", "Korkinmäki", "Kyttälä", "Kämmenniemi", "Lappi", 
    "Leinola", "Lentävänniemi", "Lielahti", "Linnainmaa", "Lukonmäki", "Messukylä", 
    "Multisilta", "Muotiala", "Nekala", "Niemi", "Niihama", "Nirva", "Pappila", 
    "Peltolammi", "Petsamo", "Pispala", "Pohtola", "Pyynikki", "Rahola", "Ratina", 
    "Rautaharkko", "Ruotula", "Rusko", "Santalahti", "Sarankulma", "Särkänniemi", 
    "Takahuhti", "Tahmela", "Tammela", "Tammerkoski", "Tampella", "Tesoma", 
    "Tohloppi", "Tulli", "Turtola", "Uusikylä", "Vehmainen", "Viiala", "Viinikka", 
    "Villilä", "Vuores", "Vuohenoja"
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
    
    # Haetaan kuvat (sort: main_date_str asc varmistaa vanhimmat kuvat ensin)
    params = {
        "lookfor": f'Tampere "{valittu_alue}"',
        "filter[]": ['format:0/Image/', 'online_boolean:1'],
        "sort": "main_date_str asc",
        "limit": 100,
        "field[]": ["title", "images", "year", "buildings", "id"]
    }

    with st.spinner(f"Haetaan kuvia: {valittu_alue}..."):
        try:
            res = requests.get(api_url, params=params)
            data = res.json()
            
            if "records" in data:
                # Tiukka vuosisuodatus Pythonissa
                naytettavat = []
                for r in data["records"]:
                    vuo = r.get("year")
                    if vuo and str(vuo).isdigit():
                        y = int(vuo)
                        if vuodet[0] <= y <= vuodet[1]:
                            naytettavat.append(r)
                
                # Tulosten näyttäminen
                if naytettavat:
                    st.subheader(f"Löytyi {len(naytettavat)} kuvaa väliltä {vuodet[0]}–{vuodet[1]}")
                    
                    cols = st.columns(3)
                    for idx, record in enumerate(naytettavat[:30]):
                        with cols[idx % 3]:
                            img_url = "https://api.finna.fi" + record["images"][0]
                            st.image(img_url, use_container_width=True)
                            
                            vuosi_txt = record.get('year', 'N/A')
                            st.write(f"**{record['title']}** ({vuosi_txt})")
                            
                            # Lähdetiedot
                            lahde = record['buildings'][0]['translated'] if 'buildings' in record else "Arkisto"
                            
                            # LINKIN KORJAUS: Koodataan ID niin, että se toimii selaimessa
                            # Tämä muuttaa esim. kaksoispisteet muotoon %3A
                            encoded_id = urllib.parse.quote(record['id'], safe='')
                            finna_link = f"https://finna.fi/Record/{encoded_id}"
                            
                            st.caption(f"Lähde: {lahde} | [Katso Finnassa]({finna_link})")
                            st.divider()
                else:
                    st.warning(f"Ei löytynyt kuvia vuosilta {vuodet[0]}-{vuodet[1]}.")
            else:
                st.info("Hakusanalla ei löytynyt kuvia.")
                
        except Exception as e:
            st.error(f"Yhteysvirhe: {e}")

st.sidebar.markdown("---")
st.sidebar.caption("Data: Finna.fi API")
