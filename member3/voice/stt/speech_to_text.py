import os
import tempfile
import sounddevice as sd
import scipy.io.wavfile as wav
import whisper

# Global cache for the Whisper model to avoid reloading it on every function call
_model_cache = {}

def get_whisper_model(model_size: str = "tiny"):
    """
    Retrieves or loads the specified Whisper model from the cache.
    
    Args:
        model_size (str): Size of the Whisper model to load (e.g., 'tiny', 'base').
        
    Returns:
        whisper.Whisper: The loaded Whisper model.
    """
    global _model_cache
    if model_size not in _model_cache:
        print(f"[INFO] Loading Whisper '{model_size}' model...")
        _model_cache[model_size] = whisper.load_model(model_size)
    return _model_cache[model_size]

def transcribe_microphone(duration: int = 5) -> str:
    """
    Records microphone audio at 16 kHz mono, temporarily saves it as a WAV file,
    transcribes it using Whisper, returns the recognized text, and cleans up the
    temporary WAV file.
    
    Args:
        duration (int): Duration of the recording in seconds. Default is 5.
        
    Returns:
        str: The recognized text transcribed from the audio.
    """
    sample_rate = 16000
    channels = 1
    
    # Generate a temporary file path for the WAV audio
    fd, temp_wav_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    
    try:
        print(f"\n[INFO] Recording microphone input for {duration} seconds... Please speak.")
        # Record microphone input
        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=channels,
            dtype='int16'
        )
        sd.wait()  # Wait until the recording is finished
        print("[INFO] Recording completed. Saving to temporary WAV file...")
        
        # Save recording to WAV file
        wav.write(temp_wav_path, sample_rate, audio_data)
        
        # Get the Whisper model (using 'tiny' model by default)
        model = get_whisper_model("tiny")
        
        print("[INFO] Transcribing audio...")
        result = model.transcribe(temp_wav_path)
        
        text = result.get("text", "").strip()
        return text
        
    finally:
        # Clean up temporary WAV file
        if os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
                print(f"[INFO] Cleaned up temporary file: {temp_wav_path}")
            except Exception as e:
                print(f"[WARNING] Failed to delete temporary file '{temp_wav_path}': {e}")

def main():
    print("=" * 60)
    print("         PHASE 2A: SPEECH-TO-TEXT PROTOTYPE")
    print("=" * 60)
    
    try:
        duration_input = input("Enter recording duration in seconds (default 5): ").strip()
        duration = int(duration_input) if duration_input else 5
    except ValueError:
        print("[WARNING] Invalid duration. Using default of 5 seconds.")
        duration = 5

    try:
        transcription = transcribe_microphone(duration)
        print("\n" + "=" * 60)
        print("                  TRANSCRIPTION RESULT")
        print("=" * 60)
        print(f"Recognized Text: \"{transcription}\"")
        print("=" * 60)
    except Exception as e:
        print(f"[ERROR] An error occurred during transcription: {e}")

if __name__ == "__main__":
    main()
