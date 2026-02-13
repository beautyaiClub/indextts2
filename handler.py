import runpod
import os
import sys
import base64
import traceback
import requests
import tempfile
import numpy as np
import soundfile as sf
from io import BytesIO

# Add IndexTTS2 to path
sys.path.append('/app/index-tts')

# Import IndexTTS2 (adjust based on actual API)
try:
    # These imports may need adjustment based on actual IndexTTS2 structure
    from inference import IndexTTS2Inference
    MODEL_AVAILABLE = True
except ImportError:
    print("Warning: IndexTTS2 modules not found. Running in mock mode.")
    MODEL_AVAILABLE = False

# Global model instance
model = None

def download_audio_from_url(url):
    """
    Download audio file from URL and save to temporary file.
    Returns the file path.
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Create temporary file
        suffix = '.mp3' if 'mp3' in url.lower() else '.wav'
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.write(response.content)
        temp_file.close()

        return temp_file.name
    except Exception as e:
        print(f"Error downloading audio from URL: {str(e)}")
        return None

def load_model():
    """
    Load the IndexTTS2 model on cold start.
    """
    global model
    try:
        print("Loading IndexTTS2 model...")

        if not MODEL_AVAILABLE:
            print("Model modules not available, running in mock mode")
            return True

        model_path = os.environ.get('MODEL_PATH', '/app/models')

        # Initialize IndexTTS2 model
        # Adjust this based on actual IndexTTS2 API
        model = IndexTTS2Inference(
            model_dir=model_path,
            device='cuda'
        )

        print("Model loaded successfully")
        return True

    except Exception as e:
        print(f"Error loading model: {str(e)}")
        traceback.print_exc()
        return False

def handler(job):
    """
    RunPod serverless handler for IndexTTS2.

    Expected input format:
    {
        "input": {
            "text": "Text to synthesize",
            "speaker_audio": "URL or base64 encoded audio",
            "top_k": 30,
            "top_p": 0.8,
            "num_beams": 3,
            "temperature": 0.8,
            "emotion_scale": 1,
            "length_penalty": 0,
            "max_mel_tokens": 1500,
            "randomize_emotion": false,
            "repetition_penalty": 10,
            "interval_silence_ms": 200,
            "max_text_tokens_per_segment": 120
        }
    }
    """
    try:
        job_input = job["input"]

        # Required parameter
        text = job_input.get("text", "")
        if not text:
            return {"error": "No text provided"}

        # Optional parameters with defaults matching Replicate
        speaker_audio = job_input.get("speaker_audio", None)
        top_k = job_input.get("top_k", 30)
        top_p = job_input.get("top_p", 0.8)
        num_beams = job_input.get("num_beams", 3)
        temperature = job_input.get("temperature", 0.8)
        emotion_scale = job_input.get("emotion_scale", 1.0)
        length_penalty = job_input.get("length_penalty", 0)
        max_mel_tokens = job_input.get("max_mel_tokens", 1500)
        randomize_emotion = job_input.get("randomize_emotion", False)
        repetition_penalty = job_input.get("repetition_penalty", 10)
        interval_silence_ms = job_input.get("interval_silence_ms", 200)
        max_text_tokens_per_segment = job_input.get("max_text_tokens_per_segment", 120)

        print(f"Processing TTS request: {text[:100]}...")

        # Handle speaker audio
        speaker_audio_path = None
        if speaker_audio:
            if speaker_audio.startswith('http://') or speaker_audio.startswith('https://'):
                # Download from URL
                print(f"Downloading speaker audio from URL...")
                speaker_audio_path = download_audio_from_url(speaker_audio)
                if not speaker_audio_path:
                    return {"error": "Failed to download speaker audio"}
            else:
                # Assume base64 encoded audio
                try:
                    audio_data = base64.b64decode(speaker_audio)
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                    temp_file.write(audio_data)
                    temp_file.close()
                    speaker_audio_path = temp_file.name
                except Exception as e:
                    return {"error": f"Failed to decode speaker audio: {str(e)}"}

        # Generate audio using IndexTTS2
        if MODEL_AVAILABLE and model is not None:
            try:
                # Call IndexTTS2 model
                # Adjust this based on actual IndexTTS2 API
                audio_array, sample_rate = model.synthesize(
                    text=text,
                    reference_audio=speaker_audio_path,
                    top_k=top_k,
                    top_p=top_p,
                    num_beams=num_beams,
                    temperature=temperature,
                    emotion_scale=emotion_scale,
                    length_penalty=length_penalty,
                    max_mel_tokens=max_mel_tokens,
                    randomize_emotion=randomize_emotion,
                    repetition_penalty=repetition_penalty,
                    interval_silence_ms=interval_silence_ms,
                    max_text_tokens_per_segment=max_text_tokens_per_segment
                )

                # Convert audio to WAV format in memory
                wav_buffer = BytesIO()
                sf.write(wav_buffer, audio_array, sample_rate, format='WAV')
                wav_buffer.seek(0)

                # Encode to base64
                audio_base64 = base64.b64encode(wav_buffer.read()).decode('utf-8')

                # Clean up temporary files
                if speaker_audio_path and os.path.exists(speaker_audio_path):
                    os.unlink(speaker_audio_path)

                return {
                    "status": "success",
                    "audio": audio_base64,
                    "sample_rate": sample_rate,
                    "duration": len(audio_array) / sample_rate
                }

            except Exception as e:
                # Clean up on error
                if speaker_audio_path and os.path.exists(speaker_audio_path):
                    os.unlink(speaker_audio_path)
                raise e
        else:
            # Mock response for testing
            return {
                "status": "mock",
                "message": "Model not loaded. This is a mock response.",
                "received_parameters": {
                    "text": text[:100],
                    "top_k": top_k,
                    "top_p": top_p,
                    "num_beams": num_beams,
                    "temperature": temperature,
                    "emotion_scale": emotion_scale,
                    "length_penalty": length_penalty,
                    "max_mel_tokens": max_mel_tokens,
                    "randomize_emotion": randomize_emotion,
                    "repetition_penalty": repetition_penalty,
                    "interval_silence_ms": interval_silence_ms,
                    "max_text_tokens_per_segment": max_text_tokens_per_segment,
                    "has_speaker_audio": speaker_audio is not None
                }
            }

    except Exception as e:
        print(f"Error in handler: {str(e)}")
        traceback.print_exc()
        return {"error": str(e)}

# Load model on cold start
print("Initializing IndexTTS2 handler...")
load_model()
print("Handler ready")

# Start the RunPod serverless handler
runpod.serverless.start({"handler": handler})
