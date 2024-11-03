# -*- coding: utf-8 -*-
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()
sarvam_api = os.getenv("SARVAM_API_KEY")

url = "https://api.sarvam.ai/text-to-speech"

payload = {
    "target_language_code": "hi-IN",
    # "speaker": "amartya",
    "speaker": "meera",
    "pitch": 0.1,
    "pace": 1,
    "loudness": 1,
    
    "enable_preprocessing": True,
    "model": "bulbul:v1",
    "inputs": ["बजाज फिनसर्व हेल्थ विभिन्न स्वास्थ्य बीमा योजनाएँ प्रदान करता है, जिनमें हॉस्पिटलाइजेशन, प्री और पोस्ट-हॉस्पिटल केयर शामिल हैं। यह डिजिटल हेल्थ कार्ड, कैशलेस ट्रीटमेंट, EMI विकल्प और क्रिटिकल इलनेस कवर जैसी सुविधाएँ भी देता है। इसके तहत पॉलिसीधारकों को सालाना हेल्थ चेकअप और 24/7 डॉक्टर कंसल्टेशन की सुविधा मिलती है।"]
}

headers = {
    "api-subscription-key": sarvam_api,  # Replace with your actual subscription key
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    audio_data = response.json().get('audios')
    print("Audio generated successfully:")
    
    # Assuming the first audio data is what you need
    audio_base64 = audio_data[0]
    
    # Decode the base64 audio data
    audio_bytes = base64.b64decode(audio_base64)
    
    # Save the audio to a file
    with open("sarvam_test_audio.wav", "wb") as audio_file:
        audio_file.write(audio_bytes)
    
    print("Audio saved as 'output_audio.wav'")
else:
    print(f"Error: {response.status_code} - {response.text}")
