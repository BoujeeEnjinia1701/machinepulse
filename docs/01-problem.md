---
doc_id: MPL-PRB-001
title: MachinePulse problem statement
project: MachinePulse
doc_type: Problem statement
version: "0.4"
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
  change: Populate to TRL 2 (problem, users, context, constraints, prior work)
- version: "0.3"
  date: '2026-09-25'
  author: Amish Chadha
  change: Open questions updated for the items adopted for TRL 3 in MPL-DDR-001; CT constraint noted from MPL-CAL-001
- version: "0.4"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002)
---

# MachinePulse problem statement

Small factories run machines that have no monitoring, so breakdowns arrive without warning and utilization is unknown. The machines themselves are often sound: a 30-year-old lathe, pump or air compressor can run for decades more. What is missing is a cheap, safe way to see how hard each machine works and to notice when it starts to change.

## The problem

Most machines in small workshops are driven by an induction motor and have no electronics beyond a contactor and an overload relay. Maintenance is reactive: a bearing, belt or coupling runs until it fails, and the first sign is noise, heat or a stopped line. The owner also has no record of how many hours each machine actually runs, so decisions on staffing, replacement and energy use are guesses.

The cost of this is measurable. A NIST study of US discrete manufacturing estimated $119.1 billion of losses in 2016 from inadequate maintenance, and found that establishments in the top quarter for reliance on reactive maintenance had 3.3 times more downtime and 16 times more defects than those in the bottom quarter ([Thomas and Weiss, NIST AMS 100-34, 2020](https://nvlpubs.nist.gov/nistpubs/ams/NIST.AMS.100-34.pdf)). An earlier NIST review reported maintenance cost reductions of 15 % to 98 % from advanced maintenance in the literature it surveyed ([Thomas, NIST AMS 100-18, 2018](https://nvlpubs.nist.gov/nistpubs/ams/NIST.AMS.100-18.pdf)).

Condition monitoring is a mature field. ISO 20816-1 sets general conditions for measuring and evaluating machine vibration ([ISO](https://www.iso.org/standard/63180.html)), and motor makers sell predictive maintenance platforms ([ABB Ability Digital Powertrain Insights](https://www.abb.com/global/en/areas/motion/services/asset-health-and-monitoring/abb-ability-digital-powertrain-insights), for example). These products are priced and supported for large plants. Open energy monitors show that clip-on current transformers can be used safely by non-specialists when they measure an insulated conductor ([OpenEnergyMonitor CT guide](https://docs.openenergymonitor.org/electricity-monitoring/ct-sensors/introduction.html)), but they do not look at vibration or temperature. There is no open, low-cost reference design that combines run time, load, vibration and temperature for one old machine and that a small shop can build, inspect and adapt.

## Users and context

| User | Need | Context |
| --- | --- | --- |
| Owner of a small machine shop or plant | Run hours and load per machine; early warning before a breakdown | 5 to 50 machines, no maintenance engineer, shop Wi-Fi |
| Machine operator or maintainer | A simple sign that a machine has changed (hotter, rougher, drawing more current) | Shop floor, dusty and oily, noisy |
| Electrician or technician | A current clamp that fits safely and quickly on an insulated conductor | Installs during a planned stop, with the machine isolated |
| Makerspace, school or university workshop | Utilization of shared machines and a teaching tool for condition monitoring | Mixed users, safety-sensitive |
| Open hardware and digital twin community | A sensor that feeds TwinKit and can be adapted to other machines | Lab and field |

Typical machines: lathes and mills, bench and pillar drills, air compressors, water and coolant pumps, fans and blowers, grain and rice mills, and small conveyors, most driven by 0.37 kW to 15 kW induction motors on single-phase or three-phase supplies.

## Constraints

- Garage-buildable prototype, about $81 USD per monitored machine, from off-the-shelf modules and hand-made parts, with no custom PCB for the first build.
- Non-invasive: no change to the machine's wiring, controls or guarding. The pod attaches by magnets; the current clamp goes around one existing insulated single-core conductor (a multi-core cable carries currents that cancel, so the clamp cannot read it).
- Works on old machines with no electronics of their own, on cast iron, steel or aluminium frames.
- Low voltage only inside the pod (5 V USB from a certified adapter).
- Survives a workshop: dust, oil mist, splashes and frame temperatures typical of running motors.
- Data stays on the owner's network by default (TwinKit gateway or any MQTT broker); no cloud account is needed.

## Out of scope

- Machine protection or control. MachinePulse never trips, stops or starts a machine; existing protective devices stay in charge.
- Revenue-grade energy metering.
- Automated fault diagnosis with a guaranteed accuracy. The concept flags changes against the machine's own baseline for a person to check.

## Safety context

> **Safety:** The current clamp is fitted around a conductor at mains voltage. Fitting it may require opening a terminal box or panel, which is work for a qualified person with the machine isolated and locked off. The pod is fixed to a machine with rotating parts: mount it only on stationary surfaces, route leads away from belts, shafts and chucks, and never fit it while the machine runs.

## Open questions

- First pilot site and machines: a makerspace or university workshop with a lathe and a compressor. Decided by Amish, 2026-09-25: go with recommendation (MPL-DDR-001, D8).
- Co-design partner for the alerts and dashboard: who decides what "changed" should mean to an operator? No recommendation was made. Proposed, awaiting Amish (MPL-DDR-001, O1).
- Single-phase and three-phase coverage in the first build: one CT on one phase for both. Decided by Amish, 2026-09-25: go with recommendation (MPL-DDR-001, D4). Whether energy per shift (R4) is then accepted as at risk or relaxed to a relative trend is still awaiting Amish (O2).
- How many machines in a small shop offer a single insulated phase conductor outside a closed enclosure. MPL-CAL-001 finds R10 not met where they do not; the pilot site should show how common this is.
