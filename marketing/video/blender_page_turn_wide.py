#!/usr/bin/env python3
"""blender_page_turn_wide.py — the 16:9 variant of blender_page_turn.py.

Same rolling-page model, generalized from the square: the sheet spans
x in [-W/2, W/2] with W = 16/9, the ortho camera covers exactly that width
(ortho_scale = W * margin), the bed is a W x 1.0 plane so the incoming 16:9 art
fills the frame exactly, and UVs are remapped u = (x + W/2) / W.

Run: blender -b --python blender_page_turn_wide.py -- \
        --from art_a.png --to art_b.png --outdir /tmp/turnw \
        --frames 22 --height 1080 --curl 0.13 --samples 20
Output: <outdir>/page_####.png + shadow_####.png (RGBA), same contract as the
square version (compose via compose_turn_wide.py).
"""
import math
import os
import sys

import bpy
import numpy as np


def argv():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = {}
    i = 0
    while i < len(a):
        if a[i].startswith("--"):
            out[a[i][2:]] = a[i + 1] if i + 1 < len(a) and not a[i + 1].startswith("--") else "1"
            i += 2
        else:
            i += 1
    return out


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def image_material(name, path, paper=False):
    """Simple, robust: the illustration on BOTH sides, dimmed as the surface turns
    away. The art/paper Backfacing branch was tried and abandoned — both flip states
    rendered the paper branch and the page came out blank white, wasting two 20-min
    renders. For a ~1s transition the paper back is invisible anyway."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(path)
    tex.extension = "EXTEND"
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    nt.links.new(lw.outputs["Facing"], inv.inputs[1])
    cap = nt.nodes.new("ShaderNodeMath"); cap.operation = "MULTIPLY"
    cap.inputs[1].default_value = 0.55
    nt.links.new(inv.outputs[0], cap.inputs[0])
    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "MIX"
    nt.links.new(cap.outputs[0], mix.inputs["Fac"])
    nt.links.new(tex.outputs["Color"], mix.inputs["Color1"])
    mix.inputs["Color2"].default_value = (0.35, 0.30, 0.25, 1.0)
    emis = nt.nodes.new("ShaderNodeEmission")
    emis.inputs["Strength"].default_value = 1.0
    nt.links.new(mix.outputs["Color"], emis.inputs["Color"])
    outn = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(emis.outputs["Emission"], outn.inputs["Surface"])
    return m


NX, NY = 260, 40


def bake_uvs(me, orig, W):
    flip = True
    if "UVMap" not in me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uv = me.uv_layers["UVMap"]
    for loop in me.loops:
        x, y, _ = orig[loop.vertex_index]
        uv.data[loop.index].uv = ((x + W / 2) / W, (0.5 - y) if flip else (y + 0.5))


def roll_geometry(me, p, W=16/9, R=0.13, nx=NX, ny=NY, y_half=0.58):
    """Rolling page generalized to width W: roll centre c runs from +W/2 to
    -(W/2 + 2R); flat part spans [-W/2, c]; wrap continues past c."""
    pe = p * p * (3 - 2 * p)
    c = W / 2 - (W + 2 * R) * pe
    flat_len = max(0.0, c + W / 2)
    L = W / 2 - flat_len + W / 2          # total wrapped length so far
    s = np.linspace(0.0, W, nx)
    on_flat = s <= flat_len
    a = np.clip(s - flat_len, 0.0, None)
    ang = -math.pi / 2 + a / R
    x = np.where(on_flat, -W / 2 + s, c + R * np.cos(ang))
    z = np.where(on_flat, 0.0, R + R * np.sin(ang))
    for j, yy in enumerate(np.linspace(y_half, -y_half, ny)):
        for i in range(nx):
            me.vertices[j * nx + i].co = (x[i], yy, z[i])


def main():
    A = argv()
    src = A["from"]
    dst = A["to"]
    outdir = A.get("outdir", "/tmp/turnw")
    nframes = int(A.get("frames", 22))
    height = int(A.get("height", 1080))
    curl = float(A.get("curl", 0.13))
    samples = int(A.get("samples", 24))
    W = 16 / 9
    os.makedirs(outdir, exist_ok=True)

    clear()
    sc = bpy.context.scene

    # bed: W x 1.0 plane -> its default UVs show the 16:9 art across exactly the frame
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, -0.002))
    bed = bpy.context.object
    bed.name = "bed"
    bed.scale = (W, 1.0, 1.0)
    bed.data.materials.append(image_material("m_bed", dst))

    bpy.ops.mesh.primitive_grid_add(x_subdivisions=NX - 1, y_subdivisions=NY - 1, size=1.0)
    page = bpy.context.object
    page.name = "page"
    page.rotation_euler = (0, 0, 0)
    orig = [v.co.copy() for v in page.data.vertices]
    if len(orig) != NX * NY:
        raise SystemExit(f"grid has {len(orig)} verts, expected {NX*NY}")
    import bmesh
    if os.environ.get("TURN_NOFLIP", "0") != "1":
        bm = bmesh.new()
        bm.from_mesh(page.data)
        for f in bm.faces:
            f.normal_flip()
        bm.to_mesh(page.data)
        bm.free()
        page.data.update()
    bake_uvs(page.data, orig, W)
    page.data.materials.append(image_material("m_page", src))

    bpy.ops.mesh.primitive_plane_add(size=3.0, location=(0, 0, -0.004))
    catcher = bpy.context.object
    catcher.name = "catcher"
    catcher.is_shadow_catcher = True

    pitch = math.radians(9)
    dcam = 2.0
    cam_data = bpy.data.cameras.new("cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = W * 1.02
    cam = bpy.data.objects.new("cam", cam_data)
    cam.location = (0, -dcam * math.sin(pitch), dcam * math.cos(pitch))
    sc.collection.objects.link(cam)
    target = bpy.data.objects.new("cam_target", None)
    sc.collection.objects.link(target)
    track = cam.constraints.new("TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"
    sc.camera = cam

    ld = bpy.data.lights.new("key", type="AREA")
    ld.size = 2.6
    ld.energy = 300.0
    lo = bpy.data.objects.new("key", ld)
    lo.location = (-0.55, 0.35, 1.4)
    lo.rotation_euler = (math.radians(38), 0, math.radians(-22))
    sc.collection.objects.link(lo)

    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x = int(height * W)
    sc.render.resolution_y = height
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"

    bed.hide_render = True
    if os.environ.get("TURN_HIDEPAGE") == "1":
        page.hide_render = True
    if os.environ.get("TURN_HIDECATCHER") == "1":
        catcher.hide_render = True
    for f in range(1, nframes + 1):
        p = (f - 1) / (nframes - 1)
        roll_geometry(page.data, p, W=W, R=curl)
        page.data.update()
        sc.frame_set(f)
        catcher.hide_render = True
        sc.render.filepath = os.path.join(outdir, f"page_{f:04d}")
        bpy.ops.render.render(write_still=True)
        catcher.hide_render = False
        sc.render.filepath = os.path.join(outdir, f"shadow_{f:04d}")
        bpy.ops.render.render(write_still=True)

    print(f"rendered {nframes} frames -> {outdir}")


if __name__ == "__main__":
    main()
