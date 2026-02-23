# Task ECHO-001: API Documentation (Sphinx)

**Squad:** Echo (Documentation & Integration)  
**Priority:** P1 (High)  
**Complexity:** Medium  
**Estimated Effort:** 6-8 hours  
**Status:** ⏳ Pending

---

## Objective

Create comprehensive API documentation using Sphinx that covers all public functions, classes, and modules with examples, type hints, and cross-references.

---

## Context

The toolkit has docstrings in source files but lacks:
- Generated HTML documentation
- Cross-referenced API index
- Searchable documentation site
- Version-specific documentation
- Examples integrated with API docs

Sphinx provides professional documentation generation with:
- Auto-generation from docstrings
- Cross-referencing between modules
- Full-text search
- Multiple output formats (HTML, PDF, ePub)

---

## Acceptance Criteria

- [ ] Sphinx setup: `docs/api/` with conf.py
- [ ] Module docs: All toolkit modules documented
- [ ] API index: Searchable function/class index
- [ ] Examples: Code examples in docstrings
- [ ] Type hints: Full type annotation documentation
- [ ] Build: `make html` generates docs
- [ ] Hosting: Docs deployable to GitHub Pages
- [ ] README link: Documentation link in README

---

## Technical Notes

### Sphinx Setup

```bash
# Install Sphinx
pip install sphinx sphinx-rtd-theme

# Create docs directory
sphinx-quickstart docs/api
```

### Configuration

```python
# docs/api/conf.py
project = 'B.O.B. ROM Analysis Toolkit'
copyright = '2026, B.O.B. ROM Analysis Team'
author = 'B.O.B. ROM Analysis Team'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # Google/NumPy style docstrings
    'sphinx.ext.viewcode',  # Link to source
    'sphinx.ext.intersphinx',  # Cross-reference other projects
]

templates_path = ['_templates']
exclude_patterns = ['_build']
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
```

### Module Documentation

```rst
.. automodule:: toolkit.bob_lz
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: toolkit.bob_lz.SNESGraphicsRenderer
   :members:
   :special-members: __init__
```

### Docstring Example

```python
def bob_lz_decompress(src_bytes: bytes, dec_len: int) -> Tuple[bytes, int]:
    """
    Decompress a B.O.B.-variant LZ77 stream.

    Args:
        src_bytes: Compressed byte stream
        dec_len: Expected decompressed size in bytes

    Returns:
        Tuple of (decompressed_data, bytes_consumed_from_input)

    Raises:
        ValueError: If input is truncated or invalid

    Example:
        >>> rom = open('B.O.B..smc', 'rb').read()
        >>> compressed = rom[0x1AD34:0x1AD34 + 0x1000]
        >>> decompressed, consumed = bob_lz_decompress(compressed, 0x822)
        >>> len(decompressed)
        2082
    """
```

---

## Files to Modify

- `docs/api/` — New Sphinx documentation directory
- `docs/api/conf.py` — Sphinx configuration
- `toolkit/*.py` — Enhance docstrings
- `README.md` — Add documentation link

---

## Dependencies

- **Blocks:** None
- **Blocked by:** None

---

## Test Plan

1. Build Sphinx documentation
2. Verify all modules are documented
3. Check cross-references work
4. Test search functionality
5. Validate examples run correctly

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
