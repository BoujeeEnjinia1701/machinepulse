# BOM notes

- Line numbers 1 to 9 and 12 to 14 match the numbered callouts in `media/exploded.png` and the parts in `cad/src/model.py`. Lines 10 and 11 are not shown in the model. Line 12 is shown by the grommet, the set screw, the nylon screws and the carrier stand-offs and screws.
- Every line is priced. Prices are indicative single-unit prices in USD from typical online and distributor listings in September 2026. They are estimates, not quotes.
- Value-engineering target: USD 81 (`budget_usd` in `project.yaml`, a hypothetical control target, not a limit). Estimated cost of the constructable design: USD 83.50 (USD 2.50 over the target) (MPL-CAL-001 v0.3, section J). Making the design constructable (MPL-DDR-003) added $2.50: lines 2 (+$0.50, third gland and an M16 gland), 7 (+$1.00, sockets, terminals and light pipe), 9 and 14 (+$0.50 net, a made clip in place of a bought one) and 12 (+$0.50, grommet, set screw and carrier fixings).
- Not included: the TwinKit gateway or any other MQTT broker (a separate lab project, costed there); extra CTs for the other two phases (about $10 each, total $103.50); and a voltage reference (about $10, total $93.50).
- Line 3: choose a module without octal PSRAM. Common boards with octal PSRAM use modules rated to 65 °C, which leaves little margin on hot frames (MPL-CAL-001, G4).
- Line 4 (IIS3DWB-class accelerometer) is the least certain price and availability. An ADXL345-class breakout (about $6) is cheaper but misses R6 (0.20 mm/s against 0.1 mm/s).
- Line 8: order the CT range per machine (5 to 60 A, voltage output) so that normal load sits above about 30 % of its range. Never use a current-output type.
- Line 10 must be a certified adapter carrying the local safety mark. Do not substitute an unmarked adapter.
- Line 11: pads are costed for every pod, although only aluminium-frame machines need them; they are 3 mm thick so that the magnets keep about 75 % of their pull.
- Line 2: the M16 gland for the CT lead is chosen so the CT's 3.5 mm plug passes through its seal; check this on the parts bought. The probe and power leads each have their own M12 gland, because a single-hole seal does not seal two cables.
- Line 10: the far plug of the USB cable is cut off and the two power wires go through the power gland to the carrier board's 5 V terminal; the adapter itself stays a certified unit.
- Line 14: the probe clip is made from an aluminium offcut; its magnets must be a high-temperature grade (150 °C or more) because the clip sits on the frame.
