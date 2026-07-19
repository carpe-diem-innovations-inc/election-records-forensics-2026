"""The prose cannot drift from the data: shell scripts/claims_lint.py.

Kept as a subprocess call (not an import) so the lint stays runnable on its
own and verify.yml needs no change — CI already runs pytest.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_claims_lint_passes():
    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "claims_lint.py")],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode == 0, (
        f"claims-lint reported drift between prose and data:\n"
        f"{result.stdout}\n{result.stderr}"
    )
