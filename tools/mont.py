"""python3 mont.py OUT.jpg cols file1 file2 ...  (labelled contact sheet)"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
out, cols, files = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
tw, th = 360, 220
rows = (len(files) + cols - 1) // cols
im = Image.new('RGB', (cols * tw, rows * th), 'black'); d = ImageDraw.Draw(im)
try: f = ImageFont.truetype('/root/.fonts/Oswald-Bold.ttf', 18)
except Exception: f = ImageFont.load_default()
for k, fn in enumerate(files):
    try:
        a = Image.open(fn).convert('RGB'); a.thumbnail((tw - 4, th - 24))
        x, y = (k % cols) * tw, (k // cols) * th
        im.paste(a, (x + 2, y + 22)); d.text((x + 4, y + 1), os.path.basename(fn).rsplit('.', 1)[0][:34], fill='yellow', font=f)
    except Exception as e: pass
im.save(out, quality=85)
