"""Run all v5 renders and assemble outputs (python3 make_v5.py). Needs Blender and PIL (/usr/bin/python3)."""
import subprocess, os, json
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "v5-out"); TMP = os.path.join(OUT, "_tmp")
BL = "/Applications/Blender.app/Contents/MacOS/Blender"
os.makedirs(TMP, exist_ok=True)
def run(pose, out, res, t=0):
    subprocess.run([BL, "-b", "-P", os.path.join(HERE, "toffee_v5.py"), "--", pose, out, str(res), str(t)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
poses = ["wave", "cheer", "point", "think", "encourage", "sleep", "head"]
with ThreadPoolExecutor(4) as ex:
    list(ex.map(lambda p: run(p, f"{TMP}/{p}.png", 1024), poses))
run("idle", f"{TMP}/idle_00.png", 512, 0)       # writes the shared camera shift first
with ThreadPoolExecutor(4) as ex:
    list(ex.map(lambda i: run("idle", f"{TMP}/idle_{i:02d}.png", 512, i / 24), range(1, 24)))
for p in poses:
    Image.open(f"{TMP}/{p}.png").convert("RGBA").resize((512, 512), Image.LANCZOS).save(f"{OUT}/toffee-{p}.webp", quality=90, method=6)
sheet = Image.new("RGBA", (256 * 24, 256))
for i in range(24):
    sheet.paste(Image.open(f"{TMP}/idle_{i:02d}.png").convert("RGBA").resize((256, 256), Image.LANCZOS), (256 * i, 0))
sheet.save(f"{OUT}/toffee-idle-sheet.webp", quality=90, method=6)
json.dump({"frames": 24, "frameWidth": 256, "frameHeight": 256, "fps": 12}, open(f"{OUT}/toffee-idle-sheet.json", "w"))
# idle loop check: frame 23 vs frame 0
a = Image.open(f"{TMP}/idle_23.png").convert("RGBA").resize((384, 384)); b = Image.open(f"{TMP}/idle_00.png").convert("RGBA").resize((384, 384))
c = Image.new("RGBA", (768, 384), (255, 255, 255, 255)); c.alpha_composite(a, (0, 0)); c.alpha_composite(b, (384, 0)); c.save(f"{OUT}/loop-check_23_vs_0.png")
# compare: rows v3, v4, v5
def load(d, name, idx=None):
    if name == "idle":
        s = Image.open(f"{d}/toffee-idle-sheet.webp").convert("RGBA"); w = s.height
        return s.crop((0, 0, w, w))
    return Image.open(f"{d}/toffee-{name}.webp").convert("RGBA")
V1 = os.path.join(HERE, "v3-out"); V2 = os.path.join(HERE, "v4-out")
cols = ["wave", "cheer", "think", "sleep", "head", "idle"]; Cs = 300
img = Image.new("RGBA", (Cs * 6, Cs * 3), (255, 255, 255, 255))
for r, d in enumerate((V1, V2, OUT)):
    for c, n in enumerate(cols):
        im = load(d, n).resize((Cs, Cs), Image.LANCZOS); img.alpha_composite(im, (c * Cs, r * Cs))
img.convert("RGB").save(f"{OUT}/compare.png")
print("done")
