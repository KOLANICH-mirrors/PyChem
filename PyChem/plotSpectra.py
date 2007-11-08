# -----------------------------------------------------------------------------
# Name:		   plotSpectra.py
# Purpose:
#
# Author:	   Roger Jarvis
#
# Created:	   2007/05/22
# RCS-ID:	   $Id$
# Copyright:   (c) 2007
# Licence:	   GNU General Public Licence
# -----------------------------------------------------------------------------
# Boa:FramePanel:plotSpectra

import copy
import os
import string

import scipy
import wx
import wx.lib.agw.buttonpanel as bp
import wx.lib.agw.foldpanelbar as fpb
import wx.lib.plot
from wx.lib.anchors import LayoutAnchors

from .mva import process
from .Pca import MyPlotCanvas

[IDPLOTSPEC] = [wx.NewIdRef() for _init_ctrls in range(1)]


def errorBox(window, error):
	dlg = wx.MessageDialog(window, "".join(("The following error occured:\n\n", error)), "Error!", wx.OK | wx.ICON_ERROR)
	try:
		dlg.ShowModal()
	finally:
		dlg.Destroy()


class plotSpectra(wx.Panel):
	def _init_coll_bxsPspc1_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.bxsPspc2, 1, border=0, flag=wx.EXPAND)

	def _init_coll_bxsPspc2_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.titleBar, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.Splitter, 1, border=0, flag=wx.EXPAND)

	def _init_sizers(self):
		# generated method, don't edit
		self.bxsPspc1 = wx.BoxSizer(orient=wx.HORIZONTAL)

		self.bxsPspc2 = wx.BoxSizer(orient=wx.VERTICAL)

		self._init_coll_bxsPspc1_Items(self.bxsPspc1)
		self._init_coll_bxsPspc2_Items(self.bxsPspc2)

		self.SetSizer(self.bxsPspc1)

	def _init_ctrls(self, prnt):
		# generated method, don't edit
		wx.Panel.__init__(self, id=-1, name="plotSpectra", parent=prnt, pos=wx.Point(88, 116), size=wx.Size(757, 538), style=wx.TAB_TRAVERSAL)
		self.SetClientSize(wx.Size(749, 504))
		self.SetToolTip("")
		self.SetAutoLayout(True)

		self.Splitter = wx.SplitterWindow(id=-1, name="Splitter", parent=self, pos=wx.Point(16, 24), size=wx.Size(272, 168), style=wx.SP_3D | wx.SP_LIVE_UPDATE)
		self.Splitter.SetAutoLayout(True)
		self.Splitter.Bind(wx.EVT_SPLITTER_DCLICK, self.OnSplitterDclick)

		self.p1 = wx.Panel(self.Splitter)
		self.p1.SetAutoLayout(True)
		self.p1.prnt = prnt

		self.optDlg = selFun(self.Splitter)

		self.plcSpectraRaw = MyPlotCanvas(id=IDPLOTSPEC, name="plcSpectraRaw", parent=self.p1, pos=wx.Point(0, 0), size=wx.Size(200, 200), style=wx.SUNKEN_BORDER, toolbar=self.p1.prnt.parent.tbMain)
		self.plcSpectraRaw.enableZoom = True
		self.plcSpectraRaw.fontSizeTitle = 12
		self.plcSpectraRaw.SetToolTip("")
		self.plcSpectraRaw.fontSizeAxis = 10
		self.plcSpectraRaw.SetConstraints(LayoutAnchors(self.plcSpectraRaw, True, True, True, True))

		self.titleBar = TitleBar(self, id=-1, text="Spectral Preprocessing", style=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT, canvasList=[self.plcSpectraRaw])

		self.Splitter.SplitVertically(self.optDlg, self.p1, 1)
		self.Splitter.SetMinimumPaneSize(1)

		self._init_sizers()

	def __init__(self, parent, id, pos, size, style, name):
		self._init_ctrls(parent)

		self.parent = parent

	def Reset(self):
		curve = wx.lib.plot.PolyLine([[0, 0], [1, 1]], colour="white", width=1, style=wx.TRANSPARENT)
		curve = wx.lib.plot.PlotGraphics([curve], "Experimental Data", "Arbitrary", "Arbitrary")
		self.plcSpectraRaw.Draw(curve)

		self.optDlg.lbSpectra2.Clear()

	def OnSplitterDclick(self, event):
		if self.Splitter.GetSashPosition() <= 5:
			self.Splitter.SetSashPosition(250)
		else:
			self.Splitter.SetSashPosition(1)


class TitleBar(bp.ButtonPanel):
	def _init_btnpanel_ctrls(self, prnt):
		bp.ButtonPanel.__init__(self, parent=prnt, id=-1, text="Spectral Preprocessing", agwStyle=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self.btnSetProc = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "params.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Select Preprocessing Options", longHelp="Select Preprocessing Options")
		self.Bind(wx.EVT_BUTTON, self.OnBtnSetProcButton, id=self.btnSetProc.GetId())

		self.btnPlotRaw = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "run.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Execute Plot", longHelp="Execute Plot")
		self.btnPlotRaw.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnPlotRawButton, id=self.btnPlotRaw.GetId())

		self.spcPlotSpectra = wx.SpinCtrl(id=-1, initial=1, max=100, min=1, name="spcPlotSpectra", parent=self, pos=wx.Point(198, 554), size=wx.Size(64, 23), style=wx.SP_ARROW_KEYS)
		self.spcPlotSpectra.SetToolTip("")
		self.spcPlotSpectra.SetValue(1)

		self.cbxData = wx.Choice(choices=["Raw spectra", "Processed spectra"], id=-1, name="cbxData", parent=self, pos=wx.Point(118, 23), size=wx.Size(100, 23), style=0)
		self.cbxData.SetSelection(0)

		self.cbxNumber = wx.Choice(choices=["Single spectrum", "All spectra"], id=-1, name="cbxNumber", parent=self, pos=wx.Point(118, 23), size=wx.Size(100, 23), style=0)
		self.cbxNumber.SetSelection(0)

	def __init__(self, parent, id, text, style, alignment, canvasList):

		self._init_btnpanel_ctrls(parent)

		self.CreateButtons()

		self.parent = parent

		self.canvas = canvasList[0]

	def CreateButtons(self):
		self.Freeze()

		self.SetProperties()

		self.AddControl(self.cbxData)
		self.AddControl(self.cbxNumber)
		self.AddControl(self.spcPlotSpectra)
		self.AddSeparator()
		self.AddButton(self.btnSetProc)
		self.AddSeparator()
		self.AddButton(self.btnPlotRaw)

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

	def OnBtnPlotRawButton(self, event):
		# Plot spectra
		# set busy cursor
		wx.BeginBusyCursor()
		# get xdata
		if self.cbxData.GetSelection() == 0:
			xdata = self.data["rawtrunc"]
			tit = "Raw"
		else:
			self.RunProcessingSteps()
			xdata = self.data["proctrunc"]
			tit = "Processed"

		# Plot xdata
		if self.cbxNumber.GetSelection() == 1:
			self.PlotSpectra(xdata, tit, self.data["xaxis"])
		elif self.cbxNumber.GetSelection() == 0:
			idx = self.spcPlotSpectra.GetValue() - 1
			self.PlotSpectra(scipy.reshape(xdata[idx], (1, xdata.shape[1])), tit, self.data["xaxis"])
		wx.EndBusyCursor()

	def RunProcessingSteps(self):
		# Run pre-processing
		self.data["proc"] = copy.deepcopy(self.data["raw"])
		for each in self.data["processlist"]:
			if each == 3:
				self.data["proc"] = mva.process.norm01(self.data["proc"])
			elif each == 4:
				self.data["proc"] = mva.process.normhigh(self.data["proc"])
			elif each == 5:
				self.data["proc"] = mva.process.normtot(self.data["proc"])
			elif each == 6:
				self.data["proc"] = mva.process.meancent(self.data["proc"])
			elif each == 7:
				self.data["proc"] = mva.process.autoscale(self.data["proc"])
			elif each == 8:
				self.data["proc"] = scipy.transpose(mva.process.autoscale(scipy.transpose(self.data["proc"])))
			elif each == 11:
				self.data["proc"] = mva.process.avgfilt(self.data["proc"], 3, "c")
			elif each == 12:
				self.data["proc"] = mva.process.avgfilt(self.data["proc"], 4, "c")
			elif each == 13:
				self.data["proc"] = mva.process.avgfilt(self.data["proc"], 5, "c")
			elif each == 14:
				self.data["proc"] = mva.process.avgfilt(self.data["proc"], 6, "c")
			elif each == 15:
				self.data["proc"] = mva.process.avgfilt(self.data["proc"], 7, "c")
			elif each == 16:
				self.data["proc"] = mva.process.avgfilt(self.data["proc"], 8, "c")
			elif each == 17:
				self.data["proc"] = mva.process.avgfilt(self.data["proc"], 9, "c")
			elif each == 18:
				self.data["proc"] = mva.process.avgfilt(self.data["proc"], 10, "c")
			elif each == 21:
				self.data["proc"] = mva.process.baseline1(self.data["proc"])
			elif each == 22:
				self.data["proc"] = mva.process.baseline2(self.data["proc"])
			elif each == 23:
				self.data["proc"] = mva.process.lintrend(self.data["proc"])
			elif each == 26:
				self.data["proc"] = mva.process.derivlin(self.data["proc"], 3)
			elif each == 27:
				self.data["proc"] = mva.process.derivlin(self.data["proc"], 4)
			elif each == 28:
				self.data["proc"] = mva.process.derivlin(self.data["proc"], 5)
			elif each == 29:
				self.data["proc"] = mva.process.derivlin(self.data["proc"], 6)
			elif each == 30:
				self.data["proc"] = mva.process.derivlin(self.data["proc"], 7)
			elif each == 31:
				self.data["proc"] = mva.process.derivlin(self.data["proc"], 8)
			elif each == 32:
				self.data["proc"] = mva.process.derivlin(self.data["proc"], 9)
			elif each == 33:
				self.data["proc"] = mva.process.derivlin(self.data["proc"], 10)

		self.parent.parent.parent.GetExperimentDetails()

	def OnBtnSetProcButton(self, event):
		if self.parent.Splitter.GetSashPosition() <= 5:
			self.parent.Splitter.SetSashPosition(250)
		else:
			self.parent.Splitter.SetSashPosition(1)

	def getData(self, data):
		self.data = data
		self.parent.optDlg.getData(data)

	def PlotSpectra(self, array, title, xaxis, type=0):
		compileSpecPlot, ColourCount, Count = [], 0, 0
		# get xaxis
		Shape = array.shape[1]
		specPlot = []

		colourList = ["BLUE", "BROWN", "CYAN", "GREY", "GREEN", "MAGENTA", "ORANGE", "PURPLE", "VIOLET"]

		if type == 0:
			while Count < array.shape[0]:
				tempArray = array[Count, :]
				specPlot = scipy.concatenate((scipy.reshape(xaxis, (len(xaxis), 1)), scipy.reshape(tempArray, (len(tempArray), 1))), 1)
				compileSpecPlot.append(wx.lib.plot.PolyLine(specPlot, colour=colourList[ColourCount], width=1, style=wx.SOLID))
				Count += 1
				ColourCount += 1
				if ColourCount == len(colourList):
					ColourCount = 0

			DrawSpecPlot = wx.lib.plot.PlotGraphics(compileSpecPlot, title, "Arbitrary", "Arbitrary")

			self.canvas.Draw(DrawSpecPlot)


class selFun(fpb.FoldPanelBar):
	def _init_coll_gbsSelfun_Growables(self, parent):
		# generated method, don't edit

		parent.AddGrowableRow(0)
		parent.AddGrowableCol(0)
		parent.AddGrowableCol(1)

	def _init_coll_gbsSelfun_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.lbSpectra2, (0, 0), flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.btnSpectraUp, (1, 0), flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.btnSpectraDown, (1, 1), flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.btnSpectraDelete, (2, 0), flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.btnSpectraReset, (2, 1), flag=wx.EXPAND, span=(1, 1))
		parent.AddSpacer(wx.Size(8, 8), (3, 0), flag=wx.EXPAND, span=(2, 2))

	def _init_selparam_sizers(self):
		# generated method, don't edit
		self.gbsSelfun = wx.GridBagSizer(5, 5)
		self.gbsSelfun.SetCols(2)
		self.gbsSelfun.SetRows(5)

		self._init_coll_gbsSelfun_Items(self.gbsSelfun)
		self._init_coll_gbsSelfun_Growables(self.gbsSelfun)

		self.fpSelected.SetSizer(self.gbsSelfun)

	def _init_selfun_ctrls(self, prnt):
		# generated method, don't edit
		fpb.FoldPanelBar.__init__(self, prnt, -1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=fpb.FPB_DEFAULT_STYLE | fpb.FPB_SINGLE_FOLD)
		self.SetConstraints(LayoutAnchors(self, True, True, True, True))
		self.SetAutoLayout(True)

		icons = wx.ImageList(16, 16)
		icons.Add(wx.Bitmap(os.path.join("bmp", "arrown.png"), wx.BITMAP_TYPE_PNG))
		icons.Add(wx.Bitmap(os.path.join("bmp", "arrows.png"), wx.BITMAP_TYPE_PNG))

		self.fpFunctions = self.AddFoldPanel("Preprocessing functions", collapsed=True, foldIcons=icons)
		self.fpFunctions.SetAutoLayout(True)

		self.fpSelected = self.AddFoldPanel("Selected functions", collapsed=True, foldIcons=icons)
		self.fpSelected.SetAutoLayout(True)
		##		  self.fpResults.Bind(wx.EVT_SIZE, self.OnFpbResize)

		self.plSelected = wx.Panel(id=-1, name="plSelected", parent=self.fpSelected, pos=wx.Point(0, 0), size=wx.Size(200, 350), style=wx.TAB_TRAVERSAL)
		self.plSelected.SetToolTip("")
		self.plSelected.SetConstraints(LayoutAnchors(self.plSelected, True, True, True, True))

		self.lbSpectra1 = wx.ListBox(choices=["", "Scaling", "	Normalise to 0 for min, +1 for max.", "  Normalise max. bin to +1", "	Normalise to total", "	Mean centre", "	 Column normalisation", "  Row normalisation", "", "Filtering", "  Linear mean filter, frame width 3", "  Linear mean filter, frame width 4", "	 Linear mean filter, frame width 5", "	Linear mean filter, frame width 6", "  Linear mean filter, frame width 7", "  Linear mean filter, frame width 8", "	 Linear mean filter, frame width 9", "	Linear mean filter, frame width 10", "", "Baseline Correction", "  Set first bin to zero", "  Subtract average of first and last bin", "  Subtract a linearly increasing baseline", "", "Derivatisation", "	 Linear derivatisation, frame width 3", "  Linear derivatisation, frame width 4", "	 Linear derivatisation, frame width 5", "  Linear derivatisation, frame width 6", "	 Linear derivatisation, frame width 7", "  Linear derivatisation, frame width 8", "	 Linear derivatisation, frame width 9", "  Linear derivatisation, frame width 10", ""], id=-1, name="lbSpectra1", parent=self.fpFunctions, pos=wx.Point(0, 23), size=wx.Size(250, 280), style=wx.HSCROLL, validator=wx.DefaultValidator)
		self.lbSpectra1.SetToolTip("")
		self.lbSpectra1.Bind(wx.EVT_LISTBOX_DCLICK, self.OnLbspectra1ListboxDclick)

		self.lbSpectra2 = wx.ListBox(choices=[], id=-1, name="lbSpectra2", parent=self.plSelected, pos=wx.Point(0, 0), size=wx.Size(250, 150), style=wx.HSCROLL, validator=wx.DefaultValidator)
		self.lbSpectra2.SetToolTip("")

		self.btnSpectraUp = wx.Button(id=-1, label="Up", name="btnSpectraUp", parent=self.plSelected, pos=wx.Point(0, 0), size=wx.Size(48, 23), style=0)
		self.btnSpectraUp.SetToolTip("Move up")
		self.btnSpectraUp.Bind(wx.EVT_BUTTON, self.OnBtnspectraupButton)

		self.btnSpectraDelete = wx.Button(id=-1, label="Del", name="btnSpectraDelete", parent=self.plSelected, pos=wx.Point(0, 0), size=wx.Size(48, 23), style=0)
		self.btnSpectraDelete.SetToolTip("Delete selected function")
		self.btnSpectraDelete.Bind(wx.EVT_BUTTON, self.OnBtnspectradeleteButton)

		self.btnSpectraDown = wx.Button(id=-1, label="Down", name="btnSpectraDown", parent=self.plSelected, pos=wx.Point(0, 0), size=wx.Size(48, 23), style=0)
		self.btnSpectraDown.SetToolTip("Move down")
		self.btnSpectraDown.Bind(wx.EVT_BUTTON, self.OnBtnspectradownButton)

		self.btnSpectraReset = wx.Button(id=-1, label="Reset", name="btnSpectraReset", parent=self.plSelected, pos=wx.Point(0, 0), size=wx.Size(46, 23), style=0)
		self.btnSpectraReset.SetToolTip("Reset")
		self.btnSpectraReset.Bind(wx.EVT_BUTTON, self.OnBtnspectraresetButton)

		self.AddFoldPanelWindow(self.fpFunctions, self.lbSpectra1, fpb.FPB_ALIGN_WIDTH)
		self.AddFoldPanelWindow(self.fpSelected, self.plSelected, fpb.FPB_ALIGN_WIDTH)

		self._init_selparam_sizers()

	def __init__(self, parent):
		self._init_selfun_ctrls(parent)

		self.Expand(self.fpFunctions)
		self.Expand(self.fpSelected)

	def getData(self, data):
		self.data = data

	def OnLbspectra1ListboxDclick(self, event):
		Selected = self.lbSpectra1.GetSelection()
		SelectedText = self.lbSpectra1.GetStringSelection()
		if SelectedText[0:2] == "  ":
			self.data["processlist"].append(Selected + 1)
			self.lbSpectra2.Append(SelectedText[2 : len(SelectedText)])

	def OnBtnspectraupButton(self, event):
		CurrentPos = self.lbSpectra2.GetSelection()
		if CurrentPos > 0:
			NewList = []
			NewProcessList = []
			for i in range(0, CurrentPos - 1):
				NewList.append(self.lbSpectra2.GetString(i))
				NewProcessList.append(self.data["processlist"][i])

			NewList.append(self.lbSpectra2.GetString(CurrentPos))
			NewList.append(self.lbSpectra2.GetString(CurrentPos - 1))
			NewProcessList.append(self.data["processlist"][CurrentPos])
			NewProcessList.append(self.data["processlist"][CurrentPos - 1])

			for i in range(CurrentPos + 1, self.lbSpectra2.GetCount()):
				NewList.append(self.lbSpectra2.GetString(i))
				NewProcessList.append(self.data["processlist"][i])

			self.data["processlist"] = NewProcessList
			self.lbSpectra2.Clear()
			for i in range(len(NewList)):
				self.lbSpectra2.Append(NewList[i])
			self.lbSpectra2.SetSelection(CurrentPos - 1)

	def OnBtnspectradeleteButton(self, event):
		if len(self.data["processlist"]) > 0:
			del self.data["processlist"][self.lbSpectra2.GetSelection()]
			self.lbSpectra2.Delete(self.lbSpectra2.GetSelection())
			if len(self.data["processlist"]) == 0:
				self.data["processlist"] = []
				self.data["proc"] = None

	def OnBtnspectradownButton(self, event):
		CurrentPos = self.lbSpectra2.GetSelection()
		if CurrentPos < self.lbSpectra2.GetCount() - 1:
			NewList = []
			NewProcessList = []
			if CurrentPos > 0:
				for i in range(0, CurrentPos):
					NewList.append(self.lbSpectra2.GetString(i))
					NewProcessList.append(self.data["processlist"][i])

			NewList.append(self.lbSpectra2.GetString(CurrentPos + 1))
			NewList.append(self.lbSpectra2.GetString(CurrentPos))
			NewProcessList.append(self.data["processlist"][CurrentPos + 1])
			NewProcessList.append(self.data["processlist"][CurrentPos])

			if CurrentPos + 2 <= self.lbSpectra2.GetCount() - 1:
				for i in range(CurrentPos + 2, self.lbSpectra2.GetCount()):
					NewList.append(self.lbSpectra2.GetString(i))
					NewProcessList.append(self.data["processlist"][i])

			self.ProcessList = NewProcessList
			self.lbSpectra2.Clear()
			for i in range(len(NewList)):
				self.lbSpectra2.Append(NewList[i])
			self.lbSpectra2.SetSelection(CurrentPos + 1)

	def OnBtnspectraresetButton(self, event):
		self.lbSpectra2.Clear()
		self.data["processlist"] = []
		self.data["proc"] = None
