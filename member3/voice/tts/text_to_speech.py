# pyrefly: ignore [missing-import]
import pyttsx3

def speak_text(text: str) -> None:
    """
    Speaks the given text through the computer's default audio output using SAPI5.
    
    Args:
        text (str): The text content to be spoken.
    """
    if not text:
        return
        
    try:
        print(f"[INFO] Speaking: \"{text}\"")
        # Initialize with Windows SAPI5 engine
        engine = pyttsx3.init('sapi5')
        
        # Enumerate available voices and select a suitable English voice if one is available
        voices = engine.getProperty('voices')
        selected_voice = None
        for voice in voices:
            is_english = False
            # Check voice.languages if populated
            if hasattr(voice, 'languages') and voice.languages:
                for lang in voice.languages:
                    if "en" in str(lang).lower():
                        is_english = True
                        break
            # Fallback to checking name or id
            if not is_english:
                voice_str = f"{voice.name} {voice.id}".lower()
                if "english" in voice_str or "en-us" in voice_str or "en-gb" in voice_str or "en_" in voice_str:
                    is_english = True
            
            if is_english:
                selected_voice = voice
                break
        
        if selected_voice:
            engine.setProperty('voice', selected_voice.id)
            print(f"[DEBUG] Selected voice: {selected_voice.name}")
        else:
            print("[DEBUG] No specific English voice found. Using default voice.")

        # Set speech rate to around 150 words per minute (WPM)
        engine.setProperty('rate', 150)
        
        # Set volume to 1.0 (max)
        engine.setProperty('volume', 1.0)
            
        print(f"[DEBUG] Speech rate: {engine.getProperty('rate')} WPM")
        
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[ERROR] Failed to run text-to-speech: {e}")
        raise e

def main():
    print("=" * 60)
    print("         PHASE 2B: TEXT-TO-SPEECH PROTOTYPE")
    print("=" * 60)
    
    test_sentence = "Hello, this is the text to speech module for our RAG chatbot."
    speak_text(test_sentence)

if __name__ == "__main__":
    main()
