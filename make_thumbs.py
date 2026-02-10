#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageOps

# -------- Einstellungen --------
SRC_DIR = Path("assets/images")     # <-- HIER deine Originalbilder
OUT_DIR = Path("assets/thumbs")     # <-- Zielordner für Thumbnails

MODE = "cover"  # "cover" (crop) oder "contain" (kein crop)
TARGET_W, TARGET_H = 360, 480       # 3:4 thumbnails (ruhig, hochkant)
JPEG_QUALITY = 82

EXTS = {".jpg", ".jpeg", ".png", ".webp"}
# -------------------------------

def make_cover(im: Image.Image, w: int, h: int) -> Image.Image:
    # croppt mittig auf Zielseitenverhältnis + skaliert
    return ImageOps.fit(im, (w, h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))

def make_contain(im: Image.Image, w: int, h: int) -> Image.Image:
    # skaliert so, dass es in w×h passt (ohne crop) + fügt ggf. Rand hinzu
    im = im.copy()
    im.thumbnail((w, h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (w, h), (245, 245, 245))
    x = (w - im.width) // 2
    y = (h - im.height) // 2
    canvas.paste(im, (x, y))
    return canvas

def main():
    if not SRC_DIR.exists():
        raise SystemExit(f"SRC_DIR not found: {SRC_DIR.resolve()}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    count = 0
    for p in sorted(SRC_DIR.rglob("*")):
        if p.suffix.lower() not in EXTS:
            continue

        with Image.open(p) as im:
            im = im.convert("RGB")

            if MODE == "cover":
                thumb = make_cover(im, TARGET_W, TARGET_H)
            elif MODE == "contain":
                thumb = make_contain(im, TARGET_W, TARGET_H)
            else:
                raise SystemExit('MODE must be "cover" or "contain"')

            out_name = p.stem + ".jpg"        # speichert alles als JPG
            out_path = OUT_DIR / out_name
            thumb.save(out_path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)

        count += 1

    print(f"Done. Created {count} thumbnails in: {OUT_DIR.resolve()}")

if __name__ == "__main__":
    main()
