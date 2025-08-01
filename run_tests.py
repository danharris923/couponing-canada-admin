#!/usr/bin/env python3
"""
Test runner script for Modern Template Content Scraper.

This script provides convenient commands for running different types of tests:
- Unit tests
- Integration tests  
- All tests
- Coverage reports
- Specific test files or functions

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit            # Run only unit tests
    python run_tests.py --integration     # Run only integration tests
    python run_tests.py --coverage        # Run with coverage report
    python run_tests.py --file test_name  # Run specific test file
    python run_tests.py --fast            # Skip slow tests
    python run_tests.py --no-ai           # Skip tests requiring AI
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and return the result."""
    if description:
        print(f"\n{'='*60}")
        print(f"[RUN] {description}")
        print(f"{'='*60}")
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description="Test runner for Modern Template Content Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Test selection options
    parser.add_argument(
        "--unit", 
        action="store_true",
        help="Run only unit tests"
    )
    parser.add_argument(
        "--integration",
        action="store_true", 
        help="Run only integration tests"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Run specific test file (e.g., test_validator)"
    )
    parser.add_argument(
        "--function",
        type=str,
        help="Run specific test function (e.g., test_config_validation)"
    )
    
    # Test execution options
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip slow tests (excludes network and AI tests)"
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Skip tests that require AI/LLM API access"
    )
    parser.add_argument(
        "--no-network",
        action="store_true",
        help="Skip tests that require network access"
    )
    
    # Coverage and reporting
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--html-coverage",
        action="store_true",
        help="Generate HTML coverage report"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    # Other options
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install test dependencies before running"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean test artifacts before running"
    )
    
    args = parser.parse_args()
    
    # Set up environment
    os.environ["PYTHONPATH"] = str(Path.cwd())
    os.environ["TEST_MODE"] = "true"
    
    # Install dependencies if requested
    if args.install_deps:
        print("[INSTALL] Installing test dependencies...")
        if not run_command([sys.executable, "-m", "pip", "install", "-r", "scraper/requirements.txt"]):
            print("[ERROR] Failed to install dependencies")
            return 1
        if not run_command([sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio", "pytest-cov", "pytest-mock"]):
            print("[ERROR] Failed to install test dependencies")
            return 1
    
    # Clean artifacts if requested
    if args.clean:
        print("[CLEAN] Cleaning test artifacts...")
        import shutil
        for path in [".pytest_cache", "htmlcov", ".coverage", "__pycache__"]:
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
    
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Test selection
    if args.unit:
        cmd.extend(["-m", "unit"])
        description = "Running unit tests"
    elif args.integration:
        cmd.extend(["-m", "integration"])
        description = "Running integration tests"
    elif args.file:
        test_file = args.file
        if not test_file.startswith("test_"):
            test_file = f"test_{test_file}"
        if not test_file.endswith(".py"):
            test_file = f"{test_file}.py"
        cmd.extend([f"tests/**/{test_file}"])
        description = f"Running tests from {test_file}"
    elif args.function:
        cmd.extend(["-k", args.function])
        description = f"Running test function: {args.function}"
    else:
        description = "Running all tests"
    
    # Test execution options
    markers = []
    if args.fast:
        markers.append("not slow")
    if args.no_ai:
        markers.append("not ai_required")
    if args.no_network:
        markers.append("not network")
    
    if markers:
        cmd.extend(["-m", " and ".join(markers)])
    
    # Coverage options
    if args.coverage or args.html_coverage:
        cmd.extend([
            "--cov=scraper",
            "--cov-report=term-missing"
        ])
        if args.html_coverage:
            cmd.extend(["--cov-report=html"])
    
    # Verbose output
    if args.verbose:
        cmd.append("-v")
    
    # Add common options
    cmd.extend([
        "--tb=short",
        "--color=yes"
    ])
    
    # Run tests
    success = run_command(cmd, description)
    
    if success:
        print("\n[SUCCESS] All tests passed!")
        
        if args.coverage or args.html_coverage:
            print("\n[REPORT] Coverage report generated")
            if args.html_coverage:
                print("   HTML report: htmlcov/index.html")
    else:
        print("\n[ERROR] Some tests failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())