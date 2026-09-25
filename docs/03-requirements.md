---
doc_id: MPL-REQ-001
title: MachinePulse requirements
project: MachinePulse
doc_type: Requirements
version: "0.2"
status: Draft
date: '2026-09-25'
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
---

# MachinePulse requirements

These are first-pass requirements for the concept. Targets are proposals for review, awaiting Amish. The status column gives the first-order view from the design precis (MPL-PRC-001); every "met" is an estimate to be checked by calculation at TRL 3. Three requirements are not met by the concept as it stands (R4, R10 and R12), and two are unverified with a known risk (R6 and R11).

Table 1. Requirements and concept status.

| ID | Requirement | Target | Concept status (estimate) | Verification (TRL 3 or later) |
| --- | --- | --- | --- | --- |
| R1 | Detect run state | Off, idle and running classified from current, with 1 s time resolution | Met: CT RMS every 1 s against two thresholds | Calculation; later bench test on a motor |
| R2 | Log run time | Run hours per machine, error within 1 % over a week | Met: 1 s resolution gives far less than 1 % error on runs over 2 min | Calculation |
| R3 | Measure load current | Within 5 % of reading from 10 % to 100 % of CT range, after a two-point calibration | Met on paper; ESP32 ADC nonlinearity is the main risk | Error budget; later comparison with a clamp meter |
| R4 | Estimate energy per shift | Within 10 % of a reference meter | **Not met.** One CT with assumed voltage and power factor gives about 20 %; needs voltage sensing or three CTs | Error budget |
| R5 | Measure vibration | Velocity RMS over 10 to 1,000 Hz (ISO 20816-1 band), three axes | Met: IIS3DWB-class sensor, dc to 6 kHz | Datasheet and calculation; later shaker check |
| R6 | Low vibration noise floor | 0.1 mm/s RMS or better, 10 to 1,000 Hz | Met on datasheet (about 0.04 mm/s); magnet mount effect unverified | Noise calculation; later mounted test |
| R7 | Resolve running-speed peaks | Spectrum bin 0.5 Hz or finer up to 1 kHz | Met: 0.41 Hz bins (8,192 points at 3.33 kHz) | Calculation |
| R8 | Measure frame temperature | Within 2 °C of the surface, 0 to 100 °C | Unverified: DS18B20 is within 0.5 °C to 85 °C and about 2 °C to 125 °C (datasheet); contact error unknown | Calculation; later comparison with a thermocouple |
| R9 | Report often enough | One summary per minute; spectrum every 15 min; delivered within 2 min | Met: about 0.4 MB per day over Wi-Fi | Data budget |
| R10 | Install without opening live enclosures | Pod and probe in 10 min without tools; CT on an accessible insulated conductor | **Not met for many machines.** Pod and probe met; the CT often needs a terminal box or panel opened by a qualified person | Design review with pilot site |
| R11 | Stay attached | No slip under 5 g peak on a painted cast frame; option for aluminium frames | Unverified: about 6 times margin estimated; steel pads included for aluminium frames | Force calculation; later pull test |
| R12 | Tolerate hot frames | Operate on frames up to 80 °C in 40 °C ambient | **Not met with the stock ABS box.** Needs a stand-off or a higher-temperature enclosure; 60 °C frame is the concept limit | Thermal estimate |
| R13 | Workshop protection | IP54 or better for the pod | Met on paper: IP54 box, IP68 glands | Design review |
| R14 | Keep data local | Works with TwinKit or any MQTT broker on the local network; no cloud account | Met | Design review |
| R15 | Store data when the network is down | 7 days of summaries on the pod | Met: about 10 days in 4 MB of flash | Data budget |
| R16 | Low cost and buildable | Parts $80 or less per machine; hand tools and a drill press; no custom PCB | Met with a thin margin: about $79 | Priced BOM |
| R17 | Safe by design | Low voltage in the pod; certified 5 V adapter; voltage-output CT only; no connection to machine controls | Met on paper | Design review |

## Assumptions

- Target machines are driven by induction motors from 0.37 kW to 15 kW, running at 50 or 60 Hz, at speeds from about 700 to 3,600 rpm.
- A single CT on one phase is enough to judge run state and relative load on a three-phase motor whose phases are balanced; it is not an energy meter.
- The pod is mounted on a clean flat or gently curved area of the frame or bearing housing, near the non-drive or drive-end bearing, with paint thickness under about 0.2 mm.
- The workshop has Wi-Fi coverage at the machine, or a TwinKit gateway nearby.
