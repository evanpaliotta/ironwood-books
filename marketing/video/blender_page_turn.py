#!/usr/bin/env python3
"""
blender_page_turn.py — a photoreal page turn rendered headlessly by Blender.

Run:  blender -b --python blender_page_turn.py -- \
          --from art_a.png --to art_b.png --outdir /tmp/turn \
          --frames 22 --height 1080 --curl 0.13 --samples 24

WHY: the numpy version (page_turn.py) computes the right geometry but reads as
flat cardboard — no real lighting, no soft shadow, no paper thickness. Blender is
free, runs with -b (no GUI, ever), and gives all three. The GRID here is still our
own physics: the sheet is hinged at the spine and rotates 0..180 deg with a
semicircular curl, extruded in Y and rendered with Cycles.

Two render layers, because the ends must stay EXACT art:
  - "page":  the sheet, an EMISSION surface so the illustration is reproduced
             faithfully, dimmed by its own angle to camera so the curl still reads
             as a rounded surface (factor is exactly 1.0 when flat -> frame 0 is
             the untouched illustration).
  - "shadow": a shadow-catcher plane that catches only the light the lifting sheet
             blocks. Composited in Python over the incoming art, so the last frame
             is the untouched incoming illustration.

Output: <outdir>/page_####.png and <outdir>/shadow_####.png (RGBA), which
compose_turn.py turns into the final mp4.
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
    """ONE material that shows ART when the face is front-facing and PAPER when it
    is backfacing — the physical page, with no Solidify shell to get the direction
    of wrong. The art is EMISSION so the illustration is reproduced faithfully, and
    a Layer-Weight term dims it as the surface turns away (exactly 1.0 when flat,
    so frame 0 is the untouched illustration)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    # shading (multiply by the Facing ramp) happens AFTER the front/back mix, so
    # the paper back of the rolled page also gets cylindrical shading — before
    # this, the roll rendered as a flat white band.
    mix_shade = nt.nodes.new("ShaderNodeMixRGB")
    mix_shade.blend_type = "MULTIPLY"
    mix_shade.inputs["Fac"].default_value = 1.0
    emis = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(mix_shade.outputs["Color"], emis.inputs["Color"])
    nt.links.new(emis.outputs["Emission"], out.inputs["Surface"])

    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.45, 0.45, 0.50, 1)   # edge-on: dark
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (1, 1, 1, 1)            # facing camera: full
    nt.links.new(lw.outputs["Facing"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], mix_shade.inputs["Color2"])

    art = nt.nodes.new("ShaderNodeTexImage")
    art.image = bpy.data.images.load(path)
    art.interpolation = "Closest"
    paper = nt.nodes.new("ShaderNodeMixRGB")
    paper.blend_type = "MIX"
    paper.inputs["Fac"].default_value = 1.0
    paper.inputs["Color1"].default_value = (0.955, 0.945, 0.90, 1.0)
    paper.inputs["Color2"].default_value = (0.90, 0.885, 0.83, 1.0)
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    nt.links.new(geo.outputs["Backfacing"], paper.inputs["Fac"])
    # front face = the illustration, back face = paper; both then get shaded
    nt.links.new(art.outputs["Color"], paper.inputs["Color1"])
    nt.links.new(paper.outputs["Color"], mix_shade.inputs["Color1"])
    return m


NX, NY = 180, 40


def bake_uvs(me, orig):
    """UVs from the ORIGINAL flat positions, so the illustration stays glued to the
    sheet as it deforms. Grid primitives cannot be trusted to have usable UVs, and
    without them an Image Texture samples one point of the art and the whole page
    renders as a flat colour.

    The v axis is FLIPPED (v = 0.5 - y): measured with v = y + 0.5, the render came
    out as the illustration mirrored top-to-bottom (the diff map was a moth —
    symmetric about the horizontal centre line). Blender's image texture has v=0 at
    the BOTTOM, and the ortho top-down camera's frame up-direction turned out to
    oppose the mesh's +Y, so v tracks 0.5 - y.
    """
    import os

    flip = os.environ.get("TURN_UV_FLIP", "1") == "1"
    if "UVMap" not in me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uv = me.uv_layers["UVMap"]
    for loop in me.loops:
        x, y, _ = orig[loop.vertex_index]
        uv.data[loop.index].uv = (x + 0.5, (0.5 - y) if flip else (y + 0.5))


def roll_geometry(me, p, W=1.0, R=0.10, nx=NX, ny=NY, y_half=0.58):
    """THE ROLLING PAGE (the model that actually works in a full-frame video):

    a cylinder of radius R rests on the bed at x=c and travels right->left; the
    page wraps around it (art inward, so the roll's visible outside is the paper
    back), the flat part still lying on the bed shrinks ahead of it, and the NEXT
    page is revealed behind it (x > c + R). At p=0 the roll sits at the right
    edge with zero wrap = the untouched illustration; at p=1 the roll has exited
    the left edge = the untouched incoming illustration. In-frame throughout.

      flat part  s in [0, flat_len]:  x = -0.5 + s,          z = 0
      wrap       a = s - flat_len:    angle = -pi/2 + a/R
                                      pos = (c + R cos(angle), R + R sin(angle))
    with flat_len = c + 0.5 and c = 0.5 - (1 + 2R) * ease(p).

    Continuity is exact: the flat part ends at x = c, the cylinder's bottom
    contact point, and both tangents there point +x.

    The sheet is TALLER than the frame (y_half 0.58 > 0.5) with the UV clamping at
    the art's edge: with the camera tilted, a 1.0-tall sheet would open slivers of
    the bed at the frame's top/bottom mid-turn.
    """
    pe = p * p * (3 - 2 * p)                     # ease-in-out
    c = 0.5 - (1.0 + 2 * R) * pe                 # roll centre x: 0.5 -> -(0.5+2R)
    flat_len = max(0.0, c + 0.5)                 # page still lying on the bed
    L = W - flat_len                             # length already wrapped
    wrap = L / R                                 # wrap angle (may exceed 2pi: layers)

    s = np.linspace(0.0, W, nx)
    on_flat = s <= flat_len
    a = np.clip(s - flat_len, 0.0, None)         # arc length into the wrap
    ang = -math.pi / 2 + a / R
    x = np.where(on_flat, -0.5 + s, c + R * np.cos(ang))
    z = np.where(on_flat, 0.0, R + R * np.sin(ang))

    for j, yy in enumerate(np.linspace(y_half, -y_half, ny)):
        for i in range(nx):
            me.vertices[j * nx + i].co = (x[i], yy, z[i])


def main():
    A = argv()
    src = A["from"]
    dst = A["to"]
    outdir = A.get("outdir", "/tmp/turn")
    nframes = int(A.get("frames", 22))
    res = int(A.get("height", 1080))
    curl = float(A.get("curl", 0.13))
    samples = int(A.get("samples", 24))
    os.makedirs(outdir, exist_ok=True)

    clear()
    sc = bpy.context.scene

    # ---- the incoming page, flat in the bed (exact art, unlit emission)
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, -0.002))
    bed = bpy.context.object
    bed.name = "bed"
    bed.data.materials.append(image_material("m_bed", dst))

    # ---- the sheet: grid + solidify so its edge shows as paper.
    # Subdivisions must be (NX-1, NY-1): a grid with x_subdivisions=N has N+1
    # vertices across, and curl_geometry writes exactly NX x NY vertices.
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=NX - 1, y_subdivisions=NY - 1, size=1.0)
    page = bpy.context.object
    page.name = "page"
    page.rotation_euler = (0, 0, 0)
    orig = [v.co.copy() for v in page.data.vertices]   # flat-sheet positions
    if len(orig) != NX * NY:
        raise SystemExit(f"grid has {len(orig)} verts, expected {NX*NY}")
    # The grid's faces face DOWN (-Z): rendered from above, the visible face is
    # backfacing, so the paper branch of the material wins and frame 0 is a blank
    # cream page (measured: uniform rgb, std 0). Flip the normals FIRST, then bake
    # UVs — flipping reverses loop order and would misassign already-baked UVs.
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(page.data)
    for f in bm.faces:
        f.normal_flip()
    bm.to_mesh(page.data)
    bm.free()
    page.data.update()
    bake_uvs(page.data, orig)
    page.data.materials.append(image_material("m_page", src))

    # ---- shadow catcher: catches only what the lifting sheet blocks
    bpy.ops.mesh.primitive_plane_add(size=3.0, location=(0, 0, -0.004))
    catcher = bpy.context.object
    catcher.name = "catcher"
    catcher.is_shadow_catcher = True

    # ---- camera: orthographic, tilted ~9 deg so the roll gets parallax (a perfect
    # top-down view turns the cylinder into a flat band — the complaint that
    # started this iteration). It must STILL centre on the sheet: an offset tilt
    # slid the frame's centre 0.32 off the origin and the incoming page showed at
    # the frame's bottom. So: position on a 9-deg cone aimed at the origin, plus a
    # TRACK_TO constraint to guarantee it.
    pitch = math.radians(9)
    d = 2.0
    cam_data = bpy.data.cameras.new("cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 1.02
    cam = bpy.data.objects.new("cam", cam_data)
    cam.location = (0, -d * math.sin(pitch), d * math.cos(pitch))
    sc.collection.objects.link(cam)
    target = bpy.data.objects.new("cam_target", None)
    sc.collection.objects.link(target)
    track = cam.constraints.new("TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"
    sc.camera = cam

    # ---- light: big soft area, upper left, so the shadow is soft and believable
    ld = bpy.data.lights.new("key", type="AREA")
    ld.size = 2.2
    ld.energy = 260.0
    lo = bpy.data.objects.new("key", ld)
    lo.location = (-0.55, 0.35, 1.4)
    lo.rotation_euler = (math.radians(38), 0, math.radians(-22))
    sc.collection.objects.link(lo)

    # ---- render settings: Cycles, transparent film, STANDARD transform (no filmic
    # tone mapping — that would shift the illustration's colors)
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x = res
    sc.render.resolution_y = res
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"

    # Two passes per frame by toggling hide_render (view layers are overkill and
    # their API churns between Blender versions):
    #   page pass  -> sheet only, transparent elsewhere
    #   shadow pass-> catcher only, but the sheet must stay so it still occludes
    bed.hide_render = True
    for f in range(1, nframes + 1):
        p = (f - 1) / (nframes - 1)
        roll_geometry(page.data, p, W=1.0, R=curl)
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
