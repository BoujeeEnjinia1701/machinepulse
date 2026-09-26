"""MachinePulse parametric model (build123d), TRL 3, massing-plus level of detail.

Run from the repo root:  python cad/src/model.py
Exports STEP and STL into cad/step and cad/stl:
    machinepulse-assembly.step / .stl   pod, current transformer and probe as installed
    machinepulse-pod.step / .stl        the magnetic sensor pod on its own
    sensor-block.step / .stl            aluminium sensor block with its round boss

Axes: the pod sits on the top line of a horizontal motor frame. The magnet contact line is
the X axis at z = 0, X runs along the motor shaft, Z is up, and the motor axis is at
z = -motor_r. Keeping the pod at the origin lets the kit's cutaway cutter pass through it.
Main dimensions and interfaces only: magnet spacing and contact, sensor block and boss,
insulating stand-offs, enclosure envelope and glands, board placement, current transformer
aperture and probe clip. Not fabrication detail; not for fabrication. The same PARAMS feed
docs/04-calcs/sizing.py (MPL-CAL-001) and the drawing MPL-DWG-001 (cad/src/sheets.py).
"""
from pathlib import Path

# Top-level parameters (mm). Edit these, not the geometry below.
PARAMS = {
    # 6 pot magnets: 32 mm high-temperature neodymium pot magnets with M6 studs, spaced along X
    # (rated 120 degC; MPL-DDR-002 N1 replaced the 80 degC standard grade)
    "mag_d": 32.0, "mag_h": 8.0, "mag_pitch": 40.0, "mag_t_max": 120.0,
    # 5 aluminium sensor block and round boss (boss carries the accelerometer through the box floor)
    "block": (76.0, 36.0, 10.0), "boss_d": 20.0, "boss_x": -20.0,   # boss directly above magnet 1
    "boss_above_floor": 3.5,                                         # boss top above the inside floor
    # 13 insulating stand-offs: nylon, between block and box floor (thermal break, MPL-CAL-001 C)
    "standoff_h": 5.0, "standoff_d": 6.0, "standoff_xy": (30.0, 12.0),
    # 1, 2 stock IP54 ABS box: outer size, base and lid heights, wall
    "box": (100.0, 68.0, 40.0), "lid_h": 12.0, "wall": 2.5,
    "floor_hole_d": 24.0,                  # clearance hole round the boss, sealed by a silicone boot
    "gland_d": 16.0, "gland_len": 16.0,    # M12 IP68 cable glands, one each end
    # 3, 4, 7 boards inside the box
    "controller": (51.0, 22.0, 1.6), "controller_xy": (20.0, 16.0),
    "interface": (40.0, 26.0, 1.6), "interface_xy": (22.0, -17.0),
    "board_standoff": 5.0,
    "accel_board": (18.0, 18.0, 1.6),
    # 8 split-core current transformer, SCT-013 class, voltage output
    "ct_od": 44.0, "ct_t": 28.0, "ct_aperture": 13.0, "ct_latch": (18.0, 28.0, 10.0),
    # 9 surface temperature probe in a magnetic clip
    "probe_clip": (22.0, 16.0, 8.0), "probe_d": 6.0, "probe_len": 34.0,
    # installed positions on the context motor (7.5 kW class, IEC 132 frame class)
    "motor_r": 130.0, "motor_len": 380.0, "pod_x": -70.0,
    "ct_pos": (95.0, 150.0, 45.0),         # CT round one phase conductor leaving the terminal box
    "probe_x": -165.0,                     # near the non-drive-end bearing
    "tbox": (110.0, 110.0, 90.0), "tbox_x": 95.0,
}


def derived(p=PARAMS):
    """Dimensions the calc note and drawing quote, computed from PARAMS."""
    bl, bw, bt = p["block"]
    L, W, H = p["box"]
    z_block0 = p["mag_h"]
    z_block1 = z_block0 + bt
    z_box0 = z_block1 + p["standoff_h"]
    z_floor_in = z_box0 + p["wall"]
    z_boss_top = z_floor_in + p["boss_above_floor"]
    z_top = z_box0 + H
    return {
        "z_block0": z_block0, "z_block1": z_block1, "z_box0": z_box0, "z_floor_in": z_floor_in,
        "z_boss_top": z_boss_top, "z_top": z_top, "z_lid0": z_top - p["lid_h"],
        "boss_h": z_boss_top - z_block1,
        "pod_h": z_top,                                          # magnet face to lid top
        "pod_len_glands": L + 2 * p["gland_len"],
        "mag_x": (-p["mag_pitch"] / 2, p["mag_pitch"] / 2),
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


def build_parts(p=PARAMS, installed=True):
    """Return [(bom_no, name, shape)] in the pod frame (installed=False) or on the motor."""
    b = _b3d()
    D = derived(p)
    bl, bw, bt = p["block"]
    L, W, H = p["box"]
    wall, lid_h = p["wall"], p["lid_h"]
    base_h = H - lid_h
    bx = p["boss_x"]

    # 6 magnets, 5 block and boss
    magnets = zcyl(D["mag_x"][0], 0, 0, p["mag_d"] / 2, p["mag_h"]) + zcyl(D["mag_x"][1], 0, 0, p["mag_d"] / 2, p["mag_h"])
    block = box(0, 0, D["z_block0"] + bt / 2, bl, bw, bt) + zcyl(bx, 0, D["z_block1"], p["boss_d"] / 2, D["boss_h"])

    # 13 insulating stand-offs
    sx, sy = p["standoff_xy"]
    stand = None
    for ix in (-1, 1):
        for iy in (-1, 1):
            s = zcyl(ix * sx, iy * sy, D["z_block1"], p["standoff_d"] / 2, p["standoff_h"])
            stand = s if stand is None else stand + s

    # 2 base with floor hole and glands, 1 lid with LED window
    z0 = D["z_box0"]
    base = box(0, 0, z0 + base_h / 2, L, W, base_h) - box(0, 0, z0 + wall + base_h / 2, L - 2 * wall, W - 2 * wall, base_h)
    base = base - zcyl(bx, 0, z0 - 1, p["floor_hole_d"] / 2, wall + 2)
    gz = z0 + base_h / 2
    gl, gr = p["gland_len"], p["gland_d"] / 2
    base = (base + b.Pos(L / 2 + gl / 2, 12, gz) * b.Rot(0, 90, 0) * b.Cylinder(gr, gl)
            + b.Pos(-L / 2 - gl / 2, 0, gz) * b.Rot(0, 90, 0) * b.Cylinder(gr, gl))
    zl = D["z_lid0"]
    lid = box(0, 0, zl + lid_h / 2, L, W, lid_h) - box(0, 0, zl + lid_h / 2 - wall, L - 2 * wall, W - 2 * wall, lid_h)
    lid = lid + zcyl(30, -20, D["z_top"], 3, 2)
    # silicone boot round the boss (part of line 12 hardware)
    boot = zcyl(bx, 0, z0 - 1.0, p["floor_hole_d"] / 2 + 2, 1.0) - zcyl(bx, 0, z0 - 1.5, p["boss_d"] / 2, 2)

    # 4 accelerometer breakout on the boss top; 3 controller and 7 interface board on stand-offs
    ab = p["accel_board"]
    accel = box(bx, 0, D["z_boss_top"] + ab[2] / 2, *ab) + box(bx, 0, D["z_boss_top"] + ab[2] + 0.5, 4, 4, 1.0)
    zb = D["z_floor_in"] + p["board_standoff"]
    cx, cy = p["controller_xy"]; c = p["controller"]
    controller = box(cx, cy, zb + c[2] / 2, *c) + box(cx + 6, cy, zb + c[2] + 1.6, 18, 18, 3.2)
    ix_, iy_ = p["interface_xy"]; i = p["interface"]
    interface = box(ix_, iy_, zb + i[2] / 2, *i) + box(ix_ + 14, iy_, zb + i[2] + 3, 8, 12, 6)

    # 8 current transformer and 9 probe (installed positions refer to the motor)
    ct_r, ct_t, ap = p["ct_od"] / 2, p["ct_t"], p["ct_aperture"] / 2
    ct = b.Rot(90, 0, 0) * (b.Cylinder(ct_r, ct_t) - b.Cylinder(ap, ct_t + 2))
    ct = ct + b.Pos(0, 0, ct_r + p["ct_latch"][2] / 2 - 4) * b.Box(*p["ct_latch"])
    pc = p["probe_clip"]
    probe = b.Pos(0, 0, pc[2] / 2) * b.Box(*pc) + b.Pos(0, 0, pc[2] + p["probe_d"] / 2 - 1) * b.Rot(90, 0, 0) * b.Cylinder(p["probe_d"] / 2, p["probe_len"])
    if installed:
        px = p["pod_x"]
        pod = lambda s: b.Pos(px, 0, 0) * s
        magnets, block, stand, base, lid, boot, accel, controller, interface = map(
            pod, (magnets, block, stand, base, lid, boot, accel, controller, interface))
        ct = b.Pos(*p["ct_pos"]) * ct
        probe = b.Pos(p["probe_x"], 0, 0) * probe
    else:
        ct = b.Pos(0, 110, 30) * ct
        probe = b.Pos(0, -95, 0) * probe

    return [
        (1, "Enclosure lid with LED window", lid),
        (2, "Enclosure base with cable glands", base),
        (3, "Controller, ESP32-S3 module board", controller),
        (4, "Vibration accelerometer, IIS3DWB class", accel),
        (5, "Aluminium sensor block", block),
        (6, "Pot magnets, 32 mm, pair", magnets),
        (7, "Interface board (CT, probe, LED)", interface),
        (8, "Split-core current transformer", ct),
        (9, "Surface temperature probe", probe),
        (12, "Silicone boot round the boss", boot),
        (13, "Insulating stand-offs, nylon, four", stand),
    ]


def pod_parts(p=PARAMS):
    return [t for t in build_parts(p, installed=False) if t[0] not in (8, 9)]


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
    """Grey context: phase conductor through the CT, and the CT, probe and USB leads."""
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
    gz = D["z_box0"] + (p["box"][2] - p["lid_h"]) / 2
    px = p["pod_x"]
    gxp, gxn = px + L / 2 + p["gland_len"], px - L / 2 - p["gland_len"]
    ct_lead = rod((gxp, 12, gz), (cx, cy - 20, cz + p["ct_od"] / 2 + 6), 2.0)
    probe_lead = rod((gxn, 0, gz), (p["probe_x"], 0, p["probe_clip"][2] + 2), 2.0)
    usb = rod((gxn, -2, gz - 3), (gxn - 20, -200, gz - 3), 2.0) + rod((gxn - 20, -200, gz - 3), (gxn - 20, -200, zf), 2.0)
    return cond + ct_lead + probe_lead + usb


def assembly(p=PARAMS, installed=True, pod_only=False):
    from build123d import Compound
    parts = pod_parts(p) if pod_only else build_parts(p, installed)
    return Compound(children=[s for _, _, s in parts])


if __name__ == "__main__":
    from build123d import export_step, export_stl
    out = Path(__file__).resolve().parents[1]
    (out / "step").mkdir(exist_ok=True); (out / "stl").mkdir(exist_ok=True)
    block = [s for n, _, s in pod_parts() if n == 5][0]
    D = derived()
    for name, shape in (("machinepulse-assembly", assembly()),
                        ("machinepulse-pod", assembly(pod_only=True)),
                        ("sensor-block", block)):
        export_step(shape, str(out / "step" / f"{name}.step"))
        export_stl(shape, str(out / "stl" / f"{name}.stl"))
        bb = shape.bounding_box()
        print(f"{name}: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm")
    print(f"pod height magnet face to lid {D['pod_h']:.1f} mm; length over glands {D['pod_len_glands']:.0f} mm")
