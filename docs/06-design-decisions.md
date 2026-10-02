---
doc_id: MPL-DEC-001
title: MachinePulse design decisions register
project: MachinePulse
doc_type: Design decisions register
version: "0.2"
status: Draft
date: '2026-10-02'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-10-01'
  author: Amish Chadha
  change: Register opened with the build plan; open decisions from MPL-DDR-001 to 003 and the review note
- version: "0.2"
  date: '2026-10-02'
  author: Amish Chadha
  change: 'Amish approved the recommendations for all six open decisions (2026-10-02); MPL-DDR-003 accepted; moved to decisions made'
---

# MachinePulse design decisions register

Every design decision still to be made, and every decision made, in one place. Each decision is argued in full in its decision record under `docs/decisions/`; this register is the index Amish works from. The build plan (`docs/05-build-plan.md`) describes the design as it stands and does not list open decisions.

## Open decisions

None. All open decisions were decided on 2026-10-02.

## To confirm when parts are bought

| # | What to confirm | Why it matters | Source |
| --- | --- | --- | --- |
| 1 | The current transformer's 3.5 mm plug passes the M16 gland's seal | Otherwise the plug must be fitted after the lead is through, or a larger gland used | MPL-DDR-003, P6 |
| 2 | The pot magnets' M6 studs are at least 5 mm long and can be trimmed | The stud and the set screw share the block's left hole | MPL-DDR-003, P1, P2 |
| 3 | The silicone grommet fits a 24 mm hole in 2.5 mm panel and grips a 20 mm boss | It seals the floor and must stay soft so it carries little vibration or heat | MPL-DDR-003, P4 |
| 4 | The stock box: four corner pillars about 7 mm across, 2.5 mm walls, continuous use at 70 °C | The gland heights, the carrier position and the thermal model assume them | MPL-DDR-003, P7; MPL-CAL-001, G |
| 5 | The controller board: about 22 x 51 mm, two 20-pin rows 19.4 mm apart, no octal PSRAM | The carrier's header sockets are spaced for it | MPL-DDR-003, P5; MPL-CAL-001, G4 |
| 6 | The light pipe's hole size (3.2 mm clearance or 3.0 mm press fit) and its length (about 29 mm) | The lid hole and the LED position follow from it | MPL-DDR-003, P10 |
| 7 | The probe clip's disc magnets are rated 150 °C or more | The clip sits on frames up to 100 °C | MPL-DDR-003, P9 |
| 8 | The accelerometer breakout's size (about 18 x 18 mm) and that its back can be bonded flat | It is bonded to the 20 mm boss top | MPL-DDR-003, P8 |

## Value engineering

Value-engineering target: USD 81 (a hypothetical control target, not a limit). Estimated cost of the constructable design: USD 83.50 (USD 2.50 over the target). Main cost drivers and savings worth trying:

- The largest lines are the accelerometer (USD 15, the least certain price), the current transformer (USD 10), the controller (USD 9), the box with its glands (USD 9.50) and the power adapter (USD 8).
- Making the design constructable added USD 2.50: the third gland and the larger M16 gland (USD 0.50), the carrier board's sockets, terminals and light pipe (USD 1.00), the made probe clip with its magnets in place of a bought clip (USD 0.50 net) and the grommet, set screw and carrier fixings (USD 0.50).
- Savings worth trying: the steel pads (USD 4 for two) are needed only on aluminium-framed machines and could be left out of the standard kit; the accelerometer price should be checked against current breakout boards; an adapter and cable bought in quantity, or reused from an existing USB charger at the site, would cover the gap.

## Decisions made

| Date | Decision | Decided by | Record |
| --- | --- | --- | --- |
| 2026-09-25 | TRL 2 review items D1 to D10: Wi-Fi first, certified 5 V adapter, IIS3DWB-class sensor, one CT on one phase, first-week baseline alerts, TwinKit or any MQTT broker, stock ABS box on 5 mm nylon stand-offs, makerspace pilot, no budget change, features every minute and a spectrum every 15 minutes | Amish: "i accept all your recommendations, go with them across all repos." | MPL-DDR-001, MPL-DDR-002 |
| 2026-09-25 | N1 high-temperature pot magnets rated 120 °C; N2 R8 restated (2 °C to 85 °C, 4 °C from 85 to 100 °C); N3 keep the R3 and R5 targets and measure first at TRL 4 | Amish, same instruction | MPL-DDR-002 |
| 2026-09-30 | Build plans are written in the approved format, and the design is made physically buildable as the pictures are drawn | Amish: "If you are realising that the design cannot be built as per concept - fix the design assumptions to match and be physically feasible as you draw the illustrations." | MPL-DDR-003 (changes accepted on 2026-10-02, below) |
| 2026-09-30 | Open decisions are kept in this register, not in the build plan | Amish: "don't log outstanding decisions in this build plan - that is not the place for it." | This register |
| 2026-10-01 | `budget_usd` is a value-engineering target, not a limit | Amish: "the budgets are a hypothethical control target to ensure we are thinking along a value engineering lens." | This register, Value engineering |
| 2026-10-02 | Design for construction accepted: all ten changes of Table 1 and their knock-on changes, as made | Amish: "i approve your recommendations for all 555 open decisions." | MPL-DDR-003, Table 1 |
| 2026-10-02 | Power entry: (a) for the prototype, the cut USB cable through an M12 gland to a screw terminal | Amish: "i approve your recommendations for all 555 open decisions." | MPL-DDR-003, A1 |
| 2026-10-02 | Status button: (a) for the prototype, on the carrier board and pressed with the lid off; a sealed lid button only if field pairing shows it is needed | Amish: "i approve your recommendations for all 555 open decisions." | MPL-DDR-003, A2; review note 2026-09-26, item 1 |
| 2026-10-02 | R4: restated as a relative energy trend for the first build, with any kWh figure reported as an estimate; the voltage reference (c) stays an option for sites that need absolute energy | Amish: "i approve your recommendations for all 555 open decisions." | MPL-DDR-001, O2; MPL-DDR-002 |
| 2026-10-02 | Co-design partner for alerts and dashboard: the makerspace pilot already decided, with its shop lead deciding what "changed" should mean, and the maintenance person of one small production machine shop as a second voice (first candidate type to approach, not agreed) | Amish: "i approve your recommendations for all 555 open decisions." | MPL-DDR-001, O1 |
| 2026-10-02 | Enclosure colour: a single-colour stock box is bought; two-tone stays a later option | Amish: "i approve your recommendations for all 555 open decisions." | Review note 2026-09-26, item 2 |
