import subprocess
import tempfile
from openai import OpenAI
import os

client = OpenAI()
client.api_key = os.environ.get("OPENAI_API_KEY")

temp_audio_file = None
recording_process = None

def start_recording():
    global temp_audio_file, recording_process
    temp_audio_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    audio_file_path = temp_audio_file.name
    
    # Start recording using sox
    recording_process = subprocess.Popen(["rec", "-r", "44100", "-c", "2", audio_file_path])
    
    return "Recording started"

def stop_recording_and_process():
    global temp_audio_file, recording_process
    
    try:
        if recording_process:
            recording_process.terminate()
            recording_process.wait()
        
        if temp_audio_file:
            audio_file_path = temp_audio_file.name
            temp_audio_file.close()
            
            # Process the audio file using gpt
            with open(audio_file_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1"
                )
            return transcription.text
        
        return "No recording to process"
    except Exception as e:
        print(f"Error in stop_recording_and_process: {str(e)}")
        return f"Error processing recording: {str(e)}"
