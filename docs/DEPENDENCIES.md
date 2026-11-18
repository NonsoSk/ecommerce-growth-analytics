# Python and dependencies

Current dependency scope: standard-library core analysis, optional isolated Tableau Hyper tooling, and Google Cloud CLI only for separately authorized cloud operations. Initial interpreter inspection below is historical (November 12).

Detected interpreters: `/usr/local/bin/python3` is Python 3.14.8; `/usr/bin/python3` is Apple's Python 3.9.6. The project uses a standard Python 3.14.8 virtual environment; the system interpreter is unchanged. No version change is required.

The bootstrap and synthetic milestone use only Python's standard library, including `json`, `pathlib`, `sqlite3`, `sys`, `random`, `datetime`, `collections`, `hashlib`, `argparse`, `tempfile`, `copy` and `unittest`. Compatibility is checked by executing generation and tests inside the existing Python 3.14 environment. There are no third-party core-analysis dependencies; pip is environment tooling. Optional Tableau generation dependencies are pinned separately.

Before adding pandas, NumPy, notebook tooling, a test framework or a cloud SDK:

1. Identify the feature that requires it and inspect its current official Python support and dependency metadata.
2. Use `.venv/bin/python -m pip install --dry-run --only-binary=:all: PACKAGE` to check resolution and available wheels on this interpreter and machine. Replace `PACKAGE` with the reviewed package/version.
3. Install reviewed versions, run `pip check`, and verify imports and the actual feature; record reproducible dependency versions at that point.
4. If a required package lacks Python 3.14 support, explain the constraint before proposing a supported interpreter and rebuilding the environment. Do not silently fall back to Apple's Python.

Package compatibility has not been claimed for future integrations. Those dependencies will be selected when their milestones begin.

Milestone 2 uses standard-library `sqlite3`, `csv` and `unittest` for local analysis. Verified Python 3.14.8 includes SQLite 3.50.4, which supports the chosen STRICT tables and window functions. No packages or interpreter changes were needed. A future environment requires SQLite 3.37+ for this schema, independently of its Python version.

## Optional Tableau build

The verified macOS ARM64/Python 3.14.8 environment uses tableauhyperapi 0.0.26479, cffi 2.1.1 and pycparser 3.12 as specified in [the pinned requirements](../dashboard/requirements-hyper.txt). Use the actual pins in that file; the [dashboard guide](../dashboard/README.md) gives installation and build commands in a separate virtual environment. Viewing the included TWBX does not require Python or Hyper installation.

Google Cloud CLI provides `gcloud`/`bq` for the implemented migration workflow; no Python cloud SDK is required. Local reproduction does not need authentication or cloud access. Historical version/execution evidence is preserved in the migration and build records.
