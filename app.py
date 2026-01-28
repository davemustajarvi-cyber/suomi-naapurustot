import streamlit as st
import requests

st.set_page_config(page_title="Tampereen Aikamatka", page_icon="📸")

st.title("📸 Tampereen Aikamatka")
st.write("Valitse kaupunginosa ja kurkista menneisyyteen. Kuvat haetaan livenä Finna.fi-arkistosta.")

# 1. Tampereen kaupunginosia
kaupunginosat = [
    "Amuri", "Epilä", "Hatanpää", "Hervanta", "Järvensivu", 
    "Kaleva", "Keskustori", "Lielahti", "Messukylä", "Nekala", 
    "Pispala", "Pyynikki", "Ratina", "Tammela", "Viinikka"
]

valittu_alue = st.selectbox("Minkä alueen historiaa katsotaan?", kaupunginosat)

if valittu_alue:
    # Finna API haku
    # lookfor: Hakusanat
    # filter[] format: Vain kuvat
    # filter[] usage_rights: Vapaasti käytettävät (ei-kaupallinen sallittu)
    # limit: Haetaan 20 kuvaa kerralla
    
    url = "https://api.finna.fi/v1/search"
    params = {
        "lookfor": f"Tampere {valittu_alue}",
        "filter[]": [
            'format:0/Image/',
            'usage_rights_str_mv:usage_all' # Vapaasti käytettävät kuvat
        ],
        "limit": 20,
        "field[]": ["title", "images", "year", "buildings", "id"]
    }

    with st.spinner(f"Haetaan kuvia alueelta {valittu_alue}..."):
        response = requests.get(url, params=params)
        data = response.json()

    if "records" in data and data["records"]:
        st.success(f"Löytyi {data['resultCount']} kuvaa!")
        
        for record in data["records"]:
            with st.container():
                # Otsikko ja vuosi
                vuosi = record.get("year", "Vuosi tuntematon")
                st.subheader(f"{record['title']} ({vuosi})")
                
                # Kuvan näyttäminen (Finna palauttaa suhteellisen polun)
                if "images" in record:
                    img_url = "https://api.finna.fi" + record["images"][0]
                    st.image(img_url, use_container_width=True)
                
                # Lähdetiedot
                if "buildings" in record:
                    lahde = record["buildings"][0].get("translated", "Tuntematon arkisto")
                    st.caption(f"Lähde: {lahde} | [Katso Finnassa](https://finna.fi/Record/{record['id']})")
                
                st.markdown("---")
    else:
        st.warning("Hups, tältä alueelta ei löytynyt vapaita kuvia juuri nyt. Kokeile toista kaupunginosaa!")

st.sidebar.info("""
Tämä sovellus käyttää Finna API:a. 
Kuvat on rajattu vapaasti käytettäviin aineistoihin (CC-lisenssit).
""")
