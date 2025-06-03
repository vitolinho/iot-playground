import asyncio
import streamlit as st
from muselsl import stream, list_muses

from record import record

def to_stream():
    with st.spinner("Recherche du Muse en cours..."):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        muses = list_muses()

    if not muses:
        st.error("Aucun Muse n'a été trouvé.")
        return

    st.success("Muse détecté ! Démarrage du streaming en cours...")

    stream(muses[0]["address"], acc_enabled=True, gyro_enabled=True)

st.title("Amuse toi !")

st.write("**Connecte-toi à ton casque Muse, puis lance l'enregistrement pour commencer à jouer à des jeux vidéo contrôlés par ta tête !**")

st.markdown(
    "[Tu n'as pas encore de casque ? Clique ici pour acheter le Muse sur Amazon.](https://www.amazon.fr/Muse-2-The-Brain-Sensing-Headband/dp/B0C836PV92)",
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    st.button("Connecter", on_click=to_stream, type="primary")

with col2:
    st.button("Enregistrer", on_click=record)
