from openai import OpenAI

import requests

# Set up the OpenAI API key
client = OpenAI()
client.api_key = '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'


import subprocess
import tempfile

# Prompt the user to record a message
print("Press Enter to start recording. Press Ctrl+C to stop.")
input()

# Create a temporary file to store the recording
with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
    audio_file_path = temp_audio.name

# Use sox to capture audio (this works on Unix systems)
try:
    subprocess.run(["rec", "-r", "44100", "-c", "2", audio_file_path], check=True)
except KeyboardInterrupt:
    print("\nRecording stopped.")
except subprocess.CalledProcessError:
    print("Error: Unable to record audio. Make sure you have 'sox' installed.")
    exit(1)

print(f"Audio recorded and saved to {audio_file_path}")

with open(audio_file_path, "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-1"
    )

print(transcription.text)

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "You are an AI trained to analyze text and deduce emotions. Please provide an analysis of the emotional content in the given text."
        },
        {
            "role": "user",
            "content": f"Based on this text:'{transcription.text}' - Can you provide me with a json blob response where 'Content' maps to a brief factual description of the stimulus causing the emotion? This trigger can likely be categorized as one of the following six forms of psychological stress: physical pain, full bladder, temperature, sound, light, and internal personal frustration. 'Emotion' maps to a description of the emotions the person is experiencing as a result of the stimulus."
        }
    ],
)

print(completion.choices[0].message.content)
