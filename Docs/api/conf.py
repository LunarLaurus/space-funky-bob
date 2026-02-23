# Configuration file for the Sphinx documentation builder.
# B.O.B. ROM Analysis Toolkit API Documentation

import os
import sys
sys.path.insert(0, os.path.abspath('../../toolkit'))

# -- Project information -----------------------------------------------------
project = 'B.O.B. ROM Analysis Toolkit'
copyright = '2026, B.O.B. ROM Analysis Team'
author = 'B.O.B. ROM Analysis Team'
release = '0.2.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for autodoc -----------------------------------------------------
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# -- Options for napoleon ----------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True

# -- Options for intersphinx -------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_title = 'B.O.B. ROM Analysis Toolkit'
html_short_title = 'B.O.B. Toolkit'
html_logo = None
html_favicon = None

# Theme options
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
}
