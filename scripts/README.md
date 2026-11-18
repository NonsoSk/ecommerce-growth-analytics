# Script entry points

Run commands from the repository root using `.venv/bin/python`. See [the main README](../README.md) and [dashboard build guide](../dashboard/README.md) for prerequisites.

| Script | Purpose / expected result |
|---|---|
| `run_analysis.py` | Complete local tests and analysis; ignored baseline/SQLite/CSV/report outputs |
| `generate_sample.py` | Deterministic baseline only; defaults to seed 42 and 90 days |
| `verify_environment.py` | Interpreter, directory and SQLite smoke checks |
| `prepare_dashboard.py` | Three separate baseline dashboard datasets and filter expectations |
| `build_dashboard_release.py --hyper-python PATH` | Orchestrates the optional extract-backed build into a separate REBUILD package |
| `bigquery_migrate.py prepare` | Offline preparation only; other subcommands can access cloud resources and require separate authorization |

The dashboard orchestrator calls `prepare_tableau_extracts.py`, `build_tableau_dashboard.py`, `finalize_tableau_review.py`, `validate_tableau_workbook.py`, `package_tableau_dashboard.py` and `validate_portable_tableau.py`. Use the orchestrator for reproducibility rather than guessing the sequence. Hyper-backed steps use the separately supplied interpreter. A successful build validates data/expressions; it does not claim a fresh Tableau GUI acceptance.

The ignored local `test_tableau_xml.py` is a **historical diagnostic probe**, preserved locally to explain the original repair; it is not included in a clean checkout. It is not the unittest suite or a clean-checkout entry point and may reference ignored local draft/probe files. See [the dated probe record](../dashboard/XML_PROBE_STATUS.md). The supported release build does not depend on that script or those ignored files.
