"""
build_icon.py
Converts assets/logo.png -> assets/icon.ico for use by PyInstaller.
Run once before building: python build_icon.py
"""

import os
from PIL import Image

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
src_png = os.path.join(BASE_DIR, "assets", "logo.png")
dst_ico = os.path.join(BASE_DIR, "assets", "icon.ico")

SIZES = [16, 32, 48, 64, 128, 256]

def convert():
    if not os.path.exists(src_png):
        print(f"[ERROR] Source PNG not found: {src_png}")
        return False

    img = Image.open(src_png).convert("RGBA")

    # Generate each size as a thumbnail
    icons = []
    for size in SIZES:
        resized = img.copy()
        resized.thumbnail((size, size), Image.LANCZOS)
        icons.append(resized)

    # Save multi-size .ico
    icons[0].save(
        dst_ico,
        format="ICO",
        sizes=[(s, s) for s in SIZES],
        append_images=icons[1:]
    )
    print(f"[OK] Icon saved to: {dst_ico}")
    return True

if __name__ == "__main__":
    success = convert()
    if not success:
        exit(1)
