import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title('Amazon Gewinnanalyse')

uploaded_amazon = st.file_uploader("Amazon Export CSV hochladen", type="csv")
uploaded_produkte = st.file_uploader("Produktinformationen CSV hochladen", type="csv")

if uploaded_amazon and uploaded_produkte:
    amazon_df = pd.read_csv(uploaded_amazon)
    produkte_df = pd.read_csv(uploaded_produkte)

    # Automatische Aktualisierung: Prüfe auf neue SKUs in Amazon-Daten
    new_skus = set(amazon_df['SKU']) - set(produkte_df['SKU'])
    if new_skus:
        st.warning(f"Neue SKUs gefunden, bitte Produktinfos aktualisieren für: {', '.join(new_skus)}")

    merged_df = pd.merge(amazon_df, produkte_df, on='SKU', how='inner')

    merged_df['Gewinn'] = (merged_df['Preis'] - merged_df['Amazon_Gebuehren'] - merged_df['Einkaufspreis'] - merged_df['Sonstige_Gebuehren']) * merged_df['Verkaufte_Anzahl']

    gewinn_df = merged_df.groupby(['SKU', 'Produktname']).agg({
        'Verkaufte_Anzahl': 'sum',
        'Gewinn': 'sum'
    }).reset_index()

    # Automatische Kategorisierung
    conditions = [
        gewinn_df['Gewinn'] > gewinn_df['Gewinn'].quantile(0.75),
        gewinn_df['Gewinn'] < gewinn_df['Gewinn'].quantile(0.25)
    ]
    choices = ['Top-Produkt', 'Verlust-Produkt']
    gewinn_df['Kategorie'] = np.select(conditions, choices, default='Mittel')

    st.write("### Gewinnübersicht mit Kategorien")
    st.dataframe(gewinn_df)

    # Gewinn-Diagramm
    st.write("### Gewinn nach Produkt")
    chart_df = gewinn_df.sort_values('Gewinn', ascending=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(chart_df['Produktname'], chart_df['Gewinn'])
    ax.set_xlabel('Gewinn')
    ax.set_ylabel('Produktname')
    ax.invert_yaxis()
    st.pyplot(fig)

    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(gewinn_df)

    st.download_button(
        label="Ergebnis als CSV herunterladen",
        data=csv,
        file_name='gewinnanalyse.csv',
        mime='text/csv'
    )
