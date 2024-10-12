from flask import Flask, jsonify, render_template
# from flask_cors import CORS
import services.test_math as test_math
import services.voice as voice

app = Flask(__name__)
#CORS(app, resources={r"/calculate": {"origins": "http://localhost:5000"}})

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
        result = voice.stop_recording_and_process()
        return jsonify({"message": "Recording stopped and processed", "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
