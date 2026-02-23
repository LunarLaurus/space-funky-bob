"""B.O.B. ROM Analysis Toolkit — Unified Test Runner

Usage:
    python -m tests                  # Run all tests
    python -m tests --verbose        # Verbose output
    python -m tests --filter lz77    # Run only LZ77 tests
    python -m tests --format json    # JSON output
"""

import argparse
import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime


def run_pytest_tests(filter_pattern=None, verbose=False):
    """Run pytest-based tests."""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"]
    
    if filter_pattern:
        cmd.extend(["-k", filter_pattern])
    
    if not verbose:
        cmd.extend(["-q"])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        return {
            'suite': 'pytest',
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            'suite': 'pytest',
            'returncode': 1,
            'stdout': '',
            'stderr': f'Test timeout (180s)'
        }
    except Exception as e:
        return {
            'suite': 'pytest',
            'returncode': 1,
            'stdout': '',
            'stderr': str(e)
        }


def run_simple_tests(verbose=False):
    """Run simple test runner (run_tests.py)."""
    cmd = [sys.executable, "run_tests.py"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return {
            'suite': 'simple',
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except Exception as e:
        return {
            'suite': 'simple',
            'returncode': 1,
            'stdout': '',
            'stderr': str(e)
        }


def run_property_tests(verbose=False):
    """Run property-based tests."""
    cmd = [sys.executable, "property_tests.py"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return {
            'suite': 'property',
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except Exception as e:
        return {
            'suite': 'property',
            'returncode': 1,
            'stdout': '',
            'stderr': str(e)
        }


def run_full_suite(verbose=False):
    """Run full test suite."""
    cmd = [sys.executable, "run_full_test_suite.py"]
    if verbose:
        cmd.append("--verbose")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return {
            'suite': 'full',
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except Exception as e:
        return {
            'suite': 'full',
            'returncode': 1,
            'stdout': '',
            'stderr': str(e)
        }


def format_text_results(results, verbose=False):
    """Format results as text."""
    lines = []
    lines.append("=" * 60)
    lines.append("B.O.B. ROM TOOLKIT — TEST RESULTS")
    lines.append("=" * 60)
    lines.append("")
    
    total_passed = 0
    total_failed = 0
    
    for suite_name, result in results.items():
        status = "PASS" if result['returncode'] == 0 else "FAIL"
        lines.append(f"[{status}] {suite_name}")
        
        if verbose and result['stdout']:
            for line in result['stdout'].split('\n')[-10:]:
                if line.strip():
                    lines.append(f"    {line}")
        
        if result['returncode'] == 0:
            total_passed += 1
        else:
            total_failed += 1
    
    lines.append("")
    lines.append("-" * 60)
    lines.append(f"Summary: {total_passed} passed, {total_failed} failed")
    lines.append("=" * 60)
    
    return '\n'.join(lines)


def format_json_results(results):
    """Format results as JSON."""
    summary = {
        'timestamp': datetime.now().isoformat(),
        'suites': {},
        'total_passed': 0,
        'total_failed': 0
    }
    
    for suite_name, result in results.items():
        passed = result['returncode'] == 0
        summary['suites'][suite_name] = {
            'passed': passed,
            'returncode': result['returncode']
        }
        if passed:
            summary['total_passed'] += 1
        else:
            summary['total_failed'] += 1
    
    return json.dumps(summary, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='B.O.B. ROM Toolkit — Unified Test Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m tests                     Run all tests
  python -m tests -v                  Verbose output
  python -m tests --filter lz77       Run only LZ77 tests
  python -m tests --format json       JSON output
  python -m tests --suite pytest      Run only pytest suite
        """
    )
    
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Quiet mode (minimal output)')
    parser.add_argument('--filter', '-f', type=str,
                        help='Filter tests by name pattern')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                        help='Output format (default: text)')
    parser.add_argument('--suite', '-s', choices=['pytest', 'simple', 'property', 'full', 'all'],
                        default='all', help='Test suite to run (default: all)')
    
    args = parser.parse_args()
    
    # Run selected test suites
    results = {}
    
    if args.suite in ['pytest', 'all']:
        if not args.quiet:
            print(f"Running pytest tests...")
        results['pytest'] = run_pytest_tests(args.filter, args.verbose)
    
    if args.suite in ['simple', 'all']:
        if not args.quiet:
            print(f"Running simple tests...")
        results['simple'] = run_simple_tests(args.verbose)
    
    if args.suite in ['property', 'all']:
        if not args.quiet:
            print(f"Running property tests...")
        results['property'] = run_property_tests(args.verbose)
    
    if args.suite == 'full':
        if not args.quiet:
            print(f"Running full test suite...")
        results['full'] = run_full_suite(args.verbose)
    
    # Output results
    if args.format == 'json':
        print(format_json_results(results))
    else:
        print(format_text_results(results, args.verbose))
    
    # Exit with appropriate code
    all_passed = all(r['returncode'] == 0 for r in results.values())
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
