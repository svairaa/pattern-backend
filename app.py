from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

app = Flask(__name__)
CORS(app)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file"}), 400

    file.save(file.filename)
    return jsonify({"msg": "uploaded"})

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json

    def cm(x): return float(x) * 28.35

    bust = cm(data["bust"])
    length = cm(data["length"])

    c = canvas.Canvas("pattern.pdf", pagesize=A4)
    width, height = A4

    x = 50
    y = height - 50

    # rectangle pattern
    c.rect(x, y-length, bust/4, length)

    # waist line
    c.line(x, y-length/2, x + bust/4, y-length/2)

    c.drawString(50, 800, "Pattern Generated")

    c.save()

    return send_file("pattern.pdf", as_attachment=True)

if __name__ == "__main__":
    app.run()
