---
doc_id: MPL-DDR-002
title: MachinePulse recommendations accepted
project: MachinePulse
doc_type: Design decision record
version: "0.2"
status: Draft
date: '2026-10-02'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: Record the recommendations accepted by Amish on 2026-09-25, what changed in the repo, and the items still open
- version: "0.2"
  date: '2026-10-02'
  author: Amish Chadha
  change: 'O1 and O2 decided by Amish on 2026-10-02'
---

# 0002: Recommendations accepted

- **Date:** 2026-09-25
- **Status:** accepted. Amish accepted every recommendation in this repo on 2026-09-25. Items with no recommendation stayed "Proposed, awaiting Amish" until Amish decided them on 2026-10-02 ("i approve your recommendations for all 555 open decisions.").

## Context

On 2026-09-25 Amish wrote: "i accept all your recommendations, go with them across all repos." Before that, MachinePulse held ten items adopted for TRL 3 work and open for his review (MPL-DDR-001, D1 to D10), three new proposals from the TRL 3 calculations (`docs/REVIEW.md`, session "TRL 3", items 3 to 5) and two items without a single recommendation (MPL-DDR-001, O1 and O2).

## Options considered

The options for each item are those in `docs/REVIEW.md` (sessions "/populate" and "TRL 3") and in MPL-DDR-001. Where a recommendation named one of several options, that option is the decision.

## Decision

*Table 1. Items decided by Amish, 2026-09-25: go with recommendation.*

| # | Item | Decision | What changed in the repo |
| --- | --- | --- | --- |
| D1 | Radio | Wi-Fi on the ESP32-S3 first; LoRaWAN summaries through FieldNode a later option | Status wording only (MPL-DDR-001 v0.2, MPL-PRC-001 v0.4) |
| D2 | Power | Certified 5 V USB adapter | Status wording only |
| D3 | Accelerometer | IIS3DWB class, ADXL345 class as documented fallback | Status wording only |
| D4 | Current sensing | One CT on one phase | Status wording only (MPL-PRB-001 v0.4) |
| D5 | Alert logic | First-week baseline per load band; flags to a person | Status wording only |
| D6 | Data home | TwinKit gateway, any MQTT broker, no cloud | Status wording only |
| D7 | Enclosure | Stock IP54 ABS box on 5 mm nylon stand-offs | Status wording only |
| D8 | Pilot site | A makerspace or university workshop with a lathe and a compressor | Status wording only (MPL-PRB-001 v0.4); choosing the actual site and running the pilot are TRL 4 work, on hold |
| D9 | Budget | No change at the time; superseded in effect by N1 | See N1 |
| D10 | Data schedule | Features every minute, a spectrum every 15 min | Status wording only |
| N1 | Magnets for hot frames (R12) | Option (b): high-temperature pot magnets rated 120 °C or more, about $1.00 more for the pair | `cad/src/model.py` gains `mag_t_max` = 120 °C (geometry unchanged); STEP and STL re-exported; BOM line 6 from $3.50 to $4.00 each, parts from $80.00 to $81.00; `budget_usd` from 80 to 81; GA MPL-DWG-001 from Rev P1 to Rev P2 (magnet note); MPL-CAL-001 v0.2: hot-frame limit from 81.3 °C (magnets) to 109.6 °C (accelerometer), R12 from at risk to met by calculation; R16 target from $80 to $81 in MPL-REQ-001 v0.4 |
| N2 | R8 range | Restate R8 as within 2 °C from 0 to 85 °C and within 4 °C from 85 to 100 °C | MPL-REQ-001 v0.4; R8 from at risk to met by calculation (1.69 K at 85 °C, 3.59 K at 100 °C) |
| N3 | R3 and R5 follow-up | Keep both targets; measure the ADC residual and the mount resonance first at TRL 4; consider a flat steel saddle for curved frames | Targets unchanged; noted in MPL-CAL-001 v0.2 and MPL-PRC-001 v0.4. The measurements and any saddle design are TRL 4 work, decided but on hold |

*Table 2. Items left open on 2026-09-25, decided by Amish on 2026-10-02.*

| # | Item | Status |
| --- | --- | --- |
| O1 | Co-design partner for the alerts and dashboard. No recommendation was made. | Decided by Amish, 2026-10-02: the makerspace pilot already decided, with its shop lead deciding what "changed" should mean, and the maintenance person of one small production machine shop as a second voice |
| O2 | How to treat R4 with one CT: accept at risk with a power factor curve, relax to "relative energy trend", or add a voltage reference ($10, parts $91.00). The recommendation offered two courses without choosing one, so no option is taken. | Decided by Amish, 2026-10-02: (b), R4 restated as a relative energy trend for the first build, with any kWh figure reported as an estimate; the voltage reference (c) stays an option for sites that need absolute energy |

## Consequences

- Requirement status (MPL-CAL-001 v0.2): 1 not met (R10), 4 at risk (R3, R4, R5, R16), 9 met by calculation, 3 met by design. Before: 1 not met, 6 at risk, 7 met by calculation, 3 met by design.
- `project.yaml`: `budget_usd` from 80 to 81; `trl` and `trl_target` stay 3. No reworded pitch or problem was recommended, so those lines are unchanged.
- Controlled documents revised: MPL-PRB-001 v0.4, MPL-PRC-001 v0.4, MPL-REQ-001 v0.4, MPL-CAL-001 v0.2, MPL-DDR-001 v0.2; drawing MPL-DWG-001 Rev P2; concept media regenerated.
- Cross-repo actions: none required. The decisions do not change any interface with TwinKit, FieldNode or CalRig.
- TRL 4 is on hold by Amish's instruction. Nothing in this record authorizes building, testing or buying parts.
