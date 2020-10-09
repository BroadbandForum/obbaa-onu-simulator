# Configuration file for the Sphinx documentation builder.
#
# Copyright 2020 Broadband Forum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import warnings

# https://github.com/agronholm/sphinx-autodoc-typehints/issues/
#         133#issuecomment-629718966
warnings.filterwarnings('ignore', message='sphinx.util.inspect.Signature\(\) '
                        'is deprecated')

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

# -- Project information -----------------------------------------------------

project = 'onusim'
# noinspection PyShadowingBuiltins
copyright = '2020, Broadband Forum'
author = 'William Lupton'


# -- General configuration ---------------------------------------------------

master_doc = 'index'
default_role = 'any'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'sphinxarg.ext'
]

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'show-inheritance': True,
    'special-members': '__init__, __str__'
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['docs', 'README.md', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'
html_theme = 'nature'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['static']


# -- App setup ---------------------------------------------------------------
# see https://pypi.org/project/sphinx-markdown-parser
def setup(app):
    app.add_source_suffix('.md', 'markdown')
    app.add_source_suffix('.rst', 'restructuredtext')

    from sphinx_markdown_parser.parser import MarkdownParser
    app.add_source_parser(MarkdownParser)
    app.add_config_value('markdown_parser_config', {
        'enable_auto_toc_tree': True,
        'auto_toc_tree_maxdepth': 3,
        'auto_toc_tree_numbered': 2,
        'auto_toc_tree_section': 'Contents',
        'enable_eval_rst': True,
        'extensions': [
            'extra',
            'nl2br',
            'sane_lists',
            'smarty',
            'toc',
            'wikilinks',
        ]
    }, True)

    app.add_css_file('extra.css')

    from sphinx_markdown_parser.transform import AutoStructify
    app.add_transform(AutoStructify)
