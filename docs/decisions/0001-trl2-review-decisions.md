---
doc_id: MPL-DDR-001
title: MachinePulse TRL 2 review decisions
project: MachinePulse
doc_type: Design decision record
version: "0.2"
status: Draft
date: '2026-09-25'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: Record the TRL 2 review items adopted for TRL 3 work under Amish's 2026-09-25 instruction, and the items that remain open
- version: "0.2"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002)
---

# 0001: TRL 2 review decisions

- **Date:** 2026-09-25
- **Status:** accepted for D1 to D10. On 2026-09-25 Amish wrote "i accept all your recommendations, go with them across all repos", so items D1 to D10 are decided as recommended (see MPL-DDR-002). Items O1 and O2 carry no single recommendation and remain "Proposed, awaiting Amish".

## Context

The TRL 2 review note (`docs/REVIEW.md`, session 2026-09-25, /populate) listed nine items as "Proposed, awaiting Amish", and the design precis MPL-PRC-001 v0.2 listed key design choices, most with options and a recommendation. On 2026-09-25 Amish asked for this batch of repos to be taken through the usual process with the instruction "you know the drill, nothing gets past TRL 3". He has not reviewed this repo's items one by one. Every item that carries a recommendation is therefore adopted as recommended for TRL 3 under that instruction, open for his review. Items without a single recommendation stay open.

## Options considered

The options for each item are those listed in `docs/REVIEW.md` (session 2026-09-25, /populate) and in MPL-PRC-001 v0.2, Key design choices.

## Decision

*Table 1. Items decided by Amish on 2026-09-25 (first adopted for TRL 3 work, then accepted).*

| # | Item | Adopted recommendation | Status |
| --- | --- | --- | --- |
| D1 | Radio | Wi-Fi on the ESP32-S3 first; a summaries-only LoRaWAN variant through the FieldNode radio core stays a later option | Decided by Amish, 2026-09-25: go with recommendation |
| D2 | Power | Certified 5 V USB adapter; no battery and no energy harvesting | Decided by Amish, 2026-09-25: go with recommendation |
| D3 | Accelerometer | IIS3DWB class, with the ADXL345 class kept as a documented fallback | Decided by Amish, 2026-09-25: go with recommendation |
| D4 | Current sensing | One CT on one phase, for single-phase and three-phase machines | Decided by Amish, 2026-09-25: go with recommendation |
| D5 | Alert logic | Baseline learned over the first week per load band; flags at twice baseline vibration or a temperature rise above baseline, sent to a person; fixed ISO 20816 zones a later option | Decided by Amish, 2026-09-25: go with recommendation |
| D6 | Data home | TwinKit gateway by default, any MQTT broker supported, no cloud dependency | Decided by Amish, 2026-09-25: go with recommendation |
| D7 | Enclosure | Stock IP54 ABS box for the first build, with a stand-off or insulating pad studied at TRL 3 for hot frames | Decided by Amish, 2026-09-25: go with recommendation |
| D8 | Pilot site | A makerspace or university workshop with a lathe and a compressor | Decided by Amish, 2026-09-25: go with recommendation |
| D9 | Budget | No change: `budget_usd` stays $80. Superseded in effect by MPL-DDR-002, N1, which raises it to $81 for high-temperature magnets | Decided by Amish, 2026-09-25: go with recommendation |
| D10 | Data schedule | Features computed on the pod every minute, a spectrum every 15 min, raw bursts on demand | Decided by Amish, 2026-09-25: go with recommendation |

*Table 2. Items that remain open.*

| # | Item | Status |
| --- | --- | --- |
| O1 | Co-design partner for the alerts and dashboard: who decides what "changed" should mean to an operator. No recommendation was made. | Proposed, awaiting Amish |
| O2 | How to treat R4 with one CT. The TRL 2 note offered two courses without choosing: accept that R4 is not met in the first build, or relax R4 to "relative energy trend". MPL-CAL-001 now puts R4 at risk (8.5 % RSS) rather than not met, which bears on this choice. R4 keeps its 10 % target until Amish decides. | Proposed, awaiting Amish |

## Consequences

- `project.yaml`: only the TRL fields change. No budget change was recommended (D9), and no reworded pitch or problem line was recommended, so `budget_usd`, `pitch` and `problem` and the matching lines in `README.md` keep their wording. MPL-DDR-002 later raised `budget_usd` to $81.
- MPL-PRB-001, MPL-PRC-001 and MPL-REQ-001 are revised to v0.3. The key design choices in the precis are no longer "proposed". No requirement target changes as a result of these decisions; R4 stays at 10 % pending O2.
- D7 study result (MPL-CAL-001, section G): 5 mm nylon stand-offs between the sensor block and the box floor keep the floor at 53.9 °C on an 80 °C frame, against 67.2 °C without them. They are added to the design and the BOM (line 13, $1.00), which brings the parts to $80.00, exactly the budget.
- Other details added within these decisions by the calculations: a CT bias of 1.50 V, clamp diodes on the CT input, a ±16 g accelerometer range, a module without octal PSRAM, 3 mm steel pads, a silicone boot round the boss and a load-dependent power factor curve in the gateway software.
- New proposals from MPL-CAL-001 (high-temperature magnets, R8 range, R3 and R5 follow-up) were decided by Amish on 2026-09-25 and are recorded in MPL-DDR-002.
- TRL 4 is on hold by Amish's instruction. Nothing in this record authorizes building or testing.
