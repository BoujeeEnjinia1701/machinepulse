"""MachinePulse sizing calculations, MPL-CAL-001 v0.1 (TRL 3).

Run from the repo root:  python docs/04-calcs/sizing.py
Prints every number quoted in docs/04-calcs/01-sizing.md. Each line carries a tag such as
[D3] that the note cites. Geometry and part volumes come from cad/src/model.py (PARAMS,
derived and build_parts), the parts cost from bom/bom.csv and the budget from project.yaml.
First-principles estimates for a paper proof of concept; not a substitute for tests.
"""
import csv
import math
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cad" / "src"))
from model import PARAMS as P, derived, pod_parts  # noqa: E402

D = derived(P)
G = 9.81
SIGMA = 5.67e-8


def tag(t, text):
    print(f"[{t}] {text}")


# ------------------------------------------------------------------ assumptions
MOTOR = dict(kw=7.5, v=400.0, eff=0.88, pf=0.84)       # design-case motor, typical nameplate values
CT_RANGE = 30.0            # A, SCT-013-030: 1 V RMS at 30 A
FS_ADC = 2000.0            # Hz current sampling
ADC_LIN = (0.10, 2.90)     # V, ESP32-S3 ADC window treated as linear at 12 dB attenuation (assumed)
V_BIAS = 1.50              # V, CT bias (was 1.65 V at TRL 2; see section A)
ADC_RESID = 0.003          # V equivalent error on a 1 s RMS value after two-point calibration (assumed)
ERR_CT = 0.010             # CT ratio nonlinearity after calibration
ERR_TEMP = 0.010           # burden and reference drift, 0 to 60 degC
ERR_REF = 0.010            # reference clamp meter used for calibration
ERR_POS = 0.010            # conductor position in the aperture
ACC_ND = 75e-6             # g/sqrt(Hz), IIS3DWB class noise density (ST)
ACC_ND_FALLBACK = 400e-6   # g/sqrt(Hz), ADXL345 class, order of magnitude (assumed)
ODR = 26667.0              # Hz, IIS3DWB output data rate
DECIM = 8
BURST_S = 4.0
NFFT = 8192
F_LO, F_HI = 10.0, 1000.0
K_CONTACT_FLAT = 2.0e7     # N/m per magnet contact, flat clean steel (assumed; to be measured)
K_CONTACT_CURVED = 0.5e7   # N/m per magnet contact, painted and curved frame (assumed)
MAG_F0 = 290.0             # N rated pull per 32 mm pot magnet on thick flat steel (typical catalog, assumed)
MAG_G0 = 0.5               # mm, pull-gap law F = F0 / (1 + g/g0)^2 (assumed)
PAINT = 0.2                # mm paint or scale under the magnets
MU = 0.25                  # friction, nickel-plated magnet on painted steel (assumed)
A_PEAK = 5.0               # g, R11
T_SAT_PAD = 4.0            # mm steel thickness for full pull of a 32 mm pot magnet (assumed)
PAD_T = 3.0                # mm steel adhesive pads (BOM line 11)
FLASH_Q = 4.0e6            # B reserved for the offline queue
SUMMARY_B = 200            # B per summary (compact JSON)
SPEC_HDR = 64              # B per spectrum message header
OVERHEAD = 0.15            # MQTT, TCP and IP overhead
I_WIFI = 0.080             # A at 3.3 V, Wi-Fi connected with modem sleep (assumed, as at TRL 2)
I_BURST = 0.040            # A extra while sampling and computing
T_BURST = 5.0              # s per minute (4 s burst plus about 1 s FFT and features)
I_ACC, I_DS, I_LED, I_BIAS, I_LDO_Q = 1.1e-3, 1.0e-3, 2.0e-3, 0.165e-3, 0.1e-3
ADAPTER_EFF = 0.70         # small USB adapter at 0.4 W (assumed)
T_AMB, T_FRAME = 40.0, 80.0

cost_rows = list(csv.DictReader((ROOT / "bom" / "bom.csv").open()))
budget = float(yaml.safe_load((ROOT / "project.yaml").read_text())["budget_usd"])

print("MachinePulse sizing, MPL-CAL-001 v0.1")
print(f"Geometry from cad/src/model.py: box {P['box']} mm, block {P['block']} mm, magnets {P['mag_d']:.0f} mm at "
      f"{P['mag_pitch']:.0f} mm pitch, stand-offs {P['standoff_h']:.0f} mm, pod height {D['pod_h']:.0f} mm")

# ------------------------------------------------------------------ A. Current, CT and ADC window (R1, R3)
print("\nA. Motor current and CT selection")
m = MOTOR
fla = m["kw"] * 1000 / (math.sqrt(3) * m["v"] * m["eff"] * m["pf"])
tag("A1", f"design motor 7.5 kW, 400 V: full-load current {fla:.1f} A = {fla / CT_RANGE * 100:.0f} % of a {CT_RANGE:.0f} A CT")
for kw, v, ph, eff, pf in ((0.37, 230, 1, 0.65, 0.75), (1.5, 400, 3, 0.80, 0.80), (15.0, 400, 3, 0.90, 0.86)):
    i = kw * 1000 / ((math.sqrt(3) if ph == 3 else 1) * v * eff * pf)
    ct = next(r for r in (5, 10, 15, 20, 30, 50, 60) if r >= i * 1.1)
    tag("A2", f"{kw:g} kW {'three' if ph == 3 else 'single'}-phase {v} V: {i:.1f} A, smallest voltage-output CT with 10 % headroom {ct} A ({i / ct * 100:.0f} % of range)")
pk = math.sqrt(2) * 1.0
lo, hi = V_BIAS - pk, V_BIAS + pk
tag("A3", f"full-range CT peak {pk:.3f} V about a {V_BIAS:.2f} V bias spans {lo:.3f} to {hi:.3f} V; linear window {ADC_LIN[0]:.2f} to {ADC_LIN[1]:.2f} V")
old_hi = 1.65 + pk
tag("A4", f"TRL 2 bias of 1.65 V would reach {old_hi:.3f} V at full range, {old_hi - ADC_LIN[1]:.3f} V above the window")
clip = min(ADC_LIN[1] - V_BIAS, V_BIAS - ADC_LIN[0]) / pk
# clipped sine RMS relative to ideal, numerically
n = 20000
ideal = sum(math.sin(2 * math.pi * k / n) ** 2 for k in range(n)) / n
clipd = sum(max(-clip, min(clip, math.sin(2 * math.pi * k / n))) ** 2 for k in range(n)) / n
tag("A5", f"clipping at 100 % of range with the {V_BIAS:.2f} V bias: peak limited to {clip * 100:.1f} % of the sine, RMS error {(1 - math.sqrt(clipd / ideal)) * 100:.3f} %")
inrush = 6 * fla
tag("A6", f"starting current about 6 x FLA = {inrush:.0f} A gives {inrush / CT_RANGE * pk:.2f} V peak at the ADC pin: series resistor and clamp diodes needed on the interface board")

# ------------------------------------------------------------------ B. Current error budget, run state, run time (R1, R2, R3)
print("\nB. Current error budget and run time")
def i_err(frac):
    v = frac * 1.0
    adc = ADC_RESID / v
    rss = math.sqrt(ERR_CT ** 2 + adc ** 2 + ERR_TEMP ** 2 + ERR_REF ** 2 + ERR_POS ** 2)
    worst = ERR_CT + adc + ERR_TEMP + ERR_REF + ERR_POS
    return adc, rss, worst
for frac in (0.10, fla / CT_RANGE, 1.0):
    adc, rss, worst = i_err(frac)
    tag("B1", f"at {frac * 100:.0f} % of range: ADC term {adc * 100:.1f} %, RSS {rss * 100:.1f} %, worst-case sum {worst * 100:.1f} % (R3 target 5 %)")
noise_a = 3 * 0.757e-3 / 1.0 * CT_RANGE
tag("B2", f"zero-current reading from ADC noise (3 LSB RMS) about {noise_a:.2f} A on a 30 A CT; off threshold set at 0.5 A")
tag("B3", f"1 s RMS window holds {FS_ADC:.0f} samples, 50 whole cycles at 50 Hz and 60 at 60 Hz; state updates every 1 s (R1)")
for run in (30, 100, 120, 600):
    tag("B4", f"run of {run} s: worst-case edge error 1 s = {1 / run * 100:.2f} % of that run; random edge error on a week of such runs is far smaller")

# ------------------------------------------------------------------ C. Energy per shift (R4)
print("\nC. Energy per shift from one CT")
# shift: (fraction of time, current as fraction of FLA, true power factor)
shift = [(0.375, 0.40, 0.20), (0.625, 0.80, 0.81)]
hours = 8.0
true_e = sum(f * hours * math.sqrt(3) * m["v"] * i * fla * pf for f, i, pf in shift) / 1000
fixed = sum(f * hours * math.sqrt(3) * m["v"] * i * fla * m["pf"] for f, i, _ in shift) / 1000
tag("C1", f"8 h shift, 3 h idle at 40 % FLA and PF 0.20, 5 h at 80 % FLA and PF 0.81: true energy {true_e:.1f} kWh")
tag("C2", f"with a fixed nameplate PF of {m['pf']}: {fixed:.1f} kWh, error {(fixed / true_e - 1) * 100:+.0f} % (the TRL 2 method)")
i_share = shift[0][0] * shift[0][1] * shift[0][2] / sum(f * i * pf for f, i, pf in shift)
e_i = i_err(0.8 * fla / CT_RANGE)[1]
e_v, e_pf_run, e_pf_idle, e_imb = 0.05, 0.06, 0.25, 0.03
e_pf = math.hypot((1 - i_share) * e_pf_run, i_share * e_pf_idle)
rss = math.sqrt(e_i ** 2 + e_v ** 2 + e_pf ** 2 + e_imb ** 2)
worst = e_i + e_v + e_pf + e_imb
tag("C3", f"with a load-dependent PF curve from the nameplate: current {e_i * 100:.1f} %, voltage {e_v * 100:.0f} %, PF {e_pf * 100:.1f} % (idle share {i_share * 100:.0f} %), imbalance {e_imb * 100:.0f} %")
tag("C4", f"energy error RSS {rss * 100:.1f} %, worst-case sum {worst * 100:.1f} % (R4 target 10 %)")
rss_v = math.sqrt(e_i ** 2 + 0.01 ** 2 + 0.02 ** 2 + e_imb ** 2)
tag("C5", f"with a voltage reference (measured V and PF on one phase): RSS {rss_v * 100:.1f} %, for about $10 more (not in the BOM)")

# ------------------------------------------------------------------ D. Vibration (R5, R6, R7)
print("\nD. Vibration sensing")
def v_noise(nd):
    return nd * G / (2 * math.pi) * math.sqrt(1 / F_LO - 1 / F_HI) * 1000
tag("D1", f"velocity noise 10 to 1,000 Hz: IIS3DWB class {v_noise(ACC_ND):.3f} mm/s RMS; ADXL345 class fallback {v_noise(ACC_ND_FALLBACK):.2f} mm/s RMS (R6 target 0.1)")
fs = ODR / DECIM
q16 = 32.0 / 65536 / math.sqrt(12) / math.sqrt(fs / 2)
tag("D2", f"decimated rate {fs:.0f} Hz, Nyquist {fs / 2:.0f} Hz; 4 s burst = {int(BURST_S * fs)} samples per axis; +-16 g range, quantization {q16 * 1e6:.1f} ug/sqrt(Hz), negligible")
for v, f in ((11.0, 500.0), (11.0, 1000.0)):
    a = 2 * math.pi * f * v / 1000 * math.sqrt(2) / G
    tag("D3", f"{v:.0f} mm/s RMS at {f:.0f} Hz is {a:.1f} g peak, so the +-2 g range would clip; +-16 g selected")
bin_hz = fs / NFFT
tag("D4", f"{NFFT}-point FFT at {fs:.0f} Hz: bin {bin_hz:.3f} Hz, Hann noise bandwidth {1.5 * bin_hz:.2f} Hz; 1x at 1,450 rpm = {1450 / 60:.2f} Hz (R7 target 0.5 Hz)")
raw_kb = BURST_S * ODR * 6 / 1000
dec_kb = BURST_S * fs * 6 / 1000
tag("D5", f"raw burst {raw_kb:.0f} kB at full rate does not fit the S3's 512 kB SRAM; decimating on the fly stores {dec_kb:.0f} kB; FFT buffer {NFFT * 8 / 1000:.0f} kB")

# mass of the parts carried by the magnet contact, from model volumes
dens = {1: 1.05, 2: 1.05, 5: 2.70, 6: 7.5, 12: 1.2, 13: 1.14}
fixed_g = {3: 8.0, 4: 3.0, 7: 12.0}
mass = 0.0
for no, name, shape in pod_parts(P):
    g = fixed_g.get(no, shape.volume / 1000 * dens.get(no, 1.0))
    mass += g
wiring = 20.0
mass_kg = (mass + wiring) / 1000
tag("D6", f"pod mass from model volumes and board allowances, plus {wiring:.0f} g of internal wiring: {mass_kg * 1000:.0f} g")
for label, k in (("flat clean steel", K_CONTACT_FLAT), ("painted curved frame", K_CONTACT_CURVED)):
    fn = math.sqrt(2 * k / mass_kg) / (2 * math.pi)
    tag("D7", f"mounted resonance on {label}: {fn:.0f} Hz; +10 % amplification reached at {0.30 * fn:.0f} Hz, +3 dB at {0.54 * fn:.0f} Hz")

# ------------------------------------------------------------------ E. Magnet holding (R11)
print("\nE. Magnet holding")
def pull_fraction(R, paint, n=200):
    a = P["mag_d"] / 2
    tot = acc = 0.0
    for i in range(n):
        for j in range(n):
            x = -a + (i + 0.5) * 2 * a / n; y = -a + (j + 0.5) * 2 * a / n
            if x * x + y * y > a * a:
                continue
            sag = 0.0 if R is None else R - math.sqrt(R * R - y * y)
            g = paint + sag
            acc += 1 / (1 + g / MAG_G0) ** 2; tot += 1
    return acc / tot
f_flat = pull_fraction(None, PAINT)
f_curv = pull_fraction(P["motor_r"], PAINT)
F_flat, F_curv = 2 * MAG_F0 * f_flat, 2 * MAG_F0 * f_curv
w5 = mass_kg * A_PEAK * G
tag("E1", f"pull per magnet {MAG_F0:.0f} N rated; {f_flat * 100:.0f} % through 0.2 mm paint on a flat frame, {f_curv * 100:.0f} % on a {P['motor_r']:.0f} mm radius frame")
tag("E2", f"total pull {F_flat:.0f} N flat, {F_curv:.0f} N curved; load at 5 g {w5:.1f} N")
tag("E3", f"pull-off margin {F_curv / w5:.1f} (curved); slip margin mu {MU} x pull / load = {MU * F_curv / w5:.1f} curved, {MU * F_flat / w5:.1f} flat")
h_cg = D["z_block0"] + 20.0
tip = (F_curv * P["mag_d"] / 4) / (w5 * h_cg / 1000 * 1000)
tag("E4", f"tipping across a curved frame (lever r/2 = {P['mag_d'] / 4:.0f} mm, CG {h_cg:.0f} mm up): margin {tip:.1f}")
pad = min(1.0, PAD_T / T_SAT_PAD)
tag("E5", f"steel pads {PAD_T:.0f} mm thick on aluminium frames: about {pad * 100:.0f} % of rated pull, {2 * MAG_F0 * pad:.0f} N; slip margin {MU * 2 * MAG_F0 * pad / w5:.1f}")
tag("E6", f"1 mm pads (TRL 2 wording did not fix thickness) would give about {100 / T_SAT_PAD:.0f} %, slip margin {MU * 2 * MAG_F0 * 0.25 / w5:.1f}")

# ------------------------------------------------------------------ F. Surface temperature probe (R8)
print("\nF. Probe contact error")
A_pad = 6e-3 * 20e-3
R_c = 0.5e-3 / (3.0 * A_pad) + 1.0          # thermal pad 0.5 mm, 3 W/mK, plus 1 K/W clip and sleeve
A_s = math.pi * 6e-3 * 34e-3
R_a = 1 / (1 / (1 / (10 * A_s)) + 0.005)    # sleeve to air at 10 W/m2K in parallel with 0.005 W/K down the lead
frac = R_c / (R_c + R_a)
for Ts, sens in ((80.0, 0.5), (85.0, 0.5), (100.0, 2.0)):
    e = (Ts - T_AMB) * frac
    tag("F1", f"frame {Ts:.0f} degC, air {T_AMB:.0f} degC: contact error {e:.2f} K + sensor {sens} K = {e + sens:.2f} K (R8 target 2 K)")

# ------------------------------------------------------------------ G. Pod temperature on a hot frame (R12)
print("\nG. Pod temperature on a hot frame")
def power():
    i3 = I_WIFI + I_BURST * T_BURST / 60 + I_ACC + I_DS * 0.75 / 60 + I_LED * 0.05 + I_BIAS
    i5 = i3 + I_LDO_Q
    return i3, i5, 5.0 * i5
i3, i5, p5 = power()
Q = p5
A_mag = math.pi * (P["mag_d"] / 2e3) ** 2
bl, bw, bt = [v / 1000 for v in P["block"]]
hole = math.pi * (P["floor_hole_d"] / 2e3) ** 2
A_bf = bl * bw - hole
Lb, Wb, Hb = [v / 1000 for v in P["box"]]
A_floor = Lb * Wb
A_rest = 2 * (Lb * Wb + Lb * Hb + Wb * Hb) - A_floor
t_w = P["wall"] / 1000
k_abs = 0.17
G_fb = 1 / (1 / (2 * 750 * A_mag * 0.5) + 1 / (2 * 3000 * A_mag)) + 9.6 * (bl * bw - 2 * A_mag)
G_ba = 10 * 2 * (bl + bw) * bt
G_flin = 5 * (Lb - 2 * t_w) * (Wb - 2 * t_w)
G_flout = 8 * (A_floor - bl * bw)
U = 1 / (1 / 8 + t_w / k_abs + 1 / 4)
G_walls = U * A_rest
G_boss = 4 * (math.pi * P["boss_d"] / 1e3 * P["boss_above_floor"] / 1e3 + math.pi * (P["boss_d"] / 2e3) ** 2)
def G_bfl(standoff):
    floor = k_abs / t_w
    if not standoff:
        return A_bf / (1 / 500 + 1 / floor)
    h_gap = 0.029 / (P["standoff_h"] / 1000) + 4 * SIGMA * 350 ** 3 * 0.1
    gap = A_bf / (1 / h_gap + 1 / floor)
    nylon = 4 * 0.25 * math.pi * (P["standoff_d"] / 2e3) ** 2 / (P["standoff_h"] / 1000)
    boot = 0.2 * (math.pi * P["boss_d"] / 1e3 * 1e-3) / 0.004
    return gap + nylon + boot

def solve(tf, ta, standoff, q=Q):
    """Nodes: block, floor, inside air. Returns (Tb, Tfl, Tair)."""
    gbf = G_bfl(standoff)
    # Gauss-Seidel on three nodes
    tb = tfl = tair = ta
    for _ in range(2000):
        tb = (G_fb * tf + G_ba * ta + gbf * tfl + G_boss * tair) / (G_fb + G_ba + gbf + G_boss)
        tfl = (gbf * tb + G_flin * tair + G_flout * ta) / (gbf + G_flin + G_flout)
        tair = (G_flin * tfl + G_walls * ta + G_boss * tb + q) / (G_flin + G_walls + G_boss)
    return tb, tfl, tair

T_ABS, T_MOD, LOCAL, T_ACC, T_MAG = 70.0, 85.0, 8.0, 105.0, 80.0
tag("G1", f"conductances W/K: frame to block {G_fb:.3f}, block to air {G_ba:.3f}, block to floor direct {G_bfl(False):.3f}, "
          f"with {P['standoff_h']:.0f} mm stand-offs {G_bfl(True):.4f}, floor to inside air {G_flin:.3f}, walls and lid {G_walls:.3f}; heat inside {Q:.2f} W")
for so in (False, True):
    name = f"{P['standoff_h']:.0f} mm stand-offs" if so else "box floor on the block (TRL 2)"
    tb, tfl, tair = solve(T_FRAME, T_AMB, so)
    tag("G2", f"{name}, frame {T_FRAME:.0f} degC, air {T_AMB:.0f} degC: magnets about {(T_FRAME + tb) / 2:.1f}, block {tb:.1f}, floor {tfl:.1f}, inside air {tair:.1f}, module about {tair + LOCAL:.1f} degC")
    lims = {}
    for tf10 in range(400, 2000):
        tf = tf10 / 10
        tb, tfl, tair = solve(tf, T_AMB, so)
        for key, bad in (("ABS floor 70 degC", tfl > T_ABS), ("module 85 degC", tair + LOCAL > T_MOD),
                         ("accelerometer 105 degC", tb > T_ACC), ("N-grade magnets 80 degC", (tf + tb) / 2 > T_MAG)):
            if bad and key not in lims:
                lims[key] = tf - 0.1
    txt = ", ".join(f"{k} at {v:.1f}" for k, v in sorted(lims.items(), key=lambda kv: kv[1]))
    tag("G3", f"{name}: frame temperature at which each limit is reached, {T_AMB:.0f} degC air: {txt}")
tb, tfl, tair = solve(T_FRAME, T_AMB, True)
tag("G4", f"module variants with octal PSRAM are rated 65 degC: at an 80 degC frame the module would sit at about {tair + LOCAL:.1f} degC, {65 - tair - LOCAL:.1f} K margin with stand-offs")
loss = 0.0012 * ((T_FRAME + tb) / 2 - 20)
tag("G5", f"magnet pull falls about 0.12 %/K reversibly: {loss * 100:.0f} % less at {(T_FRAME + tb) / 2:.0f} degC, slip margin on a curved frame {MU * F_curv * (1 - loss) / w5:.1f}")

# ------------------------------------------------------------------ H. Power
print("\nH. Power")
tag("H1", f"average 3.3 V current {i3 * 1000:.1f} mA (Wi-Fi modem sleep {I_WIFI * 1000:.0f} mA, burst {I_BURST * T_BURST / 60 * 1000:.1f} mA average, sensors and LED); 5 V input {i5 * 1000:.1f} mA = {p5:.2f} W")
tag("H2", f"at the wall with a {ADAPTER_EFF * 100:.0f} % efficient adapter: {p5 / ADAPTER_EFF:.2f} W, {p5 / ADAPTER_EFF * 8.76:.1f} kWh per year; LDO loss {(5 - 3.3) * i3:.2f} W")
tag("H3", f"peak Wi-Fi transmit about 0.35 A through the linear regulator: {0.35 * 5:.2f} W input, within a 1 A adapter")

# ------------------------------------------------------------------ I. Data, latency, offline store (R9, R15)
print("\nI. Data and storage")
bins = int(F_HI / bin_hz) + 1
spec_b = 3 * bins + SPEC_HDR
day_sum = 1440 * SUMMARY_B
day_spec = 96 * spec_b
day = (day_sum + day_spec) * (1 + OVERHEAD)
tag("I1", f"spectrum to 1 kHz at {bin_hz:.3f} Hz: {bins} bins x 3 axes x 1 byte + header = {spec_b / 1000:.1f} kB (TRL 2 assumed 1 kB)")
tag("I2", f"per day: summaries {day_sum / 1e6:.2f} MB, spectra {day_spec / 1e6:.2f} MB, with {OVERHEAD * 100:.0f} % protocol overhead {day / 1e6:.2f} MB; average {day * 8 / 86400 / 1000:.2f} kbit/s")
tag("I3", f"offline queue {FLASH_Q / 1e6:.0f} MB: summaries only {FLASH_Q / day_sum:.1f} days; summaries and spectra {FLASH_Q / (day_sum + day_spec):.1f} days (R15 target 7 days of summaries)")
tag("I4", f"flash wear: a 4 kB sector fills every {4096 / SUMMARY_B:.0f} min offline; a {FLASH_Q / 4096:.0f}-sector ring erases each sector once per {FLASH_Q / 4096 * 4096 / SUMMARY_B / 1440:.0f} days offline")
tag("I5", "worst-case delivery: 60 s window + 2 s features + 3 s reconnect + 1 s broker = 66 s (R9 target 120 s)")

# ------------------------------------------------------------------ J. Cost (R16)
print("\nJ. Cost")
total = sum(float(r["unit_cost_usd"]) * float(r["qty"]) for r in cost_rows)
tag("J1", f"BOM {len(cost_rows)} lines, total ${total:.2f} against budget_usd ${budget:.0f}: margin ${budget - total:.2f}")
tag("J2", f"a three-CT variant adds 2 x $10.00 = ${total + 20:.2f}; a voltage reference adds about $10 = ${total + 10:.2f}")
