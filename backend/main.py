import asyncio
import streamlit as st
from muselsl import stream, list_muses
import threading
import time

from record import record, stop_recording
from calibration import calibrate
from voice_control import start_voice_control, stop_voice_control

# Pour gérer l'état de l'application
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'voice_control' not in st.session_state:
    st.session_state.voice_control = False

def to_stream():
    """Connecte au casque Muse avec gestion d'erreurs améliorée"""
    try:
        with st.spinner("Recherche du Muse en cours..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            muses = list_muses()

        if not muses:
            st.error("Aucun Muse n'a été trouvé. Assurez-vous que le casque est allumé et à proximité.")
            return False

        st.success(f"Muse détecté: {muses[0]['name']} ({muses[0]['address']})")
        
        with st.spinner("Démarrage du streaming en cours..."):
            try:
                # Suppression du paramètre timeout qui cause l'erreur
                stream(muses[0]["address"], acc_enabled=True, gyro_enabled=True)
                st.success("Streaming démarré avec succès!")
                return True
            except TimeoutError:
                st.error("La connexion au Muse a expiré. Veuillez rapprocher le casque et réessayer.")
                return False
            except Exception as e:
                st.error(f"Erreur lors de la connexion: {str(e)}")
                return False
    except Exception as e:
        st.error(f"Erreur inattendue: {str(e)}")
        return False

def start_recording():
    """Démarre l'enregistrement dans un thread séparé"""
    if not st.session_state.recording:
        record()
        st.session_state.recording = True
        # Démarrer aussi le contrôle vocal
        if not st.session_state.voice_control:
            start_voice_control()
            st.session_state.voice_control = True

def stop_record():
    """Arrête l'enregistrement"""
    if st.session_state.recording:
        stop_recording()
        st.session_state.recording = False
        # Arrêter aussi le contrôle vocal
        if st.session_state.voice_control:
            stop_voice_control()
            st.session_state.voice_control = False

# Interface utilisateur Streamlit
st.title("Amuse toi !")

st.write("**Connecte-toi à ton casque Muse, puis lance l'enregistrement pour commencer à jouer à des jeux vidéo contrôlés par ta tête !**")

st.markdown(
    "[Tu n'as pas encore de casque ? Clique ici pour acheter le Muse sur Amazon.](https://www.amazon.fr/Muse-2-The-Brain-Sensing-Headband/dp/B0C836PV92)",
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    st.button("Connecter", on_click=to_stream, type="primary")

with col2:
    if not st.session_state.recording:
        st.button("Enregistrer", on_click=start_recording)
    else:
        st.button("Arrêter", on_click=stop_record, type="secondary")

with col3:
    st.button("Calibrer visage", on_click=calibrate, type="primary")