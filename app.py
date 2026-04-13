from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
import os, math

app = Flask(__name__)
CORS(app)
os.makedirs("uploads", exist_ok=True)

# ---------- AI DETECTION ----------
def detect(path):
    img = Image.open(path)
    w,h = img.size
    r = h/w

    if r>1.6: t="gown"
    elif r>1.2: t="dress"
    else: t="top"

    sleeve = "sleeveless" if w>h else "short sleeve"
    neck = "round" if r>1.3 else "v-neck"

    if t=="gown": m=["bust","waist","hip","length"]
    elif t=="dress": m=["bust","waist","length"]
    else: m=["bust","shoulder"]

    return {"type":t,"sleeve":sleeve,"neck":neck,"measurements":m}

@app.route("/upload",methods=["POST"])
def upload():
    f=request.files["file"]
    path="uploads/"+f.filename
    f.save(path)
    return jsonify(detect(path))

# ---------- PATTERN ENGINE ----------
@app.route("/generate",methods=["POST"])
def gen():
    d=request.json

    def cm(x): return float(x)*28.35

    bust=cm(d.get("bust",90))
    waist=cm(d.get("waist",70))
    length=cm(d.get("length",100))

    c=canvas.Canvas("pattern.pdf",pagesize=A4)
    W,H=A4

    x=40
    y=H-40

    bw=bust/4

    # FRONT SHAPED
    c.drawString(x,y+10,"PART 1 FRONT")
    c.line(x,y,x,y-length)
    c.line(x,y-length,x+bw,y-length)
    c.line(x+bw,y-length,x+bw,y)

    # curve simulation (armhole)
    for i in range(0,50):
        c.line(x+bw, y-i, x+bw-20, y-i-20)

    # BACK
    c.drawString(x+200,y+10,"PART 2 BACK")
    c.rect(x+200,y-length,bw,length)

    # SLEEVE
    if d["sleeve"]!="sleeveless":
        c.drawString(x,y-length-100,"PART 3 SLEEVE")
        c.circle(x+50,y-length-150,40)

    # NECK
    c.drawString(x,y-20,"Neck:"+d["neck"])

    # GRID (A4 cutting guide)
    for i in range(0,int(W),50):
        c.line(i,0,i,H)
    for j in range(0,int(H),50):
        c.line(0,j,W,j)

    c.save()
    return send_file("pattern.pdf",as_attachment=True)

if __name__=="__main__":
    app.run()
