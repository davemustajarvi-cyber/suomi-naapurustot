import streamlit as st
import pandas as pd
import plotly.express as px

# Sivun asetukset
st.set_page_config(page_title="Elinvoimamittari", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('paavo_master.csv')
    # Varmistetaan, että postinumero on aina 5 merkkiä pitkä teksti (lisää nollat alkuun)
    df['Postinumero'] = df['Postinumero'].astype(str).str.zfill(5)
    return df

df = load_data()

st.title("🏘️ Naapuruston Elinvoimamittari")
st.markdown("Hae Suomen postinumeroita nähdäksesi alueen tilastot ja elinvoiman.")

# Hakukenttä
search_query = st.text_input("Syötä 5-numeroinen postinumero (esim. 00100 tai 33960):").strip()

if search_query:
    # Varmistetaan että haku on 5 merkkiä
    query_fixed = search_query.zfill(5)
    alue = df[df['Postinumero'] == query_fixed]
    
    if not alue.empty:
        row = alue.iloc[0]
        st.header(f"📍 {row['Alueen_nimi']} ({query_fixed})")
        
        # ELINVOIMA-ARVOSANA (Yksinkertainen lasku keskitulon perusteella)
        tulo = row['Asukkaiden keskitulot (HR)']
        tähdet = "⭐" * max(1, min(5, int(tulo / 12000))) # 1 tähti per 12k€, max 5
        
        st.subheader(f"Elinvoimaluokitus: {tähdet}")

        # Mittarit
        col1, col2, col3 = st.columns(3)
        col1.metric("Asukkaita", f"{int(row['Asukkaat yhteensä (HE)'])} kpl")
        col2.metric("Keskitulo", f"{int(tulo)} €/vuosi")
        col3.metric("Keski-ikä", f"{row['Asukkaiden keski-ikä (HE)']} vuotta")
        
        # Visualisointi: Ikärakenne
        ika_ryhmat = ['0-2-vuotiaat (HE)', '3-6-vuotiaat (HE)', '7-12-vuotiaat (HE)', 
                      '13-15-vuotiaat (HE)', '16-17-vuotiaat (HE)', '18-19-vuotiaat (HE)',
                      '20-24-vuotiaat (HE)', '25-29-vuotiaat (HE)', '30-34-vuotiaat (HE)',
                      '35-39-vuotiaat (HE)', '40-44-vuotiaat (HE)', '45-49-vuotiaat (HE)']
        
        ika_data = pd.DataFrame({
            'Ikäryhmä': [c.replace(' (HE)', '') for c in ika_ryhmat],
            'Määrä': [row[c] for c in ika_ryhmat]
        })
        
        fig = px.bar(ika_data, x='Ikäryhmä', y='Määrä', color='Määrä', 
                     title="Alueen nuoriso ja työikäiset")
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.warning(f"Postinumeroa {query_fixed} ei löytynyt. Kokeile esim. 00100.")

# Sivupalkin Top-lista
st.sidebar.header("Suomen rikkaimmat")
top_10 = df.sort_values('Asukkaiden keskitulot (HR)', ascending=False).head(10)
st.sidebar.dataframe(top_10[['Postinumero', 'Alueen_nimi', 'Asukkaiden keskitulot (HR)']], hide_index=True)
