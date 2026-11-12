"""Verify the local Python foundation without network access or private data."""

import json
from pathlib import Path
import sqlite3
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    expected_env = root / ".venv"
    checks = {
        "virtual_environment_active": sys.prefix != sys.base_prefix,
        "project_environment_selected": Path(sys.prefix).resolve() == expected_env.resolve(),
        "python_3_14": sys.version_info[:2] == (3, 14),
        "required_folders_present": all(
            (root / folder).is_dir()
            for folder in ("src", "sql", "notebooks", "tests", "docs", "reports", "data/sample")
        ),
    }
    with sqlite3.connect(":memory:") as connection:
        checks["standard_library_sql_available"] = (
            connection.execute("SELECT 1 + 1").fetchone()[0] == 2
        )
    print(json.dumps({
        "python_version": sys.version.split()[0],
        "executable": sys.executable,
        "checks": checks,
        "result": "PASS" if all(checks.values()) else "FAIL",
    }, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
