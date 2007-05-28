# -----------------------------------------------------------------------------
# Name:		   Pca.py
# Purpose:
#
# Author:	   Roger Jarvis
#
# Created:	   2007/05/22
# RCS-ID:	   $Id$
# Copyright:   (c) 2007
# Licence:	   GNU General Public Licence
# -----------------------------------------------------------------------------
# Boa:FramePanel:Pca

import os
import string

import scipy

import wx
import wx.lib.agw.buttonpanel as bp
import wx.lib.buttons
import wx.lib.plot
import wx.lib.stattext
from scipy import newaxis as nA
from wx.lib.anchors import LayoutAnchors

from .mva import chemometrics
from .mva.chemometrics import _index
from .utils.io import str_array

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
	wxID_FRAME1,
	wxID_FRAME1BTNAPPLY,
	wxID_FRAME1CBGRID,
	wxID_FRAME1SPNFONTSIZEAXES,
	wxID_FRAME1SPNXMAX,
	wxID_FRAME1SPNXMIN,
	wxID_FRAME1SPNYMAX,
	wxID_FRAME1SPNYMIN,
	wxID_FRAME1STFONT,
	wxID_FRAME1STTITLE,
	wxID_FRAME1STXFROM,
	wxID_FRAME1STXLABEL,
	wxID_FRAME1STXTO,
	wxID_FRAME1STYFROM,
	wxID_FRAME1STYLABEL,
	wxID_FRAME1STYTO,
	wxID_FRAME1TXTTITLE,
	wxID_FRAME1TXTXLABEL,
	wxID_FRAME1TXTXMAX,
	wxID_FRAME1TXTXMIN,
	wxID_FRAME1TXTYLABEL,
	wxID_FRAME1TXTYMAX,
	wxID_FRAME1TXTYMIN,
] = [wx.NewIdRef() for _init_plot_prop_ctrls in range(23)]

[
	MNUPLOTCOPY,
	MNUPLOTPRINT,
	MNUPLOTSAVE,
	MNUPLOTPROPS,
] = [wx.NewIdRef() for _init_plot_menu_Items in range(4)]


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

	plotCanvas.Draw(NewplotLine)


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
		if colRange == 3:
			idx = _index(mask, getColour)
		else:
			idx = list(range(len(coords)))

		if (coords.shape[1] > 1) & (col1 != col2) is True:
			# plot 2d
			plotText.append(wx.lib.plot.PolyMarker(scipy.take(scipy.take(coords, [col1, col2], 1), idx, 0), marker="text", labels=scipy.take(text, idx, 0), text_colour=colours[getColour]))
		else:
			# plot 1d
			plotText.append(wx.lib.plot.PolyMarker(scipy.take(scipy.concatenate((np.array(cLass)[:, nA], scipy.take(coords, [col1], 1)), 1), idx, 0), marker="text", labels=scipy.take(text, idx, 0), text_colour=colours[getColour]))

	if (coords.shape[1] > 1) & (col1 != col2) is True:
		draw_plotText = wx.lib.plot.PlotGraphics(plotText, tit, xLabel=xL, yLabel=yL)
	else:
		draw_plotText = wx.lib.plot.PlotGraphics(plotText, tit, xLabel="Class", yLabel=yL)

	plotCanvas.Draw(draw_plotText)


class MyPlotCanvas(wx.lib.plot.PlotCanvas):
	def _init_plot_menu_Items(self, parent):

		parent.Append(help="", id=MNUPLOTCOPY, kind=wx.ITEM_NORMAL, text="Copy")
		parent.Append(help="", id=MNUPLOTPRINT, kind=wx.ITEM_NORMAL, text="Print")
		parent.Append(help="", id=MNUPLOTSAVE, kind=wx.ITEM_NORMAL, text="Save")
		parent.Append(help="", id=MNUPLOTPROPS, kind=wx.ITEM_NORMAL, text="Properties")
		self.Bind(wx.EVT_MENU, self.OnMnuPlotCopy, id=MNUPLOTCOPY)
		self.Bind(wx.EVT_MENU, self.OnMnuPlotPrint, id=MNUPLOTPRINT)
		self.Bind(wx.EVT_MENU, self.OnMnuPlotSave, id=MNUPLOTSAVE)
		self.Bind(wx.EVT_MENU, self.OnMnuPlotProperties, id=MNUPLOTPROPS)

	def _init_utils(self):
		self.plotMenu = wx.Menu(title="")

		self._init_plot_menu_Items(self.plotMenu)

	def __init__(self, parent, id, pos, size, style, name):
		wx.lib.plot.PlotCanvas.__init__(self, parent, id, pos, size, style, name)

		self._init_utils()

		self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)

	def OnMnuPlotCopy(self, event):
		# for winxp
		self.Redraw(wx.MetaFileDC()).SetClipboard()

		# for linux

	##		  wx.TheClipboard.Open()
	##		  wx.TheClipboard.SetData(self.Copy())
	##		  wx.TheClipboard.Close()

	def OnMnuPlotPrint(self, event):
		self.Printout()

	def OnMnuPlotSave(self, event):
		self.SaveFile()

	def OnMnuPlotProperties(self, event):
		height = wx.GetDisplaySize()[1]
		dlg = plotProperties(self)
		dlg.SetSize(wx.Size(250, height))
		dlg.SetPosition(wx.Point(0, 0))
		dlg.Iconize(False)
		dlg.Show()

	def OnMouseRightDown(self, event):
		pt = event.GetPosition()
		self.PopupMenu(self.plotMenu, pt)


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
		self.SetAutoLayout(True)
		self.SetToolTip("")

		self.plcPCeigs = MyPlotCanvas(id=-1, name="plcPCeigs", parent=self, pos=wx.Point(589, 283), size=wx.Size(20, 20), style=0)
		self.plcPCeigs.SetToolTip("")
		self.plcPCeigs.fontSizeTitle = 10
		self.plcPCeigs.enableZoom = True
		self.plcPCeigs.fontSizeAxis = 8
		self.plcPCeigs.SetConstraints(LayoutAnchors(self.plcPCeigs, False, True, False, True))
		self.plcPCeigs.fontSizeLegend = 8
		self.plcPCeigs.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))

		self.plcPCvar = MyPlotCanvas(id=-1, name="plcPCvar", parent=self, pos=wx.Point(176, 283), size=wx.Size(20, 20), style=0)
		self.plcPCvar.fontSizeAxis = 8
		self.plcPCvar.fontSizeTitle = 10
		self.plcPCvar.enableZoom = True
		self.plcPCvar.SetToolTip("")
		self.plcPCvar.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))
		self.plcPCvar.fontSizeLegend = 8

		self.plcPCAscore = MyPlotCanvas(parent=self, id=-1, name="plcPCAscore", pos=wx.Point(0, 24), size=wx.Size(20, 20), style=0)
		self.plcPCAscore.fontSizeTitle = 10
		self.plcPCAscore.fontSizeAxis = 8
		self.plcPCAscore.enableZoom = True
		self.plcPCAscore.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "MS Sans Serif"))
		self.plcPCAscore.SetToolTip("")
		self.plcPCAscore.fontSizeLegend = 8

		self.plcPcaLoadsV = MyPlotCanvas(id=-1, name="plcPcaLoadsV", parent=self, pos=wx.Point(0, 24), size=wx.Size(20, 20), style=0)
		self.plcPcaLoadsV.SetToolTip("")
		self.plcPcaLoadsV.fontSizeTitle = 10
		self.plcPcaLoadsV.enableZoom = True
		self.plcPcaLoadsV.fontSizeAxis = 8
		self.plcPcaLoadsV.fontSizeLegend = 8
		self.plcPcaLoadsV.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))

		self.titleBar = TitleBar(self, id=-1, text="Principal Components Analysis", style=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self._init_sizers()

	def __init__(self, parent, id, pos, size, style, name):
		self._init_ctrls(parent)

		self.parent = parent

	def Reset(self):
		self.titleBar.spnNumPcs1.Enable(0)
		self.titleBar.spnNumPcs2.Enable(0)
		self.titleBar.spnNumPcs1.SetValue(1)
		self.titleBar.spnNumPcs2.SetValue(2)

		objects = {"plcPCeigs": ["Eigenvalues", "Principal Component", "Eigenvalue"], "plcPCvar": ["Percentage Explained Variance", "Principal Component", "Cumulative % Variance"], "plcPCAscore": ["PCA Scores", "PC 1", "PC 2"], "plcPcaLoadsV": ["PCA Loading", "Arbitrary", "Arbitrary"]}
		curve = wx.lib.plot.PolyLine([[0, 0], [1, 1]], colour="white", width=1, style=wx.TRANSPARENT)

		for each in list(objects.keys()):
			exec("self." + each + ".Draw(wx.lib.plot.PlotGraphics([curve]," + 'objects["' + each + '"][0],' + 'objects["' + each + '"][1],' + 'objects["' + each + '"][2]))')


class TitleBar(bp.ButtonPanel):
	def _init_btnpanel_ctrls(self, prnt):
		bp.ButtonPanel.__init__(self, parent=prnt, id=-1, text="Principal Components Analysis", agwStyle=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)
		self.Bind(wx.EVT_PAINT, self.OnButtonPanelPaint)

		self.btnRunPCA = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "run.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Run PCA", longHelp="Run Principal Components Analysis")
		self.btnRunPCA.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnRunPCAButton, id=self.btnRunPCA.GetId())

		self.btnExportPcaResults = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "export.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Export PCA Results", longHelp="Export PCA Results")
		self.btnExportPcaResults.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnExportPcaResultsButton, id=self.btnExportPcaResults.GetId())

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
		self.AddControl(self.cbxPcaType)
		self.AddControl(wx.lib.stattext.GenStaticText(self, -1, "No. PCs:", style=wx.TRANSPARENT_WINDOW))
		self.AddControl(self.spnPCAnum)
		self.AddSeparator()
		self.AddControl(wx.lib.stattext.GenStaticText(self, -1, "PC", style=wx.TRANSPARENT_WINDOW))
		self.AddControl(self.spnNumPcs1)
		self.AddControl(wx.lib.stattext.GenStaticText(self, -1, " vs. ", style=wx.TRANSPARENT_WINDOW))
		self.AddControl(self.spnNumPcs2)
		self.AddSeparator()
		self.AddButton(self.btnRunPCA)
		self.AddSeparator()
		self.AddButton(self.btnExportPcaResults)

		self.Thaw()

		self.DoLayout()

	def OnButtonPanelPaint(self, event):
		event.Skip()

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

	def OnBtnRunPCAButton(self, event):
		self.runPca()

	def OnBtnExportPcaResultsButton(self, event):
		dlg = wx.FileDialog(self, "Choose a file", ".", "", "Any files (*.*)|*.*", wx.FD_SAVE)
		try:
			if dlg.ShowModal() == wx.ID_OK:
				saveFile = dlg.GetPath()
				out = "#PRINCIPAL_COMPONENT_SCORES\n" + str_array(self.data["pcscores"], col_sep="\t") + "\n" + "#PRINCIPAL_COMPONENT_LOADINGS\n" + str_array(self.data["pcloads"], col_sep="\t") + "\n" + "#EIGENVALUES\n" + str_array(self.data["pceigs"], col_sep="\t") + "\n" + "#CUMULATIVE_PERCENTAGE_EXPLAINED_VARIANCE\n" + str_array(self.data["pcpervar"], col_sep="\t") + "\n"
				f = file(saveFile, "w")
				f.write(out)
				f.close()
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
		try:
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
				self.data["pcscores"], self.data["pcloads"], self.data["pcpervar"], self.data["pceigs"] = mva.chemometrics.PCA_SVD(xdata, self.data["pcatype"])

				self.data["pcscores"] = self.data["pcscores"][:, 0 : len(self.data["pceigs"])]

				self.data["pcloads"] = self.data["pcloads"][0 : len(self.data["pceigs"]), :]

				self.data["niporsvd"] = "svd"

			elif self.cbxPcaType.GetSelection() == 0:
				# run PCA using NIPALS
				self.data["pcscores"], self.data["pcloads"], self.data["pcpervar"], self.data["pceigs"] = mva.chemometrics.PCA_NIPALS(xdata, self.spnPCAnum.GetValue(), self.data["pcatype"], self.parent.parent.parent.sbMain)

				self.data["niporsvd"] = "nip"

			# Enable ctrls
			self.btnExportPcaResults.Enable(1)
			self.spnNumPcs1.SetRange(1, len(self.data["pceigs"]))
			self.spnNumPcs1.SetValue(1)
			self.spnNumPcs2.SetRange(1, len(self.data["pceigs"]))
			self.spnNumPcs2.SetValue(2)

			# plot results
			self.PlotPca()

		except Exception as error:
			errorBox(self, "%s" % str(error))

	def PlotPca(self):
		try:
			# check for metadata & setup limits for dfa
			if (sum(self.data["class"]) != 0) and (self.data["class"] is not None):
				self.parent.parent.parent.plDfa.titleBar.cbxData.SetSelection(0)
				self.parent.parent.parent.plDfa.titleBar.spnDfaPcs.SetRange(2, len(self.data["pceigs"]))
				self.parent.parent.parent.plDfa.titleBar.spnDfaDfs.SetRange(1, int(max(self.data["class"])) - 1)

			# Plot loadings
			self.plotPcaLoads()

			# Plot scores
			self.plotPcaScores()

			# Plot % variance
			plotLine(self.parent.plcPCvar, scipy.transpose(self.data["pcpervar"]), scipy.arange(0, len(self.data["pcpervar"]))[:, nA], 0, "Percentage Explained Variance", "Principal Component", "Cumulative % Variance")

			# Plot eigenvalues
			plotLine(self.parent.plcPCeigs, scipy.transpose(self.data["pceigs"]), scipy.arange(1, len(self.data["pceigs"]) + 1)[:, nA], 0, "Eigenvalues", "Principal Component", "Eigenvalue")
		except:
			pass

	##		  except Exception, error:
	##			  errorBox(self,'%s' %str(error))

	def plotPcaLoads(self):
		if self.spnNumPcs1.GetValue() != self.spnNumPcs2.GetValue():
			plotText(self.parent.plcPcaLoadsV, scipy.transpose(self.data["pcloads"]), self.data["validation"], self.data["class"], self.data["indlabels"], self.spnNumPcs1.GetValue() - 1, self.spnNumPcs2.GetValue() - 1, "Principal Component Loadings", "PC Loading", 0)
		else:
			idx = self.spnNumPcs1.GetValue() - 1
			plotStem(self.parent.plcPcaLoadsV, scipy.concatenate((scipy.arange(1, self.data["pcloads"].shape[1] + 1)[:, nA], self.data["pcloads"][idx, :][:, nA]), 1), "Principal Component Loadings", "Variable", "PC Loading " + str(idx + 1))

	def plotPcaScores(self):
		plotText(self.parent.plcPCAscore, self.data["pcscores"], self.data["validation"], self.data["class"], self.data["label"], self.spnNumPcs1.GetValue() - 1, self.spnNumPcs2.GetValue() - 1, "Principal Component Scores", "PC", 0)

		# Annotate axes with % expl. variance
		xLabel = self.parent.plcPCAscore.last_draw[0].getXLabel()
		yLabel = self.parent.plcPCAscore.last_draw[0].getYLabel()
		xLabel = xLabel + " (" + "%.2f" % (self.data["pcpervar"][self.spnNumPcs1.GetValue()] - self.data["pcpervar"][self.spnNumPcs1.GetValue() - 1]) + "%)"
		yLabel = yLabel + " (" + "%.2f" % (self.data["pcpervar"][self.spnNumPcs2.GetValue()] - self.data["pcpervar"][self.spnNumPcs2.GetValue() - 1]) + "%)"
		self.parent.plcPCAscore.last_draw[0].setXLabel(xLabel)
		self.parent.plcPCAscore.last_draw[0].setYLabel(yLabel)
		self.parent.plcPCAscore.Redraw()

	def OnSpnNumPcs1(self, event):
		self.PlotPca()

	def OnSpnNumPcs2(self, event):
		self.PlotPca()


class plotProperties(wx.Frame):
	def _init_coll_gbsPlotProps_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.stTitle, (0, 0), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.txtTitle, (0, 1), border=4, flag=wx.EXPAND, span=(1, 5))
		parent.AddWindow(self.stFont, (1, 0), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.spnFontSizeAxes, (1, 1), border=4, flag=wx.EXPAND, span=(1, 5))
		parent.AddWindow(self.stXlabel, (2, 0), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.txtXlabel, (2, 1), border=4, flag=wx.EXPAND, span=(1, 5))
		parent.AddWindow(self.stYlabel, (3, 0), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.txtYlabel, (3, 1), border=4, flag=wx.EXPAND, span=(1, 5))
		parent.AddWindow(self.stXfrom, (4, 0), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.txtXmin, (4, 1), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.spnXmin, (4, 2), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.stXto, (4, 3), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.txtXmax, (4, 4), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.spnXmax, (4, 5), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.stYfrom, (5, 0), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.txtYmin, (5, 1), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.spnYmin, (5, 2), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.stYto, (5, 3), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.txtYmax, (5, 4), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.spnYmax, (5, 5), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.cbGrid, (6, 0), border=4, flag=wx.EXPAND, span=(1, 6))
		parent.AddWindow(self.btnApply, (7, 0), border=4, flag=wx.EXPAND, span=(1, 6))

	def _init_coll_gbsPlotProps_Growables(self, parent):
		# generated method, don't edit

		parent.AddGrowableCol(0)
		parent.AddGrowableCol(1)
		parent.AddGrowableCol(2)
		parent.AddGrowableCol(3)
		parent.AddGrowableCol(4)
		parent.AddGrowableCol(5)

	def _init_plot_prop_sizers(self):
		# generated method, don't edit
		self.gbsPlotProps = wx.GridBagSizer(hgap=4, vgap=10)
		self.gbsPlotProps.SetCols(6)
		self.gbsPlotProps.SetRows(6)
		self.gbsPlotProps.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
		self.gbsPlotProps.SetMinSize(wx.Size(250, 439))
		self.gbsPlotProps.SetEmptyCellSize(wx.Size(0, 0))
		self.gbsPlotProps.SetFlexibleDirection(wx.HORIZONTAL)

		self._init_coll_gbsPlotProps_Items(self.gbsPlotProps)
		self._init_coll_gbsPlotProps_Growables(self.gbsPlotProps)

		self.panel.SetSizer(self.gbsPlotProps)

	def _init_plot_prop_ctrls(self, prnt):
		# generated method, don't edit
		wx.Frame.__init__(self, id=wxID_FRAME1, name="", parent=prnt, pos=wx.Point(0, 0), size=wx.Size(250, 466), style=wx.DEFAULT_FRAME_STYLE, title="Plot Properties")

		self.panel = wx.Panel(id=-1, name="panel", parent=self, pos=wx.Point(0, 0), size=wx.Size(180, 739), style=wx.TAB_TRAVERSAL)
		self.panel.SetToolTip("")

		self.stTitle = wx.StaticText(id=wxID_FRAME1STTITLE, label="Title", name="stTitle", parent=self.panel, pos=wx.Point(0, 0), size=wx.Size(40, 24), style=0)
		self.stTitle.SetToolTip("")

		self.stYfrom = wx.StaticText(id=wxID_FRAME1STYFROM, label="Y-Axis From:", name="stYfrom", parent=self.panel, pos=wx.Point(0, 131), size=wx.Size(40, 24), style=0)
		self.stYfrom.SetToolTip("")

		self.stYto = wx.StaticText(id=wxID_FRAME1STYTO, label="To:", name="stYto", parent=self.panel, pos=wx.Point(144, 131), size=wx.Size(40, 24), style=0)
		self.stYto.SetToolTip("")

		self.stXfrom = wx.StaticText(id=wxID_FRAME1STXFROM, label="X-Axis From:", name="stXfrom", parent=self.panel, pos=wx.Point(0, 103), size=wx.Size(40, 24), style=0)
		self.stXfrom.SetToolTip("")

		self.stXto = wx.StaticText(id=wxID_FRAME1STXTO, label="To:", name="stXto", parent=self.panel, pos=wx.Point(144, 103), size=wx.Size(40, 24), style=0)
		self.stXto.SetToolTip("")

		self.stXlabel = wx.StaticText(id=wxID_FRAME1STXLABEL, label="X label", name="stXlabel", parent=self.panel, pos=wx.Point(0, 53), size=wx.Size(40, 21), style=0)
		self.stXlabel.SetToolTip("")

		self.stYlabel = wx.StaticText(id=wxID_FRAME1STYLABEL, label="Y label", name="stYlabel", parent=self.panel, pos=wx.Point(0, 78), size=wx.Size(40, 21), style=0)
		self.stYlabel.SetToolTip("")

		self.txtTitle = wx.TextCtrl(id=wxID_FRAME1TXTTITLE, name="txtTitle", parent=self.panel, pos=wx.Point(15, 0), size=wx.Size(40, 24), style=0, value="")
		self.txtTitle.SetToolTip("")

		self.txtYlabel = wx.TextCtrl(id=wxID_FRAME1TXTYLABEL, name="txtYlabel", parent=self.panel, pos=wx.Point(15, 78), size=wx.Size(40, 21), style=0, value="")
		self.txtYlabel.SetToolTip("")

		self.txtXlabel = wx.TextCtrl(id=wxID_FRAME1TXTXLABEL, name="txtXlabel", parent=self.panel, pos=wx.Point(15, 53), size=wx.Size(40, 21), style=0, value="")
		self.txtXlabel.SetToolTip("")

		self.txtXmin = wx.TextCtrl(id=wxID_FRAME1TXTXMIN, name="txtXmin", parent=self.panel, pos=wx.Point(15, 103), size=wx.Size(40, 24), style=0, value="")
		self.txtXmin.SetToolTip("")

		self.spnXmin = wx.SpinButton(id=wxID_FRAME1SPNXMIN, name="spnXmin", parent=self.panel, pos=wx.Point(96, 103), size=wx.Size(15, 24), style=wx.SP_VERTICAL)
		self.spnXmin.SetToolTip("")
		self.spnXmin.Bind(wx.EVT_SPIN_DOWN, self.OnSpnXminSpinDown, id=wxID_FRAME1SPNXMIN)
		self.spnXmin.Bind(wx.EVT_SPIN_UP, self.OnSpnXminSpinUp, id=wxID_FRAME1SPNXMIN)

		self.spnXmax = wx.SpinButton(id=wxID_FRAME1SPNXMAX, name="spnXmax", parent=self.panel, pos=wx.Point(240, 103), size=wx.Size(15, 24), style=wx.SP_VERTICAL)
		self.spnXmax.SetToolTip("")
		self.spnXmax.Bind(wx.EVT_SPIN_DOWN, self.OnSpnXmaxSpinDown, id=wxID_FRAME1SPNXMAX)
		self.spnXmax.Bind(wx.EVT_SPIN_UP, self.OnSpnXmaxSpinUp, id=wxID_FRAME1SPNXMAX)

		self.spnYmax = wx.SpinButton(id=wxID_FRAME1SPNYMAX, name="spnYmax", parent=self.panel, pos=wx.Point(240, 131), size=wx.Size(15, 24), style=wx.SP_VERTICAL)
		self.spnYmax.SetToolTip("")
		self.spnYmax.Bind(wx.EVT_SPIN_DOWN, self.OnSpnYmaxSpinDown, id=wxID_FRAME1SPNYMAX)
		self.spnYmax.Bind(wx.EVT_SPIN_UP, self.OnSpnYmaxSpinUp, id=wxID_FRAME1SPNYMAX)

		self.spnYmin = wx.SpinButton(id=wxID_FRAME1SPNYMIN, name="spnYmin", parent=self.panel, pos=wx.Point(96, 131), size=wx.Size(15, 24), style=wx.SP_VERTICAL)
		self.spnYmin.SetToolTip("")
		self.spnYmin.Bind(wx.EVT_SPIN_DOWN, self.OnSpnYminSpinDown, id=wxID_FRAME1SPNYMIN)
		self.spnYmin.Bind(wx.EVT_SPIN_UP, self.OnSpnYminSpinUp, id=wxID_FRAME1SPNYMIN)

		self.txtXmax = wx.TextCtrl(id=wxID_FRAME1TXTXMAX, name="txtXmax", parent=self.panel, pos=wx.Point(192, 103), size=wx.Size(40, 24), style=0, value="")
		self.txtXmax.SetToolTip("")

		self.txtYmax = wx.TextCtrl(id=wxID_FRAME1TXTYMAX, name="txtYmax", parent=self.panel, pos=wx.Point(192, 131), size=wx.Size(40, 24), style=0, value="")
		self.txtYmax.SetToolTip("")

		self.txtYmin = wx.TextCtrl(id=wxID_FRAME1TXTYMIN, name="txtYmin", parent=self.panel, pos=wx.Point(15, 131), size=wx.Size(40, 24), style=0, value="")
		self.txtYmin.SetToolTip("")

		self.stFont = wx.StaticText(id=wxID_FRAME1STFONT, label="Font size axes and title (pt)", name="stFont", parent=self.panel, pos=wx.Point(0, 28), size=wx.Size(40, 21), style=0)
		self.stFont.SetToolTip("")

		self.spnFontSizeAxes = wx.SpinCtrl(id=wxID_FRAME1SPNFONTSIZEAXES, initial=8, max=76, min=4, name="spnFontSizeAxes", parent=self.panel, pos=wx.Point(15, 28), size=wx.Size(40, 21), style=wx.SP_ARROW_KEYS)
		self.spnFontSizeAxes.SetToolTip("")
		self.spnFontSizeAxes.SetValue(8)
		self.spnFontSizeAxes.SetRange(4, 76)

		self.cbGrid = wx.CheckBox(id=wxID_FRAME1CBGRID, label="Show grid", name="cbGrid", parent=self.panel, pos=wx.Point(0, 159), size=wx.Size(50, 21), style=0)
		self.cbGrid.SetValue(False)
		self.cbGrid.SetToolTip("")

		self.btnApply = wx.Button(id=wxID_FRAME1BTNAPPLY, label="Apply", name="btnApply", parent=self.panel, pos=wx.Point(0, 184), size=wx.Size(50, 28), style=0)
		self.btnApply.Bind(wx.EVT_BUTTON, self.OnBtnApplyButton)

		self._init_plot_prop_sizers()

	def __init__(self, parent):
		self._init_plot_prop_ctrls(parent)

		self.minXrange = parent.GetXCurrentRange()[0]
		self.maxXrange = parent.GetXCurrentRange()[1]
		self.minYrange = parent.GetYCurrentRange()[0]
		self.maxYrange = parent.GetYCurrentRange()[1]

		self.graph = parent.last_draw[0]
		self.canvas = parent

		self.txtXmin.SetEditable(1)
		self.txtXmax.SetEditable(1)
		self.txtYmin.SetEditable(1)
		self.txtYmax.SetEditable(1)

		self.Increment = (self.maxXrange - self.minXrange) / 100

		self.txtXmin.SetValue("%.3f" % self.minXrange)
		self.txtXmax.SetValue("%.3f" % self.maxXrange)
		self.txtYmin.SetValue("%.3f" % self.minYrange)
		self.txtYmax.SetValue("%.3f" % self.maxYrange)

		try:
			self.txtTitle.SetValue(self.graph.getTitle())
		except:
			pass

		try:
			self.txtXlabel.SetValue(self.graph.getXLabel())
		except:
			pass

		try:
			self.txtYlabel.SetValue(self.graph.getYLabel())
		except:
			pass

		self.spnFontSizeAxes.SetValue(parent.GetFontSizeAxis())

		if self.canvas.GetEnableGrid() is True:
			self.cbGrid.SetValue(True)

	def OnBtnApplyButton(self, event):
		self.applyChanges()

	def applyChanges(self):
		self.canvas.fontSizeAxis = self.spnFontSizeAxes.GetValue()
		self.canvas.fontSizeTitle = self.spnFontSizeAxes.GetValue()
		self.canvas.SetEnableGrid(self.cbGrid.GetValue())

		self.graph.setTitle(self.txtTitle.GetValue())
		self.graph.setXLabel(self.txtXlabel.GetValue())
		self.graph.setYLabel(self.txtYlabel.GetValue())

		if (float(self.txtXmin.GetValue()) < float(self.txtXmax.GetValue())) and (float(self.txtYmin.GetValue()) < float(self.txtYmax.GetValue())) is True:
			self.canvas.last_draw = [self.canvas.last_draw[0], np.array([float(self.txtXmin.GetValue()), float(self.txtXmax.GetValue())]), np.array([float(self.txtYmin.GetValue()), float(self.txtYmax.GetValue())])]

		self.canvas.Redraw()

		self.Close()

	def tempRedraw(self):
		origX = self.canvas.last_draw[1]
		origY = self.canvas.last_draw[2]
		self.canvas.last_draw = [self.canvas.last_draw[0], np.array([float(self.txtXmin.GetValue()), float(self.txtXmax.GetValue())]), np.array([float(self.txtYmin.GetValue()), float(self.txtYmax.GetValue())])]
		self.canvas.Redraw()
		self.canvas.last_draw = [self.canvas.last_draw[0], origX, origY]

	def OnSpnXminSpinUp(self, event):
		curr = float(self.txtXmin.GetValue())
		curr = curr + self.Increment
		self.txtXmin.SetValue("%.3f" % curr)

	def OnSpnXminSpinDown(self, event):
		curr = float(self.txtXmin.GetValue())
		curr = curr - self.Increment
		self.txtXmin.SetValue("%.3f" % curr)

	def OnSpnXmaxSpinUp(self, event):
		curr = float(self.txtXmax.GetValue())
		curr = curr + self.Increment
		self.txtXmax.SetValue("%.3f" % curr)

	def OnSpnXmaxSpinDown(self, event):
		curr = float(self.txtXmax.GetValue())
		curr = curr - self.Increment
		self.txtXmax.SetValue("%.3f" % curr)

	def OnSpnYmaxSpinUp(self, event):
		curr = float(self.txtYmax.GetValue())
		curr = curr + self.Increment
		self.txtYmax.SetValue("%.3f" % curr)

	def OnSpnYmaxSpinDown(self, event):
		curr = float(self.txtYmax.GetValue())
		curr = curr - self.Increment
		self.txtYmax.SetValue("%.3f" % curr)

	def OnSpnYminSpinUp(self, event):
		curr = float(self.txtYmin.GetValue())
		curr = curr + self.Increment
		self.txtYmin.SetValue("%.3f" % curr)

	def OnSpnYminSpinDown(self, event):
		curr = float(self.txtYmin.GetValue())
		curr = curr - self.Increment
		self.txtYmin.SetValue("%.3f" % curr)
