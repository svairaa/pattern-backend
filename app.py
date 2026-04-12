from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Backend is running 🚀"

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    # For now just confirm received
    return jsonify({"message": "File received successfully"})

if __name__ == '__main__':
    app.run()
