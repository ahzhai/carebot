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

@app.route('/static/<filename>')
def serve_static_file(filename):
    response = send_from_directory('static', filename)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

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
        
        server_directory = os.path.dirname(os.path.abspath(__file__))
        output_file_path = os.path.join(server_directory, 'static', 'output.mp3')

        CareBot.run_carebot(audio_response, output_file_path)
        
        return jsonify({"message": "Recording processed. Generated voice message.", "result": output_file_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete_output', methods=['POST'])
def delete_output():
    try:
        server_directory = os.path.dirname(os.path.abspath(__file__))
        output_file_path = os.path.join(server_directory, 'static', 'output.mp3')

        if os.path.exists(output_file_path):
            os.remove(output_file_path)
            return jsonify({"message": "Old output file deleted."}), 200
        else:
            return jsonify({"error": "Output file not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)
