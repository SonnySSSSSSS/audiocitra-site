"""Lahari as analog rack gear, for the site's hero shots: the editor's own capture as the front panel, real 3D knobs at real height
standing on the printed ones (each cap carries its own printed top and pointer from the capture), and the Noir rack around it (ears,
handles, crinkle chassis, the dark studio), as in the Spanda, Agni and Gālana Noir rack shots. Replaces tools/lahari_hero.py's knobs,
which stood 0.35 x their diameter.

    CAP=<3x capture> SKIN=fantasy|analog [CYCLES_DEVICE=GPU] blender -b -noaudio -t 4 -P lahari_rack.py -- <out.png> <samples> <res_x> <res_y> [hero|right]

The capture: LAHARI_SCALE=3 LahariSnapshot <dir> (SynthLab akasa-vst), one PNG per skin, 2700 x 1680 for the 900 x 560 editor.
Env: KIT = a folder holding noir_plate_kit.py (default Agni's tools/skins); ROOM = the studio image the lacquer mirrors (default
Gālana's tools/noir/noir_room.png); KNOBH=old keeps the drawn proportions (0.35 x the diameter)."""
import bpy, math, os, sys
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
HOUT, HSAMP, RX, RY = os.path.abspath(argv[0]), int(argv[1]), int(argv[2]), int(argv[3])
SHOT = argv[4] if len(argv) > 4 else "hero"
SKIN = os.environ.get("SKIN", "fantasy"); CAP = os.environ["CAP"]
sys.path.insert(0, os.environ.get("KIT", r"D:\AI\Agni\tools\skins"))
import noir_plate_kit as K
W, H = 900, 560
K.W, K.H = W, H
P, mat, box, bevel, smooth = K.P, K.mat, K.box, K.bevel, K.smooth
K.reset()
sc = bpy.context.scene

# Knobs per skin, editor px: (x, y, skirt radius, cap radius, angle deg). Fantasy: a gold ring round a black glass cap; Analog: a
# black bakelite body, its pointer moulded in. Angles as captured (the knobs' default values).
KN = {
    "fantasy": [(125, 170, 30, 24, 0), (235, 170, 30, 24, 0), (125, 348, 30, 24, 0), (235, 348, 30, 24, 0),
                (665, 170, 30, 24, 0), (775, 170, 30, 24, 0), (665, 348, 30, 24, 0), (775, 348, 30, 24, 0)],
    "analog": [(107, 448, 24, 21, 0), (205, 448, 24, 21, 0), (303, 448, 24, 21, 0), (401, 448, 24, 21, 0),
               (499, 448, 24, 21, 0), (597, 448, 24, 21, 0), (695, 448, 24, 21, 0), (793, 448, 24, 21, 0),
               (371, 228, 30, 26, 0), (371, 306, 16, 14, 0)],          # the unit selector; LFO Rate
}[SKIN]
MM_PER_PX = 483.0 / W                          # the 19-inch face
def top_units(rs):
    """the knob's height above the panel (scene units, 100 px = 1): 9 mm + 0.24 x its diameter, held to 12..20 mm"""
    if os.environ.get("KNOBH") == "old": return 0.7 * rs / 100.0
    return min(20.0, max(12.0, 9.0 + 0.24 * 2 * rs * MM_PER_PX)) / MM_PER_PX / 100.0

# ---------- the capture ----------
img = bpy.data.images.load(CAP); cw, chh = img.size
pxs = np.empty(cw * chh * 4, np.float32); img.pixels.foreach_get(pxs); pxs = pxs.reshape(chh, cw, 4)
def ring_col(x, y, r0, r1):
    """median colour of the capture in an annulus (editor px): the printed knob's own side colour"""
    k = cw / W; yy, xx = np.mgrid[0:chh, 0:cw]; fy = (chh - 1 - yy) / k; fx = xx / k
    d2 = (fx - x) ** 2 + (fy - y) ** 2; m = (d2 >= r0 * r0) & (d2 <= r1 * r1)
    return tuple(float(v) for v in np.median(pxs[m][:, :3], axis=0))

def print_mat(name, side, rough=0.3, coat=0.6, metal=0.0, emit=0.0):
    """the capture on every face that looks up (a knob's top, the panel), a plain side colour on the rest"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough; b.inputs["Coat Weight"].default_value = coat; b.inputs["Metallic"].default_value = metal
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = img; t.interpolation = "Cubic"
    tc = nt.nodes.new("ShaderNodeTexCoord"); sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Normal"], sp.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.93; mr.inputs["From Max"].default_value = 0.99
    nt.links.new(sp.outputs["Z"], mr.inputs["Value"])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; nt.links.new(mr.outputs[0], mx.inputs[0])
    mx.inputs[6].default_value = (*side, 1); nt.links.new(t.outputs["Color"], mx.inputs[7]); nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    if emit:
        e = nt.nodes.new("ShaderNodeMath"); e.operation = "MULTIPLY"; e.inputs[1].default_value = emit; nt.links.new(mr.outputs[0], e.inputs[0])
        nt.links.new(t.outputs["Color"], b.inputs["Emission Color"]); nt.links.new(e.outputs[0], b.inputs["Emission Strength"])
    return m
def planar_uv(o):
    uv = o.data.uv_layers[0] if o.data.uv_layers else o.data.uv_layers.new()
    for poly in o.data.polygons:
        for li in poly.loop_indices:
            v = o.matrix_world @ o.data.vertices[o.data.loops[li].vertex_index].co
            uv.data[li].uv = (v.x / (W / 100) + 0.5, v.y / (H / 100) + 0.5)

# ---------- the panel: the capture, lit a little so displays and lamps read ----------
PW, PH = W / 100 + 0.3, H / 100 + 0.3
M_FACE = print_mat("face", (0.01, 0.01, 0.012), rough=0.42, coat=0.15 if SKIN == "fantasy" else 0.1, emit=0.12)
M_EDGE = mat("panel_edge", ring_col(450, 548, 0, 6) if SKIN == "analog" else (0.012, 0.012, 0.016), rough=0.4, coat=0.5)
edge = box(0, 0, PW, PH, -0.2, -0.002); edge.data.materials.append(M_EDGE); bevel(edge, 0.02, 3, 40)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0)); face = bpy.context.object
face.scale = (W / 100, H / 100, 1); bpy.ops.object.transform_apply(scale=True); face.data.materials.append(M_FACE); planar_uv(face)

# ---------- the knobs ----------
for (x, y, rs, rc, deg) in KN:
    cx, cy = P(x, y); R_s, R_c = rs / 100.0, rc / 100.0; top = top_units(rs)
    side = ring_col(x, y, rc * 0.82, rc * 0.98)
    m = print_mat("knob", tuple(v * 0.9 for v in side), rough=0.3, coat=0.7)
    hs = min(top * 0.22, 0.06)                                         # the skirt (the printed ring round the cap stands with it)
    bpy.ops.mesh.primitive_cylinder_add(vertices=160, radius=R_s, depth=hs, location=(cx, cy, hs / 2)); s = bpy.context.object
    s.data.materials.append(print_mat("skirt", ring_col(x, y, rc * 1.05, rs * 0.95), rough=0.28, coat=0.4,
                                      metal=0.9 if SKIN == "fantasy" else 0.0)); bevel(s, R_s * 0.06, 3); smooth(s); planar_uv(s)
    bpy.ops.mesh.primitive_cylinder_add(vertices=160, radius=R_c, depth=top - hs, location=(cx, cy, hs + (top - hs) / 2)); k = bpy.context.object
    k.data.materials.append(m); bevel(k, R_c * 0.16, 8); smooth(k); planar_uv(k)

# ---------- every other control as hardware (owner 2026-11-25: the round display, header, VU meters and keys read flat) ----------
# Editor px from the 3x captures (the spec files predate the current header). Heights in mm: keys 3-6, bezels 3-6, the glass dome 8.
MMU = 1.0 / MM_PER_PX / 100.0                   # scene units per mm
def upd(o): bpy.context.view_layer.update(); planar_uv(o); return o
def key(x0, y0, x1, y1, h_mm, rad=4, side=None, rough=0.35, coat=0.5, metal=0.0, emit=0.0):
    """a raised part: its printed face on top, its sides in the colour of its printed edge"""
    side = side or ring_col_rect(x0, y0, x1, y1)
    o = K.rrect(x0, y0, x1, y1, rad, 0.0, h_mm * MMU, "key"); o.data.materials.append(print_mat("keym", side, rough, coat, metal, emit))
    bevel(o, min(1.2 * MMU, (min(x1 - x0, y1 - y0) / 100.0) * 0.18), 3, 40); smooth(o, 40); return upd(o)
def ring_col_rect(x0, y0, x1, y1):
    k = cw / W; a, b = int(x0 * k) + 2, int(x1 * k) - 2; c, d = int(y0 * k) + 2, int(y1 * k) - 2
    rows = pxs[chh - 1 - d:chh - 1 - c, a:b, :3]; edge = np.concatenate([rows[:3].reshape(-1, 3), rows[-3:].reshape(-1, 3)])
    return tuple(float(v) * 0.8 for v in np.median(edge, axis=0))
def frame(x0, y0, x1, y1, t, h_mm, rad=4, metal=0.0, glass=True):
    """a bezel round a window: the printed frame raised, the window's print left on the floor under a glass sheet"""
    side = ring_col_rect(x0, y0, x1, y1)
    for (a, b, c, d) in ((x0, y0, x1, y0 + t), (x0, y1 - t, x1, y1), (x0, y0 + t, x0 + t, y1 - t), (x1 - t, y0 + t, x1, y1 - t)):
        o = K.box((a + c) / 2 / 100 - W / 200, H / 200 - (b + d) / 2 / 100, (c - a) / 100, (d - b) / 100, 0.0, h_mm * MMU)
        o.data.materials.append(print_mat("bezel", side, 0.3, 0.5, metal)); bevel(o, min(0.8 * MMU, t / 100 * 0.3), 2, 40); upd(o)
    if glass: sheet(x0 + t, y0 + t, x1 - t, y1 - t, h_mm * MMU * 0.7)
M_GLASS = bpy.data.materials.new("glass"); M_GLASS.use_nodes = True; _g = M_GLASS.node_tree
for _n in list(_g.nodes): _g.nodes.remove(_n)
_tr = _g.nodes.new("ShaderNodeBsdfTransparent"); _gl = _g.nodes.new("ShaderNodeBsdfGlossy"); _gl.inputs["Roughness"].default_value = 0.03
_fr = _g.nodes.new("ShaderNodeFresnel"); _fr.inputs["IOR"].default_value = 1.5; _mx = _g.nodes.new("ShaderNodeMixShader"); _go = _g.nodes.new("ShaderNodeOutputMaterial")
_g.links.new(_fr.outputs[0], _mx.inputs[0]); _g.links.new(_tr.outputs[0], _mx.inputs[1]); _g.links.new(_gl.outputs[0], _mx.inputs[2]); _g.links.new(_mx.outputs[0], _go.inputs["Surface"])
def sheet(x0, y0, x1, y1, z):
    o = K.box((x0 + x1) / 200 - W / 200, H / 200 - (y0 + y1) / 200, (x1 - x0) / 100, (y1 - y0) / 100, z, z + 0.002)
    o.data.materials.append(M_GLASS); o.visible_shadow = False
def ring(cx_, cy_, r0, r1, h_mm, metal=0.0, rough=0.3):
    """a raised annulus (a bezel ring), its print on top"""
    side = ring_col(cx_, cy_, r0, r1)
    o = K.lathe([(r0 / 100, 0.0), (r1 / 100, 0.0), (r1 / 100, h_mm * MMU), (r0 / 100, h_mm * MMU)], 192, "ring")
    o.location = (*P(cx_, cy_), 0); o.data.materials.append(print_mat("ringm", side, rough, 0.5, metal)); bevel(o, 0.6 * MMU, 3, 40); smooth(o, 40)
    return upd(o)
def dome(cx_, cy_, r, h_mm, m=None, emit=0.0):
    """a lens, lamp or screw head: a flattened sphere standing on the panel, the capture printed on it"""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=r / 100, location=(*P(cx_, cy_), 0)); o = bpy.context.object
    o.scale.z = h_mm * MMU / (r / 100); smooth(o, 80)
    o.data.materials.append(m or print_mat("domem", ring_col(cx_, cy_, r * 0.8, r), 0.15, 1.0, 0.0, emit)); return upd(o)
def toggle(cx_, cy_):
    """a bat-handle toggle: a hex nut, a chrome bat, a ball tip"""
    x_, y_ = P(cx_, cy_); ch = mat("chrome2", (0.86, 0.86, 0.88), metal=1.0, rough=0.12)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=12 / 100, depth=3 * MMU, location=(x_, y_, 1.5 * MMU)); bpy.context.object.data.materials.append(ch)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=3.2 / 100, depth=16 * MMU, location=(x_, y_ + 4 / 100, 9 * MMU))
    b_ = bpy.context.object; b_.rotation_euler.x = math.radians(-22); b_.data.materials.append(ch); smooth(b_)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=4.5 / 100, location=(x_, y_ + 7.5 / 100, 17 * MMU)); bpy.context.object.data.materials.append(ch); smooth(bpy.context.object)
    for o in bpy.data.objects:           # the printed toggle under it stays on the panel: hide nothing, it reads as the nut's shadow
        pass

if SKIN == "fantasy":
    key(330, 27, 569, 54, 3.0, rad=8)                                  # the preset bar
    for a, b in ((578, 605), (609, 636), (640, 682)): key(a, 31, b, 53, 4.0, rad=4)      # A, B, COPY
    dome(711, 41, 9, 4.0, emit=0.6); dome(795, 41, 7, 3.0)             # ACTIVE / BYPASS lamps
    ring(450, 264, 118, 143, 3.0)                                      # the astrolabe's outer ring (unit names engraved)
    ring(450, 264, 110, 120, 6.0, metal=0.9, rough=0.22)               # its gold bezel
    bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=110 / 100, location=(*P(450, 264), 0))   # the glass dome
    gd = bpy.context.object; gd.scale.z = 8.0 * MMU / 1.10; smooth(gd, 80); gd.data.materials.append(M_GLASS); gd.visible_shadow = False
    dome(450, 106, 8, 4.0, emit=0.8)                                   # the lamp above it
    for (sx_, sy_) in ((315, 183), (585, 183), (315, 338), (585, 338), (450, 417)): dome(sx_, sy_, 6, 2.0)   # screws round it
    key(260, 473, 640, 513, 3.0, rad=8)                                # the program bar
    key(36, 480, 131, 501, 3.0, rad=4); key(138, 480, 241, 501, 3.0, rad=4)   # Vibrato, Preamp
    key(14, 418, 73, 445, 2.5, rad=4); key(826, 418, 885, 445, 2.5, rad=4)    # the meter readouts
    for (a, b) in ((30, 58), (842, 870)): frame(a, 98, b, 412, 3, 3.0, rad=2)  # the LED meter columns
    for xx in (125, 235, 665, 775):                                    # the value boxes under the knobs
        for yy in (224, 402): key(xx - 36, yy - 13, xx + 36, yy + 13, 2.5, rad=4)
else:
    key(59, 21, 279, 95, 3.0, rad=4)                                   # the logo plate
    frame(348, 29, 552, 77, 6, 3.0, rad=4)                             # the preset display's bezel
    key(304, 34, 342, 72, 6.0, rad=3); key(558, 34, 596, 72, 6.0, rad=3)      # preset < >
    for a, b in ((602, 620), (624, 642), (646, 680)): key(a, 44, b, 62, 3.5, rad=3)      # A, B, COPY
    ring(710, 56, 19, 24, 3.0); dome(710, 56, 19, 8.0, emit=0.5)       # EFFECT: a red lens in its collar
    toggle(795, 55)                                                    # BYPASS
    for (sx_, sy_) in ((46, 56), (854, 56), (46, 136), (854, 136)): dome(sx_, sy_, 6, 2.0)
    for (a, b) in ((58, 228), (672, 842)): frame(a, 160, b, 290, 8, 5.0, rad=6)   # the VU meters
    for (c, d) in ((162, 208), (216, 262), (270, 316)): key(525, c, 647, d, 6.0, rad=3)  # the program keys
    key(254, 288, 345, 304, 2.5, rad=6); key(254, 309, 345, 325, 2.5, rad=6)  # Vibrato, Preamp
    for xx in (107, 205, 303, 401, 499, 597, 695, 793): key(xx - 29, 504, xx + 29, 521, 2.0, rad=2)   # the value boxes
    for (sx_, sy_) in ((46, 543), (854, 543)): dome(sx_, sy_, 6, 2.0)

# ---------- the rack: ears, handles, crinkle chassis (the Noir rack shots, scaled to this face) ----------
U = W / 1280.0                                 # the Noir rack's parts were sized for a 1280 px face
EAR, CD = 0.78 * U, 13.0 * U
M_PLATE = mat("lacquer", (0.010, 0.010, 0.013), rough=0.4, coat=1.0, coat_rough=0.07)
M_TRIM = mat("trim", (0.80, 0.62, 0.36), metal=1.0, rough=0.25) if SKIN == "fantasy" else mat("trim", (0.9, 0.9, 0.92), metal=1.0, rough=0.14)
M_CHROME = mat("chrome", (0.9, 0.9, 0.92), metal=1.0, rough=0.12); M_HOLE = mat("hole", (0, 0, 0), rough=0.9); M_RUBBER = mat("rubber", (0.01, 0.01, 0.01), rough=0.8)
M_CRINKLE = mat("crinkle", (0.010, 0.010, 0.011), rough=0.55)
nt = M_CRINKLE.node_tree; bs = nt.nodes["Principled BSDF"]
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 260; nz.inputs["Detail"].default_value = 6
bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.35
nt.links.new(nz.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], bs.inputs["Normal"])
def cyl(r, dd, loc, rot=(0, 0, 0), m=None, v=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=dd, location=loc, rotation=rot); o = bpy.context.object
    if m: o.data.materials.append(m)
    smooth(o); return o
for sx in (-1, 1):
    ex = sx * (PW / 2 + EAR / 2 - 0.01)
    ear = box(ex, 0, EAR, PH, -0.2, 0.0); ear.data.materials.append(M_PLATE); bevel(ear, 0.03 * U, 3, 40)
    for hy in (-PH / 2 + 0.8 * U * 1.4, PH / 2 - 0.8 * U * 1.4):
        slot = box(ex, hy, 0.46 * U, 0.2 * U, -0.05, 0.001); slot.data.materials.append(M_HOLE); bevel(slot, 0.09 * U, 6, 30)
        hd = cyl(0.15 * U, 0.09 * U, (ex, hy, 0.045 * U), m=M_CHROME); bevel(hd, 0.05 * U, 6)
    hx = sx * (PW / 2 + EAR * 0.45); L = PH * 0.55; OUTZ = 1.05 * U
    for hy in (-L / 2, L / 2):
        cyl(0.13 * U, OUTZ, (hx, hy, OUTZ / 2), m=M_TRIM); cyl(0.2 * U, 0.08 * U, (hx, hy, 0.04 * U), m=M_TRIM)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=0.13 * U, location=(hx, hy, OUTZ))
        bpy.context.object.data.materials.append(M_TRIM); smooth(bpy.context.object)
    cyl(0.13 * U, L, (hx, 0, OUTZ), rot=(math.pi / 2, 0, 0), m=M_TRIM)
CW, CH = PW - 0.25 * U, PH - 0.3 * U
chs = box(0, 0, CW, CH, -0.2 - CD, -0.2); chs.data.materials.append(M_CRINKLE); bevel(chs, 0.05 * U, 4, 40)
TOPY = CH / 2
for row in range(3):
    zc = -0.2 - CD * (0.17 + row * 0.28)
    for i in range(18):
        x = -CW / 2 + 0.9 * U + i * (CW - 1.8 * U) / 17
        s = box(x, TOPY - 0.03 * U, 0.12 * U, 0.08 * U, zc - 1.2 * U, zc + 1.2 * U); s.data.materials.append(M_HOLE); bevel(s, 0.05 * U, 4, 30)
for sx in (-1, 1):
    for z in (-1.4 * U, -0.2 - CD + 1.2 * U):
        cyl(0.42 * U, 0.22 * U, (sx * (CW / 2 - 1.2 * U), -CH / 2 - 0.11 * U, z), rot=(math.pi / 2, 0, 0), m=M_RUBBER)

# ---------- light and room (the Noir rack shots' studio) ----------
K.room_and_lights(os.environ.get("ROOM", r"D:\AI\Galana\tools\noir\noir_room.png"), 4.0 * U, (1.0, 0.8, 0.62))
for o in bpy.data.objects:
    if o.type != "LIGHT": continue
    o.visible_camera = False
    if o.data.name == "cool": o.data.energy = 0
    if o.data.name == "key": o.location = (-7 * U, 9 * U, 9 * U); o.data.energy = 900 * U * U; o.rotation_euler = (math.radians(-35), math.radians(-25), 0)
for o in bpy.data.objects:
    if o.active_material is not None and o.active_material.name == "room": o.active_material.node_tree.nodes["Emission"].inputs["Strength"].default_value = 0.35

rig = bpy.data.objects.new("rig", None); bpy.context.collection.objects.link(rig)
for o in list(bpy.data.objects):
    if o is not rig and o.parent is None: o.parent = rig
rig.rotation_euler = (math.pi / 2, 0, 0)
FLOOR = -CH / 2 - 0.22 * U
rig.location = (0, 0, -FLOOR)
# the desk (owner 2026-11-25: a black void under the rack read as unreal): dark oiled oak, long fibres along X, a soft sheen
M_GROUND = bpy.data.materials.new("ground"); M_GROUND.use_nodes = True; _dt = M_GROUND.node_tree; _db = _dt.nodes["Principled BSDF"]
_nz = _dt.nodes.new("ShaderNodeTexNoise"); _nz.inputs["Scale"].default_value = 1.0; _nz.inputs["Detail"].default_value = 12.0; _nz.inputs["Roughness"].default_value = 0.62
_tc = _dt.nodes.new("ShaderNodeTexCoord"); _mp = _dt.nodes.new("ShaderNodeMapping"); _mp.inputs["Scale"].default_value = (0.16, 4.5, 1.0)
_dt.links.new(_tc.outputs["Object"], _mp.inputs["Vector"]); _dt.links.new(_mp.outputs["Vector"], _nz.inputs["Vector"])
_cr = _dt.nodes.new("ShaderNodeValToRGB"); _cr.color_ramp.elements[0].color = (0.005, 0.003, 0.002, 1); _cr.color_ramp.elements[1].color = (0.020, 0.012, 0.008, 1)
_dt.links.new(_nz.outputs["Fac"], _cr.inputs["Fac"]); _dt.links.new(_cr.outputs["Color"], _db.inputs["Base Color"])
_db.inputs["Roughness"].default_value = 0.6; _db.inputs["Specular IOR Level"].default_value = 0.25   # matte enough that no softbox mirrors in it
bpy.ops.mesh.primitive_plane_add(size=300, location=(0, 0, 0)); bpy.context.object.data.materials.append(M_GROUND)
def warea(name, loc, size, power, color, target=(0, 6, 3)):
    loc = tuple(v * U for v in loc); target = tuple(v * U for v in target)
    dl = bpy.data.lights.new(name, "AREA"); dl.shape = "RECTANGLE"; dl.size = size[0] * U; dl.size_y = size[1] * U; dl.energy = power * U * U; dl.color = color
    o = bpy.data.objects.new(name, dl); o.location = loc; bpy.context.collection.objects.link(o); o.visible_camera = False
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); return o
warea("top", (0, 6, 16), (16, 10), 2000, (1.0, 0.93, 0.85))
warea("rimR", (16, 18, 7), (2, 9), 900, (1.0, 0.75, 0.65))
warea("rimL", (-16, 14, 5), (2, 7), 350, (0.6, 0.75, 1.0))
# the rims and the lid softbox light the rack only: on the desk the softbox threw the rack's shadow forward with a hard far edge
_desk = bpy.data.collections.new("desk_only")
for _o in bpy.data.objects:
    if _o.type == "MESH" and _o.active_material is not None and _o.active_material.name == "ground": _desk.objects.link(_o)
for _o in bpy.data.objects:
    if _o.type == "LIGHT" and _o.name in ("rimR", "rimL", "top"):
        _o.light_linking.receiver_collection = _desk
        for _c in _desk.collection_objects: _c.light_linking.link_state = "EXCLUDE"
sc.view_settings.exposure = float(os.environ.get("EXPOSURE", "0.35"))
def card(loc, size, strength, warm=(1.0, 0.9, 0.78)):
    loc = tuple(v * U for v in loc)
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc); c = bpy.context.object; c.scale = (size[0] * U, size[1] * U, 1)
    c.rotation_euler = (math.pi / 2, 0, math.atan2(-loc[0], -loc[1]) if loc[1] else 0)
    m = bpy.data.materials.new("card"); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs[0].default_value = (*warm, 1); e.inputs[1].default_value = strength
    o = nt.nodes.new("ShaderNodeOutputMaterial"); lp_ = nt.nodes.new("ShaderNodeLightPath"); tr_ = nt.nodes.new("ShaderNodeBsdfTransparent"); mx_ = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp_.outputs["Is Glossy Ray"], mx_.inputs[0]); nt.links.new(tr_.outputs[0], mx_.inputs[1]); nt.links.new(e.outputs[0], mx_.inputs[2])
    nt.links.new(mx_.outputs[0], o.inputs[0]); c.data.materials.append(m)
    c.visible_camera = False; c.visible_diffuse = False; c.visible_shadow = False; return c
card((-9, -15, 9), (11, 7), 8.0); card((12, -12, 5), (4, 10), 5.0, (0.8, 0.88, 1.0))
# (the reflector card that lay on the table is gone: on the oak desk it showed as a hard-edged lighter patch)
wn = sc.world.node_tree; N = wn.nodes; Lk = wn.links
bg = N["Background"]; lp = N.new("ShaderNodeLightPath"); env = N.new("ShaderNodeBackground"); env.inputs[0].default_value = (0.55, 0.45, 0.36, 1)
mxw = N.new("ShaderNodeMixShader"); Lk.new(lp.outputs["Is Glossy Ray"], mxw.inputs[0]); Lk.new(bg.outputs[0], mxw.inputs[1]); Lk.new(env.outputs[0], mxw.inputs[2])
Lk.new(mxw.outputs[0], N["World Output"].inputs["Surface"])
tcw = N.new("ShaderNodeTexCoord"); spw = N.new("ShaderNodeSeparateXYZ"); mrw = N.new("ShaderNodeMapRange")
mrw.inputs["From Min"].default_value = -0.6; mrw.inputs["From Max"].default_value = 0.9; mrw.inputs["To Min"].default_value = 0.06; mrw.inputs["To Max"].default_value = 0.35
Lk.new(tcw.outputs["Generated"], spw.inputs[0]); Lk.new(spw.outputs["Z"], mrw.inputs["Value"]); Lk.new(mrw.outputs["Result"], env.inputs[1])

# ---------- camera ----------
cd = bpy.data.cameras.new("cam"); cd.dof.use_dof = True
cam = bpy.data.objects.new("cam", cd); bpy.context.collection.objects.link(cam); sc.camera = cam
CZ = -FLOOR
if SHOT == "hero":
    cd.lens = 50; cam.location = Vector((-17.0 * U, -29.0 * U, 14.0 * U)); target = Vector((0.6 * U, 2.0 * U, CZ - 0.3 * U)); cd.dof.aperture_fstop = 8
else:
    cd.lens = 40; cam.location = Vector((17.0 * U, -24.0 * U, 5.0 * U)); target = Vector((-0.6 * U, 2.0 * U, CZ + 0.3 * U)); cd.dof.aperture_fstop = 8
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
cd.dof.focus_distance = (target - cam.location).length

sc.render.engine = "CYCLES"; sc.cycles.samples = HSAMP; sc.cycles.use_denoising = True; sc.cycles.use_adaptive_sampling = True
sc.cycles.sample_clamp_indirect = 3.0
sc.cycles.device = "CPU"; sc.render.threads_mode = "FIXED"; sc.render.threads = 4
if os.environ.get("CYCLES_DEVICE") == "GPU":
    cp = bpy.context.preferences.addons["cycles"].preferences; cp.compute_device_type = "OPTIX"; cp.get_devices()
    for dv in cp.devices: dv.use = dv.type == "OPTIX"
    sc.cycles.device = "GPU"
sc.render.resolution_x, sc.render.resolution_y = RX, RY; sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
sc.render.filepath = HOUT
bpy.ops.render.render(write_still=True)
