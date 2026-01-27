import streamlit as st
import pandas as pd
import plotly.express as px

# Sivun asetukset
st.set_page_config(page_title="Elinvoimamittari", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv('paavo_master.csv')

df = load_data()

st.title("🏘️ Naapuruston Elinvoimamittari")
st.markdown("Hae postinumerolla ja katso alueen faktat.")

# Sivupalkki: Top-listat
st.sidebar.header("Suomen kärki")
rikkaimmat = df.sort_values(by='Asukkaiden keskitulot (HR)', ascending=False).head(5)
st.sidebar.write("**Rikkaimmat alueet:**")
for i, row in rikkaimmat.iterrows():
    st.sidebar.write(f"{row['Alueen_nimi']}: {int(row['Asukkaiden keskitulot (HR)'])} €")

# Pääosio: Haku
search_query = st.text_input("Syötä postinumero (esim. 02160 tai 33960):", "")

if search_query:
    alue = df[df['Postinumero'] == str(search_query)]
    
    if not alue.empty:
        row = alue.iloc[0]
        st.header(f"📍 {row['Alueen_nimi']} ({search_query})")
        
        # Mittarit
        col1, col2, col3 = st.columns(3)
        col1.metric("Asukkaat", f"{int(row['Asukkaat yhteensä (HE)'])} kpl")
        col2.metric("Keskitulo (HR)", f"{int(row['Asukkaiden keskitulot (HR)'])} €")
        col3.metric("Keski-ikä", f"{row['Asukkaiden keski-ikä (HE)']} v")
        
        # Ikäjakauma-graafi
        ika_cols = [c for c in df.columns if '(HE)' in c and '-' in c]
        ika_data = row[ika_cols].reset_index()
        ika_data.columns = ['Ikäryhmä', 'Määrä']
        
        fig = px.bar(ika_data, x='Ikäryhmä', y='Määrä', title="Alueen ikärakenne")
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.error("Postinumeroa ei löytynyt.")
