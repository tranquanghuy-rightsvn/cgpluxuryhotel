#!/usr/bin/env python3
"""Masked pixel-diff for sub pages: compares a fixed region (below the header) of original vs clone."""
import subprocess, sys
from PIL import Image
SK = "/Users/nals_macbook_116/Desktop/web100-news/cloneweb-skill/scripts/pixel-diff.mjs"
OUT = "../reports/diamondseahotel.com"
jobs = [  # name, orig png, clone png, (x0,y0,x1,y1) orig, (x0,y0,x1,y1) clone
    ("newslist-content", "dump/om-news.png", "dump/cm-news.png", (0, 384, 1366, 1250), (0, 384, 1366, 1250)),
    ("article-content", "dump/om-article.png", "dump/cm-article.png", (0, 384, 1366, 1000), (0, 384, 1366, 1000)),
    ("booking-step1", "dump/bk-1.png", "dump/cbk-1.png", (93, 104, 1273, 700), (93, 104, 1273, 700)),
    ("booking-step2", "dump/bk-2.png", "dump/cbk-2.png", (93, 104, 1273, 768), (93, 104, 1273, 768)),
    ("booking-step4", "dump/bk-7.png", "dump/cbk-7.png", (93, 104, 1273, 768), (93, 104, 1273, 768)),
]
only = sys.argv[1:]
for name, o, c, bo, bc in jobs:
    if only and name not in only: continue
    try:
        a = Image.open(o).convert("RGBA").crop(bo); b = Image.open(c).convert("RGBA").crop(bc)
    except FileNotFoundError as e:
        print(name, "missing", e.filename); continue
    pa, pb, pd = f"{OUT}/original-{name}-1366.png", f"{OUT}/clone-{name}-1366.png", f"{OUT}/diff-{name}-1366.png"
    a.save(pa); b.save(pb)
    r = subprocess.run(["node", SK, pa, pb, pd], capture_output=True, text=True)
    print(f"{name:18s}", [l for l in r.stdout.splitlines() if "%" in l][0])
