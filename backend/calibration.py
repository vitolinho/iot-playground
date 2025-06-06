import time
import streamlit as st
from pylsl import StreamInlet, resolve_byprop

# Variables de calibration
calibration_data = {
    'center_x': 0,
    'center_y': 0,
    'is_calibrated': False
}

def calibrate():
    """Effectue la calibration du casque"""
    try:
        st.info("🎯 Calibration en cours...")
        st.write("Regardez droit devant vous et restez immobile pendant 3 secondes.")
        
        # Rechercher le flux GYRO
        streams = resolve_byprop("type", "GYRO", timeout=2)
        
        if len(streams) == 0:
            st.error("❌ Impossible de trouver le flux GYRO. Assurez-vous que le streaming est actif.")
            return False
        
        inlet = StreamInlet(streams[0], max_chunklen=1)
        
        # Collecter des données pendant 3 secondes
        samples_x = []
        samples_y = []
        start_time = time.time()
        
        progress_bar = st.progress(0)
        
        while time.time() - start_time < 3:
            data, _ = inlet.pull_chunk(timeout=0.1, max_samples=1)
            if data:
                samples_x.append(data[0][0])
                samples_y.append(data[0][1])
            
            # Mettre à jour la barre de progression
            progress = (time.time() - start_time) / 3
            progress_bar.progress(progress)
        
        progress_bar.empty()
        
        if len(samples_x) > 0:
            # Calculer les valeurs moyennes
            calibration_data['center_x'] = sum(samples_x) / len(samples_x)
            calibration_data['center_y'] = sum(samples_y) / len(samples_y)
            calibration_data['is_calibrated'] = True
            
            st.success(f"✅ Calibration réussie!")
            st.write(f"Position de référence: X={calibration_data['center_x']:.2f}, Y={calibration_data['center_y']:.2f}")
            
            # Sauvegarder dans la session Streamlit
            st.session_state.calibration_data = calibration_data
            
            return True
        else:
            st.error("❌ Aucune donnée collectée pendant la calibration.")
            return False
            
    except Exception as e:
        st.error(f"❌ Erreur lors de la calibration: {str(e)}")
        return False

def get_calibration_data():
    """Retourne les données de calibration"""
    # Vérifier d'abord la session Streamlit
    if 'calibration_data' in st.session_state:
        return st.session_state.calibration_data
    return calibration_data

def is_calibrated():
    """Vérifie si le système est calibré"""
    data = get_calibration_data()
    return data.get('is_calibrated', False)

def reset_calibration():
    """Réinitialise la calibration"""
    global calibration_data
    calibration_data = {
        'center_x': 0,
        'center_y': 0,
        'is_calibrated': False
    }
    if 'calibration_data' in st.session_state:
        st.session_state.calibration_data = calibration_data