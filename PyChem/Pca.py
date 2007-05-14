# Boa:FramePanel:Pca

import os
import string

import scipy

import wx
import wx.lib.agw.buttonpanel as bp
import wx.lib.buttons
import wx.lib.plot
from scipy import newaxis as nA
from wx.lib.anchors import LayoutAnchors

from . import chemometrics
from .chemometrics import _index

[
	wxID_PCA,
	wxID_PCAPLCPCALOADSV,
	wxID_PCAPLCPCASCORE,
	wxID_PCAPLCPCEIGS,
	wxID_PCAPLCPCVAR,
] = [wx.NewIdRef() for _init_ctrls in range(5)]

[
	ID_RUNPCA,
	ID_EXPORTPCA,
	ID_PCATYPE,
	ID_SPNPCS,
	ID_NUMPCS1,
	ID_NUMPCS2,
] = [wx.NewIdRef() for _init_btnpanel_ctrls in range(6)]

[
	wxID_WXEXPORTDIALOG,
	wxID_WXEXPORTDIALOGBTNBROWSE,
	wxID_WXEXPORTDIALOGBTNCANCEL,
	wxID_WXEXPORTDIALOGBTNOK,
	wxID_WXEXPORTDIALOGCBEXPEIGS,
	wxID_WXEXPORTDIALOGCBEXPPCLOADS,
	wxID_WXEXPORTDIALOGCBEXPPERVAR,
	wxID_WXEXPORTDIALOGCBEXPSCORES,
	wxID_WXEXPORTDIALOGSTHCLUSTER,
	wxID_WXEXPORTDIALOGTCSAVEPCABROWSE,
	wxID_WXEXPORTDIALOGWDPCAEXPORT,
] = [wx.NewIdRef() for _init_export_ctrls in range(11)]


def errorBox(window, error):
	dlg = wx.MessageDialog(window, "".join(("The following error occured:\n\n", error)), "Error!", wx.OK | wx.ICON_ERROR)
	try:
		dlg.ShowModal()
	finally:
		dlg.Destroy()


def plotLine(plotCanvas, plotArr, xaxis, rownum, tit, xLabel, yLabel, type="single", ledge=[]):
	colourList = ["BLACK", "RED", "BLUE", "BROWN", "CYAN", "GREY", "GREEN", "MAGENTA", "ORANGE", "PURPLE", "VIOLET"]
	if type == "single":
		pA = plotArr[rownum, 0 : len(xaxis)]
		pA = pA[:, nA]
		Line = wx.lib.plot.PolyLine(scipy.concatenate((xaxis, pA), 1), colour="black", width=2, style=wx.SOLID)
		NewplotLine = wx.lib.plot.PlotGraphics([Line], tit, xLabel, yLabel)
	elif type == "multi":
		ColourCount = 0
		Line = []
		for i in range(plotArr.shape[0]):
			pA = plotArr[i]
			pA = pA[:, nA]
			Line.append(wx.lib.plot.PolyLine(scipy.concatenate((xaxis, pA), 1), legend=ledge[i], colour=colourList[ColourCount], width=1, style=wx.SOLID))
			ColourCount += 1
			if ColourCount == len(colourList):
				ColourCount == 0
		NewplotLine = wx.lib.plot.PlotGraphics(Line, tit, xLabel, yLabel)

	contx = 0.1 * abs(xaxis.min())
	conty = 0.1 * abs(plotArr.min())
	PlXaxis = (xaxis.min() - contx, xaxis.max() + contx)
	PlYaxis = (plotArr.min() - conty, plotArr.max() + conty)

	plotCanvas.Draw(NewplotLine, PlXaxis, PlYaxis)

	return [NewplotLine, PlXaxis, PlYaxis]


def plotStem(plotCanvas, plotArr, tit="", xLabel="", yLabel="", stemWidth=3):
	# plotArr is an n x 2 array
	plotStem = []
	for i in range(plotArr.shape[0]):
		newCoords = np.array([[plotArr[i, 0], 0], [plotArr[i, 0], plotArr[i, 1]]])
		plotStem.append(wx.lib.plot.PolyLine(newCoords, colour="black", width=stemWidth, style=wx.SOLID))

	plotStem.append(wx.lib.plot.PolyLine(np.array([[plotArr[0, 0] - (0.1 * plotArr[0, 0]), 0], [plotArr[len(plotArr) - 1, 0] + (0.1 * plotArr[0, 0]), 0]]), colour="black", width=1, style=wx.SOLID))

	plotStem = wx.lib.plot.PlotGraphics(plotStem, tit, xLabel, yLabel)

	plotCanvas.Draw(plotStem)


def plotText(plotCanvas, coords, mask, cLass, text, col1, col2, tit, axis, usemask=1, xL=None, yL=None):
	# sort out axis labels
	if (xL is not None) and (yL is not None) is True:
		xL = " ".join((axis, xL))
		yL = " ".join((axis, yL))
	else:
		xL = " ".join((axis, str(col1 + 1)))
		yL = " ".join((axis, str(col2 + 1)))

	# make label text
	nt = []
	for i in range(len(text)):
		nt.append(str(text[i]))
	text = nt

	plotText = []
	colours = ["black", "blue", "red"]
	if usemask == 1:
		colRange = 3
	else:
		colRange = 1

	# set text colour - black=train, blue=val, red=test
	for getColour in range(colRange):
		idx = _index(mask, getColour)

		if (coords.shape[1] > 1) & (col1 != col2) is True:
			# plot 2d
			plotText.append(wx.lib.plot.PolyMarker(scipy.take(scipy.take(coords, [col1, col2], 1), idx, 0), marker="text", labels=scipy.take(text, idx, 0), text_colour=colours[getColour]))
		else:
			# plot 1d
			plotText.append(wx.lib.plot.PolyMarker(scipy.take(scipy.concatenate((np.array(cLass)[:, nA], scipy.take(coords, [col1], 1)), 1), idx, 0), marker="text", labels=scipy.take(text, idx, 0), text_colour=colours[getColour]))

	if (coords.shape[1] > 1) & (col1 != col2) is True:
		draw_plotText = wx.lib.plot.PlotGraphics(plotText, tit, xLabel=xL, yLabel=yL)
		contx = 0.2 * abs(min(coords[:, col1]))
		conty = 0.2 * abs(min(coords[:, col2]))
		plotTextXaxis = (min(coords[:, col1]) - contx, max(coords[:, col1]) + contx)
		plotTextYaxis = (min(coords[:, col2]) - conty, max(coords[:, col2]) + conty)

	else:
		draw_plotText = wx.lib.plot.PlotGraphics(plotText, tit, xLabel="Class", yLabel=yL)
		plotTextXaxis = (min(cLass), max(cLass))
		plotTextYaxis = (min(coords[:, col1]), max(coords[:, col1]))

	plotCanvas.Draw(draw_plotText)  # ,xAxis=plotTextXaxis,yAxis=plotTextYaxis)

	return [draw_plotText, plotTextXaxis, plotTextYaxis]


class Pca(wx.Panel):
	# principal components analysis
	def _init_coll_grsPca1_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.plcPCAscore, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.plcPcaLoadsV, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.plcPCvar, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.plcPCeigs, 0, border=0, flag=wx.EXPAND)

	def _init_coll_bxsPca1_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.bxsPca2, 1, border=0, flag=wx.EXPAND)

	def _init_coll_bxsPca2_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.titleBar, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.grsPca1, 1, border=0, flag=wx.EXPAND)

	def _init_sizers(self):
		# generated method, don't edit
		self.bxsPca1 = wx.BoxSizer(orient=wx.HORIZONTAL)

		self.bxsPca2 = wx.BoxSizer(orient=wx.VERTICAL)

		self.grsPca1 = wx.GridSizer(cols=2, hgap=2, rows=2, vgap=2)

		self._init_coll_bxsPca1_Items(self.bxsPca1)
		self._init_coll_bxsPca2_Items(self.bxsPca2)
		self._init_coll_grsPca1_Items(self.grsPca1)

		self.SetSizer(self.bxsPca1)

	def _init_ctrls(self, prnt):
		# generated method, don't edit
		wx.Panel.__init__(self, id=wxID_PCA, name="Pca", parent=prnt, pos=wx.Point(-12, 22), size=wx.Size(1024, 599), style=wx.TAB_TRAVERSAL)
		self.SetClientSize(wx.Size(1016, 565))
		self.SetBackgroundColour(wx.Colour(167, 167, 243))
		self.SetAutoLayout(True)
		self.SetToolTip("")

		self.plcPCeigs = wx.lib.plot.PlotCanvas(id=-1, name="plcPCeigs", parent=self, pos=wx.Point(589, 283), size=wx.Size(20, 20), style=0)
		self.plcPCeigs.SetToolTip("")
		self.plcPCeigs.fontSizeTitle = 10
		self.plcPCeigs.enableZoom = True
		self.plcPCeigs.fontSizeAxis = 8
		##		  self.plcPCeigs.SetEnablePointLabel(True)
		self.plcPCeigs.SetConstraints(LayoutAnchors(self.plcPCeigs, False, True, False, True))
		self.plcPCeigs.fontSizeLegend = 8
		self.plcPCeigs.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))
		self.plcPCeigs.Bind(wx.EVT_RIGHT_DOWN, self.OnPlcPCeigsRightDown, id=-1)

		self.plcPCvar = wx.lib.plot.PlotCanvas(id=-1, name="plcPCvar", parent=self, pos=wx.Point(176, 283), size=wx.Size(20, 20), style=0)
		self.plcPCvar.fontSizeAxis = 8
		self.plcPCvar.fontSizeTitle = 10
		self.plcPCvar.enableZoom = True
		self.plcPCvar.SetToolTip("")
		##		  self.plcPCvar.SetEnablePointLabel(True)
		self.plcPCvar.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))
		self.plcPCvar.fontSizeLegend = 8
		self.plcPCvar.Bind(wx.EVT_RIGHT_DOWN, self.OnPlcPCvarRightDown, id=-1)

		self.plcPCAscore = wx.lib.plot.PlotCanvas(id=wxID_PCA - 1, name="plcPCAscore", parent=self, pos=wx.Point(0, 24), size=wx.Size(20, 20), style=0)
		self.plcPCAscore.fontSizeTitle = 10
		self.plcPCAscore.fontSizeAxis = 8
		self.plcPCAscore.enableZoom = True
		self.plcPCAscore.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "MS Sans Serif"))
		self.plcPCAscore.SetToolTip("")
		self.plcPCAscore.fontSizeLegend = 8
		##		  self.plcPCAscore.SetEnablePointLabel(True)
		self.plcPCAscore.Bind(wx.EVT_RIGHT_DOWN, self.OnPlcPCAscoreRightDown, id=wxID_PCA - 1)

		self.plcPcaLoadsV = wx.lib.plot.PlotCanvas(id=wxID_PCA - 1, name="plcPcaLoadsV", parent=self, pos=wx.Point(0, 24), size=wx.Size(20, 20), style=0)
		self.plcPcaLoadsV.SetToolTip("")
		self.plcPcaLoadsV.fontSizeTitle = 10
		self.plcPcaLoadsV.enableZoom = True
		self.plcPcaLoadsV.fontSizeAxis = 8
		##		  self.plcPcaLoadsV.SetEnablePointLabel(True)
		self.plcPcaLoadsV.fontSizeLegend = 8
		self.plcPcaLoadsV.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))
		self.plcPcaLoadsV.Bind(wx.EVT_RIGHT_DOWN, self.OnPlcPcaLoadsVRightDown, id=wxID_PCA - 1)

		self.titleBar = TitleBar(self, id=-1, text="Principal Components Analysis", style=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self._init_sizers()

	def __init__(self, parent, id, pos, size, style, name):
		self._init_ctrls(parent)

		self.parent = parent

	def OnPlcPCeigsRightDown(self, event):
		event.Skip()

	def OnPlcPCAscoreRightDown(self, event):
		event.Skip()

	def OnPlcPcaLoadsVRightDown(self, event):
		event.Skip()

	def OnPlcPCvarRightDown(self, event):
		event.Skip()

	def Reset(self):
		self.titleBar.spnNumPcs1.Enable(0)
		self.titleBar.spnNumPcs2.Enable(0)
		self.titleBar.spnNumPcs1.SetValue(1)
		self.titleBar.spnNumPcs2.SetValue(2)

		objects = {"plcPCeigs": ["Eigenvalues", "Principal Component", "Eigenvalue"], "plcPCvar": ["Percentage Explained Variance", "Principal Component", "Cumulative % Variance"], "plcPCAscore": ["PCA Model", "PC 1", "PC 2"], "plcPcaLoadsV": ["PCA Loading", "Arbitrary", "Arbitrary"]}
		curve = wx.lib.plot.PolyLine([[0, 0], [1, 1]], colour="white", width=1, style=wx.TRANSPARENT)

		for each in list(objects.keys()):
			exec("self." + each + ".Draw(wx.lib.plot.PlotGraphics([curve]," + 'objects["' + each + '"][0],' + 'objects["' + each + '"][1],' + 'objects["' + each + '"][2]))')


class TitleBar(bp.ButtonPanel):
	def _init_btnpanel_ctrls(self, prnt):
		bp.ButtonPanel.__init__(self, parent=prnt, id=-1, text="Principal Components Analysis", agwStyle=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self.btnRunPCA = wx.lib.buttons.GenButton(id=ID_RUNPCA, label="Run", name="btnRunPCA", parent=self, pos=wx.Point(8, 288), size=wx.Size(60, 23), style=0)
		self.btnRunPCA.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "MS Sans Serif"))
		self.btnRunPCA.SetToolTip("")
		self.btnRunPCA.Enable(False)
		self.btnRunPCA.SetBackgroundColour(wx.Colour(167, 167, 243))
		self.btnRunPCA.Bind(wx.EVT_BUTTON, self.OnBtnRunPCAButton, id=ID_RUNPCA)

		self.btnExportPcaResults = wx.Button(id=ID_EXPORTPCA, label="Export", name="btnExportPcaResults", parent=self, pos=wx.Point(8, 328), size=wx.Size(60, 23), style=0)
		self.btnExportPcaResults.SetToolTip("")
		self.btnExportPcaResults.Enable(False)
		self.btnExportPcaResults.SetBackgroundColour(wx.Colour(167, 167, 243))
		self.btnExportPcaResults.Bind(wx.EVT_BUTTON, self.OnBtnExportPcaResultsButton, id=ID_EXPORTPCA)

		self.cbxData = wx.Choice(choices=["Raw spectra", "Processed spectra"], id=-1, name="cbxData", parent=self, pos=wx.Point(118, 23), size=wx.Size(100, 23), style=0)
		self.cbxData.SetSelection(0)

		self.cbxPcaType = wx.Choice(choices=["NIPALS", "SVD"], id=-1, name="cbxPcaType", parent=self, pos=wx.Point(56, 23), size=wx.Size(64, 23), style=0)
		self.cbxPcaType.Bind(wx.EVT_COMBOBOX, self.OnCbxPcaType, id=ID_PCATYPE)
		self.cbxPcaType.SetSelection(0)

		self.cbxPreprocType = wx.Choice(
			choices=["Correlation matrix", "Covariance matrix"],
			id=-1,
			name="cbxPreprocType",
			parent=self,
			pos=wx.Point(118, 23),
			size=wx.Size(110, 23),
			style=0,
		)
		self.cbxPreprocType.SetSelection(0)

		self.spnPCAnum = wx.SpinCtrl(id=ID_SPNPCS, initial=3, max=100, min=3, name="spnPCAnum", parent=self, pos=wx.Point(112, 158), size=wx.Size(46, 23), style=wx.SP_ARROW_KEYS)
		self.spnPCAnum.SetToolTip("")
		self.spnPCAnum.SetValue(3)
		self.spnPCAnum.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "MS Sans Serif"))

		self.spnNumPcs1 = wx.SpinCtrl(id=ID_NUMPCS1, initial=1, max=100, min=1, name="spnNumPcs1", parent=self, pos=wx.Point(240, 184), size=wx.Size(46, 23), style=wx.SP_ARROW_KEYS)
		self.spnNumPcs1.Enable(0)
		self.spnNumPcs1.Bind(wx.EVT_SPINCTRL, self.OnSpnNumPcs1, id=-1)

		self.spnNumPcs2 = wx.SpinCtrl(id=ID_NUMPCS2, initial=2, max=100, min=2, name="spnNumPcs2", parent=self, pos=wx.Point(240, 184), size=wx.Size(46, 23), style=wx.SP_ARROW_KEYS)
		self.spnNumPcs2.Enable(0)
		self.spnNumPcs2.Bind(wx.EVT_SPINCTRL, self.OnSpnNumPcs2, id=-1)

	def __init__(self, parent, id, text, style, alignment):

		self._init_btnpanel_ctrls(parent)

		self.parent = parent

		self.CreateButtons()

	def CreateButtons(self):
		self.Freeze()

		self.SetProperties()

		self.AddControl(self.cbxData)
		self.AddControl(self.cbxPreprocType)
		self.AddSeparator()
		self.AddControl(self.cbxPcaType)
		self.AddControl(self.spnPCAnum)
		self.AddControl(self.btnRunPCA)
		self.AddSeparator()
		self.AddControl(wx.StaticText(self, -1, "PC "))
		self.AddControl(self.spnNumPcs1)
		self.AddControl(wx.StaticText(self, -1, " vs. "))
		self.AddControl(self.spnNumPcs2)
		self.AddSeparator()
		self.AddControl(self.btnExportPcaResults)

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

	def OnBtnRunPCAButton(self, event):
		self.runPca()

	def OnBtnExportPcaResultsButton(self, event):
		dlg = wxExportDialog(self)
		try:
			dlg.ShowModal()
			if dlg.GetButtonEvent() == 1:
				if dlg.GetPath() is None:
					dlg = wx.MessageDialog(self, "Please select directory", "Error!", wx.OK | wx.ICON_ERROR)
					try:
						dlg.ShowModal()
					finally:
						dlg.Destroy()
				else:
					dlg.SaveScores(self.data["pcscores"])
					dlg.SaveLoadings(scipy.transpose(self.data["pcloads"]))
					dlg.SaveEigs(self.data["pceigs"])
					dlg.SavePerVar(self.data["pcpervar"])
		finally:
			dlg.Destroy()

	def OnCbxPcaType(self, event):
		if self.cbxPcaType.GetValue() == 1:
			self.spnPCAnum.Enable(0)
		else:
			self.spnPCAnum.Enable(1)

	def getData(self, data):
		self.data = data

	def runPca(self):
		# Run principal components analysis
		##		  try:
		self.spnNumPcs1.Enable(1)
		self.spnNumPcs2.Enable(1)
		self.spnNumPcs1.SetValue(1)
		self.spnNumPcs2.SetValue(2)

		if self.cbxData.GetSelection() == 0:
			xdata = self.data["rawtrunc"]
			self.data["pcadata"] = "rawtrunc"
		elif self.cbxData.GetSelection() == 1:
			xdata = self.data["proctrunc"]
			self.data["pcadata"] = "proctrunc"

		if self.cbxPreprocType.GetSelection() == 0:
			self.data["pcatype"] = "covar"
		elif self.cbxPreprocType.GetSelection() == 1:
			self.data["pcatype"] = "corr"

		if self.cbxPcaType.GetSelection() == 1:
			# run PCA using SVD
			self.data["pcscores"], self.data["pcloads"], self.data["pcpervar"], self.data["pceigs"] = chemometrics.PCA_SVD(xdata, self.data["pcatype"])

			self.data["pcscores"] = self.data["pcscores"][:, 0 : len(self.data["pceigs"])]

			self.data["pcloads"] = self.data["pcloads"][0 : len(self.data["pceigs"]), :]

			self.data["niporsvd"] = "svd"

		elif self.cbxPcaType.GetSelection() == 0:
			# run PCA using NIPALS
			self.data["pcscores"], self.data["pcloads"], self.data["pcpervar"], self.data["pceigs"] = chemometrics.PCA_NIPALS(xdata, self.spnPCAnum.GetValue(), self.data["pcatype"], self.parent.parent.parent.sbMain)

			self.data["niporsvd"] = "nip"

		# Enable ctrls
		self.btnExportPcaResults.Enable(1)
		self.spnNumPcs1.SetRange(1, len(self.data["pceigs"]))
		self.spnNumPcs1.SetValue(1)
		self.spnNumPcs2.SetRange(1, len(self.data["pceigs"]))
		self.spnNumPcs2.SetValue(2)

		# plot results
		self.PlotPca()

	##		  except Exception, error:
	##			  errorBox(self,'%s' %str(error))
	##
	def PlotPca(self):

		##		  if (sum(self.data['class']) != 0) and (self.data['class'] is not None):
		##			  self.rbDfaRawData.SetValue(0)
		##			  self.rbDfaProcData.SetValue(0)
		##			  self.rbDFAusepcscores.Enable(1)
		##			  self.rbDFAusepcscores.SetValue(1)
		##			  self.spnDFApcs.Enable(1)
		##			  self.staticText23.Enable(1)
		##			  self.spnDFApcs.SetRange(2, len(self.PCeigs))
		##			  self.spnDFAdfs.SetRange(1, int(max(self.data['class']))-1)
		##			  self.rbUsePCscores.Enable(1)

		# Plot loadings
		self.plotPcaLoads()

		# Plot scores
		self.plotPcaScores()

		# Plot % variance
		self.DrawPcaVar = plotLine(self.parent.plcPCvar, scipy.transpose(self.data["pcpervar"]), scipy.arange(0, len(self.data["pcpervar"]))[:, nA], 0, "Percentage Explained Variance", "Principal Component", "Cumulative % Variance")

		# Plot eigenvalues
		self.DrawPCeigs = plotLine(self.parent.plcPCeigs, scipy.transpose(self.data["pceigs"]), scipy.arange(1, len(self.data["pceigs"]) + 1)[:, nA], 0, "Eigenvalues", "Principal Component", "Eigenvalue")

	def plotPcaLoads(self):
		if self.spnNumPcs1.GetValue() != self.spnNumPcs2.GetValue():
			self.DrawPcaLoadsV = plotText(self.parent.plcPcaLoadsV, scipy.transpose(self.data["pcloads"]), self.data["validation"], self.data["class"], self.data["indlabels"], self.spnNumPcs1.GetValue() - 1, self.spnNumPcs2.GetValue() - 1, "Principal Component Loadings", "PC Loading", 0)
		else:
			idx = self.spnNumPcs1.GetValue() - 1
			self.DrawPcaLoadsV = plotStem(self.parent.plcPcaLoadsV, scipy.concatenate((scipy.arange(1, self.data["pcloads"].shape[1] + 1)[:, nA], self.data["pcloads"][idx, :][:, nA]), 1), "Principal Component Loadings", "Variable", "PC Loading " + str(idx + 1))

	def plotPcaScores(self):
		self.DrawPcaScore = plotText(self.parent.plcPCAscore, self.data["pcscores"], self.data["validation"], self.data["class"], self.data["label"], self.spnNumPcs1.GetValue() - 1, self.spnNumPcs2.GetValue() - 1, "Principal Component Scores", "PC", 0)

	def OnSpnNumPcs1(self, event):
		self.plotPcaScores()
		self.plotPcaLoads()

	def OnSpnNumPcs2(self, event):
		self.plotPcaScores()
		self.plotPcaLoads()


class wxExportDialog(wx.Dialog):
	def _init_export_ctrls(self, prnt):
		# generated method, don't edit
		wx.Dialog.__init__(self, id=wxID_WXEXPORTDIALOG, name="wx.ExportDialog", parent=prnt, pos=wx.Point(530, 255), size=wx.Size(220, 220), style=wx.DEFAULT_DIALOG_STYLE, title="Export Results")
		self.SetClientSize(wx.Size(220, 220))
		self.SetToolTip("")
		self.Center(wx.BOTH)

		self.wdPcaExport = wx.Window(id=wxID_WXEXPORTDIALOGWDPCAEXPORT, name="wdPcaExport", parent=self, pos=wx.Point(0, 0), size=wx.Size(228, 254), style=wx.TAB_TRAVERSAL)
		self.wdPcaExport.SetToolTip("")

		self.cbExpScores = wx.CheckBox(id=wxID_WXEXPORTDIALOGCBEXPSCORES, label="Export principal component scores", name="cbExpScores", parent=self.wdPcaExport, pos=wx.Point(16, 56), size=wx.Size(184, 13), style=0)
		self.cbExpScores.SetValue(False)
		self.cbExpScores.SetToolTip("")

		self.tcSavePcaBrowse = wx.TextCtrl(id=wxID_WXEXPORTDIALOGTCSAVEPCABROWSE, name="tcSavePcaBrowse", parent=self.wdPcaExport, pos=wx.Point(16, 16), size=wx.Size(112, 21), style=0, value="")
		self.tcSavePcaBrowse.SetToolTip("")

		self.btnBrowse = wx.Button(id=wxID_WXEXPORTDIALOGBTNBROWSE, label="Browse...", name="btnBrowse", parent=self.wdPcaExport, pos=wx.Point(136, 16), size=wx.Size(75, 23), style=0)
		self.btnBrowse.SetToolTip("")
		self.btnBrowse.Bind(wx.EVT_BUTTON, self.OnBtnBrowseButton, id=wxID_WXEXPORTDIALOGBTNBROWSE)

		self.cbExpEigs = wx.CheckBox(id=wxID_WXEXPORTDIALOGCBEXPEIGS, label="Export eigenvalues", name="cbExpEigs", parent=self.wdPcaExport, pos=wx.Point(16, 120), size=wx.Size(192, 13), style=0)
		self.cbExpEigs.SetValue(False)
		self.cbExpEigs.SetToolTip("")

		self.cbExpPerVar = wx.CheckBox(id=wxID_WXEXPORTDIALOGCBEXPPERVAR, label="Export cumulative % variance", name="cbExpPerVar", parent=self.wdPcaExport, pos=wx.Point(16, 152), size=wx.Size(192, 13), style=0)
		self.cbExpPerVar.SetValue(False)
		self.cbExpPerVar.SetToolTip("")

		self.cbExpPcLoads = wx.CheckBox(id=wxID_WXEXPORTDIALOGCBEXPPCLOADS, label="Export principal component loadings", name="cbExpPcLoads", parent=self.wdPcaExport, pos=wx.Point(16, 88), size=wx.Size(200, 13), style=0)
		self.cbExpPcLoads.SetValue(False)
		self.cbExpPcLoads.SetToolTip("")

		self.btnOK = wx.Button(id=wxID_WXEXPORTDIALOGBTNOK, label="OK", name="btnOK", parent=self.wdPcaExport, pos=wx.Point(16, 184), size=wx.Size(75, 23), style=0)
		self.btnOK.SetToolTip("")
		self.btnOK.Bind(wx.EVT_BUTTON, self.OnBtnOKButton, id=wxID_WXEXPORTDIALOGBTNOK)

		self.btnCancel = wx.Button(id=wxID_WXEXPORTDIALOGBTNCANCEL, label="Cancel", name="btnCancel", parent=self.wdPcaExport, pos=wx.Point(128, 184), size=wx.Size(75, 23), style=0)
		self.btnCancel.SetToolTip("")
		self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancelButton, id=wxID_WXEXPORTDIALOGBTNCANCEL)

		self.stHcluster = wx.StaticText(id=wxID_WXEXPORTDIALOGSTHCLUSTER, label="The dendrogram will be saved as Hcluster.cdt & Hcluster.gtr in a format suitable for display using Alok Saldanhas Java TreeView program (http://genome-www.stanford.edu)", name="stHcluster", parent=self.wdPcaExport, pos=wx.Point(16, 80), size=wx.Size(183, 72), style=0)
		self.stHcluster.Show(False)

	def __init__(self, parent, type="PCA"):
		self._init_export_ctrls(parent)
		self.Path = None

		if type == "PCA":
			self.cbExpScores.SetLabel("Export principal component scores")
			self.cbExpPcLoads.SetLabel("Export principal component loadings")
			self.cbExpEigs.SetLabel("Export eigenvalues")
			self.cbExpPerVar.SetLabel("Export cumulative % variance")
			self.stHcluster.Show(0)
			self.scoresave = "PCscores.txt"
			self.loadsave = "PCloadings.txt"
			self.eigsave = "PCeigenvalues.txt"
			self.explvar = "PCexplvar.txt"
		if type == "DFA":
			self.cbExpScores.SetLabel("Export discriminant function scores")
			self.cbExpPcLoads.SetLabel("Export discriminant function loadings")
			self.cbExpEigs.SetLabel("Export eigenvalues")
			self.cbExpPerVar.Show(0)
			self.stHcluster.Show(0)
			self.scoresave = "DFscores.txt"
			self.loadsave = "DFloadings.txt"
			self.eigsave = "DFeigenvalues.txt"
		if type == "PLS":
			self.cbExpScores.SetLabel("Export PLS model")
			self.cbExpPcLoads.SetLabel("Export PLS loadings")
			self.cbExpEigs.SetLabel("Export PLS error")
			self.cbExpPerVar.Show(0)
			self.stHcluster.Show(0)
			self.scoresave = "PLSmodel.txt"
			self.loadsave = "PLSloadings.txt"
			self.eigsave = "PLSerror.txt"
		if type == "HCLUSTER":
			self.stHcluster.Show(1)
			self.cbExpScores.SetLabel("Save HCA outputs")
			self.cbExpScores.SetValue(1)
			self.cbExpPcLoads.Show(0)
			self.cbExpEigs.Show(0)
			self.cbExpPerVar.Show(0)
		if type == "GA":
			self.cbExpScores.SetLabel("Export chromosomes")
			self.cbExpPcLoads.SetLabel("Export fitness scores")
			self.cbExpEigs.SetLabel("Export opt. curves")
			self.cbExpPerVar.Show(0)
			self.stHcluster.Show(0)
			self.scoresave = "chroms.txt"
			self.loadsave = "scores.txt"
			self.eigsave = "curves.txt"

	def OnBtnBrowseButton(self, event):
		dlg = wx.DirDialog(self)
		try:
			if dlg.ShowModal() == wx.ID_OK:
				dir = dlg.GetPath()
				self.tcSavePcaBrowse.SetValue(dir)
				self.Path = dir
		finally:
			dlg.Destroy()

	def OnBtnOKButton(self, event):
		self.OK = 1
		self.Close()

	def OnBtnCancelButton(self, event):
		self.OK = 0
		self.Close()

	def GetButtonEvent(self):
		return self.OK

	def SaveScores(self, scores):
		if self.cbExpScores.GetValue() == 1:
			f = file(os.path.join(self.Path, self.scoresave), "w")
			scipy.io.write_array(f, scores)
			f.close()

	def SaveLoadings(self, loadings):
		if self.cbExpPcLoads.GetValue() == 1:
			f = file(os.path.join(self.Path, self.loadsave), "w")
			scipy.io.write_array(f, loadings)
			f.close()

	def SaveEigs(self, eigs):
		if self.cbExpEigs.GetValue() == 1:
			f = file(os.path.join(self.Path, self.eigsave), "w")
			scipy.io.write_array(f, eigs)
			f.close()

	def SavePerVar(self, pervar):
		if self.cbExpPerVar.GetValue() == 1:
			f = file(os.path.join(self.Path, self.explvar), "w")
			scipy.io.write_array(f, pervar)
			f.close()

	def GetPath(self):
		return self.Path

	def CreateVarList(self, num):
		list = []
		for i in range(num):
			list.append(str(i + 1))
		return list

	def SaveHcluster(self, path, xdata, names, expid, clusters, linkdist):
		Bio.Cluster.data.writeclusterfiles(join((path, "//Hcluster"), ""), scipy.transpose(xdata), self.CreateVarList(xdata.shape[1]), expid, mask=None, geneclusters=scipy.zeros((xdata.shape[1], 2), "l"), genelinkdist=scipy.zeros((xdata.shape[1],), "d"), expclusters=np.array(clusters, "l"), explinkdist=linkdist)
