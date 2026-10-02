# Review note: MachinePulse

## Session 2026-09-25: /populate to a strong TRL 2 (batch run)

### What was done

- `docs/01-problem.md` (MPL-PRB-001 v0.2): problem, cited prior work (NIST maintenance studies, ISO 20816-1, OpenEnergyMonitor, vendor platforms), users and context, constraints, out of scope, safety context, open questions.
- `docs/03-requirements.md` (MPL-REQ-001 v0.2): 17 measurable requirements (R1 to R17) with targets, concept status and planned verification.
- `docs/02-concept.md` (MPL-PRC-001 v0.2): how it works, main components, first-order numbers with assumptions, design choices, relation to TwinKit, FieldNode and CalRig, safety, open questions.
- `cad/src/concept_media.py`: massing model of the pod (lid, base, controller, accelerometer, aluminium sensor block, magnets, interface board), current transformer and temperature probe, each with a BOM number, on a 7.5 kW class induction motor shown in grey for scale. The scene is shifted so the pod sits near the origin, because the kit's cutaway cutter is centered there.
- `media/`: `hero.png`, `concept-blueprint.png`, `.pdf` and `.svg`, `model.glb` and `viewer.html`, `exploded.png` (callouts 1 to 9 match the BOM), `cutaway.png` (section through the accelerometer and sensor block) and `flow.png` (data flow, values marked as estimates).
- `bom/bom.csv` (12 lines, indicative USD prices, numbered to match the exploded view) and `bom/bom-notes.md`.
- `README.md`: hero image and links line, concept rationale, burning platform with cited figures, use tables by industry and by region, origin and trigger, updated concept, components and safety.
- `docs/pdf/`: branded PDFs of the three controlled documents.
- `project.yaml`: unchanged. The pitch and problem still match the concept and the numbers found.

### Key results (estimates, to be checked at TRL 3)

| Quantity | Estimate | Requirement |
| --- | --- | --- |
| Parts cost | about $79 | R16 met, $1 margin |
| Pod size and mass | 100 x 68 x 58 mm, about 0.35 kg | |
| Power | about 0.5 W from 5 V | |
| Vibration band and noise | 10 to 1,000 Hz, about 0.04 mm/s RMS | R5, R6 met on datasheet |
| Spectrum resolution | 0.41 Hz | R7 met |
| Current accuracy | about 3 % of reading | R3 met on paper |
| Energy accuracy | about 20 % | R4 **not met** |
| Data volume and offline store | about 0.4 MB per day, about 10 days | R9, R15 met |
| Frame temperature limit | about 60 °C | R12 **not met** (target 80 °C) |

**Requirements not met:** R4 (energy within 10 %: one CT with assumed voltage and power factor gives about 20 %), R10 (fitting the CT without opening a live enclosure: not possible on many machines, which need a qualified person and isolation), R12 (frames up to 80 °C: the stock ABS box and module limit the concept to about 60 °C). **Unverified with known risk:** R6 (magnet mount effect on noise and bandwidth), R8 (probe contact error), R11 (magnet pull on painted curved frames).

### Proposed, awaiting Amish

1. **Radio.** Options: Wi-Fi on ESP32-S3; LoRaWAN summaries only via the FieldNode radio core; both. Recommendation: Wi-Fi first, because spectra do not fit a LoRaWAN duty cycle and small shops usually have Wi-Fi. **Decided by Amish, 2026-09-25: go with recommendation** (MPL-DDR-002).
2. **Power.** Options: certified 5 V USB adapter; Li-ion battery; energy harvesting from the CT. Recommendation: adapter, which avoids lithium cells on hot, vibrating frames. **Decided by Amish, 2026-09-25: go with recommendation** (MPL-DDR-002).
3. **Accelerometer.** Options: IIS3DWB class (about $15, low noise, dc to 6 kHz); ADXL345 class (about $6, noisier, about 1.6 kHz). Recommendation: IIS3DWB class; keep ADXL345 as a documented fallback. **Decided by Amish, 2026-09-25: go with recommendation** (MPL-DDR-002).
4. **Current sensing.** Options: one CT on one phase (within budget); three CTs (about $20 more, over budget); one CT plus a voltage reference. Recommendation: one CT, and accept that R4 is not met in the first build, or relax R4 to "relative energy trend". **One CT: decided by Amish, 2026-09-25: go with recommendation.** The R4 treatment offered two courses without choosing and stays **Proposed, awaiting Amish** (MPL-DDR-001, O2).
5. **Alert logic.** Baseline learned over the first week per load band, flags at twice baseline vibration or a temperature rise above baseline, sent to a person. Recommendation: adopt for the first build; fixed ISO 20816 zones as a later option. **Decided by Amish, 2026-09-25: go with recommendation** (MPL-DDR-002).
6. **Data home.** Options: TwinKit gateway; any MQTT broker; a cloud service. Recommendation: TwinKit gateway with any broker supported, no cloud dependency. **Decided by Amish, 2026-09-25: go with recommendation** (MPL-DDR-002).
7. **Enclosure.** Options: stock IP54 ABS box; 3D-printed box; die-cast aluminium box (better for R12, about $10 more). Recommendation: stock ABS box for the first build, with a stand-off or insulating pad studied at TRL 3 for hot frames. **Decided by Amish, 2026-09-25: go with recommendation** (MPL-DDR-002).
8. **Pilot site.** Options: a makerspace or university workshop; a small machine shop; a food or grain processing unit. Recommendation: a makerspace or university workshop with a lathe and a compressor. **Decided by Amish, 2026-09-25: go with recommendation** (MPL-DDR-002).
9. **Budget.** No change proposed: the parts total of about $79 is within the $80 budget. A three-CT or die-cast variant would need a budget increase, which is Amish's decision. **Decided by Amish, 2026-09-25: go with recommendation** (MPL-DDR-002). Later superseded by the high-temperature magnet decision, which raised the budget to $81.

### Safety concerns

- Mains voltage at the CT: fitting often needs a terminal box or panel opened by a qualified person with the machine isolated and locked off. Only voltage-output CTs with an internal burden are allowed.
- Moving machinery: fit and remove only with the machine stopped; leads must be tied clear of belts, shafts and chucks.
- Hot frames and strong magnets: burn and pinch hazards; magnets away from pacemakers.
- MachinePulse is a monitoring aid, not a protective device; it must never be wired into machine controls.

### Suggestions (not in the repo)

- A short guide for pilot sites on where to mount the pod on common machines (lathe headstock, compressor, pump) could come with the TRL 3 work.
- A TwinKit example twin of one motor would show the full data path end to end.

### Recommended next step

Review this note and the media, and decide the proposed items above, in particular the radio, current sensing and pilot site. If approved, run `/advance-trl3` to check the vibration noise and magnet mount, the current error budget, the thermal limit and the data budget by calculation, and to produce the parametric model and drawing sheet.

## Session 2026-09-25: TRL 3

On 2026-09-25 Amish asked for this batch of repos to be taken through the usual process with the instruction "you know the drill, nothing gets past TRL 3". He has not reviewed this repo's TRL 2 items one by one, so every item that carried a recommendation is adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review. This session ran `/advance-trl3` on that basis and stopped at TRL 3.

### What was done

- `docs/decisions/0001-trl2-review-decisions.md` (MPL-DDR-001 v0.1, status proposed): ten items adopted as recommended for TRL 3, open for Amish's review (D1 to D10), and two left open (O1, O2).
- `docs/04-calcs/01-sizing.md` (MPL-CAL-001 v0.1) and `docs/04-calcs/sizing.py`: CT window and starting current, current and energy error budgets, run state and run time, vibration noise, range, memory, resolution and mount resonance, magnet pull, slip and tipping, probe contact error, a three-node thermal model of the pod on a hot frame, power, data, delivery and offline store, and cost, with a status for every requirement. The script imports the model (`PARAMS`, `derived()` and the part solids for mass), reads the BOM and `project.yaml`, and prints every number the note quotes with a tag.
- `cad/src/model.py`: parametric build123d model of the pod (magnets, block with round boss, nylon stand-offs, box base with floor hole and glands, lid, silicone boot, accelerometer, controller and interface boards), the CT and the probe, with installed positions on a context motor. Exports `cad/step/` and `cad/stl/` for `machinepulse-assembly`, `machinepulse-pod` and `sensor-block`.
- `cad/src/sheets.py` and `cad/drawings/MPL-DWG-001.svg`, `.pdf`, `.png`: general arrangement at Rev P1, 1:1, marked "CONCEPT, NOT FOR FABRICATION" and "PRELIMINARY, NOT FOR FABRICATION". MPL-DWG-001 was free because the concept blueprint is MPL-DWG-010.
- `bom/bom.csv` (13 lines, all priced with a supplier or supplier type, $80.00) and `bom/bom-notes.md`. Changes: line 13 nylon stand-offs added ($1.00); lines 3, 4, 5, 7, 8 and 11 respecified from the calculations (module without octal PSRAM, ±16 g range, round boss, 1.50 V bias with clamp diodes, 5 to 60 A CT range, 3 mm pads).
- `cad/src/concept_media.py` now builds from the model; all of `media/` was re-rendered and every image checked; temporary `media/_views*` folders deleted. The model puts the magnet contact line at the origin, so the kit's cutaway cuts through the pod without the scene shift used at TRL 2.
- MPL-PRB-001, MPL-PRC-001 and MPL-REQ-001 revised to v0.3; `README.md` (TRL badge and line, links, concept numbers, components) and `project.yaml` (`trl: 3`, `trl_target: 3`, evidence list) updated. PDFs rebuilt in `docs/pdf/`.

### Requirement status (MPL-CAL-001, Table 4)

1 not met, 6 at risk, 7 met by calculation, 3 met by design.

| ID | Status | Key number |
| --- | --- | --- |
| R10 Install without opening live enclosures | **Not met** | The CT needs a single insulated conductor, often only inside a terminal box or panel |
| R3 Current | At risk | 3.6 % RSS but 7.0 % worst case at 10 % of range; ADC residual assumed |
| R4 Energy | At risk | 8.5 % RSS, 16.0 % worst case with a PF curve; 26 % with a fixed PF (TRL 2 said about 20 %, not met) |
| R5 Vibration band | At risk | Mount resonance about 927 Hz on a painted curved frame (1,853 Hz flat); +10 % from 278 Hz |
| R8 Probe | At risk | 1.56 K at 80 °C, about 3.6 K at 100 °C |
| R12 Hot frames | At risk | Box and module pass with stand-offs; N-grade magnets hit 80 °C at an 81.3 °C frame |
| R16 Cost | At risk | $80.00 against $80, no margin |
| R1, R2, R6, R7, R9, R11, R15 | Met by calculation | 0.037 mm/s noise; 0.407 Hz bins; 1.15 MB/day; slip margin 3.3; 13.9 days offline |
| R13, R14, R17 | Met by design | |

Key numbers: design motor 14.6 A on a 30 A CT; pod 100 x 68 x 63 mm, 295 g; 0.42 W from 5 V (5.3 kWh a year at the wall); spectrum 7.4 kB. TRL 2 figures corrected: data 0.4 to 1.15 MB/day (a spectrum is 7.4 kB, not 1 kB), CT range 5 to 60 A (the 100 A SCT-013-000 is current output), "usable to 2 kHz" mount withdrawn, box limit about 60 °C replaced by a magnet limit of about 81 °C.

### Decisions recorded (MPL-DDR-001)

Decided by Amish, 2026-09-25: go with recommendation (first adopted for TRL 3 under his instruction, then accepted; see MPL-DDR-002): D1 Wi-Fi first; D2 certified 5 V adapter; D3 IIS3DWB class with ADXL345 fallback; D4 one CT on one phase; D5 first-week baseline alerts to a person; D6 TwinKit or any MQTT broker, no cloud; D7 stock ABS box with a stand-off studied (5 mm nylon stand-offs adopted from the study); D8 makerspace or university workshop pilot; D9 no budget change; D10 features every minute and a spectrum every 15 min. No reworded pitch or problem line was recommended, so `project.yaml` and `README.md` keep the existing wording. `budget_usd` stays $80.

### Still awaiting Amish

1. **O1, co-design partner** for the alerts and dashboard. No recommendation was made. Proposed, awaiting Amish.
2. **O2, R4 with one CT.** Options: (a) accept R4 as at risk with the power factor curve (8.5 % RSS); (b) relax R4 to "relative energy trend"; (c) add a voltage reference ($10, total $90.00, over budget). The TRL 2 note offered (a) or (b) without choosing, so no option is adopted. Proposed, awaiting Amish.
3. **New, magnets for hot frames (R12).** Options: (a) keep N-grade magnets and state the frame limit as 80 °C with no margin; (b) high-temperature pot magnets rated 120 °C or more, about $1.00 more for the pair, total $81.00, over the $80 budget. Recommendation: (b), because the magnets sit within 2 K of the frame. **Decided by Amish, 2026-09-25: go with recommendation** (MPL-DDR-002, N1); applied, `budget_usd` now 81.
4. **New, R8 range.** Recommendation: state R8 as within 2 °C from 0 to 85 °C, and within 4 °C from 85 to 100 °C. **Decided by Amish, 2026-09-25: go with recommendation** (MPL-DDR-002, N2); applied in MPL-REQ-001 v0.4.
5. **New, R5 and R3 follow-up.** Recommendation: keep both targets, record the mount resonance and the ADC residual as the first things to measure at TRL 4, and consider a flat steel saddle for curved frames. **Decided by Amish, 2026-09-25: go with recommendation** (MPL-DDR-002, N3); targets kept, measurements and saddle are TRL 4 work, on hold.

### Cross-repo consistency

- TwinKit (TWK REVIEW, TRL 3): accepts MQTT over Ethernet or Wi-Fi (R2), runs the broker and stores data locally. MachinePulse's 1.15 MB a day per machine is small against its storage budget. No conflict. TwinKit's twin service would host the baseline and the power factor curve; that is a software assumption, not an interface change.
- FieldNode (FND REVIEW, TRL 3): LoRaWAN core with 20-byte payloads. Only a summaries-only MachinePulse variant could use it; spectra cannot. No conflict, since D1 keeps Wi-Fi.
- CalRig (CLR REVIEW): can check the DS18B20 probe against its reference; no vibration reference. No interface assumed at TRL 3.
- CellGuard, MotionCore and ThermaCart: not used.

### Safety concerns

- Mains voltage at the CT: fitting often needs a terminal box or panel opened by a qualified person with the machine isolated and locked off. Only voltage-output CTs; the CT input on the interface board is now clamped against starting current (4.14 V peak at 6 x full load).
- Moving machinery: fit and remove only with the machine stopped; leads tied clear of belts, shafts and chucks.
- Hot frames and strong magnets: the block runs within a few kelvin of the frame; standard magnets are at their temperature limit on 80 °C frames. Magnets away from pacemakers.
- MachinePulse is a monitoring aid, not a protective device; it must never be wired into machine controls.

### Gaps and notes

- Prices are indicative, not supplier quotes. No citations were flagged as unchecked in the TRL 2 note, so no WebFetch checks were made and no sources were added.
- Assumptions that only tests can settle: ESP32-S3 ADC residual error, magnet contact stiffness, the pull-gap law and friction, probe contact resistance, and the thermal coefficients.
- The concept blueprint `media/concept-blueprint.png` shows the installed pod, CT and probe, so its orthographic views are small at 1:5; the GA sheet MPL-DWG-001 shows the pod at 1:1.
- Existing material beyond TRL 3: `build-log/README.md` (scaffold) is present, untouched and not extended. `firmware/` and `electronics/` hold only placeholders. No test, build or firmware material was created.

### Recommended next step

TRL 4 is on hold by Amish's instruction; this repo stops at TRL 3. Amish's review is needed on O1, O2 and new items 3 to 5 above. For the record only, TRL 4 would need: a bench build of one pod; a lab test report (TST, `environment: lab`) covering CT accuracy against a clamp meter across the range, energy against a reference meter, mounted resonance and noise on flat and curved painted steel, magnet pull and slip, probe error against a thermocouple, pod temperatures on a hot plate at 80 °C, and power and data volume over a sustained run; and build log entries. None of this has been started.

## Session 2026-09-25: recommendations accepted

On 2026-09-25 Amish wrote: "i accept all your recommendations, go with them across all repos." Every item in this note and in MPL-DDR-001 that carried a recommendation is now **Decided by Amish, 2026-09-25: go with recommendation**. The record is `docs/decisions/0002-recommendations-accepted.md` (MPL-DDR-002 v0.1).

### Decisions applied and what changed

- **D1 to D10 (MPL-DDR-001):** radio, power, accelerometer, one CT, baseline alerts, data home, enclosure with stand-offs, pilot site type, budget and data schedule. Wording changed from "adopted for TRL 3, open for review" to decided; no design change. D9 ("no budget change") is superseded in effect by N1.
- **N1, high-temperature magnets (R12):** BOM line 6 from $3.50 to $4.00 each (a 120 °C grade); parts from $80.00 to $81.00; `budget_usd` from 80 to 81; `mag_t_max` = 120 °C added to `cad/src/model.py` (geometry unchanged) and STEP and STL re-exported; MPL-DWG-001 from Rev P1 to Rev P2 (magnet note); hot-frame limit from 81.3 °C (magnets) to 109.6 °C (accelerometer); R12 from at risk to met by calculation.
- **N2, R8 range:** target from "within 2 °C, 0 to 100 °C" to "within 2 °C from 0 to 85 °C, within 4 °C from 85 to 100 °C"; 1.69 K at 85 °C and 3.59 K at 100 °C, so R8 moves from at risk to met by calculation.
- **N3, R3 and R5:** targets kept; ADC residual and mount resonance are the first TRL 4 measurements, and a flat steel saddle is the option to consider then. Decided but on hold.
- Documents revised: MPL-PRB-001 v0.4, MPL-PRC-001 v0.4, MPL-REQ-001 v0.4, MPL-CAL-001 v0.2 (script rerun, results match), MPL-DDR-001 v0.2, new MPL-DDR-002 v0.1; `bom/bom.csv`, `bom/bom-notes.md`, `project.yaml`, `README.md`. Concept media, the GA sheet and all PDFs were regenerated, which also removes the old site address from generated files.
- `README.md`: "What sparked the idea" rewritten around the Toyoda Type G automatic loom (1924) and its auto-stop devices, the origin of jidoka; the reference to how the project was chosen is removed.

### Requirement status now (MPL-CAL-001 v0.2)

1 not met, 4 at risk, 9 met by calculation, 3 met by design (was 1, 6, 7, 3).

| ID | Status | Key number |
| --- | --- | --- |
| R10 Install without opening live enclosures | **Not met** | CT needs a single insulated conductor, often inside a terminal box |
| R3 Current | At risk | 7.0 % worst case at 10 % of range |
| R4 Energy | At risk | 8.5 % RSS, 16.0 % worst case |
| R5 Vibration band | At risk | Mount resonance about 927 Hz on a curved frame |
| R16 Cost | At risk | $81.00 against $81, no margin |
| R1, R2, R6, R7, R8, R9, R11, R12, R15 | Met by calculation | R8 3.59 K at 100 °C against 4 °C; R12 limit 109.6 °C frame |
| R13, R14, R17 | Met by design | |

### Still awaiting Amish

1. **O1, co-design partner** for alerts and dashboard. No recommendation. Proposed, awaiting Amish.
2. **O2, R4 with one CT.** Accept at risk, relax to a relative energy trend, or add a voltage reference (parts $91.00). No single option was recommended. Proposed, awaiting Amish.

### Cross-repo actions

None. The decisions change no interface with TwinKit, FieldNode or CalRig.

### TRL 4

TRL 4 remains on hold by Amish's instruction. `trl: 3` and `trl_target: 3` are unchanged. No build, test, pilot, purchasing, PCB or firmware work was started.

## Session 2026-09-26: sources strengthened

- README, "By country or region", United States row: ITIF policy article (itif.org, citing NAM) replaced by the SBA Office of Advocacy manufacturing statistics (98 % of manufacturers are small), with NAM's Census-based figures (239,265 firms in 2022, all but 4,177 under 500 employees, about three-quarters under 20) kept alongside. The earlier "roughly 244,000" figure is replaced by the verified 2022 count.
- README, India and European Union rows: uncited statements about machine age removed; each row now states only what its source supports.
- All other README links (NIST, IEA, World Bank, PIB, IEA Africa Energy Outlook, ECLAC, Eurostat, Toyota Industries, Toyota) were fetched and confirmed to support their claims. "What sparked the idea" unchanged; it already rests on Toyota's own history pages.
- No controlled document changed; no budget change.

## Session 2026-09-26: product appearance model and photoreal renders

Amish chose this repo for the first batch of product renders on 2026-09-26.

### What was added

- `cad/src/product_model.py`: an appearance model for photoreal renders. `product_parts()` returns 41 parts (26 shell, 9 internal, 3 accessory, 3 context) with colour, material class, BOM line, group and explode offset. It also defines `TITLE` and `RENDER_VIEWS` (hero on the motor, exploded, and a detail view of the hub and sensors without the motor).
- Enclosure: two-tone stock box with filleted corners and edges, a parting-line groove at the lid joint, four lid screws in corner pockets, a lit status light pipe in a bezel (BOM 1 and 7), a silicone status button, and a printed lid label with the kit accent stripe.
- Fluted M12 cable glands with seal inserts on both end walls (BOM 2).
- Magnetic sensor base: filleted aluminium block and boss (BOM 5), M6 stud nut, high-temperature pot magnets with a pole groove (BOM 6), nylon stand-offs (BOM 13) and the silicone boot (BOM 12).
- Internals: ESP32-S3 board with module shield, USB-C and antenna print (BOM 3), interface perfboard with jack, terminal block and capacitors (BOM 7), accelerometer adapter board (BOM 4), brass board spacers (BOM 12).
- Current transformer: filleted ring and latch with the split-core seam, a latch finger recess, a "30 A : 1 V, VOLTAGE OUTPUT" marking and a cable strain relief (BOM 8).
- Temperature probe: filleted magnetic clip, retaining strap, stainless sleeve with crimp ring and heat-shrink boot (BOM 9).
- Accessories for the exploded view: the two steel adhesive pads (BOM 11) and the USB-C power adapter with its cable (BOM 10), neither of which model.py shows.
- Context: the 7.5 kW class motor from `motor_context()` in clay, the insulated phase conductor through the clamp, and swept clamp, probe and USB leads.
- `README.md`: hero image now points to `media/render-hero.png`, with a link to `media/render-exploded.png`. The render files are produced separately.

### Differences from model.py

Every main dimension and interface (box, lid and base heights, wall, glands, floor hole, block and boss, magnets, stand-offs, board positions, clamp and probe envelopes, installed positions) is taken from PARAMS and derived(). The following are appearance choices, each Proposed, awaiting Amish:

1. **Status button on the lid.** BOM line 7 lists a button, but model.py shows no lid opening for it. The appearance model puts a 9 mm silicone button at pod coordinates (30, -4), next to the LED. Recommendation: keep it on the lid beside the LED so a user can wake or pair the pod without opening the box; confirm before the drawing shows it.
2. **Two-tone enclosure.** Light grey lid on a dark grey base. A stock IP54 box is usually one colour. Recommendation: accept for the renders; buy a single-colour box and treat the two-tone scheme as a later option.
3. **Separate vibration puck.** The render brief asked for a vibration sensor puck. In this design the accelerometer sits on the boss of the aluminium block inside the hub, so there is no separate puck; the magnetic sensor base under the hub plays that role. Recommendation: keep the design as it is (MPL-DDR-001 D7); the renders show the sensor base, not a puck.
4. **Probe and USB leads share the probe-side gland**, as model.py already routes them; the model shows a two-hole seal insert. Recommendation: specify a multi-hole seal insert for that gland at TRL 4.
5. **Lid label and clamp marking** are illustrative artwork, not a specified label.

### Status

This is an appearance model only: no tolerances, no fabrication detail, and no change to model.py, the BOM, the calculations or the drawing. `trl` stays 3 and TRL 4 remains on hold.

## Session 2026-09-27: kit 1.5.0 and image quality

- Kit 1.5.0 synced: STANDARDS v1.5 (sections 12 to 15: product renders, storefront images and image quality, public release, authorship and signing), `.kit/cards.py`, `.kit/image_qc.py`, `.kit/release_gate.py`, issue templates, and the `/render-product` and `/release` commands. `CLAUDE.md` now matches `.kit/CLAUDE.md`.
- Every `media/render-*.png` recaptioned from its original render with the new layout: the title, concept label and repository sit in a band above the render and the view note in a band below it, each line wrapped to the image width, so no text overlaps other text or the render or runs off the image. `media/card.png` and `media/social-preview.png` regenerated with the same rules.
- `python .kit/image_qc.py` and `python .kit/release_gate.py` pass. trl stays 3.

## Session 2026-10-01: design for construction and prototype build plan (kit 1.7.0)

Amish approved the build plan format on 2026-09-30 and asked for it across all repos, with outstanding decisions kept in a separate register. This session installed kit 1.7.0, made the design constructable and wrote the illustrated build plan. No commit or push was made from this working copy.

### What was done

- Kit 1.7.0 installed (`.kit/`, `.claude/commands/`); `CLAUDE.md` now matches `.kit/CLAUDE.md`.
- `cad/src/model.py`: constructable model with 25 components and a `--check` mode; 102 constructability checks (26 contacts, 21 clearances, 55 overlap tests) all pass. STEP and STL re-exported.
- `docs/decisions/0003-design-for-construction.md` (MPL-DDR-003 v0.1, Draft): every change below, made under Amish's 2026-09-30 instruction to make the design physically buildable; open for his review.
- `docs/05-build-plan.md` (MPL-BLD-001 v0.1) with `cad/src/build_plan_media.py`: overview, six making sketches (MPL-DWG-101 to 106), a drilling layout, seven joint close-ups, thirteen step pictures and a wiring diagram.
- `docs/06-design-decisions.md` (MPL-DEC-001 v0.1): six open decisions, eight items to confirm when parts are bought, value engineering, and decisions made.
- MPL-DWG-001 Rev P4; MPL-CAL-001 v0.3, MPL-REQ-001 v0.5, MPL-PRC-001 v0.5; `bom/bom.csv` (14 lines) and `bom/bom-notes.md`; concept media regenerated; `project.yaml` (`design_state: constructable`, evidence); README links line and "Building the prototype" section.

### Design changes made for construction (MPL-DDR-003)

1. Sensor block made as a 10 mm plate; the boss is a separate piece of 20 mm round bar on an M6 x 12 set screw over magnet 1, so no lathe or mill is needed.
2. Magnet holes tapped M6 through; studs trimmed to 5 mm.
3. Nylon stand-offs moved to 33 x 13 mm each side of centre and held by M3 nylon screws into the block (they were 0.6 mm from the floor hole and overlapped the boot).
4. The floating boot replaced by a silicone grommet in the floor hole, gripping the boss.
5. The two floating boards replaced by one 45 x 56 mm carrier perfboard on four M3 x 5 mm stand-offs, with the controller in header sockets.
6. Three glands, one lead each (M16 for the CT, M12 for the probe and for power), centred 15.5 mm up so the nuts clear the floor and pillars; the power cable's far plug is cut off and wired to a 5 V terminal.
7. The box's moulded corner pillars modelled and every clearance checked against them.
8. The accelerometer bonded to the boss with rigid epoxy after the base is fitted (its board cannot pass the floor hole).
9. A made probe clip (aluminium block, groove, two high-temperature disc magnets) holds the sleeve on its pad against the frame; the concept's sleeve sat 7 mm above the frame. New BOM line 14.
10. A 3 mm light pipe takes the status LED through a sealed hole in the lid.

### Key results

- Pod 319 g (was 295 g); mount resonance 892 Hz curved, 1,783 Hz flat (was 927 and 1,853 Hz); slip margin 3.0 (2.8 at 80 °C); thermal results unchanged; 137 mm over the glands.
- Requirement status: 1 not met (R10), 3 at risk (R3, R4, R5), 9 met by calculation, 3 met by design. R16: value-engineering target USD 81; estimated cost of the constructable design USD 83.50 (USD 2.50 over the target). `budget_usd` unchanged.

### Proposed, awaiting Amish

See the design decisions register: acceptance of MPL-DDR-003 (decision 1), the power entry (2), the status button position (3), plus the earlier open items R4 treatment (4), co-design partner (5) and enclosure colour (6).

### Stale files to regenerate on Amish's Mac

The design changed visibly (glands, boss, boards, probe clip), so these still show the concept: `media/render-hero.png`, `media/render-exploded.png`, `media/render-detail.png` (not present in this working copy), `media/card.png`, `media/social-preview.png`, and the appearance model `cad/src/product_model.py`, which still models the boot, two boards and two glands.

### Safety concerns

Unchanged: mains at the current transformer (qualified person, isolation, voltage-output only), moving machinery, hot frames and strong magnets. The build plan adds safety stops S1 to S5 and the epoxy and threadlocker precautions. The adapter stays a certified 5 V unit; cutting its cable's far plug does not change the safety case.

### Recommended next step

Amish to review MPL-DDR-003 and the register's open decisions. TRL 4 remains on hold; the build plan is ready for a bench build when it is lifted.

## Session 2026-10-02: open decisions decided by Amish

Authority: Amish, 2026-10-02: "i approve your recommendations for all 555 open decisions." The recommendations approved are those written for the open decisions in the design decisions register. No model, BOM quantity or price, or picture was changed; where a decision needs one, it is listed below as a follow-up. `trl` and `trl_target` stay at 3. No commit or push.

### Decisions recorded

6, all moved to "Decisions made" in `docs/06-design-decisions.md`, dated 2026-10-02:

1. Design for construction (MPL-DDR-003) accepted: all ten changes.
2. Power entry: cut USB cable through an M12 gland to a screw terminal, for the prototype.
3. Status button: on the carrier board, pressed with the lid off; a sealed lid button only if field pairing shows it is needed.
4. R4 restated as a relative energy trend for the first build, with any kWh figure reported as an estimate; a voltage reference stays an option for sites that need absolute energy.
5. Co-design partner for alerts and dashboard: the makerspace pilot's shop lead, with the maintenance person of one small production machine shop as a second voice (first candidates to approach).
6. Enclosure colour: single-colour stock box; two-tone a later option.

### Documents changed

- `docs/06-design-decisions.md` (MPL-DEC-001 v0.2)
- `docs/decisions/0003-design-for-construction.md` (MPL-DDR-003 v0.2): accepted; A1 and A2 recorded; status stays Draft
- `docs/decisions/0001-trl2-review-decisions.md` (MPL-DDR-001 v0.3): O1 and O2 decided
- `docs/decisions/0002-recommendations-accepted.md` (MPL-DDR-002 v0.2): O1 and O2 decided
- `docs/02-concept.md` (MPL-PRC-001 v0.6): R4 as a relative trend; partner candidates
- `docs/03-requirements.md` (MPL-REQ-001 v0.6): R4 restated; met by design as restated; counts
- `docs/04-calcs/01-sizing.md` (MPL-CAL-001 v0.4): R4 row and summary count

### Follow-up actions to carry approved decisions into the design

1. Decision 4 (docs): State in the firmware and gateway sketch notes that energy is shown as a relative trend against the machine's baseline and any kWh figure is labelled an estimate.
2. Decision 6 (pictures): Show a single-colour stock box in the photoreal renders (`media/render-*.png`) and `cad/src/product_model.py` when they are next regenerated on Amish's Mac.

### Points found in the review

- A saving in Value engineering (reusing an existing USB charger at the site) conflicts with the decided certified 5 V adapter (D2) and R17; it should be removed.
- R10 is not met for many machines because the current transformer often has to go inside a terminal box opened by a qualified person, yet there is no open decision on how installs will be handled. A rule that a qualified electrician fits the CT would close it.
