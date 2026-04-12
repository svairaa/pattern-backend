import ezdxf
import uuid

def export_dxf(pattern):

doc = ezdxf.new(dxfversion="R2010")
msp = doc.modelspace()

scale = 10

w = pattern["width"] * scale
l = pattern["length"] * scale
arm = pattern["armhole"] * scale
sleeve = pattern["sleeve_cap"] * scale

# FRONT BODY
msp.add_lwpolyline([
    (0,0), (w,0), (w,l), (0,l), (0,0)
])

# FRONT ARMHOLE
msp.add_arc(center=(w, arm/2), radius=arm/2, start_angle=270, end_angle=360)

# BACK BODY
offset = 200
msp.add_lwpolyline([
    (offset,0), (offset+w,0), (offset+w,l), (offset,l), (offset,0)
])

# BACK ARMHOLE
msp.add_arc(center=(offset+w, arm/2), radius=arm/2-5, start_angle=270, end_angle=360)

# NECKLINE
msp.add_arc(center=(0,0), radius=pattern["neck_w"]*scale, start_angle=0, end_angle=90)

# DART
dx = w/2
msp.add_line((dx, l), (dx-10, l-70))
msp.add_line((dx, l), (dx+10, l-70))

# SLEEVE
msp.add_lwpolyline([
    (100,300),
    (100+sleeve,250),
    (200+sleeve,250),
    (200,300),
    (200,450),
    (100,450),
    (100,300)
])

filename = f"pattern_{uuid.uuid4().hex}.dxf"
doc.saveas(filename)

return filename
