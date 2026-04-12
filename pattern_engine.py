def build_pattern(bust, waist, length):

width = bust / 4 + 2
armhole = bust / 6 + 5
neck_w = bust / 12
neck_d = bust / 5

dart = (bust - waist) / 2

sleeve_cap = armhole * 0.75

return {
    "width": width,
    "length": length,
    "armhole": armhole,
    "neck_w": neck_w,
    "neck_d": neck_d,
    "dart": dart,
    "sleeve_cap": sleeve_cap
}
