# Task DELTA-001: Test Runner Consolidation

**Squad:** Delta (Testing & QA)  
**Priority:** P0 (Critical)  
**Complexity:** Medium  
**Estimated Effort:** 4-6 hours  
**Status:** ⏳ Pending

---

## Objective

Consolidate the multiple test runners (`run_tests.py`, `run_full_test_suite.py`, `property_tests.py`) into a single unified test runner with consistent output, configuration options, and reporting.

---

## Context

The project currently has three separate test runners:
1. `run_tests.py` — Simple runner, no pytest dependency
2. `run_full_test_suite.py` — Comprehensive suite with subprocess tests
3. `property_tests.py` — Property-based tests (standalone)

This fragmentation causes:
- Confusion about which runner to use
- Duplicate test execution
- Inconsistent output formats
- Maintenance overhead

A unified runner would provide:
- Single entry point for all tests
- Configurable verbosity and filtering
- Consistent output formatting
- Multiple output formats (text, JSON, HTML)

---

## Acceptance Criteria

- [ ] Single runner: `python -m tests` runs all tests
- [ ] Backward compatibility: Old runners still work (with deprecation warning)
- [ ] Configuration: `--verbose`, `--quiet`, `--filter` options
- [ ] Output formats: Text (default), JSON (`--json`), HTML (`--html`)
- [ ] Filtering: Run specific tests by name pattern (`--filter pattern`)
- [ ] Exit codes: Proper exit codes for CI integration
- [ ] Documentation: Updated testing guide

---

## Technical Notes

### Unified Runner Design

```python
# tests/__main__.py
import argparse
import sys
from .runners import pytest_runner, simple_runner, property_runner

def main():
    parser = argparse.ArgumentParser(description='B.O.B. Toolkit Test Runner')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--quiet', '-q', action='store_true')
    parser.add_argument('--filter', '-f', type=str, help='Test name pattern')
    parser.add_argument('--format', choices=['text', 'json', 'html'], default='text')
    parser.add_argument('--coverage', action='store_true', help='Run with coverage')
    
    args = parser.parse_args()
    
    # Run all test suites
    results = {
        'unit': pytest_runner.run(args),
        'integration': simple_runner.run(args),
        'property': property_runner.run(args)
    }
    
    # Report results
    report(results, args.format)
    
    # Exit with appropriate code
    sys.exit(0 if all_passed(results) else 1)
```

### Output Format Examples

**Text (default):**
```
============================================
B.O.B. Toolkit Test Suite
============================================
Unit Tests (pytest).......... [PASS] 45/47
Integration Tests............ [PASS] 12/12
Property Tests............... [PASS] 8/8
============================================
Total: 65 passed, 0 failed
============================================
```

**JSON:**
```json
{
  "summary": {"passed": 65, "failed": 0, "total": 65},
  "suites": {
    "unit": {"passed": 45, "failed": 2},
    "integration": {"passed": 12, "failed": 0},
    "property": {"passed": 8, "failed": 0}
  }
}
```

---

## Files to Modify

- `tests/__main__.py` — New unified runner
- `tests/runners.py` — New runner modules
- `run_tests.py` — Add deprecation warning
- `run_full_test_suite.py` — Add deprecation warning

---

## Dependencies

- **Blocks:** DELTA-005 (CI/CD uses unified runner)
- **Blocked by:** None

---

## Test Plan

1. Run unified runner against all existing tests
2. Verify output matches expected formats
3. Test filtering with various patterns
4. Verify exit codes for CI integration
5. Test backward compatibility of old runners

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
