from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
import os

app = Flask(__name__)
CORS(app)
os.makedirs("uploads", exist_ok=True)

def detect(path):
    img = Image.open(path)
    w,h = img.size
    r = h/w

    if r>1.5: t="gown"
    elif r>1.2: t="dress"
    else: t="top"

    sleeve = "sleeveless" if w>h else "short sleeve"
    neck = "round"

    if t=="gown":
        m=["bust","waist","hip","length"]
    elif t=="dress":
        m=["bust","waist","length"]
    else:
        m=["bust","shoulder"]

    return {"type":t,"sleeve":sleeve,"neck":neck,"measurements":m}

@app.route("/upload", methods=["POST"])
def upload():
    f = request.files["file"]
    path = "uploads/"+f.filename
    f.save(path)
    return jsonify(detect(path))

@app.route("/generate", methods=["POST"])
def generate():
    d = request.json

    def cm(x): return float(x)*28.35

    bust = cm(d.get("bust",90))
    length = cm(d.get("length",100))

    c = canvas.Canvas("pattern.pdf", pagesize=A4)
    W,H = A4

    x=50
    y=H-50

    # FRONT
    c.drawString(x,y+10,"FRONT")
    c.rect(x,y-length,bust/4,length)

    # BACK
    c.drawString(x+150,y+10,"BACK")
    c.rect(x+150,y-length,bust/4,length)

    # SLEEVE
    if d["sleeve"]!="sleeveless":
        c.drawString(x,y-length-100,"SLEEVE")
        c.circle(x+50,y-length-150,40)

    c.save()

    return send_file("pattern.pdf", as_attachment=True)

if __name__ == "__main__":
    app.run()
