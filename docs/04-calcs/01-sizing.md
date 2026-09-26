---
doc_id: MPL-CAL-001
title: MachinePulse sizing calculations
project: MachinePulse
doc_type: Calculation
version: "0.1"
status: Draft
date: '2026-09-25'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: First issue for TRL 3 (current and CT window, current and energy error budgets, vibration noise, bandwidth and mount resonance, magnet holding, probe error, pod temperature, power, data and storage, cost)
---

# MachinePulse sizing calculations

On paper, MachinePulse meets ten of its seventeen requirements (seven by calculation, three by design), has six at risk and misses one. The miss is R10: on many machines the current transformer (CT) can only go round a single insulated conductor inside a terminal box or panel, which needs a qualified person and isolation. The six at risk are current accuracy at the bottom of the CT range (R3), energy per shift (R4), the magnet mount's resonance inside the vibration band (R5), probe accuracy above 85 °C (R8), the standard magnets' 80 °C limit on hot frames (R12) and cost, which lands exactly on the $80 budget (R16). Several TRL 2 figures change. Data per day is about 1.15 MB, not 0.4 MB, because a full-resolution spectrum is 7.4 kB, not 1 kB. The magnet mount resonates at about 0.93 to 1.85 kHz rather than being usable to 2 kHz. Energy error with a fixed power factor is about 26 %, not 20 %; with a load-dependent power factor curve it falls to 8.5 % RSS. The box on its own would survive an 80 °C frame; the limit that TRL 2 put at 60 °C is set by the magnets, not the enclosure. The calculations add four details within the adopted design: a CT bias of 1.50 V instead of 1.65 V, clamp diodes on the CT input, a ±16 g accelerometer range, and 5 mm nylon stand-offs between the sensor block and the box floor. Every number in this note is printed by `docs/04-calcs/sizing.py`; the tag in brackets, for example [D7], is the line of that script's output that carries it.

> **Safety:** These are first-principles estimates for a paper proof of concept. They are not a substitute for bench measurements, an electrical safety review of the CT installation or pull tests on real frames. See MPL-PRC-001, Safety.

## Scope and method

The note checks every requirement in MPL-REQ-001 v0.3 against the design in MPL-PRC-001 v0.3 and the parametric model `cad/src/model.py`. The script imports the model's `PARAMS`, `derived()` and part solids, so the magnet spacing, block, stand-off gap, box and part volumes used here are the ones in the STEP files and in drawing MPL-DWG-001. It also reads `bom/bom.csv` and `budget_usd` in `project.yaml`. Run it from the repo root with `python docs/04-calcs/sizing.py`.

The design case is a 7.5 kW, 400 V three-phase induction motor (IEC 132 frame class, 130 mm frame radius) in a workshop at 40 °C, with the pod on the top line of the frame and the CT on one phase conductor where it leaves the terminal box.

Status terms used in Table 4: **met by calculation** (the estimate meets the target with the stated assumptions), **met by design** (a design feature meets it; no number to compute), **at risk** (the central estimate meets the target but the worst case or a key untested assumption does not, or the margin is nil), and **not met**.

## Assumptions

*Table 1. Main assumptions.*

| Area | Assumption | Basis |
| --- | --- | --- |
| Motor | 7.5 kW, 400 V, efficiency 0.88, power factor 0.84 at full load | Typical nameplate values |
| CT | SCT-013 class, voltage output, 1 V RMS at rated current, 13 mm aperture; ratio nonlinearity 1 % after calibration | Typical of the family; to confirm |
| ADC | ESP32-S3 ADC at 12 dB attenuation treated as linear from 0.10 to 2.90 V; residual error after two-point calibration equal to 3 mV on a 1 s RMS value; noise 3 LSB RMS | Assumed; the S3 ADC's nonlinearity is the main current risk and must be measured |
| Other current errors | Burden and reference drift 1 %; calibration clamp meter 1 %; conductor position 1 % | Assumed |
| Energy | Supply voltage within ±5 % of nominal; power factor from a nameplate-based curve within ±6 % running and ±25 % at idle; phase imbalance 3 % | Assumed |
| Accelerometer | IIS3DWB class: 75 µg/√Hz, 26.667 kHz output rate, ±16 g range ([ST](https://www.st.com/en/mems-and-sensors/iis3dwb.html)); ADXL345 class fallback taken as about 400 µg/√Hz | Datasheet figure for the first; order of magnitude for the second |
| Mount stiffness | Contact stiffness per magnet 2.0 × 10⁷ N/m on flat clean steel, 0.5 × 10⁷ N/m on a painted curved frame | Assumed; to be measured |
| Magnets | 32 mm pot magnet, 290 N rated pull on thick flat steel; pull falls as F₀ / (1 + g/0.5 mm)² with gap g; 0.2 mm paint; friction 0.25; full pull needs about 4 mm of steel; standard (N) grade limited to 80 °C; pull falls 0.12 %/K | Typical catalog values; gap law assumed |
| Probe | DS18B20 within 0.5 °C from −10 to 85 °C, taken as 2 °C above 85 °C; 0.5 mm thermal pad at 3 W/mK over 6 x 20 mm plus 1 K/W for clip and sleeve; 10 W/m²K on the sleeve; 0.005 W/K down the lead | Datasheet figure below 85 °C; the rest assumed |
| Thermal | ABS box continuous-use limit 70 °C; controller module rated 85 °C (no octal PSRAM) with an 8 K local rise; accelerometer rated 105 °C; outside surfaces 8 to 10 W/m²K, inside 4 to 5 W/m²K; magnet contact 750 W/m²K over half the face on paint | Assumed; check against the chosen box and module datasheets |
| Power | Wi-Fi connected with modem sleep 80 mA at 3.3 V; 40 mA more for 5 s a minute during the burst; linear regulator from 5 V; adapter 70 % efficient at this load | As at TRL 2; to be measured |
| Data | Summary 200 B a minute; spectrum every 15 min, three axes, one byte per bin; 15 % protocol overhead; 4 MB of flash for the offline queue | Design choices |

## A. Motor current and CT window (R1, R3)

- **Design motor.** Full-load current is 14.6 A, 49 % of a 30 A CT [A1]. Small and large machines need other CTs: 0.37 kW single-phase draws 3.3 A and 1.5 kW three-phase 3.4 A, both suited to a 5 A CT; 15 kW draws 28.0 A and needs a 50 A CT [A2]. The voltage-output range therefore runs from 5 to 60 A. The 100 A SCT-013-000 is a current-output type and is excluded, so the TRL 2 key figure "5 to 100 A" is corrected.
- **ADC window.** At full range the CT gives 1.414 V peak. About the TRL 2 bias of 1.65 V it would reach 3.064 V, 0.164 V above the linear window [A4]. A 1.50 V bias spans 0.086 to 2.914 V [A3], which clips the peak by 1 % and costs 0.12 % of RMS at 100 % of range [A5]. The interface board bias moves to 1.50 V.
- **Starting current.** About six times full load (88 A) gives 4.14 V peak at the ADC pin [A6]. A series resistor and clamp diodes on the CT input are added to the interface board (BOM line 7); run-state logic ignores the clipped start.

## B. Current error, run state and run time (R1, R2, R3)

*Table 2. Current error budget [B1].*

| Point in the CT range | ADC term | RSS | Worst-case sum | R3 target |
| --- | --- | --- | --- | --- |
| 10 % | 3.0 % | 3.6 % | 7.0 % | 5 % |
| 49 % (design motor) | 0.6 % | 2.1 % | 4.6 % | 5 % |
| 100 % | 0.3 % | 2.0 % | 4.3 % | 5 % |

- **R3 is at risk.** The RSS error meets 5 % across the range, but the worst case at 10 % of range is 7.0 %, and the ADC term rests on an assumed 3 mV residual. Choosing the CT so that normal load sits above about 30 % of its range (section A) keeps the design motor at 4.6 % worst case.
- **Run state.** A 1 s RMS window holds 2,000 samples, 50 whole cycles at 50 Hz and 60 at 60 Hz, so the state updates every second [B3]. ADC noise reads as about 0.07 A at zero current on a 30 A CT, well below a 0.5 A off threshold [B2]. R1 is met by calculation.
- **Run time.** The worst-case edge error of 1 s is 1.00 % of a 100 s run and 0.17 % of a 10 min run; it reaches 3.33 % only for 30 s runs, where random edge errors over a week largely cancel [B4]. R2 is met by calculation for runs of 100 s or longer even in the worst case.

## C. Energy per shift from one CT (R4)

- **Example shift.** Three hours idling at 40 % of full-load current and power factor 0.20, then five hours at 80 % and 0.81, use 35.3 kWh [C1].
- **Fixed power factor (the TRL 2 method).** Using the nameplate 0.84 throughout gives 44.3 kWh, 26 % high, because idle current is mostly magnetizing current [C2].
- **Load-dependent power factor.** With a power factor curve built from the nameplate and the measured no-load current, the error terms are current 2.1 %, voltage 5 %, power factor 5.8 % and imbalance 3 % [C3], for 8.5 % RSS and 16.0 % worst case [C4]. R4 is therefore at risk rather than not met. The curve is adopted in the gateway software design.
- **Voltage reference.** Measuring voltage and power factor on one phase would give 4.3 % RSS for about $10 more [C5], which would take the parts to $90.00 [J2]. Not adopted; see the review note.

## D. Vibration sensing (R5, R6, R7)

- **Noise (R6).** Integrating 75 µg/√Hz as velocity over 10 to 1,000 Hz gives 0.037 mm/s RMS, a factor of 2.7 inside the 0.1 mm/s target. An ADXL345-class fallback at about 400 µg/√Hz gives 0.20 mm/s and would miss R6 [D1].
- **Range and sampling.** Decimating the 26.7 kHz stream by eight gives 3,333 Hz with a 1,667 Hz Nyquist limit, and 13,333 samples per axis in a 4 s burst; quantization at ±16 g adds only 3.5 µg/√Hz [D2]. The ±2 g range assumed at TRL 2 would clip: 11 mm/s at 500 Hz is already 5.0 g peak [D3].
- **Memory.** The raw burst at full rate is 640 kB and does not fit the ESP32-S3's 512 kB of internal SRAM; decimating as the FIFO is read keeps 80 kB, plus a 66 kB FFT buffer [D5].
- **Resolution (R7).** An 8,192-point FFT at 3,333 Hz gives 0.407 Hz bins (0.61 Hz Hann noise bandwidth), against 0.5 Hz; the 1x line of a 1,450 rpm motor is at 24.17 Hz [D4]. R7 is met by calculation.
- **Mount resonance (R5).** The pod weighs 295 g [D6], all carried by the two magnet contacts. On flat clean steel it resonates at about 1,853 Hz, so readings are 10 % high by 556 Hz; on a painted 130 mm radius frame it resonates at about 927 Hz, 10 % high by 278 Hz and 3 dB high by 500 Hz [D7]. The sensor covers the 10 to 1,000 Hz band, but the mount does not measure it flat. Overall velocity on most machines is dominated by running-speed components well below 278 Hz, so the effect on the ISO 20816 value is usually small; bearing and gear content near the top of the band will be overstated. R5 is at risk. The TRL 2 statement "usable to about 2 kHz" is withdrawn.

## E. Magnet holding (R11)

- **Pull.** Through 0.2 mm of paint a magnet keeps about 51 % of its rated pull on a flat frame and 33 % on a 130 mm radius frame, because the face touches only along a line [E1]. The pair gives 296 N flat and 191 N curved, against 14.5 N at 5 g [E2].
- **Margins.** Pull-off margin is 13.2 on the curved frame. Slip governs: 0.25 friction gives a margin of 3.3 curved and 5.1 flat [E3]. At 80 °C the magnets lose about 7 % of their pull and the curved slip margin falls to 3.1 [G5]. Tipping across a curved frame, with the contact lever taken as a quarter of the magnet diameter, has a margin of 3.8 [E4]. R11 is met by calculation, with the pull-gap law and friction still to be checked by a pull test.
- **Aluminium frames.** Steel pads 3 mm thick keep about 75 % of rated pull (435 N, slip margin 7.5) [E5]. Thin 1 mm pads would keep about 25 % (slip margin 2.5) [E6], so BOM line 11 now specifies 35 mm by 3 mm discs.

## F. Surface temperature probe (R8)

- **Contact error.** With a thermal pad and the sleeve cooled by air and its lead, the probe reads 1.06 K low on an 80 °C frame and 1.19 K low at 85 °C, for totals of 1.56 K and 1.69 K with the sensor tolerance [F1]. R8 is met to 85 °C.
- **Above 85 °C.** At 100 °C the contact error is 1.59 K and the sensor tolerance outside its ±0.5 °C band is taken as 2 °C, for 3.59 K [F1]. R8 is at risk over its full 0 to 100 °C range. A relaxed range is proposed in the review note.

## G. Pod temperature on a hot frame (R12)

- **Network.** The model has three nodes (block, box floor, inside air) between the frame and the room. Conductances are 0.547 W/K from frame to block through the magnets, 0.137 W/K from block to floor with the floor sitting on the block, 0.0229 W/K across the 5 mm stand-off gap, 0.030 W/K from floor to inside air and 0.052 W/K through walls and lid; 0.42 W of electronics heat is released inside [G1].
- **Results at an 80 °C frame and 40 °C air.** With the floor on the block (the TRL 2 arrangement), the floor reaches 67.2 °C and the controller module about 63.7 °C. With 5 mm nylon stand-offs the floor falls to 53.9 °C and the module to about 58.9 °C; the magnets sit at about 78.7 °C and the block and accelerometer at 77.4 °C [G2].

*Table 3. Frame temperature at which each limit is reached, 40 °C air [G3].*

| Arrangement | N-grade magnets 80 °C | ABS floor 70 °C | Accelerometer 105 °C | Module 85 °C |
| --- | --- | --- | --- | --- |
| Floor on the block (TRL 2) | 82.0 °C | 84.2 °C | 112.0 °C | 163.1 °C |
| 5 mm nylon stand-offs | 81.3 °C | 134.7 °C (beyond the other limits) | 109.6 °C | Not reached |

- **Finding.** The box alone would take an 80 °C frame, with only 4 K in hand; the stand-offs add a large margin for the box and module for $1.00 and are adopted within decision D7. The magnets now set the limit, with 1.3 K to spare at 80 °C, so R12 is at risk. High-temperature magnets (rated 120 °C or more) would clear it; they are proposed in the review note because they would take the parts over budget.
- **Module choice.** ESP32-S3 module variants with octal PSRAM are rated to 65 °C and would have only 6.1 K of margin even with stand-offs [G4]. BOM line 3 now specifies a module without octal PSRAM, rated to 85 °C.

## H. Power

- **Average.** About 84.7 mA at 3.3 V (Wi-Fi modem sleep 80 mA, burst processing 3.3 mA averaged, sensors and LED), or 84.8 mA and 0.42 W from 5 V [H1]. The TRL 2 figure of about 0.5 W stands.
- **At the wall.** With a 70 % efficient adapter, 0.61 W, or 5.3 kWh a year, not the 4.4 kWh stated at TRL 2; the regulator dissipates 0.14 W inside the box [H2].
- **Peak.** Wi-Fi transmit peaks near 0.35 A, 1.75 W from the adapter, within its 1 A rating [H3].

## I. Data, delivery and offline store (R9, R15)

- **Spectrum size.** Keeping 0.407 Hz bins up to 1 kHz needs 2,458 bins per axis; at one byte per bin for three axes plus a header, each spectrum is 7.4 kB, not the 1 kB assumed at TRL 2 [I1].
- **Daily volume.** Summaries are 0.29 MB and spectra 0.71 MB a day, or 1.15 MB with protocol overhead, an average of 0.11 kbit/s [I2]. This is trivial for Wi-Fi and for a TwinKit gateway. R9 is met by calculation.
- **Delivery.** A summary reaches the broker within about 66 s of the start of its minute, against 120 s [I5].
- **Offline store (R15).** The 4 MB queue holds 13.9 days of summaries alone, or 4.0 days of summaries and spectra [I3]. The queue keeps summaries first and drops the oldest spectra when full. R15 is met by calculation. Flash wear is negligible: each 4 kB sector is erased once per 14 days of offline running [I4].

## J. Cost (R16)

The 13-line BOM totals $80.00 against the $80 `budget_usd`, a margin of $0.00 [J1]. The stand-offs ($1.00) used the last dollar. A three-CT variant would cost $100.00 and a voltage reference $90.00 [J2]. Prices are indicative, not quotes, so R16 is at risk.

## Results against every requirement

*Table 4. Requirement status from this note.*

| ID | Requirement | Target | Value from this note | Status |
| --- | --- | --- | --- | --- |
| R10 | Install without opening live enclosures | Pod and probe in 10 min without tools; CT on an accessible insulated conductor | Pod and probe need no tools; the CT needs a single insulated conductor, often only inside a terminal box or panel | **Not met** |
| R3 | Measure load current | Within 5 % of reading, 10 % to 100 % of range | RSS 3.6 % at 10 %, 2.1 % at 49 %; worst case 7.0 % at 10 % [B1] | At risk |
| R4 | Estimate energy per shift | Within 10 % of a reference meter | 8.5 % RSS, 16.0 % worst case with a PF curve; 26 % with a fixed PF [C2, C4] | At risk |
| R5 | Measure vibration | Velocity RMS, 10 to 1,000 Hz, three axes | Sensor covers the band; mount resonance 927 to 1,853 Hz, +10 % from 278 Hz on a curved frame [D7] | At risk |
| R8 | Measure frame temperature | Within 2 °C, 0 to 100 °C | 1.56 K at 80 °C, 1.69 K at 85 °C, 3.59 K at 100 °C [F1] | At risk |
| R12 | Tolerate hot frames | Frames up to 80 °C in 40 °C air | Box and module pass with stand-offs; N-grade magnets reach their limit at an 81.3 °C frame [G3] | At risk |
| R16 | Low cost and buildable | Parts $80 or less; hand tools; no custom PCB | $80.00, margin $0.00 [J1]; hand tools and perfboard | At risk |
| R1 | Detect run state | Off, idle, running at 1 s resolution | 1 s RMS windows; 0.07 A zero reading against a 0.5 A threshold [B2, B3] | Met by calculation |
| R2 | Log run time | Within 1 % over a week | 1.00 % worst case on 100 s runs, 0.17 % on 10 min runs [B4] | Met by calculation |
| R6 | Low vibration noise floor | 0.1 mm/s RMS or better | 0.037 mm/s [D1] | Met by calculation |
| R7 | Resolve running-speed peaks | 0.5 Hz bins or finer to 1 kHz | 0.407 Hz [D4] | Met by calculation |
| R9 | Report often enough | Summary each minute, spectrum each 15 min, within 2 min | 1.15 MB/day; 66 s worst delivery [I2, I5] | Met by calculation |
| R11 | Stay attached | No slip at 5 g on a painted cast frame; aluminium option | Slip margin 3.3 (3.1 at 80 °C); 3 mm pads 7.5 [E3, E5, G5] | Met by calculation |
| R15 | Store data when offline | 7 days of summaries | 13.9 days [I3] | Met by calculation |
| R13 | Workshop protection | IP54 or better | IP54 box, IP68 glands, silicone boot round the boss | Met by design |
| R14 | Keep data local | TwinKit or any MQTT broker; no cloud | MQTT on the local network | Met by design |
| R17 | Safe by design | Low voltage in the pod; certified adapter; voltage-output CT; no link to controls | Unchanged; CT input now clamped [A6] | Met by design |

Summary: 1 not met, 6 at risk, 7 met by calculation, 3 met by design, none left unverifiable at TRL 3. R13's IP rating and the at-risk items need bench evidence that belongs to TRL 4, which is on hold.

## Checks against the TRL 2 figures

*Table 5. TRL 2 figures that change.*

| Quantity | TRL 2 | This note |
| --- | --- | --- |
| Pod size and mass | 100 x 68 x 58 mm, 0.35 kg | 100 x 68 x 63 mm (132 mm over glands), 0.30 kg [D6] |
| CT variants | 5 to 100 A | 5 to 60 A voltage output [A2] |
| Current accuracy | About 3 % | 2.1 % RSS at the design point, 3.6 % at 10 % of range [B1] |
| Energy accuracy | About 20 % | 26 % fixed PF; 8.5 % RSS with a PF curve [C2, C4] |
| Magnet mount | Usable to about 2 kHz | Resonance 927 to 1,853 Hz [D7] |
| Magnet margin | About 6 times | Pull-off 13.2, slip 3.3 [E3] |
| Data volume | About 0.4 MB/day | 1.15 MB/day [I2] |
| Offline store | About 10 days | 13.9 days of summaries, 4.0 days with spectra [I3] |
| Frame temperature limit | About 60 °C (box) | About 81 °C (magnets) [G3] |
| Annual energy | About 4.4 kWh | 5.3 kWh at the wall [H2] |
| Parts cost | About $79 | $80.00 [J1] |
