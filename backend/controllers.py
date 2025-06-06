from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key
import threading
import time
from config import *

class MouseControl:
    """Gère le contrôle de la souris"""
    
    def __init__(self):
        self.mouse = MouseController()
        self.speed_multiplier = 1.0
        self.last_click_time = 0
        self.current_direction = 'CENTRE'
        
    def move(self, direction):
        """Déplace la souris selon la direction"""
        if direction == 'CENTRE':
            self.speed_multiplier = 1.0
            self.current_direction = direction
            return
            
        self.current_direction = direction
        current_x, current_y = self.mouse.position
        dx, dy = 0, 0
        
        # Calculer le déplacement
        if 'GAUCHE' in direction:
            dx = -MOUSE_SPEED * self.speed_multiplier
        elif 'DROITE' in direction:
            dx = MOUSE_SPEED * self.speed_multiplier
        
        if 'HAUT' in direction:
            dy = -MOUSE_SPEED * self.speed_multiplier
        elif 'BAS' in direction:
            dy = MOUSE_SPEED * self.speed_multiplier
        
        # Pour les diagonales, réduire la vitesse
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707
        
        # Appliquer le mouvement
        try:
            self.mouse.position = (current_x + dx, current_y + dy)
        except:
            pass  # Ignorer si on sort de l'écran
        
        # Accélération progressive
        if self.speed_multiplier < MOUSE_ACCELERATION:
            self.speed_multiplier += 0.05
    
    def click(self):
        """Effectue un clic gauche"""
        current_time = time.time()
        if current_time - self.last_click_time > CENTER_COOLDOWN:
            self.mouse.click(Button.left)
            self.last_click_time = current_time
            return True
        return False
    
    def reset_acceleration(self):
        """Réinitialise l'accélération"""
        self.speed_multiplier = 1.0
    
    def get_current_direction(self):
        """Retourne la direction actuelle du mouvement"""
        return self.current_direction

class KeyboardControl:
    """Gère le contrôle du clavier"""
    
    def __init__(self):
        self.keyboard = KeyboardController()
        self.last_key_time = 0
        self.pending_directions = []
        self.has_gesture_processed = False
        
    def press_keys(self, direction):
        """Appuie sur les touches selon la direction"""
        current_time = time.time()
        
        # Ignorer les actions trop rapprochées
        if current_time - self.last_key_time < KEY_REPEAT_DELAY:
            return
            
        # Ne pas déclencher d'action si on est au centre
        if direction == 'CENTRE':
            self.has_gesture_processed = False
            return
        
        # Si on a déjà traité un geste, attendre le retour au centre
        if self.has_gesture_processed:
            return
            
        # Stocker la direction et déclencher une action uniquement pour les gestes complets
        # La classe HeadTracker s'assure déjà que c'est un geste complet
        self._execute_keyboard_action(direction)
        self.has_gesture_processed = True
        self.last_key_time = current_time
    
    def _execute_keyboard_action(self, direction):
        """Exécute l'action clavier en fonction de la direction"""
        if direction == 'GAUCHE':
            self.keyboard.tap(Key.left)
            print("⌨️ Touche: GAUCHE")
        elif direction == 'DROITE':
            self.keyboard.tap(Key.right)
            print("⌨️ Touche: DROITE")
        elif direction == 'HAUT':
            self.keyboard.tap(Key.up)
            print("⌨️ Touche: HAUT")
        elif direction == 'BAS':
            self.keyboard.tap(Key.down)
            print("⌨️ Touche: BAS")
        # elif direction == 'GAUCHE HAUT':
        #     self.keyboard.tap(Key.left)
        #     self.keyboard.tap(Key.up)
        #     print("⌨️ Touche: GAUCHE+HAUT")
        # elif direction == 'GAUCHE BAS':
        #     self.keyboard.tap(Key.left)
        #     self.keyboard.tap(Key.down)
        #     print("⌨️ Touche: GAUCHE+BAS")
        # elif direction == 'DROITE HAUT':
        #     self.keyboard.tap(Key.right)
        #     self.keyboard.tap(Key.up)
        #     print("⌨️ Touche: DROITE+HAUT")
        # elif direction == 'DROITE BAS':
        #     self.keyboard.tap(Key.right)
        #     self.keyboard.tap(Key.down)
        #     print("⌨️ Touche: DROITE+BAS")
    
    def press_space(self):
        """Appuie sur la barre espace"""
        current_time = time.time()
        if current_time - self.last_key_time > KEY_REPEAT_DELAY:
            self.keyboard.tap(Key.space)
            self.last_key_time = current_time
            return True
        return False
    
    def reset(self):
        """Réinitialise les états"""
        self.has_gesture_processed = False
        self.pending_directions = []

class ControlManager:
    """Gestionnaire principal des contrôles"""
    
    def __init__(self):
        self.mouse_control = MouseControl()
        self.keyboard_control = KeyboardControl()
        self.current_mode = DEFAULT_MODE
        self.movement_active = False
        self.current_direction = 'CENTRE'
        self.last_gesture_direction = None
        self.is_running = False
        self.movement_thread = None
        
    def start(self):
        """Démarre le gestionnaire de contrôles"""
        self.is_running = True
        self.movement_thread = threading.Thread(target=self._movement_loop, daemon=True)
        self.movement_thread.start()
        
    def stop(self):
        """Arrête le gestionnaire de contrôles"""
        self.is_running = False
        if self.movement_thread:
            self.movement_thread.join(timeout=1)
            
    def set_mode(self, mode):
        """Change le mode de contrôle"""
        self.current_mode = mode
        self.mouse_control.reset_acceleration()
        self.keyboard_control.reset()
        
    def get_mode(self):
        """Retourne le mode actuel"""
        return self.current_mode
        
    def update_direction(self, direction):
        """Met à jour la direction actuelle"""
        # Détecter les changements de direction
        direction_changed = (self.current_direction != direction)
        
        if direction_changed and direction != 'CENTRE':
            # Nouvelle direction non-centre détectée
            self.last_gesture_direction = direction
            
        self.current_direction = direction
        self.movement_active = (direction != 'CENTRE')
        
        # En mode clavier, gérer immédiatement les changements
        # pour réduire la latence des actions
        if self.current_mode == "keyboard" and direction_changed:
            self.keyboard_control.press_keys(direction)
            
    def _movement_loop(self):
        """Boucle principale de mouvement"""
        while self.is_running:
            if self.movement_active:
                if self.current_mode == "mouse":
                    self.mouse_control.move(self.current_direction)
                # Mode clavier géré directement dans update_direction pour être plus réactif
            else:
                self.mouse_control.reset_acceleration()
                
            time.sleep(0.02)  # 50 FPS
            
    def handle_center_action(self):
        """Gère l'action quand la tête est au centre"""
        # if self.current_mode == "mouse":
        #     if self.mouse_control.click():
        #         print("🖱️ Clic!")
        #         return True
        # else:  # Mode clavier
        #     if self.keyboard_control.press_space():
        #         print("⌨️ Espace!")
        #         return True
        return False