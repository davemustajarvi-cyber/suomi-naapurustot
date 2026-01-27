import streamlit as st
import pandas as pd
import plotly.express as px

# Sivun asetukset
st.set_page_config(page_title="Elinvoimamittari", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('paavo_master.csv')
    df['Postinumero'] = df['Postinumero'].astype(str).str.zfill(5)
    return df

df = load_data()

# Määritellään KAIKKI ikäryhmät
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

# Välilehdet eri toiminnoille
tab1, tab2 = st.tabs(["🔍 Yksittäinen alue", "📊 Vertailu"])

def nayta_statsit(row, col_context, p_nro):
    tulo = row['Asukkaiden keskitulot (HR)']
    tähdet = "⭐" * max(1, min(5, int(tulo / 12000)))
    
    col_context.subheader(f"📍 {row['Alueen_nimi']} ({p_nro})")
    col_context.write(f"**Elinvoima:** {tähdet}")
    
    col_context.metric("Asukkaita", f"{int(row['Asukkaat yhteensä (HE)'])} kpl")
    col_context.metric("Keskitulo", f"{int(tulo)} €/v")
    col_context.metric("Keski-ikä", f"{row['Asukkaiden keski-ikä (HE)']} v")
    
    # Graafi
    ika_data = pd.DataFrame({
        'Ikä': [c.replace(' (HE)', '') for c in ika_ryhmat],
        'Määrä': [row[c] for c in ika_ryhmat]
    })
    fig = px.bar(ika_data, x='Ikä', y='Määrä', color='Määrä', height=300)
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0))
    col_context.plotly_chart(fig, use_container_width=True)

# TAB 1: YKSI ALUE
with tab1:
    search_query = st.text_input("Syötä postinumero:").strip().zfill(5)
    if len(search_query) == 5 and search_query != "00000":
        alue = df[df['Postinumero'] == search_query]
        if not alue.empty:
            nayta_statsit(alue.iloc[0], st, search_query)
        else:
            st.error("Aluetta ei löytynyt.")

# TAB 2: VERTAILU
with tab2:
    col_a, col_b = st.columns(2)
    p1 = col_a.text_input("Postinumero 1:", key="p1").strip().zfill(5)
    p2 = col_b.text_input("Postinumero 2:", key="p2").strip().zfill(5)
    
    if p1 and p2 and p1 != "00000" and p2 != "00000":
        alue1 = df[df['Postinumero'] == p1]
        alue2 = df[df['Postinumero'] == p2]
        
        if not alue1.empty and not alue2.empty:
            nayta_statsit(alue1.iloc[0], col_a, p1)
            nayta_statsit(alue2.iloc[0], col_b, p2)
        else:
            st.warning("Varmista, että molemmat postinumerot ovat oikein.")

# Sivupalkki
st.sidebar.header("Rikkaimmat alueet top 5")
top_5 = df.sort_values('Asukkaiden keskitulot (HR)', ascending=False).head(5)
for i, r in top_5.iterrows():
    st.sidebar.write(f"{r['Postinumero']} {r['Alueen_nimi']}: **{int(r['Asukkaiden keskitulot (HR)'])} €**")
