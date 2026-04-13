from flask import Flask, request, send_file
from flask_cors import CORS
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)
CORS(app)

@app.route("/generate", methods=["POST"])
def generate():

    data = request.json

    # -------- INPUT --------
    bust = float(data.get("bust", 90))
    waist = float(data.get("waist", 70))
    length = float(data.get("length", 100))

    # -------- SCALE (important for real size) --------
    scale = 2.8
    bust *= scale
    waist *= scale
    length *= scale

    # -------- REAL TAILORING LOGIC --------
    chest = bust / 4 + 8
    waist_w = waist / 4 + 8
    armhole = bust / 6
    shoulder = bust / 12
    neck_width = bust / 12
    neck_depth = bust / 12 + 5

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    x = 80
    y = 750

    # ================= FRONT =================
    c.drawString(x, y + 20, "FRONT")

    # neckline
    c.arc(x, y - neck_depth, x + neck_width, y, 0, 90)

    # shoulder
    c.line(x + neck_width, y, x + shoulder, y - 20)

    # armhole curve
    c.bezier(
        x + shoulder, y - 20,
        x + chest, y - armhole,
        x + chest, y - armhole - 50,
        x + chest - 15, y - armhole - 120
    )

    # waist shaping
    c.line(
        x + chest - 15,
        y - armhole - 120,
        x + waist_w,
        y - length
    )

    # bottom
    c.line(x + waist_w, y - length, x, y - length)

    # center
    c.line(x, y - length, x, y)

    # ================= BACK =================
    x2 = x + chest + 150

    c.drawString(x2, y + 20, "BACK")

    c.arc(x2, y - neck_width, x2 + neck_width, y, 0, 90)

    c.line(x2 + neck_width, y, x2 + shoulder, y - 10)

    c.bezier(
        x2 + shoulder, y - 10,
        x2 + chest, y - armhole,
        x2 + chest, y - armhole - 40,
        x2 + chest - 15, y - armhole - 100
    )

    c.line(
        x2 + chest - 15,
        y - armhole - 100,
        x2 + waist_w,
        y - length
    )

    c.line(x2 + waist_w, y - length, x2, y - length)
    c.line(x2, y - length, x2, y)

    # ================= SLEEVE =================
    x3 = x2 + chest + 150

    c.drawString(x3, y + 20, "SLEEVE")

    sleeve_w = chest
    sleeve_h = armhole

    c.bezier(
        x3, y,
        x3 + sleeve_w / 3, y + sleeve_h,
        x3 + 2 * sleeve_w / 3, y + sleeve_h,
        x3 + sleeve_w, y
    )

    c.line(x3, y, x3 + 20, y - 180)
    c.line(x3 + sleeve_w, y, x3 + sleeve_w - 20, y - 180)

    c.line(x3 + 20, y - 180, x3 + sleeve_w - 20, y - 180)

    # ================= NOTE =================
    c.drawString(80, 60, "Add seam allowance before cutting")

    c.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="pattern.pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
    
