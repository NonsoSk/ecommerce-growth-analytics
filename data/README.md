# Data handling

- `generated/baseline/`: ignored bulk synthetic tables and manifest, produced by `.venv/bin/python scripts/generate_sample.py`. Never commit these generated files.
- `sample/`: only manually reviewed, small, explicitly labeled synthetic illustrations.
- `private/`: ignored location for future approved private inputs; currently no private data. Git does not preserve empty folders.

No real retailer or customer data is included. Credentials belong outside data folders. Do not move private or bulk files into `sample/` to bypass ignore rules. Separate intentionally invalid fixtures live in `tests/fixtures/` and are not part of the baseline.
