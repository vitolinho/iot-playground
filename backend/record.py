# record.py - Fonction principale d'enregistrement

from pylsl import StreamInlet, resolve_byprop
from pynput.keyboard import Listener, Key
import threading
import time
import streamlit as st

from head_tracker import HeadTracker
from controllers import ControlManager
from config import *

# Variables globales
is_recording = False
control_manager = None
head_tracker = None
keyboard_listener = None
recording_thread = None

def on_press(key):
    """Gestion des touches pour changer de mode"""
    global control_manager, head_tracker
    
    if not control_manager:
        return
        
    try:
        if key == Key.tab:  # TAB pour changer de mode
            current_mode = control_manager.get_mode()
            new_mode = "keyboard" if current_mode == "mouse" else "mouse"
            control_manager.set_mode(new_mode)
            print(f"\n🔄 Mode changé: {new_mode.upper()}")
            
            # Mettre à jour dans Streamlit si possible
            try:
                st.session_state.control_mode = new_mode
            except:
                pass
                
        elif hasattr(key, 'char') and key.char == 'r':  # R pour reset
            if head_tracker:
                head_tracker.reset()
                print("\n🔄 Position réinitialisée!")
    except:
        pass

def _recording_loop():
    """Boucle principale d'enregistrement"""
    global is_recording, control_manager, head_tracker
    
    print("🔍 Recherche d'un flux GYRO...")
    
    # Résoudre les flux disponibles
    streams = resolve_byprop("type", "GYRO", timeout=2)
    
    if len(streams) == 0:
        print("❌ Impossible de trouver un flux GYRO.")
        print("Vérifiez que le streaming Muse est bien démarré.")
        is_recording = False
        return
    
    inlet = StreamInlet(streams[0], max_chunklen=1)
    print("✅ Flux GYRO trouvé! Démarrage du contrôle...")
    print("\n📋 CONTRÔLES:")
    print("  TAB : Basculer mode souris/clavier")
    print("  R   : Réinitialiser la position")
    print(f"  Mode actuel : {control_manager.get_mode().upper()}\n")
    
    center_hold_time = 0
    last_state = 'CENTRE'
    
    while is_recording:
        try:
            data, _ = inlet.pull_chunk(timeout=0.01, max_samples=1)
            
            if data:
                gyro_x = data[0][0]
                gyro_y = data[0][1]
                
                # Mettre à jour le tracker
                state = head_tracker.update(gyro_x, gyro_y)
                control_manager.update_direction(state)
                
                # Afficher les changements d'état
                if state != last_state:
                    status = "↩️ Retour au centre" if head_tracker.is_returning_to_center() else "➡️ Mouvement"
                    print(f"{status} | Direction: {state:12s} | Gyro X:{gyro_x:6.1f} Y:{gyro_y:6.1f}")
                    last_state = state
                
                # Gérer l'action au centre
                if state == 'CENTRE':
                    if last_state != 'CENTRE':
                        center_hold_time = time.time()
                    elif time.time() - center_hold_time > CENTER_HOLD_TIME:
                        control_manager.handle_center_action()
                        center_hold_time = time.time() + CENTER_COOLDOWN
                        
        except Exception as e:
            print(f"⚠️ Erreur dans la boucle: {e}")
            
        time.sleep(0.01)
    
    print("\n👋 Enregistrement arrêté.")

def record():
    """Lance l'enregistrement des mouvements de tête"""
    global is_recording, control_manager, head_tracker, keyboard_listener, recording_thread
    
    if is_recording:
        print("⚠️ L'enregistrement est déjà en cours!")
        return
    
    print("\n🎮 Démarrage du système de contrôle par mouvements de tête...")
    
    # Initialiser les composants
    is_recording = True
    head_tracker = HeadTracker()
    control_manager = ControlManager()
    control_manager.start()
    
    # Démarrer l'écoute du clavier
    keyboard_listener = Listener(on_press=on_press)
    keyboard_listener.start()
    
    # Démarrer l'enregistrement dans un thread séparé
    recording_thread = threading.Thread(target=_recording_loop, daemon=True)
    recording_thread.start()
    
    # Stocker le mode dans la session Streamlit si disponible
    try:
        st.session_state.control_mode = control_manager.get_mode()
    except:
        pass

def stop_recording():
    """Arrête l'enregistrement"""
    global is_recording, control_manager, keyboard_listener, recording_thread
    
    if not is_recording:
        print("⚠️ Aucun enregistrement en cours.")
        return
    
    print("\n🛑 Arrêt de l'enregistrement...")
    
    # Arrêter l'enregistrement
    is_recording = False
    
    # Attendre la fin du thread
    if recording_thread:
        recording_thread.join(timeout=2)
    
    # Arrêter les composants
    if control_manager:
        control_manager.stop()
        control_manager = None
        
    if keyboard_listener:
        keyboard_listener.stop()
        keyboard_listener = None
    
    print("✅ Enregistrement arrêté.")

def get_current_mode():
    """Retourne le mode de contrôle actuel"""
    global control_manager
    if control_manager:
        return control_manager.get_mode()
    return DEFAULT_MODE

def set_mode(mode):
    """Change le mode de contrôle"""
    global control_manager
    if control_manager and mode in ["mouse", "keyboard"]:
        control_manager.set_mode(mode)
        print(f"🔄 Mode changé: {mode.upper()}")

def is_recording_active():
    """Indique si l'enregistrement est actif"""
    global is_recording
    return is_recording