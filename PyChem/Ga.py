# -----------------------------------------------------------------------------
# Name:		   Ga.py
# Purpose:
#
# Author:	   Roger Jarvis
#
# Created:	   2007/05/22
# RCS-ID:	   $Id$
# Copyright:   (c) 2006
# Licence:	   GNU General Public Licence
# -----------------------------------------------------------------------------
# Boa:FramePanel:Ga

import os
import string

import mva.chemometrics
import mva.fitfun
import mva.genetic
import mva.process
import scipy
import wx
import wx.lib.agw.buttonpanel as bp
import wx.lib.buttons
import wx.lib.plot
import wx.lib.stattext
from mva.chemometrics import _index
from scipy import newaxis as nA
from wx.lib.anchors import LayoutAnchors

from .Pca import MyPlotCanvas, plotLine, plotStem, plotText
from .Plsr import PlotPlsModel
from .utils.io import str_array


def errorBox(window, error):
	dlg = wx.MessageDialog(window, "".join(("The following error occured:\n\n", error)), "Error!", wx.OK | wx.ICON_ERROR)
	try:
		dlg.ShowModal()
	finally:
		dlg.Destroy()


class Ga(wx.Panel):
	# genetic algorithm coupled to discriminant function analysis
	def _init_coll_bxsGa1_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.bxsGa2, 1, border=0, flag=wx.EXPAND)

	def _init_coll_bxsGa2_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.titleBar, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.grsGa, 1, border=0, flag=wx.EXPAND)

	def _init_coll_grsGa_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.plcGaPlot, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.plcGaFreqPlot, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.plcGaFeatPlot, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.nbGaModPlot, 0, border=0, flag=wx.EXPAND)

	def _init_coll_nbGaModPlot_Pages(self, parent):
		# generated method, don't edit

		parent.AddPage(imageId=-1, page=self.plcGaOptPlot, select=True, text="GA Optimisation Curve")
		parent.AddPage(imageId=-1, page=self.plcGaEigs, select=False, text="Eigenvalues")
		parent.AddPage(imageId=-1, page=self.plcGaSpecLoad, select=False, text="Spectral Loadings")
		parent.AddPage(imageId=-1, page=self.plcGaGrpDistPlot, select=False, text="Model Error Comparisons")

	def _init_sizers(self):
		self.grsGa = wx.GridSizer(cols=2, hgap=2, rows=2, vgap=2)

		self.bxsGa2 = wx.BoxSizer(orient=wx.VERTICAL)

		self.bxsGa1 = wx.BoxSizer(orient=wx.HORIZONTAL)

		self._init_coll_bxsGa1_Items(self.bxsGa1)
		self._init_coll_bxsGa2_Items(self.bxsGa2)
		self._init_coll_grsGa_Items(self.grsGa)

		self.SetSizer(self.bxsGa1)

	def _init_ctrls(self, prnt):
		wx.Panel.__init__(self, id=-1, name="Ga", parent=prnt, pos=wx.Point(47, 118), size=wx.Size(796, 460), style=wx.TAB_TRAVERSAL)
		self.SetToolTip("")
		self.SetAutoLayout(True)

		self.plcGaPlot = MyPlotCanvas(id=-1, name="plcGaPlot", parent=self, pos=wx.Point(0, 0), size=wx.Size(310, 272), style=0)
		self.plcGaPlot.enableZoom = True
		self.plcGaPlot.fontSizeAxis = 8
		self.plcGaPlot.fontSizeLegend = 8
		self.plcGaPlot.fontSizeTitle = 10
		self.plcGaPlot.SetToolTip("")
		self.plcGaPlot.SetAutoLayout(True)
		self.plcGaPlot.SetConstraints(LayoutAnchors(self.plcGaPlot, True, True, True, True))
		self.plcGaPlot.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))

		self.nbGaModPlot = wx.Notebook(id=-1, name="nbGaModPlot", parent=self, pos=wx.Point(760, 326), size=wx.Size(310, 272), style=wx.NB_BOTTOM)
		self.nbGaModPlot.SetToolTip("")
		self.nbGaModPlot.SetAutoLayout(True)
		self.nbGaModPlot.SetConstraints(LayoutAnchors(self.nbGaModPlot, True, True, True, True))

		self.plcGaEigs = MyPlotCanvas(id=-1, name="plcGaEigs", parent=self.nbGaModPlot, pos=wx.Point(0, 0), size=wx.Size(310, 272), style=0)
		self.plcGaEigs.enableZoom = True
		self.plcGaEigs.fontSizeAxis = 8
		self.plcGaEigs.fontSizeLegend = 8
		self.plcGaEigs.fontSizeTitle = 10
		self.plcGaEigs.SetToolTip("")
		self.plcGaEigs.SetAutoLayout(True)
		self.plcGaEigs.SetConstraints(LayoutAnchors(self.plcGaEigs, True, True, True, True))
		self.plcGaEigs.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))

		self.plcGaSpecLoad = MyPlotCanvas(id=-1, name="plcGaSpecLoad", parent=self.nbGaModPlot, pos=wx.Point(0, 24), size=wx.Size(503, 279), style=0)
		self.plcGaSpecLoad.SetToolTip("")
		self.plcGaSpecLoad.enableZoom = True
		self.plcGaSpecLoad.fontSizeAxis = 8
		self.plcGaSpecLoad.fontSizeLegend = 8
		self.plcGaSpecLoad.fontSizeTitle = 10
		self.plcGaSpecLoad.SetAutoLayout(True)
		self.plcGaSpecLoad.SetConstraints(LayoutAnchors(self.plcGaSpecLoad, True, True, True, True))
		self.plcGaSpecLoad.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))

		self.plcGaFreqPlot = MyPlotCanvas(id=-1, name="plcGaFreqPlot", parent=self, pos=wx.Point(760, 0), size=wx.Size(310, 272), style=0)
		self.plcGaFreqPlot.enableZoom = True
		self.plcGaFreqPlot.fontSizeAxis = 8
		self.plcGaFreqPlot.fontSizeLegend = 8
		self.plcGaFreqPlot.fontSizeTitle = 10
		self.plcGaFreqPlot.SetToolTip("")
		self.plcGaFreqPlot.SetAutoLayout(True)
		self.plcGaFreqPlot.SetConstraints(LayoutAnchors(self.plcGaFreqPlot, True, True, True, True))
		self.plcGaFreqPlot.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))

		self.plcGaFeatPlot = MyPlotCanvas(id=-1, name="plcGaFeatPlot", parent=self, pos=wx.Point(0, 24), size=wx.Size(310, 272), style=0)
		self.plcGaFeatPlot.SetToolTip("")
		self.plcGaFeatPlot.enableZoom = True
		self.plcGaFeatPlot.fontSizeAxis = 8
		self.plcGaFeatPlot.fontSizeLegend = 8
		self.plcGaFeatPlot.fontSizeTitle = 10
		self.plcGaFeatPlot.SetAutoLayout(True)
		self.plcGaFeatPlot.SetConstraints(LayoutAnchors(self.plcGaFeatPlot, True, True, True, True))
		self.plcGaFeatPlot.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))

		self.plcGaGrpDistPlot = MyPlotCanvas(id=-1, name="plcGaGrpDistPlot", parent=self.nbGaModPlot, pos=wx.Point(0, 0), size=wx.Size(310, 272), style=0)
		self.plcGaGrpDistPlot.enableLegend = True
		self.plcGaGrpDistPlot.enableZoom = True
		self.plcGaGrpDistPlot.fontSizeAxis = 8
		self.plcGaGrpDistPlot.fontSizeLegend = 8
		self.plcGaGrpDistPlot.fontSizeTitle = 10
		self.plcGaGrpDistPlot.SetToolTip("")
		self.plcGaGrpDistPlot.SetAutoLayout(True)
		self.plcGaGrpDistPlot.SetConstraints(LayoutAnchors(self.plcGaGrpDistPlot, True, True, True, True))
		self.plcGaGrpDistPlot.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))

		self.plcGaOptPlot = MyPlotCanvas(id=-1, name="plcGaOptPlot", parent=self.nbGaModPlot, pos=wx.Point(0, 0), size=wx.Size(310, 272), style=0)
		self.plcGaOptPlot.enableLegend = False
		self.plcGaOptPlot.enableZoom = True
		self.plcGaOptPlot.fontSizeAxis = 8
		self.plcGaOptPlot.fontSizeLegend = 8
		self.plcGaOptPlot.fontSizeTitle = 10
		self.plcGaOptPlot.SetToolTip("")
		self.plcGaOptPlot.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))
		self.plcGaOptPlot.SetAutoLayout(True)
		self.plcGaOptPlot.SetConstraints(LayoutAnchors(self.plcGaOptPlot, True, True, True, True))

		self.titleBar = TitleBar(self, id=-1, text="", style=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT, gatype=self.type)

		self._init_coll_nbGaModPlot_Pages(self.nbGaModPlot)

		self._init_sizers()

	def __init__(self, parent, id, pos, size, style, name, type):
		self.type = type

		self._init_ctrls(parent)

		self.parent = parent

	def Reset(self):
		# disable ctrls
		self.titleBar.spnGaScoreFrom.Enable(False)
		self.titleBar.spnGaScoreTo.Enable(False)
		self.titleBar.cbxFeature1.Enable(False)
		self.titleBar.cbxFeature2.Enable(False)

		# clear plots
		objects = {"plcGaPlot": ["Predictions", "Latent Variable 1", "Latent Variable 1"], "plcGaFeatPlot": ["Independent Variable Biplot", "Variable", "Variable"], "plcGaFreqPlot": ["Frequency of Variable Selection", "Independent Variable", "Frequency"], "plcGaOptPlot": ["Rate of GA Optimisation", "Generation", "Fitness Score"]}

		curve = wx.lib.plot.PolyLine([[0, 0], [1, 1]], colour="white", width=1, style=wx.TRANSPARENT)

		for each in list(objects.keys()):
			exec("self." + each + ".Draw(wx.lib.plot.PlotGraphics([curve]," + 'objects["' + each + '"][0],' + 'objects["' + each + '"][1],' + 'objects["' + each + '"][2]))')


class TitleBar(bp.ButtonPanel):
	def _init_btnpanel_ctrls(self, prnt):
		bp.ButtonPanel.__init__(self, parent=prnt, id=-1, text="GA-" + self.type, agwStyle=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self.cbxData = wx.Choice(choices=["Raw spectra", "Processed spectra"], id=-1, name="cbxData", parent=self, pos=wx.Point(118, 23), size=wx.Size(100, 23), style=0)
		self.cbxData.SetSelection(0)

		self.btnRunGa = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "run.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Run Genetic Algorithm", longHelp="Run Genetic Algorithm")
		self.btnRunGa.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnrungaButton, id=self.btnRunGa.GetId())

		self.btnExportGa = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "export.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Export GA Results", longHelp="Export Genetic Algorithm Results")
		self.btnExportGa.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnexportgaButton, id=self.btnExportGa.GetId())

		self.cbxFeature1 = wx.Choice(choices=[""], id=-1, name="cbxFeature1", parent=self, pos=wx.Point(118, 23), size=wx.Size(60, 23), style=0)
		self.cbxFeature1.SetSelection(0)
		self.cbxFeature1.Bind(wx.EVT_CHOICE, self.OnCbxfeature1, id=-1)

		self.cbxFeature2 = wx.Choice(choices=[""], id=-1, name="cbxFeature2", parent=self, pos=wx.Point(118, 23), size=wx.Size(60, 23), style=0)
		self.cbxFeature2.SetSelection(0)
		self.cbxFeature2.Bind(wx.EVT_CHOICE, self.OnCbxfeature2, id=-1)

		self.spnGaScoreFrom = wx.SpinCtrl(id=-1, initial=1, max=100, min=1, name="spnGaScoreFrom", parent=self, pos=wx.Point(184, 2), size=wx.Size(40, 23), style=wx.SP_ARROW_KEYS)
		self.spnGaScoreFrom.SetValue(1)
		self.spnGaScoreFrom.SetToolTip("")
		self.spnGaScoreFrom.Bind(wx.EVT_SPINCTRL, self.OnSpnGascorefromSpinctrl, id=-1)

		self.spnGaScoreTo = wx.SpinCtrl(id=-1, initial=2, max=100, min=1, name="spnGaScoreTo", parent=self, pos=wx.Point(256, 2), size=wx.Size(40, 23), style=wx.SP_ARROW_KEYS)
		self.spnGaScoreTo.SetValue(2)
		self.spnGaScoreTo.SetToolTip("")
		self.spnGaScoreTo.Bind(wx.EVT_SPINCTRL, self.OnSpnGascoretoSpinctrl, id=-1)

		self.btnSetParams = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "params.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Set GA Parameters", longHelp="Set Genetic Algorithm Parameters")
		self.Bind(wx.EVT_BUTTON, self.OnBtnbtnSetParamsButton, id=self.btnSetParams.GetId())

	def __init__(self, parent, id, text, style, alignment, gatype):
		self.parent = parent

		self.type = gatype

		self._init_btnpanel_ctrls(parent)

		self.dlg = selParam(self)

		self.dlg.SetTitle("GA-" + self.type + " Parameters")

		self.spnGaScoreFrom.Show(0)
		self.spnGaScoreTo.Show(False)

		self.CreateButtons()

	def getData(self, data):
		self.data = data

	def CreateButtons(self):
		self.Freeze()

		self.SetProperties()

		self.AddControl(self.cbxData)
		self.AddSeparator()
		if self.type in ["DFA"]:
			self.AddControl(wx.lib.stattext.GenStaticText(self, -1, "DF ", style=wx.TRANSPARENT_WINDOW))
			self.AddControl(self.spnGaScoreFrom)
			self.AddControl(wx.lib.stattext.GenStaticText(self, -1, " vs. ", style=wx.TRANSPARENT_WINDOW))
			self.AddControl(self.spnGaScoreTo)
			self.AddSeparator()
		self.AddControl(wx.lib.stattext.GenStaticText(self, -1, "Variable", style=wx.TRANSPARENT_WINDOW))
		self.AddControl(self.cbxFeature1)
		self.AddControl(wx.lib.stattext.GenStaticText(self, -1, " vs. ", style=wx.TRANSPARENT_WINDOW))
		self.AddControl(self.cbxFeature2)
		self.AddSeparator()
		self.AddButton(self.btnSetParams)
		self.AddSeparator()
		self.AddButton(self.btnRunGa)
		self.AddSeparator()
		self.AddButton(self.btnExportGa)

		self.Thaw()

		self.DoLayout()

	def SetProperties(self):

		# Sets the colours for the two demos: called only if the user didn't
		# modify the colours and sizes using the Settings Panel
		bpArt = self.GetBPArt()

		# set the color the text is drawn with
		bpArt.SetColor(bp.BP_TEXT_COLOUR, wx.WHITE)

		background = self.GetBackgroundColour()
		bpArt.SetColor(bp.BP_TEXT_COLOUR, wx.BLUE)
		bpArt.SetColor(bp.BP_BORDER_COLOUR, bp.BrightenColour(background, 0.85))
		bpArt.SetColor(bp.BP_SEPARATOR_COLOUR, bp.BrightenColour(background, 0.85))
		bpArt.SetColor(bp.BP_BUTTONTEXT_COLOUR, wx.BLACK)
		bpArt.SetColor(bp.BP_SELECTION_BRUSH_COLOUR, wx.Colour(242, 242, 235))
		bpArt.SetColor(bp.BP_SELECTION_PEN_COLOUR, wx.Colour(206, 206, 195))

	def OnBtnbtnSetParamsButton(self, event):
		height = wx.GetDisplaySize()[1]
		self.dlg.SetSize(wx.Size(250, height))
		self.dlg.SetPosition(wx.Point(0, 0))
		self.dlg.Iconize(False)
		self.dlg.Show()

	def OnBtnrungaButton(self, event):
		self.runGa(varfrom=self.dlg.spnGaVarsFrom.GetValue(), varto=self.dlg.spnGaVarsTo.GetValue(), inds=self.dlg.spnGaNoInds.GetValue(), runs=self.dlg.spnGaNoRuns.GetValue(), xovr=float(self.dlg.stGaXoverRate.GetValue()), mutr=float(self.dlg.stGaMutRate.GetValue()), insr=float(self.dlg.stGaInsRate.GetValue()), maxf=self.dlg.spnGaMaxFac.GetValue(), mgen=self.dlg.spnGaMaxGen.GetValue(), rgen=self.dlg.spnGaRepUntil.GetValue())

	def OnBtnexportgaButton(self, event):
		dlg = wx.FileDialog(self, "Choose a file", ".", "", "Any files (*.*)|*.*", wx.FD_SAVE)
		try:
			if dlg.ShowModal() == wx.ID_OK:
				saveFile = dlg.GetPath()
				out = "#CHROMOSOMES\n" + str_array(self.data["gadfachroms"], col_sep="\t") + "\n" + "#FITNESS_OPTIMISATION\n" + str_array(self.data["gadfacurves"], col_sep="\t")
				f = file(saveFile, "w")
				f.write(out)
				f.close()
		finally:
			dlg.Destroy()

	def OnSpnGascorefromSpinctrl(self, event):
		# GA scores plot
		gaOrdPlot = plotText(self.parent.plcGaPlot, self.data["gadfadfscores"], self.data["validation"], self.data["class"], self.data["label"], self.spnGaScoreFrom.GetValue() - 1, self.spnGaScoreTo.GetValue() - 1, "", "Discriminant Function")

		# DF loadings
		exec("drawGaLoad = self.dlg.plotGaLoads(self.dlg.currentChrom,self.data['ga" + self.type.lower() + self.type.lower() + "loads'],self.parent.plcGaSpecLoad,self.spnGaScoreFrom.GetValue()-1)")

	def OnSpnGascoretoSpinctrl(self, event):
		# GA scores plot
		gaOrdPlot = plotText(self.parent.plcGaPlot, self.data["gadfadfscores"], self.data["validation"], self.data["class"], self.data["label"], self.spnGaScoreFrom.GetValue() - 1, self.spnGaScoreTo.GetValue() - 1, "", "Discriminant Function")

		# DF loadings
		exec("drawGaLoad = self.dlg.plotGaLoads(self.dlg.currentChrom,self.data['ga" + self.type.lower() + self.type.lower() + "loads'],self.parent.plcGaSpecLoad,self.spnGaScoreFrom.GetValue()-1)")

	def OnCbxfeature1(self, event):
		gaFeatPlot = self.dlg.PlotGaVariables(self.parent.plcGaFeatPlot)

	def OnCbxfeature2(self, event):
		gaFeatPlot = self.dlg.PlotGaVariables(self.parent.plcGaFeatPlot)

	def runGa(self, **_attr):
		"""Runs GA
		**_attr - key word _attributes
			Defaults:
				'varfrom' = 2,		- No of ind. variables from
				'varto' = 2,	  - No of ind. variables to
				'inds'= 10,		- No. of individuals
				'runs'= 1,	   - No. of independent GA runs
				'xovr'= 0.8,	 - Crossover rate
				'mutr'= 0.4,	 - Mutation rate
				'insr'= 0.8,	 - Insertion rate
				'maxf'= 1,	   - Maximum no.of latent variables
				'mgens'= 5,		 - Max. no. of generations
				'rgens'= 5,		 - No. of repeat gens

		"""

		dlg = wx.MessageDialog(self, "This can take a while, are you sure?", "Preparing to run GA", wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
		try:
			go = 0
			if dlg.ShowModal() == wx.ID_OK:
				go = 1
		finally:
			dlg.Destroy()

		if go == 1:
			self.parent.Reset()
			try:
				# set busy cursor
				wx.BeginBusyCursor()

				# Set xdata
				if self.cbxData.GetSelection() == 0:
					xdata = self.data["raw"]
				elif self.cbxData.GetSelection() == 1:
					xdata = self.data["proc"]

				# Run DFA - set containers
				scoreList = []
				chromList = []
				cUrves = []

				varFrom = varfrom
				varTo = varto
				if varTo - varFrom == 0:
					varRange = 1
				else:
					varRange = varTo - varFrom + 1

				for Vars in range(varRange):
					# set num latent variables
					if int(maxf) >= int(max(self.data["class"])):
						Lvs = int(max(self.data["class"])) - 1
					else:
						Lvs = int(maxf)

					for Runs in range(runs):
						# run ga-dfa

						# create initial population
						chrom = mva.genetic.crtpop(inds, Vars + varFrom, xdata.shape[1])

						# evaluate initial population
						if self.type in ["DFA"]:
							scores = mva.fitfun.call_dfa(chrom, xdata, self.data["validation"], self.data["class"], self.data["label"], Lvs)

						elif self.type in ["PLS"]:
							scores = mva.fitfun.call_pls(chrom, xdata, self.data["validation"][:, nA], np.array(self.data["class"])[:, nA], Lvs)

						# add additional methods here

						count = 0

						# set stopping criterion
						if self.dlg.cbGaRepUntil.GetValue() is False:
							stop = mgen
						else:
							stop = 1000
							chromRecord = scipy.zeros((1, Vars + varFrom))

						while count < stop:
							# linear ranking
							ranksc, chrom, scores = mva.genetic.rank(chrom, scores)

							# select individuals from population
							chromSel = mva.genetic.select(ranksc, chrom, insr)

							# perform crossover
							if self.dlg.cbGaXover.GetValue() is True:
								chromSel = mva.genetic.xover(chromSel, xovr, xdata.shape[1])

							# perform mutation
							if self.dlg.cbGaMut.GetValue() is True:
								chromSel = mva.genetic.mutate(chromSel, mutr, xdata.shape[1])

							# evaluate chromSel
							if self.type in ["DFA"]:
								scoresSel = mva.fitfun.call_dfa(chromSel, xdata, self.data["validation"], self.data["class"], self.data["label"], Lvs)
							elif self.type in ["PLS"]:
								scoresSel = mva.fitfun.call_pls(chromSel, xdata, self.data["validation"][:, nA], np.array(self.data["class"])[:, nA], Lvs)
							# add additional methods here

							# reinsert chromSel replacing worst parents in chrom
							chrom, scores = mva.genetic.reinsert(chrom, chromSel, scores, scoresSel)

							if count == 0:
								scoresOut = [min(min(scores))]
							else:
								scoresOut.append(min(min(scores)))

							# Build history for second stopping criterion
							if self.dlg.cbGaRepUntil.GetValue() is True:
								Best = scores[0]
								tChrom = chrom[0]
								chromRecord = scipy.concatenate((chromRecord, tChrom[nA, :]), 0)
								if count >= int(rgen):
									chk = 0
									for n in range(count - rgen + 2, count + 2):
										a = chromRecord[n - 1]
										a.sort()
										b = chromRecord[n]
										b.sort()
										chk = chk + scipy.sum(a - b)
									if chk == 0:
										count = 999

							count += 1

							# report progress to status bar
							self.parent.parent.parent.sbMain.SetStatusText(" ".join(("Variable", str(Vars + varFrom))), 0)
							self.parent.parent.parent.sbMain.SetStatusText(" ".join(("Run", str(Runs + 1))), 1)
							self.parent.parent.parent.sbMain.SetStatusText(" ".join(("Generation", str(count))), 2)

						# Save GA optimisation curve
						scoresOut = scipy.asarray(scoresOut)

						# concatenate run result
						if varRange == 1:
							if Vars + Runs == 0:
								# scores
								scoreList = [1.0 / float(scores[0])]
								# chromosomes
								chromList = chrom[0, :][nA]
								chromList.sort()
								# opt curves
								cUrves = scipy.reshape(scoresOut, (1, len(scoresOut)))
							else:
								# scores
								scoreList.append(1.0 / float(scores[0]))
								# chromosomes
								ins = chrom[0, :][nA]
								ins.sort()
								chromList = scipy.concatenate((chromList, ins), 0)
								# opt curves
								length = cUrves.shape[1]
								if length < len(scoresOut):
									cUrves = scipy.concatenate((cUrves, scipy.zeros((len(cUrves), len(scoresOut) - length))), 1)
								elif length > len(scoresOut):
									scoresOut = scipy.concatenate((scipy.reshape(scoresOut, (1, len(scoresOut))), scipy.zeros((1, length - len(scoresOut)))), 1)
									scoresOut = scipy.reshape(scoresOut, (scoresOut.shape[1],))
								cUrves = scipy.concatenate((cUrves, scipy.reshape(scoresOut, (1, len(scoresOut)))), 0)
						elif varRange > 1:
							if Vars + Runs == 0:
								# scores
								scoreList = [1.0 / float(scores[0])]
								# chromosomes
								ins = chrom[0, :][nA]
								ins.sort()
								chromList = scipy.concatenate((ins, scipy.zeros((1, varRange - Vars - 1), "d")), 1)
								# opt curves
								cUrves = scipy.reshape(scoresOut, (1, len(scoresOut)))
							else:
								# scores
								scoreList.append(1.0 / float(scores[0]))
								# chromosomes
								ins = chrom[0, :][nA]
								ins.sort()
								chromList = scipy.concatenate((chromList, scipy.concatenate((ins, scipy.zeros((1, varRange - Vars - 1), "d")), 1)), 0)

								# opt curves
								length = cUrves.shape[1]
								if length < len(scoresOut):
									cUrves = scipy.concatenate((cUrves, scipy.zeros((len(cUrves), len(scoresOut) - length))), 1)
								elif length > len(scoresOut):
									scoresOut = scipy.concatenate((scipy.reshape(scoresOut, (1, len(scoresOut))), scipy.zeros((1, length - len(scoresOut)))), 1)
									scoresOut = scipy.reshape(scoresOut, (scoresOut.shape[1],))
								cUrves = scipy.concatenate((cUrves, scipy.reshape(scoresOut, (1, len(scoresOut)))), 0)

				# add results to disctionary
				exec("self.data['ga" + self.type.lower() + "chroms'] = chromList")
				exec("self.data['ga" + self.type.lower() + "scores'] = scoreList")
				exec("self.data['ga" + self.type.lower() + "curves'] = cUrves")

				# Create results tree
				self.CreateGaResultsTree(self.dlg.treGaResults, gacurves=cUrves, chroms=chromList, varfrom=varfrom, varto=varto, runs=runs - 1)

				# enable export btn
				self.btnExportGa.Enable(1)

				# reset cursor
				wx.EndBusyCursor()

			except Exception as error:
				wx.EndBusyCursor()
				errorBox(self, "%s" % str(error))
		##				  raise

		# clear status bar
		self.parent.parent.parent.sbMain.SetStatusText("Status", 0)
		self.parent.parent.parent.sbMain.SetStatusText("", 1)
		self.parent.parent.parent.sbMain.SetStatusText("", 2)

	def CreateGaResultsTree(self, tree, **_attr):
		"""Populates GA results tree ctrl
		**_attr - key word _attributes
			Defaults:
				'gacurves' = None	   - Optimisation curves from each ind. run
				'chroms' = None		   - Array of chromosomes
				'varfrom' = 2		   - Min. no. of vars selected
				'varto' = 2			   - Max. no. of vars selected
				'runs' = 1			   - Number of ind. GA runs

		"""

		# clear tree ctrl
		tree.DeleteAllItems()
		tree.AddRoot("Root")
		dfaRoot = tree.GetRootItem()

		# generate top score list
		gacurves = scipy.concatenate((gacurves, scipy.zeros((len(gacurves), 1))), 1)
		gaScoreList = []
		for x in range(len(gacurves)):
			t = (
				gacurves[
					x,
				]
				.tolist()
				.index(0)
			)
			gaScoreList.append(gacurves[x, t - 1])

		tree.DeleteAllItems()
		tree.AddRoot("Root")
		dfaRoot = tree.GetRootItem()

		##		  if self.cbDfaSavePc.GetValue() is False:#saved only best result
		noSaveChroms = 1
		##		  elif self.cbDfaSavePc.GetValue() is True: #saved % of results
		##			  noSaveChroms = int((float(self.stDfaSavePc.GetValue())/100)*int(self.stDfaNoInds.GetValue()))

		TreeItemIdList = []
		Count, IterCount = 0, 0
		for vars in range(varto - varfrom + 1):
			NewVar = tree.AppendItem(dfaRoot, "".join((str(vars + varfrom), " variables")))
			TreeItemIdList.append(NewVar)
			for runs in range(runs + 1):
				for mch in range(noSaveChroms):
					RunLabel = scipy.sort(chroms[Count + mch, 0 : vars + varfrom]).tolist()
					NewChrom = tree.AppendItem(NewVar, "".join(("#", str(IterCount + 1), " ", str(scipy.take(scipy.reshape(self.data["indlabels"], (len(self.data["indlabels"]),)), RunLabel)), " " "%.2f" % (gaScoreList[Count + mch]))))
					TreeItemIdList.append(NewChrom)
					IterCount += 1
				Count += mch + 1

		tree.Expand(dfaRoot)
		for i in range(len(TreeItemIdList)):
			tree.Expand(TreeItemIdList[i])


class selParam(wx.Frame):
	def _init_coll_gbsGa_Growables(self, parent):
		# generated method, don't edit

		parent.AddGrowableRow(12)
		parent.AddGrowableCol(0)
		parent.AddGrowableCol(1)
		parent.AddGrowableCol(2)

	def _init_coll_gbsGa_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(wx.StaticText(self.panel, -1, "No. vars. from", style=wx.ALIGN_RIGHT), (0, 0), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.spnGaVarsFrom, (0, 1), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddSpacer(wx.Size(8, 8), (0, 2), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(wx.StaticText(self.panel, -1, "No. vars. to", style=wx.ALIGN_RIGHT), (1, 0), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.spnGaVarsTo, (1, 1), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddSpacer(wx.Size(8, 8), (1, 2), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(wx.StaticText(self.panel, -1, "No. inds.", style=wx.ALIGN_RIGHT), (2, 0), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.spnGaNoInds, (2, 1), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddSpacer(wx.Size(8, 8), (2, 2), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(wx.StaticText(self.panel, -1, "No. runs", style=wx.ALIGN_RIGHT), (3, 0), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.spnGaNoRuns, (3, 1), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddSpacer(wx.Size(8, 8), (3, 2), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(wx.StaticText(self.panel, -1, "Crossover rate", style=wx.ALIGN_RIGHT), (4, 0), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.stGaXoverRate, (4, 1), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.cbGaXover, (4, 2), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(wx.StaticText(self.panel, -1, "Mutation rate", style=wx.ALIGN_RIGHT), (5, 0), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.stGaMutRate, (5, 1), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.cbGaMut, (5, 2), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(wx.StaticText(self.panel, -1, "Insertion rate", style=wx.ALIGN_RIGHT), (6, 0), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.stGaInsRate, (6, 1), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddSpacer(wx.Size(8, 8), (6, 2), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(wx.StaticText(self.panel, -1, "Max. factors", style=wx.ALIGN_RIGHT), (7, 0), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.spnGaMaxFac, (7, 1), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddSpacer(wx.Size(8, 8), (7, 2), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(wx.StaticText(self.panel, -1, "Max. gens", style=wx.ALIGN_RIGHT), (8, 0), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.spnGaMaxGen, (8, 1), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.cbGaMaxGen, (8, 2), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(wx.StaticText(self.panel, -1, "Repeat until", style=wx.ALIGN_RIGHT), (9, 0), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.spnGaRepUntil, (9, 1), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.cbGaRepUntil, (9, 2), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddSpacer(wx.Size(8, 8), (10, 0), border=10, flag=wx.EXPAND, span=(1, 3))
		parent.AddWindow(self.staticText1, (11, 0), border=10, flag=wx.EXPAND, span=(1, 3))
		parent.AddWindow(self.treGaResults, (12, 0), border=10, flag=wx.EXPAND, span=(1, 3))

	def _init_selparam_sizers(self):
		# generated method, don't edit
		self.gbsGa = wx.GridBagSizer(hgap=4, vgap=4)
		self.gbsGa.SetCols(3)
		self.gbsGa.SetRows(13)
		self.gbsGa.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
		self.gbsGa.SetMinSize(wx.Size(100, 439))
		self.gbsGa.SetEmptyCellSize(wx.Size(0, 0))
		self.gbsGa.SetFlexibleDirection(wx.VERTICAL)

		self._init_coll_gbsGa_Items(self.gbsGa)
		self._init_coll_gbsGa_Growables(self.gbsGa)

		self.panel.SetSizer(self.gbsGa)

	def _init_selparam_ctrls(self, prnt):
		# generated method, don't edit
		wx.Frame.__init__(self, id=-1, name="selFun", parent=prnt, pos=wx.Point(0, 0), size=wx.Size(180, 739), style=wx.DEFAULT_FRAME_STYLE, title="Define GA Parameters")
		self.SetToolTip("")
		self.Bind(wx.EVT_CLOSE, self.OnMiniFrameClose)

		self.panel = wx.Panel(id=-1, name="panel", parent=self, pos=wx.Point(0, 0), size=wx.Size(180, 739), style=wx.TAB_TRAVERSAL)
		self.panel.SetToolTip("")

		self.staticText1 = wx.StaticText(id=-1, label="Results", name="staticText1", parent=self.panel, pos=wx.Point(72, 8), size=wx.Size(54, 21), style=0)
		self.staticText1.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, True, "MS Shell Dlg 2"))

		self.spnGaVarsFrom = wx.SpinCtrl(id=-1, initial=2, max=100, min=2, name="spnGaVarsFrom", parent=self.panel, pos=wx.Point(73, 0), size=wx.Size(15, 21), style=wx.SP_ARROW_KEYS)
		self.spnGaVarsFrom.SetToolTip("Variable range from")

		self.spnGaVarsTo = wx.SpinCtrl(id=-1, initial=2, max=100, min=2, name="spnGaVarsTo", parent=self.panel, pos=wx.Point(219, 0), size=wx.Size(15, 21), style=wx.SP_ARROW_KEYS)
		self.spnGaVarsTo.SetToolTip("Variable range to")

		self.spnGaNoInds = wx.SpinCtrl(id=-1, initial=10, max=1000, min=10, name="spnGaNoInds", parent=self.panel, pos=wx.Point(73, 23), size=wx.Size(15, 21), style=wx.SP_ARROW_KEYS)
		self.spnGaVarsTo.SetToolTip("Number of individuals")

		self.spnGaNoRuns = wx.SpinCtrl(id=-1, initial=1, max=1000, min=1, name="spnGaNoRuns", parent=self.panel, pos=wx.Point(219, 23), size=wx.Size(15, 21), style=wx.SP_ARROW_KEYS)
		self.spnGaVarsTo.SetToolTip("Number of independent GA runs")

		self.stGaXoverRate = wx.TextCtrl(id=-1, name="stGaXoverRate", value="0.8", parent=self.panel, pos=wx.Point(216, 48), size=wx.Size(15, 21), style=0)
		self.stGaXoverRate.SetToolTip("Crossover rate")

		self.cbGaXover = wx.CheckBox(id=-1, label="", name="cbGaXover", parent=self.panel, pos=wx.Point(0, 46), size=wx.Size(10, 21), style=wx.ALIGN_LEFT)
		self.cbGaXover.SetValue(True)
		self.cbGaXover.SetToolTip("")

		self.stGaMutRate = wx.TextCtrl(id=-1, name="stGaMutRate", value="0.4", parent=self.panel, pos=wx.Point(216, 48), size=wx.Size(15, 21), style=0)
		self.stGaMutRate.SetToolTip("Mutation rate")

		self.cbGaMut = wx.CheckBox(id=-1, label="", name="cbGaMut", parent=self.panel, pos=wx.Point(146, 46), size=wx.Size(10, 21), style=wx.ALIGN_LEFT)
		self.cbGaMut.SetValue(True)
		self.cbGaMut.SetToolTip("")

		self.stGaInsRate = wx.TextCtrl(id=-1, name="stGaInsRate", value="0.8", parent=self.panel, pos=wx.Point(216, 48), size=wx.Size(15, 21), style=0)
		self.stGaXoverRate.SetToolTip("Insertion rate")

		self.spnGaMaxFac = wx.SpinCtrl(id=-1, initial=1, max=100, min=1, name="spnGaMaxFac", parent=self.panel, pos=wx.Point(219, 69), size=wx.Size(15, 21), style=wx.SP_ARROW_KEYS)
		self.spnGaMaxFac.SetToolTip("Maximum number of latent variables")

		self.spnGaMaxGen = wx.SpinCtrl(id=-1, initial=5, max=1000, min=5, name="spnGaMaxGen", parent=self.panel, pos=wx.Point(73, 92), size=wx.Size(15, 21), style=wx.SP_ARROW_KEYS)
		self.spnGaMaxGen.SetToolTip("Maximum number of generations")

		self.cbGaMaxGen = wx.CheckBox(id=-1, label="", name="cbGaMaxGen", parent=self.panel, pos=wx.Point(0, 92), size=wx.Size(10, 21), style=wx.ALIGN_LEFT)
		self.cbGaMaxGen.SetValue(True)
		self.cbGaMaxGen.SetToolTip("")
		self.cbGaMaxGen.Show(False)

		self.spnGaRepUntil = wx.SpinCtrl(id=-1, initial=5, max=1000, min=5, name="spnGaRepUntil", parent=self.panel, pos=wx.Point(219, 92), size=wx.Size(15, 21), style=wx.SP_ARROW_KEYS)
		self.spnGaRepUntil.SetToolTip("Repeat generations until")

		self.cbGaRepUntil = wx.CheckBox(id=-1, label="", name="cbGaRepUntil", parent=self.panel, pos=wx.Point(146, 92), size=wx.Size(10, 21), style=wx.ALIGN_LEFT)
		self.cbGaRepUntil.SetValue(False)
		self.cbGaRepUntil.SetToolTip("")

		self.treGaResults = wx.TreeCtrl(id=-1, name="treGaResults", parent=self.panel, pos=wx.Point(0, 115), size=wx.Size(100, 100), style=wx.TR_DEFAULT_STYLE | wx.TR_HAS_BUTTONS, validator=wx.DefaultValidator)
		self.treGaResults.SetToolTip("")
		self.treGaResults.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnTregaaresultsTreeItemActivated, id=-1)

		self._init_selparam_sizers()

	def __init__(self, parent):
		self._init_selparam_ctrls(parent)

		self.prnt = parent

	def OnMiniFrameClose(self, event):
		self.Hide()

	def CountForOptCurve(self, curve):
		count = 0
		for i in range(len(curve)):
			if curve[i] != 0:
				count += 1
		return count

	def OnTregaaresultsTreeItemActivated(self, event):
		# define dfa or pls
		exec("self.chroms = self.prnt.data['ga" + self.prnt.type.lower() + "chroms']")
		exec("self.scores = self.prnt.data['ga" + self.prnt.type.lower() + "scores']")
		exec("self.curves = self.prnt.data['ga" + self.prnt.type.lower() + "curves']")

		# colours and markers for plotting
		markerList = ["circle", "square", "cross", "plus"]
		colourList = ["BLUE", "BROWN", "CYAN", "GREY", "GREEN", "MAGENTA", "ORANGE", "PURPLE", "VIOLET"]

		# set busy cursor
		##		  wx.BeginBusyCursor()

		if self.prnt.cbxData.GetSelection() == 0:
			xdata = self.prnt.data["raw"]
		elif self.prnt.cbxData.GetSelection() == 1:
			xdata = self.prnt.data["proc"]

		currentItem = event.GetItem()
		chromId = self.treGaResults.GetItemText(currentItem)
		chkValid = float(chromId.split("]")[1])
		chromId = chromId.split("[")[0]
		chromId = int(chromId.split("#")[1]) - 1
		currentChrom = self.chroms[chromId].tolist()
		self.currentChrom = currentChrom

		# Plot frequency of variable selection for no. vars
		# Get chrom data and error data for each child
		Chroms = []
		VarsId = self.treGaResults.GetItemParent(currentItem)
		NoVars = self.treGaResults.GetItemText(VarsId)
		NoVars = int(NoVars.split(" ")[0])

		# adjust chrom length if mutliple var subsets used
		currentChrom = currentChrom[0:NoVars]

		##		  if chkValid > 10.0**-5:
		# Re-Running DFA
		# set no. DFs
		if len(currentChrom) < int(self.spnGaMaxFac.GetValue()):
			Lvs = len(currentChrom)
		else:
			Lvs = int(self.spnGaMaxFac.GetValue())

		# run dfa
		if self.prnt.type in ["DFA"]:
			self.prnt.data["gadfadfscores"], self.prnt.data["gadfadfaloads"], gaError = mva.fitfun.rerun_dfa(currentChrom, xdata, self.prnt.data["validation"], self.prnt.data["class"], self.prnt.data["label"], Lvs)

			# plot scores
			self.prnt.spnGaScoreFrom.SetRange(1, self.prnt.data["gadfadfaloads"].shape[1])
			self.prnt.spnGaScoreFrom.SetValue(1)
			self.prnt.spnGaScoreTo.SetRange(1, self.prnt.data["gadfadfaloads"].shape[1])
			self.prnt.spnGaScoreTo.SetValue(1)
			if self.prnt.data["gadfadfaloads"].shape[1] > 1:
				self.prnt.spnGaScoreTo.SetValue(2)

			gaOrdPlot = plotText(self.prnt.parent.plcGaPlot, self.prnt.data["gadfadfscores"], self.prnt.data["validation"], self.prnt.data["class"], self.prnt.data["label"], self.prnt.spnGaScoreFrom.GetValue() - 1, self.prnt.spnGaScoreTo.GetValue() - 1, "", "Discriminant Function")

		if self.prnt.type in ["PLS"]:
			# select only chrom vars from x
			self.prnt.data["gaplsplsloads"], T, P, Q, facs, predy, predyv, predyt, RMSEC, RMSEPC, rmsec, rmsepc, RMSEPT = mva.fitfun.rerun_pls(currentChrom, xdata, np.array(self.prnt.data["class"])[:, nA], self.prnt.data["validation"][:, nA], Lvs)

			gaError = scipy.concatenate((np.array(rmsec)[nA, :], np.array(rmsepc)[nA, :]), 0)

			# plot pls model
			plsModel = PlotPlsModel(self, self.prnt.parent.plcGaPlot, np.array(self.prnt.data["class"])[:, nA], predy, predyv, predyt, self.prnt.data["validation"][:, nA], RMSEPT, Lvs)

		##			  if self.cbDfaSavePc.GetValue() is False:
		NoRuns = int(self.spnGaNoRuns.GetValue())
		##			  else:
		##				  tp = int((float(self.stDfaSavePc.GetValue())/100)*int(self.stDfaNoInds.GetValue()))
		##				  NoRuns = int(self.stDfaNoRuns.GetValue())*tp

		for runs in range(NoRuns):
			if runs == 0:
				ChildId = self.treGaResults.GetFirstChild(VarsId)[0]
			else:
				ChildId = self.treGaResults.GetNextSibling(ChildId)

			# get chrom ids
			itemId = self.treGaResults.GetItemText(ChildId)
			itemId = itemId.split("[")[0]
			itemId = int(itemId.split("#")[1]) - 1
			items = self.chroms[itemId][0:NoVars]
			for each in items:
				Chroms.append(each)

		# calculate variable frequencies
		VarFreq = scipy.zeros((1, 2), "i")
		while len(Chroms) > 1:
			VarFreq = scipy.concatenate((VarFreq, scipy.reshape([float(Chroms[0]), 1.0], (1, 2))), 0)
			NewChroms = []
			for i in range(1, len(Chroms), 1):
				if Chroms[i] == VarFreq[VarFreq.shape[0] - 1, 0]:
					VarFreq[VarFreq.shape[0] - 1, 1] += 1.0
				else:
					NewChroms.append(float(Chroms[i]))
			Chroms = NewChroms
		if len(Chroms) == 1:
			VarFreq = scipy.concatenate((VarFreq, scipy.reshape([float(Chroms[0]), 1.0], (1, 2))), 0)
		VarFreq = VarFreq[1 : VarFreq.shape[0]]

		# Plot var freq as percentage
		VarFreq[:, 1] = (VarFreq[:, 1] / sum(VarFreq[:, 1])) * 100
		# plot variable frequencies
		LineObj = []
		for i in range(VarFreq.shape[0]):
			Start = scipy.concatenate((scipy.reshape(self.prnt.data["xaxis"][int(VarFreq[i, 0])], (1, 1)), scipy.reshape(0.0, (1, 1))), 1)
			FullVarFreq = scipy.concatenate((scipy.reshape(self.prnt.data["xaxis"][int(VarFreq[i, 0])], (1, 1)), scipy.reshape(VarFreq[i, 1], (1, 1))), 1)
			FullVarFreq = scipy.concatenate((Start, FullVarFreq), 0)
			if int(VarFreq[i, 0]) in currentChrom:
				LineObj.append(wx.lib.plot.PolyLine(FullVarFreq, colour="red", width=2, style=wx.SOLID))
			else:
				LineObj.append(wx.lib.plot.PolyLine(FullVarFreq, colour="black", width=2, style=wx.SOLID))

		meanSpec = scipy.concatenate((scipy.reshape(self.prnt.data["xaxis"], (len(self.prnt.data["xaxis"]), 1)), scipy.reshape(mva.process.norm01(scipy.reshape(scipy.mean(xdata, 0), (1, xdata.shape[1]))) * max(VarFreq[:, 1]), (xdata.shape[1], 1))), 1)

		meanSpec = wx.lib.plot.PolyLine(meanSpec, colour="black", width=0.75, style=wx.SOLID)

		LineObj.append(meanSpec)

		DfaPlotFreq = wx.lib.plot.PlotGraphics(LineObj, "Frequency of Variable Selection", "Variable ID", "Frequency (%)")

		xAx = (self.prnt.data["xaxis"].min(), self.prnt.data["xaxis"].max())

		yAx = (0, max(VarFreq[:, 1]) * 1.1)

		self.prnt.parent.plcGaFreqPlot.Draw(DfaPlotFreq, xAxis=xAx, yAxis=yAx)

		##			  self.DfaPlotFreq = [DfaPlotFreq,xAx,yAx]

		# plot variables
		list = []
		for each in currentChrom:
			list.append(str(self.prnt.data["indlabels"][int(each)]))

		self.prnt.cbxFeature1.SetItems(list)
		self.prnt.cbxFeature2.SetItems(list)
		self.prnt.cbxFeature1.SetSelection(0)
		self.prnt.cbxFeature2.SetSelection(0)

		gaFeatPlot = self.PlotGaVariables(self.prnt.parent.plcGaFeatPlot)

		# plot ga optimisation curve
		noGens = self.CountForOptCurve(self.curves[chromId])
		gaPlotOptLine = plotLine(self.prnt.parent.plcGaOptPlot, scipy.reshape(self.curves[chromId, 0:noGens], (1, noGens)), scipy.arange(1, noGens + 1)[:, nA], 0, "GA Optimisation Curve", "Generation", "Objective function score")

		# plot loadings
		exec("drawGaLoad = self.plotGaLoads(currentChrom,self.prnt.data['ga" + self.prnt.type.lower() + self.prnt.type.lower() + "loads'],self.prnt.parent.plcGaSpecLoad,0)")

		# plot eigenvalues
		if gaError.shape[0] == 1:
			errorCurve = plotLine(self.prnt.parent.plcGaEigs, gaError, scipy.arange(1, gaError.shape[0] + 1)[:, nA], 0, "", "Eigenvalues", "Discriminant Function")
		else:
			errorCurve = plotLine(self.prnt.parent.plcGaEigs, gaError, scipy.arange(1, gaError.shape[1] + 1)[:, nA], 0, "", "PLS Factor", "RMS Error", type="multi", ledge=["Train err", "Test err"])

			self.prnt.parent.nbGaModPlot.SetPageText(1, "Model Error")

		# plot variables vs. error for pairs
		gaVarFrom = int(self.spnGaVarsFrom.GetValue())
		gaVarTo = int(self.spnGaVarsTo.GetValue())
		if gaVarTo - gaVarFrom == 0:
			gaVarRange = 1
		else:
			gaVarRange = gaVarTo - gaVarFrom + 1

		VarErrObj = []
		MaxVarErr = 0
		MinVarErr = 0
		for vars in range(gaVarRange):
			VarErr = scipy.zeros((1, 2), "d")
			if vars == 0:
				gaRoot = self.treGaResults.GetRootItem()
				VarsId = self.treGaResults.GetFirstChild(gaRoot)[0]
			else:
				VarsId = self.treGaResults.GetNextSibling(VarsId)

			Var = self.treGaResults.GetItemText(VarsId)

			Var = Var.split(" ")[0]

			for runs in range(int(self.spnGaNoRuns.GetValue())):
				if runs == 0:
					RunsId = self.treGaResults.GetFirstChild(VarsId)[0]
				else:
					RunsId = self.treGaResults.GetNextSibling(RunsId)

				Run = self.treGaResults.GetItemText(RunsId)

				Run = Run.split(" ")

				Run = Run[len(Run) - 1]

				VarErr = scipy.concatenate((VarErr, scipy.reshape([float(Var), float(Run)], (1, 2))), 0)

			VarErr = VarErr[1 : VarErr.shape[0], :]

			if max(VarErr[:, 1]) > MaxVarErr:
				MaxVarErr = max(VarErr[:, 1])
			if min(VarErr[:, 1]) < MinVarErr:
				MinVarErr = min(VarErr[:, 1])

			# select marker shape and colour for pair
			VarErrObj.append(
				wx.lib.plot.PolyMarker(
					VarErr,
					legend=" ".join((str(Var), "vars")),
					colour=colourList[
						int(
							round(
								scipy.rand(
									1,
								)[0]
								* (len(colourList) - 1)
							)
						)
					],
					fillstyle=wx.SOLID,
					marker=markerList[
						int(
							round(
								scipy.rand(
									1,
								)[0]
								* (len(markerList) - 1)
							)
						)
					],
					size=1.5,
				)
			)

			gaPlotVarErr = wx.lib.plot.PlotGraphics(VarErrObj, "Fitness Summary	 ", "Total no. variables selected", "Fitness")

			Xax = (gaVarFrom - 0.25, gaVarTo + 0.25)

			Yax = (MinVarErr, MaxVarErr)

			self.prnt.parent.plcGaGrpDistPlot.Draw(gaPlotVarErr, xAxis=Xax, yAxis=Yax)

			##				  self.gaPlotVarErr = [gaPlotVarErr,Xax,Yax]

			# Enable ctrls
			self.prnt.spnGaScoreFrom.Enable(1)
			self.prnt.spnGaScoreTo.Enable(1)
			self.prnt.cbxFeature1.Enable(1)
			self.prnt.cbxFeature2.Enable(1)

	##		  else:
	##			  dlg = wx.MessageDialog(self, 'Model not valid - unable to calculate results',
	##				'Error!', wx.OK | wx.ICON_ERROR)
	##			  try:
	##				  dlg.ShowModal()
	##			  finally:
	##				  dlg.Destroy()
	##
	##		  #reset busy cursor
	##		  wx.EndBusyCursor()

	def PlotGaVariables(self, canvas):
		chrom = self.currentChrom

		pos1 = int(self.prnt.cbxFeature1.GetSelection())
		pos2 = int(self.prnt.cbxFeature2.GetSelection())
		var1 = int(self.prnt.cbxFeature1.GetCurrentSelection())
		var2 = int(self.prnt.cbxFeature2.GetCurrentSelection())
		xdata = self.prnt.data["raw"]

		if self.prnt.cbxData.GetSelection() == 1:
			xdata = self.prnt.data["proc"]

		if pos1 == pos2:
			coords = scipy.reshape(scipy.take(xdata, [var1], 1), (len(xdata), 1))
			L1 = "Dummy"
			L2 = str(self.prnt.data["indlabels"][int(chrom[pos1])])

			DrawGaVars = plotText(canvas, coords, self.prnt.data["validation"], self.prnt.data["class"], self.prnt.data["label"], 0, 0, "", "Variable", xL=L1, yL=L2)
		else:
			coords = scipy.reshape(scipy.take(xdata, [var1, var2], 1), (len(xdata), 2))
			L1 = str(self.prnt.data["indlabels"][int(chrom[pos1])])
			L2 = str(self.prnt.data["indlabels"][int(chrom[pos2])])

			DrawGaVars = plotText(canvas, coords, self.prnt.data["validation"], self.prnt.data["class"], self.prnt.data["label"], 0, 1, "", "Variable", xL=L1, yL=L2)

		return DrawGaVars

	def plotGaLoads(self, chrom, loads, canvas, loadCol, width=4, xLabel="Variable"):
		# this width thing is a fix to allow for plotting of GA vars and also
		# PCA & DFA loadings using stem
		if width == 4:
			plotVals = scipy.concatenate((scipy.take(self.prnt.data["xaxis"], chrom)[:, nA], scipy.reshape(loads[:, loadCol], (len(loads), 1))), 1)
		else:
			plotVals = scipy.concatenate((scipy.take(self.prnt.data["xaxis"], chrom)[:, nA], scipy.reshape(scipy.transpose(loads)[:, loadCol], (loads.shape[1], 1))), 1)

		if self.prnt.spnGaScoreFrom.GetValue() != self.prnt.spnGaScoreTo.GetValue():
			plotOut = plotText(canvas, loads, scipy.zeros((len(loads), 1)), None, plotVals[:, 0], self.prnt.spnGaScoreFrom.GetValue() - 1, self.prnt.spnGaScoreTo.GetValue() - 1, "DF Loadings", "DF Loading", 0)
		else:
			plotOut = plotStem(canvas, plotVals, "", xLabel, "", width)

		return plotOut
