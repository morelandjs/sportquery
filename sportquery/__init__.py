# -*- coding: utf-8 -*-
""" Project initialization and common objects. """
import os
from pathlib import Path

__version__ = '0.1'

homedir = Path(os.getenv('HOME'))
cachedir = homedir / '.local/share/sportquery'
