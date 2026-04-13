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
        length = cm(data.get("length"), 100)

        page_w, page_h = A4

        file_path = "pattern.pdf"
        c = canvas.Canvas(file_path, pagesize=A4)

        # -------- SCALE DOWN TO FIT GRID --------
        scale = 0.6
        bw = (bust / 4) * scale
        length = length * scale

        cols = 2
        rows = 2

        part_count = 1

        for row in range(rows):
            for col in range(cols):

                c.setFont("Helvetica", 10)
                c.drawString(20, page_h - 20, f"PART {part_count} (Grid {row+1},{col+1})")

                x = 40
                y = page_h - 60

                # Draw FRONT piece (scaled)
                p = c.beginPath()
                p.moveTo(x, y)

                # neckline
                p.curveTo(x+20, y, x+40, y-10, x+60, y-30)

                # shoulder
                p.lineTo(x + bw, y - 40)

                # armhole
                p.curveTo(x + bw, y - 80, x + bw - 30, y - 120, x + bw - 40, y - 150)

                # waist shaping
                p.lineTo(x + bw - 20, y - length)

                # bottom
                p.lineTo(x, y - length)

                p.lineTo(x, y)

                c.drawPath(p)

                # -------- SEAM ALLOWANCE --------
                c.setDash(2,2)
                c.rect(x-10, y-length-10, bw+20, length+20)
                c.setDash()

                # -------- GRID CUT MARK --------
                c.setFont("Helvetica", 8)
                c.drawString(20, 20, "Cut & Join with adjacent pages")

                c.showPage()
                part_count += 1

        c.save()

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
