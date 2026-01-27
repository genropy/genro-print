# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# Configuration file for the Sphinx documentation builder.

project = 'genro-print'
copyright = '2025, Softwell S.r.l.'
author = 'Genropy Team'
release = '0.1.0'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'genro_bag': ('https://genro-bag.readthedocs.io/en/latest/', None),
}

# MyST settings
myst_enable_extensions = [
    'colon_fence',
    'deflist',
]
