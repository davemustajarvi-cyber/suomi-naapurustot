# 1. Tarkempi API-suodatin
    params = {
        "lookfor": f'Tampere "{valittu_alue}"',
        "filter[]": [
            'format:0/Image/',
            'online_boolean:1',
            # Huom: Finna käyttää usein tätä syntaksia aikaväleille
            f'daterange:[{vuodet[0]} TO {vuodet[1]}]'
        ],
        "limit": 50, # Haetaan vähän enemmän, jotta voidaan siivota käsin
        "field[]": ["title", "images", "year", "buildings", "id"]
    }

    with st.spinner(f"Etsitään kuvia: {valittu_alue}, vuodet {vuodet[0]}-{vuodet[1]}..."):
        response = requests.get(url, params=params)
        data = response.json()

    if "records" in data and data["records"]:
        # 2. TUPLAVARMISTUS: Suodatetaan tulokset vielä Pythonilla
        valid_records = []
        for r in data["records"]:
            year_str = r.get("year")
            if year_str and year_str.isdigit():
                y = int(year_str)
                if vuodet[0] <= y <= vuodet[1]:
                    valid_records.append(r)
        
        st.subheader(f"Löytyi {len(valid_records)} kuvaa väliltä {vuodet[0]}–{vuodet[1]}")
        
        if valid_records:
            cols = st.columns(3)
            for idx, record in enumerate(valid_records[:24]): # Näytetään max 24
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
            st.warning("Ei tarkkoja osumia tälle aikavälille. Kokeile laajempaa hakua!")
