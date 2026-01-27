import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Naapuruston Elinvoimamittari", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('paavo_master.csv')
    df['Postinumero'] = df['Postinumero'].astype(str).str.zfill(5)
    return df

df = load_data()

# Ikäryhmät graafia varten
ika_ryhmat = [
    '0-2-vuotiaat (HE)', '3-6-vuotiaat (HE)', '7-12-vuotiaat (HE)', 
    '13-15-vuotiaat (HE)', '16-17-vuotiaat (HE)', '18-19-vuotiaat (HE)',
    '20-24-vuotiaat (HE)', '25-29-vuotiaat (HE)', '30-34-vuotiaat (HE)',
    '35-39-vuotiaat (HE)', '40-44-vuotiaat (HE)', '45-49-vuotiaat (HE)',
    '50-54-vuotiaat (HE)', '55-59-vuotiaat (HE)', '60-64-vuotiaat (HE)',
    '65-69-vuotiaat (HE)', '70-74-vuotiaat (HE)', '75-79-vuotiaat (HE)',
    '80-84-vuotiaat (HE)', '85 vuotta täyttäneet (HE)'
]

st.title("🏘️ Naapuruston Elinvoimamittari v2.0")

tab1, tab2 = st.tabs(["🔍 Aluehaku", "⚔️ Alueiden taistelu"])

def nayta_statsit(row, context, p_nro, winner_tags=None, suffix=""):
    context.subheader(f"{row['Alueen_nimi']} ({p_nro})")
    
    if winner_tags:
        for tag in winner_tags:
            context.info(tag)

    # MITTARIT - Rivi 1 (Perustiedot)
    m1, m2, m3 = context.columns(3)
    m1.metric("Asukkaita", f"{int(row['Asukkaat yhteensä (HE)'])} kpl")
    m2.metric("Keskitulo", f"{int(row['Asukkaiden keskitulot (HR)'])} €/v")
    m3.metric("Keski-ikä", f"{row['Asukkaiden keski-ikä (HE)']} v")
    
    # MITTARIT - Rivi 2 (Uusi data!)
    m4, m5, m6 = context.columns(3)
    
    # Koulutus: Lasketaan korkeakoulutettujen osuus 18v täyttäneistä
    korkea = (row['Ylemmän korkeakoulututkinnon suorittaneet (KO)'] / row['18 vuotta täyttäneet yhteensä (KO)']) * 100
    m4.metric("Korkeakoulutetut", f"{korkea:.1f} %")
    
    # Työllisyys: Työllisten osuus asukkaista
    tyo = (row['Työlliset (PT)'] / row['Asukkaat yhteensä (HE)']) * 100
    m5.metric("Työllisyysaste", f"{tyo:.1f} %")
    
    # Asuminen: Keskipinta-ala
    m6.metric("Asunnon koko (ka)", f"{row['Asuntojen keskipinta-ala (RA)']} m²")

    # Ikäjakauma
    ika_data = pd.DataFrame({
        'Ikä': [c.replace(' (HE)', '') for c in ika_ryhmat],
        'Määrä': [row[c] for c in ika_ryhmat]
    })
    fig = px.bar(ika_data, x='Ikä', y='Määrä', color='Määrä', height=300)
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0), showlegend=False)
    context.plotly_chart(fig, use_container_width=True, key=f"chart_{p_nro}_{suffix}")

# TAB 1: ALUEHAKU
with tab1:
    search_input = st.text_input("Hae postinumerolla:", key="search_bar").strip()
    if search_input:
        q = search_input.zfill(5)
        res = df[df['Postinumero'] == q]
        if not res.empty:
            nayta_statsit(res.iloc[0], st, q, suffix="single")
        else:
            st.warning("Aluetta ei löytynyt.")

# TAB 2: VERTAILU
with tab2:
    st.write("Vertaile kahta aluetta vastakkain!")
    c1, c2 = st.columns(2)
    p1_in = c1.text_input("Alue 1:", key="v1").strip()
    p2_in = c2.text_input("Alue 2:", key="v2").strip()
    
    if p1_in and p2_in:
        p1, p2 = p1_in.zfill(5), p2_in.zfill(5)
        r1, r2 = df[df['Postinumero'] == p1], df[df['Postinumero'] == p2]
        
        if not r1.empty and not r2.empty:
            row1, row2 = r1.iloc[0], r2.iloc[0]
            w1, w2 = [], []
            
            # Koulutusvoittaja
            k1 = row1['Ylemmän korkeakoulututkinnon suorittaneet (KO)'] / row1['18 vuotta täyttäneet yhteensä (KO)']
            k2 = row2['Ylemmän korkeakoulututkinnon suorittaneet (KO)'] / row2['18 vuotta täyttäneet yhteensä (KO)']
            if k1 > k2: w1.append("🎓 Korkeakoulutetumpi")
            else: w2.append("🎓 Korkeakoulutetumpi")
            
            # Pinta-alavoittaja
            if row1['Asuntojen keskipinta-ala (RA)'] > row2['Asuntojen keskipinta-ala (RA)']:
                w1.append("🏠 Väljempää asumista")
            else:
                w2.append("🏠 Väljempää asumista")
            
            nayta_statsit(row1, c1, p1, w1, suffix="c1")
            nayta_statsit(row2, c2, p2, w2, suffix="c2")

st.sidebar.header("Suomen kärki")
top_5 = df.sort_values('Asukkaiden keskitulot (HR)', ascending=False).head(5)
for i, r in top_5.iterrows():
    st.sidebar.write(f"{r['Postinumero']} {r['Alueen_nimi']}")
