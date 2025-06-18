#!/usr/bin/env python3
"""
ManzAI Studio Test Runner

This script provides a convenient way to run tests for the ManzAI Studio application.
It allows running all tests or specific test categories with various options.

Usage:
    python run_tests.py [options]

Options:
    --unit           Run unit tests only
    --integration    Run integration tests only
    --services       Run service tests only
    --api            Run API tests only
    --all            Run all tests (default)
    --verbose        Enable verbose output
    --coverage       Generate coverage report
    --xml           Generate XML report for CI systems
    --module=MODULE  Run tests from a specific module
    --help          Show this help message
"""

import argparse
import subprocess
import sys


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="ManzAI Studio Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--services", action="store_true", help="Run service tests only")
    parser.add_argument("--api", action="store_true", help="Run API tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--xml", action="store_true", help="Generate XML report for CI systems")
    parser.add_argument("--module", help="Run tests from a specific module")
    return parser.parse_args()


def run_tests(args):
    """Run tests based on provided arguments."""
    # Base pytest command
    cmd = ["python", "-m", "pytest"]

    # Add verbosity if requested
    if args.verbose:
        cmd.append("-v")

    # Add coverage if requested
    if args.coverage:
        cmd.extend(["--cov=src", "--cov-report=term-missing"])

    # Add XML report if requested
    if args.xml:
        cmd.append("--junitxml=test-results.xml")

    # Determine which tests to run
    if args.module:
        # Run specific module
        cmd.append(f"tests/test_{args.module}.py")
    elif args.unit:
        # Run unit tests (exclude integration tests)
        cmd.append("tests/test_*.py")
        cmd.append("--ignore=tests/test_integration.py")
    elif args.integration:
        # Run only integration tests
        cmd.append("tests/test_integration.py")
    elif args.services:
        # Run service tests
        cmd.append("tests/test_ollama_service.py")
        cmd.append("tests/test_voicevox_service.py")
        cmd.append("tests/test_audio_manager.py")
    elif args.api:
        # Run API tests
        cmd.append("tests/test_api_endpoints.py")
    else:
        # Run all tests
        cmd.append("tests/")

    # Run the tests
    print(f"Running command: {' '.join(cmd)}")
    return subprocess.run(cmd)


def main():
    """Main entry point."""
    # Parse arguments
    args = parse_args()

    # If no test category specified, run all tests
    if not any([args.unit, args.integration, args.services, args.api, args.module]):
        args.all = True

    # Run tests
    result = run_tests(args)

    # Return exit code from pytest
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
