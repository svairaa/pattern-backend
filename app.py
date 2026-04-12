from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from pattern_engine import build_pattern
from dxf_engine import export_dxf

app = Flask(name)
CORS(app)

@app.route("/")
def home():
return "Backend running!"

@app.route("/generate", methods=["POST"])
def generate():

data = request.json

size = data.get("size")
custom = data.get("custom", False)

if custom:
    bust = float(data["bust"])
    waist = float(data["waist"])
    length = float(data["length"])
else:
    from grading import SIZE_CHART
    s = SIZE_CHART[size]
    bust, waist, length = s["bust"], s["waist"], s["length"]

pattern = build_pattern(bust, waist, length)
file_path = export_dxf(pattern)

return send_file(file_path, as_attachment=True)

@app.route("/health")
def health():
return jsonify({"status": "ok"})
