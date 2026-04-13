from flask import Flask, request, jsonify, send_file
from reportlab.platypus import SimpleDocTemplate, PageBreak
from reportlab.graphics.shapes import Drawing, Line, String
import math
import uuid
import os

app = Flask(__name__)

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# -------------------------
# IMAGE ANALYSIS (RULE BASED)
# -------------------------
def analyze_image(filename):
    name = filename.lower()

    garment = "top"
    if "dress" in name or "gown" in name:
        garment = "dress"
    elif "kurti" in name:
        garment = "kurti"

    sleeve = "short"
    if "sleeveless" in name:
        sleeve = "sleeveless"
    elif "long" in name:
        sleeve = "long"

    neckline = "round"
    if "v" in name:
        neckline = "v"
    elif "boat" in name:
        neckline = "boat"
    elif "square" in name:
        neckline = "square"

    fit = "semi-fit"
    if "loose" in name:
        fit = "loose"
    elif "tight" in name:
        fit = "fitted"

    return {
        "garment": garment,
        "sleeve": sleeve,
        "neckline": neckline,
        "fit": fit
    }


# -------------------------
# SIZE SYSTEM
# -------------------------
STANDARD_SIZES = {
    "S": {"bust": 34, "waist": 28, "hip": 36},
    "M": {"bust": 38, "waist": 32, "hip": 40},
    "L": {"bust": 42, "waist": 36, "hip": 44},
    "XL": {"bust": 46, "waist": 40, "hip": 48},
    "XXL": {"bust": 50, "waist": 44, "hip": 52},
}


# -------------------------
# PATTERN ENGINE
# -------------------------
def generate_pattern(measurements, style):
    bust = measurements["bust"]
    waist = measurements.get("waist", bust)
    hip = measurements.get("hip", bust)
    length = measurements.get("length", 40)
    shoulder = measurements.get("shoulder", 14)
    sleeve_len = measurements.get("sleeve", 10)

    ease = 2 if style["fit"] == "fitted" else 4

    bust_q = (bust + ease) / 4
    waist_q = (waist + ease) / 4
    armhole = bust / 6

    pattern = {
        "front": [],
        "back": [],
        "sleeve": []
    }

    # FRONT BLOCK
    pattern["front"] = [
        (0, 0),
        (bust_q, 0),
        (bust_q, length),
        (0, length),
        (0, armhole),
        (bust_q, armhole)
    ]

    # BACK BLOCK
    pattern["back"] = [
        (0, 0),
        (bust_q, 0),
        (bust_q, length),
        (0, length)
    ]

    # SLEEVE
    if style["sleeve"] != "sleeveless":
        sleeve_width = armhole * 2
        pattern["sleeve"] = [
            (0, 0),
            (sleeve_width, 0),
            (sleeve_width, sleeve_len),
            (0, sleeve_len)
        ]

    return pattern


# -------------------------
# PDF GENERATOR (A4 GRID)
# -------------------------
def create_pdf(pattern):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(OUTPUT_DIR, f"{file_id}.pdf")

    doc = SimpleDocTemplate(file_path)

    elements = []

    def draw_piece(points, title):
        d = Drawing(500, 700)

        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]
            d.add(Line(x1 * 10, y1 * 10, x2 * 10, y2 * 10))

        d.add(String(10, 650, title))
        return d

    elements.append(draw_piece(pattern["front"], "FRONT"))
    elements.append(PageBreak())

    elements.append(draw_piece(pattern["back"], "BACK"))
    elements.append(PageBreak())

    if pattern["sleeve"]:
        elements.append(draw_piece(pattern["sleeve"], "SLEEVE"))

    doc.build(elements)

    return file_path


# -------------------------
# ROUTES
# -------------------------
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    filename = file.filename

    style = analyze_image(filename)

    return jsonify(style)


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json

    size_mode = data["mode"]

    if size_mode == "standard":
        measurements = STANDARD_SIZES[data["size"]]
    else:
        measurements = data["measurements"]

    style = data["style"]

    pattern = generate_pattern(measurements, style)

    pdf_path = create_pdf(pattern)

    return jsonify({"file": pdf_path})


@app.route("/download")
def download():
    path = request.args.get("file")
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
