import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_ai_fix_local_stub_scenarios():
    result = subprocess.run(
        ["bash", "scripts/ai_fix.sh", "--scenario", "all"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.count("PASS:") == 2
    assert "1 passed" in result.stdout
