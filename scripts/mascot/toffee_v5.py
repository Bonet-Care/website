"""Toffee v5: one fused streamlined body (metaballs). Usage:
blender -b -P toffee_v5.py -- POSE [OUT.png] [RES] [T]
POSE: idle wave cheer point think encourage sleep head. T = idle phase 0..1.
Default output dir: ./v5-out (next to this script)."""
import bpy, sys, math, json, os
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.environ.get("MASCOT_OUT", os.path.join(HERE, "v5-out"))
TMP = os.path.join(OUTDIR, "_tmp")
os.makedirs(TMP, exist_ok=True)
args = sys.argv[sys.argv.index("--") + 1:]
POSE = args[0]
OUT = args[1] if len(args) > 1 else os.path.join(TMP, "%s.png" % POSE)
RES = int(args[2]) if len(args) > 2 else 1024
T = float(args[3]) if len(args) > 3 else 0.0
SAMPLES = 40
OUTFIT = os.environ.get("OUTFIT", "")   # optional accessory layer: bandana bowtie cap glasses scarf chef cape crown
LIFT = [0.0]

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
V = Vector
R2 = math.radians

def lin(h):
    h = h.lstrip('#')
    return tuple((int(h[i:i+2], 16) / 255) ** 2.2 for i in (0, 2, 4)) + (1,)

def mat(name, hexc, rough=0.55, sss=0.15, sheen=0.5, coat=0.0, emit=0.0, spec=0.4):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = lin(hexc)
    b.inputs["Roughness"].default_value = rough
    for k, v in (("Subsurface Weight", sss), ("Sheen Weight", sheen), ("Coat Weight", coat),
                 ("Specular IOR Level", spec)):
        if k in b.inputs: b.inputs[k].default_value = v
    if "Subsurface Radius" in b.inputs:
        b.inputs["Subsurface Radius"].default_value = (0.5, 0.2, 0.08)
    if "Sheen Tint" in b.inputs:
        b.inputs["Sheen Tint"].default_value = (1.0, 0.8, 0.55, 1)
    if emit:
        b.inputs["Emission Color"].default_value = lin(hexc)
        b.inputs["Emission Strength"].default_value = emit
    return m

ORANGE = mat("orange", "#EE8F2E", 0.6, 0.2, 0.6)
ORANGE2 = mat("orange2", "#DE7A1E", 0.6, 0.2, 0.6)
TAN = mat("tan", "#F6AE5C", 0.6, 0.2, 0.6)
WHITE = mat("white", "#FFF9F0", 0.6, 0.15, 0.5)
PINKIN = mat("pinkin", "#FFB9A6", 0.6, 0.25, 0.2)
NOSE = mat("nose", "#1A1210", 0.15, 0, 0, coat=1.0)
EYE = mat("eye", "#1E0E06", 0.08, 0, 0, coat=1.0)
IRIS = mat("iris", "#8A4A1C", 0.15, 0, 0, coat=0.6)
LIGHT = mat("light", "#FFFFFF", 1, 0, 0, emit=4.0)
MOUTH = mat("mouth", "#4A1A14", 0.5, 0, 0)
TONGUE = mat("tongue", "#FF7A90", 0.35, 0.3, 0, coat=0.4)
TONGUE2 = mat("tongue2", "#FFA3B2", 0.3, 0.1, 0, coat=0.5)
TGRV = mat("tgrv", "#D8566F", 0.4, 0, 0)
LINE = mat("line", "#4A2410", 0.4, 0, 0)
BROW = mat("brow", "#9A4E16", 0.5, 0, 0)
BLUSH = mat("blush", "#FF9A92", 0.8, 0, 0)

PAR = [None]

def smooth(o):
    for p in o.data.polygons: p.use_smooth = True

def setpar(o, p):
    bpy.context.view_layer.update()
    o.parent = p
    o.matrix_parent_inverse = p.matrix_world.inverted()

def ell(name, loc, rad, m, rot=(0, 0, 0), parent=None, seg=48, rings=24):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=seg, ring_count=rings, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = rad
    o.rotation_euler = rot
    smooth(o)
    o.data.materials.append(m)
    p = parent or PAR[0]
    if p: setpar(o, p)
    return o

def pivot(name, loc, parent=None):
    e = bpy.data.objects.new(name, None)
    sc.collection.objects.link(e)
    e.location = loc
    bpy.context.view_layer.update()
    p = parent or PAR[0]
    if p: setpar(e, p)
    return e

def curve(name, pts, bevel, m, parent=None):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = bevel
    cu.bevel_resolution = 4
    cu.fill_mode = 'FULL'
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts): sp.points[i].co = (p[0], p[1], p[2], 1)
    o = bpy.data.objects.new(name, cu)
    sc.collection.objects.link(o)
    cu.materials.append(m)
    for end in (pts[0], pts[-1]):
        ell(name + "cap", end, (bevel,) * 3, m, seg=12, rings=8, parent=parent)
    if parent or PAR[0]: setpar(o, parent or PAR[0])
    return o

def ear_mesh(name, loc, rx, ry, h, m, parent, tipw=0.4, fold=0.0, zf=0.55):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=48, ring_count=32, location=(0, 0, 0))
    o = bpy.context.object
    o.name = name
    for v in o.data.vertices:
        z = v.co.z
        t = (z + 1) / 2
        v.co.x = v.co.x * rx * (1 - (1 - tipw) * (t ** 1.3))
        v.co.y = v.co.y * ry * (1 - 0.45 * t)
        v.co.z = (z + 1) * h / 2
        if fold:   # floppy tip: bend forward/down above the fold height
            zz = v.co.z / h
            u = min(max((zz - (zf - 0.12)) / 0.3, 0.0), 1.0); u = u * u * (3 - 2 * u)
            dz = max(v.co.z - zf * h, 0.0)
            a = R2(fold) * u
            if dz > 0:
                y0 = v.co.y
                v.co.y = y0 - math.sin(a) * dz
                v.co.z = zf * h + math.cos(a) * dz
    o.location = loc
    smooth(o)
    o.data.materials.append(m)
    setpar(o, parent)
    return o

# ================= v3: ONE fused fur surface (metaballs) =================
import numpy as np
from mathutils import Matrix, Euler
from mathutils.bvhtree import BVHTree

RESMB = 0.022
FURK = 1 / 0.575          # metaball size per unit surface radius (radius=1, stiffness 2)
BL = []                    # blobs: (centre, radii, rot3x3, stiffness)
ZN = []                    # colour zones: (centre, radii, rot3x3, rgb, inner, outer)
HS = {"hp": V((0, 0, 0)), "R": Matrix.Identity(3)}
I3 = Matrix.Identity(3)
C_OR = lin("#EE8F2E")[:3]; C_WH = lin("#FFF9F0")[:3]; C_TAN = lin("#F6AE5C")[:3]; C_DK = lin("#D9741A")[:3]

def eu(r):  # degrees tuple -> 3x3
    return Euler(tuple(R2(a) for a in r), 'XYZ').to_matrix()

SWAY = {"M": Matrix.Identity(3), "pv": V((0, 0.3, 0))}   # whole-body roll (wiggle clip); identity otherwise
def sw(c):
    return SWAY["pv"] + SWAY["M"] @ (V(c) - SWAY["pv"])

def blob(c, r, rm=None, st=2.0, neg=False):
    BL.append((sw(c), V(r), SWAY["M"] @ (rm if rm is not None else I3), st, neg))

def zone(c, r, rm=None, col=C_WH, a=0.7, b=1.12):
    ZN.append((sw(c), V(r), SWAY["M"] @ (rm if rm is not None else I3), col, a, b))

def set_head(hp, hrot):
    HS["hp"] = V(hp); HS["R"] = eu(hrot)

def hl(l):
    return HS["hp"] + HS["R"] @ V(l)

def hblob(l, r, rot=(0, 0, 0), st=2.0, neg=False):
    blob(hl(l), r, HS["R"] @ eu(rot), st, neg)

def hzone(l, r, col=C_WH, a=0.7, b=1.12):
    zone(hl(l), r, HS["R"], col, a, b)

MZ = (0.0, -0.66, -0.26)
MR = (0.38, 0.34, 0.27)
HX, HY, HZ = 0.98, 0.82, 0.8

def ear_blobs(earL, earR):
    """only a short fused stub at each ear base; the upper ear is a clean separate mesh embedded in it."""
    for s, e in ((-1, earL), (1, earR)):
        oa, fa = e[0], e[1]
        M = eu((fa, s * oa, 0))
        base = V((s * 0.56, 0.1, 0.5))
        for t, w, th in ((-0.06, 0.27, 0.15),):
            p = base + M @ V((0, 0.06, t)) - V((s * 0.04, 0, 0.05))
            hblob(tuple(p), (w, th, 0.08), rot=tuple(math.degrees(a) for a in M.to_euler('XYZ')))

C_PINK = lin("#FFB9A6")[:3]

def head_blobs(squash=1.0, earL=(14, 0), earR=(14, 0), mouth_open=0.0):
    hblob((0, 0, 0), (HX, HY, HZ), st=2.0)
    for s in (-1, 1):
        hblob((s * 0.5, -0.3, -0.36), (0.26, 0.3, 0.24), (0, 0, s * 28))     # fluffy cheeks
    hblob(MZ, MR)                                                            # muzzle
    ear_blobs(earL, earR)
    if mouth_open > 0:
        hblob((0, -0.88, -0.45), (0.23, 0.12, 0.1 * mouth_open + 0.05), st=2.0, neg=True)
    # white zones in head frame
    hzone((0, -0.66, -0.28), (0.56, 0.62, 0.4), a=0.7, b=1.12)
    hzone((0, -0.72, 0.28), (0.105, 0.34, 0.66), a=0.55, b=1.0)
    hzone((0, -0.65, 0.62), (0.075, 0.3, 0.24), a=0.5, b=1.0)

def limb(root, rot, zs, spec, white=None):
    """spec: list of (offset, radii). offset/radii z are stretched by zs, all rotated about root."""
    M = eu(rot)
    for off, r in spec:
        o = V((off[0], off[1], off[2] * zs))
        blob(V(root) + M @ o, (r[0], r[1], r[2] * (zs ** 0.5)), M)
    if white:
        off, r = white
        zone(V(root) + M @ V((off[0], off[1], off[2] * zs)), r, M, C_WH, 0.55, 1.0)

ARM_LEN = 0.68   # front-limb length factor (founder: arms too long); applies to every pose

def lerp_arm(s, rot, w, lift, bob):
    """arm that blends from hanging (w=0) to raised mitten (w=1) with no shape pop (animation clips)."""
    hang = [((0, 0.0, 0.0), (0.26, 0.26, 0.3)), ((0, -0.03, -0.3), (0.19, 0.2, 0.3)),
            ((0, -0.07, -0.55), (0.16, 0.18, 0.24)), ((0, -0.13, -0.82), (0.19, 0.28, 0.13))]
    up = [((0, 0.0, 0.0), (0.26, 0.26, 0.28)), ((0, -0.02, -0.3), (0.19, 0.19, 0.3)),
          ((0, -0.04, -0.58), (0.16, 0.17, 0.24)), ((0, -0.06, -0.86), (0.22, 0.23, 0.2))]
    L = lambda a, b: tuple(x + (y - x) * w for x, y in zip(a, b))
    zs = ARM_LEN * (1 + 0.5 * w)
    rh = (s * 0.44, -0.52, 0.94 + lift + bob * 0.5 - 0.82 * (1 - ARM_LEN))
    ru = (s * 0.5, -0.52, 0.94 + lift + bob * 0.5)
    root = L(rh, ru)
    spec = [(L(a[0], b[0]), L(a[1], b[1])) for a, b in zip(hang, up)]
    limb(root, rot, zs, spec, white=(L((0, -0.1, -0.78), (0, -0.06, -0.84)), L((0.36, 0.5, 0.30), (0.34, 0.34, 0.36))))
    if w < 0.5:
        zone((s * 0.22, -0.7, 0.62 + lift), (0.07, 0.22, 0.4), None, C_DK, 0.2, 1.0)

def front_leg(s, rot, zs, lift, bob):
    zs = zs * ARM_LEN
    raised = any(rot)
    root = (s * (0.5 if raised else 0.44), -0.52, 0.94 + lift + bob * 0.5)
    if not raised:   # shortened hanging arm: drop the shoulder so the paw still reaches the floor
        root = (root[0], root[1], root[2] - 0.82 * (1 - ARM_LEN) * (1 - 0.0))
    if raised:
        spec = [((0, 0.0, 0.0), (0.26, 0.26, 0.28)),
                ((0, -0.02, -0.3), (0.19, 0.19, 0.3)),
                ((0, -0.04, -0.58), (0.16, 0.17, 0.24)),
                ((0, -0.06, -0.86), (0.22, 0.23, 0.2))]            # round mitten
        limb(root, rot, zs, spec, white=((0, -0.06, -0.84), (0.34, 0.34, 0.36)))
    else:
        spec = [((0, 0.0, 0.0), (0.26, 0.26, 0.3)),
                ((0, -0.03, -0.3), (0.19, 0.2, 0.3)),
                ((0, -0.07, -0.55), (0.16, 0.18, 0.24)),
                ((0, -0.13, -0.82), (0.19, 0.28, 0.13))]
        limb(root, rot, zs, spec, white=((0, -0.1, -0.78), (0.36, 0.5, 0.30)))
        # soft shading crease where leg meets chest
        zone((s * 0.22, -0.7, 0.62 + lift), (0.07, 0.22, 0.4), None, C_DK, 0.2, 1.0)

def torso_sit(rig):
    bob = rig.get("bob", 0.0); lift = rig.get("lift", 0.0)
    br = 1 + 0.5 * bob   # breathing swell
    z = lift
    tr = eu((22, 0, 0))
    blob((0, 0.4, 0.9 + z), (0.7 * br, 0.74, 0.7), tr)                 # torso
    blob((0, -0.22, 1.0 + z + bob * 0.5), (0.52 * br, 0.44, 0.52), tr)   # chest
    blob((0, -0.12, 1.42 + z + bob * 0.8), (0.44, 0.4, 0.4))               # neck
    blob((0, 0.78, 0.46 + z), (0.62, 0.56, 0.46))                           # rump
    for s in (-1, 1):
        blob((s * 0.5, 0.42, 0.4 + z), (0.3, 0.5, 0.37))                   # haunch
        blob((s * 0.46, 0.12, 0.21 + z * 0.3), (0.22, 0.3, 0.2))           # thigh to foot
        blob((s * 0.44, -0.1, 0.13 + z * 0.3), (0.2, 0.33, 0.13))          # hind foot
        zone((s * 0.44, -0.16, 0.12 + z * 0.3), (0.34, 0.46, 0.22), None, C_WH, 0.55, 1.0)
    # white bib + belly
    zone((0, -0.7, 1.0 + z), (0.26, 0.4, 0.5), None, C_WH, 0.5, 1.0)
    zone((0, -0.5, 0.55 + z), (0.36, 0.42, 0.34), None, C_WH, 0.55, 1.0)
    # tail nub
    pv = V((0, 1.1, 0.6 + z))
    M = Euler((0, 0, R2(rig.get("wag", 0))), 'XYZ').to_matrix()
    c = pv + M @ V((0, 0.3, 0.06))
    blob(c, (0.17, 0.19, 0.16), M)
    zone(c, (0.24, 0.26, 0.22), M, C_TAN, 0.5, 1.0)
    for s, key in ((-1, "legL"), (1, "legR")):
        if ("blend" + key) in rig:
            lerp_arm(s, rig[key], rig["blend" + key], z, bob); continue
        front_leg(s, rig.get(key, (0, 0, 0)), rig.get("legscale", 1.0) if rig.get(key) else 1.0, z, bob)

def sleep_blobs(b=0.0):
    blob((0, 0.55, 0.4 + 0.02 * b), (0.74 + 0.02 * b, 1.0, 0.42 + 0.05 * b))
    blob((0, 1.2, 0.4), (0.6, 0.5, 0.4))
    blob((0.45, 0.8, 0.28), (0.3, 0.5, 0.28))
    blob((0, 0.05, 0.42 + 0.02 * b), (0.55 + 0.02 * b, 0.5, 0.4 + 0.05 * b))
    blob((0, -0.3, 0.55 + 0.03 * b), (0.42, 0.4, 0.34 + 0.03 * b))
    for x in (-0.36, 0.36):
        blob((x, -0.5, 0.2), (0.17, 0.5, 0.17))
        blob((x, -1.0, 0.16), (0.2, 0.22, 0.16))
        zone((x, -1.0, 0.14), (0.3, 0.34, 0.24), None, C_WH, 0.55, 1.0)
    blob((0.5, 0.25, 0.11), (0.2, 0.32, 0.12))
    zone((0.5, 0.2, 0.1), (0.34, 0.46, 0.22), None, C_WH, 0.55, 1.0)
    zone((0, -0.3, 0.3), (0.34, 0.42, 0.36), None, C_WH, 0.5, 1.0)
    c = V((0, 1.78, 0.5))
    blob(c, (0.15, 0.17, 0.14)); zone(c, (0.21, 0.23, 0.2), None, C_TAN, 0.5, 1.0)

FUR = mat("fur", "#FFFFFF", 0.6, 0.2, 0.6)
_b = FUR.node_tree.nodes["Principled BSDF"]
_vc = FUR.node_tree.nodes.new("ShaderNodeVertexColor"); _vc.layer_name = "Col"
FUR.node_tree.links.new(_vc.outputs["Color"], _b.inputs["Base Color"])

BVH = [None]

def fuse():
    mb = bpy.data.metaballs.new("fur")
    mb.resolution = RESMB; mb.render_resolution = RESMB; mb.threshold = 0.6
    for c, r, rm, st, neg in BL:
        e = mb.elements.new(type='ELLIPSOID')
        e.co = c; e.radius = 1.0; e.stiffness = st; e.use_negative = neg
        e.size_x, e.size_y, e.size_z = r.x * FURK, r.y * FURK, r.z * FURK
        e.rotation = rm.to_quaternion()
    o = bpy.data.objects.new("furmeta", mb); sc.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.convert(target='MESH')
    o = bpy.context.object; o.name = "fur"
    md = o.modifiers.new('relax', 'SMOOTH'); md.factor = 0.6; md.iterations = 10
    bpy.ops.object.modifier_apply(modifier='relax')
    me = o.data
    n = len(me.vertices)
    P = np.empty(n * 3); me.vertices.foreach_get('co', P); P = P.reshape(n, 3)
    col = np.tile(np.array(C_OR), (n, 1))
    # subtle depth tone: slightly deeper orange low on the body, lighter on top
    zt = np.clip((P[:, 2] - 0.2) / 2.0, 0, 1)[:, None]
    col = col * (0.93 + 0.1 * zt)
    for c, r, rm, zc, a, b in ZN:
        q = ((P - np.array(c)) @ np.array(rm)) / np.array(r)
        d = np.linalg.norm(q, axis=1)
        t = np.clip((d - a) / (b - a), 0, 1)
        w = 1 - t * t * (3 - 2 * t)
        col = col * (1 - w[:, None]) + np.array(zc) * w[:, None]
    rgba = np.concatenate([col, np.ones((n, 1))], axis=1).astype(np.float32)
    ca = me.color_attributes.new("Col", 'FLOAT_COLOR', 'POINT')
    ca.data.foreach_set('color', rgba.ravel())
    me.materials.append(FUR)
    smooth(o)
    dg = bpy.context.evaluated_depsgraph_get()
    BVH[0] = BVHTree.FromObject(o, dg)
    print("FUR verts", n)
    return o

def fy(x, z):
    """head-local y of the fused surface at head-local (x, z), probing from the front."""
    R = HS["R"]
    o = HS["hp"] + R @ V((x, -1.3, z)); d = R @ V((0, 1, 0))
    Ri = R.inverted()
    for _ in range(5):
        hit = BVH[0].ray_cast(o, d, 2.5)[0]
        if hit is None: return -0.8
        y = (Ri @ (hit - HS["hp"])).y
        if y > -1.12: return y        # ignore paws/limbs in front of the face
        o = hit + d * 0.02
    return -0.8

def build_head_feats(hp, hrot, eyes="open", mouth="smile", brows="happy", earL=(14, 0), earR=(14, 0), blink=0.0, blush=True):
    H = pivot("head", hp, parent=PAR[0])
    P = lambda l: V(hp) + V(l)
    ell("nose", P((0, fy(0, MZ[2] + 0.17) + 0.035, MZ[2] + 0.17)), (0.14, 0.095, 0.095), NOSE, parent=H)
    ell("noseh", P((-0.035, fy(0, MZ[2] + 0.17) - 0.02, MZ[2] + 0.2)), (0.04, 0.015, 0.022), LIGHT, parent=H, seg=12, rings=8)
    if blush:
        for s in (-1, 1):
            x, z = s * 0.66, -0.12
            ell("blush", P((x, fy(x, z) + 0.03, z)), (0.12, 0.03, 0.07), BLUSH, rot=(0, 0, s * -0.9), parent=H)
    for s in (-1, 1):
        ex, ez = s * 0.43, 0.02
        ey = fy(ex, ez)
        if eyes == "open":
            sq = blink
            hz = 0.21 * (1 - 0.92 * sq)
            ell("eye", P((ex, ey + 0.03, ez)), (0.165, 0.1, hz), EYE, rot=(0, 0, s * 0.45), parent=H, seg=40, rings=24)
            if sq < 0.5:
                ell("iris", P((ex + s * 0.005, ey - 0.01, ez - 0.075)), (0.12, 0.06, 0.1 * (1 - sq)), IRIS, rot=(0, 0, s * 0.45), parent=H, seg=32, rings=16)
                ell("cl1", P((ex - s * 0.045, ey - 0.075, ez + 0.075)), (0.038, 0.02, 0.038), LIGHT, parent=H, seg=20, rings=10)
                ell("cl2", P((ex + s * 0.07, ey - 0.07, ez - 0.095)), (0.02, 0.012, 0.02), LIGHT, parent=H, seg=16, rings=8)
        elif eyes == "happy":
            pts = [P((ex + t * 0.17, ey - 0.0, ez - 0.07 + 0.14 * math.cos(t * math.pi / 2))) for t in [i / 8 * 2 - 1 for i in range(9)]]
            curve("eyeA", pts, 0.032, LINE, parent=H)
        elif eyes == "closed":
            pts = [P((ex + t * 0.17, ey - 0.0, ez + 0.06 - 0.1 * math.cos(t * math.pi / 2))) for t in [i / 8 * 2 - 1 for i in range(9)]]
            curve("eyeC", pts, 0.03, LINE, parent=H)
    for s in (-1, 1):
        ex = s * 0.43; ez = 0.32
        tilt = 0.0; lift = 0.0
        if brows == "happy": tilt = -0.22; lift = 0.04
        elif brows == "soft": tilt = 0.42
        elif brows == "up_one":
            lift = 0.09 if s == 1 else -0.02
            tilt = -0.2 if s == 1 else 0.15
        elif brows == "none": continue
        z = ez + lift
        ell("brow", P((ex, fy(ex, z) + 0.01, z)), (0.14, 0.035, 0.055), BROW, rot=(0, s * tilt, s * 0.225), parent=H, seg=24, rings=12)
    front = lambda x, z: fy(x, z) - 0.008
    if mouth in ("smile", "soft"):
        k = 0.075 if mouth == "smile" else 0.05
        zc = MZ[2] - 0.05
        pts = []
        for i in range(25):
            t = i / 24 * 2 - 1
            x = t * 0.24
            z = zc - k * abs(math.sin(math.pi * t)) ** 0.8 * (1 if t != 0 else 0)
            pts.append(P((x, front(x, z), z)))
        curve("smile", pts, 0.015, LINE, parent=H)
        curve("phil", [P((0, front(0, MZ[2] - 0.0), MZ[2] - 0.0)), P((0, front(0, zc), zc))], 0.014, LINE, parent=H)
        if mouth == "smile":
            ell("tongue", P((0.0, fy(0, zc - 0.07) + 0.01, zc - 0.075)), (0.055, 0.035, 0.04), TONGUE, parent=H, seg=20, rings=10)
    elif mouth in ("open", "bigopen"):
        big = 1.3 if mouth == "bigopen" else 1.0
        mz = -0.45
        ell("mouth", P((0, -0.80, mz)), (0.24, 0.1, 0.1 * big + 0.05), MOUTH, parent=H, seg=40, rings=24)
        ell("tongue", P((0, -0.82, mz - 0.07 * big)), (0.16, 0.09, 0.07 * big + 0.03), TONGUE, rot=(0.25, 0, 0), parent=H, seg=40, rings=24)
        ell("tonguehi", P((0, -0.9, mz - 0.05 * big)), (0.07, 0.025, 0.03), TONGUE2, rot=(0.25, 0, 0), parent=H, seg=16, rings=8)
        curve("tgrv", [P((0, -0.9, mz - 0.0 * big)), P((0, -0.91, mz - 0.1 * big))], 0.007, TGRV, parent=H)
        curve("phil", [P((0, front(0, MZ[2]), MZ[2])), P((0, front(0, MZ[2] - 0.1), MZ[2] - 0.1))], 0.014, LINE, parent=H)
    for s, e in ((-1, earL), (1, earR)):
        oa, fa = e[0], e[1]; fold = e[2] if len(e) > 2 else 0.0
        EP = pivot("earp", P((s * 0.56, 0.1, 0.5)), parent=H)
        ear_mesh("ear", P((s * 0.56, 0.1, 0.5)), 0.38, 0.19, 1.0, ORANGE, EP, tipw=0.5, fold=fold)
        ear_mesh("earin", P((s * 0.555, 0.0, 0.56)), 0.26, 0.15, 0.78, PINKIN, EP, tipw=0.5, fold=fold, zf=0.55 / 0.78 * 0.9)
        EP.rotation_euler = (R2(fa), R2(s * oa), 0)
    if OUTFIT: add_outfit(H, hp)
    H.rotation_euler = tuple(R2(a) for a in hrot)
    return H

# ================= optional outfit layer (OUTFIT env var; nothing here runs without it) =================
# Every accessory object is named ACC*, parented to the head pivot (hats, glasses, neckwear) or the
# root (cape) so it follows the pose, and is ignored by the camera framing so outfitted renders line
# up pixel for pixel with the plain ones.
def acc_mat(name, hexc, rough=0.7, metal=0.0, sheen=0.4):
    m = bpy.data.materials.new("ACC" + name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = lin(hexc)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for k, v in (("Sheen Weight", sheen), ("Specular IOR Level", 0.3)):
        if k in b.inputs: b.inputs[k].default_value = v
    return m

def aprim(kind, loc, scale, mt, rot=(0, 0, 0), parent=None, name="ACC", **kw):
    if kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=40, ring_count=24, location=loc)
    elif kind == "cyl":
        bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, vertices=48, location=loc)
    elif kind == "cone":
        bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=kw.get("r2", 0.0), depth=2, vertices=48, location=loc)
    elif kind == "torus":
        bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=kw.get("minor", 0.15), major_segments=64,
                                         minor_segments=20, location=loc)
    elif kind == "cube":
        bpy.ops.mesh.primitive_cube_add(size=2, location=loc)
    o = bpy.context.object
    o.name = "ACC" + name
    o.scale = scale
    o.rotation_euler = tuple(R2(a) for a in rot)
    smooth(o)
    if kind == "cube":
        bv = o.modifiers.new("bev", 'BEVEL'); bv.width = 0.25; bv.segments = 4
    o.data.materials.append(mt)
    setpar(o, parent or PAR[0])
    return o

def amesh(name, verts, faces, mt, parent, thick=0.0):
    me = bpy.data.meshes.new("ACC" + name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    o = bpy.data.objects.new("ACC" + name, me)
    sc.collection.objects.link(o)
    if thick:
        md = o.modifiers.new("sol", 'SOLIDIFY'); md.thickness = thick; md.offset = 0
    me.materials.append(mt)
    setpar(o, parent)
    bpy.context.view_layer.objects.active = o
    for p in me.polygons: p.use_smooth = True
    return o

def add_outfit(H, hp):
    P = lambda l: V(hp) + V(l)
    k = OUTFIT
    RED = acc_mat("red", "#D7263D", 0.75)
    DRED = acc_mat("dred", "#B3162B", 0.75)
    WHT = acc_mat("wht", "#FFFFFF", 0.7, sheen=0.2)
    BLU = acc_mat("blu", "#2F6FB5", 0.7)
    NAVY = acc_mat("navy", "#1F3F73", 0.6)
    GOLD = acc_mat("gold", "#F2B632", 0.3, metal=0.35, sheen=0.1)
    JADE = acc_mat("jade", "#1E9E78", 0.55)
    DARK = acc_mat("dark", "#2B2B33", 0.5, sheen=0.1)
    if k == "bandana":
        # triangle neckerchief: a band under the chin plus a point hanging on the chest
        aprim("torus", P((0, -0.06, -0.9)), (0.58, 0.5, 0.6), BLU, parent=H, name="band", minor=0.13)
        vs = [P(v) for v in ((-0.52, -0.5, -0.86), (0.52, -0.5, -0.86), (0.0, -0.66, -1.38))]
        amesh("tri", vs, [(0, 1, 2)], BLU, H, thick=0.06)
        for x, z in ((-0.2, -0.98), (0.2, -0.98), (0.0, -1.12), (-0.08, -0.9), (0.08, -0.9)):
            aprim("sphere", P((x, -0.64 + 0.1 * abs(x), z + 0.0)), (0.045, 0.014, 0.045), WHT, parent=H, name="dot")
    elif k == "bowtie":
        c = (0, -0.56, -0.9)
        for s in (-1, 1):
            aprim("cone", P((c[0] + s * 0.24, c[1], c[2])), (0.21, 0.08, 0.21), RED, rot=(0, s * 90, 0), parent=H, name="wing", r2=0.35)
        aprim("sphere", P(c), (0.1, 0.09, 0.115), DRED, parent=H, name="knot")
    elif k == "cap":
        # baseball cap: dome sits on the crown between the ears, brim points forward over the forehead
        aprim("sphere", P((0, -0.06, 0.6)), (0.5, 0.5, 0.5), RED, rot=(-6, 0, 0), parent=H, name="dome")
        aprim("cyl", P((0, -0.06, 0.58)), (0.51, 0.51, 0.025), DRED, parent=H, name="rimline")
        sl = POSE == "sleep"   # head is pitched forward when asleep: tilt the brim up so it reads as a peak
        aprim("sphere", P((0, -0.7, 0.62 if sl else 0.58)), (0.4, 0.38, 0.045), DRED, rot=(-4 if sl else 14, 0, 0), parent=H, name="brim")
        aprim("sphere", P((0, -0.06, 1.1)), (0.06, 0.06, 0.05), DRED, parent=H, name="button")
    elif k == "glasses":
        for s in (-1, 1):
            ex, ez = s * 0.43, 0.02
            y = fy(ex, ez)
            aprim("torus", P((ex, y - 0.03, ez)), (0.255, 0.255, 0.255), DARK, rot=(90, 0, 0), parent=H, name="rim", minor=0.075)
        aprim("cyl", P((0, fy(0, 0.06) - 0.025, 0.06)), (0.022, 0.022, 0.1), DARK, rot=(0, 90, 0), parent=H, name="bridge")
    elif k == "scarf":
        # knitted scarf, lai-see red with gold stripes, one tail hanging down the chest
        aprim("torus", P((0, -0.06, -0.9)), (0.62, 0.52, 0.6), RED, parent=H, name="wrap", minor=0.2)
        for dz in (-0.13, 0.13):
            aprim("torus", P((0, -0.06, -0.9 + dz)), (0.6, 0.5, 0.6), GOLD, parent=H, name="gstripe", minor=0.045)
        aprim("cube", P((0.3, -0.52, -1.25)), (0.18, 0.05, 0.4), RED, rot=(0, -5, 0), parent=H, name="tail")
        for z in (-1.08, -1.25):
            aprim("cube", P((0.3, -0.56, z)), (0.182, 0.054, 0.035), GOLD, rot=(0, -5, 0), parent=H, name="tailstripe")
        for i in range(5):
            aprim("cyl", P((0.2 + i * 0.05, -0.55, -1.68)), (0.014, 0.014, 0.1), GOLD, parent=H, name="fringe")
    elif k == "chef":
        # tall white toque between the ears
        aprim("cyl", P((0, -0.06, 0.74)), (0.36, 0.35, 0.14), WHT, parent=H, name="band")
        aprim("cyl", P((0, -0.06, 0.8)), (0.345, 0.335, 0.025), RED, parent=H, name="stripe")
        aprim("sphere", P((0, -0.06, 1.2)), (0.46, 0.43, 0.34), WHT, parent=H, name="puff")
        for s in (-1, 1):
            aprim("sphere", P((s * 0.27, -0.06, 1.0)), (0.2, 0.2, 0.2), WHT, parent=H, name="puffs")
        aprim("sphere", P((0, 0.12, 1.0)), (0.22, 0.2, 0.2), WHT, parent=H, name="puffb")
    elif k == "crown":
        aprim("cyl", P((0, -0.06, 0.8)), (0.34, 0.33, 0.09), GOLD, parent=H, name="ring")
        for i in range(5):
            a = i / 5 * 2 * math.pi
            x, y = 0.32 * math.sin(a), -0.06 - 0.31 * math.cos(a)
            aprim("cone", P((x, y, 1.02)), (0.1, 0.1, 0.17), GOLD, parent=H, name="spike", r2=0.0)
            aprim("sphere", P((x, y, 1.2)), (0.055, 0.055, 0.055), RED if i % 2 == 0 else BLU, parent=H, name="gem")
        aprim("sphere", P((0, -0.4, 0.82)), (0.07, 0.04, 0.07), RED, parent=H, name="front")
    elif k == "cape":
        cape_build()
        aprim("torus", P((0, -0.06, -0.9)), (0.6, 0.5, 0.6), RED, parent=H, name="collar", minor=0.1)
        aprim("sphere", P((0, -0.55, -0.9)), (0.12, 0.06, 0.12), GOLD, parent=H, name="brooch")

def cape_build():
    RED = acc_mat("cred", "#D7263D", 0.8, sheen=0.7)
    GOLD = acc_mat("cgold", "#F2B632", 0.3, metal=0.35, sheen=0.1)
    z0 = LIFT[0]
    if POSE == "sleep":
        # blanket-style cape lying over the back: drop each point onto the fur surface
        n, m = 26, 22
        vs = []; fs = []
        def top(x, y):
            for xs in [abs(x) - 0.02 * q for q in range(0, 60)]:
                if xs < 0: break
                hit = BVH[0].ray_cast(V((math.copysign(xs, x), y, 3.0)), V((0, 0, -1)), 4.0)[0]
                if hit is not None:
                    return min(hit.z, 0.9) + 0.045 - 1.6 * (abs(x) - xs)
            return 0.1
        for j in range(m):
            v = j / (m - 1)
            y = 0.5 + v * 1.05
            for i in range(n):
                u = i / (n - 1) * 2 - 1
                x = u * (0.78 + 0.12 * v)
                vs.append((x, y, max(0.04, top(x, y))))
        for j in range(m - 1):
            for i in range(n - 1):
                a = j * n + i; fs.append((a, a + 1, a + n + 1, a + n))
        amesh("cape", vs, fs, RED, PAR[0], thick=0.03)
        return
    prof = [(1.52, -0.08, 0.52, 0.48), (1.3, 0.08, 0.64, 0.62), (1.0, 0.36, 0.8, 0.82), (0.7, 0.6, 0.82, 0.88), (0.38, 0.82, 0.78, 0.8)]
    def interp(z):
        for a, b in zip(prof, prof[1:]):
            if b[0] <= z <= a[0]:
                t = (a[0] - z) / (a[0] - b[0])
                return tuple(a[i] + (b[i] - a[i]) * t for i in range(1, 4))
        return prof[-1][1:] if z < prof[-1][0] else prof[0][1:]
    n, m = 26, 20
    vs = []; fs = []
    for j in range(m):
        v = j / (m - 1)
        z = 1.5 - v * 1.15 + z0
        cy, rx, ry = interp(z - z0)
        flare = 0.2 + 0.5 * v
        for i in range(n):
            u = i / (n - 1) * 2 - 1
            th = u * math.radians(125)
            x = (rx + flare) * math.sin(th)
            y = cy + (ry + flare * 0.6) * math.cos(th) + 0.04
            vs.append((x, y, z))
    for j in range(m - 1):
        for i in range(n - 1):
            a = j * n + i; fs.append((a, a + 1, a + n + 1, a + n))
    amesh("cape", vs, fs, RED, PAR[0], thick=0.035)


def hb(kw):
    return dict(earL=kw.get("earL", (14, 0)), earR=kw.get("earR", (14, 0)),
                mouth_open={"open": 1.0, "bigopen": 1.3}.get(kw.get("mouth"), 0.0))

def make_sit(rig, head_kw):
    bob = rig.get("bob", 0.0); lift = rig.get("lift", 0.0)
    hp = V((0, -0.14, 1.94 + bob + lift)); hrot = rig.get("hrot", (0, 0, -22)); LIFT[0] = lift
    roll = rig.get("roll", 0.0)
    SWAY["M"] = Euler((0, R2(roll), 0), 'XYZ').to_matrix()
    set_head(hp, hrot)
    torso_sit(rig); head_blobs(**hb(head_kw))
    fuse()
    if roll:
        hp = sw(hp)
        hrot = tuple(math.degrees(a) for a in (SWAY["M"] @ eu(hrot)).to_euler('XYZ'))
        set_head(hp, hrot)
    Rt = pivot("root", (0, 0, 0), parent=None); PAR[0] = Rt
    build_head_feats(hp, hrot, **head_kw)
    Rt.rotation_euler = (R2(rig.get("pitch", 0)), 0, 0)

def build(pose):
    if pose == "idle":
        ph = 2 * math.pi * T
        blink = max(0.0, 1 - abs(T - 0.62) / 0.05) if abs(T - 0.62) < 0.05 else 0.0
        make_sit(dict(bob=0.03 * math.sin(ph), wag=26 * math.sin(2 * ph),
                      hrot=(2 * math.sin(ph + 0.6), 1.5 * math.sin(ph), -26 + 2.5 * math.sin(ph))),
                 dict(eyes="open", mouth="smile", blink=blink))
    elif pose == "wave":
        ph = 2 * math.pi * T
        make_sit(dict(hrot=(0, 4 + 1.5 * math.sin(ph), -24), legR=(-5 + 4 * math.cos(2 * ph), -132 + 16 * math.sin(2 * ph), 0), legscale=1.6, wag=18 * math.sin(2 * ph), bob=0.01 * math.sin(2 * ph)),
                 dict(eyes="open", mouth="open", brows="happy"))
    elif pose == "point":
        e = math.sin(math.pi * T) ** 2; e = min(1.0, e * 1.5)       # extend, hold, return
        e = e * e * (3 - 2 * e)
        make_sit(dict(hrot=(0, -6 * e, -22 + 2 * e), legR=(-10 * e, -95 * e, 0), blendlegR=e, legL=(0, 0, 0), wag=10 * math.sin(2 * math.pi * T)),
                 dict(eyes="open", mouth="smile"))
    elif pose == "wiggle":
        ph = 2 * math.pi * T
        make_sit(dict(hrot=(0, -9 * math.sin(ph), -22 + 7 * math.sin(ph)), roll=10 * math.sin(ph), wag=34 * math.sin(2 * ph), bob=0.03 * math.cos(2 * ph)),
                 dict(eyes="happy", mouth="smile", brows="happy"))
    elif pose == "tilt":
        e = math.sin(math.pi * T) ** 2; e = min(1.0, e * 1.4); e = e * e * (3 - 2 * e)
        make_sit(dict(hrot=(2 * e, 17 * e, -22 - 4 * e)),
                 dict(eyes="open", mouth="soft", brows="up_one", earL=(14 + 6 * e, 0), earR=(14, 3 * e, 20 * e)))
    elif pose == "think":
        make_sit(dict(hrot=(0, 18, -16)),
                 dict(eyes="open", mouth="soft", brows="up_one", earL=(14, 0), earR=(14, 4, 105)))
    elif pose == "encourage":
        make_sit(dict(hrot=(8, 0, -24), wag=12),
                 dict(eyes="open", mouth="smile", brows="soft"))
    elif pose == "cheer":
        ph = 2 * math.pi * T
        h = (1 - math.cos(ph)) / 2
        pump = math.sin(ph)
        make_sit(dict(hrot=(-8 - 3 * h, 0, -22), lift=0.03 + 0.2 * h, legL=(-8, 125 - 6 * pump, -25), legR=(-8, -125 + 6 * pump, 25), legscale=1.4, wag=24 * math.sin(2 * ph)),
                 dict(eyes="happy", mouth="bigopen", brows="happy", earL=(20, 0), earR=(20, 0)))
    elif pose == "sleep":
        sb = math.sin(2 * math.pi * T)
        hp = V((0, -0.2, 1.0 + 0.012 * sb)); hrot = (16 + 0.8 * sb, 0, -24)
        set_head(hp, hrot)
        sleep_blobs(sb); head_blobs(**hb(dict(earL=(22, 8), earR=(30, 14), mouth="soft"))); fuse()
        PAR[0] = pivot("root", (0, 0, 0), parent=None)
        build_head_feats(hp, hrot, eyes="closed", mouth="soft", brows="soft", earL=(22, 8), earR=(30, 14))
    elif pose == "headopen":
        set_head((0, 0, 0), (0, 0, 0))
        head_blobs(mouth_open=1.0); fuse()
        PAR[0] = pivot("root", (0, 0, 0), parent=None)
        build_head_feats((0, 0, 0), (0, 0, 0), eyes="open", mouth="open")
    elif pose == "headthink":
        set_head((0, 0, 0), (0, 0, 0))
        head_blobs(earL=(14, 0), earR=(14, 4, 105)); fuse()
        PAR[0] = pivot("root", (0, 0, 0), parent=None)
        build_head_feats((0, 0, 0), (0, 0, 0), eyes="open", mouth="soft", brows="up_one", earL=(14, 0), earR=(14, 4, 105))
    elif pose == "head":
        set_head((0, 0, 0), (0, 0, 0))
        head_blobs(); fuse()
        PAR[0] = pivot("root", (0, 0, 0), parent=None)
        build_head_feats((0, 0, 0), (0, 0, 0), eyes="open", mouth="smile")

build(POSE)

# ---- ground shadow (soft radial)
if POSE not in ("head", "headopen", "headthink"):
    sw = {"sleep": (1.5, 1.4), "cheer": (1.0, 1.4)}.get(POSE, (1.0, 1.55))
    bpy.ops.mesh.primitive_circle_add(vertices=64, fill_type='NGON', radius=1, location=(0, 0.55, 0.003))
    sd = bpy.context.object
    sd.scale = (sw[0], sw[1], 1)
    sd.name = "shadow"
    sm = bpy.data.materials.new("shadow")
    sm.use_nodes = True
    nt = sm.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Location"].default_value = (-0.5, -0.5, 0)
    gr = nt.nodes.new("ShaderNodeTexGradient"); gr.gradient_type = 'SPHERICAL'
    cr = nt.nodes.new("ShaderNodeValToRGB")
    # spherical gradient: 1 at centre, 0 at distance .5
    cr.color_ramp.elements[0].position = 0.0
    cr.color_ramp.elements[0].color = (0, 0, 0, 1)
    cr.color_ramp.elements[1].position = 0.9
    cr.color_ramp.elements[1].color = (1, 1, 1, 1)
    ramp_in = nt.nodes.new("ShaderNodeMath"); ramp_in.operation = 'MULTIPLY'; ramp_in.inputs[1].default_value = 1.0
    pb = nt.nodes.new("ShaderNodeBsdfPrincipled")
    pb.inputs["Base Color"].default_value = (0.25, 0.1, 0.04, 1)
    pb.inputs["Roughness"].default_value = 1
    mm = nt.nodes.new("ShaderNodeMath"); mm.operation = 'MULTIPLY'; mm.inputs[1].default_value = 0.38
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    nt.links.new(mp.outputs[0], gr.inputs[0])
    nt.links.new(gr.outputs["Fac"], cr.inputs[0])
    nt.links.new(cr.outputs[0], mm.inputs[0])
    nt.links.new(mm.outputs[0], pb.inputs["Alpha"])
    nt.links.new(pb.outputs[0], out.inputs[0])
    sm.surface_render_method = 'BLENDED'
    sd.data.materials.append(sm)
    sd.visible_shadow = False

# ---- lights, world, camera
w = bpy.data.worlds.new("w"); sc.world = w
w.use_nodes = True
bg = w.node_tree.nodes["Background"]
bg.inputs[0].default_value = (1.0, 0.95, 0.9, 1)
bg.inputs[1].default_value = 0.4

def area(name, loc, energy, size, color=(1, 1, 1)):
    l = bpy.data.lights.new(name, 'AREA')
    l.energy = energy; l.size = size; l.color = color
    o = bpy.data.objects.new(name, l)
    sc.collection.objects.link(o)
    o.location = loc
    return o

tgt = bpy.data.objects.new("tgt", None); sc.collection.objects.link(tgt)
def aim(o):
    c = o.constraints.new('TRACK_TO'); c.target = tgt
    c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
cam = bpy.data.cameras.new("cam"); cam.type = 'ORTHO'
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
if POSE in ("head", "headopen", "headthink"):
    az, el, tz, S = 20, 4, 0.0, 2.7
elif POSE == "sleep":
    az, el, tz, S = 38, 22, 0.5, 4.4
else:
    az, el, tz, S = 34, 15, 1.4, 4.9
tgt.location = (0, 0.0, tz)
for o in (area("key", (-4.5, -5.5, 6.5), 380, 5, (1, 0.96, 0.9)),
          area("fill", (5.5, -4, 3), 150, 6, (0.95, 0.97, 1.0)),
          area("rim", (3.5, 6, 4.5), 420, 3, (1, 0.9, 0.75)),
          area("rim2", (-4, 5, 4), 380, 3, (1, 0.93, 0.8)),
          area("top", (0, -1, 8), 70, 6)):
    aim(o)
d = 14
co.location = (-math.sin(R2(az)) * math.cos(R2(el)) * d + tgt.location.x,
               -math.cos(R2(az)) * math.cos(R2(el)) * d + tgt.location.y,
               tz + math.sin(R2(el)) * d)
aim(co)
cam.ortho_scale = S
cam.clip_end = 100
bpy.context.view_layer.update()

mi = [1e9, 1e9]; ma = [-1e9, -1e9]
inv = co.matrix_world.inverted()
for o in sc.objects:
    if o.type in ('MESH', 'CURVE') and o.name != "shadow" and not o.name.startswith("ACC") and not (o.parent and o.parent.name.startswith("ACC")):
        for c in o.bound_box:
            p = inv @ (o.matrix_world @ V(c))
            mi[0] = min(mi[0], p.x); ma[0] = max(ma[0], p.x)
            mi[1] = min(mi[1], p.y); ma[1] = max(ma[1], p.y)
cx, cy = (mi[0] + ma[0]) / 2, (mi[1] + ma[1]) / 2
print("BBOX w,h", ma[0] - mi[0], ma[1] - mi[1], "scale", S)
SJ = os.environ.get("MASCOT_SHIFT") or os.path.join(TMP, "idle_shift.json")
if POSE == "idle" or os.environ.get("MASCOT_SHIFT"):
    # animation clips: the reference frame (T == MASCOT_REF, default 0) writes the shared camera shift, all other frames reuse it
    if abs(T - float(os.environ.get("MASCOT_REF", "0"))) < 1e-9:
        json.dump([cx, cy], open(SJ, "w"))
    elif os.path.exists(SJ):
        cx, cy = json.load(open(SJ))
cam.shift_x = cx / S
cam.shift_y = cy / S

sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x = sc.render.resolution_y = RES
sc.render.film_transparent = True
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGBA'
sc.view_settings.view_transform = 'Standard'
try: sc.eevee.taa_render_samples = SAMPLES
except Exception: pass
for a, v in (("use_raytracing", True), ("use_gtao", True), ("gtao_distance", 0.6), ("use_shadows", True)):
    try: setattr(sc.eevee, a, v)
    except Exception: pass
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("DONE", POSE)
