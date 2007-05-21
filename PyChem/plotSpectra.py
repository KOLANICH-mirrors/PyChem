# Boa:FramePanel:plotSpectra

import copy
import string

import scipy
import wx
import wx.lib.agw.buttonpanel as bp
import wx.lib.plot
from wx.lib.anchors import LayoutAnchors

from . import process
from .Pca import MyPlotCanvas

[IDPLOTSPEC] = [wx.NewIdRef() for _init_ctrls in range(1)]

[
	wxID_SELFUN,
	wxID_SELFUNBTNSPECTRADELETE,
	wxID_SELFUNBTNSPECTRADOWN,
	wxID_SELFUNBTNSPECTRARESET,
	wxID_SELFUNBTNSPECTRAUP,
	wxID_SELFUNLBSPECTRA1,
	wxID_SELFUNLBSPECTRA2,
] = [wx.NewIdRef() for _init_selfun_ctrls in range(7)]


def errorBox(window, error):
	dlg = wx.MessageDialog(window, "".join(("The following error occured:\n\n", error)), "Error!", wx.OK | wx.ICON_ERROR)
	try:
		dlg.ShowModal()
	finally:
		dlg.Destroy()


class plotSpectra(wx.Panel):
	def _init_coll_grsPspc1_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.plcSpectraRaw, 0, border=0, flag=wx.EXPAND)

	def _init_coll_bxsPspc1_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.bxsPspc2, 1, border=0, flag=wx.EXPAND)

	def _init_coll_bxsPspc2_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.titleBar, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.grsPspc1, 1, border=0, flag=wx.EXPAND)

	def _init_sizers(self):
		# generated method, don't edit
		self.bxsPspc1 = wx.BoxSizer(orient=wx.HORIZONTAL)

		self.bxsPspc2 = wx.BoxSizer(orient=wx.VERTICAL)

		self.grsPspc1 = wx.GridSizer(cols=1, hgap=2, rows=1, vgap=2)

		self._init_coll_bxsPspc1_Items(self.bxsPspc1)
		self._init_coll_bxsPspc2_Items(self.bxsPspc2)
		self._init_coll_grsPspc1_Items(self.grsPspc1)

		self.SetSizer(self.bxsPspc1)

	def _init_ctrls(self, prnt):
		# generated method, don't edit
		wx.Panel.__init__(self, id=-1, name="plotSpectra", parent=prnt, pos=wx.Point(88, 116), size=wx.Size(757, 538), style=wx.TAB_TRAVERSAL)
		self.SetClientSize(wx.Size(749, 504))
		self.SetBackgroundColour(wx.Colour(167, 167, 243))
		self.SetToolTip("")
		self.SetAutoLayout(True)

		self.plcSpectraRaw = MyPlotCanvas(id=IDPLOTSPEC, name="plcSpectraRaw", parent=self, pos=wx.Point(272, 0), size=wx.Size(20, 20), style=0)
		self.plcSpectraRaw.enableZoom = True
		self.plcSpectraRaw.fontSizeTitle = 12
		self.plcSpectraRaw.SetToolTip("")
		self.plcSpectraRaw.fontSizeAxis = 10
		self.plcSpectraRaw.SetConstraints(LayoutAnchors(self.plcSpectraRaw, True, True, True, True))
		self.plcSpectraRaw.SetAutoLayout(True)

		self.titleBar = TitleBar(self, id=-1, text="Spectral Preprocessing", style=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT, canvasList=[self.plcSpectraRaw])

		self._init_sizers()

	def __init__(self, parent, id, pos, size, style, name):
		self._init_ctrls(parent)

		self.parent = parent

	def Reset(self):
		curve = wx.lib.plot.PolyLine([[0, 0], [1, 1]], colour="white", width=1, style=wx.TRANSPARENT)
		curve = wx.lib.plot.PlotGraphics([curve], "Experimental Data", "Arbitrary", "Arbitrary")
		self.plcSpectraRaw.Draw(curve)


class TitleBar(bp.ButtonPanel):
	def _init_btnpanel_ctrls(self, prnt):
		bp.ButtonPanel.__init__(self, parent=prnt, id=-1, text="Spectral Preprocessing", agwStyle=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self.btnSetProc = wx.Button(id=-1, label="Select Functions", name="btnPlotRaw", parent=self, pos=wx.Point(6, 584), size=wx.Size(92, 23), style=0)
		self.btnSetProc.SetToolTip("")
		self.btnSetProc.Bind(wx.EVT_BUTTON, self.OnBtnSetProcButton, id=-1)

		self.btnPlotRaw = wx.Button(id=-1, label="Plot", name="btnPlotRaw", parent=self, pos=wx.Point(6, 584), size=wx.Size(75, 23), style=0)
		self.btnPlotRaw.SetToolTip("")
		self.btnPlotRaw.Enable(False)
		self.btnPlotRaw.Bind(wx.EVT_BUTTON, self.OnBtnPlotRawButton, id=-1)

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

		self.dlg = selFun(self)

	def CreateButtons(self):
		self.Freeze()

		self.SetProperties()

		self.AddControl(self.btnSetProc)
		self.AddControl(self.cbxData)
		self.AddControl(self.cbxNumber)
		self.AddControl(self.spcPlotSpectra)
		self.AddControl(self.btnPlotRaw)

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
		bpArt.SetColor(bp.BP_SELECTION_BRUSH_COLOUR, wx.Colour(167, 167, 243))  # wx.Colour(242, 242, 235))
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
				self.data["proc"] = process.norm01(self.data["proc"])
			elif each == 4:
				self.data["proc"] = process.normhigh(self.data["proc"])
			elif each == 5:
				self.data["proc"] = process.normtot(self.data["proc"])
			elif each == 6:
				self.data["proc"] = process.meancent(self.data["proc"])
			elif each == 7:
				self.data["proc"] = process.autoscale(self.data["proc"])
			elif each == 8:
				self.data["proc"] = scipy.transpose(process.autoscale(scipy.transpose(self.data["proc"])))
			elif each == 11:
				self.data["proc"] = process.avgfilt(self.data["proc"], 3, "c")
			elif each == 12:
				self.data["proc"] = process.avgfilt(self.data["proc"], 4, "c")
			elif each == 13:
				self.data["proc"] = process.avgfilt(self.data["proc"], 5, "c")
			elif each == 14:
				self.data["proc"] = process.avgfilt(self.data["proc"], 6, "c")
			elif each == 15:
				self.data["proc"] = process.avgfilt(self.data["proc"], 7, "c")
			elif each == 16:
				self.data["proc"] = process.avgfilt(self.data["proc"], 8, "c")
			elif each == 17:
				self.data["proc"] = process.avgfilt(self.data["proc"], 9, "c")
			elif each == 18:
				self.data["proc"] = process.avgfilt(self.data["proc"], 10, "c")
			elif each == 21:
				self.data["proc"] = process.baseline1(self.data["proc"])
			elif each == 22:
				self.data["proc"] = process.baseline2(self.data["proc"])
			elif each == 23:
				self.data["proc"] = process.lintrend(self.data["proc"])
			elif each == 26:
				self.data["proc"] = process.derivlin(self.data["proc"], 3)
			elif each == 27:
				self.data["proc"] = process.derivlin(self.data["proc"], 4)
			elif each == 28:
				self.data["proc"] = process.derivlin(self.data["proc"], 5)
			elif each == 29:
				self.data["proc"] = process.derivlin(self.data["proc"], 6)
			elif each == 30:
				self.data["proc"] = process.derivlin(self.data["proc"], 7)
			elif each == 31:
				self.data["proc"] = process.derivlin(self.data["proc"], 8)
			elif each == 32:
				self.data["proc"] = process.derivlin(self.data["proc"], 9)
			elif each == 33:
				self.data["proc"] = process.derivlin(self.data["proc"], 10)

		self.parent.parent.parent.GetExperimentDetails()

	def OnBtnSetProcButton(self, event):
		height = wx.GetDisplaySize()[1]
		self.dlg.SetSize(wx.Size(250, height))
		self.dlg.SetPosition(wx.Point(0, 0))
		self.dlg.Iconize(False)
		self.dlg.Show()

	def getData(self, data):
		self.data = data
		self.dlg.getData(data)

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

			xAx = (min(min(xaxis)), max(max(xaxis)))
			yAx = (array.min(), array.max())
			self.canvas.Draw(DrawSpecPlot)  # ,xAx,yAx)
			self.DrawSpecPlot = [DrawSpecPlot, xAx, yAx]


class selFun(wx.Frame):
	def _init_coll_gbsSelfun_Growables(self, parent):
		# generated method, don't edit

		parent.AddGrowableRow(1)
		parent.AddGrowableRow(3)
		parent.AddGrowableCol(0)
		parent.AddGrowableCol(1)

	def _init_coll_gbsSelfun_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(wx.StaticText(self, -1, "Select Function", style=wx.ALIGN_LEFT), (0, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.lbSpectra1, (1, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(wx.StaticText(self, -1, "Preprocessing Steps", style=wx.ALIGN_LEFT), (2, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.lbSpectra2, (3, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.btnSpectraUp, (4, 0), border=2, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.btnSpectraDown, (4, 1), border=2, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.btnSpectraDelete, (5, 0), border=2, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.btnSpectraReset, (5, 1), border=2, flag=wx.EXPAND, span=(1, 1))

	def _init_selparam_sizers(self):
		# generated method, don't edit
		self.gbsSelfun = wx.GridBagSizer(hgap=4, vgap=4)
		self.gbsSelfun.SetCols(2)
		self.gbsSelfun.SetRows(6)
		self.gbsSelfun.SetMinSize(wx.Size(100, 439))
		self.gbsSelfun.SetEmptyCellSize(wx.Size(0, 0))

		self._init_coll_gbsSelfun_Items(self.gbsSelfun)
		self._init_coll_gbsSelfun_Growables(self.gbsSelfun)

		self.SetSizer(self.gbsSelfun)

	def _init_selfun_ctrls(self, prnt):
		# generated method, don't edit
		wx.Frame.__init__(self, id=wxID_SELFUN, name="selFun", parent=prnt, pos=wx.Point(22, 29), size=wx.Size(180, 500), style=wx.DEFAULT_FRAME_STYLE, title="Pre-processing Functions")
		self.SetClientSize(wx.Size(269, 466))
		self.SetBackgroundColour(wx.Color(167, 167, 243))
		self.Center(wx.BOTH)
		self.SetToolTip("")
		self.Bind(wx.EVT_CLOSE, self.OnMiniFrameClose)

		self.lbSpectra1 = wx.ListBox(choices=["", "Scaling", "	Normalise to 0 for min, +1 for max.", "  Normalise max. bin to +1", "	Normalise to total", "	Mean centre", "	 Column normalisation", "  Row normalisation", "", "Filtering", "  Linear mean filter, frame width 3", "  Linear mean filter, frame width 4", "	 Linear mean filter, frame width 5", "	Linear mean filter, frame width 6", "  Linear mean filter, frame width 7", "  Linear mean filter, frame width 8", "	 Linear mean filter, frame width 9", "	Linear mean filter, frame width 10", "", "Baseline Correction", "  Set first bin to zero", "  Subtract average of first and last bin", "  Subtract a linearly increasing baseline", "", "Derivatisation", "	 Linear derivatisation, frame width 3", "  Linear derivatisation, frame width 4", "	 Linear derivatisation, frame width 5", "  Linear derivatisation, frame width 6", "	 Linear derivatisation, frame width 7", "  Linear derivatisation, frame width 8", "	 Linear derivatisation, frame width 9", "  Linear derivatisation, frame width 10", ""], id=wxID_SELFUNLBSPECTRA1, name="lbSpectra1", parent=self, pos=wx.Point(6, 8), size=wx.Size(170, 296), style=wx.HSCROLL, validator=wx.DefaultValidator)
		self.lbSpectra1.SetToolTip("")
		self.lbSpectra1.Show(True)
		self.lbSpectra1.SetLabel("Pre-processing Functions")
		self.lbSpectra1.Bind(wx.EVT_LISTBOX_DCLICK, self.OnLbspectra1ListboxDclick, id=wxID_SELFUNLBSPECTRA1)

		self.lbSpectra2 = wx.ListBox(choices=[], id=wxID_SELFUNLBSPECTRA2, name="lbSpectra2", parent=self, pos=wx.Point(6, 312), size=wx.Size(170, 112), style=wx.HSCROLL, validator=wx.DefaultValidator)
		self.lbSpectra2.SetToolTip("")

		self.btnSpectraUp = wx.Button(id=wxID_SELFUNBTNSPECTRAUP, label="Up", name="btnSpectraUp", parent=self, pos=wx.Point(6, 434), size=wx.Size(48, 23), style=0)
		self.btnSpectraUp.SetToolTip("Move up")
		self.btnSpectraUp.Bind(wx.EVT_BUTTON, self.OnBtnspectraupButton, id=wxID_SELFUNBTNSPECTRAUP)

		self.btnSpectraDelete = wx.Button(id=wxID_SELFUNBTNSPECTRADELETE, label="Del", name="btnSpectraDelete", parent=self, pos=wx.Point(144, 434), size=wx.Size(48, 23), style=0)
		self.btnSpectraDelete.SetToolTip("Delete selected function")
		self.btnSpectraDelete.Bind(wx.EVT_BUTTON, self.OnBtnspectradeleteButton, id=wxID_SELFUNBTNSPECTRADELETE)

		self.btnSpectraDown = wx.Button(id=wxID_SELFUNBTNSPECTRADOWN, label="Down", name="btnSpectraDown", parent=self, pos=wx.Point(76, 434), size=wx.Size(48, 23), style=0)
		self.btnSpectraDown.SetToolTip("Move down")
		self.btnSpectraDown.Bind(wx.EVT_BUTTON, self.OnBtnspectradownButton, id=wxID_SELFUNBTNSPECTRADOWN)

		self.btnSpectraReset = wx.Button(id=wxID_SELFUNBTNSPECTRARESET, label="Reset", name="btnSpectraReset", parent=self, pos=wx.Point(216, 434), size=wx.Size(46, 23), style=0)
		self.btnSpectraReset.SetToolTip("Reset")
		self.btnSpectraReset.Bind(wx.EVT_BUTTON, self.OnBtnspectraresetButton, id=wxID_SELFUNBTNSPECTRARESET)

		self._init_selparam_sizers()

	def __init__(self, parent):
		self._init_selfun_ctrls(parent)

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

	def OnMiniFrameClose(self, event):
		self.Hide()
