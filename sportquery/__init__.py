# -*- coding: utf-8 -*-
""" Project initialization and common objects. """
import os
from pathlib import Path

__version__ = '0.1'

workdir = Path(os.getenv('WORKDIR', '.'))
cachedir = workdir / 'cache'
