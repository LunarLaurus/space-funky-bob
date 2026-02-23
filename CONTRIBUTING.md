# Contributing to B.O.B. ROM Analysis Toolkit

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Table of Contents

- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

---

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- (Optional) pytest for running tests

### Installation

```bash
# Clone the repository
git clone https://github.com/LunarLaurus/space-funky-bob.git
cd space-funky-bob

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install development dependencies
pip install pytest pytest-cov black flake8
```

### Project Structure

```
space-funky-bob/
├── toolkit/           # Core Python modules
├── tests/             # Test files
├── docs/              # Documentation
├── benchmarks/        # Performance benchmarks
├── configs/           # Configuration files
└── .planning/         # Development planning
```

---

## Code Style

### Python Style Guide

We follow PEP 8 with these conventions:

- **Line length:** 100 characters maximum
- **Indentation:** 4 spaces (no tabs)
- **Imports:** Standard library first, then third-party, then local
- **Naming:** 
  - Functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_CASE`

### Formatting Tools

Use these tools to maintain code quality:

```bash
# Format code with Black
black toolkit/ tests/

# Lint with Flake8
flake8 toolkit/ tests/

# Type checking with MyPy (optional)
mypy toolkit/
```

### Docstrings

All public functions should have docstrings:

```python
def bob_lz_decompress(src_bytes, dec_len):
    """
    Decompress a B.O.B.-variant LZ77 stream.

    Args:
        src_bytes: Compressed byte stream
        dec_len: Expected decompressed size in bytes

    Returns:
        Tuple of (decompressed_data, bytes_consumed)

    Raises:
        ValueError: If input is truncated or invalid
    """
```

---

## Testing

### Running Tests

```bash
# Run all tests
python -m tests

# Run with verbose output
python -m tests --verbose

# Run specific test file
pytest tests/test_lz77_roundtrip.py -v

# Run with coverage
pytest --cov=toolkit --cov-report=html
```

### Writing Tests

- **Unit tests:** Go in `tests/test_*.py`
- **Property tests:** Go in `property_tests.py`
- **Test naming:** `test_<function>_<scenario>`

Example:

```python
def test_decompress_empty_input():
    """Empty input should return empty output."""
    result, consumed = bob_lz_decompress(b'', 0)
    assert result == b''
    assert consumed == 0
```

### Test Coverage

- **Minimum coverage:** 80% for new code
- **Critical paths:** 100% coverage required
- **Edge cases:** Test empty inputs, boundaries, errors

---

## Pull Request Process

### Before Submitting

1. **Fork the repository**
2. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Run tests** to ensure nothing is broken:
   ```bash
   python -m tests
   ```
5. **Format your code:**
   ```bash
   black toolkit/ tests/
   ```
6. **Update documentation** if you changed functionality

### PR Requirements

- [ ] Tests pass (`python -m tests`)
- [ ] Code is formatted (`black` and `flake8` pass)
- [ ] New code has tests
- [ ] Documentation is updated
- [ ] Commit messages are clear

### Commit Messages

Follow this format:

```
<component>: <description>

<optional details>
```

Examples:

```
ALPHA-001: LZ77 Encoder Round-Trip Testing complete

- Add 32 round-trip tests
- Integrate into run_full_test_suite.py

bob_lz: Add streaming decompression API

- New bob_lz_decompress_stream() generator function
- Memory-efficient processing for large files
```

### Review Process

1. Submit PR on GitHub
2. Wait for review (typically 1-3 days)
3. Address any feedback
4. PR will be merged when approved

---

## Issue Reporting

### Before Creating an Issue

- Search existing issues to avoid duplicates
- Check the documentation for answers
- Try the latest version from `main` branch

### Bug Reports

Include:

- **Description:** Clear description of the bug
- **Steps to Reproduce:** Exact steps to trigger the bug
- **Expected Behavior:** What should happen
- **Actual Behavior:** What actually happens
- **Environment:** Python version, OS, ROM file (if applicable)
- **Logs:** Any error messages or stack traces

### Feature Requests

Include:

- **Description:** What feature you want
- **Use Case:** Why you need it
- **Examples:** How it would be used
- **Alternatives:** Any workarounds you've tried

### Issue Labels

Issues may be labeled with:

- `bug` — Something isn't working
- `enhancement` — New feature request
- `documentation` — Documentation improvements
- `good first issue` — Good for newcomers
- `help wanted` — Extra attention needed

---

## Questions?

- Check the [documentation](docs/)
- Read the [FAQ](docs/FAQ.md) (if available)
- Open an issue for questions

---

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

---

Thank you for contributing to the B.O.B. ROM Analysis Toolkit!
