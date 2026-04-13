from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
import os

app = Flask(__name__)
CORS(app)
os.makedirs("uploads", exist_ok=True)

# ---------- AI DETECTION ----------
def detect(path):
    img = Image.open(path)
    w, h = img.size
    ratio = h / w

    if ratio > 1.5:
        dress_type = "gown"
    elif ratio > 1.2:
        dress_type = "dress"
    else:
        dress_type = "top"

    sleeve = "sleeveless" if w > h else "short sleeve"
    neck = "round"

    if dress_type == "gown":
        measurements = ["bust", "waist", "hip", "length"]
    elif dress_type == "dress":
        measurements = ["bust", "waist", "length"]
    else:
        measurements = ["bust", "shoulder"]

    return {
        "type": dress_type,
        "sleeve": sleeve,
        "neck": neck,
        "measurements": measurements
    }

@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files["file"]
        path = os.path.join("uploads", file.filename)
        file.save(path)
        result = detect(path)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- PATTERN GENERATION ----------
@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.json

        def cm(val):
            if val is None or val == "" or val == "0":
                return 100 * 28.35   # default safe value
            return float(val) * 28.35

        bust = cm(data.get("bust"))
        waist = cm(data.get("waist"))
        length = cm(data.get("length"))

        file_path = "pattern.pdf"

        c = canvas.Canvas(file_path, pagesize=A4)
        W, H = A4

        x = 50
        y = H - 50

        # FRONT
        c.drawString(x, y + 10, "PART 1 - FRONT")
        c.rect(x, y - length, bust / 4, length)

        # BACK
        c.drawString(x + 200, y + 10, "PART 2 - BACK")
        c.rect(x + 200, y - length, bust / 4, length)

        # SLEEVE
        if data.get("sleeve") != "sleeveless":
            c.drawString(x, y - length - 80, "PART 3 - SLEEVE")
            c.circle(x + 60, y - length - 140, 40)

        # GRID (for cutting)
        for i in range(0, int(W), 50):
            c.line(i, 0, i, H)
        for j in range(0, int(H), 50):
            c.line(0, j, W, j)

        c.save()

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run()
