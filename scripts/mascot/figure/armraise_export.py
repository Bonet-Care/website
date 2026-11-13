"""Render the arm-raise loop (G03 look) as transparent RGBA frames + exact 2D joint positions.
Usage: blender -b -P armraise_export.py -- OUTDIR
Writes OUTDIR/f0000.png ... and OUTDIR/joints.json. build_sheet.py then packs the sprite sheet.
Image-left/right naming: l_* = figure's arm on the image LEFT, r_* = image RIGHT (model-left bone _L = image right = "r")."""
import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mannequin as M
from mannequin import define, build
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

OUT = sys.argv[sys.argv.index("--") + 1]
os.makedirs(OUT, exist_ok=True)
W, H, SS = 360, 540, 2          # frame size, supersample factor
N = 32                          # frames at 12 fps
UP = {"upper_arm_L": (-172, 0, 0), "forearm_L": (0, 0, 0), "clavicle_L": (0, -9, 0),
      "spine": (-3, 0, 0), "chest": (-2, 0, 0), "head": (2, 0, 0)}
# 3 hold at bottom (29..3), 12 up, 4 hold at top (15..18), 11 down; frame N keyed == frame 0 (seamless)
define("ARM", N, [(0, {}), (3, {}), (15, UP), (18, UP), (29, {}), (N, {})], {"arm_L"}, framing="tall", shadow=None,
       cam=dict(az=float(os.environ.get("AZ", 22)), el=float(os.environ.get("EL", 12)), target=(.30, .05, 1.06), scale=float(os.environ.get("SCALE", 2.36))))
ex = build("ARM", 64)
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = W * SS, H * SS
sc.render.film_transparent = True
sc.render.image_settings.color_mode = 'RGBA'
arm = bpy.data.objects["rig"]; cam = sc.camera
sc.frame_start, sc.frame_end = 0, N - 1

def P(bone, t=0.0):
    pb = arm.pose.bones[bone]
    p = arm.matrix_world @ (pb.head + (pb.tail - pb.head) * t)
    return p
def proj(p):
    v = world_to_camera_view(sc, cam, p)
    return [round(v.x * W, 2), round((1 - v.y) * H, 2)]
JOINTS = ["head", "neck", "l_shoulder", "r_shoulder", "l_elbow", "r_elbow", "l_wrist", "r_wrist",
          "l_hip", "r_hip", "l_knee", "r_knee", "l_ankle", "r_ankle"]
# image-left = model R bone (model faces camera), image-right = model L bone
S = {"l": "R", "r": "L"}
points, ang = [], []
ONLY = [int(x) for x in os.environ["FRAMES"].split(",")] if os.environ.get("FRAMES") else range(N)  # FRAMES=16 renders one test frame
for f in ONLY:
    sc.frame_set(f)
    bpy.context.view_layer.update()
    pts = {"head": proj(P("head", .435)), "neck": proj(P("neck"))}
    for s, b in S.items():
        pts[s + "_shoulder"] = proj(P("upper_arm_" + b)); pts[s + "_elbow"] = proj(P("forearm_" + b))
        pts[s + "_wrist"] = proj(P("hand_" + b)); pts[s + "_hip"] = proj(P("thigh_" + b))
        pts[s + "_knee"] = proj(P("shin_" + b)); pts[s + "_ankle"] = proj(P("foot_" + b))
    points.append([pts[j] for j in JOINTS])
    a = P("upper_arm_L", 1) - P("upper_arm_L", 0)
    ang.append(round(math.degrees(math.acos(max(-1, min(1, -a.z / a.length)))), 2))
    sc.render.filepath = os.path.join(OUT, "f%04d.png" % f)
    bpy.ops.render.render(write_still=True)
mx = max(ang)
json.dump({"frames": N, "fps": 12, "frameWidth": W, "frameHeight": H, "joints": JOINTS, "points": points,
           "shoulderAngleDeg": ang, "peakFrames": [i for i, a in enumerate(ang) if a >= mx - 1.0],
           "workingArm": "r", "mirrored": False}, open(os.path.join(OUT, "joints.json"), "w"))
print("done", mx)
