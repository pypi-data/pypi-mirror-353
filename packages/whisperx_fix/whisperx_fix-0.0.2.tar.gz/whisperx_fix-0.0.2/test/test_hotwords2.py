#!/usr/bin/env python3
"""
Test script for transcribe_with_hotwords function
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from whisperx_fix.asr import load_model
import soundfile as sf
from dotenv import load_dotenv

load_dotenv()

MODEL_DIR = os.getenv('MODEL_DIR')
TEST_AUDIO = os.getenv('TEST_AUDIO')

def test_transcribe_with_hotwords():
    hotwords = "Cline Cline Windsurf"
    # hotwords = ""
    asr_options={
        "hotwords": hotwords
    }
    
    # load model
    model = load_model(
        download_root=MODEL_DIR,
        whisper_arch="large-v3",
        device="cuda",
        compute_type="float32",
        language="en",
        asr_options=asr_options
    )
    
    # load audio
    audio, sample_rate = sf.read(TEST_AUDIO, dtype="float32")
    
    print("Test original transcribe method:")
    try:
        result1 = model.transcribe(audio)
        print(f"Origin result: {result1}")
    except Exception as e:
        print(f"Origin transcribe error: {e}")
    
    print("\nTest transcribe function with hotwords:")
    try:
        # hotwords function
        hotwords = "Claude Claude"
        result2 = model.transcribe(
            audio, 
            hotwords=hotwords
        )
        print(f"Hotwords result: {result2}")
        print(f"Hotwords: {hotwords}")
    except Exception as e:
        print(f"Transcribe with hotwords error: {e}")

if __name__ == "__main__":
    test_transcribe_with_hotwords() 