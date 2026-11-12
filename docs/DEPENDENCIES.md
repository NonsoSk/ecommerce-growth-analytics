# Python and dependencies

Status: initial setup, verified locally on 2026-11-12.

Detected interpreters: `/usr/local/bin/python3` is Python 3.14.8; `/usr/bin/python3` is Apple's Python 3.9.6. The project uses a standard Python 3.14.8 virtual environment; the system interpreter is unchanged. No version change is required.

The bootstrap and synthetic milestone use only Python's standard library, including `json`, `pathlib`, `sqlite3`, `sys`, `random`, `datetime`, `collections`, `hashlib`, `argparse`, `tempfile`, `copy` and `unittest`. Compatibility is checked by executing generation and tests inside the existing Python 3.14 environment. There are no third-party runtime dependencies or lock file yet; pip is environment tooling, not an analysis dependency.

Before adding pandas, NumPy, notebook tooling, a test framework or a cloud SDK:

1. Identify the feature that requires it and inspect its current official Python support and dependency metadata.
2. Use `.venv/bin/python -m pip install --dry-run --only-binary=:all: PACKAGE` to check resolution and available wheels on this interpreter and machine. Replace `PACKAGE` with the reviewed package/version.
3. Install reviewed versions, run `pip check`, and verify imports and the actual feature; record reproducible dependency versions at that point.
4. If a required package lacks Python 3.14 support, explain the constraint before proposing a supported interpreter and rebuilding the environment. Do not silently fall back to Apple's Python.

Package compatibility has not been claimed for future integrations. Those dependencies will be selected when their milestones begin.
