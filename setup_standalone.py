# note use $: python setup_standalone.py py2exe -b 2 -p xml.etree

from distutils.core import setup

import py2exe

setup(windows=["PyChemApp.py"])
