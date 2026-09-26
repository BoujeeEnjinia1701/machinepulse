# BOM notes

- Line numbers 1 to 9, 12 and 13 match the numbered callouts in `media/exploded.png` and the parts in `cad/src/model.py`. Lines 10 and 11 are not shown in the model. Line 12 is shown only by the silicone boot round the boss.
- Every line is priced. Prices are indicative single-unit prices in USD from typical online and distributor listings in September 2026. They are estimates, not quotes.
- Parts total: $80.00 against the $80 `budget_usd` in `project.yaml`, a margin of $0.00 (MPL-CAL-001, section J). The nylon stand-offs (line 13, $1.00) added at TRL 3 used the last dollar.
- Not included: the TwinKit gateway or any other MQTT broker (a separate lab project, costed there); extra CTs for the other two phases (about $10 each, total $100.00); a voltage reference (about $10, total $90.00); and high-temperature magnets for frames above about 80 °C (about $1.00 more for the pair, total $81.00, proposed and awaiting Amish in `docs/REVIEW.md`).
- Line 3: choose a module without octal PSRAM. Common boards with octal PSRAM use modules rated to 65 °C, which leaves little margin on hot frames (MPL-CAL-001, G4).
- Line 4 (IIS3DWB-class accelerometer) is the least certain price and availability. An ADXL345-class breakout (about $6) is cheaper but misses R6 (0.20 mm/s against 0.1 mm/s).
- Line 8: order the CT range per machine (5 to 60 A, voltage output) so that normal load sits above about 30 % of its range. Never use a current-output type.
- Line 10 must be a certified adapter carrying the local safety mark. Do not substitute an unmarked adapter.
- Line 11: pads are costed for every pod, although only aluminium-frame machines need them; they are 3 mm thick so that the magnets keep about 75 % of their pull.
