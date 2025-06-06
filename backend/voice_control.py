import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
from pynput.keyboard import Key, Controller
from pynput.mouse import Button, Controller as MouseController  # Add this import
import scipy.io.wavfile
import time

def simulate_key(keyboard, key):
    keyboard.press(key)
    keyboard.release(key)

def simulate_mouse_click(mouse, button):
    """Simulate a mouse click with specified button"""
    mouse.click(button)
    print(f"🖱️ Mouse {button} clicked")

def hold_key(keyboard, key):
    """Hold a key down"""
    keyboard.press(key)
    print(f"⌨️ Holding {key.upper()}")

def release_key(keyboard, key):
    """Release a held key"""
    keyboard.release(key)
    print(f"⌨️ Released {key.upper()}")

def execute_command(text, keyboard):
    """Execute a single command"""
    if "stop" in text:
        # Release all held keys
        for key in ['z', 's', 'q', 'd']:
            release_key(keyboard, key)
        print("🛑 All keys released")
        return

    if "top" in text or "up" in text:
        print("⬆️ Moving forward")
        hold_key(keyboard, 'z')
    elif "down" in text:
        print("⬇️ Moving backward")
        hold_key(keyboard, 's')
    elif "left" in text:
        print("👈 Moving left")
        hold_key(keyboard, 'q')
    elif "right" in text:
        print("👉 Moving right")
        hold_key(keyboard, 'd')
    elif "inventory" in text:
        print("🎒 Opening inventory")
        simulate_key(keyboard, 'e')

def execute_repeated_command(text, keyboard, count):
    """Execute a command multiple times"""
    print(f"🔄 Executing '{text}' {count} times")
    for i in range(count):
        if "top" in text or "up" in text:
            print(f"⌨️ Pressing UP (#{i+1}/{count})")
            simulate_key(keyboard, Key.up)
        elif "down" in text:
            print(f"⌨️ Pressing DOWN (#{i+1}/{count})")
            simulate_key(keyboard, Key.down)
        elif "left" in text:
            print(f"⌨️ Pressing LEFT (#{i+1}/{count})")
            print(f"👈 LEFT command activated (#{i+1}/{count})")
            simulate_key(keyboard, Key.left)
            print(f"✅ LEFT command completed (#{i+1}/{count})")
        elif "right" in text:
            print(f"⌨️ Pressing RIGHT (#{i+1}/{count})")
            print(f"👉 RIGHT command activated (#{i+1}/{count})")
            simulate_key(keyboard, Key.right)
            print(f"✅ RIGHT command completed (#{i+1}/{count})")
        time.sleep(0.1)

def transcribe_audio():
    print("✨ Initializing...")
    model = WhisperModel("tiny", device="cpu", compute_type="int8", num_workers=2)
    keyboard = Controller()
    mouse = MouseController()
    keyboard_enabled = True  # Changed to True - Enabled by default
    print("✅ Initialization complete")
    print("🎮 Keyboard controls ENABLED by default")
    
    # Optimized audio parameters
    samplerate = 16000
    chunk_duration = 0.5  # Reduced to 200ms for faster response
    chunk_size = int(samplerate * chunk_duration)
    device = 1
    
    def audio_callback(indata, frames, time, status):
        if status:
            print(f"⚠️ Status: {status}")
            return
        
        nonlocal keyboard_enabled  # Pour pouvoir modifier la variable
        
        # Simplified audio processing
        audio = indata.copy().squeeze()
        audio_level = np.max(np.abs(audio))
        
        # Audio level logging
        print(f"\n📊 Audio level: {audio_level:.4f}")
        
        if audio_level > 0.1:
            print("🎙️ Sound detected!")
            try:
                segments, _ = model.transcribe(
                    audio,
                    language="en",
                    beam_size=1,
                    vad_filter=False,
                    initial_prompt="top up down left right stop inventory right click left click",
                    condition_on_previous_text=False,
                    no_speech_threshold=0.5,
                    compression_ratio_threshold=2.4,
                    temperature=0
                )
                
                # Get first segment only
                for segment in segments:
                    text = segment.text.lower().strip()
                    if text:
                        # Clean up repeated words
                        words = text.split()
                        unique_words = []
                        for word in words:
                            if word not in unique_words:
                                unique_words.append(word)
                        
                        cleaned_text = ' '.join(unique_words)
                        print(f"\n🗣️ Detected: '{cleaned_text}'")
                        
                        # Check for keyboard activation/deactivation
                        if "keyboard on" in cleaned_text:
                            keyboard_enabled = True
                            print("🎮 Keyboard controls ENABLED")
                        elif "keyboard off" in cleaned_text:
                            keyboard_enabled = False
                            print("🔒 Keyboard controls DISABLED")
                        
                        # Only process commands if keyboard is enabled
                        elif keyboard_enabled:
                            if "right click" in cleaned_text:  # Check for clicks first
                                print("🖱️ RIGHT CLICK command")
                                simulate_mouse_click(mouse, Button.right)
                            elif "left click" in cleaned_text:
                                print("🖱️ LEFT CLICK command")
                                simulate_mouse_click(mouse, Button.left)
                            elif "right" in cleaned_text:
                                print("👉 RIGHT command")
                                simulate_key(keyboard, Key.right)
                            elif "left" in cleaned_text:
                                print("👈 LEFT command")
                                simulate_key(keyboard, Key.left)
                            elif "up" in cleaned_text or "top" in cleaned_text:
                                print("⬆️ UP command")
                                simulate_key(keyboard, Key.up)
                            elif "down" in cleaned_text:
                                print("⬇️ DOWN command")
                                simulate_key(keyboard, Key.down)
                        elif not keyboard_enabled and any(cmd in cleaned_text for cmd in ["right", "left", "up", "top", "down", "jump"]):
                            print("🔒 Commands ignored - Keyboard is DISABLED")

                    break  # Only process first segment
                        
            except Exception as e:
                print(f"❌ Error: {str(e)}")
            
            print("-" * 30)
    
    try:
        print("\n🎤 Starting continuous recording...")
        with sd.InputStream(
            samplerate=samplerate,
            channels=1,
            dtype=np.float32,
            blocksize=chunk_size,
            device=device,
            callback=audio_callback
        ):
            print("✅ Ready!")
            while True:
                time.sleep(0.05)  # Reduced sleep time
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")

if __name__ == "__main__":
    transcribe_audio()

