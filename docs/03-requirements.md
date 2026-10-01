---
doc_id: MPL-REQ-001
title: MachinePulse requirements
project: MachinePulse
doc_type: Requirements
version: "0.5"
status: Draft
date: '2026-10-01'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: Initial scaffold
- version: "0.2"
  date: '2026-09-25'
  author: Amish Chadha
  change: First measurable requirements for TRL 2, with concept status
- version: "0.3"
  date: '2026-09-25'
  author: Amish Chadha
  change: Status from MPL-CAL-001 for TRL 3; decisions from MPL-DDR-001 reflected; targets unchanged
- version: "0.4"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002)
- version: "0.5"
  date: '2026-10-01'
  author: Amish Chadha
  change: Status from MPL-CAL-001 v0.3 for the constructable design (MPL-DDR-003); R16 reported against the value-engineering target; targets unchanged
---

# MachinePulse requirements

These are the MachinePulse requirements with their status from the TRL 3 calculation note MPL-CAL-001 v0.3, which checks the constructable design of MPL-DDR-003. The design they are checked against follows the decisions Amish made on 2026-09-25 (MPL-DDR-001 and MPL-DDR-002): Wi-Fi, USB adapter, IIS3DWB-class sensor, one CT, baseline alerts, TwinKit or any broker, stock box with stand-offs and high-temperature magnets. Two targets change in v0.4 under MPL-DDR-002: R8 is restated with a wider tolerance above 85 °C (N2), and R16 follows the budget raised to $81 for the high-temperature magnets (N1). R3 and R5 keep their targets (N3). One requirement is not met (R10), three are at risk (R3, R4 and R5), nine are met by calculation and three by design. R16 is reported against the value-engineering target: the constructable design is estimated at $83.50, $2.50 over the $81 target. How R4 should be treated with one CT is still awaiting Amish (MPL-DDR-001, O2).

Table 1. Requirements and TRL 3 status.

| ID | Requirement | Target | Status (MPL-CAL-001) | Verification after TRL 3 |
| --- | --- | --- | --- | --- |
| R1 | Detect run state | Off, idle and running classified from current, with 1 s time resolution | Met by calculation: 1 s RMS windows of 2,000 samples; zero-current reading 0.07 A against a 0.5 A threshold | Bench test on a motor |
| R2 | Log run time | Run hours per machine, error within 1 % over a week | Met by calculation: worst case 1.00 % on 100 s runs, 0.17 % on 10 min runs | Comparison with a timed log |
| R3 | Measure load current | Within 5 % of reading from 10 % to 100 % of CT range, after a two-point calibration | At risk: RSS 3.6 % at 10 % of range and 2.1 % at the design point, but 7.0 % worst case at 10 %; ESP32-S3 ADC residual assumed | Comparison with a clamp meter |
| R4 | Estimate energy per shift | Within 10 % of a reference meter | At risk: 8.5 % RSS, 16.0 % worst case with a load-dependent power factor curve; 26 % with a fixed power factor. Treatment awaiting Amish (MPL-DDR-001, O2) | Comparison with a reference meter |
| R5 | Measure vibration | Velocity RMS over 10 to 1,000 Hz (ISO 20816-1 band), three axes | At risk: sensor covers the band, but the magnet mount resonates at about 892 Hz on a painted curved frame (1,783 Hz flat), so readings are 10 % high from about 267 Hz | Mounted shaker check |
| R6 | Low vibration noise floor | 0.1 mm/s RMS or better, 10 to 1,000 Hz | Met by calculation: 0.037 mm/s (ADXL345-class fallback 0.20 mm/s would miss it) | Mounted noise test |
| R7 | Resolve running-speed peaks | Spectrum bin 0.5 Hz or finer up to 1 kHz | Met by calculation: 0.407 Hz bins | Spectrum of a known tone |
| R8 | Measure frame temperature | Within 2 °C of the surface from 0 to 85 °C, and within 4 °C from 85 to 100 °C (restated per MPL-DDR-002, N2; was within 2 °C from 0 to 100 °C) | Met by calculation: 1.56 K at 80 °C, 1.69 K at 85 °C and 3.59 K at 100 °C | Comparison with a thermocouple |
| R9 | Report often enough | One summary per minute; spectrum every 15 min; delivered within 2 min | Met by calculation: 1.15 MB per day; 66 s worst delivery | Network log |
| R10 | Install without opening live enclosures | Pod and probe in 10 min without tools; CT on an accessible insulated conductor | **Not met for many machines.** Pod and probe need no tools; the CT needs a single insulated conductor, often only inside a terminal box or panel opened by a qualified person | Design review with the pilot site |
| R11 | Stay attached | No slip under 5 g peak on a painted cast frame; option for aluminium frames | Met by calculation: slip margin 3.0 on a curved painted frame (2.8 at 80 °C); 3 mm steel pads for aluminium frames, margin 7.0 | Pull and shake tests |
| R12 | Tolerate hot frames | Operate on frames up to 80 °C in 40 °C ambient | Met by calculation: with 5 mm stand-offs the box floor reaches 53.9 °C and the module about 58.9 °C; the 120 °C magnets (MPL-DDR-002, N1) reach their limit at a 122.7 °C frame, so the accelerometer now sets the limit at 109.6 °C (N-grade magnets would have stopped at 81.3 °C) | Hot-plate test |
| R13 | Workshop protection | IP54 or better for the pod | Met by design: IP54 box, three IP68 glands with one cable each, silicone grommet round the sensor boss, sealed light pipe | IP test |
| R14 | Keep data local | Works with TwinKit or any MQTT broker on the local network; no cloud account | Met by design | Configuration check |
| R15 | Store data when the network is down | 7 days of summaries on the pod | Met by calculation: 13.9 days of summaries in 4 MB (4.0 days with spectra) | Offline run |
| R16 | Low cost and buildable | Parts $81 or less per machine (was $80; MPL-DDR-002, N1); hand tools and a drill press; no custom PCB | Over the value-engineering target by $2.50: estimated $83.50 against the $81 target (indicative prices); hand tools, a drill press and perfboard, no custom PCB | Supplier quotes |
| R17 | Safe by design | Low voltage in the pod; certified 5 V adapter; voltage-output CT only; no connection to machine controls | Met by design; the CT input is now clamped against starting current | Design review |

## Assumptions

- Target machines are driven by induction motors from 0.37 kW to 15 kW, running at 50 or 60 Hz, at speeds from about 700 to 3,600 rpm.
- The CT is chosen per machine from the 5 to 60 A voltage-output range so that normal load sits above about 30 % of its range.
- A single CT on one phase is enough to judge run state and relative load on a three-phase motor whose phases are balanced; it is not an energy meter. Energy uses a power factor curve built from the nameplate and the measured no-load current.
- The pod is mounted on a clean flat or gently curved area of the frame or bearing housing, near the non-drive or drive-end bearing, with paint thickness under about 0.2 mm.
- The workshop has Wi-Fi coverage at the machine, or a TwinKit gateway nearby.
