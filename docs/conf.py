# -*- coding: utf-8 -*-

import os
import sys

import sportquery


sys.path.insert(0, os.path.abspath(os.pardir))

project = 'sportquery'
version = release = sportquery.__version__
author = 'J. Scott Moreland'
copyright = '2021 J. Scott Moreland'

source_suffix = '.rst'
master_doc = 'index'

templates_path = ['_templates']
html_static_path = ['_static']
exclude_patterns = ['_build']

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon']

default_role = 'math'

html_theme = 'sphinx_rtd_theme'
html_context = dict(show_source=False)
