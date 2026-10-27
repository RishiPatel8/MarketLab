"""
MarketLab AI — Master Test Runner
Runs backend unit & integration tests, AI evaluation test suite, and frontend build verification.
"""

import subprocess
import sys
import os

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def run_backend_tests():
    print("=" * 60)
    print("1. Running Backend Unit, Integration & AI Evaluation Tests...")
    print("=" * 60)
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "-W", "ignore::pydantic.warnings.PydanticDeprecatedSince20"]
    ret = subprocess.call(cmd, cwd=backend_dir)
    if ret != 0:
        print("\n[FAIL] Backend tests failed!")
        return False
    print("\n[OK] Backend tests passed successfully!")
    return True

def run_frontend_build():
    print("=" * 60)
    print("2. Verifying Frontend TypeScript Compilation and Production Bundle...")
    print("=" * 60)
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
    cmd = ["npm.cmd" if os.name == "nt" else "npm", "run", "build"]
    ret = subprocess.call(cmd, cwd=frontend_dir)
    if ret != 0:
        print("\n[FAIL] Frontend build failed!")
        return False
    print("\n[OK] Frontend build passed successfully!")
    return True

def main():
    backend_ok = run_backend_tests()
    frontend_ok = run_frontend_build()

    print("\n" + "=" * 60)
    if backend_ok and frontend_ok:
        print("[SUCCESS] ALL TEST SUITES PASSED! MarketLab AI IS 100% OPERATIONAL.")
        sys.exit(0)
    else:
        print("[FAIL] Test failures detected.")
        sys.exit(1)

if __name__ == "__main__":
    main()
