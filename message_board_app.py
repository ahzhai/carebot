from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Storage for messages
messages = []

# Serve the dashboard page
@app.route('/')
def index():
    return render_template('message_board.html')  # Make sure this matches the HTML file name

# API to fetch existing messages (for the dashboard)
@app.route('/get_messages')
def get_messages():
    return jsonify(messages)

# API to add a new message from the caregiver or patient
@app.route('/add_message', methods=['POST'])
def add_message():
    data = request.json
    new_message = {
        "content": data['message'],
        "sender": data.get('sender', 'unknown')  # Expecting sender field (caregiver/patient)
    }
    messages.append(new_message)  # Add to the list of messages
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)
