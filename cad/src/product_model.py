"""MachinePulse product appearance model (build123d), TRL 3.

Finished-product look for photoreal renders: a single-colour filleted stock enclosure with a parting-line
groove, lid screws, a lit status light pipe, a status button and a printed label; fluted M12
cable glands; the machined aluminium sensor block on nylon stand-offs and high-temperature pot
magnets; the boards inside; a split-core current transformer with its seam, latch, marking and
strain relief; the stainless temperature probe in its magnetic clip; swept cables; and a clay
7.5 kW class motor with a phase conductor as context.
APPEARANCE MODEL ONLY: no tolerances, no fabrication detail. CONCEPT, NOT FOR FABRICATION.

Every main dimension and interface comes from PARAMS, derived(), build_parts() and
motor_context() in model.py. Axes as model.py: the magnet contact line is the X axis at z = 0,
X runs along the motor shaft, Z is up, and the motor axis is at z = -motor_r. The pod sits at
x = pod_x, the current transformer at ct_pos and the probe at probe_x, all as installed.

    from product_model import product_parts
    for p in product_parts(): print(p["name"], p["group"], p["material"])
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build123d import (Axis, Box, Circle, Cone, Cylinder, Plane, Pos, RectangleRounded,
                       RegularPolygon, Rot, Sphere, Spline, Text, Vector, extrude, fillet, sweep)
from model import PARAMS, derived, build_parts, motor_context

TITLE = "MachinePulse: clip-on condition monitor for older machines"

RENDER_VIEWS = [
    {"name": "hero", "groups": ["shell", "internal", "context"], "explode": False, "el": 30, "az": 42,
     "note": "Product render from the right, on the cable side of the motor, and above (about 30 deg "
             "elevation); hub on the frame top, current clamp on the phase conductor at right, "
             "temperature probe at the left end"},
    {"name": "exploded", "groups": ["shell", "internal", "accessory"], "explode": True, "el": 28, "az": -55,
     "note": "Exploded view from the front right and above (about 28 deg elevation): lid, boards, "
             "enclosure base and glands, magnetic sensor base (block, stand-offs, magnets, steel pads), "
             "current clamp, temperature probe and USB power adapter"},
    {"name": "detail", "groups": ["shell", "internal"], "explode": False, "el": 26, "az": 42,
     "note": "Detail view from the right and above (about 26 deg elevation), without the motor: hub on "
             "its magnetic sensor base, current clamp at right, temperature probe in its clip at left"},
]

# Colours (restrained product palette; accent from the kit)
C_LID = "#D3D7DB"
C_BASE = C_LID           # single-colour stock box (decided 2026-10-02); two-tone is a later option
C_DARK = "#23272E"
C_ACCENT = "#0F766E"
C_LED = "#34D399"
C_LABEL = "#F2F1EC"
C_INK = "#1F2937"
C_ALU = "#C5CAD0"
C_STEEL = "#A9B0B8"
C_NYLON = "#EFECE4"
C_BRASS = "#C9A227"
C_PCB_BLACK = "#1A1D21"
C_PCB_GREEN = "#166534"
C_PCB_PURPLE = "#4C1D95"
C_CHIP = "#111827"
C_CABLE = "#1C1F24"
C_COND = "#3B3F46"
C_CLAY = "#CFC5B8"
C_WHITE = "#F4F4F2"

# Appearance-only detail sizes (mm)
BOX_R = 5.0            # plan corner radius of the stock box
FIL_TOP = 3.0          # lid top edge fillet
FIL_BOT = 2.0          # base bottom edge fillet
GROOVE = 0.6           # parting-line groove depth and half height
LID_SCREW = 6.0        # lid screw inset from the outer corner
LED_XY = (30.0, -20.0) # pod-local, as model.py
BTN_XY = (30.0, -4.0)  # pod-local status button (appearance addition, BOM 7 button)
LABEL = (24.0, 56.0, -14.0, 0.0)   # label plate size in X and Y, centre x, centre y (pod-local)


def _fillet_try(shape, edges, radii):
    """Fillet `edges` with the first radius that gives a valid solid; else return the input."""
    edges = list(edges)
    if not edges:
        return shape
    for r in radii:
        try:
            out = fillet(edges, r)
            if out.is_valid and out.volume > 0:
                return out
        except Exception:
            pass
    return shape


def _prism(L, W, r, z0, h, x=0.0, y=0.0):
    """Rounded-rectangle prism in plan, from z0 up by h."""
    r = max(min(r, min(L, W) / 2 - 0.01), 0.01)
    return Pos(x, y, z0) * extrude(RectangleRounded(L, W, r), amount=h)


def _top_edges(s):
    return s.faces().sort_by(Axis.Z)[-1].edges()


def _bottom_edges(s):
    return s.faces().sort_by(Axis.Z)[0].edges()


def _cable(points, r, t0, t1):
    """Round cable swept along a spline through `points` with end tangents t0 and t1."""
    pts = [Vector(*q) for q in points]
    d = 3.0 * r
    pts = [pts[0], pts[0] + Vector(*t0) * d] + pts[1:-1] + [pts[-1] - Vector(*t1) * d, pts[-1]]
    path = Spline(*pts)
    prof = Plane(origin=path @ 0, z_dir=path % 0) * Circle(r)
    return sweep(prof, path=path)


def _gland(x_face, y, z, sign):
    """M12 cable gland on an end wall: hex body, fluted dome cap and seal nose, along sign * X."""
    hexb = extrude(RegularPolygon(9.2, 6), amount=5.0)
    cap = Pos(0, 0, 5.0) * Cylinder(8.0, 9.0, align=None)
    for k in range(12):
        a = 30.0 * k
        cap -= Rot(0, 0, a) * Pos(8.2, 0, 10.0) * Box(1.4, 1.2, 8.0)
    nose = Pos(0, 0, 14.0) * extrude(Circle(6.0), amount=2.0)
    g = hexb + cap + nose
    g = _fillet_try(g, _top_edges(g), [0.8, 0.4])
    g -= Pos(0, 0, 13.0) * Cylinder(4.8, 8.0)          # seal insert opening
    seal = Pos(0, 0, 14.5) * Cylinder(4.8, 1.0) - Pos(0, 0, 14.5) * Cylinder(2.3, 2.0)
    rot = Rot(0, 90 * sign, 0)
    return Pos(x_face, y, z) * rot * g, Pos(x_face, y, z) * rot * seal


def _pan_screw(x, y, z0, r=2.8, h=1.2):
    head = Pos(x, y, z0 + h / 2) * Cylinder(r, h)
    head = _fillet_try(head, _top_edges(head), [0.6, 0.3])
    head -= Pos(x, y, z0 + h) * Box(2.6, 0.6, 1.0)
    head -= Pos(x, y, z0 + h) * Box(0.6, 2.6, 1.0)
    return head


def product_parts(P=PARAMS):
    D = derived(P)
    m = {no: s for no, _, s in build_parts(P, installed=True)}
    out = []

    def add(name, shape, color, material, bom, group, explode):
        out.append({"name": name, "shape": shape, "color": color, "material": material,
                    "bom": bom, "group": group, "explode": tuple(float(v) for v in explode)})

    px = P["pod_x"]
    L, W, H = P["box"]
    wall, lid_h = P["wall"], P["lid_h"]
    z0, zl, zt = D["z_box0"], D["z_lid0"], D["z_top"]
    bx = P["boss_x"]
    gl, gr = P["gland_len"], P["gland_d"] / 2
    gz = z0 + (H - lid_h) / 2

    # ---------------------------------------------------------------- enclosure (BOM 1, 2)
    groove = _prism(L + 2, W + 2, BOX_R + 1, zl - GROOVE, 2 * GROOVE, x=px) - \
        _prism(L - 2 * GROOVE, W - 2 * GROOVE, BOX_R - GROOVE, zl - 2 * GROOVE, 4 * GROOVE, x=px)

    lid = _prism(L, W, BOX_R, zl, lid_h, x=px)
    lid = _fillet_try(lid, _top_edges(lid), [FIL_TOP, 2.0, 1.0])
    lid -= _prism(L - 2 * wall, W - 2 * wall, BOX_R - wall, zl - 1, lid_h - wall + 1, x=px)
    lid -= groove
    lx, ly = LED_XY
    bxx, bxy = BTN_XY
    lid -= Pos(px + lx, ly, zt - wall / 2) * Cylinder(3.0, wall + 2)
    lid -= Pos(px + bxx, bxy, zt - wall / 2) * Cylinder(4.6, wall + 2)
    screws_xy = [(px + sx * (L / 2 - LID_SCREW), sy * (W / 2 - LID_SCREW)) for sx in (-1, 1) for sy in (-1, 1)]
    for (x, y) in screws_xy:
        lid -= Pos(x, y, zt - 0.6) * Cylinder(3.4, 1.2 + 0.01)
    add("Enclosure lid", lid, C_LID, "plastic", 1, "shell", (0, 0, 165))
    lid_screws = None
    for (x, y) in screws_xy:
        s = _pan_screw(x, y, zt - 1.2)
        lid_screws = s if lid_screws is None else lid_screws + s
    add("Lid screws, four", lid_screws, C_STEEL, "metal", 12, "shell", (0, 0, 185))

    bezel = Pos(px + lx, ly, zt + 0.3) * (Cylinder(4.4, 0.6) - Cylinder(3.0, 1.0))
    add("Status light bezel", bezel, C_DARK, "plastic", 1, "shell", (0, 0, 172))
    pipe = Pos(px + lx, ly, zt - 1.0) * Cylinder(2.95, 2.0, align=None) + \
        Pos(px + lx, ly, zt + 1.0) * Cylinder(2.95, 1.0, align=None)
    pipe = _fillet_try(pipe, _top_edges(pipe), [1.2, 0.8, 0.4])
    add("Status LED light pipe (lit)", pipe, C_LED, "emissive", 7, "shell", (0, 0, 172))
    btn_bezel = Pos(px + bxx, bxy, zt + 0.3) * (Cylinder(6.0, 0.6) - Cylinder(4.6, 1.0))
    add("Button bezel", btn_bezel, C_DARK, "plastic", 7, "shell", (0, 0, 172))
    btn = Pos(px + bxx, bxy, zt) * Cylinder(4.3, 2.4)
    btn = _fillet_try(btn, _top_edges(btn), [1.0, 0.6])
    add("Status button (silicone)", btn, C_ACCENT, "rubber", 7, "shell", (0, 0, 176))

    ll, lw, lcx, lcy = LABEL
    plate = _prism(ll, lw, 2.0, zt, 0.2, x=px + lcx, y=lcy)
    add("Lid label", plate, C_LABEL, "paper", None, "shell", (0, 0, 166))
    # print reads along +Y so it is upright from both the hero and the exploded camera
    txt = Pos(px + lcx - 4.0, lcy, zt + 0.2) * Rot(0, 0, 90) * extrude(Text("MachinePulse", 7.0), amount=0.15)
    txt += Pos(px + lcx + 5.5, lcy, zt + 0.2) * Rot(0, 0, 90) * extrude(Text("CURRENT  VIBRATION  TEMP", 2.6), amount=0.15)
    add("Label print", txt, C_INK, "painted", None, "shell", (0, 0, 166))
    bar = _prism(1.6, lw - 8, 0.6, zt + 0.2, 0.15, x=px + lcx + 1.2, y=lcy)
    add("Label accent stripe", bar, C_ACCENT, "painted", None, "shell", (0, 0, 166))

    base = _prism(L, W, BOX_R, z0, zl - z0, x=px)
    base = _fillet_try(base, _bottom_edges(base), [FIL_BOT, 1.5, 1.0])
    base -= _prism(L - 2 * wall, W - 2 * wall, BOX_R - wall, z0 + wall, zl - z0, x=px)
    base -= groove
    base -= Pos(px + bx, 0, z0 + wall / 2) * Cylinder(P["floor_hole_d"] / 2, wall + 2)
    base -= Pos(px + L / 2 - wall / 2, 12, gz) * Rot(0, 90, 0) * Cylinder(6.0, wall + 2)
    base -= Pos(px - L / 2 + wall / 2, 0, gz) * Rot(0, 90, 0) * Cylinder(6.0, wall + 2)
    add("Enclosure base", base, C_BASE, "plastic", 2, "shell", (0, 0, 60))

    g1, s1 = _gland(px + L / 2, 12, gz, +1)
    g2, s2 = _gland(px - L / 2, 0, gz, -1)
    add("Cable gland, clamp side", g1, C_DARK, "plastic", 2, "shell", (28, 0, 60))
    add("Gland seal insert, clamp side", s1, "#3A3F47", "rubber", 2, "shell", (28, 0, 60))
    add("Cable gland, probe and power side", g2, C_DARK, "plastic", 2, "shell", (-28, 0, 60))
    add("Gland seal insert, probe and power side", s2, "#3A3F47", "rubber", 2, "shell", (-28, 0, 60))

    # ---------------------------------------------------------------- magnetic sensor base (5, 6, 13, 12)
    bl, bw, bt = P["block"]
    block = _prism(bl, bw, 3.0, D["z_block0"], bt, x=px)
    block = _fillet_try(block, _top_edges(block), [1.0, 0.6])
    block = _fillet_try(block, _bottom_edges(block), [0.6, 0.3])
    boss = Pos(px + bx, 0, D["z_block1"] - 0.5) * extrude(Circle(P["boss_d"] / 2), amount=D["boss_h"] + 0.5)
    boss = _fillet_try(boss, _top_edges(boss), [0.8, 0.5])
    add("Aluminium sensor block", block + boss, C_ALU, "metal", 5, "shell", (0, 0, 0))
    nut = Pos(px + D["mag_x"][1], 0, D["z_block1"]) * extrude(RegularPolygon(5.8, 6), amount=5.0)
    nut = _fillet_try(nut, _top_edges(nut), [0.6, 0.3])
    nut -= Pos(px + D["mag_x"][1], 0, D["z_block1"] + 4.0) * Cylinder(2.6, 3.0)
    add("M6 magnet stud nut", nut, C_STEEL, "metal", 12, "shell", (0, 0, 10))

    mags = None
    for mx in D["mag_x"]:
        cup = Pos(px + mx, 0, 0) * extrude(Circle(P["mag_d"] / 2), amount=P["mag_h"])
        cup = _fillet_try(cup, _top_edges(cup), [1.0, 0.6])
        cup = _fillet_try(cup, _bottom_edges(cup), [0.6, 0.3])
        cup -= Pos(px + mx, 0, 0) * (Cylinder(12.5, 1.0) - Cylinder(11.5, 2.0))   # pole ring groove
        mags = cup if mags is None else mags + cup
    add("High-temperature pot magnets, pair", mags, C_STEEL, "metal", 6, "shell", (0, 0, -45))

    sx, sy = P["standoff_xy"]
    st = None
    for ix in (-1, 1):
        for iy in (-1, 1):
            c = Pos(px + ix * sx, iy * sy, D["z_block1"]) * extrude(Circle(P["standoff_d"] / 2), amount=P["standoff_h"])
            st = c if st is None else st + c
    add("Insulating stand-offs, nylon, four", st, C_NYLON, "plastic", 13, "shell", (0, 0, 22))
    boot = _fillet_try(m[12], _bottom_edges(m[12]), [0.3])
    add("Silicone boot round the boss", boot, C_DARK, "rubber", 12, "shell", (0, 0, 40))

    # ---------------------------------------------------------------- internals (3, 4, 7, 12)
    zb = D["z_floor_in"] + P["board_standoff"]
    cx, cy = P["controller_xy"]
    c = P["controller"]
    pcb = _prism(c[0], c[1], 1.0, zb, c[2], x=px + cx, y=cy)
    add("Controller board, ESP32-S3", pcb, C_PCB_BLACK, "plastic", 3, "internal", (0, 0, 115))
    can = Pos(px + cx + 6, cy, zb + c[2]) * extrude(RectangleRounded(18, 18, 0.8), amount=3.2)
    can = _fillet_try(can, _top_edges(can), [0.4, 0.2])
    usbc = Pos(px + cx - c[0] / 2 + 3.2, cy, zb + c[2] + 1.6) * Box(7.2, 9.0, 3.2)
    usbc = _fillet_try(usbc, usbc.edges().filter_by(Axis.X), [1.2, 0.8])
    add("ESP32-S3 module shield and USB-C", can + usbc, C_STEEL, "metal", 3, "internal", (0, 0, 115))
    antenna = Pos(px + cx + 20, cy, zb + c[2] + 0.1) * Box(7.0, 16.0, 0.2)
    add("Module antenna print", antenna, C_ACCENT, "painted", 3, "internal", (0, 0, 115))

    ix_, iy_ = P["interface_xy"]
    i = P["interface"]
    perf = _prism(i[0], i[1], 1.0, zb, i[2], x=px + ix_, y=iy_)
    add("Interface board (perfboard)", perf, C_PCB_GREEN, "plastic", 7, "internal", (0, 0, 115))
    zi = zb + i[2]
    jack = Pos(px + ix_ + 14, iy_, zi + 3) * Box(8, 12, 6)
    jack = _fillet_try(jack, jack.edges().filter_by(Axis.Z), [1.0, 0.5])
    term = Pos(px + ix_ - 12, iy_ + 6, zi + 4) * Box(10, 7.5, 8)
    chips = Pos(px + ix_, iy_ - 6, zi + 1.0) * Box(6, 4, 2)
    add("Interface jack and terminal block", jack + term + chips, C_CHIP, "plastic", 7, "internal", (0, 0, 115))
    caps = None
    for k, (dx, dy) in enumerate([(-2, 6), (4, 6), (-10, -6), (6, -8)]):
        cc = Pos(px + ix_ + dx, iy_ + dy, zi) * extrude(Circle(2.0), amount=5.0)
        cc = _fillet_try(cc, _top_edges(cc), [0.5, 0.3])
        caps = cc if caps is None else caps + cc
    add("Interface capacitors", caps, "#1E3A8A", "painted", 7, "internal", (0, 0, 115))

    ab = P["accel_board"]
    apcb = _prism(ab[0], ab[1], 1.0, D["z_boss_top"], ab[2], x=px + bx)
    add("Accelerometer adapter board", apcb, C_PCB_PURPLE, "plastic", 4, "internal", (0, 0, 95))
    achip = Pos(px + bx, 0, D["z_boss_top"] + ab[2] + 0.5) * Box(4, 4, 1.0)
    achip += Pos(px + bx - 6, 0, D["z_boss_top"] + ab[2] + 1.25) * Box(2.5, 10, 2.5)
    add("IIS3DWB-class accelerometer", achip, C_CHIP, "plastic", 4, "internal", (0, 0, 95))

    spacers = None
    for (qx, qy, hw, hl) in ((cx, cy, 21.0, 8.0), (ix_, iy_, 16.0, 10.0)):
        for sgx in (-1, 1):
            for sgy in (-1, 1):
                h = Pos(px + qx + sgx * hw, qy + sgy * hl, D["z_floor_in"]) * \
                    extrude(RegularPolygon(2.6, 6), amount=P["board_standoff"])
                spacers = h if spacers is None else spacers + h
    add("Brass board spacers", spacers, C_BRASS, "metal", 12, "internal", (0, 0, 100))

    # ---------------------------------------------------------------- current clamp (BOM 8)
    ctx, cty, ctz = P["ct_pos"]
    ct_r, ct_t, ap = P["ct_od"] / 2, P["ct_t"], P["ct_aperture"] / 2
    ring = Pos(ctx, cty, ctz) * Rot(90, 0, 0) * (Cylinder(ct_r, ct_t) - Cylinder(ap, ct_t + 2))
    ring = _fillet_try(ring, ring.edges(), [2.5, 1.5, 0.8])
    lat = P["ct_latch"]
    latch = Pos(ctx, cty, ctz + ct_r + lat[2] / 2 - 4) * Box(*lat)
    latch = _fillet_try(latch, latch.edges(), [2.0, 1.2, 0.6])
    ct = ring + latch
    ct -= Pos(ctx, cty, ctz) * Box(0.7, ct_t + 4, 2 * ct_r + 30)          # split-core seam
    ct -= Pos(ctx, cty, ctz + ct_r + lat[2] - 4) * Box(12, 3, 2.4)        # latch finger recess
    CT_EX = (-60, -60, 20)
    add("Split-core current transformer", ct, C_DARK, "plastic", 8, "shell", CT_EX)
    face = Plane(origin=(0, 0, 0), x_dir=(-1, 0, 0), z_dir=(0, 1, 0))     # +Y face, seen in hero and detail
    mark = Pos(ctx, cty + ct_t / 2, ctz - ct_r + 11.0) * (face * extrude(Text("30 A : 1 V", 4.0), amount=0.2))
    mark += Pos(ctx, cty + ct_t / 2, ctz - ct_r + 6.8) * (face * extrude(Text("VOLTAGE OUTPUT", 2.0), amount=0.2))
    add("Clamp rating marking", mark, "#D1D5DB", "painted", 8, "shell", CT_EX)
    rz = ctz + ct_r + lat[2] / 2 - 4
    relief = Pos(ctx + 4, cty - ct_t / 2, rz) * Rot(90, 0, 0) * Cone(3.2, 2.4, 9.0, align=None)
    add("Clamp cable strain relief", relief, C_DARK, "rubber", 8, "shell", CT_EX)

    # ---------------------------------------------------------------- temperature probe (BOM 9)
    pc = P["probe_clip"]
    prx = P["probe_x"]
    clip = Pos(prx, 0, 0) * extrude(RectangleRounded(pc[0], pc[1], 3.0), amount=pc[2])
    clip = _fillet_try(clip, _top_edges(clip), [1.5, 1.0, 0.5])
    zs = pc[2] + P["probe_d"] / 2 - 1
    clip -= Pos(prx, 0, zs) * Rot(90, 0, 0) * Cylinder(P["probe_d"] / 2 + 0.1, pc[1] + 2)
    strap = Pos(prx, 0, zs) * Rot(90, 0, 0) * (Cylinder(P["probe_d"] / 2 + 1.4, 5.0) - Cylinder(P["probe_d"] / 2 + 0.1, 6.0))
    strap &= Pos(prx, 0, zs + 5) * Box(pc[0], 8, 10)
    strap += Pos(prx - pc[0] / 2 + 2.5, 0, pc[2] - 0.5) * Box(5, 5, 1.0) + Pos(prx + pc[0] / 2 - 2.5, 0, pc[2] - 0.5) * Box(5, 5, 1.0)
    PR_EX = (35, -85, 25)
    add("Probe magnetic clip", clip, C_DARK, "plastic", 9, "shell", PR_EX)
    add("Probe retaining strap", strap, C_STEEL, "metal", 9, "shell", PR_EX)
    pl = P["probe_len"]
    sleeve = Pos(prx, 0, zs) * Rot(90, 0, 0) * Cylinder(P["probe_d"] / 2, pl)
    sleeve = _fillet_try(sleeve, sleeve.faces().sort_by(Axis.Y)[0].edges(), [1.5, 1.0])
    sleeve += Pos(prx, pl / 2 - 3, zs) * Rot(90, 0, 0) * Cylinder(P["probe_d"] / 2 + 0.4, 1.2)   # crimp ring
    add("Stainless probe sleeve, DS18B20", sleeve, C_ALU, "metal", 9, "shell", PR_EX)
    pboot = Pos(prx, pl / 2 + 3, zs) * Rot(-90, 0, 0) * Cone(3.0, 2.2, 6.0)
    add("Probe heat-shrink boot", pboot, C_CABLE, "rubber", 9, "shell", PR_EX)

    # ---------------------------------------------------------------- accessories (10, 11)
    pads = None
    for mx in D["mag_x"]:
        d = Pos(px + mx, 0, -3.0) * extrude(Circle(17.5), amount=3.0)
        d = _fillet_try(d, _top_edges(d), [0.6, 0.3])
        pads = d if pads is None else pads + d
    add("Steel adhesive mounting pads, two", pads, "#4B5563", "painted", 11, "accessory", (0, 0, -85))
    ax, ay, az0 = 70.0, -40.0, -70.0                       # beside the clamp in the exploded view
    ad = Pos(ax, ay, az0) * extrude(RectangleRounded(46, 46, 6), amount=28)
    ad = _fillet_try(ad, _top_edges(ad), [5.0, 3.0, 1.5])
    ad = _fillet_try(ad, _bottom_edges(ad), [1.5, 1.0])
    ad -= Pos(ax - 23, ay, az0 + 14) * Box(3.0, 9.4, 3.6)
    add("USB-C power adapter, 5 V", ad, C_WHITE, "plastic", 10, "accessory", (0, 0, 0))
    plug = _cable([(ax - 35, ay, az0 + 14), (ax - 52, ay + 4, az0 + 12), (ax - 64, ay + 16, az0 + 6),
                   (ax - 70, ay + 34, az0 + 2)], 2.0, (-1, 0, 0), (0, 1, 0))
    plug += Pos(ax - 29, ay, az0 + 14) * Box(12, 8.4, 4.0)
    add("USB-C cable and plug", plug, C_CABLE, "rubber", 10, "accessory", (0, 0, 0))

    # ---------------------------------------------------------------- context: motor, conductor, leads
    add("7.5 kW class motor (clay)", motor_context(P), C_CLAY, "clay", None, "context", (0, 0, 0))
    zf = -P["motor_r"] - 150 - 30                                  # underside of the motor feet
    tw = P["tbox"][1]
    cond = _cable([(ctx, tw / 2 + 40, ctz), (ctx, 200, ctz), (ctx, 250, ctz - 30), (ctx, 262, ctz - 110),
                   (ctx, 262, zf)], 5.5, (0, 1, 0), (0, 0, -1))
    add("Phase conductor (insulated)", cond, C_COND, "rubber", None, "context", (0, 0, 0))
    gxp = px + L / 2 + gl
    gxn = px - L / 2 - gl
    ct_lead = _cable([(gxp, 12, gz), (gxp + 18, 26, gz - 4), (32, 70, 34), (62, 112, 54),
                      (ctx + 4, cty - ct_t / 2 - 9, rz)], 2.2, (1, 0, 0), (0, 1, 0))
    probe_lead = _cable([(prx, pl / 2 + 5.5, zs), (prx, pl / 2 + 16, zs + 4), (prx + 8, 26, 28),
                         (gxn - 10, 5, gz), (gxn, 2.6, gz)], 2.0, (0, 1, 0), (1, 0, 0))
    usb = _cable([(gxn, -2.6, gz), (gxn - 14, -12, gz - 3), (-162, -60, 20), (-168, -120, -30),
                  (-172, -152, -120), (-172, -156, zf)], 2.2, (-1, 0, 0), (0, 0, -1))
    add("Clamp, probe and USB leads", ct_lead + probe_lead + usb, C_CABLE, "rubber", None, "context", (0, 0, 0))
    return out


if __name__ == "__main__":
    for p in product_parts():
        s = p["shape"]
        print(f"{p['name']:40s} {p['group']:9s} {p['material']:8s} valid={s.is_valid} vol={s.volume / 1000:8.2f} cm3")
