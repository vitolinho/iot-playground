import time
from pynput.keyboard import Key, Controller

keyboard = Controller()

while True:
    time.sleedup(5)
    
    # flèche du haut
    keyboard.press(Key.up)
    keyboard.release(Key.up)
    time.sleep(2)

    # flèche du haut
    keyboard.press(Key.down)
    keyboard.release(Key.down)

    # flèche de droite
    keyboard.press(Key.right)
    keyboard.release(Key.right)

    # flèche de gauche
    keyboard.press(Key.left)
    keyboard.release(Key.left)
