"""Render looping mascot sprite sheets. Usage: python3 animate.py [clip ...]   (default: all)
Needs Blender and Pillow. Frames render via toffee_v5.py (one Blender process per frame), then one-row WebP sheets
are written to ../../img/mascot/anim/<clip>.webp/.json plus -sm (240 px) variants."""
import subprocess, os, sys, json
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "../../img/mascot/anim"))
TMP = os.environ.get("MASCOT_FRAMES", "/private/tmp/mascot-frames")
BL = "/Applications/Blender.app/Contents/MacOS/Blender"
# clip: (pose, frames, fps, reference T for camera framing)
CLIPS = {"wave": ("wave", 20, 16, 0.0), "cheer": ("cheer", 20, 16, 0.5), "point": ("point", 24, 16, 0.5),
         "wiggle": ("wiggle", 20, 16, 0.0), "tilt": ("tilt", 24, 14, 0.5), "sleep": ("sleep", 24, 12, 0.0),
         "idle": ("idle", 24, 12, 0.0)}
QUALITY = {"wave": 82, "cheer": 82, "point": 82, "wiggle": 82, "tilt": 82, "sleep": 82, "idle": 82}
RES = 480
def render(pose, clip, i, n, ref):
    d = f"{TMP}/{clip}"; os.makedirs(d, exist_ok=True)
    env = dict(os.environ, MASCOT_SHIFT=f"{d}/shift.json", MASCOT_REF=repr(ref), MASCOT_OUT=d)
    subprocess.run([BL, "-b", "-P", os.path.join(HERE, "toffee_v5.py"), "--", pose, f"{d}/f{i:02d}.png", str(RES), repr(i / n)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
def do(clip, quality=None):
    pose, n, fps, ref = CLIPS[clip]
    ri = round(ref * n)
    render(pose, clip, ri, n, ref * 1.0 if abs(ri / n - ref) < 1e-9 else ri / n)
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(lambda i: render(pose, clip, i, n, ri / n), [i for i in range(n) if i != ri]))
    os.makedirs(OUT, exist_ok=True)
    for suf, w in (("", RES), ("-sm", 240)):
        sheet = Image.new("RGBA", (w * n, w))
        for i in range(n):
            im = Image.open(f"{TMP}/{clip}/f{i:02d}.png").convert("RGBA")
            if w != RES: im = im.resize((w, w), Image.LANCZOS)
            sheet.paste(im, (w * i, 0))
        sheet.save(f"{OUT}/{clip}{suf}.webp", quality=quality or QUALITY[clip], method=6)
        json.dump({"frames": n, "fps": fps, "frameWidth": w, "frameHeight": w, "loop": True}, open(f"{OUT}/{clip}{suf}.json", "w"))
        print(clip + suf, os.path.getsize(f"{OUT}/{clip}{suf}.webp") // 1024, "KB")
if __name__ == "__main__":
    for c in (sys.argv[1:] or CLIPS): do(c)
