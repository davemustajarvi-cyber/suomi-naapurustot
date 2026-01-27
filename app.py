import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Naapuruston Elinvoimamittari", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('paavo_master.csv')
    df['Postinumero'] = df['Postinumero'].astype(str).str.zfill(5)
    
    # Yritetään hakea koordinaatit
    try:
        coords_url = "https://raw.githubusercontent.com/themiika/finnish-postalcodes/master/postalcodes.csv"
        coords = pd.read_csv(coords_url)
        coords['code'] = coords['code'].astype(str).str.zfill(5)
        # Yhdistetään (merge)
        df = pd.merge(df, coords[['code', 'lat', 'lng']], left_on='Postinumero', right_on='code', how='left')
    except Exception as e:
        st.sidebar.warning("Karttojen latauksessa ongelma. Näytetään vain tilastot.")

    # VARMISTUS: Jos sarakkeita ei ole (merge epäonnistui), luodaan ne tyhjinä
    if 'lat' not in df.columns:
        df['lat'] = None
    if 'lng' not in df.columns:
        df['lng'] = None
        
    return df

df = load_data()

# Kaikki ikäryhmät
ika_ryhmat = [
    '0-2-vuotiaat (HE)', '3-6-vuotiaat (HE)', '7-12-vuotiaat (HE)', 
    '13-15-vuotiaat (HE)', '16-17-vuotiaat (HE)', '18-19-vuotiaat (HE)',
    '20-24-vuotiaat (HE)', '25-29-vuotiaat (HE)', '30-34-vuotiaat (HE)',
    '35-39-vuotiaat (HE)', '40-44-vuotiaat (HE)', '45-49-vuotiaat (HE)',
    '50-54-vuotiaat (HE)', '55-59-vuotiaat (HE)', '60-64-vuotiaat (HE)',
    '65-69-vuotiaat (HE)', '70-74-vuotiaat (HE)', '75-79-vuotiaat (HE)',
    '80-84-vuotiaat (HE)', '85 vuotta täyttäneet (HE)'
]

st.title("🏘️ Naapuruston Elinvoimamittari")

tab1, tab2 = st.tabs(["🔍 Aluehaku", "⚔️ Alueiden taistelu"])

def nayta_statsit(row, context, p_nro, winner_tags=None, suffix=""):
    tulo = row['Asukkaiden keskitulot (HR)']
    tähdet = "⭐" * max(1, min(5, int(tulo / 12000)))
    
    context.subheader(f"{row['Alueen_nimi']} ({p_nro})")
    
    if winner_tags:
        for tag in winner_tags:
            context.info(tag)

    m1, m2, m3 = context.columns(3)
    m1.metric("Asukkaita", f"{int(row['Asukkaat yhteensä (HE)'])} kpl")
    m2.metric("Keskitulo", f"{int(tulo)} €/v")
    m3.metric("Keski-ikä", f"{row['Asukkaiden keski-ikä (HE)']} v")
    
    # TURVALLINEN KARTTA-TARKISTUS: Tarkistetaan löytyykö sarake ja onko siinä arvo
    if 'lat' in row and pd.notnull(row['lat']) and pd.notnull(row['lng']):
        map_data = pd.DataFrame({'lat': [row['lat']], 'lon': [row['lng']]})
        context.map(map_data, zoom=10)
    
    ika_data = pd.DataFrame({
        'Ikä': [c.replace(' (HE)', '') for c in ika_ryhmat],
        'Määrä': [row[c] for c in ika_ryhmat]
    })
    fig = px.bar(ika_data, x='Ikä', y='Määrä', color='Määrä', height=300)
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0), showlegend=False)
    context.plotly_chart(fig, use_container_width=True, key=f"chart_{p_nro}_{suffix}")

# TAB 1: ALUEHAKU
with tab1:
    search_input = st.text_input("Hae postinumerolla:", key="single_search").strip()
    if search_input:
        search_query = search_input.zfill(5)
        res = df[df['Postinumero'] == search_query]
        if not res.empty:
            nayta_statsit(res.iloc[0], st, search_query, suffix="search")
            
            # Lisätty: Latausnappi
            csv = res.to_csv(index=False).encode('utf-8')
            st.download_button("Lataa alueen tiedot (CSV)", csv, f"raportti_{search_query}.csv", "text/csv")
        else:
            st.warning("Aluetta ei löytynyt.")

# TAB 2: VERTAILU
with tab2:
    st.write("Vertaile kahta aluetta keskenään.")
    c1, c2 = st.columns(2)
    p1_in = c1.text_input("Alue 1 (postinumero):", key="v1_in").strip()
    p2_in = c2.text_input("Alue 2 (postinumero):", key="v2_in").strip()
    
    if p1_in and p2_in:
        p1, p2 = p1_in.zfill(5), p2_in.zfill(5)
        r1 = df[df['Postinumero'] == p1]
        r2 = df[df['Postinumero'] == p2]
        
        if not r1.empty and not r2.empty:
            row1, row2 = r1.iloc[0], r2.iloc[0]
            w1, w2 = [], []
            if row1['Asukkaiden keskitulot (HR)'] > row2['Asukkaiden keskitulot (HR)']:
                w1.append("💰 Varakkaampi")
            else:
                w2.append("💰 Varakkaampi")
            
            # Näytetään molemmat
            nayta_statsit(row1, c1, p1, w1, suffix="comp1")
            nayta_statsit(row2, c2, p2, w2, suffix="comp2")
        else:
            st.error("Tarkista numerot.")

# Sivupalkki
st.sidebar.header("Rikkaimmat alueet top 5")
top_5 = df.sort_values('Asukkaiden keskitulot (HR)', ascending=False).head(5)
for i, r in top_5.iterrows():
    st.sidebar.write(f"{r['Postinumero']} {r['Alueen_nimi']}: **{int(r['Asukkaiden keskitulot (HR)'])} €**")
