"""Pack OUTDIR/f*.png + joints.json into img/figure/armraise.webp (360x540 frames), armraise-sm.webp (180x270) and armraise.json.
Usage: /usr/bin/python3 build_sheet.py FRAMES_DIR   (needs Pillow)"""
import sys, os, json
from PIL import Image
src = sys.argv[1]
NAME = os.environ.get("NAME", "armraise")  # NAME=armraise-side for the side-on scene sheet (render with AZ=68)
dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "img", "figure")
j = json.load(open(os.path.join(src, "joints.json")))
N, W, H = j["frames"], j["frameWidth"], j["frameHeight"]
cols = 8; rows = -(-N // cols)
j["cols"], j["rows"] = cols, rows
for name, s in ((NAME, 1), (NAME + "-sm", 2)):
    w, h = W // s, H // s
    sheet = Image.new("RGBA", (cols * w, rows * h), (0, 0, 0, 0))
    for i in range(N):
        im = Image.open(os.path.join(src, "f%04d.png" % i)).convert("RGBa").resize((w, h), Image.LANCZOS).convert("RGBA")  # premultiplied resize: no dark fringe
        sheet.paste(im, ((i % cols) * w, (i // cols) * h))
    p = os.path.join(dst, name + ".webp")
    sheet.save(p, "WEBP", quality=80, method=6, exact=False)
    print(name, sheet.size, os.path.getsize(p) // 1024, "KB")
json.dump({k: j[k] for k in ("frames", "fps", "frameWidth", "frameHeight", "cols", "rows", "peakFrames", "joints", "points", "shoulderAngleDeg", "workingArm", "mirrored")},
          open(os.path.join(dst, NAME + ".json"), "w"), separators=(",", ":"))
