#!/usr/bin/env python

from distutils.core import setup

setup(
	name="PyChem",
	version="3.0.2 Beta",
	description="The Python Multivariate Analysis Package",
	author="Roger Jarvis",
	author_email="roger.jarvis@manchester.ac.uk",
	url="http://pychem.sf.net/",
	packages=["pychem", "pychem.mva"],
	package_data={"pychem": ["bmp/*.png", "ico/*.ico", "examples/*.*", "docs/*.*"]},
	##		data_files=[('pychem/bmp', ['pychem/bmp/addclass.png', 'pychem/bmp/addlabel.png',
	##								 'pychem/bmp/addvalidation.png','pychem/bmp/arrown.png',
	##								 'pychem/bmp/arrows.png','pychem/bmp/export.png',
	##								 'pychem/bmp/import.png','pychem/bmp/insertxvar.png',
	##								 'pychem/bmp/params.png','pychem/bmp/pychemsplash.png',
	##								 'pychem/bmp/run.png']),
	##					('pychem/examples', ['pychem/examples/ftir-ga3-bioprocess-expsetup-import.csv',
	##								  'pychem/examples/ftir-ga3-bioprocess-indvars-import.csv',
	##								  'pychem/examples/ftir-ga3-raw-data.txt']),
	##					('pychem/ico', ['pychem/ico/pychem.ico'])],
)
