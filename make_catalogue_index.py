#!/usr/bin/env python3
from pathlib import Path

THUMBS_DIR = Path("assets/thumbs")
OUT_FILE = Path("catalogue/index.html")

HTML_HEAD = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Catalogue — Christou.Art</title>
</head>
<body>
<ul>
"""

HTML_FOOT = """
</ul>
</body>
</html>
"""

def main():
    thumbs = sorted(
        [p for p in THUMBS_DIR.glob("*.jpg") if p.stem.isdigit()],
        key=lambda p: int(p.stem)
    )

    have = {int(p.stem) for p in thumbs}
    expected = set(range(1, 100))
    missing = sorted(expected - have)

    print("Missing thumbnails:", ", ".join(f"{n:02d}" for n in missing) if missing else "none")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUT_FILE.open("w", encoding="utf-8") as f:
        f.write(HTML_HEAD)
        for n in sorted(have):
            nn = f"{n:02d}"
            f.write(f'<li><a href="../image{nn}.html">{nn}</a></li>\n')
        f.write(HTML_FOOT)

    print(f"Catalogue index created with {len(have)} works")

if __name__ == "__main__":
    main()
