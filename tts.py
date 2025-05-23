import pyttsx3
import tempfile
import os

def speak(text):
    try:
        print("TTS: Starting engine...")
        engine = pyttsx3.init()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:

            audio_path = tmpfile.name
        print(f"TTS: Saving to {audio_path}")
        engine.save_to_file(text, audio_path)
        engine.runAndWait()
        print(f"TTS: File created: {os.path.exists(audio_path)}")
        return audio_path if os.path.exists(audio_path) else None
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

