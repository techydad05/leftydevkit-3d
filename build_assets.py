#!/usr/bin/env python3
"""Build brick-fist assets from the leftydevkit overlay logo.
- Extracts the blue fist as a binary mask -> brick grid rows (JS array text)
- Saves fist.png (white->transparent crop) for the nav + boot reveal
- Saves downscaled copies of both logos for the page
"""
import os
from PIL import Image

SRC = r"C:\Users\techydad06\Desktop\leftydevkit"
OUT = r"C:\Users\techydad06\Projects\leftydevkit-3d\assets"
os.makedirs(OUT, exist_ok=True)

# ---------- 1. blue fist mask from overlay_logo ----------
im = Image.open(os.path.join(SRC, "overlay_logo.png")).convert("RGB")
w, h = im.size
px = im.load()
mask = Image.new("L", (w, h), 0)
mp = mask.load()
for y in range(h):
    for x in range(w):
        r, g, b = px[x, y]
        if (b - r > 25) and (b - g > 25) and b > 120:
            mp[x, y] = 255

# bbox of fist — EXCLUDE the text band at the bottom (rows with width > 900)
counts = [sum(1 for x in range(w) if mp[x, y]) for y in range(h)]
text_top = next((y for y in range(int(h * 0.6), h) if counts[y] > 900), h)
fist_bottom = max(text_top - 60, 0)
print("text band starts at row", text_top, "-> fist region rows 0..", fist_bottom)

fist_mask = mask.crop((0, 0, w, fist_bottom))
bbox = fist_mask.getbbox()
print("fist bbox:", bbox)
fw, fh = bbox[2] - bbox[0], bbox[3] - bbox[1]
print("fist size:", fw, fh)

# ---------- 2. brick grid ----------
GRID_W = 12
ratio = fh / fw
GRID_H = max(8, round(GRID_W * ratio))
print("grid:", GRID_W, "x", GRID_H)

small = fist_mask.crop(bbox).resize((GRID_W, GRID_H), Image.BOX)
sp = small.load()
rows = []
for y in range(GRID_H):
    row = ""
    for x in range(GRID_W):
        row += "X" if sp[x, y] > 100 else "."
    rows.append(row)
brick_rows = "\n".join(rows)
print("---- brick mask ----")
print(brick_rows)
print("---- end mask ----")
n_bricks = sum(r.count("X") for r in rows)
print("bricks:", n_bricks)

with open(os.path.join(OUT, "fist-mask.txt"), "w") as f:
    f.write(brick_rows + "\n")

# ---------- 3. fist.png (transparent bg, tight crop, 320px tall) ----------
fist = Image.open(os.path.join(SRC, "overlay_logo.png")).convert("RGBA")
fp = fist.load()
for y in range(h):
    for x in range(w):
        r, g, b, a = fp[x, y]
        # white-ish -> transparent; keep blue with full alpha
        if r > 235 and g > 235 and b > 235:
            fp[x, y] = (r, g, b, 0)
        else:
            fp[x, y] = (r, g, b, 255)
crop = fist.crop((bbox[0], 0, bbox[2], fist_bottom))
scale = 320 / crop.height
crop = crop.resize((max(1, round(crop.width * scale)), 320), Image.LANCZOS)
crop.save(os.path.join(OUT, "fist.png"))
print("fist.png saved:", crop.size)

# ---------- 4. overlay-logo.png downscaled (640px wide) ----------
ov = Image.open(os.path.join(SRC, "overlay_logo.png")).convert("RGBA")
ov = ov.resize((640, round(640 * ov.height / ov.width)), Image.LANCZOS)
ov.save(os.path.join(OUT, "overlay-logo.png"))
print("overlay-logo.png saved:", ov.size)

# ---------- 5. reg logo downscaled (900px wide, PNG) ----------
rg = Image.open(os.path.join(SRC, "leftydevkit_logo.png")).convert("RGB")
rg = rg.resize((900, round(900 * rg.height / rg.width)), Image.LANCZOS)
rg.save(os.path.join(OUT, "reg-logo.png"))
print("reg-logo.png saved:", rg.size)

for f in os.listdir(OUT):
    print(f, os.path.getsize(os.path.join(OUT, f)) // 1024, "KB")
