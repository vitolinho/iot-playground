from collections import deque
from config import *

class HeadTracker:
    """Gère le suivi de la position de la tête et la détection des mouvements"""
    
    def __init__(self):
        self.current_state = 'CENTRE'
        self.movement_history = deque(maxlen=HISTORY_SIZE)  # Historique des mouvements
        self.last_significant_direction = 'CENTRE'
        self.return_to_center_mode = False
        self.stable_counter = 0
        self.movement_threshold = MOVEMENT_THRESHOLD
        self.return_threshold = RETURN_THRESHOLD
        
        # Nouveaux attributs pour la détection de geste complet
        self.gesture_in_progress = False
        self.gesture_buffer = []
        self.gesture_start_time = 0
        self.last_gesture_direction = 'CENTRE'
        self.gesture_cooldown = 0
        
    def update(self, gyro_x, gyro_y):
        """Met à jour l'état basé sur les données du gyroscope"""
        # Déterminer le mouvement brut
        raw_movement = self._get_raw_movement(gyro_x, gyro_y)
        
        # Ajouter à l'historique
        self.movement_history.append((gyro_x, gyro_y, raw_movement))
        
        # Gérer les gestes complets
        if self.gesture_cooldown > 0:
            self.gesture_cooldown -= 1
            return self.current_state
        
        # Détection de geste complet
        gesture_result = self._process_gesture(gyro_x, gyro_y, raw_movement)
        if gesture_result:
            self.current_state = gesture_result
            self.last_significant_direction = gesture_result
            self.gesture_cooldown = GESTURE_COOLDOWN_FRAMES
            return gesture_result
        
        # Si on est en mode retour au centre
        if self.return_to_center_mode:
            # Vérifier si on est stabilisé au centre
            if abs(gyro_x) < self.return_threshold and abs(gyro_y) < self.return_threshold:
                self.stable_counter += 1
                if self.stable_counter > STABLE_FRAMES:  # Stable pendant N frames
                    self.current_state = 'CENTRE'
                    self.return_to_center_mode = False
                    self.last_significant_direction = 'CENTRE'
                    self.stable_counter = 0
            else:
                self.stable_counter = 0
                
            # En mode retour, on reste sur l'état actuel sauf si mouvement très fort
            if abs(gyro_x) > 30 or abs(gyro_y) > 30:
                self.return_to_center_mode = False
                self.current_state = raw_movement
                self.last_significant_direction = raw_movement
                
        else:
            # Mode normal
            if raw_movement != 'CENTRE':
                # Mouvement significatif détecté
                if self._is_opposite_movement(raw_movement, self.last_significant_direction):
                    # Mouvement opposé - probablement un retour au centre
                    self.return_to_center_mode = True
                    self.stable_counter = 0
                else:
                    # Mouvement dans la même direction ou nouvelle direction
                    self.current_state = raw_movement
                    self.last_significant_direction = raw_movement
            else:
                # Pas de mouvement significatif
                self.stable_counter += 1
                if self.stable_counter > 10:
                    self.current_state = 'CENTRE'
                    
        return self.current_state
    
    def _process_gesture(self, gyro_x, gyro_y, raw_movement):
        """Traite les données pour détecter un geste complet"""
        movement_magnitude = (gyro_x**2 + gyro_y**2)**0.5

        # Début d'un geste (mouvement significatif)
        if not self.gesture_in_progress and movement_magnitude > GESTURE_START_THRESHOLD:
            self.gesture_in_progress = True
            self.gesture_buffer = [(gyro_x, gyro_y, raw_movement)]
            self.gesture_start_time = 0
            return None

        # Accumulation des données pendant le geste
        if self.gesture_in_progress:
            self.gesture_buffer.append((gyro_x, gyro_y, raw_movement))
            self.gesture_start_time += 1
            
            # Fin du geste (retour au calme)
            if movement_magnitude < GESTURE_END_THRESHOLD:
                if self.gesture_start_time >= MIN_GESTURE_FRAMES:
                    gesture_result = self._analyze_gesture_buffer()
                    self.gesture_in_progress = False
                    self.gesture_buffer = []
                    return gesture_result
                elif self.gesture_start_time > MAX_GESTURE_FRAMES:
                    # Geste trop long, on l'annule
                    self.gesture_in_progress = False
                    self.gesture_buffer = []
            
        return None
    
    def _analyze_gesture_buffer(self):
        """Analyse le buffer de geste pour déterminer la direction dominante"""
        if not self.gesture_buffer:
            return None
            
        # Calculer la moyenne des valeurs de gyroscope
        avg_x = sum(x for x, _, _ in self.gesture_buffer) / len(self.gesture_buffer)
        avg_y = sum(y for _, y, _ in self.gesture_buffer) / len(self.gesture_buffer)
        
        # Compter les directions
        direction_counts = {}
        for _, _, direction in self.gesture_buffer:
            if direction != 'CENTRE':
                direction_counts[direction] = direction_counts.get(direction, 0) + 1
        
        if not direction_counts:
            return None
            
        # Trouver la direction dominante
        dominant_direction = max(direction_counts.items(), key=lambda x: x[1])
        direction = dominant_direction[0]
        count = dominant_direction[1]
        
        # Vérifier que la direction dominante représente au moins 40% des échantillons
        if count / len(self.gesture_buffer) < 0.4:
            # Si pas de direction clairement dominante, utiliser les moyennes
            return self._get_raw_movement(avg_x, avg_y)
            
        return direction
    
    def _get_raw_movement(self, gyro_x, gyro_y):
        """Détermine le mouvement brut basé sur les valeurs gyro"""
        # Valeurs inversées pour correspondre à l'intuition
        h = -gyro_x
        v = -gyro_y
        
        # Diagonales
        if abs(h) > DIAGONAL_THRESHOLD and abs(v) > DIAGONAL_THRESHOLD:
            if h > 0 and v < 0:
                return 'DROITE HAUT'
            elif h > 0 and v > 0:
                return 'DROITE BAS'
            elif h < 0 and v < 0:
                return 'GAUCHE HAUT'
            elif h < 0 and v > 0:
                return 'GAUCHE BAS'
        
        # Directions simples
        if abs(h) > abs(v):
            if h > self.movement_threshold:
                return 'DROITE'
            elif h < -self.movement_threshold:
                return 'GAUCHE'
        else:
            if v > self.movement_threshold:
                return 'BAS'
            elif v < -self.movement_threshold:
                return 'HAUT'
                
        return 'CENTRE'
    
    def _is_opposite_movement(self, current, previous):
        """Vérifie si deux mouvements sont opposés"""
        opposites = {
            'GAUCHE': 'DROITE',
            'DROITE': 'GAUCHE',
            'HAUT': 'BAS',
            'BAS': 'HAUT',
            'GAUCHE HAUT': 'DROITE BAS',
            'DROITE BAS': 'GAUCHE HAUT',
            'GAUCHE BAS': 'DROITE HAUT',
            'DROITE HAUT': 'GAUCHE BAS'
        }
        return opposites.get(current) == previous
    
    def reset(self):
        """Réinitialise le tracker"""
        self.__init__()
        
    def is_returning_to_center(self):
        """Indique si on est en mode retour au centre"""
        return self.return_to_center_mode
        
    def is_gesture_in_progress(self):
        """Indique si un geste est en cours"""
        return self.gesture_in_progress