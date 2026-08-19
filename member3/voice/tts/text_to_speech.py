
# pyrefly: ignore [missing-import]
import pyttsx3


def speak_text(text: str) -> None:
    """Speak the given text using Microsoft Zira on Windows."""

    if not text or not text.strip():
        return

    print(f'[INFO] Speaking: "{text}"')

    try:
        engine = pyttsx3.init("sapi5")

        # Find Microsoft Zira
        voices = engine.getProperty("voices")
        zira_voice = None

        for voice in voices:
            if voice.name and "zira" in voice.name.lower():
                zira_voice = voice
                break

        if zira_voice is None:
            print("[ERROR] Microsoft Zira was not found.")
            engine.stop()
            return

        # Select Zira
        engine.setProperty("voice", zira_voice.id)

        # Slightly slower for more natural speech
        engine.setProperty("rate", 135)

        # Full volume
        engine.setProperty("volume", 1.0)

        print(f"[INFO] Selected voice: {zira_voice.name}")
        print(f"[INFO] Speech rate: {engine.getProperty('rate')}")

        # Give very short text a little more natural pacing
        if len(text.strip().split()) <= 3:
            text = text.strip().rstrip(".!?") + "."

        engine.say(text)
        engine.runAndWait()

        engine.stop()

    except Exception as e:
        print(f"[ERROR] Text-to-speech failed: {e}")


def main():
    print("=" * 60)
    print("       PHASE 2B: TEXT-TO-SPEECH PROTOTYPE")
    print("=" * 60)

    test_sentences = [
        "Hello.",
        "Hello, how are you?",
        "Hello. This is a test of the text to speech module."
    ]

    print("\n[INFO] Testing Microsoft Zira...\n")

    for sentence in test_sentences:
        print(f'[TEST] "{sentence}"')
        speak_text(sentence)

    print("\n[INFO] TTS testing completed.")


if __name__ == "__main__":
    main()
