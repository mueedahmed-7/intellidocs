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
# pyrefly: ignore [missing-import]
import whisper
# pyrefly: ignore [missing-import]
import noisereduce as nr


# Global cache for the Whisper model
_model_cache = {}

SAMPLE_RATE = 16000
CHANNELS = 1


def get_whisper_model(model_size: str = "tiny"):
    """
    Loads the Whisper model once and reuses it.
    """

    global _model_cache

    if model_size not in _model_cache:
        print(f"[INFO] Loading Whisper '{model_size}' model...")
        _model_cache[model_size] = whisper.load_model(model_size)

    return _model_cache[model_size]


def record_voice_note() -> str:
    """
    Records microphone audio until the user presses S.

    Returns:
        str: Path to the temporary WAV file.
    """

    print("\n" + "=" * 60)
    print("                VOICE NOTE MODE")
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

    # Combine recorded chunks
    audio_data = np.concatenate(
        audio_chunks,
        axis=0
    )

    print(
        "[INFO] Recording captured."
    )

    # Convert int16 audio to float32
    audio_float = (
        audio_data.astype(np.float32)
        / 32768.0
    )

    # --------------------------------------------------
    # NOISE REDUCTION
    # --------------------------------------------------

    print(
        "[INFO] Removing background noise..."
    )

    try:

        reduced_audio = nr.reduce_noise(
            y=audio_float,
            sr=SAMPLE_RATE,
            stationary=True
        )

    except Exception as e:

        print(
            f"[WARNING] Noise reduction failed: {e}"
        )

        print(
            "[INFO] Continuing with original audio."
        )

        reduced_audio = audio_float

    # Convert back to int16 for WAV
    reduced_audio = np.clip(
        reduced_audio,
        -1.0,
        1.0
    )

    reduced_audio = np.int16(
        reduced_audio * 32767
    )

    # Create temporary WAV file
    fd, temp_wav_path = tempfile.mkstemp(
        suffix=".wav"
    )

    os.close(fd)

    wav.write(
        temp_wav_path,
        SAMPLE_RATE,
        reduced_audio
    )

    print(
        "[INFO] Cleaned audio saved temporarily."
    )

    return temp_wav_path


def transcribe_voice_note(temp_wav_path: str) -> str:
    """
    Transcribes the cleaned voice note using Whisper.
    """

    model = get_whisper_model("tiny")

    print(
        "\n[INFO] Transcribing voice note..."
    )

    result = model.transcribe(
        temp_wav_path,
        fp16=False
    )

    return result.get(
        "text",
        ""
    ).strip()


def main():

    temp_wav_path = None

    try:

        temp_wav_path = record_voice_note()

        print(
            "\n[INFO] Recording completed."
        )

        transcription = transcribe_voice_note(
            temp_wav_path
        )

        print("\n" + "=" * 60)
        print("                  TRANSCRIPTION RESULT")
        print("=" * 60)

        if transcription:

            print(
                f'Recognized Text: "{transcription}"'
            )

        else:

            print(
                "[WARNING] No speech detected."
            )

        print("=" * 60)

    except KeyboardInterrupt:

        print(
            "\n[INFO] Operation cancelled."
        )

    except Exception as e:

        print(
            f"\n[ERROR] An error occurred: {e}"
        )

    finally:

        # Delete temporary WAV file
        if (
            temp_wav_path
            and os.path.exists(temp_wav_path)
        ):

            try:

                os.remove(temp_wav_path)

                print(
                    "[INFO] Temporary audio file cleaned up."
                )

            except Exception as e:

                print(
                    f"[WARNING] Could not delete "
                    f"temporary file: {e}"
                )


if __name__ == "__main__":
    main()