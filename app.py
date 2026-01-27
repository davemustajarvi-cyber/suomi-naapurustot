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

def nayta_statsit(row, context, p_nro, winner_tags=None):
    tulo = row['Asukkaiden keskitulot (HR)']
    tähdet = "⭐" * max(1, min(5, int(tulo / 12000)))
    
    context.subheader(f"{row['Alueen_nimi']} ({p_nro})")
    
    # Jos alue on voittaja jossain kategoriassa, näytetään mitali
    if winner_tags:
        for tag in winner_tags:
            context.info(tag)

    context.write(f"**Elinvoima:** {tähdet}")
    context.metric("Asukkaita", f"{int(row['Asukkaat yhteensä (HE)'])} kpl")
    context.metric("Keskitulo", f"{int(tulo)} €/v")
    context.metric("Keski-ikä", f"{row['Asukkaiden keski-ikä (HE)']} v")
    
    ika_data = pd.DataFrame({
        'Ikä': [c.replace(' (HE)', '') for c in ika_ryhmat],
        'Määrä': [row[c] for c in ika_ryhmat]
    })
    fig = px.bar(ika_data, x='Ikä', y='Määrä', color='Määrä', height=300)
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0), showlegend=False)
    context.plotly_chart(fig, use_container_width=True)

# TAB 1: ALUEHAKU
with tab1:
    search_query = st.text_input("Hae postinumerolla:").strip().zfill(5)
    if len(search_query) == 5 and search_query != "00000":
        res = df[df['Postinumero'] == search_query]
        if not res.empty:
            nayta_statsit(res.iloc[0], st, search_query)

# TAB 2: VERTAILU (VOITTAJA-LOGIIKALLA)
with tab2:
    st.write("Laita kaksi aluetta vastakkain ja katso kumpi voittaa!")
    c1, c2 = st.columns(2)
    p1 = c1.text_input("Alue 1:", key="v1").strip().zfill(5)
    p2 = c2.text_input("Alue 2:", key="v2").strip().zfill(5)
    
    if p1 and p2 and p1 != "00000" and p2 != "00000" and p1 != p2:
        r1 = df[df['Postinumero'] == p1]
        r2 = df[df['Postinumero'] == p2]
        
        if not r1.empty and not r2.empty:
            row1, row2 = r1.iloc[0], r2.iloc[0]
            
            # VOITTAJA-LOGIIKKA
            w1, w2 = [], []
            
            # 1. Varakkaampi
            if row1['Asukkaiden keskitulot (HR)'] > row2['Asukkaiden keskitulot (HR)']:
                w1.append("💰 Varakkaampi")
            else:
                w2.append("💰 Varakkaampi")
            
            # 2. Nuorekkaampi
            if row1['Asukkaiden keski-ikä (HE)'] < row2['Asukkaiden keski-ikä (HE)']:
                w1.append("👶 Nuorekkaampi")
            else:
                w2.append("👶 Nuorekkaampi")
                
            # 3. Lapsirikkaampi (0-6v osuus)
            lapset1 = (row1['0-2-vuotiaat (HE)'] + row1['3-6-vuotiaat (HE)']) / row1['Asukkaat yhteensä (HE)']
            lapset2 = (row2['0-2-vuotiaat (HE)'] + row2['3-6-vuotiaat (HE)']) / row2['Asukkaat yhteensä (HE)']
            if lapset1 > lapset2:
                w1.append("🍼 Lapsiystävällisempi")
            else:
                w2.append("🍼 Lapsiystävällisempi")

            # Näytetään tulokset
            nayta_statsit(row1, c1, p1, w1)
            nayta_statsit(row2, c2, p2, w2)
