import os
import tempfile
import time
import msvcrt

# pyrefly: ignore [missing-import]
import numpy as np
# pyrefly: ignore [missing-import]
import sounddevice as sd
# pyrefly: ignore [missing-import]
import scipy.io.wavfile as wav


# Whisper model cache
_model_cache = {}

SAMPLE_RATE = 16000
CHANNELS = 1


def get_whisper_model(model_size: str = "tiny"):
    """
    Loads Whisper only when it is actually needed.
    The model is then kept in memory for later calls.
    """

    global _model_cache

    if model_size not in _model_cache:

        print(
            f"[INFO] Loading Whisper '{model_size}' model..."
        )

        # Lazy import: Whisper is not loaded at startup
        # pyrefly: ignore [missing-import]
        import whisper

        _model_cache[model_size] = whisper.load_model(
            model_size
        )

        print("[INFO] Whisper model ready.")

    return _model_cache[model_size]


def record_voice() -> np.ndarray:
    """
    Records microphone audio until the user presses S.

    Returns:
        np.ndarray: Recorded audio as int16 samples.
    """

    print("\n" + "=" * 60)
    print("                VOICE INPUT")
    print("=" * 60)

    input("Press ENTER to start recording...")

    print("\n[INFO] Recording started.")
    print("[INFO] Speak normally.")
    print("[INFO] Press S to stop recording.")
    print()

    audio_chunks = []

    def callback(indata, frames, time_info, status):

        if status:
            print(f"[WARNING] {status}")

        audio_chunks.append(indata.copy())

    try:

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            callback=callback
        ):

            while True:

                # Check keyboard without blocking
                if msvcrt.kbhit():

                    key = msvcrt.getwch()

                    if key.lower() == "s":

                        print(
                            "\n[INFO] Recording stopped."
                        )

                        break

                time.sleep(0.05)

    except Exception as e:

        print(
            f"[ERROR] Microphone recording failed: {e}"
        )

        raise

    if not audio_chunks:

        raise RuntimeError(
            "No audio was recorded."
        )

    return np.concatenate(
        audio_chunks,
        axis=0
    )


def reduce_noise(audio_data: np.ndarray) -> np.ndarray:
    """
    Reduces steady background noise.

    noisereduce is imported only when this function
    is actually called.
    """

    print(
        "[INFO] Removing background noise..."
    )

    # Lazy import
    # pyrefly: ignore [missing-import]
    import noisereduce as nr

    audio_float = (
        audio_data.astype(np.float32)
        / 32768.0
    )

    try:

        cleaned_audio = nr.reduce_noise(
            y=audio_float,
            sr=SAMPLE_RATE,
            stationary=True
        )

    except Exception as e:

        print(
            f"[WARNING] Noise reduction failed: {e}"
        )

        print(
            "[INFO] Using original audio."
        )

        cleaned_audio = audio_float

    cleaned_audio = np.clip(
        cleaned_audio,
        -1.0,
        1.0
    )

    return np.int16(
        cleaned_audio * 32767
    )


def transcribe_audio(audio_data: np.ndarray) -> str:
    """
    Saves cleaned audio temporarily and transcribes it
    using Whisper.

    Returns:
        str: Recognized text.
    """

    temp_wav_path = None

    try:

        fd, temp_wav_path = tempfile.mkstemp(
            suffix=".wav"
        )

        os.close(fd)

        wav.write(
            temp_wav_path,
            SAMPLE_RATE,
            audio_data
        )

        print(
            "[INFO] Transcribing audio..."
        )

        model = get_whisper_model("tiny")

        result = model.transcribe(
            temp_wav_path,
            fp16=False
        )

        return result.get(
            "text",
            ""
        ).strip()

    finally:

        if (
            temp_wav_path
            and os.path.exists(temp_wav_path)
        ):

            try:

                os.remove(temp_wav_path)

            except Exception:
                pass


def transcribe_voice_note() -> str:
    """
    Main integration function.

    Records the user's voice, removes background noise,
    transcribes the audio, and returns the recognized text.

    Returns:
        str: Transcribed user input.
    """

    audio_data = record_voice()

    cleaned_audio = reduce_noise(
        audio_data
    )

    text = transcribe_audio(
        cleaned_audio
    )

    print("\n" + "=" * 60)
    print("                  TRANSCRIPTION")
    print("=" * 60)

    if text:

        print(
            f'Recognized Text: "{text}"'
        )

    else:

        print(
            "[WARNING] No speech detected."
        )

    print("=" * 60)

    return text


def main():

    try:

        text = transcribe_voice_note()

        print(
            f"\n[RESULT] Returned text: {text}"
        )

    except KeyboardInterrupt:

        print(
            "\n[INFO] Operation cancelled."
        )

    except Exception as e:

        print(
            f"\n[ERROR] An error occurred: {e}"
        )


if __name__ == "__main__":
    main()