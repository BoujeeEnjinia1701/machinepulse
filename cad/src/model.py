"""MachinePulse parametric model (build123d), TRL 3, constructable design (MPL-DDR-003).

Run from the repo root:
    python cad/src/model.py            export STEP and STL into cad/step and cad/stl
    python cad/src/model.py --check    run the constructability checks (contacts and clearances)

Exports:
    machinepulse-assembly.step / .stl   pod, current transformer and probe as installed
    machinepulse-pod.step / .stl        the magnetic sensor pod on its own
    sensor-block.step / .stl            aluminium sensor block with its boss screwed on

Axes: the pod sits on the top line of a horizontal motor frame. The magnet contact line is
the X axis at z = 0, X runs along the motor shaft, Z is up, and the motor axis is at
z = -motor_r. Keeping the pod at the origin lets the kit's cutaway cutter pass through it.

Constructable level of detail (STANDARDS section 18): every part has a stated process and a
fixing. The sensor block is a drilled and tapped plate; the boss is a separate piece of round
bar screwed to it with a set screw over magnet 1; the box base carries its moulded corner
pillars, three gland holes, the boss hole and the screw holes; one carrier perfboard on four
stand-offs holds the interface circuit and the controller in header sockets; a light pipe takes
the status LED to the lid; a silicone grommet seals the boss hole; the probe clip is a made
aluminium block that holds the sleeve on its thermal pad against the frame. Not for fabrication.
The same PARAMS feed docs/04-calcs/sizing.py (MPL-CAL-001), drawing MPL-DWG-001
(cad/src/sheets.py) and the build plan pictures (cad/src/build_plan_media.py).
"""
import sys
from pathlib import Path

# Top-level parameters (mm). Edit these, not the geometry below.
PARAMS = {
    # 6 pot magnets: 32 mm high-temperature neodymium pot magnets with M6 studs, spaced along X
    # (rated 120 degC; MPL-DDR-002 N1). Studs trimmed to 5 mm and screwed into the block.
    "mag_d": 32.0, "mag_h": 8.0, "mag_pitch": 40.0, "mag_t_max": 120.0, "stud_len": 5.0,
    # 5 aluminium sensor block (plate) and boss (round bar), joined by an M6 x 12 set screw
    "block": (76.0, 36.0, 10.0), "boss_d": 20.0, "boss_x": -20.0,   # boss directly above magnet 1
    "boss_above_floor": 3.5,                                         # boss top above the inside floor
    "boss_tap_depth": 8.0, "set_screw_len": 12.0,
    # 13 insulating stand-offs: nylon, between block and box floor (thermal break, MPL-CAL-001 G)
    "standoff_h": 5.0, "standoff_d": 6.0, "standoff_xy": (33.0, 13.0),
    # 1, 2 stock IP54 ABS box: outer size, base and lid heights, wall, moulded corner pillars
    "box": (100.0, 68.0, 40.0), "lid_h": 12.0, "wall": 2.5, "pillar_d": 7.0,
    "floor_hole_d": 24.0,                  # clearance hole round the boss, sealed by a silicone grommet
    # 12 silicone grommet in the floor hole: bore, body, flange diameter, flange thickness
    "grommet": (20.0, 24.0, 28.0, 1.0),
    # 2 cable glands: name -> (end of the box, y, thread, hole, outside body d, body length, nut across flats)
    "glands": {"ct": (+1, 0.0, "M16", 16.2, 20.0, 20.0, 20.0),
               "probe": (-1, 13.0, "M12", 12.2, 15.0, 17.0, 15.0),
               "power": (-1, -13.0, "M12", 12.2, 15.0, 17.0, 15.0)},
    "gland_above_base": 15.5,              # gland centre above the underside of the box
    "gland_d": 16.0, "gland_len": 16.0,    # envelope used by the appearance model and drawing notes
    # 3 controller, 4 accelerometer, 7 carrier board (interface circuit) on four stand-offs
    "controller": (22.0, 51.0, 1.6), "controller_xy": (11.5, 0.0),   # module board, long side along Y
    "socket_h": 8.5,                       # female header sockets the controller plugs into
    "interface": (45.0, 56.0, 1.6), "interface_xy": (15.5, 0.0),    # carrier perfboard
    "board_standoff": 5.0, "carrier_holes": ((-3.5, 25.0), (35.0, 25.0)),
    "accel_board": (18.0, 18.0, 1.6),
    "led_xy": (30.0, -20.0),               # status LED under the lid's light pipe
    # 8 split-core current transformer, SCT-013 class, voltage output
    "ct_od": 44.0, "ct_t": 28.0, "ct_aperture": 13.0, "ct_latch": (18.0, 28.0, 10.0),
    # 9 surface temperature probe and 14 its clip
    "probe_d": 6.0, "probe_len": 34.0, "pad": (6.0, 20.0, 0.5),
    "probe_clip": (42.0, 16.0, 10.0),      # across the sleeve, along the sleeve, height
    "clip_mag": (12.0, 3.0, 13.0),         # high-temperature disc magnets: d, thickness, offset from centre
    # installed positions on the context motor (7.5 kW class, IEC 132 frame class)
    "motor_r": 130.0, "motor_len": 380.0, "pod_x": -70.0,
    "ct_pos": (95.0, 150.0, 45.0),         # CT round one phase conductor leaving the terminal box
    "probe_x": -165.0,                     # near the non-drive-end bearing
    "tbox": (110.0, 110.0, 90.0), "tbox_x": 95.0,
}


def derived(p=PARAMS):
    """Dimensions the calc note, drawings and build plan quote, computed from PARAMS."""
    bl, bw, bt = p["block"]
    L, W, H = p["box"]
    z_block0 = p["mag_h"]
    z_block1 = z_block0 + bt
    z_box0 = z_block1 + p["standoff_h"]
    z_floor_in = z_box0 + p["wall"]
    z_boss_top = z_floor_in + p["boss_above_floor"]
    z_top = z_box0 + H
    z_carrier = z_floor_in + p["board_standoff"]
    return {
        "z_block0": z_block0, "z_block1": z_block1, "z_box0": z_box0, "z_floor_in": z_floor_in,
        "z_boss_top": z_boss_top, "z_top": z_top, "z_lid0": z_top - p["lid_h"],
        "boss_h": z_boss_top - z_block1,
        "z_carrier": z_carrier, "z_carrier_top": z_carrier + p["interface"][2],
        "z_controller": z_carrier + p["interface"][2] + p["socket_h"],
        "z_gland": z_box0 + p["gland_above_base"],
        "pod_h": z_top,                                          # magnet face to lid top
        "pod_len_glands": L + p["glands"]["ct"][5] + p["glands"]["probe"][5],
        "mag_x": (-p["mag_pitch"] / 2, p["mag_pitch"] / 2),
        "pillar_xy": (L / 2 - p["wall"] - p["pillar_d"] / 2, W / 2 - p["wall"] - p["pillar_d"] / 2),
        "floor_area_mm2": bl * bw,                               # block footprint under the box floor
        "box_outer_area_mm2": 2 * (L * W + L * H + W * H),
        "box_floor_area_mm2": L * W,
    }


def _b3d():
    import build123d as b
    return b


def box(cx, cy, cz, sx, sy, sz):
    b = _b3d()
    return b.Pos(cx, cy, cz) * b.Box(sx, sy, sz)


def zcyl(x, y, z0, r, h):
    """Vertical cylinder standing on z0."""
    b = _b3d()
    return b.Pos(x, y, z0 + h / 2) * b.Cylinder(r, h)


def zhex(x, y, z0, af, h):
    """Vertical hexagon (across flats af) standing on z0."""
    b = _b3d()
    return b.Pos(x, y, z0) * b.extrude(b.RegularPolygon(af / 2, 6, major_radius=False), amount=h)


def xcyl(x0, y, z, r, h):
    """Cylinder along +X starting at x0."""
    b = _b3d()
    return b.Pos(x0 + h / 2, y, z) * b.Rot(0, 90, 0) * b.Cylinder(r, h)


def xhex(x0, y, z, af, h):
    b = _b3d()
    return b.Pos(x0, y, z) * b.Rot(0, 90, 0) * b.extrude(b.RegularPolygon(af / 2, 6, major_radius=False, rotation=30), amount=h)


def _fuse(shapes):
    out = None
    for s in shapes:
        out = s if out is None else out + s
    return out


def screw(x, y, z_head, head_d, head_h, shank_r, length, down=True):
    """Pan-head screw: head sits on z_head (on top if down=True), shank runs down (or up)."""
    if down:
        return zcyl(x, y, z_head, head_d / 2, head_h) + zcyl(x, y, z_head - length, shank_r, length)
    return zcyl(x, y, z_head - head_h, head_d / 2, head_h) + zcyl(x, y, z_head, shank_r, length)


def build_components(p=PARAMS):
    """Every component of the pod, the probe and its clip, and the CT, in the pod frame
    (pod at the origin, probe at y = -95, CT at y = +110). Returns {key: (bom_no, name, shape)}."""
    b = _b3d()
    D = derived(p)
    bl, bw, bt = p["block"]
    L, W, H = p["box"]
    wall, lid_h = p["wall"], p["lid_h"]
    base_h = H - lid_h
    bx = p["boss_x"]
    z0 = D["z_box0"]
    C = {}

    # 6 magnets with their trimmed M6 studs
    mags = []
    for mx in D["mag_x"]:
        mags.append(zcyl(mx, 0, 0, p["mag_d"] / 2, p["mag_h"]) + zcyl(mx, 0, p["mag_h"], 3.0, p["stud_len"]))
    C["magnets"] = (6, "Pot magnets, 32 mm, pair", _fuse(mags))

    # 5 sensor block: plate tapped M6 at both magnets and M3 at the four stand-offs
    sx, sy = p["standoff_xy"]
    so_xy = [(ix * sx, iy * sy) for ix in (-1, 1) for iy in (-1, 1)]
    blk = box(0, 0, D["z_block0"] + bt / 2, bl, bw, bt)
    for mx in D["mag_x"]:
        blk = blk - zcyl(mx, 0, D["z_block0"] - 1, 3.0, bt + 2)
    for x, y in so_xy:
        blk = blk - zcyl(x, y, D["z_block0"] - 1, 1.5, bt + 2)
    C["block"] = (5, "Aluminium sensor block", blk)
    # 5 boss: round bar, tapped M6 from below
    boss = zcyl(bx, 0, D["z_block1"], p["boss_d"] / 2, D["boss_h"]) - zcyl(bx, 0, D["z_block1"] - 1, 3.0, p["boss_tap_depth"] + 1)
    C["boss"] = (5, "Sensor boss", boss)
    # 12 M6 set screw: half in the block, half in the boss
    ss_len = p["set_screw_len"]
    C["set_screw"] = (12, "M6 x 12 set screw", zcyl(bx, 0, D["z_block1"] + p["boss_tap_depth"] - ss_len, 3.0, ss_len))

    # 13 insulating stand-offs (tubes) and 12 their M3 nylon screws
    so = _fuse([zcyl(x, y, D["z_block1"], p["standoff_d"] / 2, p["standoff_h"]) - zcyl(x, y, D["z_block1"] - 1, 1.6, p["standoff_h"] + 2)
                for x, y in so_xy])
    C["standoffs"] = (13, "Insulating stand-offs, nylon, four", so)
    C["standoff_screws"] = (12, "M3 x 12 nylon screws, four", _fuse([screw(x, y, D["z_floor_in"], 5.5, 2.0, 1.5, 12.0) for x, y in so_xy]))

    # 2 base: shell, moulded corner pillars, floor holes, gland holes
    base = box(0, 0, z0 + base_h / 2, L, W, base_h) - box(0, 0, z0 + wall + base_h / 2, L - 2 * wall, W - 2 * wall, base_h)
    px_, py_ = D["pillar_xy"]
    for ix in (-1, 1):
        for iy in (-1, 1):
            base = base + (zcyl(ix * px_, iy * py_, D["z_floor_in"], p["pillar_d"] / 2, base_h - wall)
                           - zcyl(ix * px_, iy * py_, D["z_floor_in"] + 4, 1.25, base_h))
    base = base - zcyl(bx, 0, z0 - 1, p["floor_hole_d"] / 2, wall + 2)
    for x, y in so_xy:
        base = base - zcyl(x, y, z0 - 1, 1.6, wall + 2)
    ch = [(x, sgn * y) for x, y in p["carrier_holes"] for sgn in (-1, 1)]
    for x, y in ch:
        base = base - zcyl(x, y, z0 - 1, 1.6, wall + 2)
    zg = D["z_gland"]
    for key, (end, gy, thr, hole, bd, blen, af) in p["glands"].items():
        x0 = L / 2 - wall - 1 if end > 0 else -L / 2 - 1
        base = base - xcyl(x0, gy, zg, hole / 2, wall + 2)
    C["base"] = (2, "Enclosure base, drilled", base)

    # 2 glands: outside body with hex, inside nut
    for key, (end, gy, thr, hole, bd, blen, af) in p["glands"].items():
        xo = end * L / 2                         # outer wall face
        xi = end * (L / 2 - wall)                # inner wall face
        if end > 0:
            body = xhex(xo, gy, zg, af, 3.0) + xcyl(xo + 3, gy, zg, bd / 2, blen - 3)
            th = xcyl(xi - 5.5, gy, zg, hole / 2 - 0.1, wall + 5.5)
            nut = xhex(xi - 5.0, gy, zg, af, 5.0) - xcyl(xi - 6, gy, zg, hole / 2 - 0.1, 7)
        else:
            body = xhex(xo - 3.0, gy, zg, af, 3.0) + xcyl(xo - blen, gy, zg, bd / 2, blen - 3)
            th = xcyl(xo, gy, zg, hole / 2 - 0.1, wall + 5.5)
            nut = xhex(xi, gy, zg, af, 5.0) - xcyl(xi - 1, gy, zg, hole / 2 - 0.1, 7)
        C[f"gland_{key}"] = (2, f"{thr} cable gland ({key})", body + th + nut)

    # 12 silicone grommet in the floor hole, gripping the boss
    gb, gbody, gfl, gft = p["grommet"]
    gr = (zcyl(bx, 0, z0 - gft, gfl / 2, gft) + zcyl(bx, 0, z0, gbody / 2, wall) + zcyl(bx, 0, D["z_floor_in"], gfl / 2, gft)) \
        - zcyl(bx, 0, z0 - gft - 1, gb / 2, wall + 2 * gft + 2)
    C["grommet"] = (12, "Silicone grommet round the boss", gr)

    # 4 accelerometer breakout bonded on the boss top
    ab = p["accel_board"]
    C["accel"] = (4, "Vibration accelerometer, IIS3DWB class",
                  box(bx, 0, D["z_boss_top"] + ab[2] / 2, *ab) + box(bx, 0, D["z_boss_top"] + ab[2] + 0.5, 4, 4, 1.0))

    # 12 carrier stand-offs (M3 x 5 hex) with screws from below the floor and above the board
    zc, zct = D["z_carrier"], D["z_carrier_top"]
    cso = _fuse([zhex(x, y, D["z_floor_in"], 5.5, p["board_standoff"]) - zcyl(x, y, D["z_floor_in"] - 1, 1.5, p["board_standoff"] + 2)
                 for x, y in ch])          # female-female, tapped M3 right through
    csc = _fuse([screw(x, y, z0, 5.5, 2.0, 1.5, 6.0, down=False) for x, y in ch]
                + [screw(x, y, zct, 5.5, 2.0, 1.5, 6.0) for x, y in ch])
    C["carrier_standoffs"] = (12, "Carrier stand-offs", cso)
    C["carrier_screws"] = (12, "Carrier M3 screws", csc)
    # 7 carrier perfboard with holes, interface parts, header sockets, LED
    cw, cd, ct_ = p["interface"]
    cx, cy = p["interface_xy"]
    carrier = box(cx, cy, zc + ct_ / 2, cw, cd, ct_)
    for x, y in ch:
        carrier = carrier - zcyl(x, y, zc - 1, 1.6, ct_ + 2)
    C["carrier"] = (7, "Carrier board (interface circuit)", carrier)
    k = p["controller"]
    kx, ky = p["controller_xy"]
    sockets = box(kx - k[0] / 2 + 1.3, ky, zct + p["socket_h"] / 2, 2.5, k[1], p["socket_h"]) + \
        box(kx + k[0] / 2 - 1.3, ky, zct + p["socket_h"] / 2, 2.5, k[1], p["socket_h"])
    C["sockets"] = (7, "Header sockets for the controller", sockets)
    lx, ly = p["led_xy"]
    jack = box(32.0, 2.0, zct + 2.5, 12.0, 6.0, 5.0)
    t5 = box(26.0, -9.0, zct + 4.0, 7.0, 10.0, 8.0)
    tp = box(26.0, 14.0, zct + 4.0, 7.0, 15.0, 8.0)
    button = box(34.5, -10.0, zct + 2.5, 6.0, 6.0, 5.0)
    led = zcyl(lx, ly, zct, 1.5, 2.0)
    C["interface_parts"] = (7, "Jack, screw terminals, button, LED", jack + t5 + tp + button + led)
    # 7 light pipe from the LED through the lid, with its bezel on the lid top
    C["light_pipe"] = (7, "Light pipe", zcyl(lx, ly, zct + 2.0, 1.5, D["z_top"] - zct - 2.0) + zcyl(lx, ly, D["z_top"], 3.0, 2.0))
    # 3 controller board plugged into the sockets
    zk = D["z_controller"]
    C["controller"] = (3, "Controller, ESP32-S3 module board",
                       box(kx, ky, zk + k[2] / 2, *k) + box(kx, ky + 10, zk + k[2] + 1.6, 18, 25, 3.2))

    # 1 lid with the light pipe hole
    zl = D["z_lid0"]
    lid = box(0, 0, zl + lid_h / 2, L, W, lid_h) - box(0, 0, zl + lid_h / 2 - wall, L - 2 * wall, W - 2 * wall, lid_h)
    lid = lid - zcyl(lx, ly, D["z_top"] - wall - 1, 1.5, wall + 2)
    C["lid"] = (1, "Enclosure lid, drilled", lid)

    # 8 current transformer (pod frame: beside the pod)
    ct_r, ct_t, ap = p["ct_od"] / 2, p["ct_t"], p["ct_aperture"] / 2
    ct = b.Rot(90, 0, 0) * (b.Cylinder(ct_r, ct_t) - b.Cylinder(ap, ct_t + 2))
    ct = ct + b.Pos(0, 0, ct_r + p["ct_latch"][2] / 2 - 4) * b.Box(*p["ct_latch"])
    C["ct"] = (8, "Split-core current transformer", b.Pos(0, 110, 30) * ct)

    # 9 probe (sleeve along Y on its pad) and 14 its clip, on the frame line z = 0 at y = -95
    C.update(probe_components(p, x=0.0, y=-95.0))
    return C


def probe_components(p=PARAMS, x=0.0, y=0.0):
    b = _b3d()
    pw, pl_, pt = p["pad"]
    r = p["probe_d"] / 2
    zs = pt + r
    pad = box(x, y, pt / 2, pw, pl_, pt)
    sleeve = b.Pos(x, y, zs) * b.Rot(90, 0, 0) * b.Cylinder(r, p["probe_len"])
    cl, cw, ch = p["probe_clip"]
    md, mt, mo = p["clip_mag"]
    clip = box(x, y, ch / 2, cl, cw, ch) - box(x, y, (pt + 2 * r) / 2 - 0.5, 2 * r + 0.2, cw + 2, pt + 2 * r + 1)
    for s in (-1, 1):
        clip = clip - zcyl(x + s * mo, y, -1, md / 2 + 0.1, mt + 1)
    mags = zcyl(x - mo, y, 0, md / 2, mt) + zcyl(x + mo, y, 0, md / 2, mt)
    return {"pad": (9, "Thermal pad", pad), "probe": (9, "Surface temperature probe", sleeve),
            "probe_clip": (14, "Probe clip", clip), "clip_magnets": (14, "Probe clip magnets", mags)}


BOM_NAMES = {1: "Enclosure lid, drilled, with light pipe hole", 2: "Enclosure base, drilled, with three cable glands",
             3: "Controller, ESP32-S3 module board", 4: "Vibration accelerometer, IIS3DWB class",
             5: "Aluminium sensor block and boss", 6: "Pot magnets, 32 mm, pair",
             7: "Carrier board (interface circuit, sockets, light pipe)", 8: "Split-core current transformer",
             9: "Surface temperature probe and pad", 12: "Grommet, screws and stand-offs (hardware)",
             13: "Insulating stand-offs, nylon, four", 14: "Probe clip with magnets"}


def build_parts(p=PARAMS, installed=True):
    """Return [(bom_no, name, shape)], one fused shape per BOM line, in the pod frame
    (installed=False) or on the motor. Used by the concept media, the calcs and the product model."""
    b = _b3d()
    C = build_components(p)
    groups = {}
    for key, (no, _, s) in C.items():
        groups.setdefault(no, []).append((key, s))
    out = []
    for no in sorted(groups):
        shapes = [s for _, s in groups[no]]
        keys = [k for k, _ in groups[no]]
        s = b.Compound(children=shapes) if len(shapes) > 1 else shapes[0]
        if installed:
            if no == 8:
                s = b.Pos(*p["ct_pos"]) * b.Pos(0, -110, -30) * s
            elif no in (9, 14):
                s = b.Pos(p["probe_x"], 95, 0) * s
            else:
                s = b.Pos(p["pod_x"], 0, 0) * s
        out.append((no, BOM_NAMES[no], s))
    return out


def pod_parts(p=PARAMS):
    return [t for t in build_parts(p, installed=False) if t[0] not in (8, 9, 14)]


def motor_context(p=PARAMS):
    """Grey context: 7.5 kW class induction motor with the frame top line at z = 0. Not in the BOM."""
    b = _b3d()
    R, Lm = p["motor_r"], p["motor_len"]
    zc = -R
    frame = b.Pos(0, 0, zc) * b.Rot(0, 90, 0) * b.Cylinder(R, Lm)
    fins = None
    for k in range(24):                    # axial cooling fins, none on the top band
        ang = k * 15.0
        if ang <= 20 or ang >= 340:
            continue
        f = b.Pos(0, 0, zc) * b.Rot(ang, 0, 0) * b.Pos(0, 0, R + 4) * b.Box(Lm - 20, 4, 12)
        fins = f if fins is None else fins + f
    shields = (b.Pos(-Lm / 2 - 15, 0, zc) * b.Rot(0, 90, 0) * b.Cylinder(R - 12, 30)
               + b.Pos(Lm / 2 + 15, 0, zc) * b.Rot(0, 90, 0) * b.Cylinder(R - 12, 30))
    shaft = b.Pos(Lm / 2 + 70, 0, zc) * b.Rot(0, 90, 0) * b.Cylinder(19, 80)
    fz = zc - R + 50
    feet = (b.Pos(-120, 0, zc - 150) * b.Box(70, 260, 60) + b.Pos(120, 0, zc - 150) * b.Box(70, 260, 60)
            + b.Pos(-120, 0, fz - 40) * b.Box(50, 150, 80) + b.Pos(120, 0, fz - 40) * b.Box(50, 150, 80))
    tx, (tl, tw, th) = p["tbox_x"], p["tbox"]
    tbox = b.Pos(tx, 0, th / 2 - 10) * b.Box(tl, tw, th)
    cz = p["ct_pos"][2]
    conduit = b.Pos(tx, tw / 2 + 25, cz) * b.Rot(90, 0, 0) * b.Cylinder(16, 50)
    return frame + fins + shields + shaft + feet + tbox + conduit


def leads(p=PARAMS):
    """Grey context: phase conductor through the CT, and the CT, probe and power leads."""
    b = _b3d()
    D = derived(p)

    def rod(p0, p1, r):
        d = b.Vector(*p1) - b.Vector(*p0)
        return b.Solid.make_cylinder(r, d.length, b.Plane(origin=p0, z_dir=d))
    tx, tw = p["tbox_x"], p["tbox"][1]
    cx, cy, cz = p["ct_pos"]
    zf = -2 * p["motor_r"] - 10
    cond = rod((tx, tw / 2 + 50, cz), (tx, 260, cz), 5.5) + rod((tx, 260, cz), (tx, 260, zf), 5.5)
    L = p["box"][0]
    gz = D["z_gland"]
    px = p["pod_x"]
    G = p["glands"]
    gxp = px + L / 2 + G["ct"][5]
    gxn = px - L / 2 - G["probe"][5]
    ct_lead = rod((gxp, G["ct"][1], gz), (cx, cy - 20, cz + p["ct_od"] / 2 + 6), 2.0)
    probe_lead = rod((gxn, G["probe"][1], gz), (p["probe_x"], p["probe_len"] / 2, p["pad"][2] + p["probe_d"] / 2), 2.0)
    pw = G["power"][1]
    usb = rod((gxn, pw, gz), (gxn - 20, -200, gz), 2.0) + rod((gxn - 20, -200, gz), (gxn - 20, -200, zf), 2.0)
    return cond + ct_lead + probe_lead + usb


def assembly(p=PARAMS, installed=True, pod_only=False):
    from build123d import Compound
    parts = pod_parts(p) if pod_only else build_parts(p, installed)
    return Compound(children=[s for _, _, s in parts])


# ----------------------------------------------------------------- constructability checks
TOUCH = [  # (a, b, what holds them): faces that must meet
    ("magnets", "block", "magnet backs flat on the block underside, studs in its tapped holes"),
    ("set_screw", "block", "set screw in the block's tapped hole"),
    ("set_screw", "boss", "set screw in the boss's tapped hole"),
    ("boss", "block", "boss face flat on the block top"),
    ("standoffs", "block", "stand-offs on the block top"),
    ("standoffs", "base", "stand-offs under the box floor"),
    ("standoff_screws", "base", "screw heads on the inside of the floor"),
    ("standoff_screws", "block", "screws in the block's tapped holes"),
    ("grommet", "base", "grommet seated in the floor hole"),
    ("grommet", "boss", "grommet bore grips the boss"),
    ("accel", "boss", "accelerometer board bonded to the boss top"),
    ("carrier_standoffs", "base", "carrier stand-offs on the floor"),
    ("carrier_standoffs", "carrier", "carrier on its stand-offs"),
    ("carrier_screws", "carrier_standoffs", "M3 screws into the stand-offs from below and above"),
    ("sockets", "carrier", "sockets soldered to the carrier"),
    ("controller", "sockets", "controller plugged into the sockets"),
    ("interface_parts", "carrier", "jack, terminals, button and LED on the carrier"),
    ("light_pipe", "interface_parts", "light pipe on the LED"),
    ("light_pipe", "lid", "light pipe through the lid hole"),
    ("lid", "base", "lid on the base"),
    ("gland_ct", "base", "gland through the end wall"),
    ("gland_probe", "base", "gland through the end wall"),
    ("gland_power", "base", "gland through the end wall"),
    ("pad", "probe", "sleeve on its thermal pad"),
    ("probe", "probe_clip", "sleeve held in the clip's groove"),
    ("clip_magnets", "probe_clip", "magnets bonded in the clip pockets"),
]
CLEAR = [  # (a, b, minimum gap mm)
    ("block", "base", 4.0), ("magnets", "base", 10.0), ("accel", "base", 1.0), ("accel", "grommet", 1.0),
    ("accel", "carrier", 3.0), ("accel", "controller", 3.0), ("accel", "gland_probe", 3.0), ("accel", "gland_power", 3.0),
    ("carrier", "gland_ct", 2.0), ("controller", "gland_ct", 2.0), ("interface_parts", "gland_ct", 2.0),
    ("controller", "lid", 2.0), ("interface_parts", "controller", 0.5), ("standoff_screws", "carrier", 2.0),
    ("standoff_screws", "grommet", 0.5), ("standoffs", "grommet", 0.5), ("carrier", "base", 1.0),
    ("gland_probe", "gland_power", 3.0), ("controller", "base", 1.0), ("boss", "base", 1.0),
    ("set_screw", "magnets", 0.0),
]


def check(p=PARAMS, verbose=True):
    """Constructability checks: every listed pair that must touch does touch without overlapping,
    and every listed pair that must be apart is apart by at least the gap. Returns failures."""
    C = build_components(p)
    fails, n = [], 0
    keys = list(C)
    for a, bk, why in TOUCH:
        sa, sb = C[a][2], C[bk][2]
        d = sa.distance_to(sb)
        v = (sa & sb).volume
        n += 1
        ok = d < 0.05 and v < 1.0
        if verbose:
            print(f"{'ok  ' if ok else 'FAIL'} touch {a} / {bk}: gap {d:.2f} mm, overlap {v:.2f} mm3 ({why})")
        if not ok:
            fails.append((a, bk))
    for a, bk, gap in CLEAR:
        d = C[a][2].distance_to(C[bk][2])
        n += 1
        ok = d >= gap - 1e-6
        if verbose:
            print(f"{'ok  ' if ok else 'FAIL'} clear {a} / {bk}: {d:.2f} mm (needs {gap:.1f})")
        if not ok:
            fails.append((a, bk))
    # no two components overlap anywhere (except the probe pad, which is meant to squeeze)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, bk = keys[i], keys[j]
            sa, sb = C[a][2], C[bk][2]
            ba, bb_ = sa.bounding_box(), sb.bounding_box()
            if ba.max.X < bb_.min.X or bb_.max.X < ba.min.X or ba.max.Y < bb_.min.Y or bb_.max.Y < ba.min.Y \
                    or ba.max.Z < bb_.min.Z or bb_.max.Z < ba.min.Z:
                continue
            v = (sa & sb).volume
            n += 1
            if v > 1.0:
                fails.append((a, bk))
                if verbose:
                    print(f"FAIL overlap {a} / {bk}: {v:.1f} mm3")
    # the accelerometer must go in after the box: its board cannot pass the floor hole
    diag = (p["accel_board"][0] ** 2 + p["accel_board"][1] ** 2) ** 0.5
    if verbose:
        print(f"note accelerometer board diagonal {diag:.1f} mm against a {p['floor_hole_d']:.0f} mm floor hole: "
              f"{'bond it on the boss after the base is fitted' if diag > p['floor_hole_d'] else 'it passes the hole'}")
    print(f"{n - len(fails)} of {n} constructability checks pass")
    return fails


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(1 if check() else 0)
    from build123d import export_step, export_stl
    out = Path(__file__).resolve().parents[1]
    (out / "step").mkdir(exist_ok=True); (out / "stl").mkdir(exist_ok=True)
    C = build_components()
    import build123d as b
    block = b.Compound(children=[C["block"][2], C["boss"][2], C["set_screw"][2]])
    D = derived()
    for name, shape in (("machinepulse-assembly", assembly()),
                        ("machinepulse-pod", assembly(pod_only=True)),
                        ("sensor-block", block)):
        export_step(shape, str(out / "step" / f"{name}.step"))
        export_stl(shape, str(out / "stl" / f"{name}.stl"), tolerance=0.05, angular_tolerance=0.3)
        bb = shape.bounding_box()
        print(f"{name}: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm")
    print(f"pod height magnet face to lid {D['pod_h']:.1f} mm; length over glands {D['pod_len_glands']:.0f} mm")
