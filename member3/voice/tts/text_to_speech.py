# pyrefly: ignore [missing-import]
import pyttsx3
import os
import re
import threading


_engine_lock = threading.Lock()
_speech_run_lock = threading.Lock()
_active_engine = None

DEFAULT_VOICE_HINTS = ("aria", "jenny", "zira", "hazel", "david", "mark")
DEFAULT_RATE = 155


def _voice_hints() -> tuple[str, ...]:
    raw_hints = os.getenv("TTS_VOICE_HINTS", ",".join(DEFAULT_VOICE_HINTS))
    hints = tuple(item.strip().lower() for item in raw_hints.split(",") if item.strip())
    return hints or DEFAULT_VOICE_HINTS


def _speech_rate() -> int:
    try:
        rate = int(os.getenv("TTS_RATE", str(DEFAULT_RATE)))
    except ValueError:
        return DEFAULT_RATE
    return min(max(rate, 120), 250)


def _select_voice(voices, hints: tuple[str, ...]):
    """Prefer a natural installed SAPI voice without requiring a fixed ID."""
    for hint in hints:
        for voice in voices:
            identity = f"{getattr(voice, 'name', '')} {getattr(voice, 'id', '')}".lower()
            if hint in identity:
                return voice
    return None


def _plain_speech_text(text: str) -> str:
    """Make Markdown/chat text sound like normal prose when read aloud."""
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def stop_speaking() -> bool:
    """Stop the currently active text-to-speech engine, if there is one."""
    with _engine_lock:
        engine = _active_engine

    if engine is None:
        return False

    try:
        engine.stop()
        return True
    except Exception as error:
        print(f"[TTS STOP ERROR] {error}")
        return False


def get_zira_engine():
    """
    Creates and configures the Windows SAPI5
    Microsoft Zira text-to-speech engine.

    Returns:
        pyttsx3.Engine: Configured Zira engine.
    """

    # Do not require a particular Windows voice. Many local installations do
    # not include Zira, while the system default is still a usable TTS voice.
    engine = pyttsx3.init("sapi5")

    voices = engine.getProperty("voices")

    selected_voice = _select_voice(voices, _voice_hints())
    if selected_voice is not None:
        engine.setProperty("voice", selected_voice.id)

    # Slightly slower and easier to understand
    engine.setProperty(
        "rate",
        _speech_rate()
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

    global _active_engine

    # Only one server-side voice may run at a time. The separate stop endpoint
    # can still call engine.stop() while this thread is in runAndWait().
    with _speech_run_lock:
        engine = None

        try:
            engine = get_zira_engine()
            with _engine_lock:
                _active_engine = engine

            engine.say(_plain_speech_text(text))
            engine.runAndWait()

        except Exception as e:
            print(f"[ERROR] Text-to-speech failed: {e}")
            raise

        finally:
            with _engine_lock:
                if _active_engine is engine:
                    _active_engine = None

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
