---
doc_id: MPL-DDR-003
title: MachinePulse design for construction
project: MachinePulse
doc_type: Design decision record
version: "0.2"
status: Draft
date: '2026-10-02'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-10-01'
  author: Amish Chadha
  change: Changes that make the concept physically buildable, with the reason for each; made under Amish's 2026-09-30 instruction to make the design physically buildable; open for his review
- version: "0.2"
  date: '2026-10-02'
  author: Amish Chadha
  change: 'Accepted by Amish on 2026-10-02, with A1 and A2 as recommended; record stays Draft'
---

# 0003: Design for construction

- **Date:** 2026-10-01
- **Status:** accepted. Made under Amish's 2026-09-30 instruction to make the design physically buildable. Amish, 2026-10-02: "i approve your recommendations for all 555 open decisions." This covers every change in Tables 1 and 2 and the recommendations in Table 3 (A1 and A2), which are now decided as recommended and recorded in the design decisions register (MPL-DEC-001). The record stays Draft.

## Context

On 2026-09-30 Amish approved the build plan format for the portfolio and wrote: "If you are realising that the design cannot be built as per concept - fix the design assumptions to match and be physically feasible as you draw the illustrations." The concept model of MPL-DDR-002 showed what MachinePulse does and was enough for the calculations, but it was a massing model: several parts could not be made with hand tools and a drill press (R16), had no fixing, floated in space or overlapped their neighbours. Checking the model with build123d (intersections, distances and an assembly order) found the ten problems in Table 1.

The changes keep what the pod does: the same box, magnets, block footprint, boss height, stand-off gap, sensors, controller, CT, probe, power supply, data path and installed positions. Nothing here changes the pitch or the safety case. Every change is in `cad/src/model.py`, which now runs 102 constructability checks (`python cad/src/model.py --check`): 26 pairs of parts that must touch do touch without overlapping, 21 pairs that must be apart are apart by at least the stated gap, and no two of the 25 modelled components overlap anywhere (55 pairs whose outlines meet are checked). All 102 pass.

## Decision

*Table 1. Changes made to the model, the BOM and the calculations.*

| # | Problem in the concept | Change made | Why this way |
| --- | --- | --- | --- |
| P1 | The sensor block and its boss were one solid 21 mm tall with a 20 mm boss on a 10 mm plate. That needs a lathe or a mill, against R16's hand tools and a drill press. | The block is a 76 x 36 x 10 mm plate. The boss is a separate 11 mm length of 20 mm round bar, tapped M6 8 mm deep in its base, joined to the block by an M6 x 12 set screw with threadlocker in the left magnet's tapped hole, its face pulled down flat on the block. | Keeps the stiff metal path frame, magnet, block, boss, accelerometer and the boss height of 11 mm. The set screw shares the hole the magnet stud uses, so the boss sits directly over magnet 1 as the concept had it. |
| P2 | The magnets' M6 studs had no holes in the block. | Both magnet positions are drilled 5.0 mm and tapped M6 right through; the studs are trimmed to 5 mm and screwed in with threadlocker until the magnet backs sit flat on the block. | A tapped through hole can be made square in a drill press; 5 mm of stud leaves room for the set screw above magnet 1. |
| P3 | The four nylon stand-offs had no screws or holes, sat 0.6 mm from the edge of the 24 mm floor hole and overlapped the boot by about 9 mm³. | Stand-offs moved from 30 x 12 mm to 33 x 13 mm each side of centre; each is held by an M3 x 12 nylon screw from inside the box, through the floor and the stand-off, into an M3 tapped hole in the block. | The screws stay nylon, so the stand-offs remain a thermal break; the new positions clear the grommet by 1.4 mm and stay outside the magnets' footprint. |
| P4 | The silicone boot was a 1 mm ring floating 4 mm above the block, held by nothing. | A stock silicone grommet seated in the 24 mm floor hole, its 20 mm bore gripping the boss, with a 1 mm flange each side of the floor. | Seals the floor hole (R13) with a bought part; the soft grommet touches the boss over about the same length the thermal model already assumed, so the floor temperature result stands. |
| P5 | The controller and interface boards floated 5 mm above the floor with no fixing; module boards of this class usually have no mounting holes. | One carrier perfboard, 45 x 56 mm, on four M3 x 5 mm hex stand-offs screwed through the floor (the screw heads sit beside the block, outside its footprint). The interface circuit, jack, terminals, button and LED are on it, and the controller plugs into two 20-pin header sockets on it. | One board to fix instead of two; the controller can be lifted out to be programmed. The board stays 4 mm clear of the CT gland nut and 5 mm from the accelerometer. |
| P6 | The glands were cylinders fused to the outside of the end walls, with no holes and no nuts; the probe and USB leads shared one M12 gland, which a single-hole seal cannot seal; a USB-C plug cannot pass through a gland. | Three glands, one cable each, centred 15.5 mm up from the box underside so their nuts clear the floor and the corner pillars: an M16 gland (cable 4 to 8 mm) on the right end for the CT lead, whose 3.5 mm plug passes the seal, and two M12 glands on the left end for the probe and power leads. The power cable's far plug is cut off and its two wires go to a 5 V screw terminal on the carrier. | Keeps R13 (IP54) true for every lead, and lets every lead be fitted without cutting the CT's or the probe's own leads. The adapter itself stays a certified unit, so the safety case (D2) is unchanged. Also settles the review note's 2026-09-26 item 4 (two leads in one gland). |
| P7 | The box's moulded corner pillars and lid screws were not modelled, so clearances to them were unchecked. | The base now carries four 7 mm pillars; every gland nut, board and stand-off is checked against them. | The stock box has them; the carrier board and the gland positions were set to clear them. |
| P8 | The accelerometer board had no fixing, and at 18 x 18 mm (25.5 mm across the corners) it cannot pass the 24 mm floor hole. | It is bonded to the boss top with a thin layer of rigid two-part epoxy, after the base is fitted (build step 5). | A rigid bond is the usual way to mount a MEMS accelerometer for vibration; the order of assembly follows from the board's size. |
| P9 | The temperature probe's sleeve lay on top of a block "clip" 7 mm above the frame, so it did not touch the frame, and a magnetic clip for a 6 mm sleeve is not a stock part. | A made probe clip: an aluminium bar 42 x 16 x 10 mm with a 6.2 mm wide, 6.5 mm deep groove across its underside and two 12 x 3 mm high-temperature disc magnets bonded flush in pockets. The sleeve lies in the groove on its 0.5 mm thermal pad; the magnets pull the clip down and the groove presses the sleeve onto the pad. New BOM line 14. | Puts the sleeve where the probe calculation (MPL-CAL-001, F) assumed it: on a 6 x 20 mm pad on the frame. The magnets are a high-temperature grade because the clip sits on frames up to 100 °C. |
| P10 | The lid had an LED window but nothing carried light from the board to it. | A 3 mm light pipe stands on the status LED on the carrier and passes up through a 3.2 mm hole in the lid; its bezel is sealed to the lid with silicone. | Gives the status light the concept shows without opening the box; sealing the bezel keeps IP54. |

*Table 2. Knock-on changes.*

| Item | Change | Reason |
| --- | --- | --- |
| Mass | Pod 319 g [D6] (was 295 g). | Carrier board, sockets, glands, pillars and fixings. |
| Mount resonance (R5) | 892 Hz on a painted curved frame (was 927 Hz), 1,783 Hz flat (was 1,853 Hz); readings 10 % high from 267 Hz (was 278 Hz) [D7]. R5 stays at risk. | Follows the mass. |
| Magnet holding (R11) | Slip margin 3.0 curved (was 3.3), 2.8 at 80 °C (was 3.1); pull-off 12.2 (was 13.2); 3 mm pads 7.0 (was 7.5) [E3, E5, G5]. R11 stays met by calculation. | Follows the mass. |
| Thermal (R12) | Unchanged: the stand-off gap, block, box and boss contact are the same, and the grommet replaces the boot with the same contact. | |
| Cost | BOM lines 2, 7, 9 and 12 repriced and line 14 added. Value-engineering target: USD 81. Estimated cost of the constructable design: USD 83.50 (USD 2.50 over the target) [J1]. `budget_usd` unchanged. | Parts added for construction; see the register's value engineering section. |
| Size | 137 mm over the glands (was 132 mm); 100 x 68 x 63 mm unchanged. | The M16 gland is longer than the M12 it replaces. |
| Drawing | MPL-DWG-001 Rev P4; making sketches MPL-DWG-101 to 106 added. | Follows the model. |
| Documents | MPL-CAL-001 v0.3, MPL-REQ-001 v0.5, MPL-PRC-001 v0.5, `bom/bom.csv`, `bom/bom-notes.md`. No requirement target changed; R16 is now reported against the value-engineering target. | Follows the model. |

*Table 3. Items that were proposed, awaiting Amish; decided by Amish on 2026-10-02.*

| # | Question | Options | Recommendation |
| --- | --- | --- | --- |
| A1 | How the 5 V supply enters the box. | (a) cut the USB cable's far plug and wire it through an M12 gland to a screw terminal, as modelled; (b) an IP67 panel-mount USB-C socket in the end wall, about USD 5 more. | (a) for the prototype: cheapest, sealed, and the adapter stays certified. **Decided by Amish, 2026-10-02:** (a). |
| A2 | Where the status button goes (carried over from the 2026-09-26 review note, item 1). | (a) on the carrier board, pressed with the lid off, as modelled; (b) a sealed button on the lid beside the light pipe, about USD 1.50 more and another lid hole. | (a) for the prototype; (b) if pairing in the field turns out to need it. **Decided by Amish, 2026-10-02:** (a), pressed with the lid off; a sealed lid button only if field pairing shows it is needed. |

## Consequences

- `design_state: constructable` in `project.yaml`. The build plan MPL-BLD-001 shows every component and step in pictures generated from the model (`cad/src/build_plan_media.py`); open items are in the design decisions register MPL-DEC-001.
- Requirement status (MPL-CAL-001 v0.3): 1 not met (R10), 3 at risk (R3, R4, R5), 9 met by calculation, 3 met by design, and R16 USD 2.50 over the value-engineering target.
- The photoreal renders (`media/render-*.png`), `media/card.png`, `media/social-preview.png` and the appearance model `cad/src/product_model.py` still show the concept's boss, glands and boards; they need updating on Amish's Mac, where Blender is.
- Parts to check when bought (stud length, gland seals, grommet, box pillars, controller pin rows, light pipe hole) are listed in the register.
- TRL 4 is on hold by Amish's instruction. Nothing in this record authorizes building, testing or buying parts.
