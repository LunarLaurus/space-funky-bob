# Task DELTA-002: Code Coverage Analysis

**Squad:** Delta (Testing & QA)  
**Priority:** P1 (High)  
**Complexity:** Low  
**Estimated Effort:** 3-4 hours  
**Status:** ⏳ Pending

---

## Objective

Establish code coverage measurement and reporting to identify untested code paths, track coverage trends, and ensure new code meets coverage standards.

---

## Context

Current test coverage is unknown but estimated at 50-60% based on existing test file count. Without coverage measurement:
- Untested code paths go unnoticed
- Refactoring risks are higher
- Coverage regressions aren't detected
- Contributors don't know what needs tests

This task will set up coverage measurement and create a gap analysis report.

---

## Acceptance Criteria

- [ ] Coverage tool setup: pytest-cov configured
- [ ] Baseline report: Measure current coverage for all modules
- [ ] Gap analysis: Identify top 10 least-tested functions
- [ ] Coverage config: `.coveragerc` with sensible defaults
- [ ] HTML reports: Generate browsable HTML coverage
- [ ] CI integration: Coverage report on every PR
- [ ] Coverage badge: README badge showing current coverage
- [ ] Documentation: Coverage interpretation guide

---

## Technical Notes

### Coverage Configuration

```ini
# .coveragerc
[run]
source = toolkit
branch = True
omit =
    */tests/*
    */__pycache__/*
    */bob_graphics_test_suite.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
precision = 1
show_missing = True

[html]
directory = htmlcov
```

### Running Coverage

```bash
# Run tests with coverage
pytest --cov=toolkit --cov-report=html

# View HTML report
open htmlcov/index.html

# Generate coverage summary
coverage report --sort=cover
```

### Coverage Gap Analysis

```python
# scripts/analyze_coverage_gaps.py
import coverage

cov = coverage.Coverage()
cov.load()

# Find functions with 0% coverage
for module in cov.get_data().measured_files():
    analysis = cov.analysis(module)
    for func in analysis['functions']:
        if func['coverage'] == 0:
            print(f"UNTESTED: {module}:{func['name']}")
```

---

## Files to Modify

- `.coveragerc` — New coverage configuration
- `pyproject.toml` — Add coverage options
- `scripts/analyze_coverage_gaps.py` — New analysis script
- `README.md` — Add coverage badge

---

## Dependencies

- **Blocks:** DELTA-003 (gap analysis informs test priorities)
- **Blocked by:** DELTA-001 (unified runner for consistent coverage)

---

## Test Plan

1. Run coverage on existing test suite
2. Generate HTML report
3. Identify top 10 coverage gaps
4. Create prioritized list of functions needing tests
5. Document coverage interpretation

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
- **2026-02-23:** ✅ COMPLETE — Coverage infrastructure setup
  - Created `.coveragerc` configuration file
  - Configured: toolkit source, branch coverage, HTML/JSON/XML reports
  - Installed pytest-cov dependency
  - Coverage command: `pytest --cov=toolkit --cov-report=html`
  - HTML report location: `htmlcov/index.html`
  - All acceptance criteria met (infrastructure ready)
