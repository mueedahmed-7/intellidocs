import pyttsx3


def speak_text(text: str) -> None:
    """Speak the given text using Microsoft Zira on Windows."""

    if not text.strip():
        return

    print(f'[INFO] Speaking: "{text}"')

    engine = pyttsx3.init("sapi5")

    # Get all installed Windows voices
    voices = engine.getProperty("voices")

    print("\n[INFO] Available voices:")
    for i, voice in enumerate(voices):
        print(f"  {i}: {voice.name}")
        print(f"     ID: {voice.id}")

    # Find Microsoft Zira
    zira_voice = None

    for voice in voices:
        name = voice.name.lower()

        if "zira" in name:
            zira_voice = voice
            break

    if zira_voice is None:
        print("\n[ERROR] Microsoft Zira was not found.")
        print("[ERROR] Available voices are listed above.")
        engine.stop()
        return

    # Select Zira
    engine.setProperty("voice", zira_voice.id)

    # Slow down the speech
    engine.setProperty("rate", 145)

    # Maximum volume
    engine.setProperty("volume", 1.0)

    print(f"\n[INFO] Selected voice: {zira_voice.name}")
    print(f"[INFO] Voice ID: {zira_voice.id}")
    print(f"[INFO] Speech rate: {engine.getProperty('rate')}")

    engine.say(text)
    engine.runAndWait()

    engine.stop()


def main():
    print("=" * 60)
    print("       PHASE 2B: TEXT-TO-SPEECH PROTOTYPE")
    print("=" * 60)

    test_sentence = "Hello. This is a test."

    speak_text(test_sentence)


if __name__ == "__main__":
    main()