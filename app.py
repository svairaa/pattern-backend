from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import pathobject
from PIL import Image
import os

app = Flask(__name__)
CORS(app)
os.makedirs("uploads", exist_ok=True)

# ---------- AI DETECTION ----------
def detect(path):
    img = Image.open(path)
    w, h = img.size
    r = h / w

    if r > 1.5:
        t = "gown"
    elif r > 1.2:
        t = "dress"
    else:
        t = "top"

    sleeve = "sleeveless" if w > h else "short sleeve"
    neck = "round"

    if t == "gown":
        m = ["bust", "waist", "hip", "length"]
    elif t == "dress":
        m = ["bust", "waist", "length"]
    else:
        m = ["bust", "shoulder"]

    return {"type": t, "sleeve": sleeve, "neck": neck, "measurements": m}


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    path = os.path.join("uploads", file.filename)
    file.save(path)
    return jsonify(detect(path))


# ---------- PATTERN ENGINE ----------
@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.json

        def cm(val, default):
            if val is None or val == "" or val == "0":
                return default * 28.35
            return float(val) * 28.35

        bust = cm(data.get("bust"), 90)
        waist = cm(data.get("waist"), 70)
        hip = cm(data.get("hip"), 95)
        length = cm(data.get("length"), 100)

        c = canvas.Canvas("pattern.pdf", pagesize=A4)
        W, H = A4

        x = 50
        y = H - 50

        bw = bust / 4

        # ---------------- FRONT WITH CURVES ----------------
        c.drawString(x, y + 10, "PART 1 - FRONT")

        p = c.beginPath()

        # start top-left
        p.moveTo(x, y)

        # neckline (curve)
        p.curveTo(x + 20, y, x + 40, y - 10, x + 60, y - 30)

        # shoulder to armhole
        p.lineTo(x + bw, y - 40)

        # armhole curve
        p.curveTo(x + bw, y - 80, x + bw - 30, y - 120, x + bw - 40, y - 150)

        # side seam
        p.lineTo(x + bw - 20, y - length)

        # bottom
        p.lineTo(x, y - length)

        # close shape
        p.lineTo(x, y)

        c.drawPath(p)

        # ---------------- BACK ----------------
        c.drawString(x + 200, y + 10, "PART 2 - BACK")

        p2 = c.beginPath()
        p2.moveTo(x + 200, y)

        # back neck (shallower)
        p2.curveTo(x + 220, y, x + 240, y - 5, x + 260, y - 15)

        p2.lineTo(x + 200 + bw, y - 40)

        p2.curveTo(x + 200 + bw, y - 80, x + 200 + bw - 30, y - 120, x + 200 + bw - 40, y - 150)

        p2.lineTo(x + 200 + bw - 20, y - length)
        p2.lineTo(x + 200, y - length)
        p2.lineTo(x + 200, y)

        c.drawPath(p2)

        # ---------------- SLEEVE (REAL SHAPE) ----------------
        if data.get("sleeve") != "sleeveless":
            c.drawString(x, y - length - 80, "PART 3 - SLEEVE")

            sx = x
            sy = y - length - 120

            sleeve_w = bw
            sleeve_h = 80

            sp = c.beginPath()

            # sleeve cap curve
            sp.moveTo(sx, sy)

            sp.curveTo(
                sx + sleeve_w * 0.25, sy + sleeve_h,
                sx + sleeve_w * 0.75, sy + sleeve_h,
                sx + sleeve_w, sy
            )

            # bottom
            sp.lineTo(sx + sleeve_w, sy - 60)
            sp.lineTo(sx, sy - 60)
            sp.lineTo(sx, sy)

            c.drawPath(sp)

        # ---------------- LABEL ----------------
        c.drawString(x, 40, f"Type: {data.get('type')} | Sleeve: {data.get('sleeve')}")

        c.save()

        return send_file("pattern.pdf", as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run()
