#!/usr/bin/env python3
"""
Test runner script for AdGenius backend.
Makes it easy to run tests with various options.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --cov              # Run tests with coverage report
    python run_tests.py --parallel         # Run tests in parallel
    python run_tests.py --watch            # Run tests in watch mode (rerun on file changes)

You can combine options:
    python run_tests.py --unit --cov       # Run unit tests with coverage
"""

import argparse
import subprocess
import sys


def run_tests():
    """Parse arguments and run tests with appropriate options."""
    parser = argparse.ArgumentParser(
        description="Run backend tests with various options"
    )
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument(
        "--integration", action="store_true", help="Run only integration tests"
    )
    parser.add_argument("--api", action="store_true", help="Run only API tests")
    parser.add_argument("--cov", action="store_true", help="Generate coverage report")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument(
        "--watch", action="store_true", help="Watch for file changes and re-run tests"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("paths", nargs="*", help="Specific test paths to run")

    args = parser.parse_args()

    # Construct the pytest command
    cmd = ["python", "-m", "pytest"]

    # Add verbosity
    if args.verbose:
        cmd.append("-v")

    # Add markers
    markers = []
    if args.unit:
        markers.append("unit")
    if args.integration:
        markers.append("integration")
    if args.api:
        markers.append("api")

    if markers:
        cmd.append("-m")
        cmd.append(" or ".join(markers))

    # Add coverage options
    if args.cov:
        cmd.append("--cov")
        cmd.append("--cov-report=term")
        cmd.append("--cov-report=html")

    # Add parallel execution
    if args.parallel:
        # Automatically use number of available CPUs
        cmd.append("-xvs")

    # Add watch mode
    if args.watch:
        try:
            # Check if pytest-watch is installed
            subprocess.run(
                ["pip", "show", "pytest-watch"], check=True, capture_output=True
            )
            # Replace pytest command with ptw
            cmd = ["ptw", "--"] + cmd[2:]
        except subprocess.CalledProcessError:
            print("pytest-watch not found. Installing...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pytest-watch"], check=True
            )
            # Replace pytest command with ptw
            cmd = ["ptw", "--"] + cmd[2:]

    # Add specific test paths
    if args.paths:
        cmd.extend(args.paths)

    # Print the command being run
    cmd_str = " ".join(cmd)
    print(f"Running: {cmd_str}")

    # Run the command
    process = subprocess.run(cmd)
    return process.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
