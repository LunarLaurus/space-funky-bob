#!/usr/bin/env python3
"""
Test runner for Space Funky B.O.B. Level Editor tests.

Runs all test suites and reports results.
"""

import os
import sys
import unittest


def run_tests():
    """Run all tests and report results."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.join(base_dir, "tests")

    sys.path.insert(0, os.path.join(base_dir, "editor", "lib"))
    sys.path.insert(0, tests_dir)

    loader = unittest.TestLoader()
    suite = loader.discover(tests_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print(f"SUCCESS: {result.testsRun} tests passed")
        print("=" * 60)
        return 0
    else:
        failures = len(result.failures)
        errors = len(result.errors)
        print(
            f"FAILURE: {failures} failures, {errors} errors out of {result.testsRun} tests"
        )
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
