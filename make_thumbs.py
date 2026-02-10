#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageOps

SRC_DIR = Path("assets/catalogue")
OUT_DIR = Path("assets/thumbs")

MODE = "cover"
TARGET_W, TARGET_H = 360, 480
JPEG_QUALITY = 82

EXTS = {".jpg", ".jpeg", ".png", ".webp"}

def make_cover(im, w, h):
    return ImageOps.fit(im, (w, h), Image.Resampling.LANCZOS, centering=(0.5, 0.5))

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    count = 0

    for p in sorted(SRC_DIR.glob("*")):
        if p.suffix.lower() not in EXTS:
            continue
        if not p.stem.isdigit():
            continue

        try:
            with Image.open(p) as im:
                im = im.convert("RGB")
                thumb = make_cover(im, TARGET_W, TARGET_H)
                out = OUT_DIR / f"{int(p.stem):02d}.jpg"
                thumb.save(out, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
                count += 1
        except Exception as e:
            print(f"Skipping {p.name}: {e}")

    print(f"Done. Created {count} thumbnails in: {OUT_DIR}")

if __name__ == "__main__":
    main()

