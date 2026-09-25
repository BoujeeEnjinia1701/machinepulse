# BOM notes

- Line numbers 1 to 9 match the numbered callouts in `media/exploded.png`. Lines 10 to 12 are not shown in the massing model.
- Prices are indicative single-unit prices in USD from typical online and distributor listings in September 2026. They are estimates, not quotes, and will be checked at TRL 3.
- Parts total: about $79, against the $80 prototype budget. The margin is thin.
- Not included: the TwinKit gateway or any other MQTT broker (a separate lab project), and extra current transformers for the other two phases (about $10 each, which would take the total over budget; see docs/REVIEW.md).
- Line 4 (IIS3DWB-class accelerometer) is the least certain price and availability. An ADXL345-class breakout (about $6) is a cheaper fallback with a higher noise floor and a lower bandwidth.
- Line 10 must be a certified adapter carrying the local safety mark. Do not substitute an unmarked adapter.
