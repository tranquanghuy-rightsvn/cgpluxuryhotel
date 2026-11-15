#!/usr/bin/env python3
"""Crop matching sections from original/clone full-page screenshots and run pixel-diff on each.
usage: secdiff.py <orig.png> <orig-sections.json> <clone.png> <clone-sections.json> <outdir> <suffix>
sections json: {"name": [y, h], ...}"""
import json, subprocess, sys, os
from PIL import Image
o_png, o_js, c_png, c_js, out, suf = sys.argv[1:7]
SK = "/Users/nals_macbook_116/Desktop/web100-news/cloneweb-skill/scripts/pixel-diff.mjs"
O, Cc = Image.open(o_png).convert("RGBA"), Image.open(c_png).convert("RGBA")
os_, cs = json.load(open(o_js)), json.load(open(c_js))
os.makedirs(out, exist_ok=True)
res = {}
for name, (oy, oh) in os_.items():
    if name not in cs: continue
    cy, ch = cs[name]
    h = min(oh, ch); w = min(O.size[0], Cc.size[0])
    a = O.crop((0, oy, w, oy + h)); b = Cc.crop((0, cy, w, cy + h))
    pa, pb, pd = f"{out}/original-{name}-{suf}.png", f"{out}/clone-{name}-{suf}.png", f"{out}/diff-{name}-{suf}.png"
    a.save(pa); b.save(pb)
    r = subprocess.run(["node", SK, pa, pb, pd], capture_output=True, text=True)
    txt = [l for l in (r.stdout + r.stderr).splitlines() if "%" in l]
    res[name] = (txt[0].split(":")[1].split("(")[0].strip() if txt else "?") + f"  (orig h{oh} / clone h{ch})"
    print(f"{name:10s} {res[name]}")
json.dump(res, open(f"{out}/diff-{suf}.json", "w"), indent=1)
