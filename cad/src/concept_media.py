"""MachinePulse concept media (TRL 3, constructable design MPL-DDR-003), generated from the parametric model.

Run from the repo root:  python cad/src/concept_media.py
Takes the pod, current transformer and probe from cad/src/model.py (PARAMS), adds a 7.5 kW
class induction motor and the leads (grey, no BOM number) as context, and renders the media
set with .kit/concept.py. Parts are colored and numbered to match bom/bom.csv. Figures on
the sheet and in the flow diagram come from docs/04-calcs/sizing.py (MPL-CAL-001).
Not for fabrication.

The model puts the magnet contact line on the X axis at z = 0, so the pod sits at the origin
and the kit's cutaway cutter passes through it without a shift.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / ".kit"), str(ROOT / "cad" / "src")]
from concept import Part, render_all  # noqa: E402
from model import PARAMS as P, build_parts, motor_context, leads  # noqa: E402

COLORS = {1: "#FDE68A", 2: "#E0B84A", 3: "#0F766E", 4: "#B45309", 5: "#8A9299", 6: "#374151",
          7: "#2563EB", 8: "#1F2937", 9: "#C2410C", 12: "#DC2626", 13: "#F9FAFB",
          14: "#57534E"}
EXPLODE = {1: (0, 0, 215), 2: (0, 0, 70), 3: (0, 0, 165), 4: (0, 0, 100), 5: (0, 0, 0), 6: (0, 0, -45),
           7: (0, 0, 118), 8: (0, 0, 60), 9: (0, 0, 70), 12: (0, 0, 45), 13: (0, 0, 22),
           14: (0, 0, 35)}

parts = [Part(name, shape, COLORS[no], no, EXPLODE[no]) for no, name, shape in build_parts(P)]
context = [Part("7.5 kW class induction motor and leads", motor_context(P) + leads(P), "#C8CDD3")]

render_all(
    parts, project="MachinePulse", title="Clip-on machine monitor concept", dwg_no="MPL-DWG-010",
    date="2026-09-25",
    key_figures=["Pod 100 x 68 x 63 mm (137 mm over glands), about 0.32 kg",
                 "Split-core CT on one phase, 5 to 60 A voltage-output variants",
                 "Vibration 10 to 1,000 Hz velocity RMS, noise 0.037 mm/s",
                 "Summary every 60 s, about 1.15 MB/day; 0.42 W from 5 V USB",
                 "$83.50 in parts (indicative); target $81, MPL-CAL-001"],
    scale_figure=False, context=context,
    cut_exclude=("Split-core current transformer", "Surface temperature probe and pad", "Probe clip with magnets"),
    flow={"title": "data flow (estimates, MPL-CAL-001)", "unit": "",
          "stages": [("Machine", "current, vibration, heat"),
                     ("Sensors", "CT, accel, probe"),
                     ("On-pod features", "0.29 MB/day (est.)"),
                     ("Wi-Fi, MQTT", "1.15 MB/day (est.)"),
                     ("TwinKit or broker", "trends, baseline flags"),
                     ("Maintenance team", "run hours, load, faults")]},
)
