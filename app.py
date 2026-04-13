from flask import Flask, request, send_file
from flask_cors import CORS
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)
CORS(app)

@app.route("/generate", methods=["POST"])
def generate():

    data = request.json

    bust = float(data.get("bust", 36))
    waist = float(data.get("waist", 28))
    length = float(data.get("length", 40))
    neck_type = data.get("neck", "round")  # round or v

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    scale = 15

    # Derived measurements
    chest_w = bust / 4 * scale
    waist_w = waist / 4 * scale
    armhole_depth = bust / 6 * scale
    shoulder = bust / 12 * scale
    sleeve_length = 20 * scale
    seam = 10  # seam allowance

    x = 100
    y = 750

    # ---------------- FRONT ----------------
    c.drawString(x, y + 30, "PART 1 - FRONT")

    # Shoulder
    c.line(x, y, x + shoulder, y - 20)

    # Neck styles
    if neck_type == "v":
        c.line(x, y, x + 20, y - 40)
    else:
        c.arc(x - 20, y - 20, x + 40, y + 40, 0, 90)

    # Armhole
    c.bezier(
        x + shoulder, y - 20,
        x + chest_w + 40, y - armhole_depth,
        x + chest_w, y - armhole_depth - 60,
        x + chest_w - 20, y - armhole_depth - 120
    )

    # Side
    c.line(
        x + chest_w - 20,
        y - armhole_depth - 120,
        x + waist_w,
        y - length * scale
    )

    # Bottom
    c.line(x + waist_w, y - length * scale, x, y - length * scale)

    # Center
    c.line(x, y - length * scale, x, y)

    # Seam allowance
    c.rect(x - seam, y - length * scale - seam,
           waist_w + seam * 2, length * scale + seam * 2)

    # ---------------- BACK ----------------
    x2 = x + 300
    c.drawString(x2, y + 30, "PART 2 - BACK")

    c.line(x2, y, x2 + shoulder, y - 10)

    c.arc(x2 - 10, y - 10, x2 + 30, y + 30, 0, 90)

    c.bezier(
        x2 + shoulder, y - 10,
        x2 + chest_w + 30, y - armhole_depth,
        x2 + chest_w, y - armhole_depth - 40,
        x2 + chest_w - 20, y - armhole_depth - 100
    )

    c.line(
        x2 + chest_w - 20,
        y - armhole_depth - 100,
        x2 + waist_w,
        y - length * scale
    )

    c.line(x2 + waist_w, y - length * scale, x2, y - length * scale)
    c.line(x2, y - length * scale, x2, y)

    # ---------------- SLEEVE ----------------
    x3 = x2 + 300
    c.drawString(x3, y + 30, "PART 3 - SLEEVE")

    # Sleeve cap curve
    c.bezier(
        x3, y,
        x3 + 60, y + 40,
        x3 + 120, y + 40,
        x3 + 180, y
    )

    # Sleeve sides
    c.line(x3, y, x3 + 20, y - sleeve_length)
    c.line(x3 + 180, y, x3 + 160, y - sleeve_length)

    # Bottom
    c.line(x3 + 20, y - sleeve_length, x3 + 160, y - sleeve_length)

    # ---------------- A4 GRID ----------------
    c.drawString(100, 80, "A4 Cutting Grid Guide")

    grid_x = 100
    grid_y = 60
    box = 40

    for i in range(5):
        for j in range(5):
            c.rect(grid_x + i * box, grid_y + j * box, box, box)

    # ---------------- INFO ----------------
    c.drawString(100, 30,
                 f"Bust: {bust} | Waist: {waist} | Length: {length} | Neck: {neck_type}")

    c.save()
    buffer.seek(0)

    return send_file(buffer,
                     as_attachment=True,
                     download_name="pattern.pdf",
                     mimetype="application/pdf")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
