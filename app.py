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

    scale = 8

    chest = bust * scale / 4 + 10
    waist_w = waist * scale / 4 + 10
    armhole = bust * scale / 6
    shoulder = bust * scale / 12

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    x = 100
    y = 700

    # FRONT
    c.drawString(x, y+20, "FRONT")
    c.line(x, y, x+shoulder, y-20)

    c.bezier(
        x+shoulder, y-20,
        x+chest, y-armhole,
        x+chest, y-armhole-50,
        x+chest-20, y-armhole-120
    )

    c.line(x+chest-20, y-armhole-120, x+waist_w, y-length*scale)
    c.line(x+waist_w, y-length*scale, x, y-length*scale)
    c.line(x, y-length*scale, x, y)

    # BACK
    x2 = x + chest + 100
    c.drawString(x2, y+20, "BACK")

    c.line(x2, y, x2+shoulder, y-10)

    c.bezier(
        x2+shoulder, y-10,
        x2+chest, y-armhole,
        x2+chest, y-armhole-40,
        x2+chest-20, y-armhole-100
    )

    c.line(x2+chest-20, y-armhole-100, x2+waist_w, y-length*scale)
    c.line(x2+waist_w, y-length*scale, x2, y-length*scale)
    c.line(x2, y-length*scale, x2, y)

    # SLEEVE
    x3 = x2 + chest + 100
    c.drawString(x3, y+20, "SLEEVE")

    c.bezier(
        x3, y,
        x3+60, y+60,
        x3+120, y+60,
        x3+180, y
    )

    c.line(x3, y, x3+20, y-150)
    c.line(x3+180, y, x3+160, y-150)
    c.line(x3+20, y-150, x3+160, y-150)

    c.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="pattern.pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
