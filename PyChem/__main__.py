#!/usr/bin/env python
# Boa:App:BoaApp

import wx

from . import PyChemMain

modules = {"Cluster": [0, "", "Cluster.py"], "Dfa": [0, "", "Dfa.py"], "Ga": [0, "", "Ga.py"], "Pca": [0, "", "Pca.py"], "Plsr": [0, "", "Plsr.py"], "PyChemMain": [1, "Main frame of Application", "PyChemMain.py"], "chemometrics": [0, "", "chemometrics.py"], "expSetup": [0, "", "expSetup.py"], "fitfun": [0, "", "fitfun.py"], "genetic": [0, "", "genetic.py"], "plotSpectra": [0, "", "plotSpectra.py"], "process": [0, "", "process.py"]}


class BoaApp(wx.App):
	def OnInit(self):
		self.main = PyChemMain.create(None)
		self.main.Show()
		self.SetTopWindow(self.main)
		return True


def main():
	application = BoaApp(0)
	application.MainLoop()


if __name__ == "__main__":
	main()
