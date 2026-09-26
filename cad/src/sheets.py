"""MachinePulse general arrangement sheet MPL-DWG-001, Rev P2 (TRL 3).

Run from the repo root:  python cad/src/sheets.py
Writes cad/drawings/MPL-DWG-001.svg, .pdf and .png from the parametric model in
cad/src/model.py with .kit/drawing.py. The orthographic views show the sensor pod; the
isometric view shows the pod, current transformer and probe as installed on the context
motor. Dimensions come from PARAMS and derived(), so they follow any parameter change.
The concept blueprint in media/ is MPL-DWG-010.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / ".kit"), str(ROOT / "cad" / "src")]
from drawing import Sheet, _viewbox, _t, M, TB_Y, INK, MUTED, project_views  # noqa: E402
from model import PARAMS as P, assembly, derived, motor_context  # noqa: E402

DATE = "2026-09-25"


def ortho_cells(sheet, views, names=("front", "top", "right")):
    """Repeat Sheet.add_ortho's layout arithmetic to find where each view lands (x, y, w, h)."""
    ax, ay, aw, ah = M + 10, M + 16, 245, TB_Y - M - 20
    gap, lab = 14, 12
    dims = {n: _viewbox(Path(views[n]).read_text())[2:] for n in names}
    fw, fh = dims["front"]; tw, th = dims["top"]; rw, rh = dims["right"]
    k = sheet.scale
    ax += (aw - (k * (max(fw, tw) + rw) + gap)) / 2
    ay += (ah - (k * (th + max(fh, rh)) + gap + 2 * lab)) / 2
    colw = k * max(fw, tw)
    front_y = ay + k * th + lab + gap
    row_h = k * max(fh, rh)
    return {"top": (ax, ay, colw, k * th), "front": (ax, front_y, colw, row_h),
            "right": (ax + colw + gap, front_y, k * rw, row_h)}


def dim_h(x1, x2, y, text):
    a = 1.4
    return [f'<line x1="{x1:.2f}" y1="{y:.2f}" x2="{x2:.2f}" y2="{y:.2f}" stroke="{INK}" stroke-width="0.18"/>',
            f'<path d="M{x1:.2f} {y:.2f} l{a} -0.5 l0 1 Z" fill="{INK}"/>',
            f'<path d="M{x2:.2f} {y:.2f} l{-a} -0.5 l0 1 Z" fill="{INK}"/>',
            _t((x1 + x2) / 2, y - 1.0, text, 2.3, 400, INK, "middle", mono=True)]


def dim_v(x, y1, y2, text, side=-1):
    a = 1.4
    cx, cy = x + side * 1.0, (y1 + y2) / 2
    return [f'<line x1="{x:.2f}" y1="{y1:.2f}" x2="{x:.2f}" y2="{y2:.2f}" stroke="{INK}" stroke-width="0.18"/>',
            f'<path d="M{x:.2f} {y1:.2f} l-0.5 {a} l1 0 Z" fill="{INK}"/>',
            f'<path d="M{x:.2f} {y2:.2f} l-0.5 {-a} l1 0 Z" fill="{INK}"/>',
            f'<g transform="rotate(-90 {cx:.2f} {cy:.2f})">{_t(cx, cy, text, 2.3, 400, INK, "middle", mono=True)}</g>']


def ext(x1, y1, x2, y2):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{MUTED}" stroke-width="0.13"/>'


def leader(x1, y1, x2, y2, text, anchor="start"):
    return [f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{MUTED}" stroke-width="0.15"/>',
            f'<circle cx="{x1:.2f}" cy="{y1:.2f}" r="0.5" fill="{INK}"/>',
            _t(x2 + (1 if anchor == "start" else -1), y2 + 0.8, text, 2.1, 400, INK, anchor)]


def main():
    from build123d import Compound
    D = derived(P)
    work = ROOT / "cad" / "drawings" / "_views"
    pod = assembly(pod_only=True)
    views = project_views(pod, work)
    inst = Compound(children=[assembly(), motor_context(P)])
    views["iso"] = project_views(inst, work / "iso")["iso"]
    bb = pod.bounding_box()
    s = Sheet(project="MachinePulse", title="General arrangement", dwg_no="MPL-DWG-001", rev="P2",
              author="Amish Chadha", date=DATE, scale=1.0, theme="technical",
              material="ABS box, 6061 block, nylon stand-offs; bought-in parts per bom/bom.csv. PRELIMINARY, NOT FOR FABRICATION",
              revisions=[("P1", "Preliminary GA for TRL 3 (from cad/src/model.py)", DATE, "AC"),
                         ("P2", "High-temperature magnets per MPL-DDR-002", DATE, "AC")])
    s.add_ortho(views)
    k = s.scale
    c = ortho_cells(s, views)
    L, W, H = P["box"]
    bl, bw, bt = P["block"]
    L_ = []

    gl = P["gland_len"]
    # front view (from -Y): X right, Z up
    x, y, w, h = c["front"]
    X = lambda mx: x + (mx - bb.min.X) * k
    Z = lambda mz: y + h - (mz - bb.min.Z) * k
    L_.append(f'<line x1="{X(bb.min.X) - 4:.2f}" y1="{Z(0):.2f}" x2="{X(bb.max.X) + 4:.2f}" y2="{Z(0):.2f}" stroke="{INK}" stroke-width="0.35" stroke-dasharray="4 1 0.6 1"/>')
    L_.append(_t(X(bb.max.X) + 4, Z(0) - 1.5, "FRAME TOP LINE", 1.9, 600, MUTED, "end"))
    xl = X(-L / 2 - gl) - 5
    L_ += [ext(X(-bl / 2), Z(D["z_block1"]), xl - 1, Z(D["z_block1"])), ext(X(-L / 2), Z(D["z_box0"]), xl - 1, Z(D["z_box0"]))]
    L_ += dim_v(xl, Z(D["z_box0"]), Z(D["z_block1"]), f"{P['standoff_h']:.0f}")
    L_ += [ext(X(-bl / 2), Z(D["z_block0"]), xl - 7, Z(D["z_block0"])), ext(X(-bl / 2), Z(D["z_block1"]), xl - 7, Z(D["z_block1"]))]
    L_ += dim_v(xl - 6, Z(D["z_block1"]), Z(D["z_block0"]), f"{bt:.0f}")
    zt = bb.max.Z + 3
    L_ += [ext(X(-L / 2 - gl), Z(D["z_box0"] + 14), X(-L / 2 - gl), Z(zt + 5) - 1),
           ext(X(L / 2 + gl), Z(D["z_box0"] + 14), X(L / 2 + gl), Z(zt + 5) - 1),
           ext(X(-L / 2), Z(D["z_top"]), X(-L / 2), Z(zt) - 1), ext(X(L / 2), Z(D["z_top"]), X(L / 2), Z(zt) - 1)]
    L_ += dim_h(X(-L / 2), X(L / 2), Z(zt), f"{L:.0f} box")
    L_ += dim_h(X(-L / 2 - gl), X(L / 2 + gl), Z(zt + 5), f"{D['pod_len_glands']:.0f} over glands")

    # top view (from +Z): X right, Y up the sheet
    x, y, w, h = c["top"]
    Xt = lambda mx: x + (mx - bb.min.X) * k
    Yt = lambda my: y + h - (my - bb.min.Y) * k
    mx1, mx2 = D["mag_x"]
    ya = Yt(W / 2) - 6
    L_ += [ext(Xt(mx1), Yt(0), Xt(mx1), ya - 1), ext(Xt(mx2), Yt(0), Xt(mx2), ya - 1)]
    L_ += dim_h(Xt(mx1), Xt(mx2), ya, f"{P['mag_pitch']:.0f} magnet pitch")
    xw = Xt(L / 2 + gl) + 5
    L_ += [ext(Xt(L / 2), Yt(W / 2), xw + 1, Yt(W / 2)), ext(Xt(L / 2), Yt(-W / 2), xw + 1, Yt(-W / 2))]
    L_ += dim_v(xw, Yt(W / 2), Yt(-W / 2), f"{W:.0f}", side=1)
    L_ += leader(Xt(-L / 2 - gl / 2), Yt(0), Xt(-L / 2 - gl / 2), Yt(W / 2) - 6, "M12 GLAND: PROBE, USB")
    L_ += leader(Xt(L / 2 + gl / 2), Yt(12), Xt(L / 2 + gl / 2), Yt(W / 2) - 6, "M12 GLAND: CT", "end")

    # right view (from +X): Y right, Z up
    x, y, w, h = c["right"]
    Yr = lambda my: x + (my - bb.min.Y) * k
    Zr = lambda mz: y + h - (mz - bb.min.Z) * k
    yr = Yr(bb.max.Y) + 5
    for i, (z1, z2, label) in enumerate(((D["z_box0"], D["z_top"], f"{H:.0f} box"),
                                         (0, D["pod_h"], f"{D['pod_h']:.0f} overall"),
                                         (0, D["z_block0"], f"{P['mag_h']:.0f}"))):
        xd = yr + 6 * i
        L_ += [ext(Yr(W / 2), Zr(z1), xd + 1, Zr(z1)), ext(Yr(W / 2), Zr(z2), xd + 1, Zr(z2))]
        L_ += dim_v(xd, Zr(z2), Zr(z1), label, side=1)
    L_ += leader(Yr(0), Zr(D["z_boss_top"]), yr + 4, Zr(bb.max.Z) - 10, f"ACCELEROMETER ON D{P['boss_d']:.0f} BOSS")

    s._layers += L_
    s.add_svg(views["iso"], 276, 32, 140, 96, label="Isometric view, installed",
              sublabel="Not to scale; motor grey context, not in the BOM")
    s.add_notes("Main dimensions and interfaces (mm)", [
        f"Pod {L:.0f} x {W:.0f} x {D['pod_h']:.0f} high from magnet face; {D['pod_len_glands']:.0f} over glands",
        f"Two D{P['mag_d']:.0f} pot magnets rated {P['mag_t_max']:.0f} °C, M6 studs, {P['mag_pitch']:.0f} pitch",
        f"Block {bl:.0f} x {bw:.0f} x {bt:.0f} aluminium; boss D{P['boss_d']:.0f} x {D['boss_h']:.0f} through a D{P['floor_hole_d']:.0f} hole",
        f"Four nylon stand-offs D{P['standoff_d']:.0f} x {P['standoff_h']:.0f}; silicone boot seals the boss",
        f"IP54 ABS box, base {H - P['lid_h']:.0f} + lid {P['lid_h']:.0f}; boards on {P['board_standoff']:.0f} stand-offs",
        f"CT SCT-013 class, D{P['ct_aperture']:.0f} aperture, one insulated conductor",
        "Probe: DS18B20 sleeve D6 in a magnetic clip near a bearing",
        "Power: certified 5 V USB adapter, 2 m lead; 0.42 W (MPL-CAL-001)",
        "Third-angle; front view from -Y; X along the motor shaft",
    ], x=276, y=150, width=146)
    out = s.save(ROOT / "cad" / "drawings" / "MPL-DWG-001")
    shutil.rmtree(work, ignore_errors=True)
    print(f"wrote {out} and .pdf, .png at scale {k:g}:1")


if __name__ == "__main__":
    main()
