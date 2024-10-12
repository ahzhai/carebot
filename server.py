from flask import Flask, jsonify, render_template, request, send_from_directory
# from flask_cors import CORS
import services.test_math as test_math
import services.voice as voice
import services.CareBot as CareBot  
import os
import requests

app = Flask(__name__, static_url_path='/static')
#CORS(app, resources={r"/calculate": {"origins": "http://localhost:5000"}})

TRANSCRIPTION_ENDPOINT = 'https://api.openai.com/v1/audio/transcriptions'
CHAT_ENDPOINT = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AUDIO_FILE_PATH = "Schizo.m4a"
AWS_KEY = ""
AWS_SECRET_KEY = ""

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/calculate')
def calculate():
    result = test_math.add_numbers()
    return jsonify({"result": result})

@app.route('/start_recording')
def start_recording():
    result = voice.start_recording()
    return jsonify({"message": "Recording started", "result": result})

@app.route('/stop_recording')
def stop_recording():
    try:
        audio_response = voice.stop_recording_and_transcribe()
        return jsonify({"message": "Recording stopped and transcribed.", "result": audio_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/process_recording', methods=['POST'])
def process_recording():
    try:
        audio_response = request.json.get('transcription')
        if not audio_response:
            return jsonify({"error": "No audio response provided"}), 400

        # After result has been processed (a transcribed message), we want to call the CareBot.py file
        prompt = (f"Based on this text:'{audio_response}' - Can you provide me with a json blob response "
              "where 'Content' maps to a brief factual description of the stimulus causing the emotion? "
              "This trigger can likely be categorized as one of the following six forms of psychological "
              "stress: physical pain, full bladder, temperature, sound, light, and internal personal frustration. "
              "'Emotion' maps to a description of the emotions the person is experiencing as a result of the stimulus.")
        
        content = CareBot.chat_with_gpt(prompt)
        if not content:
            return jsonify({"message": "" + content})
                
        # Step 3: Extract JSON response
        json_data = CareBot.extract_json(content)
        problem_description = json_data['Content']
        emotion_description = json_data['Emotion']

        # Step 4: Create a message for the caregiver
        caregiver_prompt = (f"Here is a description of a dementia patient's problem: {problem_description}. "
                            f"The emotion they're experiencing is {emotion_description}. Can you craft a text message "
                            "to send to the caregiver with an update and put it in a json blob with the key 'Text Response'?")
        message = CareBot.chat_with_gpt(caregiver_prompt)
        if message:
            message_dict = CareBot.extract_json(message)
            print(f"Caregiver Message: {message_dict['Text Response']}")
            #CareBot.send_sms_via_sns(message_dict['Text Response'])

        # Step 5: Create a message for the patient
        patient_prompt = (f"Here is a description of a dementia patient's problem: {problem_description}. "
                        f"The emotion they're experiencing is {emotion_description}. Can you craft a message "
                        "that will be transcribed to audio to say to the patient? Our main goal is to validate their "
                        "feelings and then deescalate any negative emotions/reinforce any positive emotions. Make sure "
                        "to not make it infantilizing - try to be specific. Put your response in a json blob with key 'Voice Response'.")
        message = CareBot.chat_with_gpt(patient_prompt)
        if message:
            voice_dict = CareBot.extract_json(message)
            voice_message = voice_dict['Voice Response']
            print(f"Voice Message: {voice_message}")
            CareBot.generate_voice_message(voice_message, "static/temp.mp3")

        return jsonify({"message": "Recording processed. Generated voice message.", "result": voice_message})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)
