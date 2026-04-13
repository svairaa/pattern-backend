from flask_cors import CORS
from flask import Flask, request, send_file, jsonify
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from PIL import Image
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Advanced Pattern Engine Running ✅"


# -------- FAKE AI DETECTION (IMAGE BASED RULES) --------
def detect_from_image(image_path):
    try:
        img = Image.open(image_path)
        width, height = img.size

        ratio = height / width

        # Simple logic (placeholder AI)
        if ratio > 1.5:
            dress_type = "long"
        else:
            dress_type = "top"

        # Dummy neckline + sleeve
        neckline = "round"
        sleeve = "short"

        return dress_type, neckline, sleeve

    except:
        return "top", "round", "sleeveless"


@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.form

        bust = float(data.get("bust", 90))
        waist = float(data.get("waist", 70))
        length = float(data.get("length", 100))

        image = request.files.get("image")

        image_path = "temp.jpg"
        if image:
            image.save(image_path)
            dress_type, neckline, sleeve_type = detect_from_image(image_path)
        else:
            dress_type, neckline, sleeve_type = "top", "round", "sleeveless"

        # ---------- CONVERT ----------
        bust *= cm
        waist *= cm
        length *= cm

        scale = 0.7
        fw = (bust / 4 + 2*cm) * scale
        ww = (waist / 4 + 2*cm) * scale
        length *= scale

        file_path = "pattern.pdf"
        c = canvas.Canvas(file_path, pagesize=A4)

        x = 60
        y = 750

        # ================= FRONT =================
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x, 800, "PART 1 - FRONT")

        p = c.beginPath()
        p.moveTo(x, y)

        # neckline logic
        if neckline == "v":
            p.lineTo(x+40, y-60)
        else:
            p.curveTo(x+20, y, x+40, y-20, x+60, y-50)

        p.lineTo(x + fw, y - 50)

        # armhole
        p.curveTo(
            x + fw, y - 90,
            x + fw - 30, y - 140,
            x + fw - 60, y - 180
        )

        p.lineTo(x + ww, y - length)
        p.lineTo(x, y - length)
        p.lineTo(x, y)

        c.drawPath(p)

        # ================= BACK =================
        x2 = 300
        c.drawString(x2, 800, "PART 2 - BACK")

        p2 = c.beginPath()
        p2.moveTo(x2, y)

        p2.curveTo(x2+20, y, x2+30, y-10, x2+50, y-25)
        p2.lineTo(x2 + fw, y - 40)

        p2.curveTo(
            x2 + fw, y - 80,
            x2 + fw - 25, y - 130,
            x2 + fw - 50, y - 170
        )

        p2.lineTo(x2 + ww, y - length)
        p2.lineTo(x2, y - length)
        p2.lineTo(x2, y)

        c.drawPath(p2)

        # ================= SLEEVE =================
        if sleeve_type != "sleeveless":
            sx = x
            sy = 250

            c.drawString(sx, sy + 80, f"SLEEVE ({sleeve_type})")

            sp = c.beginPath()

            sp.moveTo(sx, sy)
            sp.curveTo(sx+40, sy+80, sx+120, sy+80, sx+160, sy)

            sp.lineTo(sx+140, sy - 100)
            sp.lineTo(sx+20, sy - 100)
            sp.lineTo(sx, sy)

            c.drawPath(sp)

        # ---------- LABEL ----------
        c.setFont("Helvetica", 9)
        c.drawString(50, 50, f"Type: {dress_type} | Neck: {neckline} | Sleeve: {sleeve_type}")

        c.save()

        if os.path.exists(image_path):
            os.remove(image_path)

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
