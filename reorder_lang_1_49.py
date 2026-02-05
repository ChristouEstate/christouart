#!/usr/bin/env python3
from pathlib import Path
import re

START, END = 1, 49

TEXTBLOCK_RE = re.compile(r'(<div\s+class="text-block"\s*>)(.*?)(</div>)', re.DOTALL)
EN_MARK_RE = re.compile(r'<p>\s*<strong>\s*EN:\s*</strong>\s*</p>', re.IGNORECASE)
DE_MARK_RE = re.compile(r'<p>\s*<strong>\s*DE:\s*</strong>\s*</p>', re.IGNORECASE)

def split_by_lang(inner: str):
    en_m = EN_MARK_RE.search(inner)
    de_m = DE_MARK_RE.search(inner)
    if not en_m or not de_m:
        return None, None

    if en_m.start() < de_m.start():
        en = inner[en_m.start():de_m.start()]
        de = inner[de_m.start():]
    else:
        de = inner[de_m.start():en_m.start()]
        en = inner[en_m.start():]
    return en.strip(), de.strip()

def strip_edge_hr(s: str, leading=False, trailing=False):
    if leading:
        s = re.sub(r'^\s*(<hr\s*/?>\s*)+', '', s, flags=re.IGNORECASE)
    if trailing:
        s = re.sub(r'(\s*<hr\s*/?>\s*)+\s*$', '', s, flags=re.IGNORECASE)
    return s.strip()

def process_file(p: Path) -> bool:
    html = p.read_text(encoding="utf-8", errors="ignore")
    m = TEXTBLOCK_RE.search(html)
    if not m:
        return False

    open_div, inner, close_div = m.groups()
    en, de = split_by_lang(inner)
    if not en or not de:
        return False

    en = strip_edge_hr(en, trailing=True)
    de = strip_edge_hr(de, leading=True)

    new_inner = f"{en}\n      <hr />\n      {de}"
    new_block = f"{open_div}\n      {new_inner}\n    {close_div}"

    new_html = html[:m.start()] + new_block + html[m.end():]
    if new_html != html:
        p.write_text(new_html, encoding="utf-8")
        return True
    return False

def pick_filename(i: int) -> Path | None:
    # accept both image1.html and image01.html
    candidates = [Path(f"image{i}.html"), Path(f"image{i:02d}.html")]
    for c in candidates:
        if c.exists():
            return c
    return None

def main():
    changed = missing = failed = 0

    for i in range(START, END + 1):
        p = pick_filename(i)
        if p is None:
            missing += 1
            continue

        ok = process_file(p)
        if ok:
            changed += 1
        else:
            failed += 1

    print(f"Done. Changed: {changed}, missing: {missing}, failed: {failed}")

if __name__ == "__main__":
    main()
