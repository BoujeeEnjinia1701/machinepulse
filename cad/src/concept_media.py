"""MachinePulse concept massing model and media (TRL 2).

Run from the repo root:  python cad/src/concept_media.py
Proportions and main parts only; not for fabrication.

Layout: a magnetic-mount sensor pod sits on top of a 7.5 kW class induction motor
(IEC 132 frame class, shown in grey for scale). The split-core current transformer
clamps one phase conductor where it leaves the terminal box, and the surface
temperature probe sits near the non-drive-end bearing.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".kit"))
from build123d import Box, Cylinder, Pos, Rot, Solid, Plane, Vector
from concept import Part, render_all

# ---- Context: motor (mm) -------------------------------------------------
AXIS_Z = 180.0          # shaft center height above the floor
R_MOTOR = 130.0         # frame radius (without fins)
L_MOTOR = 380.0         # frame length along X
TOP = AXIS_Z + R_MOTOR  # top line of the frame


def rod(p0, p1, r):
    """Straight cable segment between two points."""
    d = Vector(*p1) - Vector(*p0)
    return Solid.make_cylinder(r, d.length, Plane(origin=p0, z_dir=d))


frame = Pos(0, 0, AXIS_Z) * Rot(0, 90, 0) * Cylinder(R_MOTOR, L_MOTOR)
fins = None
for k in range(-4, 5):
    ring = Pos(k * 40, 0, AXIS_Z) * Rot(0, 90, 0) * (Cylinder(R_MOTOR + 6, 6) - Cylinder(R_MOTOR - 1, 7))
    fins = ring if fins is None else fins + ring
shields = (Pos(-L_MOTOR / 2 - 15, 0, AXIS_Z) * Rot(0, 90, 0) * Cylinder(R_MOTOR - 12, 30)
           + Pos(L_MOTOR / 2 + 15, 0, AXIS_Z) * Rot(0, 90, 0) * Cylinder(R_MOTOR - 12, 30))
shaft = Pos(L_MOTOR / 2 + 30 + 40, 0, AXIS_Z) * Rot(0, 90, 0) * Cylinder(19, 80)
feet = (Pos(-120, 0, 30) * Box(70, 260, 60) + Pos(120, 0, 30) * Box(70, 260, 60)
        + Pos(-120, 0, 90) * Box(50, 150, 80) + Pos(120, 0, 90) * Box(50, 150, 80))
tbox = Pos(95, 0, TOP + 35) * Box(110, 110, 90)
TBOX_Y = 55.0
conduit = Pos(95, TBOX_Y + 25, TOP + 45) * Rot(90, 0, 0) * Cylinder(16, 50)
cable_a = rod((95, TBOX_Y + 50, TOP + 45), (95, 260, TOP + 45), 9)
cable_b = rod((95, 260, TOP + 45), (95, 260, 0), 9)
motor = frame + fins + shields + shaft + feet + tbox + conduit + cable_a + cable_b

# ---- Pod (local frame: origin at underside of enclosure base) -------------
PX, PZ = -70.0, TOP + 18.0   # pod placed on the top line of the frame; magnets touch it
BL, BW, BH, WALL = 100.0, 68.0, 28.0, 2.5
LH = 12.0


def P(x, y, z):
    return Pos(PX + x, y, PZ + z)


base = P(0, 0, BH / 2) * (Box(BL, BW, BH) - Pos(0, 0, WALL) * Box(BL - 2 * WALL, BW - 2 * WALL, BH))
glands = (P(BL / 2 + 8, 12, 14) * Rot(0, 90, 0) * Cylinder(8, 16)
          + P(-BL / 2 - 8, 0, 14) * Rot(0, 90, 0) * Cylinder(8, 16))
base = base + glands
lid = P(0, 0, BH + LH / 2) * (Box(BL, BW, LH) - Pos(0, 0, -WALL) * Box(BL - 2 * WALL, BW - 2 * WALL, LH))
led = P(30, -20, BH + LH) * Cylinder(3, 2)
lid = lid + led

block = P(0, 0, -5) * Box(76, 36, 10)
boss = P(-28, 0, 3) * Box(20, 20, 6)
sensor_block = block + boss
magnets = P(-20, 0, -14) * Cylinder(16, 8) + P(20, 0, -14) * Cylinder(16, 8)
accel = P(-28, 0, 6.8) * Box(18, 18, 1.6) + P(-28, 0, 8.1) * Box(4, 4, 1.0)
controller = P(16, 15, WALL + 5) * Box(51, 22, 1.6) + P(22, 15, WALL + 7.3) * Box(18, 20, 3.2)
interface = P(18, -17, WALL + 4) * Box(40, 26, 1.6) + P(34, -17, WALL + 8) * Box(8, 12, 6)

# ---- Current transformer on one phase conductor ---------------------------
CTY = 150.0
ct = (Pos(95, CTY, TOP + 45) * Rot(90, 0, 0) * (Cylinder(22, 28) - Cylinder(9.5, 30))
      + Pos(95, CTY, TOP + 45 + 26) * Box(18, 28, 10))

# ---- Surface temperature probe near the non-drive-end bearing -------------
probe = (Pos(-165, 0, TOP + 4) * Box(22, 16, 8)
         + Pos(-165, 0, TOP + 9) * Rot(90, 0, 0) * Cylinder(3, 34))

# ---- Leads (context) --------------------------------------------------------
gx_pos = PX + BL / 2 + 16
gx_neg = PX - BL / 2 - 16
ct_lead = rod((gx_pos, 12, PZ + 14), (95, CTY - 20, TOP + 45 + 26), 2.5)
probe_lead = rod((gx_neg, 0, PZ + 14), (-165, 0, TOP + 13), 2.5)
usb_a = rod((gx_neg, 0, PZ + 10), (gx_neg - 20, -200, PZ + 10), 2.5)
usb_b = rod((gx_neg - 20, -200, PZ + 10), (gx_neg - 20, -200, 0), 2.5)
leads = ct_lead + probe_lead + usb_a + usb_b

parts = [
    Part("Enclosure lid with LED window", lid, "#FDE68A", 1, (0, 0, 150)),
    Part("Enclosure base with cable glands", base, "#E0B84A", 2, (0, 0, 60)),
    Part("Controller, ESP32-S3 module board", controller, "#0F766E", 3, (0, 0, 110)),
    Part("Vibration accelerometer, IIS3DWB class", accel, "#B45309", 4, (0, 0, 95)),
    Part("Aluminium sensor block", sensor_block, "#8A9299", 5, (0, 0, 0)),
    Part("Pot magnets, 32 mm, pair", magnets, "#374151", 6, (0, 0, -45)),
    Part("Interface board (CT, probe, LED)", interface, "#2563EB", 7, (0, 0, 110)),
    Part("Split-core current transformer", ct, "#1F2937", 8, (0, 0, 60)),
    Part("Surface temperature probe", probe, "#C2410C", 9, (0, 0, 45)),
]
context = [Part("7.5 kW class induction motor and sensor leads", motor + leads, "#C8CDD3")]

# The kit's cutaway cutter is centered near the origin, so shift the scene down until the
# pod sits near z = 0. Geometry and proportions are unchanged.
SHIFT = Pos(0, 0, -TOP)
for p in parts + context:
    p.shape = SHIFT * p.shape

render_all(
    parts, project="MachinePulse", title="Clip-on machine monitor concept", dwg_no="MPL-DWG-010",
    key_figures=["Pod 100 x 68 x 58 mm, about 0.35 kg (estimate)",
                 "Split-core CT, one phase, 5 to 100 A variants",
                 "Vibration 10 to 1,000 Hz, velocity RMS (ISO 20816-1)",
                 "Summary every 60 s, about 0.5 W from 5 V USB (estimate)",
                 "About $79 in parts (indicative)"],
    scale_figure=False, context=context,
    cut_exclude=("Split-core current transformer", "Surface temperature probe"),
    flow={"title": "data flow (estimates)", "unit": "",
          "stages": [("Machine", "current, vibration, heat"),
                     ("Sensors", "CT, accel, probe"),
                     ("On-pod features", "about 0.2 kB/min (est.)"),
                     ("Wi-Fi, MQTT", "about 0.4 MB/day (est.)"),
                     ("TwinKit or broker", "trends, alerts"),
                     ("Maintenance team", "run hours, load, faults")]},
)
