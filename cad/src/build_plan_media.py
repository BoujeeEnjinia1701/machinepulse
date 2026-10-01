"""MachinePulse prototype build plan pictures (MPL-BLD-001, STANDARDS section 18).

Run from the repo root:  python cad/src/build_plan_media.py [overview|sheets|layouts|joints|steps|wiring ...]
With no argument it draws everything. Every picture is drawn from cad/src/model.py
(build_components), so the pictures and the model never disagree:
    docs/05-build-plan/overview.png        every component pulled apart, numbered in build order
    cad/drawings/MPL-DWG-101 to 106        making sketches for the made and drilled components
    docs/05-build-plan/base-holes.png      drilling layout of the box base (matplotlib)
    docs/05-build-plan/joint-NN.png        close-ups of the joints that need explaining
    docs/05-build-plan/step-NN.png         one picture per assembly step
    docs/05-build-plan/wiring.png          block-level wiring with wire sizes (matplotlib)
Uses .kit/build_views.py. BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / ".kit"), str(ROOT / "cad" / "src")]
import build_views as bv  # noqa: E402
from build_views import Part  # noqa: E402
from model import PARAMS as P, build_components, build_parts, derived, motor_context, leads  # noqa: E402

OUT = ROOT / "docs" / "05-build-plan"
DWG = ROOT / "cad" / "drawings"
DATE = "2026-10-01"
REPO = "github.com/BoujeeEnjinia1701/machinepulse"
D = derived(P)
C = {k: v[2] for k, v in build_components(P).items()}

COL = {"block": "#9CA3AF", "boss": "#475569", "magnets": "#1F2937", "screw": "#111827", "standoffs": "#F5F5F4",
       "base": "#E0B84A", "glands": "#1F2937", "grommet": "#DC2626", "accel": "#B45309", "cso": "#A16207",
       "carrier": "#2563EB", "parts": "#1E3A8A", "controller": "#0F766E", "pipe": "#FDE047", "lid": "#FDE68A",
       "clip": "#57534E", "clipmag": "#374151", "probe": "#C2410C", "pad": "#F472B6", "ct": "#1F2937",
       "frame": "#C8CDD3"}


def _fuse(shapes):
    out = None
    for s in shapes:
        out = s if out is None else out + s
    return out


def S(*ks):
    return _fuse([C[k] for k in ks])


def part(name, shape, color, explode=(0, 0, 0), alpha=1.0):
    return Part(name, shape, color, None, tuple(explode), alpha)


def frame_slab(x=0.0, y=0.0, w=80.0, d=60.0):
    """A small piece of the painted steel frame for close-ups (context, not in the BOM)."""
    import build123d as b
    return b.Pos(x, y, -4) * b.Box(w, d, 8)


def win(sh, x0, x1, y0, y1, z0, z1):
    import build123d as b
    return sh & (b.Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * b.Box(x1 - x0, y1 - y0, z1 - z0))


# ----------------------------------------------------------------- named parts, in build order
def made():
    return {
        "block": part("Sensor block", C["block"], COL["block"]),
        "magnets": part("Pot magnets (2)", C["magnets"], COL["magnets"]),
        "boss": part("Boss and its M6 set screw", S("boss", "set_screw"), COL["boss"]),
        "standoffs": part("Nylon stand-offs (4)", C["standoffs"], COL["standoffs"]),
        "base": part("Box base, drilled", C["base"], COL["base"]),
        "glands": part("Cable glands (3)", S("gland_ct", "gland_probe", "gland_power"), COL["glands"]),
        "grommet": part("Silicone grommet", C["grommet"], COL["grommet"]),
        "so_screws": part("Nylon screws (4)", C["standoff_screws"], COL["screw"]),
        "accel": part("Accelerometer board", C["accel"], COL["accel"]),
        "cso": part("Carrier stand-offs and screws", S("carrier_standoffs", "carrier_screws"), COL["cso"]),
        "carrier": part("Carrier board with its parts", S("carrier", "interface_parts", "sockets"), COL["carrier"]),
        "controller": part("Controller board", C["controller"], COL["controller"]),
        "pipe": part("Light pipe", C["light_pipe"], COL["pipe"]),
        "lid": part("Lid, drilled", C["lid"], COL["lid"]),
        "clip": part("Probe clip and its magnets", S("probe_clip", "clip_magnets"), COL["clip"]),
        "probe": part("Probe and thermal pad", S("probe", "pad"), COL["probe"]),
        "ct": part("Current transformer", C["ct"], COL["ct"]),
    }


# ----------------------------------------------------------------- overview
def overview():
    M = made()
    off = {"block": (0, 0, 0), "magnets": (0, 0, -45), "boss": (0, 0, 40), "standoffs": (0, 0, 22),
           "base": (0, 0, 95), "glands": (0, 0, 95), "grommet": (0, 0, 70), "so_screws": (0, 0, 150),
           "accel": (0, 0, 190), "cso": (0, 0, 215), "carrier": (0, 0, 240), "controller": (0, 0, 280),
           "pipe": (0, 0, 315), "lid": (0, 0, 355), "clip": (0, -40, 0), "probe": (0, -40, 28), "ct": (110, 40, 230)}
    parts = []
    for k in off:
        p = M[k]
        p.explode = off[k]
        parts.append(p)
    # spread the glands out from the walls so they read as separate parts
    import build123d as b
    g = parts[[q.name for q in parts].index("Cable glands (3)")]
    g.shape = _fuse([b.Pos(28, 0, 0) * C["gland_ct"], b.Pos(-28, 0, 0) * C["gland_probe"], b.Pos(-28, 0, 0) * C["gland_power"]])
    return bv.overview(parts, OUT / "overview.png", "MachinePulse prototype: every component, pulled apart",
                       subtitle="Numbered in build order. Pod in the middle, probe and clip in front, current transformer behind",
                       elev=20, azim=-58, size=(11, 9), dpi=150, key=True)


# ----------------------------------------------------------------- making sketches
def sheets():
    import build123d as b
    M = made()
    base = dict(project="MachinePulse", date=DATE)
    out = []
    z0, zb0, zb1 = D["z_box0"], D["z_block0"], D["z_block1"]

    out.append(bv.component_sheet(
        Part("Sensor block", C["block"], COL["block"]), [M["magnets"], M["boss"], M["standoffs"]],
        dwg_no="MPL-DWG-101", title="MachinePulse sensor block: making sketch",
        material="Aluminium plate 10 mm, 6061 or clean scrap", view_shape=b.Pos(0, 0, -zb0) * C["block"],
        notes=["Cut a 76 x 36 mm blank from 10 mm aluminium plate; file the",
               "  edges square and flat. Front view: the long face; top: the top face.",
               "Mark a centre line both ways. Sizes are from those centre lines.",
               "Magnet holes: two, 20 mm each side of centre on the long centre line.",
               "  Drill 5.0 mm through and tap M6 through. The left one (boss end)",
               "  also takes the boss's set screw from the top.",
               "Stand-off holes: four, 33 mm each side and 13 mm each side.",
               "  Drill 2.5 mm through and tap M3 through.",
               "Use a drill press so the holes are square to the faces.",
               "Deburr; the top face must stay flat: the boss and stand-offs sit on it.",
               "Fit: magnets screw in from below, the boss on top over the left",
               "  magnet, the four stand-offs on top at the corners.",
               "Check: an M6 screw turns in both holes by hand, square to the face."],
        inset_view=(-25, -58), **base))

    out.append(bv.component_sheet(
        Part("Boss", C["boss"], COL["boss"]), [M["block"], M["magnets"], M["accel"], M["grommet"]],
        dwg_no="MPL-DWG-102", title="MachinePulse sensor boss: making sketch",
        material="Aluminium round bar 20 mm, 6061 or 6082", view_shape=b.Pos(-P["boss_x"], 0, -zb1) * C["boss"],
        notes=[f"Saw an {D['boss_h']:.0f} mm length off 20 mm round bar, leaving a little to file.",
               f"File both ends flat and square to the bar until it is {D['boss_h']:.0f} mm long.",
               "  Check squareness with an engineer's square on a flat plate.",
               "Centre punch the bottom end. In a drill press, with the bar held",
               "  upright in a V-block, drill 5.0 mm, 8 mm deep, and tap M6 8 deep.",
               "The top end stays solid: the accelerometer board is bonded to it.",
               "Break the sharp edges lightly; do not round the top face.",
               "Fit: an M6 x 12 set screw goes half into the block's left magnet",
               "  hole and half into the boss, with medium threadlocker. Screw the",
               "  boss down hard so its bottom face sits flat on the block.",
               "The boss rises through the box floor hole and its grommet;",
               "  its top is 3.5 mm above the inside of the box floor.",
               "Check: boss upright on the block, no rocking, top face flat."],
        inset_view=(24, -58), **base))

    out.append(bv.component_sheet(
        Part("Box base", C["base"], COL["base"]), [M["block"], M["standoffs"], M["glands"], M["carrier"]],
        dwg_no="MPL-DWG-103", title="MachinePulse box base: drilling sketch",
        material="Bought IP54 ABS box 100 x 68 x 40 mm (base 28 mm)", view_shape=b.Pos(0, 0, -z0) * C["base"],
        notes=["A stock ABS box base with four moulded corner pillars. Drill only.",
               "Sizes are from the box's centre lines; the drilling layout repeats them.",
               "Floor, 24 mm boss hole: 20 mm left of centre, on the centre line.",
               "Floor, four 3.2 mm stand-off screw holes: 33 mm each side, 13 mm",
               "  each side of the centre line.",
               "Floor, four 3.2 mm carrier screw holes: 3.5 mm left of centre and",
               "  35 mm right of centre, 25 mm each side of the centre line.",
               "Left end wall: two 12.2 mm gland holes 13 mm each side of centre.",
               "Right end wall: one 16.2 mm gland hole on the centre line.",
               "  Gland centres 15.5 mm up from the underside of the box.",
               "Tape the face, pilot 3 mm slowly with wood behind, open with a step",
               "  drill at low speed, light pressure. Deburr inside and out.",
               "Check: each gland seats flat; the floor holes match the block's."],
        inset_view=(30, -58), **base))

    out.append(bv.component_sheet(
        Part("Lid", C["lid"], COL["lid"]), [M["base"], M["pipe"], M["carrier"]],
        dwg_no="MPL-DWG-104", title="MachinePulse lid: drilling sketch",
        material="Lid of the bought IP54 ABS box (lid 12 mm)", view_shape=b.Pos(0, 0, -D["z_lid0"]) * C["lid"],
        notes=["The lid of the same stock box, with its four corner screws.",
               "One hole for the light pipe, 3.2 mm. Mark it on the outside face:",
               "  30 mm from the centre toward the right (CT gland) end and",
               "  20 mm from the centre toward the front edge.",
               "Drill at low speed with wood behind; deburr both faces.",
               "Check the light pipe's datasheet: some need a 3.0 mm press-fit hole.",
               "Fit: the light pipe pushes up through the hole from inside until",
               "  its bezel sits on the lid's top face; a drop of silicone",
               "  sealant under the bezel keeps the box IP54.",
               "The lid goes on last, its own gasket clean, with the box's four",
               "  screws tightened evenly in a cross pattern.",
               "Check: the light pipe stands upright and lines up with the LED."],
        inset_view=(30, -58), **base))

    out.append(bv.component_sheet(
        Part("Carrier board", C["carrier"], COL["carrier"]), [M["cso"], part("Box base", C["base"], COL["base"])],
        dwg_no="MPL-DWG-105", title="MachinePulse carrier board: making sketch",
        material="Perfboard 1.6 mm, 2.54 mm pitch, cut to 45 x 56 mm",
        view_shape=b.Pos(-P["interface_xy"][0], 0, -D["z_carrier"]) * S("carrier", "sockets", "interface_parts"), inset_view=(65, -58),
        notes=["Cut a 45 x 56 mm piece of perfboard; file the edges smooth.",
               "Four 3.2 mm holes, 3.5 mm in from the left edge, 3 mm from the right,",
               "  3 mm in from the front and back edges (38.5 x 50 mm apart).",
               "Left part: two 20-pin header sockets 19.4 mm apart (centre to",
               "  centre), 51 mm long, for the controller board.",
               "Right part: the 3.5 mm jack for the CT facing the right end,",
               "  the 5 V and probe screw terminals, the button, and the LED",
               "  30 mm right of the box centre and 20 mm toward the front.",
               "Interface circuit as the wiring diagram: 1.50 V bias divider and",
               "  filter for the CT, series resistor and clamp diodes.",
               "Fit: on four 5 mm hex stand-offs screwed to the box floor;",
               "  the board stays 4 mm clear of the right gland nut.",
               "Check: continuity and no shorts before the controller goes in."],
        **base))

    clip = S("probe_clip")
    out.append(bv.component_sheet(
        Part("Probe clip", clip, COL["clip"]), [part("Probe", C["probe"], COL["probe"]), part("Pad", C["pad"], COL["pad"]),
                                                part("Magnets", C["clip_magnets"], COL["clipmag"])],
        dwg_no="MPL-DWG-106", title="MachinePulse probe clip: making sketch",
        material="Aluminium flat bar 16 x 10 mm, 6061 or 6082", view_shape=b.Pos(0, 95, 0) * clip,
        notes=["Cut 42 mm off 16 x 10 mm bar; file the ends square.",
               "Groove across the 16 mm width on the underside, in the middle:",
               "  6.2 mm wide, 6.5 mm deep. Saw two cuts, chisel or file out",
               "  between them, and check depth with the probe sleeve and pad.",
               "Two magnet pockets on the underside, 13 mm each side of centre:",
               "  12.2 mm across, 3 mm deep, with a flat-bottomed drill or an",
               "  end mill in the drill press.",
               "Bond a 12 x 3 mm high-temperature disc magnet in each pocket with",
               "  high-temperature epoxy, flush with the underside; same pole down.",
               "Fit: the sleeve lies in the groove on its 0.5 mm thermal pad;",
               "  the magnets pull the clip onto the frame and press the sleeve",
               "  down on the pad. The lead leaves along the groove.",
               "Check: on a steel plate the clip sits flat and the sleeve cannot slide."],
        inset_view=(-30, -60), **base))
    return out


# ----------------------------------------------------------------- drilling layout
def layouts():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle
    INK, MUT, AC = "#111827", "#4B5563", "#0F766E"
    L, W, H = P["box"]
    base_h = H - P["lid_h"]
    fig = plt.figure(figsize=(12, 7.6), dpi=150)
    ax = fig.add_axes([0.03, 0.10, 0.56, 0.74]); ax.set_aspect("equal"); ax.set_axis_off()
    # floor seen from inside, from above; front (the LED side) at the bottom of the page
    ax.add_patch(Rectangle((-L / 2, -W / 2), L, W, fc="#FEF3C7", ec=INK, lw=1.2))
    ax.add_patch(Rectangle((-L / 2 + 2.5, -W / 2 + 2.5), L - 5, W - 5, fc="none", ec=MUT, lw=0.5, ls="--"))
    ax.plot([0, 0], [-W / 2, W / 2], color=MUT, lw=0.5, ls=(0, (8, 3, 2, 3))); ax.plot([-L / 2, L / 2], [0, 0], color=MUT, lw=0.5, ls=(0, (8, 3, 2, 3)))
    px, py = D["pillar_xy"]
    for sx in (-1, 1):
        for sy in (-1, 1):
            ax.add_patch(Circle((sx * px, sy * py), P["pillar_d"] / 2, fc="#E5E7EB", ec=MUT, lw=0.6))
    bx = P["boss_x"]
    ax.add_patch(Circle((bx, 0), P["floor_hole_d"] / 2, fc="white", ec=INK, lw=1.1))
    ax.text(bx, -15.5, "24 boss hole", ha="center", va="top", fontsize=7.5, color=INK)
    sx_, sy_ = P["standoff_xy"]
    for x in (-sx_, sx_):
        for y in (-sy_, sy_):
            ax.add_patch(Circle((x, y), 1.6, fc="white", ec=INK, lw=1))
    for (x, y) in P["carrier_holes"]:
        for s in (-1, 1):
            ax.add_patch(Circle((x, s * y), 1.6, fc="#DBEAFE", ec=INK, lw=1))
    # dimension figures along the edges
    for i, x in enumerate(sorted({bx, -sx_, sx_, P["carrier_holes"][0][0], P["carrier_holes"][1][0]})):
        ax.plot([x, x], [-W / 2, -W / 2 - 4 - 6 * (i % 2)], color=AC, lw=0.4, ls=":")
        ax.text(x, -W / 2 - 5 - 6 * (i % 2), f"{x:+g}", ha="center", va="top", fontsize=7.5, color=AC)
    ax.text(0, -W / 2 - 18, "sideways from the centre, mm (+ toward the right end)", ha="center", fontsize=8, color=MUT)
    for i, y in enumerate(sorted({0, -sy_, sy_, -P["carrier_holes"][0][1], P["carrier_holes"][0][1]})):
        ax.plot([-L / 2, -L / 2 - 4], [y, y], color=AC, lw=0.4, ls=":")
        ax.text(-L / 2 - 5, y, f"{y:+g}", ha="right", va="center", fontsize=7.5, color=AC)
    ax.text(-L / 2 - 17, 0, "from the centre, mm (+ toward the back)", rotation=90, ha="center", va="center", fontsize=8, color=MUT)
    ax.text(-L / 2, W / 2 + 3, "LEFT END (probe and power glands)", ha="left", va="bottom", fontsize=7.5, color=MUT)
    ax.text(L / 2, W / 2 + 3, "RIGHT END (CT gland)", ha="right", va="bottom", fontsize=7.5, color=MUT)
    ax.text(15, -W / 2 + 4, "front edge", ha="center", va="bottom", fontsize=7, color=MUT)
    ax.set_xlim(-L / 2 - 22, L / 2 + 4); ax.set_ylim(-W / 2 - 22, W / 2 + 9)
    fig.text(0.03, 0.88, "Floor, seen from inside the box", fontsize=10, fontweight="bold", color=INK)
    # end walls, seen from outside
    for k, (title, glands, xo) in enumerate((("Left end wall, seen from outside", ("probe", "power"), 0.62),
                                             ("Right end wall, seen from outside", ("ct",), 0.62))):
        a2 = fig.add_axes([xo, 0.50 - 0.38 * k, 0.35, 0.30]); a2.set_aspect("equal"); a2.set_axis_off()
        a2.add_patch(Rectangle((-W / 2, 0), W, base_h, fc="#FEF3C7", ec=INK, lw=1.2))
        a2.plot([-W / 2, W / 2], [2.5, 2.5], color=MUT, lw=0.5, ls="--")
        zg = P["gland_above_base"]
        for g in glands:
            end, gy, thr, hole, bd, blen, af = P["glands"][g]
            # seen from outside the left end, +Y (back) is on the left; from outside the right end it is on the right
            u = -gy if end < 0 else gy
            a2.add_patch(Circle((u, zg), hole / 2, fc="white", ec=INK, lw=1.1))
            a2.add_patch(Circle((u, zg), af / 2, fc="none", ec=MUT, lw=0.6, ls="--"))
            name = {"probe": "probe", "power": "power", "ct": "CT"}[g]
            a2.text(u, base_h + 1.5, f"{name}\n{hole:g} hole ({thr})", ha="center", va="bottom", fontsize=7, color=INK, linespacing=1.2)
            if gy != 0:
                a2.text(u, -2, f"{abs(gy):g} {'back' if gy > 0 else 'front'}", ha="center", va="top", fontsize=7, color=AC)
        a2.plot([W / 2, W / 2 + 4], [zg, zg], color=AC, lw=0.4, ls=":")
        a2.text(W / 2 + 5, zg, f"{zg:g} up from\nthe underside", ha="left", va="center", fontsize=7, color=AC)
        a2.set_xlim(-W / 2 - 3, W / 2 + 26); a2.set_ylim(-9, base_h + 12)
        fig.text(xo, 0.50 - 0.38 * k + 0.32, title, fontsize=10, fontweight="bold", color=INK)
    fig.text(0.03, 0.975, "Box base: drilling layout", fontsize=13, fontweight="bold", color=INK, va="top")
    fig.text(0.03, 0.94, "Full size figures in mm, taken from the model. White: holes to drill (3.2 mm unless marked). "
             "Blue: carrier screw holes. Grey: the box's moulded pillars.\nDashed circle on the end walls: the gland's nut, "
             "which must clear the floor and the pillars.", fontsize=8.2, color=MUT, va="top")
    fig.text(0.03, 0.015, "BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT", fontsize=7, color="#B45309")
    fig.text(0.97, 0.015, REPO, fontsize=7, color=AC, ha="right", family="monospace")
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "base-holes.png", facecolor="white"); plt.close(fig)
    return OUT / "base-holes.png"


# ----------------------------------------------------------------- joints
def joint(parts, out, title, subtitle=None, elev=24, azim=-58, size=(8, 6), dpi=160, at=None):
    """bv.joint with optional leader end points: at = {part name: (x, y, z)} in model mm, so two
    parts whose default anchors fall on the same spot get their own leaders."""
    parts = [p for p in parts if bv._has_volume(p.shape)]
    W, H = int(size[0] * dpi), int(size[1] * dpi * bv.PIC_HEIGHT)
    img, proj, verts = bv._raster([(p, p.color, p.alpha, (0, 0, 0)) for p in parts], elev, azim, W, H)
    fig, ax = bv._frame(size, dpi, title, subtitle)
    ax.imshow(img, interpolation="bilinear")
    at = at or {}
    pts = [at.get(p.name, None) for p in parts]
    pts = [bv._anchor(v) if pt is None else pt for pt, v in zip(pts, verts)]
    bv._draw_labels(ax, proj, pts, [p.name for p in parts], W, H)
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor="white"); bv.plt.close(fig)
    return out


def joints():
    out = []
    bx = P["boss_x"]
    z0 = D["z_box0"]
    # 01 magnet, block, set screw and boss, cut through the boss centre (keep the back half)
    w_ = (bx - 22, bx + 22, 0, 25, -1, D["z_boss_top"] + 3)
    zb1 = D["z_block1"]
    out.append(joint([
        part("Pot magnet with its stud", win(C["magnets"], *w_), COL["magnets"]),
        part("Sensor block (tapped M6)", win(C["block"], *w_), COL["block"]),
        part("M6 set screw", win(C["set_screw"], *w_), "#B91C1C"),
        part("Boss (tapped M6, 8 deep)", win(C["boss"], *w_), "#475569")],
        OUT / "joint-01.png", "Joint 1: magnet, sensor block and boss (cut through the boss)",
        subtitle="Seen from the front, cut open. The stud and the set screw share the block's tapped hole; faces meet flat",
        elev=8, azim=-90, size=(8, 6),
        at={"Boss (tapped M6, 8 deep)": (bx - 8, 0, zb1 + 8), "M6 set screw": (bx, 0, zb1 + 2),
            "Sensor block (tapped M6)": (bx - 14, 0, zb1 - 5), "Pot magnet with its stud": (bx - 10, 0, 4)}))
    # 02 stand-off, cut through the front left stand-off
    x, y = -P["standoff_xy"][0], -P["standoff_xy"][1]
    w_ = (x - 10, x + 10, y, y + 12, D["z_block0"] - 1, D["z_floor_in"] + 4)
    out.append(joint([
        part("Sensor block (tapped M3)", win(C["block"], *w_), COL["block"]),
        part("Nylon stand-off, 5 mm", win(C["standoffs"], *w_), "#D6D3D1"),
        part("Box floor", win(C["base"], *w_), COL["base"]),
        part("M3 nylon screw", win(C["standoff_screws"], *w_), COL["screw"])],
        OUT / "joint-02.png", "Joint 2: box floor on a nylon stand-off (cut through it)",
        subtitle="Seen from the front, cut open. The 5 mm gap under the floor is the heat break",
        elev=8, azim=-90, size=(8, 6),
        at={"Box floor": (x - 7, y, D["z_floor_in"] - 1), "M3 nylon screw": (x + 1, y, D["z_floor_in"] + 1.5),
            "Nylon stand-off, 5 mm": (x + 2.4, y, D["z_block1"] + 2.5), "Sensor block (tapped M3)": (x - 5, y, D["z_block0"] + 4)}))
    # 03 grommet and accelerometer on the boss, cut
    w_ = (bx - 22, bx + 22, 0, 22, D["z_block1"] - 3, D["z_boss_top"] + 5)
    out.append(joint([
        part("Boss", win(C["boss"], *w_), COL["boss"]),
        part("Box floor", win(C["base"], *w_), COL["base"]),
        part("Silicone grommet", win(C["grommet"], *w_), COL["grommet"]),
        part("Accelerometer board, bonded", win(C["accel"], *w_), COL["accel"]),
        part("Sensor block", win(C["block"], *w_), COL["block"])],
        OUT / "joint-03.png", "Joint 3: boss through the floor, grommet and accelerometer (cut)",
        subtitle="Seen from the front, cut open. The boss never touches the floor; the grommet seals the gap",
        elev=5, azim=-90, size=(8, 6),
        at={"Box floor": (bx + 18, 0, z0 + 1.2), "Silicone grommet": (bx + 11, 0, z0 + 1.2), "Boss": (bx + 5, 0, D["z_block1"] + 6),
            "Accelerometer board, bonded": (bx - 6, 0, D["z_boss_top"] + 0.8), "Sensor block": (bx - 15, 0, D["z_block1"] - 1.5)}))
    # 04 carrier on its stand-off (back right corner), cut
    x, y = P["carrier_holes"][1]
    w_ = (x - 12, x + 4, y, y + 6, z0 - 3, D["z_carrier_top"] + 4)
    out.append(joint([
        part("Box floor", win(C["base"], *w_), COL["base"]),
        part("Hex stand-off, 5 mm", win(C["carrier_standoffs"], *w_), COL["cso"]),
        part("M3 screws, below and above", win(C["carrier_screws"], *w_), COL["screw"]),
        part("Carrier board", win(C["carrier"], *w_), COL["carrier"])],
        OUT / "joint-04.png", "Joint 4: carrier board on a stand-off (back right corner, cut)",
        subtitle="Seen from the front, cut open. One M3 screw from under the floor, one from above the board",
        elev=8, azim=-90, size=(8, 6),
        at={"Box floor": (x - 8, y, z0 + 1.2), "Hex stand-off, 5 mm": (x + 2.2, y, D["z_floor_in"] + 2.5),
            "Carrier board": (x - 7, y, D["z_carrier"] + 0.8), "M3 screws, below and above": (x, y, D["z_carrier_top"] + 1.2)}))
    # 05 glands in the left end wall, cut level with their centres (lower half kept), seen from above
    zg = D["z_gland"]
    L = P["box"][0]
    w_ = (-L / 2 - 20, -L / 2 + 12, -24, 24, z0 - 1, zg)
    out.append(joint([
        part("Box base, left end", win(C["base"], *w_), COL["base"]),
        part("M12 gland: probe (back)", win(C["gland_probe"], *w_), COL["glands"]),
        part("M12 gland: power (front)", win(C["gland_power"], *w_), "#475569")],
        OUT / "joint-05.png", "Joint 5: the two glands in the left end wall (cut level with them)",
        subtitle="Seen from above, cut open. Body and seal outside, nut inside; nuts clear the floor and the corner pillars",
        elev=82, azim=-90, size=(8, 6),
        at={"Box base, left end": (-L / 2 + 1.2, -22, zg), "M12 gland: probe (back)": (-L / 2 - 10, 13 + 5, zg),
            "M12 gland: power (front)": (-L / 2 - 10, -13 - 5, zg)}))
    # 06 probe clip on the frame, cut across the sleeve
    y0 = -95
    w_ = (-24, 24, y0, y0 + 25, -4, 11)
    out.append(joint([
        part("Motor frame (painted steel)", win(frame_slab(0, y0), *w_), COL["frame"]),
        part("Thermal pad, 0.5 mm", win(C["pad"], *w_), COL["pad"]),
        part("Probe sleeve", win(C["probe"], *w_), COL["probe"]),
        part("Probe clip", win(C["probe_clip"], *w_), COL["clip"]),
        part("High-temperature disc magnets", win(C["clip_magnets"], *w_), COL["clipmag"])],
        OUT / "joint-06.png", "Joint 6: probe clip on the frame (cut across the sleeve)",
        subtitle="Seen from the front, cut open. The magnets pull the clip down; the groove presses the sleeve on its pad",
        elev=5, azim=-90, size=(8, 6),
        at={"Motor frame (painted steel)": (-20, y0, -2), "Thermal pad, 0.5 mm": (2, y0, 0.25), "Probe sleeve": (1, y0, 4.5),
            "Probe clip": (-5, y0, 8.5), "High-temperature disc magnets": (13, y0, 1.5)}))
    # 07 light pipe through the lid, cut
    lx, ly = P["led_xy"]
    w_ = (lx - 12, lx + 12, ly, ly + 5, D["z_carrier"] - 1, D["z_top"] + 3)
    out.append(joint([
        part("Carrier board", win(C["carrier"], *w_), COL["carrier"]),
        part("Status LED", win(C["interface_parts"], *w_), COL["parts"]),
        part("Light pipe", win(C["light_pipe"], *w_), "#CA8A04"),
        part("Lid", win(C["lid"], *w_), COL["lid"])],
        OUT / "joint-07.png", "Joint 7: light pipe from the LED through the lid (cut)",
        subtitle="Seen from the front, cut open. The pipe stands on the LED; its bezel seals on the lid top",
        elev=6, azim=-90, size=(8, 6),
        at={"Lid": (lx - 9, ly, D["z_top"] - 1.2), "Light pipe": (lx, ly, (D["z_top"] + D["z_carrier_top"]) / 2),
            "Status LED": (lx + 0.5, ly, D["z_carrier_top"] + 1), "Carrier board": (lx - 9, ly, D["z_carrier"] + 0.8)}))
    return out


# ----------------------------------------------------------------- assembly steps
def step(done, new, out, title, subtitle=None, context=(), elev=24, azim=-58, size=(8, 6), dpi=160,
         label_done=True, at=None, arrows=None):
    """bv.step with optional leader end points (at = {name: (x, y, z)} in fitted position, before the
    pull-back) and a choice of which new parts get an arrow (arrows = list of names; default all)."""
    import numpy as np
    W, H = int(size[0] * dpi), int(size[1] * dpi * bv.PIC_HEIGHT)
    items = [(p, bv.GHOST, 1.0, (0, 0, 0)) for p in done]
    items += [(p, "#E5E7EB", 0.6, (0, 0, 0)) for p in context]
    items += [(p, p.color, 1.0, np.asarray(p.explode)) for p in new]
    img, proj, verts = bv._raster(items, elev, azim, W, H)
    fig, ax = bv._frame(size, dpi, title, subtitle)
    ax.imshow(img, interpolation="bilinear")
    nd, nc = len(done), len(context)
    at = at or {}
    for k, p in enumerate(new):
        off = np.asarray(p.explode, float)
        if np.linalg.norm(off) > 1e-6 and (arrows is None or p.name in arrows):
            v = verts[nd + nc + k]
            a = proj(v.mean(0)); b_ = proj(v.mean(0) - off * 0.85)
            ax.annotate("", xy=b_, xytext=a, arrowprops=dict(arrowstyle="-|>", color="#C2410C", lw=1.6, mutation_scale=14))
    names, pts = [], []
    for k, p in enumerate(new):
        names.append(p.name)
        pts.append(np.asarray(at[p.name], float) + np.asarray(p.explode, float) if p.name in at else bv._anchor(verts[nd + nc + k]))
    if label_done:
        for k, p in enumerate(done):
            names.append(p.name)
            pts.append(np.asarray(at[p.name], float) if p.name in at else bv._anchor(verts[k]))
    bv._draw_labels(ax, proj, pts, names, W, H)
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor="white"); bv.plt.close(fig)
    return out


def steps():
    M = made()
    out = []
    zfl = D["z_floor_in"]
    lower = part("M3 screws from below", win(C["carrier_screws"], -60, 60, -40, 40, D["z_box0"] - 5, zfl), COL["screw"])
    upper = part("M3 screws from above", win(C["carrier_screws"], -60, 60, -40, 40, zfl + 1, 80), COL["screw"])

    def st(n, done, new, title, sub, **kw):
        out.append(step(done, new, OUT / f"step-{n:02d}.png", f"Step {n}: {title}", subtitle=sub, **kw))

    def mv(p, e):
        return Part(p.name, p.shape, p.color, None, tuple(e), p.alpha)

    blk = M["block"]
    st(1, [blk], [mv(M["magnets"], (0, 0, -45))], "magnets onto the sensor block",
       "Studs trimmed to 5 mm, a drop of medium threadlocker; screw each in by hand until the magnet sits flat. Seen from below",
       elev=-25, azim=-58)
    st(2, [blk, M["magnets"]], [mv(M["boss"], (0, 0, 45))], "boss onto the sensor block",
       "M6 x 12 set screw into the left magnet hole, threadlocker; screw the boss down until its face sits flat",
       elev=24, azim=-58, at={"Pot magnets (2)": (36, 0, 4), "Sensor block": (-30, -18, 13)})
    st(3, [M["base"]], [mv(part("Glands, left end (2)", S("gland_probe", "gland_power"), COL["glands"]), (-45, 0, 0)),
                        mv(part("Gland, right end", C["gland_ct"], COL["glands"]), (45, 0, 0)),
                        mv(M["grommet"], (0, 0, -40))],
       "glands and grommet into the box base",
       "Each gland from outside, nut inside, hand tight plus a quarter turn; grommet pressed into the floor hole from below",
       elev=-20, azim=-58, label_done=False)
    pod1 = [blk, M["magnets"], M["boss"]]
    boxed = [M["base"], M["glands"], M["grommet"]]
    st(4, pod1, [mv(M["standoffs"], (0, 0, 30)), mv(part("Box base with glands and grommet", S("base", "gland_ct", "gland_probe", "gland_power", "grommet"), COL["base"]), (0, 0, 70)),
                 mv(M["so_screws"], (0, 0, 110))],
       "box base onto the sensor block",
       "Stand-offs on the block; lower the base so the boss passes up through the grommet; four nylon screws, snug only",
       elev=24, azim=-58, label_done=False, arrows=["Box base with glands and grommet"])
    pod2 = pod1 + [M["standoffs"]] + boxed + [M["so_screws"]]
    st(5, pod2, [mv(M["accel"], (0, 0, 40))], "accelerometer board onto the boss",
       "Clean both faces, thin layer of rigid epoxy, board square to the box edges; leave to cure fully before moving on",
       elev=40, azim=-58, label_done=False)
    st(6, [part("Carrier board", C["carrier"], COL["carrier"])],
       [mv(part("Header sockets (2)", C["sockets"], "#111827"), (0, 0, 30)),
        mv(part("Jack, terminals, button, LED", C["interface_parts"], COL["parts"]), (0, 0, 30))],
       "build the carrier board",
       "Solder the sockets, jack, terminals, button, LED and interface circuit; wire it as the wiring diagram shows",
       elev=35, azim=-58)
    pod3 = pod2 + [M["accel"]]
    st(7, pod3, [mv(part("Carrier stand-offs (4)", C["carrier_standoffs"], COL["cso"]), (0, 0, 40)), mv(lower, (0, 0, -30))],
       "carrier stand-offs onto the floor",
       "Four M3 screws from under the floor into the stand-offs; reach in beside the sensor block",
       elev=40, azim=-58, label_done=False, arrows=["Carrier stand-offs (4)"])
    so_done = [part("Carrier stand-offs", S("carrier_standoffs"), COL["cso"]), lower]
    st(8, pod3 + so_done, [mv(M["carrier"], (0, 0, 40)), mv(upper, (0, 0, 75))],
       "carrier board onto its stand-offs",
       "Board on the stand-offs with the jack toward the right gland; four M3 screws from above",
       elev=40, azim=-58, label_done=False, arrows=["Carrier board with its parts"])
    inside0 = pod3 + so_done + [M["carrier"], upper]
    st(9, inside0, [mv(M["controller"], (0, 0, 45))],
       "controller into its sockets",
       "Line up the pins and press it straight down, aerial end toward the back of the box",
       elev=40, azim=-58, label_done=False)
    inside = inside0 + [M["controller"]]
    st(10, inside, [mv(M["pipe"], (0, 0, 40)), mv(M["lid"], (0, 0, 90))],
       "leads in, light pipe and lid",
       "Leads in through their glands and wired (wiring diagram); light pipe through the lid; lid on, four screws in a cross",
       elev=30, azim=-58, label_done=False, arrows=["Lid, drilled"])
    st(11, [part("Probe clip", C["probe_clip"], COL["clip"])], [mv(part("Disc magnets (2)", C["clip_magnets"], COL["clipmag"]), (0, 0, -25))],
       "magnets into the probe clip",
       "High-temperature epoxy in each pocket; magnets flush with the underside, same pole down. Seen from below",
       elev=-35, azim=-58)
    st(12, [part("Probe clip with magnets", S("probe_clip", "clip_magnets"), COL["clip"])],
       [mv(part("Probe sleeve", C["probe"], COL["probe"]), (0, 0, -20)), mv(part("Thermal pad", C["pad"], COL["pad"]), (0, 0, -35))],
       "probe and pad into the clip",
       "Sleeve into the groove, pad stuck on the sleeve's underside; the clip goes on the frame with them. Seen from below",
       elev=-35, azim=-58, arrows=["Probe sleeve"], at={"Probe sleeve": (0, -95 - 12, 0.6), "Thermal pad": (0, -95 + 8, 0)})
    # 12 on the machine (installed positions, motor in grey)
    parts_i = {no: s for no, _, s in build_parts(P, installed=True)}
    pod_i = _fuse([parts_i[n] for n in (1, 2, 3, 4, 5, 6, 7, 12, 13)])
    st(13, [], [mv(part("Pod", pod_i, COL["base"]), (0, 0, 120)),
                mv(part("Probe clip with probe", _fuse([parts_i[9], parts_i[14]]), COL["probe"]), (0, 0, 120)),
                mv(part("Current transformer", parts_i[8], COL["ct"]), (0, 0, 0))],
       "onto the machine (machine stopped and isolated)",
       "Pod on a clean frame top near a bearing; probe clip near the other bearing; CT closed round one insulated conductor",
       context=[part("Motor and leads (site)", motor_context(P) + leads(P), "#E5E7EB")], elev=24, azim=-58, label_done=False,
       size=(9, 6.5))
    return out


# ----------------------------------------------------------------- wiring
def wiring():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    fig = plt.figure(figsize=(12, 7.2), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 120); ax.set_ylim(0, 72); ax.set_axis_off()
    INK, MUT = "#111827", "#4B5563"
    ax.text(2, 70, "MachinePulse prototype: block-level wiring", fontsize=13, fontweight="bold", color=INK, va="top")
    ax.text(2, 66.6, "Bought modules and a hand-wired carrier board; no circuit board is laid out. Stranded copper; "
            "ferrules on every screw terminal.", fontsize=8.5, color=MUT, va="top")
    ax.text(2, 1.5, "BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT", fontsize=7, color="#B45309")
    ax.text(118, 1.5, REPO, fontsize=7, color="#0F766E", ha="right", family="monospace")
    ax.add_patch(FancyBboxPatch((27, 13), 64, 47, boxstyle="round,pad=0.4", fc="#F8FAFC", ec="#94A3B8", lw=1, ls="--"))
    ax.text(28.5, 14.2, "Inside the box (all 5 V and 3.3 V)", fontsize=8, color=MUT, va="bottom")

    def blk(x, y, w, h, title, sub, color):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3", fc="white", ec=color, lw=1.8))
        ax.text(x + w / 2, y + h - 1.4, title, ha="center", va="top", fontsize=9, fontweight="bold", color=INK)
        ax.text(x + w / 2, y + h - 4.3, sub, ha="center", va="top", fontsize=7.2, color=MUT, linespacing=1.3)

    def wire(pts, color, lw=2.0):
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", zorder=1)

    def lab(x, y, text, color, ha="left"):
        ax.text(x, y, text, fontsize=7.2, color=color, ha=ha, va="center", zorder=3,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none"))
    RED, BLU, GRY = "#B91C1C", "#1D4ED8", "#6B7280"
    blk(3, 44, 17, 12, "5 V adapter", "certified, 1 A,\nUSB-A, 2 m cable", "#111827")
    blk(3, 22, 17, 12, "Temperature probe", "DS18B20 in sleeve,\n1 m lead, 3 wires", "#C2410C")
    blk(97, 33, 20, 14, "Current transformer", "SCT-013 class,\nvoltage output,\n3.5 mm plug", "#1F2937")
    blk(31, 40, 24, 15, "Carrier board", "5 V terminal, probe terminal,\n1.50 V bias and filter,\nclamp diodes, jack, LED, button", "#2563EB")
    blk(63, 40, 24, 15, "Controller", "ESP32-S3 module board\nin header sockets\n(5 V pin, 3.3 V out)", "#0F766E")
    blk(45, 17, 22, 12, "Accelerometer", "IIS3DWB class on\nthe boss, SPI", "#B45309")
    # power
    wire([(20, 50), (31, 50)], RED); lab(21, 52.4, "through the power gland,\n0.5 mm², plug cut off", RED)
    wire([(55, 51), (63, 51)], RED); lab(59, 53, "5 V, GND", RED, "center")
    wire([(75, 40), (75, 33), (60, 33), (60, 29.3)], RED); lab(75.6, 36, "3.3 V, GND", RED)
    # probe
    wire([(20, 28), (25, 28), (25, 44), (31, 44)], GRY); lab(25.8, 33, "through the probe\ngland, 3 wires", GRY)
    ax.text(32, 41.6, "1-wire, 4.7 kΩ pull-up", fontsize=6.6, color=MUT, ha="left")
    # CT
    wire([(97, 40), (93, 40), (93, 57.3), (43, 57.3), (43, 55.3)], "#1F2937"); lab(68, 58.8, "CT lead through the M16 gland into the jack", "#1F2937", "center")
    # signals carrier -> controller
    wire([(55, 46), (63, 46)], BLU); lab(59, 44.2, "CT signal, 1-wire,\nLED, button", BLU, "center")
    # accel SPI
    wire([(67, 25), (80, 25), (80, 40)], BLU); lab(80.6, 28, "SPI and interrupt,\n0.25 mm², 8 wires", BLU)
    ax.text(28, 9.6, "Safety: the CT goes round a live conductor only with the machine isolated and locked off, fitted by a qualified person. "
            "Voltage-output CTs only.", fontsize=7.6, color="#B45309", fontweight="bold")
    ax.text(28, 6.2, "Red: power. Blue: signal. Grey: probe. Everything inside the box is extra-low voltage from the certified 5 V adapter; "
            "no mains wiring is part of this build.", fontsize=7.2, color=MUT)
    out = OUT / "wiring.png"
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor="white"); plt.close(fig)
    return out


if __name__ == "__main__":
    what = sys.argv[1:] or ["overview", "sheets", "layouts", "joints", "steps", "wiring"]
    fns = {"overview": overview, "sheets": sheets, "layouts": layouts, "joints": joints, "steps": steps, "wiring": wiring}
    for w in what:
        r = fns[w]()
        print(w, "->", r)
