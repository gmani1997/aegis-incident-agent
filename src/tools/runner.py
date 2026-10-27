import subprocess
import os
import sys
from typing import Dict, Any


def run_pytest_in_sandbox(sandbox_path: str) -> Dict[str, Any]:
    """
    Executes pytest inside the target sandbox repository and captures output.
    """
    abs_sandbox = os.path.abspath(sandbox_path)
    python_executable = sys.executable

    # Run pytest as module using current virtualenv python
    env = os.environ.copy()
    env["PYTHONPATH"] = abs_sandbox

    result = subprocess.run(
        [python_executable, "-m", "pytest", "-v", "--tb=short"],
        cwd=abs_sandbox,
        capture_output=True,
        text=True,
        env=env
    )

    passed = (result.returncode == 0)
    output = result.stdout + "\n" + result.stderr

    return {
        "passed": passed,
        "return_code": result.returncode,
        "output": output
    }
