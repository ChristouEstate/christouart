#!/usr/bin/env python3
import re
from pathlib import Path

HTML_GLOB = "image*.html"
ASSET_DIR = Path("assets/catalogue")

# src="assets/catalogue/78.jpg"
SRC_RE = re.compile(r'src="assets/catalogue/(\d+)\.jpg"')

def html_num(p: Path):
    m = re.match(r"image(\d+)\.html$", p.name)
    return int(m.group(1)) if m else None

def main():
    html_files = sorted(Path(".").glob(HTML_GLOB), key=lambda p: html_num(p) or 0)
    jpgs = {p.stem for p in ASSET_DIR.glob("*.jpg")}  # stems are numbers like "78"
    jpgs_int = sorted([int(s) for s in jpgs if s.isdigit()])

    print(f"Found {len(html_files)} HTML files, {len(jpgs_int)} JPGs in {ASSET_DIR}/")
    print()

    mismatches = []
    missing_jpg_ref = []
    no_src = []

    for p in html_files:
        n = html_num(p)
        if n is None:
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore")
        m = SRC_RE.search(txt)
        if not m:
            no_src.append(p.name)
            continue
        img = int(m.group(1))
        if img != n:
            mismatches.append((n, img, p.name))
        if str(img) not in jpgs:
            missing_jpg_ref.append((n, img, p.name))

    if mismatches:
        print("MISMATCH (html -> img):")
        for n, img, name in mismatches[:50]:
            print(f"  {name}: {n} -> {img}")
        if len(mismatches) > 50:
            print(f"  ... +{len(mismatches)-50} more")
        print()
    else:
        print("No html/img number mismatches found.\n")

    if missing_jpg_ref:
        print("BROKEN REFERENCES (jpg missing on disk):")
        for n, img, name in missing_jpg_ref[:50]:
            print(f"  {name}: references {img}.jpg (missing)")
        if len(missing_jpg_ref) > 50:
            print(f"  ... +{len(missing_jpg_ref)-50} more")
        print()
    else:
        print("No broken jpg references found.\n")

    if no_src:
        print("NO IMAGE SRC FOUND IN:")
        for name in no_src[:50]:
            print(f"  {name}")
        print()

    # Show gaps in JPG numbering
    if jpgs_int:
        missing_nums = []
        for k in range(min(jpgs_int), max(jpgs_int) + 1):
            if str(k) not in jpgs:
                missing_nums.append(k)
        if missing_nums:
            print("GAPS IN JPG NUMBERING (missing files):")
            print(missing_nums[:80], ("..." if len(missing_nums) > 80 else ""))
        else:
            print("No gaps in jpg numbering range.\n")

if __name__ == "__main__":
    main()
