"""A hero scene as a real-time model for the front page's pointer-follow heroes.

Runs any hero scene script (tula_desk.py, lahari_rack.py, limiter_noir3d_rack.py, ...) with its render switched off, then
exports what the camera sees as a GLB plus <out>.json (the camera's position, target and field of view, so the page's rest
pose matches the still) and, with BAKE=1, bakes the scene's lighting into the textures first.

  blender -b -noaudio -t 4 -P hero_glb.py -- <scene.py> <out.glb> [args for the scene ...]

Env:
  BAKE=0|1        0 (default): export the scene's materials as they are (a quick check of what survives glTF).
                  1: Cycles-bake each kept object's look into a texture (needs the GPU and the render lock: a heavy job).
  BAKE_MODE       full: the whole look baked (unlit in the viewer, highlights fixed)
                  diffuse (default): colour and light baked; roughness and metal kept so the viewer's environment moves the
                  highlights as the unit turns
  BAKE_PX         texture size per object (default 1024; the face takes FACE_PX, default 2048)
  BAKE_SAMPLES    default 64
  LIVE            comma list of object-name prefixes that carry live video on the page (their material is renamed
                  LIVE_<n> and keeps its image as the poster frame; the page swaps a video into it)
  KEEP_DIST       objects whose bounds sit further than this from the camera's target are dropped (scene units, default 60)
  + whatever the scene script reads (CAP, LAYOUT, LAYERDIR, CYCLES_DEVICE, ...)
"""
import bpy, json, math, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
SCENE, OUT = os.path.abspath(argv[0]), os.path.abspath(argv[1])
SCENE_ARGS = argv[2:]
BAKE = os.environ.get("BAKE", "0") == "1"
MODE = os.environ.get("BAKE_MODE", "diffuse")
LIVE = [p for p in os.environ.get("LIVE", "").split(",") if p]

# 1. build the scene, its render switched off (the scripts end in bpy.ops.render.render; some exec others)
_real_render = bpy.ops.render.render
class _NoRender:
    def __call__(self, *a, **k): return {"FINISHED"}
    def __getattr__(self, n): return getattr(_real_render, n)
bpy.ops.render.render = _NoRender()
sys.argv = [sys.argv[0], "--", *SCENE_ARGS]
os.chdir(os.path.dirname(SCENE))
g = {"__file__": SCENE, "__name__": "__main__"}
exec(compile(open(SCENE, encoding="utf-8").read(), SCENE, "exec"), g)
bpy.ops.render.render = _real_render
sc = bpy.context.scene
cam = sc.camera

# 2. the camera: where the page's rest pose must sit
dg = bpy.context.evaluated_depsgraph_get()
fwd = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
# the target: the nearest surface straight ahead (the unit), else the focus distance
hit, loc, *_ = sc.ray_cast(dg, cam.matrix_world.translation, fwd)
dist = (loc - cam.matrix_world.translation).length if hit else (cam.data.dof.focus_distance or 10.0)
target = cam.matrix_world.translation + fwd * dist
asp = sc.render.resolution_x / sc.render.resolution_y
vfov = 2 * math.atan(math.tan(cam.data.angle_x / 2) / asp) if cam.data.sensor_fit != "VERTICAL" else cam.data.angle_y

# 3. what to keep: meshes that render, near the unit; never the light rig (area-light cards, softboxes, reflectors)
KEEP_DIST = float(os.environ.get("KEEP_DIST", "60"))
RIG = ("softbox", "card", "reflector", "lightcard", "cyc", "sweep")
drop = []
for o in list(sc.objects):
    if o.type in ("LIGHT", "LIGHT_PROBE", "SPEAKER"): continue
    if o.type == "CAMERA": continue
    if o.type not in ("MESH", "CURVE", "FONT", "SURFACE", "META"):
        continue
    mn = [m.name.lower() for m in getattr(o.data, "materials", []) if m]
    if o.hide_render or not o.visible_camera or any(n.startswith(r) for n in [o.name.lower(), *mn] for r in RIG):
        drop.append(o); continue
    c = sum((o.matrix_world @ Vector(b) for b in o.bound_box), Vector()) / 8
    if (c - target).length > KEEP_DIST: drop.append(o)
for o in drop: bpy.data.objects.remove(o, do_unlink=True)

# live parts (matched by object or material name): their material keeps its image (the poster frame) and is renamed LIVE_<name>
# for the page's video swap
live_mats = {}
for o in sc.objects:
    m = o.active_material if o.type == "MESH" else None
    if m and not m.name.startswith("LIVE_") and any(o.name.startswith(p) or m.name.startswith(p) for p in LIVE):
        live_mats[m.name] = m.name = "LIVE_" + m.name.split(".")[0]

# LIVE_CROP=<hero_frames.py's .crop.json>: the live parts' video holds only the crop of the full layer, so their UVs move onto it
crop = os.environ.get("LIVE_CROP")
if crop:
    cj = json.load(open(crop)); (cx0, cy0, cx1, cy1), (CW, CH) = cj["crop"], cj["size"]
    u0, u1, v0, v1 = cx0 / CW, cx1 / CW, 1 - cy1 / CH, 1 - cy0 / CH          # Blender UV: v up from the image's bottom
    done = set()
    for o in sc.objects:
        if o.type != "MESH" or o.data in done or not o.active_material or not o.active_material.name.startswith("LIVE_"): continue
        done.add(o.data)
        for d in o.data.uv_layers.active.data: d.uv = ((d.uv.x - u0) / (u1 - u0), (d.uv.y - v0) / (v1 - v0))
        poster = os.path.splitext(crop)[0].removesuffix(".crop") + ".png"
        for n in o.active_material.node_tree.nodes:
            if n.bl_idname == "ShaderNodeTexImage" and os.path.exists(poster): n.image = bpy.data.images.load(poster); n.extension = "CLIP"

report = {"scene": os.path.basename(SCENE), "kept": [], "dropped": [o for o in []], "materials": {}}

# 4. bake (heavy; BAKE=1 only)
if BAKE:
    px, fpx = int(os.environ.get("BAKE_PX", "1024")), int(os.environ.get("FACE_PX", "2048"))
    sc.render.engine = "CYCLES"; sc.cycles.samples = int(os.environ.get("BAKE_SAMPLES", "64"))
    sc.render.bake.margin = 8
    outdir = os.path.splitext(OUT)[0] + "_bake"; os.makedirs(outdir, exist_ok=True)
    meshes = [o for o in sc.objects if o.type in ("CURVE", "FONT", "SURFACE", "META")]
    for o in meshes:                                   # text and curves to meshes so they can carry UVs
        bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
        bpy.ops.object.convert(target="MESH")
    for o in [o for o in sc.objects if o.type == "MESH"]:
        if o.active_material and o.active_material.name.startswith("LIVE_"): continue
        me = o.data
        if not me.uv_layers:
            bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
            bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.004)
            bpy.ops.object.mode_set(mode="OBJECT")
        size = fpx if any(k in o.name.lower() for k in ("face", "panel", "plate")) else px
        img = bpy.data.images.new("bake_" + o.name, size, size, float_buffer=False)
        for m in [s.material for s in o.material_slots if s.material]:
            n = m.node_tree.nodes.new("ShaderNodeTexImage"); n.image = img; m.node_tree.nodes.active = n
        bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
        if MODE == "full":
            bpy.ops.object.bake(type="COMBINED")
        else:
            sc.render.bake.use_pass_direct = sc.render.bake.use_pass_indirect = sc.render.bake.use_pass_color = True
            bpy.ops.object.bake(type="DIFFUSE")
        img.filepath_raw = os.path.join(outdir, img.name + ".png"); img.file_format = "PNG"; img.save()
        # the object's new material: the bake as its colour (or as emission, unlit, for full)
        mats = [s.material for s in o.material_slots if s.material]
        rough = metal = 0.5
        for m in mats:
            b = m.node_tree.nodes.get("Principled BSDF")
            if b: rough = b.inputs["Roughness"].default_value; metal = b.inputs["Metallic"].default_value; break
        nm = bpy.data.materials.new("baked_" + o.name); nm.use_nodes = True; nt = nm.node_tree; b = nt.nodes["Principled BSDF"]
        t = nt.nodes.new("ShaderNodeTexImage"); t.image = img
        if MODE == "full":
            nt.links.new(t.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = 1.0
            b.inputs["Base Color"].default_value = (0, 0, 0, 1); b.inputs["Roughness"].default_value = 1.0
        else:
            nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
            b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
        o.data.materials.clear(); o.data.materials.append(nm)

# 5. what survives glTF: a Principled BSDF fed by image textures (or plain values); anything procedural is lost
def survives(m):
    if not m.use_nodes: return "plain"
    nodes = {n.bl_idname for n in m.node_tree.nodes}
    proc = nodes & {"ShaderNodeTexNoise", "ShaderNodeTexVoronoi", "ShaderNodeTexWave", "ShaderNodeTexMusgrave", "ShaderNodeMapRange",
                    "ShaderNodeNewGeometry", "ShaderNodeTexCoord", "ShaderNodeBump", "ShaderNodeMixShader", "ShaderNodeBsdfGlossy",
                    "ShaderNodeBsdfTransparent", "ShaderNodeFresnel", "ShaderNodeLayerWeight", "ShaderNodeValToRGB"}
    return "lost: " + ",".join(sorted(p.replace("ShaderNode", "") for p in proc)) if proc else "ok"
for o in sc.objects:
    if o.type != "MESH": continue
    report["kept"].append(o.name)
    for s in o.material_slots:
        if s.material: report["materials"][s.material.name] = survives(s.material)

bpy.ops.object.select_all(action="DESELECT")
for o in sc.objects:
    if o.type in ("MESH", "CAMERA"): o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True, export_cameras=True, export_lights=False,
                          export_apply=True, export_yup=True,
                          export_draco_mesh_compression_enable=os.environ.get("DRACO", "1") == "1", export_draco_mesh_compression_level=6, export_image_format="WEBP", export_jpeg_quality=82)

# glTF is y-up: (x, y, z) in Blender -> (x, z, -y)
yup = lambda v: [round(v.x, 5), round(v.z, 5), round(-v.y, 5)]
cp = cam.matrix_world.translation
off = cp - target
r = off.length
report["camera"] = {"position": yup(cp), "target": yup(target), "radius": round(r, 5),
                    "theta_deg": round(math.degrees(math.atan2(off.x, -off.y)), 3),          # model-viewer orbit: azimuth from +z (front)
                    "phi_deg": round(math.degrees(math.acos(max(-1, min(1, off.z / r)))), 3),   # polar angle from straight up
                    "vfov_deg": round(math.degrees(vfov), 4), "aspect": round(asp, 5),
                    "view_transform": sc.view_settings.view_transform, "look": sc.view_settings.look,
                    "exposure": sc.view_settings.exposure}
report["live"] = list(live_mats.values()) or [m for m in report["materials"] if m.startswith("LIVE_")]
report["bake"] = MODE if BAKE else "none"
report["glb_bytes"] = os.path.getsize(OUT)
json.dump(report, open(os.path.splitext(OUT)[0] + ".json", "w"), indent=1)
print("HERO_GLB", OUT, report["glb_bytes"], "bytes;", sum(v != "ok" and v != "plain" for v in report["materials"].values()), "materials lose detail")
