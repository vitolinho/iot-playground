import sounddevice as sd
import numpy as np

def test_microphone():
    # List all audio devices
    print("\nAvailable audio devices:")
    print(sd.query_devices())
    
    print("\nDefault input device:")
    print(sd.query_devices(kind='input'))
    
    # Test recording
    duration = 3  # seconds
    samplerate = 16000
    
    print("\nStarting 3 second recording test...")
    audio = sd.rec(int(samplerate * duration), samplerate=samplerate, 
                  channels=1, dtype=np.float32)
    sd.wait()
    
    # Check if audio was recorded
    if np.any(audio):
        print("✅ Microphone is working! Audio levels detected.")
        print(f"Max audio level: {np.max(np.abs(audio))}")
    else:
        print("❌ No audio detected. Check your microphone.")

if __name__ == "__main__":
    test_microphone()