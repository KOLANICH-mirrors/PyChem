#!/usr/bin/env python
# -----------------------------------------------------------------------------
# Name:		   PyChem.py
# Purpose:
#
# Author:	   Roger Jarvis
#
# Created:	   2007/05/22
# RCS-ID:	   $Id$
# Copyright:   (c) 2007
# Licence:	   GNU General Public Licence
# -----------------------------------------------------------------------------
# Boa:App:BoaApp

import os
import string
import time

import mva
import PyChemMain
import wx

modules = {"Cluster": [0, "", "Cluster.py"], "Dfa": [0, "", "Dfa.py"], "Ga": [0, "", "Ga.py"], "Pca": [0, "", "Pca.py"], "Plsr": [0, "", "Plsr.py"], "PyChemMain": [1, "Main frame of Application", "PyChemMain.py"], "chemometrics": [0, "", "chemometrics.py"], "expSetup": [0, "", "expSetup.py"], "fitfun": [0, "", "fitfun.py"], "genetic": [0, "", "genetic.py"], "plotSpectra": [0, "", "plotSpectra.py"], "process": [0, "", "process.py"]}

# whereami for binary dists etc
##whereami = mva.__path__[0].split('mva')[0]
# whereami for stand alone dist
whereami = mva.__path__[0].split("\library.zip\mva")[0]


class BoaApp(wx.App):
	def OnInit(self):
		# create splash object
		bmp = wx.Image(os.path.join(whereami, "bmp", "pychemsplash.png")).ConvertToBitmap()
		splash = wx.SplashScreen(bmp, wx.SPLASH_CENTRE_ON_SCREEN, 5000, None, id=-1)
		self.SetTopWindow(splash)
		time.sleep(2)

		# start pychem
		self.main = PyChemMain.create(None)
		self.main.Show()
		self.SetTopWindow(self.main)
		splash.Destroy()
		return True


def main():
	application = BoaApp(0)
	application.MainLoop()


if __name__ == "__main__":
	main()
