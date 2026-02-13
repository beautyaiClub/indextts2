#!/usr/bin/env python3
"""
Test script for IndexTTS2 RunPod Serverless endpoint
"""

import runpod
import base64
import sys
import os

def test_endpoint(endpoint_id, api_key):
    """Test the IndexTTS2 endpoint with various inputs"""

    runpod.api_key = api_key
    endpoint = runpod.Endpoint(endpoint_id)

    print("=" * 60)
    print("Testing IndexTTS2 RunPod Serverless Endpoint")
    print("=" * 60)

    # Test 1: Simple text without speaker audio
    print("\n[Test 1] Simple text synthesis (no speaker audio)...")
    try:
        result = endpoint.run_sync(
            {
                "input": {
                    "text": "Hello, this is a test of IndexTTS2."
                }
            },
            timeout=300
        )
        print(f"✓ Status: {result.get('status', 'unknown')}")
        if 'audio' in result:
            print(f"✓ Audio generated: {result.get('duration', 0):.2f}s @ {result.get('sample_rate', 0)}Hz")
            # Save audio
            audio_data = base64.b64decode(result['audio'])
            with open("test_output_1.wav", "wb") as f:
                f.write(audio_data)
            print("✓ Saved to: test_output_1.wav")
        else:
            print(f"Response: {result}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

    # Test 2: With speaker audio URL
    print("\n[Test 2] Voice cloning with speaker audio URL...")
    try:
        result = endpoint.run_sync(
            {
                "input": {
                    "text": "You miss 100% of the shots you don't take. Start today with Index TTS 2.",
                    "speaker_audio": "https://replicate.delivery/pbxt/Nitgz9LwQUvwL4jOcOpJSsKqaJ3jt8puvvWPkrnd46WLjw3H/emmy-woman-emotional.mp3",
                    "top_k": 30,
                    "top_p": 0.8,
                    "temperature": 0.8,
                    "emotion_scale": 1.0
                }
            },
            timeout=300
        )
        print(f"✓ Status: {result.get('status', 'unknown')}")
        if 'audio' in result:
            print(f"✓ Audio generated: {result.get('duration', 0):.2f}s @ {result.get('sample_rate', 0)}Hz")
            audio_data = base64.b64decode(result['audio'])
            with open("test_output_2.wav", "wb") as f:
                f.write(audio_data)
            print("✓ Saved to: test_output_2.wav")
        else:
            print(f"Response: {result}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

    # Test 3: Custom parameters
    print("\n[Test 3] Custom parameters (high emotion, slower)...")
    try:
        result = endpoint.run_sync(
            {
                "input": {
                    "text": "This is an emotional test with custom parameters!",
                    "emotion_scale": 1.5,
                    "temperature": 0.9,
                    "repetition_penalty": 15,
                    "interval_silence_ms": 300
                }
            },
            timeout=300
        )
        print(f"✓ Status: {result.get('status', 'unknown')}")
        if 'audio' in result:
            print(f"✓ Audio generated: {result.get('duration', 0):.2f}s @ {result.get('sample_rate', 0)}Hz")
            audio_data = base64.b64decode(result['audio'])
            with open("test_output_3.wav", "wb") as f:
                f.write(audio_data)
            print("✓ Saved to: test_output_3.wav")
        else:
            print(f"Response: {result}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test_endpoint.py <endpoint_id> <api_key>")
        print("\nExample:")
        print("  python test_endpoint.py abc123xyz YOUR_API_KEY")
        sys.exit(1)

    endpoint_id = sys.argv[1]
    api_key = sys.argv[2]

    test_endpoint(endpoint_id, api_key)
