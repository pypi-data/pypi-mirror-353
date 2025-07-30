# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

# Add the project root to the path
docs_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(docs_root / "src"))

# Set development mode for docs build to ensure all modules load
os.environ['FAILEXTRACT_DEV_MODE'] = '1'

# -- Project information -----------------------------------------------------

project = 'FailExtract'
copyright = '2025, FailExtract Contributors'
author = 'FailExtract Contributors'

# The full version, including alpha/beta/rc tags
release = '0.1.0'
version = '0.1.0'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',           # Automatic documentation from docstrings
    'sphinx.ext.napoleon',          # Google/NumPy style docstring support
    'sphinx.ext.viewcode',          # Add links to source code
    'sphinx.ext.intersphinx',       # Link to other project documentation
    'sphinx.ext.githubpages',       # Publish to GitHub Pages
    'sphinx.ext.coverage',          # Documentation coverage checking
    'sphinx.ext.doctest',           # Test code examples in documentation
    'myst_parser',                  # Markdown support
]

# Only add sphinx_autodoc_typehints if available
try:
    import sphinx_autodoc_typehints
    extensions.append('sphinx_autodoc_typehints')
except ImportError:
    # Use basic autodoc type hints if the extension isn't available
    pass

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  See the documentation for a list of options available for each theme.
html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',
    'logo_only': False,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom CSS files
html_css_files = [
    'custom.css',
]

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = None

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
html_use_smartypants = True

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
html_domain_indices = True

# If false, no index is generated.
html_use_index = True

# If true, the index is split into individual pages for each letter.
html_split_index = False

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = 'FailExtractdoc'

# -- Options for Napoleon ----------------------------------------------------

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Options for autodoc ----------------------------------------------------

# Autodoc settings
autodoc_member_order = 'bysource'
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'special-members': '__init__',
    'exclude-members': '__weakref__'
}
autodoc_mock_imports = []

# Include type hints in the description
autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented'

# Autodoc settings for better handling of optional dependencies
autodoc_preserve_defaults = True
autodoc_class_signature = 'mixed'

# -- Options for intersphinx -------------------------------------------------

# Intersphinx mapping for cross-references to other projects
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pytest': ('https://docs.pytest.org/en/stable/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
}

# -- Options for MyST parser ------------------------------------------------

# MyST parser settings for Markdown support
myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# -- Options for doctest ----------------------------------------------------

# Doctest settings
doctest_global_setup = '''
from failextract import *
import pytest
'''

# Don't fail build on doctest errors - these are examples not tests
doctest_test_doctest_blocks = 'ignore'

# -- Options for coverage ---------------------------------------------------

# Coverage settings
coverage_show_missing_items = True
coverage_ignore_modules = []
coverage_ignore_functions = []
coverage_ignore_classes = []

# -- Custom configuration ---------------------------------------------------

# Add custom setup function
def setup(app):
    """Custom Sphinx setup function."""
    app.add_css_file('custom.css')
    
# Suppress warnings for missing references
suppress_warnings = [
    'ref.citation',
    'ref.footnote',
]

# -- API documentation configuration ----------------------------------------

# Configure autodoc to skip certain problematic imports
autodoc_mock_imports = [
    'pyyaml',
    'rich', 
    'typer',
    'pydantic',
    'tomli',
]

# -- Build configuration ----------------------------------------------------

# Default role for interpreted text
default_role = 'py:obj'

# Maximum depth for table of contents
toctree_maxdepth = 3

# Include todos in documentation (set to False for production)
todo_include_todos = False

# Source file encoding
source_encoding = 'utf-8'

# Master document (landing page)
master_doc = 'index'

# Language for content autogenerated by Sphinx
language = 'en'

# Smartquotes language
smartquotes_action = 'qDe'

# Number figures, tables and code-blocks automatically
numfig = True

# Cross-reference format
numfig_format = {
    'figure': 'Figure %s',
    'table': 'Table %s',
    'code-block': 'Listing %s',
    'section': 'Section %s',
}

# Figure numbering
numfig_secnum_depth = 1

# -- LaTeX output configuration ---------------------------------------------

# LaTeX output settings (for PDF generation)
latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    'papersize': 'letterpaper',
    
    # The font size ('10pt', '11pt' or '12pt').
    'pointsize': '10pt',
    
    # Additional stuff for the LaTeX preamble.
    'preamble': '',
    
    # Latex figure (float) alignment
    'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'FailExtract.tex', 'FailExtract Documentation',
     'FailExtract Contributors', 'manual'),
]

# -- EPUB output configuration ----------------------------------------------

# EPUB settings
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']

# -- Manual page output configuration ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'failextract', 'FailExtract Documentation',
     [author], 1)
]

# -- Texinfo output configuration -------------------------------------------

# Grouping the document tree into Texinfo files.
texinfo_documents = [
    (master_doc, 'FailExtract', 'FailExtract Documentation',
     author, 'FailExtract', 'Test failure extraction and reporting library.',
     'Miscellaneous'),
]

# -- Extension configuration -------------------------------------------------

# Custom extension configurations can be added here