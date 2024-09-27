# Configuration file for the Sphinx documentation builder.

import os
import sys

# -- Add source files for autodoc
sys.path.insert(0, os.path.abspath('../../'))

# -- Project information

project = 'Hipopy'
copyright = '2024, Matthew McEneaney'
author = 'Matthew McEneaney'

release = '1.3'
version = '1.3.5'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]
# autosummary_generate = True  # Turn on sphinx.ext.autosummary #NOTE: ADDED

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'
html_logo = 'hipopy_logo_1.3.png'
html_theme_options = {"logo_only": True, "sticky_navigation": False}

# -- Options for EPUB output
epub_show_urls = 'footnote'
