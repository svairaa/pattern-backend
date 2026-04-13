from flask import Flask, request, send_file
from flask_cors import CORS
from reportlab.pdfgen import canvas
import io
import math

app = Flask(__name__)
CORS(app)

@app.route("/generate", methods=["POST"])
def generate():

    data = request.json

    bust = float(data.get("bust", 36))
    waist = float(data.get("waist", 28))
    length = float(data.get("length", 40))

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    # Scale factor (1 inch = 72 points)
    scale = 10

    # Base points
    width = bust / 4 * scale
    height = length * scale

    # START DRAWING FRONT
    x = 100
    y = 700

    # Shoulder slope
    c.line(x, y, x + 60, y - 20)

    # Neck curve
    c.arc(x - 20, y - 20, x + 40, y + 40, 0, 90)

    # Armhole curve (important!)
    c.bezier(
        x + 60, y - 20,
        x + 100, y - 60,
        x + 80, y - 140,
        x + 40, y - 180
    )

    # Side seam
    c.line(x + 40, y - 180, x + 40, y - height)

    # Bottom
    c.line(x + 40, y - height, x, y - height)

    # Center front
    c.line(x, y - height, x, y)

    c.drawString(x, y + 20, "PART 1 - FRONT")

    # BACK PART
    x2 = x + 200

    # Shoulder
    c.line(x2, y, x2 + 70, y - 10)

    # Neck
    c.arc(x2 - 10, y - 10, x2 + 40, y + 40, 0, 90)

    # Armhole (slightly deeper)
    c.bezier(
        x2 + 70, y - 10,
        x2 + 110, y - 50,
        x2 + 90, y - 150,
        x2 + 50, y - 200
    )

    # Side
    c.line(x2 + 50, y - 200, x2 + 50, y - height)

    # Bottom
    c.line(x2 + 50, y - height, x2, y - height)

    # Center back
    c.line(x2, y - height, x2, y)

    c.drawString(x2, y + 20, "PART 2 - BACK")

    # INFO
    c.drawString(100, 50, f"Bust: {bust}  Waist: {waist}  Length: {length}")

    c.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="pattern.pdf", mimetype="application/pdf")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
