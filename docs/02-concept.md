---
doc_id: MPL-PRC-001
title: MachinePulse design precis
project: MachinePulse
doc_type: Design precis
version: "0.6"
status: Draft
date: '2026-10-02'
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
  change: Populate to TRL 2 (architecture, first-order numbers, safety, media)
- version: "0.3"
  date: '2026-09-25'
  author: Amish Chadha
  change: TRL 3 update; design choices adopted per MPL-DDR-001; numbers from MPL-CAL-001; stand-offs, CT clamp, 1.50 V bias, +-16 g range, module variant and 3 mm pads added; GA drawing MPL-DWG-001
- version: "0.4"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002)
- version: "0.5"
  date: '2026-10-01'
  author: Amish Chadha
  change: Constructable design (MPL-DDR-003); components, numbers and GA Rev P4 updated; budget treated as a value-engineering target
- version: "0.6"
  date: '2026-10-02'
  author: Amish Chadha
  change: 'Decisions of 2026-10-02 carried in: R4 as a relative energy trend with kWh as an estimate, co-design partner candidates'
---

# MachinePulse design precis

## Summary

MachinePulse is a small magnetic pod that clips onto an old machine's motor frame, plus a split-core current transformer (CT) on one phase conductor and a surface temperature probe. Every minute it reports run state, run time, load current, vibration velocity and frame temperature to a TwinKit gateway or any MQTT broker on the shop network, and every 15 minutes it sends a vibration spectrum. The TRL 3 calculation note MPL-CAL-001 finds that stock modules, a hand-made aluminium sensor block and a stock box meet twelve of the seventeen requirements. Value-engineering target: USD 81. Estimated cost of the constructable design: USD 83.50 (USD 2.50 over the target). One requirement is not met: fitting the CT without opening a live enclosure on many machines (R10). Three are at risk: current accuracy at the bottom of the CT range (R3), energy per shift (R4) and the magnet mount's resonance inside the vibration band (R5). Writing the prototype build plan (MPL-BLD-001) made the design constructable without changing what it does: the boss is a separate piece screwed to the block, the boards sit on one carrier on stand-offs, each lead has its own gland, a grommet seals the boss and a made clip holds the probe on the frame (MPL-DDR-003, open for Amish's review). The design choices below were decided by Amish on 2026-09-25, going with the recommendations (MPL-DDR-001 and MPL-DDR-002). That decision added high-temperature pot magnets rated 120 °C, which clear hot frames to about 110 °C, and raised the budget from $80 to $81 to pay for them.

![Hero render](../media/hero.png)

Figure 1. MachinePulse on a 7.5 kW class induction motor (grey, for scale), generated from the parametric model `cad/src/model.py`. Concept, not for fabrication.

## How it works

1. **Sense current.** A voltage-output split-core CT (YHDC SCT-013 family, 5 to 60 A variants) clamps one insulated single-core phase conductor. The carrier board's interface circuit biases its output at 1.50 V, so a full-range signal stays inside the ADC's linear window, and clamps the input against starting current. The pod samples at 2 kHz and computes RMS current every second.
2. **Sense vibration.** A wideband MEMS accelerometer (IIS3DWB class, dc to 6 kHz, 75 µg/√Hz noise density, 1.1 mA ([ST](https://www.st.com/en/mems-and-sensors/iis3dwb.html))), set to ±16 g, sits on a 20 mm round boss of an aluminium sensor block, directly above one of two pot magnets. The magnets pull the block onto the frame, so vibration reaches the sensor through metal, not through the plastic box.
3. **Sense temperature.** A DS18B20 probe in a stainless sleeve sits in a small magnetic clip with a thermal pad on the frame near a bearing.
4. **Summarize on the pod.** Every 60 s the ESP32-S3 controller records a 4 s vibration burst, decimates it from 26.7 kHz to 3.33 kHz as it reads the sensor, and computes velocity RMS over 10 to 1,000 Hz (the ISO 20816-1 band ([ISO](https://www.iso.org/standard/63180.html))), acceleration RMS, crest factor and the amplitudes at 1x and 2x running speed. It adds run state, run seconds, mean and peak current, starts, and temperature.
5. **Send and store.** The summary goes over Wi-Fi to an MQTT broker, by default on the TwinKit gateway. If the network is down, summaries queue in flash for about 14 days; spectra are kept only while space allows.
6. **Compare with the machine's own baseline.** During the first week of running, the gateway software learns a baseline per load band. Afterward it flags a change, for example vibration velocity above twice its baseline or temperature rise above baseline at the same load, for a person to inspect. Energy per shift uses a power factor curve built from the nameplate and the measured no-load current, and is shown as a relative trend against the machine's own baseline, with any kWh figure marked as an estimate (decided by Amish, 2026-10-02).

![Data flow](../media/flow.png)

Figure 2. Data flow from machine to maintenance team. Values are estimates from MPL-CAL-001.

## Main components

Table 1. Main components. Numbers match the BOM and Figure 3.

| # | Component | Choice | Notes |
| --- | --- | --- | --- |
| 1, 2 | Enclosure | Stock IP54 ABS box, 100 x 68 x 40 mm, with one M16 IP68 gland (CT) and two M12 IP68 glands (probe, power), a sealed light pipe and a 24 mm hole for the boss | Stock box keeps cost low (D7); one cable per gland (MPL-DDR-003) |
| 3 | Controller | ESP32-S3 module board, 8 MB flash, no octal PSRAM, USB-C, Wi-Fi and BLE | Module rated to 85 °C; PSRAM variants are rated to 65 °C (D1) |
| 4 | Accelerometer | IIS3DWB-class 3-axis MEMS on an 18 x 18 mm adapter board, ±16 g | ADXL345-class fallback misses R6 (D3) |
| 5 | Sensor block and boss | 76 x 36 x 10 mm aluminium plate; a separate 20 mm round boss 11 mm high on an M6 set screw over magnet 1, through the box floor | Carries magnets and sensor; stiff path to the frame; no lathe needed (MPL-DDR-003) |
| 6 | Magnets | Two 32 mm high-temperature neodymium pot magnets, rated 120 °C, with M6 studs, 40 mm apart | Standard 80 °C grade would limit hot frames to about 81 °C; the 120 °C grade meets R12 (MPL-DDR-002, N1) |
| 7 | Carrier board | Perfboard 45 x 56 mm on four stand-offs, with 1.50 V CT bias and filter, series resistor and clamp diodes, 3.5 mm jack, 5 V and probe terminals, LED, button and header sockets for the controller | No custom PCB for the first build |
| 8 | Current transformer | SCT-013 family, voltage output, 13 mm aperture, 5 to 60 A chosen per machine (30 A for the design case) | Voltage output has an internal burden, so it is never open-circuited (D4) |
| 9, 14 | Temperature probe and clip | DS18B20 in stainless sleeve on a thermal pad, held against the frame by a made aluminium clip with two high-temperature disc magnets | The clip presses the sleeve on its pad (MPL-DDR-003) |
| 10 | Power | Certified 5 V 1 A USB-C adapter and 2 m cable | Low voltage only in the pod (D2) |
| 11 | Steel pads | 35 mm x 3 mm steel discs with epoxy, for aluminium frames | 3 mm keeps about 75 % of the pull |
| 12, 13 | Hardware and stand-offs | Screws, set screw, silicone grommet round the boss, carrier stand-offs; four 6 x 5 mm nylon stand-offs | The stand-offs are the thermal break studied under D7 |

![Exploded view](../media/exploded.png)

Figure 3. Exploded view with BOM numbers.

![Cutaway](../media/cutaway.png)

Figure 4. Cutaway through the accelerometer: the sensor sits on the boss of the aluminium block, which sits on the magnets; the box stands 5 mm clear of the block on nylon stand-offs and carries no vibration path.

The general arrangement drawing [MPL-DWG-001](../cad/drawings/MPL-DWG-001.pdf) (Rev P4, 1:1) gives the main dimensions: pod 100 x 68 x 63 mm high from the magnet face, 137 mm over the glands.

## Key numbers

All values come from MPL-CAL-001 and are estimates for a paper proof of concept.

Table 2. Key numbers.

| Quantity | Value | Requirement |
| --- | --- | --- |
| Design motor full-load current | 14.6 A, 49 % of a 30 A CT | Sizes the CT |
| Current accuracy | 2.1 % RSS at the design point; 3.6 % RSS and 7.0 % worst case at 10 % of range | R3 at risk |
| Energy per shift | 8.5 % RSS with a power factor curve; 26 % with a fixed power factor | R4 met by design as restated: a relative energy trend, kWh shown as an estimate |
| Velocity noise floor | 0.037 mm/s RMS, 10 to 1,000 Hz | R6 met |
| Spectrum resolution | 0.407 Hz bins (8,192 points at 3,333 Hz) | R7 met |
| Magnet mount resonance | About 892 Hz on a painted curved frame, 1,783 Hz flat | R5 at risk |
| Pod mass | About 0.32 kg | |
| Magnet holding | Slip margin 3.0 on a painted curved frame; pull-off 12.2 | R11 met |
| Probe error | 1.56 K at 80 °C, 1.69 K at 85 °C; 3.59 K at 100 °C | R8 met (restated target) |
| Hot frame, 40 °C air | Floor 53.9 °C and module about 58.9 °C at an 80 °C frame; accelerometer limit at a 109.6 °C frame, 120 °C magnets at 122.7 °C | R12 met |
| Power | 0.42 W from 5 V; 0.61 W and 5.3 kWh a year at the wall | |
| Data | 1.15 MB per day; worst delivery 66 s | R9 met |
| Offline store | 13.9 days of summaries | R15 met |
| Parts cost | $83.50 against an $81 value-engineering target | R16 $2.50 over the target |

## Key design choices

Decided by Amish, 2026-09-25: go with recommendation (MPL-DDR-001, MPL-DDR-002).

- **Stiff sensor path, plastic box for protection only (D7).** The accelerometer sits on the aluminium block's boss above a magnet, and the block sits on the magnets. The box rides on four nylon stand-offs 5 mm above the block, which keeps its floor 13 K cooler on a hot frame. The mount still resonates inside the upper vibration band on curved frames (R5).
- **Features on the pod, spectra on a slow schedule (D10).** Summaries every minute and a spectrum every 15 minutes come to about 1.15 MB a day, so one gateway can serve many machines. Raw bursts can be captured on demand for diagnosis.
- **One CT on one phase (D4).** Enough for run state, run hours and relative load, within budget. With a power factor curve the energy estimate is at risk rather than not met; a voltage reference or three CTs would cost $10 to $20 more. Decided by Amish, 2026-10-02: R4 is a relative energy trend for the first build, and any kWh figure is reported as an estimate; the voltage reference stays an option for sites that need absolute energy.
- **Wi-Fi first (D1).** Small workshops usually have Wi-Fi, and 7.4 kB spectra are far too large for a LoRaWAN duty cycle. A summaries-only LoRaWAN variant could reuse the FieldNode radio core later.
- **High-temperature magnets (MPL-DDR-002, N1).** The magnets sit within about 2 K of the frame, so the standard 80 °C grade had no margin on an 80 °C frame. Pot magnets rated 120 °C cost about $1.00 more for the pair and move the pod's hot-frame limit to about 110 °C, set by the accelerometer.
- **Mains-powered adapter, no battery (D2).** A certified 5 V adapter avoids lithium cells on a hot, vibrating frame.
- **Baseline, not fixed limits (D5).** Old machines differ too much for fixed alarm levels to be useful at first. Each machine is compared with its own first week, by load band, and flags go to a person.
- **Data stays local (D6).** MQTT to the TwinKit gateway, where the twin shows readings on the machine's model; any other broker works too.

## Relation to other lab projects

- **TwinKit** is the default data home: its gateway accepts MQTT over Ethernet or Wi-Fi, stores data offline and shows readings against a model (TwinKit REQ R2). MachinePulse adds about 1.15 MB a day per machine, small against TwinKit's storage budget. MachinePulse is a natural first "small manufacturing" twin for it.
- **FieldNode** provides a LoRaWAN radio core if a summaries-only variant is wanted for sites without Wi-Fi. Only summaries would fit its 20-byte class payloads; spectra would not.
- **CalRig** can check the temperature probe against a reference before deployment. Vibration calibration needs a separate reference (a shaker or a known accelerometer) that CalRig does not provide.

## Safety

> **Safety:** Mains voltage. The CT goes around a live conductor. Fit it only with the machine isolated and locked off, only around a single insulated conductor, and have a qualified person open any terminal box or panel. Use only voltage-output CTs with an internal burden: a current-output CT left open-circuited on a live conductor can produce dangerous voltages ([OpenEnergyMonitor](https://docs.openenergymonitor.org/electricity-monitoring/ct-sensors/introduction.html)).

> **Safety:** Moving machinery. Fit and remove the pod and probe only when the machine is stopped and isolated. Mount on stationary frames, never on guards that open or on moving parts. Route leads away from belts, shafts, chucks and fans, and secure them with ties.

> **Safety:** Hot surfaces and magnets. Motor frames and compressor heads can be hot enough to burn; the sensor block runs within a few kelvin of the frame. Strong neodymium magnets can pinch fingers and snap together; keep them away from pacemakers and magnetic media.

> **Safety:** Power supply. Use only a certified 5 V adapter with the local safety mark. The pod contains no mains wiring and no lithium cells.

MachinePulse is a monitoring aid. It is not a protective device, it must never be wired into machine controls, and it does not replace overload relays, guards or scheduled maintenance.

## Open questions

- Co-design partner for alerts and dashboard (MPL-DDR-001, O1): the makerspace pilot already decided, with its shop lead deciding what "changed" should mean, and the maintenance person of one small production machine shop as a second voice (decided by Amish, 2026-10-02; the first candidates to approach, not agreed).
- Measured values for the assumptions MPL-CAL-001 rests on: ESP32-S3 ADC residual error, magnet contact stiffness and pull on painted frames. Amish decided to keep the R3 and R5 targets and to measure the ADC residual and the mount resonance first, with a flat steel saddle for curved frames as the option to consider (MPL-DDR-002, N3). These need bench work, which belongs to TRL 4 and is on hold.

Concept media: [blueprint sheet](../media/concept-blueprint.pdf), [interactive 3D model](../media/viewer.html).
