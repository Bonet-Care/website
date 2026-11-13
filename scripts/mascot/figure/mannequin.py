"""Procedural wooden-mannequin exercise demos for the Sync rehab app.

Run headless:
  blender -b -P mannequin.py -- render G03 [G14 F01 ...]   # frames + mp4 + webp
  blender -b -P mannequin.py -- encode G03                  # re-encode existing frames
  blender -b -P mannequin.py -- quick  G03 [..]             # 4 low-sample stills per clip -> work/quick/
  blender -b -P mannequin.py -- still  G03 40               # one test PNG
Outputs: web/public/exercises/anim/<ID>.mp4 and <ID>.webp
Two rigs: 'body' (G-series, full mannequin) and 'hand' (F-series, close-up right hand + forearm stub).
Add an exercise: see define() / define_hand() and the library at the bottom.
"""
import bpy, bmesh, math, os, sys, subprocess, random
from mathutils import Vector, Matrix, Euler

WORK = "/private/tmp/claude-501/-Users-ttp/6894c086-0c0e-479d-bd65-31fa0faa8d5e/scratchpad/mannequin/"
OUT_DIR = "/Users/ttp/Coding-Projects/Sync/web/public/exercises/anim/"
RES, FPS = int(os.environ.get("MANNEQUIN_RES", "512")), 24  # 768 for sharp clips on phone screens
BG = "F7F8FA"
BODY, JOINT, HILITE = "E8E4DE", "CFC8BE", "1F8AE6"
HL_MIX = 0.60
CHAIR_SEAT, CHAIR_LEG = "CDBFA8", "B3A58F"
FFMPEG = "/opt/homebrew/bin/ffmpeg"


def hexs(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def lin(c):
    f = lambda v: v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return tuple(f(v) for v in c)


def mix_hex(a, b, t):
    A, B = hexs(a), hexs(b)
    return tuple(A[i] * (1 - t) + B[i] * t for i in range(3))


def seg(name, bone, p0, p1, r, kind, group, k=1.04):
    """Capsule-ish ellipsoid between two points (rest pose)."""
    a, b = Vector(p0), Vector(p1)
    d = b - a
    return (name, bone, tuple((a + b) / 2), (r, r, d.length / 2 * k), kind, group, tuple(d))


# =========================================================================== BODY RIG
# name: (parent, head, tail)   Z up, character faces -Y, model-left = +X (viewer's right).
def _sk():
    S = {}
    S["hips"] = (None, (0, 0, .91), (0, 0, 1.0))
    S["spine"] = ("hips", (0, 0, 1.0), (0, 0, 1.16))
    S["chest"] = ("spine", (0, 0, 1.16), (0, 0, 1.45))
    S["neck"] = ("chest", (0, 0, 1.46), (0, 0, 1.55))
    S["head"] = ("neck", (0, 0, 1.55), (0, 0, 1.75))
    for s, k in (("L", 1), ("R", -1)):
        S["clavicle_" + s] = ("chest", (.03 * k, 0, 1.43), (.20 * k, 0, 1.45))
        S["upper_arm_" + s] = ("clavicle_" + s, (.20 * k, 0, 1.45), (.20 * k, 0, 1.15))
        S["forearm_" + s] = ("upper_arm_" + s, (.20 * k, 0, 1.15), (.20 * k, 0, .90))
        S["hand_" + s] = ("forearm_" + s, (.20 * k, 0, .90), (.20 * k, 0, .72))
        S["thigh_" + s] = ("hips", (.09 * k, 0, .91), (.09 * k, 0, .50))
        S["shin_" + s] = ("thigh_" + s, (.09 * k, 0, .50), (.09 * k, 0, .08))
        S["foot_" + s] = ("shin_" + s, (.09 * k, 0, .08), (.09 * k, -.16, .03))
    return S


# parts: (name, bone, centre, radii(x,y,z), kind, group[, axis]); kind 'seg' body colour, 'jt' joint colour
def _parts():
    P = []
    a = P.append
    a(("pelvis", "hips", (0, 0, .955), (.142, .092, .105), "seg", "torso"))
    a(("abdomen", "spine", (0, 0, 1.10), (.118, .086, .10), "seg", "torso"))
    a(("waist_j", "spine", (0, 0, 1.03), (.098, .074, .078), "jt", "torso"))
    a(("chest", "chest", (0, 0, 1.31), (.162, .103, .165), "seg", "upper_torso"))
    a(("yoke", "chest", (0, 0, 1.405), (.18, .092, .064), "seg", "upper_torso"))
    a(("chest_j", "chest", (0, 0, 1.172), (.092, .072, .066), "jt", "upper_torso"))
    a(("neck", "neck", (0, 0, 1.51), (.04, .042, .066), "seg", "head"))
    a(("neck_j", "neck", (0, 0, 1.455), (.05, .05, .04), "jt", "head"))
    a(("head_j", "head", (0, 0, 1.555), (.048, .048, .04), "jt", "head"))
    a(("head", "head", (0, -.008, 1.637), (.078, .094, .113), "seg", "head"))
    a(("chin", "head", (0, -.056, 1.58), (.054, .058, .054), "seg", "head"))  # soft jaw: gives facing direction, no face
    a(("nose", "head", (0, -.100, 1.632), (.016, .026, .024), "seg", "head"))  # small nub so head turns read from the front
    for s, k in (("L", 1), ("R", -1)):
        g = "arm_" + s
        a(("clav_" + s, "clavicle_" + s, (.115 * k, 0, 1.44), (.09, .03, .03), "seg", "upper_torso"))
        a(("shoulder_j_" + s, "upper_arm_" + s, (.20 * k, 0, 1.445), (.052, .052, .052), "jt", g))
        a(("uarm_" + s, "upper_arm_" + s, (.20 * k, 0, 1.30), (.043, .043, .138), "seg", g))
        a(("elbow_j_" + s, "forearm_" + s, (.20 * k, 0, 1.15), (.040, .040, .040), "jt", g))
        a(("farm_" + s, "forearm_" + s, (.20 * k, 0, 1.025), (.036, .036, .117), "seg", g))
        a(("wrist_j_" + s, "hand_" + s, (.20 * k, 0, .90), (.030, .030, .030), "jt", g))
        # mitten hand with thumb (thumb points forward when the arm hangs)
        a(("palm_" + s, "hand_" + s, (.20 * k, -.002, .838), (.021, .041, .066), "seg", g))
        a(("fingers_" + s, "hand_" + s, (.20 * k, 0, .782), (.017, .036, .062), "seg", g))
        a(seg("thumb_" + s, "hand_" + s, (.20 * k, -.026, .868), (.20 * k, -.060, .812), .0135, "seg", g))
        g = "leg_" + s
        a(("hip_j_" + s, "thigh_" + s, (.09 * k, 0, .91), (.062, .062, .062), "jt", g))
        a(("thigh_" + s, "thigh_" + s, (.09 * k, 0, .705), (.066, .074, .192), "seg", g))
        a(("knee_j_" + s, "shin_" + s, (.09 * k, 0, .50), (.054, .054, .054), "jt", g))
        a(("shin_" + s, "shin_" + s, (.09 * k, 0, .29), (.050, .054, .195), "seg", g))
        a(("ankle_j_" + s, "foot_" + s, (.09 * k, 0, .085), (.042, .042, .042), "jt", g))
        a(("foot_" + s, "foot_" + s, (.09 * k, -.06, .042), (.040, .105, .038), "seg", g))
    return P


L1, L2 = .41, .42  # thigh / shin length

# =========================================================================== HAND RIG
FINGERS = [("index", .034, (.042, .026, .021), .0118), ("middle", .0115, (.047, .030, .022), .0122),
           ("ring", -.011, (.043, .027, .021), .0115), ("pinky", -.029, (.034, .021, .018), .0100)]
KN = .09  # knuckle height above wrist
THUMB_PTS = [(.030, -.004, .022), (.056, -.014, .058), (.071, -.019, .087), (.080, -.023, .113)]


def _hsk():
    S = {}
    S["forearm"] = (None, (0, 0, -.25), (0, 0, 0))
    S["hand"] = ("forearm", (0, 0, 0), (0, 0, KN))
    for f, x, ls, r in FINGERS:
        z = KN
        par = "hand"
        for i, (seg_n, l) in enumerate(zip(("prox", "mid", "dist"), ls)):
            S[f"{f}_{seg_n}"] = (par, (x, 0, z), (x, 0, z + l))
            par = f"{f}_{seg_n}"; z += l
    for i, n in enumerate(("mc", "prox", "dist")):
        S["thumb_" + n] = ("hand" if i == 0 else "thumb_" + ("mc", "prox")[i - 1], THUMB_PTS[i], THUMB_PTS[i + 1])
    return S


def _hparts():
    P = []
    a = P.append
    hand = ("palm", "thumb", "index", "middle", "ring", "pinky")
    a(("forearm", "forearm", (0, 0, -.13), (.032, .026, .135), "seg", "forearm"))
    a(("wrist_j", "hand", (0, 0, 0), (.027, .022, .024), "jt", "palm"))
    a(("palm", "hand", (.002, -.002, .050), (.043, .0150, .049), "seg", "palm"))
    a(("thenar", "hand", (.028, -.008, .034), (.021, .0145, .031), "seg", "palm"))
    for f, x, ls, r in FINGERS:
        z = KN
        a((f"{f}_j0", f"{f}_prox", (x, 0, z), (r * .95,) * 3, "jt", f))
        for i, (seg_n, l) in enumerate(zip(("prox", "mid", "dist"), ls)):
            rr = r * (1, .93, .85)[i]
            a(seg(f"{f}_{seg_n}", f"{f}_{seg_n}", (x, 0, z), (x, 0, z + l), rr, "seg", f, 1.06))
            z += l
            if i < 2:
                a((f"{f}_j{i+1}", f"{f}_{('mid','dist')[i]}", (x, 0, z), (rr * .8,) * 3, "jt", f))
    for i, (n, r) in enumerate((("mc", .0150), ("prox", .0128), ("dist", .0112))):
        a(seg("thumb_" + n, "thumb_" + n, THUMB_PTS[i], THUMB_PTS[i + 1], r, "seg", "thumb", 1.0))
        a((f"thumb_j{i}", "thumb_" + n, THUMB_PTS[i], (r * .85,) * 3, "jt", "thumb"))
    return P


RIGS = {"body": dict(skel=_sk(), parts=_parts(), root="hips"),
        "hand": dict(skel=_hsk(), parts=_hparts(), root="forearm")}
CUR = {}


# =========================================================================== scene helpers
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene


def material(name, rgb, rough=.52, sheen=.25, spec=.35):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*lin(rgb), 1)
    b.inputs["Roughness"].default_value = rough
    for k, v in (("Specular IOR Level", spec), ("Sheen Weight", sheen), ("Sheen Roughness", .5)):
        try: b.inputs[k].default_value = v
        except Exception: pass
    return m


def ellipsoid(name, centre, radii, mat, axis=None, segs=36, rings=20):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=1.0)
    M = Vector((0, 0, 1)).rotation_difference(Vector(axis).normalized()).to_matrix() if axis else Matrix.Identity(3)
    for v in bm.verts:
        v.co = M @ Vector((v.co.x * radii[0], v.co.y * radii[1], v.co.z * radii[2])) + Vector(centre)
    for f in bm.faces: f.smooth = True
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def rbox(name, centre, size, mat, parent, bevel=.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=centre)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(scale=True)
    bv = ob.modifiers.new("bv", 'BEVEL'); bv.width = bevel; bv.segments = 4
    bpy.ops.object.shade_smooth()
    ob.data.materials.append(mat)
    ob.parent = parent
    return ob


def build_rig(skel):
    arm_d = bpy.data.armatures.new("rig")
    arm = bpy.data.objects.new("rig", arm_d)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    eb = {}
    for n, (p, h, t) in skel.items():
        b = arm_d.edit_bones.new(n)
        b.head, b.tail = Vector(h), Vector(t)
        eb[n] = b
    for n, (p, h, t) in skel.items():
        if p: eb[n].parent = eb[p]
    bpy.ops.object.mode_set(mode='OBJECT')
    return arm


def attach(ob, arm, bone):
    b = arm.data.bones[bone]
    ob.parent = arm; ob.parent_type = 'BONE'; ob.parent_bone = bone
    ob.matrix_parent_inverse = (arm.matrix_world @ b.matrix_local @ Matrix.Translation((0, b.length, 0))).inverted()


def build_parts(arm, parts, highlight):
    mats = {}

    def mat(kind, hot):
        key = (kind, hot)
        if key not in mats:
            base = BODY if kind == "seg" else JOINT
            mats[key] = material(f"{kind}{'_hl' if hot else ''}", mix_hex(base, HILITE, HL_MIX) if hot else hexs(base))
        return mats[key]
    for p in parts:
        name, bone, c, r, kind, grp = p[:6]
        ob = ellipsoid(name, c, r, mat(kind, grp in highlight), axis=p[6] if len(p) > 6 else None)
        attach(ob, arm, bone)


# Streamlined look: each limb is one tapered tube lofted along its bone chain and skinned with weights that blend
# across the joints, so elbows, knees and fingers bend as smooth curves instead of beads on a string.
STYLE = os.environ.get("MANNEQUIN_STYLE", "skin")  # "parts" = the old beaded look


def _body_lofts():
    L = []
    T = [((0, 0, .875), .07, .06), ((0, 0, .91), .128, .088), ((0, 0, .955), .14, .092), ((0, 0, 1.0), .118, .082),
         ((0, 0, 1.05), .104, .076), ((0, 0, 1.10), .108, .08), ((0, 0, 1.16), .122, .086), ((0, 0, 1.23), .148, .097),
         ((0, 0, 1.31), .163, .103), ((0, 0, 1.38), .165, .098), ((0, 0, 1.43), .14, .085), ((0, 0, 1.465), .06, .055),
         ((0, 0, 1.49), .042, .043), ((0, 0, 1.53), .04, .042), ((0, -.004, 1.56), .05, .056), ((0, -.01, 1.59), .07, .085),
         ((0, -.01, 1.635), .08, .096), ((0, -.008, 1.69), .076, .09), ((0, -.004, 1.73), .055, .066)]
    L.append(("torso", T, [("hips", 0), ("spine", 3), ("chest", 6), ("neck", 11), ("head", 14)],
              [("torso", 0), ("upper_torso", 6), ("head", 11)]))
    for s, k in (("L", 1), ("R", -1)):
        x = .20 * k
        A = [(1.468, .036, .036), (1.44, .05, .05), (1.39, .048, .048), (1.30, .044, .044), (1.20, .04, .04), (1.15, .04, .04),
             (1.10, .038, .038), (1.02, .036, .036), (.94, .03, .03), (.90, .027, .029), (.87, .021, .036), (.835, .022, .042),
             (.80, .02, .04), (.76, .017, .035), (.735, .013, .026)]
        L.append(("arm_" + s, [((x, 0, z), a, b) for z, a, b in A],
                  [("upper_arm_" + s, 0), ("forearm_" + s, 5), ("hand_" + s, 9)], [("arm_" + s, 0)]))
        x = .09 * k
        G = [(.965, .045, .05), (.92, .07, .076), (.86, .071, .078), (.76, .067, .073), (.64, .059, .063), (.55, .052, .055),
             (.50, .05, .053), (.45, .05, .054), (.37, .052, .056), (.28, .047, .051), (.18, .039, .043), (.11, .035, .039),
             (.08, .036, .04), (.055, .034, .038)]
        L.append(("leg_" + s, [((x, 0, z), a, b) for z, a, b in G],
                  [("thigh_" + s, 0), ("shin_" + s, 6), ("foot_" + s, 12)], [("leg_" + s, 0)]))
    keep = ("chin", "nose", "thumb_L", "thumb_R", "foot_L", "foot_R")
    return L, [p for p in _parts() if p[0] in keep], dict(step=.012, seg=28)


def _hand_lofts():
    L = []
    F = [((0, 0, -.25), .034, .028), ((0, 0, -.15), .033, .027), ((0, 0, -.06), .029, .024), ((0, 0, -.015), .026, .021),
         ((0, 0, 0), .026, .02), ((.001, -.001, .012), .031, .018), ((.002, -.002, .03), .041, .0165), ((.002, -.002, .05), .045, .0155),
         ((.002, -.002, .072), .045, .0145), ((.002, -.001, .088), .042, .0135), ((.002, 0, .097), .036, .012)]
    L.append(("forearm", F, [("forearm", 0), ("hand", 4)], [("forearm", 0), ("palm", 4)]))
    for f, x, ls, r in FINGERS:
        z1, z2, z3 = KN + ls[0], KN + ls[0] + ls[1], KN + sum(ls)
        P = [((x, 0, KN - .014), r * .92, r * .92), ((x, 0, KN), r, r), ((x, 0, z1), r * .95, r * .95),
             ((x, 0, z2), r * .88, r * .88), ((x, 0, z3 - r * .6), r * .8, r * .8)]
        L.append((f, P, [(f + "_prox", 0), (f + "_mid", 2), (f + "_dist", 3)], [(f, 0)]))
    tp = [Vector(q) for q in THUMB_PTS]
    P = [(tuple(tp[0]), .0155, .0155), (tuple(tp[1]), .014, .014), (tuple(tp[2]), .0122, .0122),
         (tuple(tp[3] - (tp[3] - tp[2]).normalized() * .006), .0105, .0105)]
    L.append(("thumb", P, [("thumb_mc", 0), ("thumb_prox", 1), ("thumb_dist", 2)], [("thumb", 0)]))
    return L, [p for p in _hparts() if p[0] == "thenar"], dict(step=.0016, seg=24)


LOFTS = {"body": _body_lofts, "hand": _hand_lofts}


def _sstep(t):
    import numpy as np
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def loft(name, stations, bones, groups, highlight, arm, mat, step, seg):
    import numpy as np
    P = np.array([st[0] for st in stations], float); R = np.array([[st[1], st[2]] for st in stations], float)
    cum = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    n = max(4, int(math.ceil(cum[-1] / step)))
    sp = np.linspace(0, cum[-1], n + 1)
    C = np.stack([np.interp(sp, cum, P[:, i]) for i in range(3)], 1)
    Rr = np.stack([np.interp(sp, cum, R[:, i]) for i in range(2)], 1)
    for _ in range(3):  # round off the corners of the piecewise-linear radius profile
        Rr[1:-1] = (Rr[:-2] + 2 * Rr[1:-1] + Rr[2:]) / 4
        C[1:-1] = (C[:-2] + 2 * C[1:-1] + C[2:]) / 4
    Tg = np.gradient(C, axis=0); Tg /= np.linalg.norm(Tg, axis=1, keepdims=True)

    def ramp(items, k):  # 0..1 across the joint where item k starts
        if k == 0: return np.ones(len(sp))
        at = cum[items[k][1]]
        bw = 1.25 * float(np.interp(at, cum, R.mean(1)))
        return _sstep((sp - at) / (2 * bw) + .5)
    S = [ramp(bones, k) for k in range(len(bones))] + [np.zeros(len(sp))]
    Wb = [S[k] - S[k + 1] for k in range(len(bones))]
    Sg = [ramp(groups, k) for k in range(len(groups))] + [np.zeros(len(sp))]
    hl = sum((Sg[k] - Sg[k + 1]) * (1.0 if groups[k][0] in highlight else 0.0) for k in range(len(groups)))
    # ring list: (centre, tangent, rx, ry, station index); hemispherical caps at both ends
    rings = []
    for end, sign in ((0, -1), (n, 1)):
        cap = []
        rc = min(Rr[end]) * .9
        for th in (30, 60):
            a = math.radians(th)
            cap.append((C[end] + sign * Tg[end] * rc * math.sin(a), Tg[end], Rr[end][0] * math.cos(a), Rr[end][1] * math.cos(a), end))
        pole = (C[end] + sign * Tg[end] * rc, end)
        if sign < 0: start_cap, start_pole = cap[::-1], pole
        else: end_cap, end_pole = cap, pole
    rings = start_cap + [(C[i], Tg[i], Rr[i][0], Rr[i][1], i) for i in range(n + 1)] + end_cap
    verts, vidx = [], []
    X = np.array([1.0, 0, 0])
    for c, t, rx, ry, si in rings:
        u = X - X.dot(t) * t; u /= np.linalg.norm(u); v = np.cross(t, u)
        for q in range(seg):
            a = 2 * math.pi * q / seg
            verts.append(tuple(c + rx * math.cos(a) * u + ry * math.sin(a) * v)); vidx.append(si)
    faces = []
    for r in range(len(rings) - 1):
        for q in range(seg):
            a, b = r * seg + q, r * seg + (q + 1) % seg
            faces.append((a, b, b + seg, a + seg))
    p0 = len(verts); verts.append(tuple(start_pole[0])); vidx.append(start_pole[1])
    p1 = len(verts); verts.append(tuple(end_pole[0])); vidx.append(end_pole[1])
    last = (len(rings) - 1) * seg
    for q in range(seg):
        faces.append((p0, (q + 1) % seg, q)); faces.append((p1, last + q, last + (q + 1) % seg))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces: f.smooth = True
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    for k, (b, _) in enumerate(bones):
        vg = ob.vertex_groups.new(name=b)
        for i, si in enumerate(vidx):
            w = float(Wb[k][si])
            if w > .003: vg.add([i], w, 'REPLACE')
    ca = me.color_attributes.new("hl", 'FLOAT_COLOR', 'POINT')
    ca.data.foreach_set("color", np.repeat(np.array([hl[si] for si in vidx])[:, None], 4, axis=1).ravel())
    me.materials.append(mat)
    ob.parent = arm
    md = ob.modifiers.new("arm", 'ARMATURE'); md.object = arm; md.use_deform_preserve_volume = True
    sub = ob.modifiers.new("sub", 'SUBSURF'); sub.levels = 1; sub.render_levels = 1
    return ob


def build_skin(arm, rig, highlight):
    lofts, extras, cfg = LOFTS[rig]()
    m = material("skin", hexs(BODY)); nt = m.node_tree; bsdf = nt.nodes["Principled BSDF"]
    at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_name = "hl"
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
    mx.inputs[6].default_value = (*lin(hexs(BODY)), 1); mx.inputs[7].default_value = (*lin(mix_hex(BODY, HILITE, HL_MIX)), 1)
    nt.links.new(at.outputs["Fac"], mx.inputs[0]); nt.links.new(mx.outputs[2], bsdf.inputs["Base Color"])
    for name, stations, bones, groups in lofts:
        loft(name, stations, bones, groups, highlight, arm, m, cfg["step"], cfg["seg"])
    solid = {False: material("body", hexs(BODY)), True: material("body_hl", mix_hex(BODY, HILITE, HL_MIX))}
    for p in extras:
        name, bone, c, r, kind, grp = p[:6]
        attach(ellipsoid(name, c, r, solid[grp in highlight], axis=p[6] if len(p) > 6 else None), arm, bone)


def build_chair(x=0, y=.34, rot=0, back_h=.46):
    root = bpy.data.objects.new("chair", None); bpy.context.scene.collection.objects.link(root)
    root.location = (x, y, 0); root.rotation_euler = (0, 0, math.radians(rot))
    ms = material("chair_seat", hexs(CHAIR_SEAT), rough=.6, sheen=0)
    ml = material("chair_leg", hexs(CHAIR_LEG), rough=.6, sheen=0)
    top = .43; w, d = .46, .42
    rbox("seat", (0, 0, top - .02), (w, d, .04), ms, root, .012)
    for lx in (-.2, .2):
        for ly in (-.18, .18):
            rbox("leg", (lx, ly, (top - .04) / 2), (.04, .04, top - .04), ml, root, .01)
    for lx in (-.2, .2):
        rbox("post", (lx, .19, top + back_h / 2), (.035, .035, back_h), ml, root, .01)
    for z in (top + back_h - .31, top + back_h - .10):
        rbox("rail", (0, .19, z), (.42, .03, .07), ms, root, .01)
    bpy.context.view_layer.update()
    for ob in root.children:  # keep world placement relative to root
        ob.matrix_parent_inverse = root.matrix_world.inverted() @ Matrix.Identity(4)
        ob.matrix_parent_inverse = Matrix.Identity(4)


def build_stage(shadow):
    sc = bpy.context.scene
    # flat background; the world lights the model a bit dimmer than the camera sees it
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    nt = w.node_tree; nt.nodes.clear()
    bgc, bga = nt.nodes.new("ShaderNodeBackground"), nt.nodes.new("ShaderNodeBackground")
    for n, s in ((bgc, 1.0), (bga, 0.46)):
        n.inputs["Color"].default_value = (*lin(hexs(BG)), 1); n.inputs["Strength"].default_value = s
    lp = nt.nodes.new("ShaderNodeLightPath"); mx = nt.nodes.new("ShaderNodeMixShader"); o = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0])
    nt.links.new(bga.outputs[0], mx.inputs[1]); nt.links.new(bgc.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], o.inputs[0])
    if not shadow: return
    sx, sy, cx, cy = shadow
    # fake soft contact shadow: radial-gradient emission disc fading to exactly BG at its edge
    bpy.ops.mesh.primitive_plane_add(size=2, location=(cx, cy, .0015))
    pl = bpy.context.active_object; pl.name = "shadow"; pl.scale = (sx, sy, 1)
    m = bpy.data.materials.new("shadow"); m.use_nodes = True; t = m.node_tree; t.nodes.clear()
    tc = t.nodes.new("ShaderNodeTexCoord")
    mp = t.nodes.new("ShaderNodeMapping")
    mp.inputs["Location"].default_value = (-1, -1, 0); mp.inputs["Scale"].default_value = (2, 2, 2)
    sp = t.nodes.new("ShaderNodeTexGradient"); sp.gradient_type = 'SPHERICAL'
    pw = t.nodes.new("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = 1.5
    mixc = t.nodes.new("ShaderNodeMix"); mixc.data_type = 'RGBA'
    mixc.inputs[6].default_value = (*lin(hexs(BG)), 1)
    mixc.inputs[7].default_value = (*lin(hexs("B4B9C3")), 1)
    em = t.nodes.new("ShaderNodeEmission"); out = t.nodes.new("ShaderNodeOutputMaterial")
    t.links.new(tc.outputs["UV"], mp.inputs["Vector"])
    t.links.new(mp.outputs[0], sp.inputs[0])
    t.links.new(sp.outputs["Fac"], pw.inputs[0])
    t.links.new(pw.outputs[0], mixc.inputs[0])
    t.links.new(mixc.outputs[2], em.inputs["Color"]); t.links.new(em.outputs[0], out.inputs[0])
    pl.data.materials.append(m)


def lights(aim_at=(0, 0, 1.0), scale=1.0):
    sc = bpy.context.scene
    aim = bpy.data.objects.new("aim", None); sc.collection.objects.link(aim); aim.location = aim_at
    for n, loc, e, sz in (("key", (2.2, -3.2, 3.6), 225, 3.5), ("fill", (-3, -2.2, 1.6), 75, 4.0), ("rim", (-1.5, 3, 3), 35, 3.0)):
        d = bpy.data.lights.new(n, 'AREA'); d.energy = e; d.size = sz; d.color = (1, .985, .96)
        ob = bpy.data.objects.new(n, d); sc.collection.objects.link(ob)
        ob.location = Vector(aim_at) + Vector(loc) - Vector((0, 0, 1.0))
        c = ob.constraints.new('TRACK_TO'); c.target = aim; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'


# camera presets: same rules for all clips (orthographic, az 25 deg off front toward model-left, 8 deg above)
CAMS = {"tall": dict(target=(0, .05, 1.03), scale=2.36),     # standing, arms can go overhead
        "full": dict(target=(0, .05, .90), scale=1.98),      # standing / sit-to-stand
        "seated": dict(target=(0, .08, .72), scale=1.62),    # seated on chair
        "upper": dict(target=(0, 0, 1.28), scale=1.15),      # head, shoulders, torso
        "hand": dict(target=(.004, 0, .088), scale=.29)}


def camera(framing, over):
    c = dict(CAMS[framing]); c.update(over or {})
    az, el = math.radians(c.get("az", 25)), math.radians(c.get("el", 8))
    tgt = c["target"]
    cd = bpy.data.cameras.new("cam"); cd.type = 'ORTHO'; cd.ortho_scale = c["scale"]
    cam = bpy.data.objects.new("cam", cd); bpy.context.scene.collection.objects.link(cam)
    cam.location = Vector(tgt) + Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))) * 8
    e = bpy.data.objects.new("camaim", None); bpy.context.scene.collection.objects.link(e); e.location = tgt
    t = cam.constraints.new('TRACK_TO'); t.target = e; t.track_axis = 'TRACK_NEGATIVE_Z'; t.up_axis = 'UP_Y'
    bpy.context.scene.camera = cam
    return tgt


def render_settings(samples=48):
    sc = bpy.context.scene
    for n in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'):
        try: sc.render.engine = n; break
        except Exception: pass
    sc.render.resolution_x = sc.render.resolution_y = RES
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.render.fps = FPS
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGB'
    sc.view_settings.view_transform = 'Standard'
    try: sc.view_settings.look = 'None'
    except Exception: pass
    try: sc.eevee.taa_render_samples = samples
    except Exception: pass
    for a, v in (("use_raytracing", True), ("use_gtao", True), ("gtao_distance", .5), ("use_shadows", True), ("use_soft_shadows", True)):
        try: setattr(sc.eevee, a, v)
        except Exception: pass


# =========================================================================== posing
def rest_pose(rig):
    sk = RIGS[rig]["skel"]
    p = {n: (0.0, 0.0, 0.0) for n in sk}
    p["root"] = (0.0, 0.0, 0.0)
    if rig == "body":
        p.update({"upper_arm_L": (0, -5, 0), "upper_arm_R": (0, 5, 0), "forearm_L": (-6, 0, 0), "forearm_R": (-6, 0, 0)})
    return p


def full_pose(rig, d):
    """Merge a partial pose over REST and expand *_B keys (both sides, mirrored: ry and rz flip)."""
    p = rest_pose(rig)
    for k, v in d.items():
        if k.endswith("_B"):
            b = k[:-2]
            p[b + "_L"] = tuple(v)
            p[b + "_R"] = (v[0], -v[1], -v[2])
        else:
            p[k] = tuple(v)
    return p


_prev = {}


def apply_pose(arm, pose):
    """pose: bone -> (rx, ry, rz) degrees about rest-aligned world axes, applied in the parent's frame.
    Body: on a hanging limb negative rx swings forward (flexion); on an upright bone positive rx leans forward;
    +ry on an upright bone tilts it toward +X (model-left); +rz on a forward-pointing bone swings it toward +X.
    'root' = translation of the root bone in metres (x, y, z)."""
    for pb in arm.pose.bones:
        n = pb.name
        pb.rotation_mode = 'QUATERNION'
        R = arm.data.bones[n].matrix_local.to_3x3()
        r = Euler([math.radians(a) for a in pose[n]], 'XYZ').to_matrix()
        q = (R.inverted() @ r @ R).to_quaternion()
        if n in _prev: q.make_compatible(_prev[n])
        _prev[n] = q
        pb.rotation_quaternion = q
    rb = CUR["root"]
    R = arm.data.bones[rb].matrix_local.to_3x3()
    arm.pose.bones[rb].location = R.inverted() @ Vector(pose["root"])


def key_pose(arm, pose, frame):
    apply_pose(arm, pose)
    for pb in arm.pose.bones:
        pb.keyframe_insert("rotation_quaternion", frame=frame)
    arm.pose.bones[CUR["root"]].keyframe_insert("location", frame=frame)


def ease_curves(arm):
    act = arm.animation_data.action
    fcs = []
    try:
        for layer in act.layers:
            for strip in layer.strips:
                for cb in strip.channelbags: fcs += list(cb.fcurves)
    except Exception:
        fcs = list(act.fcurves)
    for fc in fcs:
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'; kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'


# ---- leg helpers (sagittal)
def leg_ik(hip_yz, ankle_yz):
    dy, dz = ankle_yz[0] - hip_yz[0], ankle_yz[1] - hip_yz[1]
    D = min(math.hypot(dy, dz), (L1 + L2) * .9995)
    al = math.atan2(dy, -dz)
    be = math.acos(max(-1, min(1, (L1 * L1 + D * D - L2 * L2) / (2 * L1 * D))))
    p1 = al - be
    ky, kz = hip_yz[0] + L1 * math.sin(p1), hip_yz[1] - L1 * math.cos(p1)
    p2 = math.atan2(ankle_yz[0] - ky, -(ankle_yz[1] - kz))
    return math.degrees(p1), math.degrees(p2)


def planted_legs(hip_y, hip_z, hips_rx, ankle_y=0.0):
    """Legs + flat feet planted at ankle_y while the hips move to (hip_y, hip_z); hips_rx = pelvis forward tilt."""
    p1, p2 = leg_ik((hip_y, hip_z), (ankle_y, .08))
    return {"root": (0, hip_y, hip_z - .91), "hips": (hips_rx, 0, 0),
            "thigh_B": (p1 - hips_rx, 0, 0), "shin_B": (p2 - p1, 0, 0), "foot_B": (-p2, 0, 0)}


def legW(side, tw, sw, fw, hips_rx=0):
    """One leg from WORLD sagittal angles (thigh, shin, foot); negative = forward/up for the thigh."""
    return {f"thigh_{side}": (tw - hips_rx, 0, 0), f"shin_{side}": (sw - tw, 0, 0), f"foot_{side}": (fw - sw, 0, 0)}


# =========================================================================== forward kinematics + tiny IK (hand rig)
def fk(skel, pose, chain):
    """Posed (head, tail) of bones along a chain (parents first)."""
    Q, head, out = {}, {}, {}
    off = Vector(pose.get("root", (0, 0, 0)))
    for n in chain:
        p, h, t = skel[n]
        r = Euler([math.radians(a) for a in pose[n]], 'XYZ').to_matrix()
        Qp = Q[p] if p in Q else Matrix.Identity(3)
        Q[n] = Qp @ r
        hp = Vector(h) + off if p not in head else head[p] + Qp @ (Vector(h) - Vector(skel[p][1]))
        head[n] = hp
        out[n] = (hp, hp + Q[n] @ (Vector(t) - Vector(h)))
    return out


def chain_of(skel, bone):
    c = []
    while bone: c.append(bone); bone = skel[bone][0]
    return c[::-1]


def tip_of(pose, finger):
    sk = RIGS["hand"]["skel"]
    return fk(sk, pose, chain_of(sk, finger + "_dist" if finger != "thumb" else "thumb_dist"))[
        finger + "_dist" if finger != "thumb" else "thumb_dist"][1]


def point_on(pose, finger, seg_name, t=1.0):
    sk = RIGS["hand"]["skel"]
    b = f"{finger}_{seg_name}"
    h, tl = fk(sk, pose, chain_of(sk, b))[b]
    return h + (tl - h) * t


def _climb(cost, lims, restarts=6, seed=1, step0=20.0):
    """Tiny derivative-free optimiser (coordinate descent with random restarts). cost(a) -> (value, payload)."""
    rnd = random.Random(seed)
    best = None
    for restart in range(restarts):
        a = [0.0] * len(lims) if restart == 0 else [rnd.uniform(lo, hi) * .5 for lo, hi in lims]
        a = [max(lo, min(hi, v)) for v, (lo, hi) in zip(a, lims)]
        c, p = cost(a)
        step = step0
        while step > .4:
            improved = False
            for i, (lo, hi) in enumerate(lims):
                for sgn in (step, -step):
                    b = list(a); b[i] = max(lo, min(hi, b[i] + sgn))
                    cc, pp = cost(b)
                    if cc < c - 1e-10: a, c, p, improved = b, cc, pp, True
            if not improved: step *= .6
        if best is None or c < best[0]: best = (c, p)
    return best


def thumb_to(base, target, d0=.011, seed=1):
    """Solve thumb rotations so its tip sits d0 away from `target` (Vector). Returns a pose-dict fragment."""
    sk = RIGS["hand"]["skel"]
    bones = ["thumb_mc", "thumb_prox", "thumb_dist"]
    chain = chain_of(sk, "thumb_dist")
    lim = {"thumb_mc": ((-30, 70), (-90, 40), (-50, 50)), "thumb_prox": ((-15, 75), (-25, 25), (-25, 25)), "thumb_dist": ((-15, 80), (-10, 10), (-10, 10))}
    lims = [lim[bones[i // 3]][i % 3] for i in range(9)]
    tgt = Vector(target)

    def cost(a):
        p = dict(base)
        for i, b in enumerate(bones): p[b] = tuple(a[3 * i:3 * i + 3])
        tip = fk(sk, p, chain)["thumb_dist"][1]
        return abs((tip - tgt).length - d0) + 1e-8 * sum(x * x for x in a), p
    c, p = _climb(cost, lims, 8, seed)
    print("thumb_to residual (mm):", round(c * 1000, 2))
    return {b: p[b] for b in bones}


def arm_to(side, wrist, hint=None, base=None, seed=1):
    """Two-bone arm solve: put the wrist (end of forearm) at a world point; `hint` pulls the elbow toward a point.
    Returns {upper_arm_X: (rx,ry,rz), forearm_X: (rx,0,0)}. `base` = pose the torso is in (so the shoulder is where it really is)."""
    sk = RIGS["body"]["skel"]
    ua, fa = "upper_arm_" + side, "forearm_" + side
    chain = chain_of(sk, fa)
    p0 = full_pose("body", base or {})
    tgt = Vector(wrist); hnt = Vector(hint) if hint else None
    lims = [(-175, 55), (-100, 70), (-100, 100), (-150, 0)]

    def cost(a):
        p = dict(p0); p[ua] = tuple(a[:3]); p[fa] = (a[3], 0, 0)
        out = fk(sk, p, chain)
        c = (out[fa][1] - tgt).length + (.35 * (out[fa][0] - hnt).length if hnt else 0) + 1e-8 * sum(x * x for x in a)
        return c, p
    c, p = _climb(cost, lims, 10, seed, 25.0)
    print(f"arm_to {side} residual (mm): {c*1000:.1f}")
    return {ua: p[ua], fa: p[fa]}


def arms_pose(Lw, Rw, Lh=None, Rh=None, base=None):
    d = arm_to("L", Lw, Lh, base); d.update(arm_to("R", Rw, Rh, base)); return d


def curl(f, a, b=None, c=None):
    """Finger flexion in degrees (toward the palm). b, c default to a natural ratio."""
    b = a * 1.1 if b is None else b
    c = a * .7 if c is None else c
    return {f + "_prox": (a, 0, 0), f + "_mid": (b, 0, 0), f + "_dist": (c, 0, 0)}


# =========================================================================== exercise registry
EXERCISES = {}


def define(ex_id, frames, poses, highlight, framing="full", chair=None, peak=None, shadow="auto", cam=None):
    """Register a body exercise.
    frames     loop length at 24 fps (72 = 3 s). Frame `frames` is keyed but not rendered, so the loop is seamless.
    poses      [(frame, partial_pose_dict), ...]; first and last pose must match. Bones missing stay at REST.
               Keys: bone -> (rx, ry, rz) degrees; 'X_B' = both sides mirrored; 'root' = hips offset in metres.
               Repeat a pose at two frames for a hold. planted_legs()/legW() give leg poses.
    highlight  groups tinted blue: arm_L arm_R leg_L leg_R head torso upper_torso (hand rig: thumb index middle ring pinky palm)
    framing    tall | full | seated | upper | hand ; cam = dict(az=, el=, target=, scale=) overrides
    chair      None or dict(x=, y=, rot=)"""
    return _register(ex_id, "body", frames, poses, highlight, framing, chair, peak, shadow, cam)


def define_hand(ex_id, frames, poses, highlight, peak=None, cam=None, rig_rot=(0, 0, 0)):
    """Register a hand exercise (close-up right hand + forearm stub; palm faces the camera by default).
    Pose keys: forearm/hand (wrist) and <finger>_prox/_mid/_dist, thumb_mc/_prox/_dist; curl() and thumb_to() help."""
    ex = _register(ex_id, "hand", frames, poses, highlight, "hand", None, peak, None, cam)
    ex["rig_rot"] = rig_rot
    return ex


def _register(ex_id, rig, frames, poses, highlight, framing, chair, peak, shadow, cam):
    full = [(f, full_pose(rig, d)) for f, d in poses]
    assert full[0][1] == full[-1][1], ex_id + ": first and last pose must be identical for a seamless loop"
    if shadow == "auto":
        shadow = {"tall": (.38, .26, 0, 0), "full": (.38, .26, 0, 0), "seated": (.62, .46, 0, .1)}.get(framing)
    EXERCISES[ex_id] = dict(rig=rig, frames=frames, poses=full, highlight=set(highlight), framing=framing, chair=chair,
                            peak=peak if peak is not None else full[len(full) // 2][0], shadow=shadow, cam=cam, rig_rot=(0, 0, 0))
    return EXERCISES[ex_id]


def build(ex_id, samples=48):
    ex = EXERCISES[ex_id]
    sc = reset()
    _prev.clear()
    CUR.update(RIGS[ex["rig"]])
    arm = build_rig(CUR["skel"])
    if STYLE == "parts": build_parts(arm, CUR["parts"], ex["highlight"])
    else: build_skin(arm, ex["rig"], ex["highlight"])
    arm.rotation_euler = [math.radians(a) for a in ex["rig_rot"]]
    if ex["chair"]: build_chair(**ex["chair"])
    build_stage(ex["shadow"])
    tgt = camera(ex["framing"], ex["cam"])
    lights(aim_at=tgt)
    render_settings(samples)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='POSE')
    for f, p in ex["poses"]: key_pose(arm, p, f)
    bpy.ops.object.mode_set(mode='OBJECT')
    ease_curves(arm)
    sc.frame_start, sc.frame_end = 0, ex["frames"] - 1
    return ex


def encode(ex_id, ex, fdir):
    mp4 = OUT_DIR + ex_id + ".mp4"
    for crf in (14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34):
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", fdir + "%04d.png", "-c:v", "libx264",
                        "-preset", "veryslow", "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", mp4], check=True)
        sz = os.path.getsize(mp4)
        print(f"{ex_id} crf {crf}: {sz/1024:.0f} KB")
        if sz < 245 * 1024 * (RES / 512) ** 1.5: break
    # Blender's python has no PIL: use the system python for the webp poster
    subprocess.run(["/usr/bin/python3", "-c", "import sys;from PIL import Image;Image.open(sys.argv[1]).convert('RGB').save(sys.argv[2],quality=82)",
                    fdir + "%04d.png" % ex["peak"], OUT_DIR + ex_id + ".webp"], check=True)


def main():
    import time
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    mode, ids = argv[0], argv[1:]
    sc = None
    if mode == "still":
        ex = build(ids[0]); fr = int(ids[1]) if len(ids) > 1 else ex["peak"]
        bpy.context.scene.frame_set(fr)
        bpy.context.scene.render.filepath = WORK + f"still_{ids[0]}_{fr}.png"
        bpy.ops.render.render(write_still=True)
        return
    if mode == "quick":
        os.makedirs(WORK + "quick/", exist_ok=True)
        for ex_id in ids:
            ex = build(ex_id, 12)
            n = ex["frames"]
            for i, fr in enumerate((int(n * .12), int(n * .3), ex["peak"], int(n * .72))):
                bpy.context.scene.frame_set(fr)
                bpy.context.scene.render.filepath = WORK + f"quick/{ex_id}_{i}.png"
                bpy.ops.render.render(write_still=True)
        return
    if mode == "encode":
        for ex_id in ids:
            build(ex_id); encode(ex_id, EXERCISES[ex_id], WORK + "frames/" + ex_id + "/")
        return
    for ex_id in ids:
        ex = build(ex_id)
        fdir = WORK + "frames/" + ex_id + "/"; os.makedirs(fdir, exist_ok=True)
        t0 = time.time()
        sc = bpy.context.scene
        for f in range(ex["frames"]):
            sc.frame_set(f); sc.render.filepath = fdir + "%04d.png" % f
            bpy.ops.render.render(write_still=True)
        print(f"{ex_id} render time {time.time()-t0:.1f}s")
        encode(ex_id, ex, fdir)


# =========================================================================== exercise library: BODY
# Angle cheat sheet: arms hang down, so negative rx = forward flexion, ry<0 on the L arm = abduction (out to +X),
# upright bones: +rx forward lean, +ry lean toward +X, +rz turn toward +X.
F96 = 96

# crossed arms on the chest (used for every seated exercise so hands never hover)
CROSS = arms_pose((-.07, -.20, 1.25), (.05, -.235, 1.205), (.21, -.15, 1.10), (-.21, -.17, 1.08))  # forearms clear of the chest
HOLD = None


_CL_LO = arms_pose((.08, -.23, .98), (-.08, -.23, .98), (.22, -.04, 1.15), (-.22, -.04, 1.15))
_CL_MID = arms_pose((.08, -.52, 1.44), (-.08, -.52, 1.44), (.2, -.26, 1.45), (-.2, -.26, 1.45))
_CL_TOP = arms_pose((.08, -.03, 1.97), (-.08, -.03, 1.97), (.15, -.01, 1.7), (-.15, -.01, 1.7))
_CL_TOP.update({"clavicle_B": (0, -9, 0), "spine": (-3, 0, 0), "chest": (-2, 0, 0), "head": (2, 0, 0)})
_CL_CHEST = arms_pose((.08, -.18, 1.26), (-.08, -.18, 1.26), (.22, -.07, 1.12), (-.22, -.07, 1.12))


# ---- G01 single leg stand
_g01 = {"root": (-.03, 0, 0), "thigh_R": (0, -2.2, 0), "foot_R": (0, 2.2, 0), "spine": (0, -3, 0),
        "upper_arm_B": (0, -16, 0), **legW("L", -48, 15, 8), "thigh_L": (-48, -20, 0)}
define("G01", 96, [(0, {}), (20, _g01), (68, _g01), (90, {}), (96, {})], {"leg_L", "leg_R"}, framing="full", peak=44)

# ---- G02 assisted shoulder flexion (clasped hands, both arms up)
define("G02", 108, [(0, _CL_LO), (16, _CL_MID), (32, _CL_TOP), (62, _CL_TOP), (78, _CL_MID), (98, _CL_LO), (108, _CL_LO)], {"arm_L", "arm_R"},
       framing="tall", peak=46)

# ---- G03 shoulder flexion (model-left arm = viewer's right)
_up = {"upper_arm_L": (-172, 0, 0), "forearm_L": (0, 0, 0), "clavicle_L": (0, -9, 0),
       "spine": (-3, 0, 0), "chest": (-2, 0, 0), "head": (2, 0, 0)}
define("G03", 96, [(0, {}), (28, _up), (54, _up), (90, {}), (96, {})], {"arm_L"}, framing="tall", peak=40)

# ---- G04 bilateral shoulder abduction to T
_t = {"upper_arm_B": (0, -90, 0), "forearm_B": (0, 0, 0), "clavicle_B": (0, -5, 0)}
define("G04", 96, [(0, {}), (28, _t), (56, _t), (88, {}), (96, {})], {"arm_L", "arm_R"}, framing="full", peak=42)

# ---- G05 assisted elbow extension: clasped at chest, push forward to straight
define("G05", 96, [(0, _CL_CHEST), (30, _CL_MID), (50, _CL_MID), (80, _CL_CHEST), (96, _CL_CHEST)], {"arm_L", "arm_R"}, framing="full", peak=40)

# ---- G06 elbow extension (one arm): bent 90 -> straight, in front
_g06a = {"upper_arm_L": (-85, 0, 0), "forearm_L": (-92, 0, 0)}
_g06b = {"upper_arm_L": (-85, 0, 0), "forearm_L": (0, 0, 0)}
define("G06", 96, [(0, {}), (16, _g06a), (38, _g06b), (52, _g06b), (68, _g06a), (86, {}), (96, {})], {"arm_L"}, framing="full", peak=44)

# ---- G07 shoulder external rotation: elbows pinned at sides bent 90, forearms rotate outward
_g07a = {"upper_arm_B": (0, -2, 0), "forearm_B": (-90, 0, 0)}
_g07b = {"upper_arm_B": (0, -2, 50), "forearm_B": (-90, 0, 0)}
define("G07", 96, [(0, _g07a), (30, _g07b), (50, _g07b), (82, _g07a), (96, _g07a)], {"arm_L", "arm_R"}, framing="full", peak=40)

# ---- seated base for chair exercises
SIT_Y, SIT_Z = .32, .505
CH = dict(x=0, y=.34, rot=0)


def seat(lean=0, lat=0, rot=0, headx=None, arms=CROSS):
    d = planted_legs(SIT_Y, SIT_Z, lean * .65)
    d.update({"spine": (lean * .35, lat * .55, rot * .4), "chest": (0, lat * .45, rot * .45),
              "neck": (0, 0, rot * .12), "head": (-lean * .45 if headx is None else headx, -lat * .35, rot * .15)})
    d.update(arms)
    return d


# ---- G08 seated weight shift
define("G08", 96, [(0, seat()), (20, seat(lat=34)), (32, seat(lat=34)), (48, seat()), (68, seat(lat=-34)), (80, seat(lat=-34)), (96, seat())],
       {"torso", "upper_torso"}, framing="seated", chair=CH, peak=26)

# ---- G09 trunk flexion
define("G09", 96, [(0, seat()), (30, seat(lean=42)), (50, seat(lean=42)), (84, seat()), (96, seat())],
       {"torso", "upper_torso"}, framing="seated", chair=CH, peak=40)

# ---- G10 bilateral shoulder flexion to 90, hold
_g10 = {"upper_arm_B": (-90, 0, 0), "forearm_B": (0, 0, 0)}
define("G10", 96, [(0, {}), (28, _g10), (62, _g10), (90, {}), (96, {})], {"arm_L", "arm_R"}, framing="full", peak=44)

# ---- G11 one arm abduction to shoulder height
_g11 = {"upper_arm_L": (0, -90, 0), "forearm_L": (0, 0, 0), "clavicle_L": (0, -5, 0)}
define("G11", 96, [(0, {}), (28, _g11), (50, _g11), (84, {}), (96, {})], {"arm_L"}, framing="full", peak=38)


# ---- G12 standing weight shift
def wshift(dx):
    th = math.degrees(math.asin(dx / .83))
    return {"root": (dx, 0, -.83 * (1 - math.cos(math.radians(th)))), "thigh_L": (0, th, 0), "thigh_R": (0, th, 0),
            "foot_L": (0, -th, 0), "foot_R": (0, -th, 0), "spine": (0, -th * 1.3, 0), "upper_arm_B": (0, -4, 0)}


define("G12", 96, [(0, {}), (22, wshift(.16)), (36, wshift(.16)), (52, {}), (72, wshift(-.16)), (86, wshift(-.16)), (96, {})],
       {"leg_L", "leg_R"}, framing="full", peak=28, cam=dict(az=0))  # front view: the sideways shift reads best


# ---- G13 gait pre-training: march in place, 2 steps each side (L R L R)
def march(side):
    o = "R" if side == "L" else "L"
    d = {**legW(side, -78, 12, 25), "upper_arm_" + o: (-26, 0, 0), "upper_arm_" + side: (16, 0, 0),
         "forearm_B": (-80, 0, 0), "spine": (-1, 0, 0)}
    return d


_mn = {"forearm_B": (-80, 0, 0)}
define("G13", 96, [(0, _mn), (11, march("L")), (24, _mn), (35, march("R")), (48, _mn), (59, march("L")), (72, _mn), (83, march("R")), (96, _mn)],
       {"leg_L", "leg_R"}, framing="full", peak=11)


# ---- G14 sit to stand (arms crossed)
def _sts(hy, hz, lean):
    d = planted_legs(hy, hz, lean * .65)
    d.update({"spine": (lean * .35, 0, 0), "head": (-lean * .5, 0, 0)})
    d.update(CROSS)
    return d


_sit = _sts(.32, .505, 0)
_stand = _sts(0.0, .905, 0)
define("G14", 96, [(0, _sit), (14, _sts(.30, .52, 30)), (32, _sts(.17, .74, 32)), (48, _stand), (62, _stand),
                   (74, _sts(.20, .70, 30)), (88, _sts(.31, .515, 24)), (96, _sit)],
       {"leg_L", "leg_R"}, framing="full", chair=CH, peak=52)


# ---- G15 seated knee extension, one leg then the other
def kext(side, amt):
    """amt 0 = seated, 1 = knee straight in front."""
    tw = -88 - 4 * amt
    sw = 0 - 88 * amt
    fw = 0 - 14 * amt
    return legW(side, tw, sw, fw)


def sitk(l=0, r=0):
    d = seat(); d.update(kext("L", l)); d.update(kext("R", r)); return d


define("G15", 96, [(0, sitk()), (18, sitk(l=1)), (32, sitk(l=1)), (46, sitk()), (60, sitk(r=1)), (74, sitk(r=1)), (88, sitk()), (96, sitk())],
       {"leg_L", "leg_R"}, framing="seated", chair=CH, peak=26)


# ---- G16 standing heel raises, left hand on a chair back beside the model
def heel(h):
    base = {"root": (0, -.079 * h, .058 * h), "foot_B": (40 * h, 0, 0)}
    base.update(arm_to("L", (.37, -.14, 1.0), (.3, .0, 1.1), base))
    return base


define("G16", 96, [(0, heel(0)), (26, heel(1)), (50, heel(1)), (82, heel(0)), (96, heel(0))], {"leg_L", "leg_R"}, framing="full",
       chair=dict(x=.55, y=0, rot=90, back_h=.56), peak=38, cam=dict(target=(.22, .05, .9), scale=2.05),
       shadow=(.7, .3, .22, 0))


# ---- G17 neck side bend (standing, upper-body framing); ry tilts the top toward +X (viewer's right)
def _tilt(a): return {"neck": (0, a * .4, 0), "head": (0, a * .6, 0)}


define("G17", 96, [(0, _tilt(0)), (20, _tilt(24)), (32, _tilt(24)), (48, _tilt(0)), (66, _tilt(-24)), (78, _tilt(-24)), (96, _tilt(0))],
       {"head"}, framing="upper", peak=26)


# ---- G18 neck rotation
def _turn(a): return {"neck": (0, 0, a * .4), "head": (0, 0, a * .6)}


define("G18", 96, [(0, _turn(0)), (20, _turn(62)), (34, _turn(62)), (48, _turn(0)), (66, _turn(-62)), (80, _turn(-62)), (96, _turn(0))],
       {"head"}, framing="upper", peak=26, cam=dict(az=0, el=12))


# ---- G19 chin tuck (side-ish camera)
def _tuck(a): return {"neck": (-a, 0, 0), "head": (a * 1.0, 0, 0)}


define("G19", 96, [(0, _tuck(0)), (24, _tuck(20)), (56, _tuck(20)), (86, _tuck(0)), (96, _tuck(0))], {"head"}, framing="upper",
       peak=40, cam=dict(az=75))

# ---- G20 seated trunk rotation (hips still)
define("G20", 96, [(0, seat()), (22, seat(rot=50)), (34, seat(rot=50)), (50, seat()), (70, seat(rot=-50)), (82, seat(rot=-50)), (96, seat())],
       {"torso", "upper_torso"}, framing="seated", chair=CH, peak=28)


# ---- G21 standing side bend, hand slides down the leg
def sbend(a):
    arms = {"upper_arm_L": (0, -a * .9 - 5, 0), "upper_arm_R": (0, -a * .9 + 5, 0)}
    return {"spine": (0, a * .6, 0), "chest": (0, a * .4, 0), "head": (0, -a * .4, 0), **arms}


define("G21", 96, [(0, sbend(0)), (22, sbend(26)), (34, sbend(26)), (50, sbend(0)), (70, sbend(-26)), (82, sbend(-26)), (96, sbend(0))],
       {"torso", "upper_torso"}, framing="full", peak=28)

# ---- G22 seated back extension
define("G22", 96, [(0, seat()), (30, seat(lean=-20, headx=-6)), (52, seat(lean=-20, headx=-6)), (84, seat()), (96, seat())],
       {"torso", "upper_torso"}, framing="seated", chair=CH, peak=40)

# ---- G23 shoulder blade squeeze (camera behind 3/4)
_sq0 = {"upper_arm_B": (-6, -3, 0), "forearm_B": (-90, 0, 0)}
_sq1 = {"upper_arm_B": (38, -8, 0), "forearm_B": (-90, 0, 0), "clavicle_B": (0, 0, 18), "chest": (-8, 0, 0), "spine": (-3, 0, 0)}
define("G23", 96, [(0, _sq0), (26, _sq1), (60, _sq1), (88, _sq0), (96, _sq0)], {"upper_torso"}, framing="upper", peak=40,
       cam=dict(az=125))  # side-back: elbows travel back and the chest opens


# =========================================================================== exercise library: HAND
H0 = rest_pose("hand")
_flat = {}
FNG = [f[0] for f in FINGERS]


def hp(*ds):
    out = {}
    for d in ds: out.update(d)
    return out


def allcurl(a, b, c, fingers=FNG):
    return hp(*[curl(f, a, b, c) for f in fingers])


def with_thumb(base, finger_or_point, d0=.011, seed=1):
    pose = full_pose("hand", base)
    tgt = finger_or_point if isinstance(finger_or_point, Vector) else tip_of(pose, finger_or_point)
    out = dict(base); out.update(thumb_to(pose, tgt, d0, seed)); return out


# F01 thumb-to-index pinch
_f01_i = curl("index", 36, 42, 26)
_f01 = with_thumb(_f01_i, "index", .015)
define_hand("F01", 96, [(0, {}), (28, _f01), (56, _f01), (88, {}), (96, {})], {"thumb", "index"}, peak=42, cam=dict(az=28, el=12))

# F02 hand grasp: fist, then open fully
_fist = allcurl(88, 100, 62)
_fist_t = {**_fist, **thumb_to(full_pose("hand", _fist), point_on(full_pose("hand", _fist), "index", "mid", .4) + Vector((0, -.02, 0)), .015, 3)}
define_hand("F02", 96, [(0, {}), (28, _fist_t), (54, _fist_t), (84, {}), (96, {})], {"thumb", "index", "middle", "ring", "pinky"}, peak=42)

# F03 sequential tapping: thumb to index, middle, ring, pinky, lifting between
_relax = hp(curl("index", 24, 30, 18), curl("middle", 28, 34, 20), curl("ring", 28, 34, 20), curl("pinky", 28, 34, 20))
# the tapped finger bends to meet the thumb so each tap reads as a different finger
_taps = [with_thumb({**_relax, **curl(f, 48, 52, 30)}, f, .015, 5) for f in ("index", "middle", "ring", "pinky")]
_f03 = [(0, {})]
for i, tp in enumerate(_taps):
    t0 = 6 + i * 22
    _f03 += [(t0, tp), (t0 + 7, tp), (t0 + 15, {**_relax, "thumb_mc": (0, 34, 0)})]
_f03 += [(96, {})]
define_hand("F03", 96, _f03, {"thumb", "index", "middle", "ring", "pinky"}, peak=12, cam=dict(az=28, el=12))

# F04 thumb opposition: thumb tip to base of pinky
_f04b = hp(curl("pinky", 14, 10, 6), curl("ring", 8, 8, 6))
_f04 = {**_f04b, **thumb_to(full_pose("hand", _f04b), Vector((-.026, -.016, KN - .006)), .012, 7)}
define_hand("F04", 96, [(0, {}), (30, _f04), (56, _f04), (86, {}), (96, {})], {"thumb"}, peak=42, cam=dict(az=22, el=10))

# F05 wrist extension / flexion (side view)
ALLH = {"palm", "thumb", "index", "middle", "ring", "pinky"}
define_hand("F05", 96, [(0, {}), (22, {"hand": (-55, 0, 0)}), (34, {"hand": (-55, 0, 0)}), (52, {}), (72, {"hand": (55, 0, 0)}), (84, {"hand": (55, 0, 0)}), (96, {})],
            ALLH, peak=26, cam=dict(az=80, el=6, scale=.36, target=(0, 0, .06)))

# F06 finger spread
_tog = {"index_prox": (0, -2, 0), "middle_prox": (0, 0, 0), "ring_prox": (0, 2, 0), "pinky_prox": (0, 6, 0)}
_spr = {"index_prox": (0, 15, 0), "middle_prox": (0, 4, 0), "ring_prox": (0, -7, 0), "pinky_prox": (0, -19, 0),
        "thumb_mc": (0, 12, 0), "thumb_prox": (0, 6, 0)}
define_hand("F06", 96, [(0, _tog), (30, _spr), (54, _spr), (84, _tog), (96, _tog)], {"index", "middle", "ring", "pinky", "thumb"}, peak=40)

# F07 wrist radial / ulnar deviation (palm facing camera, fingers up)
define_hand("F07", 96, [(0, {}), (22, {"hand": (0, 22, 0)}), (34, {"hand": (0, 22, 0)}), (52, {}), (72, {"hand": (0, -28, 0)}),
                         (84, {"hand": (0, -28, 0)}), (96, {})], ALLH, peak=26, cam=dict(az=15, el=10))


# F08 individual finger lifts: hand flat, palm down
def lift(f):
    return {f + "_prox": (-64, 0, 0), f + "_mid": (0, 0, 0)}


_f08 = [(0, {})]
for i, f in enumerate(("index", "middle", "ring", "pinky")):
    t0 = 4 + i * 22
    _f08 += [(t0 + 8, lift(f)), (t0 + 14, lift(f)), (t0 + 22, {})]
_f08[-1] = (96, {})
_f08 = [x for x in _f08 if x[0] <= 96]
define_hand("F08", 96, _f08, {"index", "middle", "ring", "pinky"}, peak=20, rig_rot=(90, 0, 90),
            cam=dict(az=-25, el=26, target=(.10, -.02, .03), scale=.34))

# F09 finger curls (toward the palm), extend
_f09 = allcurl(70, 82, 52)
define_hand("F09", 96, [(0, {}), (30, _f09), (50, _f09), (84, {}), (96, {})], {"index", "middle", "ring", "pinky"}, peak=40, cam=dict(az=65, el=8))

# F11 pinky to thumb touch
_f11b = curl("pinky", 62, 52, 30)
_f11 = {**_f11b, **thumb_to(full_pose("hand", _f11b), tip_of(full_pose("hand", _f11b), "pinky"), .015, 11)}
define_hand("F11", 96, [(0, {}), (30, _f11), (56, _f11), (86, {}), (96, {})], {"thumb", "pinky"}, peak=44, cam=dict(az=28, el=10))

# F13 hook fist: bend only the middle and end joints, knuckles straight
_f13 = hp(*[curl(f, 0, 88, 58) for f in FNG])
define_hand("F13", 96, [(0, {}), (30, _f13), (52, _f13), (84, {}), (96, {})], {"index", "middle", "ring", "pinky"}, peak=40, cam=dict(az=65, el=8))

if __name__ == "__main__":
    main()
