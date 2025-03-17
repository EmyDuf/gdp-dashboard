import streamlit as st

st.logo("data/n.svg")

st.set_page_config(page_title="Plotting Demo", page_icon="📈")
st.sidebar.selectbox('Person incharge', options=['john', 'peter'], index=0)
st.sidebar.selectbox('location', options=['manila', 'tokyo'], index=1)
