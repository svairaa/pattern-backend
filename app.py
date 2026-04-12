from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json

    # Create PDF
    file_path = "pattern.pdf"

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("Dress Pattern (Basic)", styles["Title"]))
    content.append(Paragraph(f"Size: {data.get('size')}", styles["Normal"]))
    content.append(Paragraph(f"Bust: {data.get('bust')} cm", styles["Normal"]))
    content.append(Paragraph(f"Waist: {data.get('waist')} cm", styles["Normal"]))
    content.append(Paragraph(f"Hip: {data.get('hip')} cm", styles["Normal"]))
    content.append(Paragraph(f"Length: {data.get('length')} cm", styles["Normal"]))

    doc.build(content)

    return send_file(file_path, as_attachment=True)
