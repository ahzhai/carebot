from flask import Flask, jsonify, render_template
# from flask_cors import CORS
import services.test_math as test_math

app = Flask(__name__)
#CORS(app, resources={r"/calculate": {"origins": "http://localhost:5000"}})

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/calculate')
def calculate():
    result = test_math.add_numbers()
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(debug=True)

