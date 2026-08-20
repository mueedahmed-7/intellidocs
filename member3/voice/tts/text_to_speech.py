# pyrefly: ignore [missing-import]
import pyttsx3


def get_zira_engine():
    """
    Creates and configures the Windows SAPI5
    Microsoft Zira text-to-speech engine.

    Returns:
        pyttsx3.Engine: Configured Zira engine.
    """

    engine = pyttsx3.init("sapi5")

    voices = engine.getProperty("voices")

    zira_voice = None

    for voice in voices:

        if voice.name and "zira" in voice.name.lower():

            zira_voice = voice
            break

    if zira_voice is None:

        engine.stop()

        raise RuntimeError(
            "Microsoft Zira voice was not found. "
            "Please make sure the Windows Zira voice is installed."
        )

    # Select Microsoft Zira
    engine.setProperty(
        "voice",
        zira_voice.id
    )

    # Slightly slower and easier to understand
    engine.setProperty(
        "rate",
        135
    )

    # Full volume
    engine.setProperty(
        "volume",
        1.0
    )

    return engine


def speak_text(text: str) -> None:
    """
    Main TTS function for integration.

    Takes text and speaks it using Microsoft Zira.

    Args:
        text: Text to speak.
    """

    if not text or not text.strip():

        print(
            "[WARNING] No text provided for TTS."
        )

        return

    print(
        f'[INFO] Speaking: "{text}"'
    )

    engine = None

    try:

        engine = get_zira_engine()

        engine.say(
            text.strip()
        )

        engine.runAndWait()

    except Exception as e:

        print(
            f"[ERROR] Text-to-speech failed: {e}"
        )

        raise

    finally:

        if engine is not None:

            try:
                engine.stop()

            except Exception:
                pass


def main():

    print("=" * 60)
    print("       PHASE 2B: TEXT-TO-SPEECH PROTOTYPE")
    print("=" * 60)

    test_text = (
    "Hello. Welcome to our AI powered RAG chatbot. "
    "This system can understand your voice, process your question, "
    "search the available documents, and provide an answer. "
    "The speech to text system converts your voice into text, "
    "while the text to speech system converts the chatbot response "
    "back into natural spoken audio. "
    "Our face recognition system can also verify the user's identity "
    "before allowing access to the system. "
    "This is a complete test of the voice output pipeline."
    )

    try:

        speak_text(
            test_text
        )

        print(
            "\n[INFO] TTS test completed successfully."
        )

    except Exception as e:

        print(
            f"\n[ERROR] TTS test failed: {e}"
        )


if __name__ == "__main__":

    main()