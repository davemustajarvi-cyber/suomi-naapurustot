import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Naapuruston Elinvoimamittari v2.2", layout="wide")

@st.cache_data
def load_data():
    # Luetaan data ja siivotaan sarakkeiden nimet heti
    df = pd.read_csv('paavo_master.csv')
    df['Postinumero'] = df['Postinumero'].astype(str).str.zfill(5)
    
    # TÄRKEÄ: Poistetaan nimistä mahdolliset piilomerkit ja välilyönnit
    df.columns = [col.strip().replace('\ufeff', '') for col in df.columns]
    return df

df = load_data()

# Apufunktio turvalliseen datan hakuun
def hae_arvo(row, osa_nimesta, oletus=0):
    for col in row.index:
        if osa_nimesta in col:
            return row[col]
    return oletus

st.title("🏘️ Naapuruston Elinvoimamittari")

def nayta_statsit(row, context, p_nro, winner_tags=None, suffix=""):
    context.subheader(f"{row.get('Alueen_nimi', 'Tuntematon')} ({p_nro})")
    
    if winner_tags:
        for tag in winner_tags:
            context.info(tag)

    # MITTARIT - Rivi 1 (Perustiedot)
    m1, m2, m3 = context.columns(3)
    asukkaat = hae_arvo(row, 'Asukkaat yhteensä (HE)')
    m1.metric("Asukkaita", f"{int(asukkaat)} kpl")
    m2.metric("Keskitulo", f"{int(hae_arvo(row, 'Asukkaiden keskitulot'))} €/v")
    m3.metric("Keski-ikä", f"{hae_arvo(row, 'Asukkaiden keski-ikä')} v")
    
    # MITTARIT - Rivi 2 (Uusi data)
    m4, m5, m6 = context.columns(3)
    
    # Koulutusaste
    ylempi = hae_arvo(row, 'Ylemmän korkeakoulututkinnon')
    k_yhteensa = hae_arvo(row, '18 vuotta täyttäneet yhteensä (KO)')
    if k_yhteensa > 0:
        m4.metric("Korkeakoulutetut", f"{(ylempi/k_yhteensa)*100:.1f} %")
    else:
        m4.metric("Korkeakoulutetut", "---")
        
    # Työllisyys
    tyolliset = hae_arvo(row, 'Työlliset (PT)')
    if asukkaat > 0:
        m5.metric("Työllisyysaste", f"{(tyolliset/asukkaat)*100:.1f} %")
    
    # Asuminen
    pinta_ala = hae_arvo(row, 'Asuntojen keskipinta-ala')
    m6.metric("Asunnon koko (ka)", f"{pinta_ala} m²")

    # Ikäjakauma-graafi
    ika_cols = [c for c in row.index if '(HE)' in c and '-' in c]
    if ika_cols:
        ika_data = pd.DataFrame({
            'Ikä': [c.replace(' (HE)', '') for c in ika_cols],
            'Määrä': [row[c] for c in ika_cols]
        })
        fig = px.bar(ika_data, x='Ikä', y='Määrä', color='Määrä', height=300)
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
        context.plotly_chart(fig, use_container_width=True, key=f"ch_{p_nro}_{suffix}")

tab1, tab2 = st.tabs(["🔍 Aluehaku", "⚔️ Vertailu"])

with tab1:
    haku = st.text_input("Hae postinumerolla:", key="h1").strip().zfill(5)
    if haku != "00000":
        r = df[df['Postinumero'] == haku]
        if not r.empty:
            nayta_statsit(r.iloc[0], st, haku, suffix="s")

with tab2:
    col_a, col_b = st.columns(2)
    p1 = col_a.text_input("Alue 1:", key="v1").strip().zfill(5)
    p2 = col_b.text_input("Alue 2:", key="v2").strip().zfill(5)
    
    if p1 != "00000" and p2 != "00000" and p1 != p2:
        res1, res2 = df[df['Postinumero'] == p1], df[df['Postinumero'] == p2]
        if not res1.empty and not res2.empty:
            row1, row2 = res1.iloc[0], res2.iloc[0]
            
            # VOITTAJA-LOGIIKKA
            w1, w2 = [], []
            # Sivistysvoittaja
            s1 = hae_arvo(row1, 'Ylemmän korkeakoulututkinnon') / max(1, hae_arvo(row1, '18 vuotta täyttäneet yhteensä (KO)'))
            s2 = hae_arvo(row2, 'Ylemmän korkeakoulututkinnon') / max(1, hae_arvo(row2, '18 vuotta täyttäneet yhteensä (KO)'))
            if s1 > s2: w1.append("🎓 Sivistyneempi")
            elif s2 > s1: w2.append("🎓 Sivistyneempi")
            
            nayta_statsit(row1, col_a, p1, winner_tags=w1, suffix="v1")
            nayta_statsit(row2, col_b, p2, winner_tags=w2, suffix="v2")
