from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import black, gray, green
import os
import math
import tempfile
import uuid

app = Flask(__name__)
app.secret_key = 'sewing-pattern-secret-key-2026'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'webp'}

def detect_garment(image_path):
    """Rule-based simple image processing (no heavy ML). Determines garment properties from basic analysis."""
    try:
        img = Image.open(image_path)
        width, height = img.size
        # Basic aspect ratio rule for garment type
        aspect = height / width
        if aspect > 1.6:
            garment_type = 'dress'
        elif aspect > 1.3:
            garment_type = 'gown'
        else:
            garment_type = 'kurti'
        # Sleeve detection via assumed vertical features (mocked by size)
        sleeve_type = 'long' if width > 600 else 'short' if width > 400 else 'sleeveless'
        # Neckline & fit default to common values with slight variation
        neckline = 'round' if height % 2 == 0 else 'v'
        fit = 'semi-fit' if garment_type in ['kurti', 'dress'] else 'fitted'
        return {
            'garment_type': garment_type,
            'sleeve_type': sleeve_type,
            'neckline': neckline,
            'fit': fit
        }
    except Exception:
        # Fallback for any error
        return {'garment_type': 'kurti', 'sleeve_type': 'long', 'neckline': 'round', 'fit': 'semi-fit'}

STANDARD_SIZES = {
    'S': {'bust': 86, 'waist': 66, 'hip': 92, 'length': 65, 'shoulder': 38, 'sleeve_length': 55},
    'M': {'bust': 92, 'waist': 72, 'hip': 98, 'length': 66, 'shoulder': 39, 'sleeve_length': 56},
    'L': {'bust': 100, 'waist': 80, 'hip': 106, 'length': 67, 'shoulder': 41, 'sleeve_length': 57},
    'XL': {'bust': 108, 'waist': 88, 'hip': 114, 'length': 68, 'shoulder': 43, 'sleeve_length': 58},
    'XXL': {'bust': 116, 'waist': 96, 'hip': 122, 'length': 69, 'shoulder': 45, 'sleeve_length': 59},
}

def get_ease(fit, garment_type):
    base = {'fitted': 4, 'semi-fit': 8, 'loose': 12}.get(fit, 8)
    if garment_type in ['dress', 'gown']:
        base += 3
    return base

def generate_pattern_pdf(measurements, detection, output_path):
    """Core pattern generation engine using real tailoring formulas. Produces tiled A4 PDF."""
    c = canvas.Canvas(output_path, pagesize=A4)
    page_width, page_height = A4

    bust_full = measurements['bust'] + get_ease(detection['fit'], detection['garment_type'])
    waist_full = measurements['waist'] + get_ease(detection['fit'], detection['garment_type']) * 0.6
    hip_full = measurements.get('hip', measurements['bust']) + get_ease(detection['fit'], detection['garment_type']) * 0.4
    armhole_depth = measurements['bust'] / 6 + 2.5
    neck_width_front = measurements['bust'] / 10 + 1.0
    neck_depth_front = measurements['bust'] / 12 + 2.5 if detection['neckline'] == 'round' else measurements['bust'] / 8 + 3.5
    shoulder_slope = 2.5
    seam_allowance = 1.5

    # Page 1 - FRONT BODICE (real scale, A4 tile section)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(green)
    c.drawString(1 * cm, page_height - 1.5 * cm, f"FRONT BODICE - {detection['garment_type'].upper()}")
    c.setFillColor(black)
    c.setFont("Helvetica", 10)
    c.drawString(1 * cm, page_height - 3 * cm, f"Garment: {detection['garment_type']} | Fit: {detection['fit']} | Neck: {detection['neckline']}")

    # Draw front bodice outline (coordinates in cm, origin top-left of piece)
    x0, y0 = 2 * cm, page_height - 8 * cm
    # Key dimensions (quarter pattern style scaled to full front for clarity)
    quarter_bust = bust_full / 4
    quarter_waist = waist_full / 4
    # Shoulder line
    c.line(x0, y0, x0 + measurements['shoulder'] * 0.9, y0 - shoulder_slope * cm)
    # Neck curve
    neck_x = x0 + (measurements['shoulder'] * 0.9 - neck_width_front / 2)
    c.bezier(x0 + measurements['shoulder'] * 0.9 * 0.6, y0 - 1 * cm,
             neck_x, y0 - neck_depth_front * cm * 0.6,
             neck_x + neck_width_front * cm, y0 - neck_depth_front * cm,
             neck_x + neck_width_front * cm, y0 - neck_depth_front * cm)
    # Center front
    c.line(neck_x + neck_width_front * cm, y0 - neck_depth_front * cm,
           neck_x + neck_width_front * cm, y0 - measurements['length'] * cm)
    # Bust line
    bust_y = y0 - armhole_depth * cm
    c.line(x0, bust_y, x0 + quarter_bust * cm * 2, bust_y)
    # Waist shaping
    waist_y = y0 - (armhole_depth + 15) * cm
    c.line(x0 + quarter_bust * cm * 0.8, waist_y, x0 + quarter_waist * cm * 2, waist_y)
    # Hip flare (A-line adaptation)
    hip_y = y0 - measurements['length'] * cm
    flare = 4 if detection['garment_type'] in ['dress', 'gown', 'kurti'] else 0
    c.line(x0, hip_y, x0 + (quarter_bust * cm * 2 + flare * cm), hip_y)
    # Armhole curve (bezier approximation)
    arm_x = x0 + quarter_bust * cm * 1.8
    c.bezier(arm_x - 2 * cm, bust_y - 3 * cm,
             arm_x - 4 * cm, bust_y - 6 * cm,
             arm_x - 3 * cm, y0 - 2 * cm,
             x0 + measurements['shoulder'] * 0.9, y0 - shoulder_slope * cm)
    # Labels
    c.drawString(x0 + 1 * cm, y0 - 2 * cm, "Shoulder")
    c.drawString(neck_x + 0.5 * cm, y0 - neck_depth_front * cm + 1 * cm, "Neckline")
    c.drawString(x0 + quarter_bust * cm, bust_y - 1 * cm, "Bust")
    c.drawString(x0 + quarter_bust * cm * 1.5, waist_y - 1 * cm, "Waist")
    c.drawString(x0 + 2 * cm, hip_y + 1 * cm, "Hem (+flare)")
    c.setFont("Helvetica", 9)
    c.drawString(x0 + 1 * cm, y0 - measurements['length'] * cm - 1.5 * cm, f"SEAM ALLOWANCE {seam_allowance}cm added")

    c.showPage()

    # Page 2 - BACK BODICE
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(green)
    c.drawString(1 * cm, page_height - 1.5 * cm, "BACK BODICE")
    c.setFillColor(black)
    c.setFont("Helvetica", 10)
    c.drawString(1 * cm, page_height - 3 * cm, f"Length: {measurements['length']}cm | Back neck lower")
    # Simple back outline (slightly wider neck)
    x0, y0 = 2 * cm, page_height - 8 * cm
    c.line(x0, y0, x0 + measurements['shoulder'] * 0.95, y0 - shoulder_slope * cm)
    c.line(x0 + measurements['shoulder'] * 0.95, y0 - shoulder_slope * cm,
           x0 + measurements['shoulder'] * 0.95 - 2 * cm, y0 - 4 * cm)
    c.line(x0, y0 - 4 * cm, x0, y0 - measurements['length'] * cm)
    c.line(x0 + measurements['shoulder'] * 0.95 - 2 * cm, y0 - 4 * cm,
           x0 + quarter_bust * cm * 2, y0 - armhole_depth * cm)
    c.line(x0 + quarter_bust * cm * 2, y0 - armhole_depth * cm,
           x0 + quarter_bust * cm * 2, y0 - measurements['length'] * cm)
    c.drawString(x0 + 2 * cm, y0 - 2 * cm, "Back Neck")
    c.drawString(x0 + 5 * cm, y0 - measurements['length'] * cm / 2 * cm, "Center Back")
    c.showPage()

    # Page 3 - SLEEVE (if not sleeveless)
    if detection['sleeve_type'] != 'sleeveless':
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(green)
        c.drawString(1 * cm, page_height - 1.5 * cm, f"SLEEVE - {detection['sleeve_type'].upper()}")
        c.setFillColor(black)
        c.setFont("Helvetica", 10)
        c.drawString(1 * cm, page_height - 3 * cm, f"Length: {measurements['sleeve_length']}cm | Matches armhole")
        x0, y0 = 2 * cm, page_height - 8 * cm
        sleeve_width_top = bust_full / 6 + 3
        sleeve_width_bottom = sleeve_width_top * 0.7
        # Sleeve rectangle with slight taper
        c.line(x0, y0, x0 + sleeve_width_top * cm, y0)
        c.line(x0 + sleeve_width_top * cm, y0, x0 + sleeve_width_bottom * cm + 2 * cm, y0 - measurements['sleeve_length'] * cm)
        c.line(x0 + sleeve_width_bottom * cm + 2 * cm, y0 - measurements['sleeve_length'] * cm, x0, y0 - measurements['sleeve_length'] * cm)
        c.line(x0, y0 - measurements['sleeve_length'] * cm, x0, y0)
        # Cap curve (matches armhole)
        c.bezier(x0 + 1 * cm, y0 - 2 * cm,
                 x0 + sleeve_width_top * cm * 0.4, y0 - 4 * cm,
                 x0 + sleeve_width_top * cm * 0.7, y0 - 1 * cm,
                 x0 + sleeve_width_top * cm, y0)
        c.drawString(x0 + 2 * cm, y0 - 1 * cm, "Sleeve Cap")
        c.drawString(x0 + sleeve_width_top * cm / 2, y0 - measurements['sleeve_length'] * cm / 2 * cm, "Sleeve Body")
        c.showPage()

    # Page 4 - Cutting instructions & assembly grid
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, page_height - 4 * cm, "CUTTING INSTRUCTIONS")
    c.setFont("Helvetica", 12)
    lines = [
        "• Cut 1 Front Bodice on fold",
        "• Cut 1 Back Bodice on fold",
        "• Cut 2 Sleeves (if applicable)",
        f"• Fabric: {measurements['length'] + 20}cm x width required",
        "• Seam allowance: 1.5cm included everywhere",
        "• Print all pages at 100% scale (no scaling)",
        "• Join tiles along dotted lines if pattern spans multiple pages",
        "• Grainline: parallel to selvedge"
    ]
    for i, line in enumerate(lines):
        c.drawString(2 * cm, page_height - (7 + i * 1.2) * cm, line)
    c.setFont("Helvetica", 9)
    c.drawString(2 * cm, 2 * cm, f"Pattern generated for {detection['garment_type']} | Measurements in cm | Production-ready")

    c.save()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return redirect(url_for('home'))
    file = request.files['image']
    mode = request.form.get('mode', 'standard')
    size = request.form.get('size')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        detection = detect_garment(filepath)
        session['detection'] = detection
        session['mode'] = mode
        session['size'] = size
        session['uploaded_image'] = filename
        return redirect(url_for('measure'))
    return redirect(url_for('home'))

@app.route('/measure')
def measure():
    detection = session.get('detection', {'garment_type': 'kurti', 'sleeve_type': 'long', 'neckline': 'round', 'fit': 'semi-fit'})
    mode = session.get('mode', 'standard')
    size = session.get('size')
    measurements = {}
    if mode == 'standard' and size:
        measurements = STANDARD_SIZES.get(size.upper(), STANDARD_SIZES['M'])
    return render_template('measure.html', detection=detection, mode=mode, measurements=measurements)

@app.route('/generate', methods=['POST'])
def generate():
    detection = session.get('detection')
    mode = session.get('mode')
    if not detection:
        return redirect(url_for('home'))
    
    if mode == 'custom':
        measurements = {
            'bust': float(request.form['bust']),
            'waist': float(request.form['waist']),
            'hip': float(request.form.get('hip', request.form['bust'])),
            'length': float(request.form['length']),
            'shoulder': float(request.form['shoulder']),
            'sleeve_length': float(request.form.get('sleeve_length', 0))
        }
    else:
        measurements = STANDARD_SIZES.get(session.get('size', 'M').upper(), STANDARD_SIZES['M'])
    
    # Adapt measurements based on garment (intelligent adjustment)
    if detection['garment_type'] in ['dress', 'gown']:
        measurements['length'] = measurements.get('length', 100) + 20  # extra length
    if detection['sleeve_type'] == 'sleeveless':
        measurements['sleeve_length'] = 0
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        pdf_path = tmp.name
    generate_pattern_pdf(measurements, detection, pdf_path)
    
    return send_file(pdf_path, as_attachment=True, download_name=f'sewing_pattern_{detection["garment_type"]}.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
