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

RIG = ("softbox", "card", "reflector", "lightcard", "cyc", "sweep")

# the unit: every rendered mesh near the camera's target that is not the room (desk, floor, walls) or the light rig. The target
# is where the camera's centre ray lands, often the desk in front of the unit, so the unit is found by kind, not by distance
ROOMN = tuple(os.environ.get("ENV_KEEP", "ground,desk,oak,floor,wall,room,backdrop").split(","))
def unit_objects(reach=float(os.environ.get("UNIT_REACH", "40"))):
    out = []
    for o in sc.objects:
        if o.type not in ("MESH", "CURVE", "FONT") or o.hide_render: continue
        mn = [m.name.lower() for m in getattr(o.data, "materials", []) if m]
        if any(n.startswith(k) for n in mn for k in ROOMN + RIG): continue
        c = sum((o.matrix_world @ Vector(b) for b in o.bound_box), Vector()) / 8
        if (c - target).length < reach: out.append(o)
    return out

# the pivot: the page turns the unit about the camera's target, so the target is moved along the centre ray (the framing does not
# change) to the point nearest the unit's centre; turning about the desk in front swung the unit half out of the frame
_u = unit_objects()
if _u and os.environ.get("PIVOT", "unit") == "unit":
    _lo = Vector([min((o.matrix_world @ Vector(b))[i] for o in _u for b in o.bound_box) for i in range(3)])
    _hi = Vector([max((o.matrix_world @ Vector(b))[i] for o in _u for b in o.bound_box) for i in range(3)])
    _t = max(1.0, (((_lo + _hi) / 2) - cam.matrix_world.translation).dot(fwd))
    print("HERO_PIVOT", round(dist, 2), "->", round(_t, 2))
    dist, target = _t, cam.matrix_world.translation + fwd * _t

# 2b. ENV=1: the environment the viewer lights metals with: an equirect HDR of this scene's lights and room, seen from the
# unit's centre with the unit hidden and the reflector cards made visible (they light the still only by reflection)
if os.environ.get("ENV") == "1":
    ex, ey = (int(v) for v in os.environ.get("ENV_RES", "2048x1024").split("x"))
    unit = unit_objects()
    lo = Vector([min((o.matrix_world @ Vector(b))[i] for o in unit for b in o.bound_box) for i in range(3)])
    hi = Vector([max((o.matrix_world @ Vector(b))[i] for o in unit for b in o.bound_box) for i in range(3)])
    centre = (lo + hi) / 2
    for o in unit: o.hide_render = True
    for o in sc.objects:                                                # the reflector cards light the still only by reflection
        mn = [m.name.lower() for m in getattr(o.data, "materials", []) if m] if o.type == "MESH" else []
        if any(n.startswith(r) for n in mn for r in RIG): o.visible_camera = True; o.hide_render = False
    pc = bpy.data.cameras.new("env"); pc.type = "PANO"; pc.panorama_type = "EQUIRECTANGULAR"
    po = bpy.data.objects.new("env", pc); sc.collection.objects.link(po)
    po.location = centre; po.rotation_euler = (math.radians(90), 0, math.radians(-90))     # glTF +z (the unit's front) at the map's centre
    sc.camera = po; sc.render.resolution_x, sc.render.resolution_y = ex, ey; sc.render.resolution_percentage = 100
    sc.render.engine = "CYCLES"; sc.cycles.samples = int(os.environ.get("ENV_SAMPLES", "128"))
    sc.render.image_settings.file_format = "HDR"; sc.render.filepath = os.path.splitext(OUT)[0] + "_env.hdr"
    sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"; sc.view_settings.exposure = 0
    _real_render(write_still=True)
    print("HERO_ENV", sc.render.filepath); sys.exit(0)

# 2c. PLATE=1: the still's own frame with the unit hidden (<out>_plate.png at the scene's resolution and colour settings). The
# page shows it under the model while the model is live, so a turned unit never uncovers the still's unit behind it
if os.environ.get("PLATE") == "1":
    unit = unit_objects()
    for o in unit: o.hide_render = True
    print("HERO_PLATE hidden", len(unit), "of", len(sc.objects), "shown:", sorted({m.name for o in sc.objects if o.type == "MESH" and not o.hide_render for m in o.data.materials if m}))
    if os.environ.get("PLATE_DRY"): sys.exit(0)
    sc.render.engine = "CYCLES"; sc.cycles.samples = int(os.environ.get("PLATE_SAMPLES", "128"))
    sc.render.image_settings.file_format = "PNG"; sc.render.filepath = os.path.splitext(OUT)[0] + "_plate.png"
    _real_render(write_still=True)
    print("HERO_PLATE", sc.render.filepath); sys.exit(0)

# 3. what to keep: meshes that render, near the unit; never the light rig (area-light cards, softboxes, reflectors)
KEEP_DIST = float(os.environ.get("KEEP_DIST", "60"))
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
# the kept meshes' modifiers are applied first: their boolean cutters are hidden objects about to be dropped, and a boolean
# without its cutter cuts nothing (the Limiter's VFD window and brass frame came out solid)
dg = bpy.context.evaluated_depsgraph_get()
for o in [o for o in sc.objects if o.type == "MESH" and o.modifiers and o not in drop]:
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
    o.modifiers.clear(); o.data = me
for o in drop: bpy.data.objects.remove(o, do_unlink=True)

# live parts (object or material name equal to a LIVE entry, ignoring Blender's .001 suffixes): renamed LIVE_<name> for the page's
# video swap; unlit, their image (the poster frame) as emission over a black base, so nothing lit shows under the video
base = lambda n: n.split(".")[0]
live_mats = {}
for o in sc.objects:
    m = o.active_material if o.type == "MESH" else None
    if m and not m.name.startswith("LIVE_") and (base(o.name) in LIVE or base(m.name) in LIVE):
        live_mats[m.name] = m.name = "LIVE_" + base(m.name)
for m in bpy.data.materials:
    if not m.name.startswith("LIVE_") or not m.use_nodes: continue
    nt = m.node_tree; im = next((n.image for n in nt.nodes if n.bl_idname == "ShaderNodeTexImage" and n.image), None)
    glow = max([n.inputs["Strength"].default_value for n in nt.nodes if n.bl_idname == "ShaderNodeEmission"] +
               [n.inputs["Emission Strength"].default_value for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"
                and n.inputs["Emission Strength"].default_value > 0] or [1.0])          # the scene's own glow (the VFD: 6.0)
    nt.nodes.clear()                                   # node references go stale as nodes go: rebuild from the image alone
    out = nt.nodes.new("ShaderNodeOutputMaterial"); b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tex = None
    if im: tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = im; tex.extension = "CLIP"
    nt.links.new(b.outputs[0], out.inputs["Surface"]); b.inputs["Base Color"].default_value = (0, 0, 0, 1)
    b.inputs["Roughness"].default_value = 1.0; b.inputs["Specular IOR Level"].default_value = 0.0
    if tex: nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = glow

# glass and see-through sheets (a transparent BSDF in a mix): glTF has no such mix, so a dark low-alpha blend that keeps a highlight
for m in bpy.data.materials:
    if not m.use_nodes or not any(n.bl_idname == "ShaderNodeBsdfTransparent" for n in m.node_tree.nodes): continue
    nt = m.node_tree; nt.nodes.clear()
    b = nt.nodes.new("ShaderNodeBsdfPrincipled"); out = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(b.outputs[0], out.inputs["Surface"])
    b.inputs["Base Color"].default_value = (0.01, 0.01, 0.012, 1); b.inputs["Roughness"].default_value = 0.06
    b.inputs["Alpha"].default_value = float(os.environ.get("GLASS_ALPHA", "0.22"))
    if hasattr(m, "surface_render_method"): m.surface_render_method = "BLENDED"
    m["hero_glass"] = True

# LIVE_CROP=<hero_frames.py's .crop.json>: the live parts' video holds only the crop of the full layer, so their UVs move onto it
crop = os.environ.get("LIVE_CROP")
if crop:
    cj = json.load(open(crop)); (cx0, cy0, cx1, cy1), (CW, CH) = cj["crop"], cj["size"]
    u0, u1, v0, v1 = cx0 / CW, cx1 / CW, 1 - cy1 / CH, 1 - cy0 / CH          # Blender UV: v up from the image's bottom
    done = set()
    for o in sc.objects:
        if o.type != "MESH" or o.data in done or not o.active_material or not o.active_material.name.startswith("LIVE_"): continue
        done.add(o.data)
        if len(o.data.vertices) == 4:
            # a layer plane: cut it down to the crop, so no part of it shows the video outside the crop (tiled, the turned model
            # showed a second display beside the first)
            uvl = o.data.uv_layers.active.data
            for li, lp in enumerate(o.data.loops):
                v = o.data.vertices[lp.vertex_index]; u = uvl[li].uv
                v.co.x = (u0 if u.x < 0.5 else u1) - 0.5; v.co.y = (v0 if u.y < 0.5 else v1) - 0.5
            for d in uvl: d.uv = (0.0 if d.uv.x < 0.5 else 1.0, 0.0 if d.uv.y < 0.5 else 1.0)
        else:
            for d in o.data.uv_layers.active.data: d.uv = ((d.uv.x - u0) / (u1 - u0), (d.uv.y - v0) / (v1 - v0))
        poster = os.path.splitext(crop)[0].removesuffix(".crop") + ".png"
        for n in o.active_material.node_tree.nodes:
            if n.bl_idname == "ShaderNodeTexImage" and os.path.exists(poster): n.image = bpy.data.images.load(poster); n.extension = "CLIP"

report = {"scene": os.path.basename(SCENE), "kept": [], "materials": {}}

# 4. bake (heavy; BAKE=1 only). One texture per material, not per object: every object of a bakeable material is joined into one
# mesh and unwrapped together. Bakeable: not live, not glass, not metal (a diffuse bake of metal is black; metals stay PBR and take
# their highlights from the viewer's environment map, rendered from this scene). The bake goes in as emission over a black base:
#   diffuse: the diffuse light (direct + indirect, colour) baked; roughness kept, so a dielectric highlight still moves as it turns
#   full:    everything baked (COMBINED), no highlight of its own
if BAKE:
    px = int(os.environ.get("BAKE_PX", "2048"))
    sc.render.engine = "CYCLES"; sc.cycles.samples = int(os.environ.get("BAKE_SAMPLES", "64"))
    sc.render.bake.margin = 8
    outdir = os.path.splitext(OUT)[0] + "_bake"; os.makedirs(outdir, exist_ok=True)
    # the live parts are out of the bake: lit surfaces right behind them (the Limiter's VFD floor) would keep a sharp copy of
    # the poster frame that the video then plays beside, a ghost display as the unit turns
    live_hidden = [o for o in sc.objects if o.active_material and o.active_material.name.startswith("LIVE_") and not o.hide_render]
    for o in live_hidden: o.hide_render = True
    for o in [o for o in sc.objects if o.type in ("CURVE", "FONT", "SURFACE", "META")]:    # text and curves to meshes (UVs)
        bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
        bpy.ops.object.convert(target="MESH")
    def principled(m):
        return m.node_tree.nodes.get("Principled BSDF") if m and m.use_nodes else None
    def bakeable(m):
        if not m or m.name.startswith("LIVE_") or m.get("hero_glass"): return False
        b = principled(m)
        if b and not b.inputs["Metallic"].is_linked and b.inputs["Metallic"].default_value >= 0.5: return False
        return True
    groups = {}
    for o in [o for o in sc.objects if o.type == "MESH"]:
        ms = {s.material for s in o.material_slots if s.material}
        if len(ms) == 1 and bakeable(next(iter(ms))): groups.setdefault(next(iter(ms)).name, []).append(o)
    report_bake = {}
    for mname, objs in groups.items():
        m = bpy.data.materials[mname]
        bpy.ops.object.select_all(action="DESELECT")
        for o in objs:
            if o.data.users > 1: o.data = o.data.copy()
            o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
        if len(objs) > 1: bpy.ops.object.join()
        o = bpy.context.view_layer.objects.active; o.name = "baked_" + mname
        while o.data.uv_layers: o.data.uv_layers.remove(o.data.uv_layers[0])          # a fresh unwrap for the bake only
        o.data.uv_layers.new(name="bake")
        bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.003)
        bpy.ops.object.mode_set(mode="OBJECT")
        img = bpy.data.images.new("bake_" + mname, px, px, float_buffer=True)
        n = m.node_tree.nodes.new("ShaderNodeTexImage"); n.image = img; m.node_tree.nodes.active = n
        # COMBINED in both modes, so lamps and other emitters keep their glow; diffuse leaves the highlights (glossy) and glass
        # (transmission) to the viewer, full bakes them as the render camera sees them
        bk = sc.render.bake
        bk.use_pass_direct = bk.use_pass_indirect = bk.use_pass_diffuse = bk.use_pass_emit = True
        bk.use_pass_glossy = bk.use_pass_transmission = MODE == "full"
        bk.view_from = "ACTIVE_CAMERA" if MODE == "full" else "ABOVE_SURFACE"
        bpy.ops.object.bake(type="COMBINED")
        img.filepath_raw = os.path.join(outdir, img.name + ".exr"); img.file_format = "OPEN_EXR"; img.save()
        # into 0..1 for an 8-bit texture: divide by the bright end, carried back as the emission strength
        # (glTF KHR_materials_emissive_strength), so baked light above 1 is not clipped
        import numpy as np
        pix = np.empty(px * px * 4, np.float32); img.pixels.foreach_get(pix); pix = pix.reshape(-1, 4)
        peak = max(1.0, float(np.percentile(pix[:, :3].max(1), 99.9)))
        lin = np.clip(pix[:, :3] / peak, 0, 1)                    # glTF reads emissive textures as sRGB: encode
        pix[:, :3] = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.power(lin, 1 / 2.4) - 0.055); pix[:, 3] = 1
        ldr = bpy.data.images.new("bake_" + mname + "_ldr", px, px); ldr.pixels.foreach_set(pix.ravel())
        ldr.filepath_raw = os.path.join(outdir, ldr.name + ".png"); ldr.file_format = "PNG"; ldr.save(); img = ldr
        b = principled(m); rough = b.inputs["Roughness"].default_value if b else 0.5
        nm = bpy.data.materials.new("baked_" + mname); nm.use_nodes = True; nt = nm.node_tree; bb = nt.nodes["Principled BSDF"]
        t = nt.nodes.new("ShaderNodeTexImage"); t.image = img
        nt.links.new(t.outputs["Color"], bb.inputs["Emission Color"]); bb.inputs["Emission Strength"].default_value = peak
        bb.inputs["Base Color"].default_value = (0, 0, 0, 1)
        bb.inputs["Roughness"].default_value = 1.0 if MODE == "full" else rough
        bb.inputs["Specular IOR Level"].default_value = 0.0 if MODE == "full" else 0.5
        o.data.materials.clear(); o.data.materials.append(nm)
        report_bake[mname] = {"objects": len(objs), "metallic": round(b.inputs["Metallic"].default_value, 3) if b else None, "peak": round(peak, 3)}
    skipped = sorted({o.name for o in sc.objects if o.type == "MESH" and not o.name.startswith("baked_")
                      and len({s.material for s in o.material_slots if s.material}) > 1})
    print("BAKED", len(groups), "materials:", report_bake, "| multi-material objects left unbaked:", skipped)
    report_baked, report_unbaked = report_bake, skipped
    for o in live_hidden: o.hide_render = False

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
if BAKE: report["baked"], report["multi_material_unbaked"] = report_baked, report_unbaked
report["glb_bytes"] = os.path.getsize(OUT)
json.dump(report, open(os.path.splitext(OUT)[0] + ".json", "w"), indent=1)
print("HERO_GLB", OUT, report["glb_bytes"], "bytes;", sum(v != "ok" and v != "plain" for v in report["materials"].values()), "materials lose detail")
