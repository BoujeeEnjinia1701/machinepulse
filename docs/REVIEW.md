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

1. **Radio.** Options: Wi-Fi on ESP32-S3; LoRaWAN summaries only via the FieldNode radio core; both. Recommendation: Wi-Fi first, because spectra do not fit a LoRaWAN duty cycle and small shops usually have Wi-Fi.
2. **Power.** Options: certified 5 V USB adapter; Li-ion battery; energy harvesting from the CT. Recommendation: adapter, which avoids lithium cells on hot, vibrating frames.
3. **Accelerometer.** Options: IIS3DWB class (about $15, low noise, dc to 6 kHz); ADXL345 class (about $6, noisier, about 1.6 kHz). Recommendation: IIS3DWB class; keep ADXL345 as a documented fallback.
4. **Current sensing.** Options: one CT on one phase (within budget); three CTs (about $20 more, over budget); one CT plus a voltage reference. Recommendation: one CT, and accept that R4 is not met in the first build, or relax R4 to "relative energy trend".
5. **Alert logic.** Baseline learned over the first week per load band, flags at twice baseline vibration or a temperature rise above baseline, sent to a person. Recommendation: adopt for the first build; fixed ISO 20816 zones as a later option.
6. **Data home.** Options: TwinKit gateway; any MQTT broker; a cloud service. Recommendation: TwinKit gateway with any broker supported, no cloud dependency.
7. **Enclosure.** Options: stock IP54 ABS box; 3D-printed box; die-cast aluminium box (better for R12, about $10 more). Recommendation: stock ABS box for the first build, with a stand-off or insulating pad studied at TRL 3 for hot frames.
8. **Pilot site.** Options: a makerspace or university workshop; a small machine shop; a food or grain processing unit. Recommendation: a makerspace or university workshop with a lathe and a compressor.
9. **Budget.** No change proposed: the parts total of about $79 is within the $80 budget. A three-CT or die-cast variant would need a budget increase, which is Amish's decision.

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
