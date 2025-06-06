# config.py - Configuration centralisée

# Paramètres de mouvement souris
MOUSE_SPEED = 15
MOUSE_ACCELERATION = 1.5

# Paramètres clavier
KEY_REPEAT_DELAY = 0.1

# Seuils de détection
MOVEMENT_THRESHOLD = 8      # Seuil pour mouvement normal
RETURN_THRESHOLD = 5        # Seuil plus bas pour le retour
STABLE_FRAMES = 5           # Frames de stabilité nécessaires
DIAGONAL_THRESHOLD = 20     # Seuil pour les diagonales

# Paramètres de détection de gestes
HISTORY_SIZE = 30           # Taille de l'historique des mouvements
GESTURE_START_THRESHOLD = 15  # Seuil pour démarrer la détection d'un geste
GESTURE_END_THRESHOLD = 6    # Seuil pour terminer la détection d'un geste
MIN_GESTURE_FRAMES = 5      # Nombre minimum de frames pour un geste valide
MAX_GESTURE_FRAMES = 30     # Nombre maximum de frames pour un geste
GESTURE_COOLDOWN_FRAMES = 10 # Temps de repos après un geste

# Actions au centre
CENTER_HOLD_TIME = 0.5  # Temps avant action au centre
CENTER_COOLDOWN = 1.0   # Cooldown après action

# Mode par défaut
DEFAULT_MODE = "mouse"