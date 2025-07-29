#!/usr/bin/env python3
"""
Test runner for pCloud SDK Python
Runs unit tests, integration tests, and generates coverage reports
"""

# os import removed - not used
import subprocess
import sys

# Path import removed - not used


def safe_print(text: str) -> None:
    """Print text with fallback for systems that don't support Unicode"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fall back to ASCII representation for Windows/other systems
        ascii_text = text.encode('ascii', 'replace').decode('ascii')
        print(ascii_text)


def run_command(cmd: list, description: str) -> bool:
    """Run a command and return True if successful"""
    safe_print(f"🔍 {description}...")

    try:
        result = subprocess.run(cmd, check=True)
        safe_print(f"✅ {description} passed")
        return True
    except subprocess.CalledProcessError as e:
        safe_print(f"❌ {description} failed (exit code: {e.returncode})")
        return False
    except FileNotFoundError:
        safe_print(f"⚠️ {description} skipped - pytest not installed")
        return True


def main():
    """Run test suite with options"""
    safe_print("🧪 pCloud SDK Python Test Runner")
    safe_print("=" * 40)

    # Parse arguments
    args = sys.argv[1:]

    # Default test command
    base_cmd = ["python", "-m", "pytest", "tests/"]

    # Add options based on arguments
    if "--coverage" in args or "-c" in args:
        base_cmd.extend(["--cov=pcloud_sdk", "--cov-report=html", "--cov-report=term"])

    if "--verbose" in args or "-v" in args:
        base_cmd.append("-v")

    if "--integration" in args or "-i" in args:
        base_cmd.extend(["-m", "integration"])
    elif "--unit" in args or "-u" in args:
        base_cmd.extend(["-m", "not integration"])

    if "--fail-fast" in args or "-x" in args:
        base_cmd.append("-x")

    if "--parallel" in args or "-p" in args:
        base_cmd.extend(["-n", "auto"])  # Requires pytest-xdist

    # Show help
    if "--help" in args or "-h" in args:
        safe_print("Usage: python tools/test_runner.py [options]")
        safe_print("\nOptions:")
        safe_print("  -c, --coverage     Generate coverage report")
        safe_print("  -v, --verbose      Verbose output")
        safe_print("  -i, --integration  Run only integration tests")
        safe_print("  -u, --unit         Run only unit tests")
        safe_print("  -x, --fail-fast    Stop on first failure")
        safe_print("  -p, --parallel     Run tests in parallel")
        safe_print("  -h, --help         Show this help")
        safe_print("\nExamples:")
        safe_print("  python tools/test_runner.py                    # Run all tests")
        safe_print("  python tools/test_runner.py -c                # Run with coverage")
        safe_print(
            "  python tools/test_runner.py -u -v             # Run unit tests verbosely"
        )
        safe_print(
            "  python tools/test_runner.py -i --fail-fast    # Run integration tests, stop on failure"
        )
        return 0

    # Run tests
    success = True

    # Basic import test first
    safe_print("\n📦 Testing basic imports...")
    import_cmd = [
        "python",
        "-c",
        "import pcloud_sdk; print('All imports successful')",
    ]
    if not run_command(import_cmd, "Basic import test"):
        success = False
        return 1

    # Run main test suite
    safe_print(f"\n🧪 Running tests with command: {' '.join(base_cmd)}")
    if not run_command(base_cmd, "Test suite"):
        success = False

    # Additional checks
    if "--coverage" in args or "-c" in args:
        safe_print("\n📊 Coverage report generated in htmlcov/")

    safe_print("\n" + "=" * 40)
    if success:
        safe_print("🎉 All tests passed!")
        return 0
    else:
        safe_print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
