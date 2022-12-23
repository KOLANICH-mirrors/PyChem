# -----------------------------------------------------------------------------
# Name:		   PyChemMain.py
# Purpose:
#
# Author:	   Roger Jarvis
#
# Created:	   2007/05/24
# RCS-ID:	   $Id$
# Copyright:   (c) 2007
# Licence:	   GNU General Public Licence
# -----------------------------------------------------------------------------
# Boa:Frame:PyChemMain

import os
import string
import sys
from xml.etree import cElementTree as ET

import scipy
import wx
import wx.adv
import wx.lib.filebrowsebutton
import wx.richtext
from numpy import loadtxt
from scipy import newaxis as nA
from wx.lib.anchors import LayoutAnchors

from . import Cluster, Dfa, Ga, Pca, Plsr, Univariate, expSetup, mva, plotSpectra
from .mva.chemometrics import _index
from .Pca import PlotPlsModel, SymColSelectTool, plotLine, plotLoads, plotScores, plotStem, plotText
from .plotSpectra import GridRowDel
from .utils import getByPath
from .utils.io import str_array


def create(parent):
	return PyChemMain(parent)


[wxID_PYCHEMMAIN, wxID_PYCHEMMAINNBMAIN, wxID_PYCHEMMAINPLCLUSTER, wxID_PYCHEMMAINPLDFA, wxID_PYCHEMMAINPLEXPSET, wxID_PYCHEMMAINPLGADFA, wxID_PYCHEMMAINPLGADPLS, wxID_PYCHEMMAINPLGAPLSC, wxID_PYCHEMMAINPLPCA, wxID_PYCHEMMAINPLPLS, wxID_PYCHEMMAINPLPREPROC, wxID_PYCHEMMAINSBMAIN, wxID_PYCHEMMAINPLUNIVARIATE] = [wx.NewIdRef() for _init_ctrls in range(13)]

[
	wxID_PYCHEMMAINMNUFILEAPPEXIT,
	wxID_PYCHEMMAINMNUFILEFILEIMPORT,
	wxID_PYCHEMMAINMNUFILELOADEXP,
	wxID_PYCHEMMAINMNUFILELOADWS,
	wxID_PYCHEMMAINMNUFILESAVEEXP,
	wxID_PYCHEMMAINMNUFILESAVEWS,
] = [wx.NewIdRef() for _init_coll_mnuFile_Items in range(6)]

[
	wxID_PYCHEMMAINMNUTOOLSEXPSET,
	wxID_PYCHEMMAINMNUTOOLSMNUCLUSTER,
	wxID_PYCHEMMAINMNUTOOLSMNUDFA,
	wxID_PYCHEMMAINMNUTOOLSMNUGADFA,
	wxID_PYCHEMMAINMNUTOOLSMNUGAPLSC,
	wxID_PYCHEMMAINMNUTOOLSMNUPCA,
	wxID_PYCHEMMAINMNUTOOLSMNUPLSR,
	wxID_PYCHEMMAINMNUTOOLSPREPROC,
] = [wx.NewIdRef() for _init_coll_mnuTools_Items in range(8)]

[
	wxID_PYCHEMMAINMNUHELPCONTENTS,
	wxID_PYCHEMMAINMNUABOUTCONTENTS,
] = [wx.NewIdRef() for _init_coll_mnuHelp_Items in range(2)]

[
	wxID_WXIMPORTCONFIRMDIALOG,
	wxID_WXIMPORTCONFIRMDIALOGBTNOK,
	wxID_WXIMPORTCONFIRMDIALOGGRDSAMPLEDATA,
	wxID_WXIMPORTCONFIRMDIALOGSTATICTEXT1,
	wxID_WXIMPORTCONFIRMDIALOGSTATICTEXT2,
	wxID_WXIMPORTCONFIRMDIALOGSTATICTEXT4,
	wxID_WXIMPORTCONFIRMDIALOGSTCOLS,
	wxID_WXIMPORTCONFIRMDIALOGSTROWS,
	wxID_WXIMPORTCONFIRMDIALOGSWLOADX,
] = [wx.NewIdRef() for _init_importconfirm_ctrls in range(9)]

[
	wxID_WXWORKSPACEDIALOG,
	wxID_WXWORKSPACEDIALOGBTNCANCEL,
	wxID_WXWORKSPACEDIALOGBTNDELETE,
	wxID_WXWORKSPACEDIALOGBTNEDIT,
	wxID_WXWORKSPACEDIALOGBTNOK,
	wxID_WXWORKSPACEDIALOGLBSAVEWORKSPACE,
] = [wx.NewIdRef() for _init_savews_ctrls in range(6)]

[MNUGRIDCOPY, MNUGRIDPASTE, MNUGRIDDELETECOL, MNUGRIDRENAMECOL, MNUGRIDRESETSORT] = [wx.NewIdRef() for _init_grid_menu_Items in range(5)]

[MNUGRIDROWDEL] = [wx.NewIdRef() for _init_grid_row_menu_Items in range(1)]


def errorBox(window, error):
	dlg = wx.MessageDialog(window, "".join(("The following error occured:\n\n", error)), "Error!", wx.OK | wx.ICON_ERROR)
	try:
		dlg.ShowModal()
	finally:
		dlg.Destroy()


class PlotToolBar(wx.ToolBar):
	def __init__(self, parent):
		wx.ToolBar.__init__(self, parent, id=-1, pos=(0, 0), size=(0, 0), style=wx.NO_BORDER | wx.TB_HORIZONTAL, name="")

		self.stTitle = wx.lib.stattext.GenStaticText(self, -1, "Title:", pos=wx.Point(2, 5), style=wx.TRANSPARENT_WINDOW)
		self.AddControl(self.stTitle)

		self.txtPlot = wx.TextCtrl(id=-1, name="txtPlot", parent=self, pos=wx.Point(26, 2), size=wx.Size(120, 21), style=wx.TE_DONTWRAP, value="Title")
		self.txtPlot.SetToolTip("Graph Title")
		self.txtPlot.Bind(wx.EVT_TEXT_ENTER, self.OnTxtPlot)
		self.AddControl(self.txtPlot)

		self.spnTitleFont = wx.SpinCtrl(id=-1, initial=12, max=76, min=5, name="spnTitleFont", parent=self, pos=wx.Point(148, 2), size=wx.Size(50, 21), style=wx.SP_ARROW_KEYS)
		self.spnTitleFont.SetToolTip("Title Font Size")
		self.spnTitleFont.Bind(wx.EVT_SPIN, self.OnSpnTitleFont)
		self.AddControl(self.spnTitleFont)

		self.AddSeparator()

		self.stXlabel = wx.lib.stattext.GenStaticText(self, -1, "X-label:", pos=wx.Point(202, 5), style=wx.TRANSPARENT_WINDOW)
		self.AddControl(self.stXlabel)

		self.txtXlabel = wx.TextCtrl(id=-1, name="txtXlabel", parent=self, pos=wx.Point(240, 2), size=wx.Size(70, 21), style=wx.TE_DONTWRAP, value="X-label")
		self.txtXlabel.SetToolTip("Abscissa (X-axis) Label")
		self.txtXlabel.Bind(wx.EVT_TEXT_ENTER, self.OnTxtXlabel)
		self.AddControl(self.txtXlabel)

		self.stYlabel = wx.lib.stattext.GenStaticText(self, -1, "Y-label:", pos=wx.Point(314, 5), style=wx.TRANSPARENT_WINDOW)
		self.AddControl(self.stYlabel)

		self.txtYlabel = wx.TextCtrl(id=-1, name="txtYlabel", parent=self, pos=wx.Point(352, 2), size=wx.Size(70, 21), style=wx.TE_DONTWRAP, value="Y-label")
		self.txtYlabel.SetToolTip("Ordinate (Y-axis) Label")
		self.txtYlabel.Bind(wx.EVT_TEXT_ENTER, self.OnTxtYlabel)
		self.AddControl(self.txtYlabel)

		self.spnAxesFont = wx.SpinCtrl(id=-1, initial=12, max=76, min=5, name="spnTitleFont", parent=self, pos=wx.Point(424, 2), size=wx.Size(50, 21), style=wx.SP_ARROW_KEYS)
		self.spnAxesFont.SetToolTip("Axes Font Size")
		self.spnAxesFont.Bind(wx.EVT_SPIN, self.OnSpnAxesFont)
		self.AddControl(self.spnAxesFont)

		self.AddSeparator()

		self.stXrange = wx.lib.stattext.GenStaticText(self, -1, "X-range:", pos=wx.Point(480, 5), style=wx.TRANSPARENT_WINDOW)
		self.AddControl(self.stXrange)

		self.txtXmin = wx.TextCtrl(id=-1, name="txtXmin", parent=self, pos=wx.Point(522, 2), size=wx.Size(40, 21), style=wx.TE_DONTWRAP, value="0.0")
		self.txtXmin.SetToolTip("Minimum X-axis range")
		self.AddControl(self.txtXmin)

		self.spnXmin = wx.SpinButton(id=-1, name="spnXmin", parent=self, pos=wx.Point(562, 2), size=wx.Size(15, 21), style=wx.SP_VERTICAL)
		self.spnXmin.SetToolTip("Minimum X-axis range")
		self.spnXmin.Bind(wx.EVT_SPIN_DOWN, self.OnSpnXminSpinDown)
		self.spnXmin.Bind(wx.EVT_SPIN_UP, self.OnSpnXminSpinUp)
		self.spnXmin.Bind(wx.EVT_SPIN, self.OnSpnXmin)
		self.AddControl(self.spnXmin)

		self.stDummy1 = wx.lib.stattext.GenStaticText(self, -1, " : ", pos=wx.Point(579, 5), style=wx.TRANSPARENT_WINDOW)
		self.AddControl(self.stDummy1)

		self.txtXmax = wx.TextCtrl(id=-1, name="txtXmax", parent=self, pos=wx.Point(590, 2), size=wx.Size(40, 21), style=wx.TE_DONTWRAP, value="0.0")
		self.txtXmax.SetToolTip("Maximum X-axis range")
		self.AddControl(self.txtXmax)

		self.spnXmax = wx.SpinButton(id=-1, name="spnXmax", parent=self, pos=wx.Point(630, 2), size=wx.Size(15, 21), style=wx.SP_VERTICAL)
		self.spnXmax.SetToolTip("Maximum X-axis range")
		self.spnXmax.Bind(wx.EVT_SPIN_DOWN, self.OnSpnXmaxSpinDown)
		self.spnXmax.Bind(wx.EVT_SPIN_UP, self.OnSpnXmaxSpinUp)
		self.spnXmax.Bind(wx.EVT_SPIN, self.OnSpnXmax)
		self.AddControl(self.spnXmax)

		self.AddSeparator()

		self.stYrange = wx.lib.stattext.GenStaticText(self, -1, "Y-range:", pos=wx.Point(647, 5), style=wx.TRANSPARENT_WINDOW)
		self.AddControl(self.stYrange)

		self.txtYmin = wx.TextCtrl(id=-1, name="txtYmin", parent=self, pos=wx.Point(690, 2), size=wx.Size(40, 21), style=wx.TE_DONTWRAP, value="0.0")
		self.txtYmin.SetToolTip("Minimum Y-axis range")
		self.AddControl(self.txtYmin)

		self.spnYmin = wx.SpinButton(id=-1, name="spnYmin", parent=self, pos=wx.Point(732, 2), size=wx.Size(15, 21), style=wx.SP_VERTICAL)
		self.spnYmin.SetToolTip("Minimum Y-axis range")
		self.spnYmin.Bind(wx.EVT_SPIN_DOWN, self.OnSpnYminSpinDown)
		self.spnYmin.Bind(wx.EVT_SPIN_UP, self.OnSpnYminSpinUp)
		self.spnYmin.Bind(wx.EVT_SPIN, self.OnSpnYmin)
		self.AddControl(self.spnYmin)

		self.stDummy2 = wx.lib.stattext.GenStaticText(self, -1, " : ", pos=wx.Point(749, 5), style=wx.TRANSPARENT_WINDOW)
		self.AddControl(self.stDummy1)

		self.txtYmax = wx.TextCtrl(id=-1, name="txtYmax", parent=self, pos=wx.Point(760, 2), size=wx.Size(40, 21), style=wx.TE_DONTWRAP, value="0.0")
		self.txtYmin.SetToolTip("Maximum Y-axis range")
		self.AddControl(self.txtYmin)

		self.spnYmax = wx.SpinButton(id=-1, name="spnYmax", parent=self, pos=wx.Point(800, 2), size=wx.Size(15, 21), style=wx.SP_VERTICAL)
		self.spnYmax.SetToolTip("Maximum Y-axis range")
		self.spnYmax.Bind(wx.EVT_SPIN_DOWN, self.OnSpnYmaxSpinDown)
		self.spnYmax.Bind(wx.EVT_SPIN_UP, self.OnSpnYmaxSpinUp)
		self.spnYmax.Bind(wx.EVT_SPIN, self.OnSpnYmax)
		self.AddControl(self.spnYmax)

		self.AddSeparator()

		self.tbConf = wx.lib.buttons.GenBitmapToggleButton(bitmap=wx.Bitmap(os.path.join("bmp", "conf_int.bmp"), wx.BITMAP_TYPE_BMP), id=-1, name="tbConf", parent=self, pos=wx.Point(817, 2), size=wx.Size(21, 21))
		self.tbConf.SetValue(False)
		self.tbConf.SetToolTip("")
		self.tbConf.Enable(False)
		self.AddControl(self.tbConf)
		self.tbConf.Bind(wx.EVT_BUTTON, self.OnTbConfButton)

		self.tbPoints = wx.lib.buttons.GenBitmapToggleButton(bitmap=wx.Bitmap(os.path.join("bmp", "plot_text.bmp"), wx.BITMAP_TYPE_BMP), id=-1, name="tbPoints", parent=self, pos=wx.Point(839, 2), size=wx.Size(21, 21))
		self.tbPoints.SetValue(True)
		self.tbPoints.SetToolTip("Plot using text labels")
		self.tbPoints.Enable(True)
		self.tbPoints.Bind(wx.EVT_BUTTON, self.OnTbPointsButton)
		self.AddControl(self.tbPoints)

		self.tbSymbols = wx.lib.buttons.GenBitmapToggleButton(bitmap=wx.Bitmap(os.path.join("bmp", "plot_symbol.bmp"), wx.BITMAP_TYPE_BMP), id=-1, name="tbSymbols", parent=self, pos=wx.Point(861, 2), size=wx.Size(21, 21))
		self.tbSymbols.SetValue(False)
		self.tbSymbols.SetToolTip("Plot using colored symbols")
		self.tbSymbols.Enable(True)
		self.tbSymbols.Bind(wx.EVT_BUTTON, self.OnTbSymbolsButton)
		self.tbSymbols.Bind(wx.EVT_RIGHT_DOWN, self.OnTbSymbolsRightClick)
		self.AddControl(self.tbSymbols)

		self.tbLoadLabels = wx.BitmapButton(bitmap=wx.Bitmap(os.path.join("bmp", "conf_0.bmp"), wx.BITMAP_TYPE_BMP), id=-1, name="tbLoadLabels", parent=self, pos=wx.Point(883, 2), size=wx.Size(20, 21))
		self.tbLoadLabels.SetToolTip("")
		self.tbLoadLabels.Enable(False)
		self.tbLoadLabels.Bind(wx.EVT_BUTTON, self.OnTbLoadLabelsButton)
		self.AddControl(self.tbLoadLabels)

		self.tbLoadLabStd1 = wx.BitmapButton(bitmap=wx.Bitmap(os.path.join("bmp", "conf_1.bmp"), wx.BITMAP_TYPE_BMP), id=-1, name="tbLoadLabStd1", parent=self, pos=wx.Point(905, 2), size=wx.Size(20, 21))
		self.tbLoadLabStd1.SetToolTip("")
		self.tbLoadLabStd1.Enable(False)
		self.tbLoadLabStd1.Bind(wx.EVT_BUTTON, self.OnTbLoadLabStd1Button)
		self.AddControl(self.tbLoadLabStd1)

		self.tbLoadLabStd2 = wx.BitmapButton(bitmap=wx.Bitmap(os.path.join("bmp", "conf_2.bmp"), wx.BITMAP_TYPE_BMP), id=-1, name="tbLoadLabStd2", parent=self, pos=wx.Point(927, 2), size=wx.Size(20, 21))
		self.tbLoadLabStd2.SetToolTip("")
		self.tbLoadLabStd2.Enable(False)
		self.tbLoadLabStd2.Bind(wx.EVT_BUTTON, self.OnTbLoadLabStd2Button)
		self.AddControl(self.tbLoadLabStd2)

		self.tbLoadSymStd2 = wx.BitmapButton(bitmap=wx.Bitmap(os.path.join("bmp", "conf_2_sym.bmp"), wx.BITMAP_TYPE_BMP), id=-1, name="tbLoadSymStd2", parent=self, pos=wx.Point(949, 2), size=wx.Size(20, 21))
		self.tbLoadSymStd2.SetToolTip("")
		self.tbLoadSymStd2.Enable(False)
		self.tbLoadSymStd2.Bind(wx.EVT_BUTTON, self.OnTbLoadSymStd2Button)
		self.tbLoadSymStd2.Bind(wx.EVT_RIGHT_DOWN, self.OnTbLoadSymStd2RightClick)
		self.AddControl(self.tbLoadSymStd2)

		self.AddSeparator()

		self.tbXlog = wx.BitmapButton(bitmap=wx.Bitmap(os.path.join("bmp", "xlog.bmp"), wx.BITMAP_TYPE_BMP), id=-1, name="tbXlog", parent=self, pos=wx.Point(971, 2), size=wx.Size(20, 21))
		self.tbXlog.SetToolTip("")
		self.tbXlog.Bind(wx.EVT_BUTTON, self.OnTbXLogButton)
		self.AddControl(self.tbXlog)

		self.tbYlog = wx.BitmapButton(bitmap=wx.Bitmap(os.path.join("bmp", "ylog.bmp"), wx.BITMAP_TYPE_BMP), id=-1, name="tbYlog", parent=self, pos=wx.Point(993, 2), size=wx.Size(20, 21))
		self.tbYlog.SetToolTip("")
		self.tbYlog.Bind(wx.EVT_BUTTON, self.OnTbYLogButton)
		self.AddControl(self.tbYlog)

		self.tbScinote = wx.BitmapButton(bitmap=wx.Bitmap(os.path.join("bmp", "scinote.bmp"), wx.BITMAP_TYPE_BMP), id=-1, name="tbScinote", parent=self, pos=wx.Point(1015, 2), size=wx.Size(20, 21))
		self.tbScinote.SetToolTip("")
		self.tbScinote.Bind(wx.EVT_BUTTON, self.OnTbScinoteButton)
		self.AddControl(self.tbScinote)

		self.SymPopUpWin = SymColSelectTool(self)

		self.loadIdx = 0

	def GetLoadPlotIdx(self):
		return self.loadIdx

	def OnTbSymbolsRightClick(self, event):
		# symbol/colour options for scores plots
		self.tbSymbols.SetValue(True)
		self.doPlot()
		btn = event.GetEventObject()
		pos = btn.ClientToScreen((0, 0))
		sz = btn.GetSize()
		self.SymPopUpWin.SetPosition(wx.Point(pos[0] - 200, pos[1] + sz[1]))

		# show plot options
		self.SymPopUpWin.ShowModal()

	def OnTbLoadLabelsButton(self, event):
		# plot loadings
		self.doPlot(loadType=0)
		self.loadIdx = 0

	def OnTxtPlot(self, event):
		self.graph.setTitle(self.txtPlot.GetValue())
		self.graph.setXLabel(self.txtXlabel.GetValue())
		self.graph.setYLabel(self.txtYlabel.GetValue())
		self.canvas.Redraw()

	def OnTxtXlabel(self, event):
		self.graph.setTitle(self.txtPlot.GetValue())
		self.graph.setXLabel(self.txtXlabel.GetValue())
		self.graph.setYLabel(self.txtYlabel.GetValue())
		self.canvas.Redraw()

	def OnTxtYlabel(self, event):
		self.graph.setTitle(self.txtPlot.GetValue())
		self.graph.setXLabel(self.txtXlabel.GetValue())
		self.graph.setYLabel(self.txtYlabel.GetValue())
		self.canvas.Redraw()

	def OnTbLoadLabStd1Button(self, event):
		# plot loadings
		self.doPlot(loadType=1)
		self.loadIdx = 1

	def OnTbLoadLabStd2Button(self, event):
		# plot loadings
		self.doPlot(loadType=2)
		self.loadIdx = 2

	def OnTbLoadSymStd2Button(self, event):
		# plot loadings
		self.doPlot(loadType=3)
		self.loadIdx = 3

	def OnTbLoadSymStd2RightClick(self, event):
		# invoke loadings plot sym/col selector
		self.doPlot(loadType=3)
		self.loadIdx = 3
		btn = event.GetEventObject()
		pos = btn.ClientToScreen((0, 0))
		sz = btn.GetSize()
		self.SymPopUpWin.SetPosition(wx.Point(pos[0] - 200, pos[1] + sz[1]))

		# show plot options
		self.SymPopUpWin.ShowModal()

	def OnTbConfButton(self, event):
		if (self.tbPoints.GetValue() is False) & (self.tbConf.GetValue() is False) & (self.tbSymbols.GetValue() is False) is False:
			# plot scores
			self.doPlot()

	def OnTbPointsButton(self, event):
		if (self.tbPoints.GetValue() is False) & (self.tbConf.GetValue() is False) & (self.tbSymbols.GetValue() is False) is False:
			# plot scores
			self.doPlot()

	def OnTbSymbolsButton(self, event):
		if (self.tbPoints.GetValue() is False) & (self.tbConf.GetValue() is False) & (self.tbSymbols.GetValue() is False) is False:
			# plot scores
			self.doPlot()

	def OnTbXLogButton(self, event):
		if self.canvas.getLogScale()[0] is True:
			self.canvas.setLogScale((False, self.canvas.getLogScale()[1]))
		else:
			self.canvas.setLogScale((True, self.canvas.getLogScale()[1]))
		self.canvas.Redraw()

	def OnTbYLogButton(self, event):
		if self.canvas.getLogScale()[1] is True:
			self.canvas.setLogScale((self.canvas.getLogScale()[0], False))
		else:
			self.canvas.setLogScale((self.canvas.getLogScale()[0], True))
		self.canvas.Redraw()

	def OnTbScinoteButton(self, event):
		if self.canvas.GetUseScientificNotation() is False:
			self.canvas.SetUseScientificNotation(True)
		else:
			self.canvas.SetUseScientificNotation(False)
		self.canvas.Redraw()

	def doPlot(self, loadType=0, symcolours=[], symsymbols=[]):
		if self.canvas.GetName() in ["plcDFAscores"]:
			if self.canvas.prnt.titleBar.data["dfscores"] is not None:
				plotScores(self.canvas, self.canvas.prnt.titleBar.data["dfscores"], cl=self.canvas.prnt.titleBar.data["class"][:, 0], labels=self.canvas.prnt.titleBar.data["label"], validation=self.canvas.prnt.titleBar.data["validation"], col1=self.canvas.prnt.titleBar.spnDfaScore1.GetValue() - 1, col2=self.canvas.prnt.titleBar.spnDfaScore2.GetValue() - 1, title=self.graph.title, xLabel=self.graph.xLabel, yLabel=self.graph.yLabel, xval=self.canvas.prnt.titleBar.cbDfaXval.GetValue(), text=self.tbPoints.GetValue(), pconf=self.tbConf.GetValue(), symb=self.tbSymbols.GetValue(), usecol=symcolours, usesym=symsymbols)

		elif self.canvas.GetName() in ["plcPCAscore"]:
			if self.canvas.prnt.titleBar.data["pcscores"] is not None:
				plotScores(self.canvas, self.canvas.prnt.titleBar.data["pcscores"], cl=self.canvas.prnt.titleBar.data["class"][:, 0], labels=self.canvas.prnt.titleBar.data["label"], validation=self.canvas.prnt.titleBar.data["validation"], col1=self.canvas.prnt.titleBar.spnNumPcs1.GetValue() - 1, col2=self.canvas.prnt.titleBar.spnNumPcs2.GetValue() - 1, title=self.graph.title, xLabel=self.graph.xLabel, yLabel=self.graph.yLabel, xval=False, text=self.tbPoints.GetValue(), pconf=False, symb=self.tbSymbols.GetValue(), usecol=symcolours, usesym=symsymbols)

		elif len(self.canvas.GetName().split("plcPredPls")) > 1:
			self.canvas = PlotPlsModel(self.canvas, model="full", tbar=self.canvas.prnt.prnt.prnt.parent.tbMain, cL=self.canvas.prnt.prnt.titleBar.data["class"], scores=self.canvas.prnt.prnt.titleBar.data["plst"], label=self.canvas.prnt.prnt.titleBar.data["label"], predictions=self.canvas.prnt.prnt.titleBar.data["plspred"], validation=self.canvas.prnt.prnt.titleBar.data["validation"], RMSEPT=self.canvas.prnt.prnt.titleBar.data["RMSEPT"], factors=self.canvas.prnt.prnt.titleBar.data["plsfactors"], type=self.canvas.prnt.prnt.titleBar.data["plstype"], col1=self.canvas.prnt.prnt.titleBar.spnPLSfactor1.GetValue() - 1, col2=self.canvas.prnt.prnt.titleBar.spnPLSfactor2.GetValue() - 1, symbols=self.tbSymbols.GetValue(), usetxt=self.tbPoints.GetValue(), usecol=symcolours, usesym=symsymbols, errplot=self.tbSymbols.GetValue(), plScL=self.canvas.prnt.prnt.titleBar.data["pls_class"])

		elif self.canvas.GetName() in ["plcGaFeatPlot"]:
			plotScores(self.canvas, self.canvas.prnt.prnt.splitPrnt.titleBar.data["gavarcoords"], cl=self.canvas.prnt.prnt.splitPrnt.titleBar.data["class"][:, 0], labels=self.canvas.prnt.prnt.splitPrnt.titleBar.data["label"], validation=self.canvas.prnt.prnt.splitPrnt.titleBar.data["validation"], col1=0, col2=1, title=self.graph.title, xLabel=self.graph.xLabel, yLabel=self.graph.yLabel, xval=True, text=self.tbPoints.GetValue(), pconf=False, symb=self.tbSymbols.GetValue(), usecol=symcolours, usesym=symsymbols)

		elif len(self.canvas.GetName().split("plcGaModelPlot")) > 1:
			if self.canvas.prnt.prnt.prnt.splitPrnt.type in ["DFA"]:
				if self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["gadfadfscores"] is not None:
					plotScores(self.canvas, self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["gadfadfscores"], cl=self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["class"][:, 0], labels=self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["label"], validation=self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["validation"], col1=self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.spnGaScoreFrom.GetValue() - 1, col2=self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.spnGaScoreTo.GetValue() - 1, title=self.graph.title, xLabel=self.graph.xLabel, yLabel=self.graph.yLabel, xval=True, text=self.tbPoints.GetValue(), pconf=self.tbConf.GetValue(), symb=self.tbSymbols.GetValue(), usecol=symcolours, usesym=symsymbols)
			else:
				self.canvas = PlotPlsModel(self.canvas, model="ga", tbar=self.canvas.prnt.prnt.prnt.splitPrnt.prnt.parent.tbMain, cL=self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["class"], scores=None, label=self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["label"], predictions=self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["gaplsscores"], validation=self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["validation"], RMSEPT=self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["gaplsrmsept"], factors=self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["gaplsfactors"], type=0, col1=self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.spnGaScoreFrom.GetValue() - 1, col2=self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.spnGaScoreTo.GetValue() - 1, symbols=self.tbSymbols.GetValue(), usetxt=self.tbPoints.GetValue(), usecol=symcolours, usesym=symsymbols, plScL=self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["pls_class"])

		elif self.canvas.GetName() in ["plcPcaLoadsV"]:
			if self.canvas.prnt.titleBar.data["pcloads"] is not None:
				plotLoads(self.canvas, scipy.transpose(self.canvas.prnt.titleBar.data["pcloads"]), xaxis=self.canvas.prnt.titleBar.data["indlabels"], col1=self.canvas.prnt.titleBar.spnNumPcs1.GetValue() - 1, col2=self.canvas.prnt.titleBar.spnNumPcs2.GetValue() - 1, title=self.graph.title, xLabel=self.graph.xLabel, yLabel=self.graph.yLabel, type=loadType, usecol=symcolours, usesym=symsymbols)

		elif self.canvas.GetName() in ["plcPLSloading"]:
			if self.canvas.prnt.titleBar.data["plsloads"] is not None:
				plotLoads(self.canvas, self.canvas.prnt.titleBar.data["plsloads"], xaxis=self.canvas.prnt.titleBar.data["indlabels"], col1=self.canvas.prnt.titleBar.spnPLSfactor1.GetValue() - 1, col2=self.canvas.prnt.titleBar.spnPLSfactor2.GetValue() - 1, title=self.graph.title, xLabel=self.graph.xLabel, yLabel=self.graph.yLabel, type=loadType, usecol=symcolours, usesym=symsymbols)

		elif self.canvas.GetName() in ["plcDfaLoadsV"]:
			if self.canvas.prnt.titleBar.data["dfloads"] is not None:
				plotLoads(self.canvas, self.canvas.prnt.titleBar.data["dfloads"], xaxis=self.canvas.prnt.titleBar.data["indlabels"], col1=self.canvas.prnt.titleBar.spnDfaScore1.GetValue() - 1, col2=self.canvas.prnt.titleBar.spnDfaScore2.GetValue() - 1, title=self.graph.title, xLabel=self.graph.xLabel, yLabel=self.graph.yLabel, type=loadType, usecol=symcolours, usesym=symsymbols)

		elif self.canvas.GetName() in ["plcGaSpecLoad"]:
			if self.canvas.prnt.prnt.prnt.splitPrnt.type in ["DFA"]:
				labels = []
				for each in self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["gacurrentchrom"]:
					labels.append(self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["indlabels"][int(each)])
				plotLoads(self.canvas, self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["gadfadfaloads"], xaxis=labels, title=self.graph.title, xLabel=self.graph.xLabel, yLabel=self.graph.yLabel, type=loadType, usecol=symcolours, usesym=symsymbols)

		elif self.canvas.GetName() in ["plcGaSpecLoad"]:
			if self.canvas.prnt.prnt.splitPrnt.type in ["PLS"]:
				labels = []
				for each in self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["gacurrentchrom"]:
					labels.append(self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["indlabels"][int(each)])
				plotLoads(self.canvas, self.canvas.prnt.prnt.splitPrnt.titleBar.data["gaplsplsloads"], xaxis=labels, title=self.graph.title, xLabel=self.graph.xLabel, yLabel=self.graph.yLabel, type=loadType, usecol=symcolours, usesym=symsymbols)

	def OnTxtTitle(self, event):
		self.graph.setTitle(self.txtTitle.GetValue())
		self.canvas.Redraw()

	def OnBtnApply(self, event):
		self.canvas.fontSizeAxis = self.spnAxesFont.GetValue()
		self.canvas.fontSizeTitle = self.spnTitleFont.GetValue()

		self.graph.setTitle(self.txtTitle.GetValue())
		self.graph.setXLabel(self.txtXlabel.GetValue())
		self.graph.setYLabel(self.txtYlabel.GetValue())

		if (float(self.txtXmin.GetValue()) < float(self.txtXmax.GetValue())) and (float(self.txtYmin.GetValue()) < float(self.txtYmax.GetValue())) is True:
			self.canvas.last_draw = [self.canvas.last_draw[0], np.array([float(self.txtXmin.GetValue()), float(self.txtXmax.GetValue())]), np.array([float(self.txtYmin.GetValue()), float(self.txtYmax.GetValue())])]

		self.canvas.Redraw()

		self.Close()

	def OnSpnAxesFont(self, event):
		self.canvas.fontSizeAxis = self.spnAxesFont.GetValue()
		self.canvas.Redraw()

	def OnSpnTitleFont(self, event):
		self.canvas.fontSizeTitle = self.spnTitleFont.GetValue()
		self.canvas.Redraw()

	def resizeAxes(self):
		if (float(self.txtXmin.GetValue()) < float(self.txtXmax.GetValue())) and (float(self.txtYmin.GetValue()) < float(self.txtYmax.GetValue())) is True:
			self.canvas.last_draw = [self.canvas.last_draw[0], np.array([float(self.txtXmin.GetValue()), float(self.txtXmax.GetValue())]), np.array([float(self.txtYmin.GetValue()), float(self.txtYmax.GetValue())])]
		self.canvas.Redraw()

	def OnSpnXmin(self, event):
		self.resizeAxes()

	def OnSpnXmax(self, event):
		self.resizeAxes()

	def OnSpnYmin(self, event):
		self.resizeAxes()

	def OnSpnYmax(self, event):
		self.resizeAxes()

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


class PyChemMain(wx.Frame):
	_custom_classes = {"wx.Panel": ["expSetup", "plotSpectra", "Pca", "Cluster", "Dfa", "Plsr", "Ga", "Univariate"]}

	def _init_coll_mnuTools_Items(self, parent):
		# generated method, don't edit

		parent.Append(help="", id=wxID_PYCHEMMAINMNUTOOLSEXPSET, kind=wx.ITEM_NORMAL, text="Experiment Setup")
		parent.Append(help="", id=wxID_PYCHEMMAINMNUTOOLSPREPROC, kind=wx.ITEM_NORMAL, text="Spectral Pre-processing")
		parent.Append(help="", id=wxID_PYCHEMMAINPLUNIVARIATE, kind=wx.ITEM_NORMAL, text="Univariate Tests")
		parent.Append(help="", id=wxID_PYCHEMMAINMNUTOOLSMNUPCA, kind=wx.ITEM_NORMAL, text="Principal Component Analysis (PCA)")
		parent.Append(help="", id=wxID_PYCHEMMAINMNUTOOLSMNUCLUSTER, kind=wx.ITEM_NORMAL, text="Cluster Analysis")
		parent.Append(help="", id=wxID_PYCHEMMAINMNUTOOLSMNUDFA, kind=wx.ITEM_NORMAL, text="Discriminant Function Analysis (DFA)")
		parent.Append(help="", id=wxID_PYCHEMMAINMNUTOOLSMNUPLSR, kind=wx.ITEM_NORMAL, text="Partial Least Squares Regression (PLSR)")
		parent.Append(help="", id=wxID_PYCHEMMAINMNUTOOLSMNUGADFA, kind=wx.ITEM_NORMAL, text="GA-Discriminant Function Analysis")
		parent.Append(help="", id=wxID_PYCHEMMAINMNUTOOLSMNUGAPLSC, kind=wx.ITEM_NORMAL, text="GA-Partial Least Squares Calibration")
		self.Bind(wx.EVT_MENU, self.OnMnuToolsExpsetMenu, id=wxID_PYCHEMMAINMNUTOOLSEXPSET)
		self.Bind(wx.EVT_MENU, self.OnMnuToolsPreprocMenu, id=wxID_PYCHEMMAINMNUTOOLSPREPROC)
		self.Bind(wx.EVT_MENU, self.OnMnuToolsMnuunivariateMenu, id=wxID_PYCHEMMAINPLUNIVARIATE)
		self.Bind(wx.EVT_MENU, self.OnMnuToolsMnupcaMenu, id=wxID_PYCHEMMAINMNUTOOLSMNUPCA)
		self.Bind(wx.EVT_MENU, self.OnMnuToolsMnuclusterMenu, id=wxID_PYCHEMMAINMNUTOOLSMNUCLUSTER)
		self.Bind(wx.EVT_MENU, self.OnMnuToolsMnuplsrMenu, id=wxID_PYCHEMMAINMNUTOOLSMNUPLSR)
		self.Bind(wx.EVT_MENU, self.OnMnuToolsMnudfaMenu, id=wxID_PYCHEMMAINMNUTOOLSMNUDFA)
		self.Bind(wx.EVT_MENU, self.OnMnuToolsMnugadfaMenu, id=wxID_PYCHEMMAINMNUTOOLSMNUGADFA)
		self.Bind(wx.EVT_MENU, self.OnMnuToolsMnugaplscMenu, id=wxID_PYCHEMMAINMNUTOOLSMNUGAPLSC)

	def _init_coll_mnuFile_Items(self, parent):
		# generated method, don't edit

		parent.Append(help="", id=wxID_PYCHEMMAINMNUFILELOADEXP, kind=wx.ITEM_NORMAL, text="Load Experiment")
		parent.Append(help="", id=wxID_PYCHEMMAINMNUFILELOADWS, kind=wx.ITEM_NORMAL, text="Load Workspace")
		parent.Append(help="", id=wxID_PYCHEMMAINMNUFILESAVEEXP, kind=wx.ITEM_NORMAL, text="Save Experiment As..")
		parent.Append(help="", id=wxID_PYCHEMMAINMNUFILESAVEWS, kind=wx.ITEM_NORMAL, text="Save Workspace As...")
		parent.Append(help="", id=wxID_PYCHEMMAINMNUFILEFILEIMPORT, kind=wx.ITEM_NORMAL, text="Import")
		parent.Append(help="", id=wxID_PYCHEMMAINMNUFILEAPPEXIT, kind=wx.ITEM_NORMAL, text="Exit")
		self.Bind(wx.EVT_MENU, self.OnMnuFileLoadexpMenu, id=wxID_PYCHEMMAINMNUFILELOADEXP)
		self.Bind(wx.EVT_MENU, self.OnMnuFileLoadwsMenu, id=wxID_PYCHEMMAINMNUFILELOADWS)
		self.Bind(wx.EVT_MENU, self.OnMnuFileSaveexpMenu, id=wxID_PYCHEMMAINMNUFILESAVEEXP)
		self.Bind(wx.EVT_MENU, self.OnMnuFileSavewsMenu, id=wxID_PYCHEMMAINMNUFILESAVEWS)
		self.Bind(wx.EVT_MENU, self.OnMnuFileFileimportMenu, id=wxID_PYCHEMMAINMNUFILEFILEIMPORT)
		self.Bind(wx.EVT_MENU, self.OnMnuFileAppexitMenu, id=wxID_PYCHEMMAINMNUFILEAPPEXIT)

	def _init_coll_mnuMain_Menus(self, parent):
		# generated method, don't edit

		parent.Append(menu=self.mnuFile, title="File")
		parent.Append(menu=self.mnuTools, title="Tools")
		parent.Append(menu=self.mnuHelp, title="Help")

	def _init_coll_mnuHelp_Items(self, parent):
		# generated method, don't edit

		parent.Append(help="", id=wxID_PYCHEMMAINMNUHELPCONTENTS, kind=wx.ITEM_NORMAL, text="Contents")
		parent.Append(help="", id=wxID_PYCHEMMAINMNUABOUTCONTENTS, kind=wx.ITEM_NORMAL, text="About")
		self.Bind(wx.EVT_MENU, self.OnMnuHelpContentsMenu, id=wxID_PYCHEMMAINMNUHELPCONTENTS)
		self.Bind(wx.EVT_MENU, self.OnMnuAboutContentsMenu, id=wxID_PYCHEMMAINMNUABOUTCONTENTS)

	def _init_coll_stbMain_Fields(self, parent):
		# generated method, don't edit
		parent.SetFieldsCount(5)

		parent.SetStatusText(number=0, text="Status")
		parent.SetStatusText(number=1, text="")
		parent.SetStatusText(number=2, text="")
		parent.SetStatusText(number=3, text="")
		parent.SetStatusText(number=4, text="")

		parent.SetStatusWidths([-2, -2, -2, -2, -5])

	def _init_coll_nbMain_Pages(self, parent):
		# generated method, don't edit

		parent.AddPage(imageId=-1, page=self.plExpset, select=True, text="Experiment Setup")
		parent.AddPage(imageId=-1, page=self.plPreproc, select=False, text="Spectral Pre-processing")
		parent.AddPage(imageId=-1, page=self.plUnivariate, select=False, text="Univariate Tests")
		parent.AddPage(imageId=-1, page=self.plPca, select=False, text="Principal Component Analysis")
		parent.AddPage(imageId=-1, page=self.plCluster, select=False, text="Cluster Analysis")
		parent.AddPage(imageId=-1, page=self.plDfa, select=False, text="Discriminant Function Analysis")
		parent.AddPage(imageId=-1, page=self.plPls, select=False, text="Partial Least Squares Regression")
		parent.AddPage(imageId=-1, page=self.plGadfa, select=False, text="GA - Discriminant Function Analysis")
		parent.AddPage(imageId=-1, page=self.plGapls, select=False, text="GA - PLSR Calibration")

	def _init_grid_menu_Items(self, parent):
		# generated method, don't edit

		parent.Append(help="", id=MNUGRIDCOPY, kind=wx.ITEM_NORMAL, text="Copy")
		parent.Append(help="", id=MNUGRIDPASTE, kind=wx.ITEM_NORMAL, text="Paste")
		parent.Append(help="", id=MNUGRIDRENAMECOL, kind=wx.ITEM_NORMAL, text="Rename column")
		parent.Append(help="", id=MNUGRIDDELETECOL, kind=wx.ITEM_NORMAL, text="Delete column")
		parent.Append(help="", id=MNUGRIDRESETSORT, kind=wx.ITEM_NORMAL, text="Reset row sort")
		self.Bind(wx.EVT_MENU, self.OnMnuGridCopy, id=MNUGRIDCOPY)
		self.Bind(wx.EVT_MENU, self.OnMnuGridPaste, id=MNUGRIDPASTE)
		self.Bind(wx.EVT_MENU, self.OnMnuGridRenameColumn, id=MNUGRIDRENAMECOL)
		self.Bind(wx.EVT_MENU, self.OnMnuGridDeleteColumn, id=MNUGRIDDELETECOL)
		self.Bind(wx.EVT_MENU, self.OnMnuGridResetSort, id=MNUGRIDRESETSORT)

	def _init_grid_row_menu_Items(self, parent):
		parent.Append(help="", id=MNUGRIDROWDEL, kind=wx.ITEM_NORMAL, text="Delete User Defined Variable")
		self.Bind(wx.EVT_MENU, self.OnMnuGridRowDel, id=MNUGRIDROWDEL)

	def _init_utils(self):
		# generated method, don't edit
		self.mnuMain = wx.MenuBar()

		self.mnuFile = wx.Menu(title="")

		self.mnuTools = wx.Menu(title="")

		self.mnuHelp = wx.Menu(title="")

		self.gridMenu = wx.Menu(title="")

		self.indRowMenu = wx.Menu(title="")

		self._init_coll_mnuMain_Menus(self.mnuMain)
		self._init_coll_mnuFile_Items(self.mnuFile)
		self._init_coll_mnuTools_Items(self.mnuTools)
		self._init_coll_mnuHelp_Items(self.mnuHelp)
		self._init_grid_menu_Items(self.gridMenu)
		self._init_grid_row_menu_Items(self.indRowMenu)

	def _init_ctrls(self, prnt):
		# generated method, don't edit
		wx.Frame.__init__(self, id=wxID_PYCHEMMAIN, name="PyChemMain", parent=prnt, pos=wx.Point(0, 0), size=wx.Size(1024, 738), style=wx.DEFAULT_FRAME_STYLE, title="PyChem 3.0.5a Beta")
		self._init_utils()
		self.SetClientSize(wx.Size(1016, 704))
		self.SetToolTip("")
		self.SetHelpText("")
		self.Center(wx.BOTH)
		self.SetIcon(wx.Icon(os.path.join("ico", "pychem.ico"), wx.BITMAP_TYPE_ICO))
		self.SetMinSize(wx.Size(200, 400))
		self.SetMenuBar(self.mnuMain)
		self.Bind(wx.EVT_SIZE, self.OnMainFrameSize)

		self.nbMain = wx.Notebook(id=wxID_PYCHEMMAINNBMAIN, name="nbMain", parent=self, pos=wx.Point(0, 0), size=wx.Size(1016, 730), style=0)
		self.nbMain.SetToolTip("")
		self.nbMain.SetMinSize(wx.Size(200, 400))
		self.nbMain.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnNbMainNotebookPageChanging, id=wxID_PYCHEMMAINNBMAIN)
		self.nbMain.parent = self

		self.sbMain = wx.StatusBar(id=wxID_PYCHEMMAINSBMAIN, name="sbMain", parent=self, style=0)
		self.sbMain.SetToolTip("")
		self._init_coll_stbMain_Fields(self.sbMain)
		self.SetStatusBar(self.sbMain)

		self.tbMain = PlotToolBar(self)
		self.tbMain.Enable(False)
		self.tbMain.Bind(wx.EVT_SIZE, self.OnTbMainSize)
		self.SetToolBar(self.tbMain)

		self.plExpset = expSetup.expSetup(id=wxID_PYCHEMMAINPLEXPSET, name="plExpset", parent=self.nbMain, pos=wx.Point(0, 0), size=wx.Size(1008, 635), style=wx.TAB_TRAVERSAL)
		self.plExpset.getFrame(self)
		self.plExpset.SetToolTip("")

		self.plPreproc = plotSpectra.plotSpectra(id=wxID_PYCHEMMAINPLPREPROC, name="plPreproc", parent=self.nbMain, pos=wx.Point(0, 0), size=wx.Size(1008, 635), style=wx.TAB_TRAVERSAL)
		self.plPreproc.SetToolTip("")

		self.plPca = Pca.Pca(id=wxID_PYCHEMMAINPLPCA, name="plPca", parent=self.nbMain, pos=wx.Point(0, 0), size=wx.Size(1008, 635), style=wx.TAB_TRAVERSAL)
		self.plPca.SetToolTip("")

		self.plCluster = Cluster.Cluster(id=wxID_PYCHEMMAINPLCLUSTER, name="plCluster", parent=self.nbMain, pos=wx.Point(0, 0), size=wx.Size(1008, 635), style=wx.TAB_TRAVERSAL)
		self.plCluster.SetToolTip("")
		self.plCluster.parent = self

		self.plDfa = Dfa.Dfa(id=wxID_PYCHEMMAINPLDFA, name="plDfa", parent=self.nbMain, pos=wx.Point(0, 0), size=wx.Size(1008, 635), style=wx.TAB_TRAVERSAL)
		self.plDfa.SetToolTip("")

		self.plPls = Plsr.Plsr(id=wxID_PYCHEMMAINPLPLS, name="plPls", parent=self.nbMain, pos=wx.Point(0, 0), size=wx.Size(1008, 635), style=wx.TAB_TRAVERSAL)
		self.plPls.SetToolTip("")
		self.plPls.parent = self

		self.plGadfa = Ga.Ga(id=wxID_PYCHEMMAINPLGADFA, name="plGadfa", parent=self.nbMain, pos=wx.Point(0, 0), size=wx.Size(1008, 635), style=wx.TAB_TRAVERSAL, type="DFA")
		self.plGadfa.SetToolTip("")
		self.plGadfa.parent = self

		self.plGapls = Ga.Ga(id=wxID_PYCHEMMAINPLGAPLSC, name="plGaplsc", parent=self.nbMain, pos=wx.Point(0, 0), size=wx.Size(1008, 635), style=wx.TAB_TRAVERSAL, type="PLS")
		self.plGapls.SetToolTip("")
		self.plGapls.parent = self

		self.plUnivariate = Univariate.Univariate(id=wxID_PYCHEMMAINPLUNIVARIATE, name="plUnivariate", parent=self.nbMain, pos=wx.Point(0, 0), size=wx.Size(1008, 635), style=wx.TAB_TRAVERSAL)
		self.plUnivariate.SetToolTip("")
		self.plUnivariate.parent = self

		self._init_coll_nbMain_Pages(self.nbMain)

	def __init__(self, parent):
		self._init_ctrls(parent)

		# set defaults
		self.Reset()

	def OnMainFrameSize(self, event):
		event.Skip()

	##		  self.Layout()
	##		  self.plUnivariate.Refresh()

	def OnTbMainSize(self, event):
		self.tbMain.Refresh()

	def OnMnuHelpContentsMenu(self, event):
		from wx.tools import helpviewer

		helpviewer.main(["", os.path.join("docs", "PAChelp.hhp")])

	def OnMnuAboutContentsMenu(self, event):
		from wx.lib.wordwrap import wordwrap

		info = wx.adv.AboutDialogInfo()
		info.Name = "PyChem"
		info.Version = "3.0.5a Beta"
		info.Copyright = "(C) 2008 Roger Jarvis"
		info.Description = wordwrap("PyChem is a software program for multivariate " "data analysis (MVA).	It includes algorithms for " "calibration and categorical analyses.	 In addition, " "novel genetic algorithm tools for spectral feature " "selection" "\n\nFor more information please go to the PyChem " "website using the link below, or email the project " "author, roger.jarvis@manchester.ac.uk", 350, wx.ClientDC(self))
		info.WebSite = ("http://pychem.sf.net/", "PyChem home page")

		# Then we call wx.adv.AboutBox giving it that info object
		wx.adv.AboutBox(info)

	def OnMnuFileLoadexpMenu(self, event):
		loadFile = wx.FileSelector("Load PyChem Experiment", "", "", "", "XML files (*.xml)|*.xml")
		dlg = wxWorkspaceDialog(self, loadFile)
		try:
			tree = dlg.getTree()
			if tree is not None:
				dlg.ShowModal()
				workSpace = dlg.getWorkspace()
				if workSpace != 0:
					self.Reset()
					self.xmlLoad(tree, workSpace)
					self.data["exppath"] = loadFile
					mb = self.GetMenuBar()
					mb.Enable(wxID_PYCHEMMAINMNUFILESAVEEXP, True)
					mb.Enable(wxID_PYCHEMMAINMNUFILESAVEWS, True)
					mb.Enable(wxID_PYCHEMMAINMNUFILELOADWS, True)
		finally:
			dlg.Destroy()

	def OnMnuFileLoadwsMenu(self, event):
		dlg = wxWorkspaceDialog(self, self.data["exppath"])
		if self.data["exppath"] is not None:
			try:
				dlg.ShowModal()
				workSpace = dlg.getWorkspace()
				if workSpace != 0:
					self.Reset(1)
					tree = dlg.getTree()
					self.xmlLoad(tree, workSpace, "ws")
			finally:
				dlg.Destroy()
		else:
			dlg.Destroy()

	def OnMnuFileSaveexpMenu(self, event):
		dlg = wx.FileDialog(self, "Choose a file", ".", "", "XML files (*.xml)|*.xml", wx.FD_SAVE)
		if self.data["raw"] is not None:
			try:
				if dlg.ShowModal() == wx.ID_OK:
					self.data["exppath"] = dlg.GetPath()
					# workspace name entry dialog
					texTdlg = wx.TextEntryDialog(self, "Type in a name under which to save the current workspace", "Save Workspace as...", "Default")
					try:
						if texTdlg.ShowModal() == wx.ID_OK:
							wsName = texTdlg.GetValue()
					finally:
						texTdlg.Destroy()
					self.xmlSave(self.data["exppath"], wsName, "new")
					# activate workspace save menu option
					mb = self.GetMenuBar()
					mb.Enable(wxID_PYCHEMMAINMNUFILESAVEEXP, True)
					mb.Enable(wxID_PYCHEMMAINMNUFILESAVEWS, True)
					mb.Enable(wxID_PYCHEMMAINMNUFILELOADWS, True)
					# show workspace dialog so that default can be edited
					dlgws = wxWorkspaceDialog(self, self.data["exppath"], dtype="Save")
					try:
						dlgws.ShowModal()
					finally:
						dlgws.Destroy()
			finally:
				dlg.Destroy()
		else:
			dlg.Destroy()

	def OnMnuFileSavewsMenu(self, event):
		if self.data["exppath"] is not None:
			wsName = ""
			# text entry dialog
			dlg = wx.TextEntryDialog(self, "Type in a name under which to save " + "the current workspace", "Save Workspace as...", "Default")
			##			  try:
			if dlg.ShowModal() == wx.ID_OK:
				wsName = dlg.GetValue()
			##			  finally:
			dlg.Destroy()

			# workspace dialog for editing
			if wsName is not "":
				# save workspace to xml file
				self.xmlSave(self.data["exppath"], wsName.replace(" ", "_"), type=self.data["exppath"])

				# show workspace dialog
				dlg = wxWorkspaceDialog(self, self.data["exppath"], dtype="Save")
				try:
					dlg.ShowModal()
					dlg.appendWorkspace(wsName)
				finally:
					dlg.Destroy()
			else:
				dlg = wx.MessageDialog(self, "No workspace name was provided", "Error!", wx.OK | wx.ICON_ERROR)
				try:
					dlg.ShowModal()
				finally:
					dlg.Destroy()

	def OnMnuFileFileimportMenu(self, event):
		dlg = wxImportDialog(self)
		try:
			dlg.ShowModal()
			if dlg.isOK() == 1:
				# Apply default settings
				self.Reset()

				# Load arrays
				wx.BeginBusyCursor()

				if dlg.Transpose() == 0:
					self.data["raw"] = loadtxt(dlg.getFile())
				else:
					self.data["raw"] = scipy.transpose(loadtxt(dlg.getFile()))

				# create additional arrays of experimental data
				self.data["rawtrunc"] = self.data["raw"]
				self.data["proc"] = self.data["raw"]
				self.data["proctrunc"] = self.data["raw"]

				# Resize grids
				expSetup.ResizeGrids(self.plExpset.grdNames, self.data["raw"].shape[0], 3, 2)
				expSetup.ResizeGrids(self.plExpset.grdIndLabels, self.data["raw"].shape[1], 0, 3)

				# activate ctrls
				self.EnableCtrls()

				# set x-range 1 to n
				self.plExpset.indTitleBar.stcRangeFrom.SetValue("1")
				self.plExpset.indTitleBar.stcRangeTo.SetValue(str(self.data["raw"].shape[1]))

				# set plot spn range
				self.plPreproc.titleBar.spcPlotSpectra.SetValue(1)
				self.plPreproc.titleBar.spcPlotSpectra.SetRange(1, self.data["raw"].shape[0])

				# Calculate Xaxis
				self.data["xaxis"] = expSetup.GetXaxis(self.plExpset.indTitleBar.stcRangeFrom.GetValue(), self.plExpset.indTitleBar.stcRangeTo.GetValue(), self.data["raw"].shape[1], self.plExpset.grdIndLabels)

				# Display preview of data
				rows = self.data["raw"].shape[0]
				cols = self.data["raw"].shape[1]
				if (rows > 10) and (cols > 10) is True:
					data = self.data["raw"][0:10, 0:10]
				elif (rows <= 10) and (cols > 10) is True:
					data = self.data["raw"][0:rows, 0:10]
				elif (rows > 10) and (cols <= 10) is True:
					data = self.data["raw"][0:10, 0:cols]
				elif (rows <= 10) and (cols <= 10) is True:
					data = self.data["raw"][0:rows, 0:cols]

				# allow for experiment save on file menu
				mb = self.GetMenuBar()
				mb.Enable(wxID_PYCHEMMAINMNUFILESAVEEXP, True)
				mb.Enable(wxID_PYCHEMMAINMNUFILESAVEWS, False)
				mb.Enable(wxID_PYCHEMMAINMNUFILELOADWS, False)

				dlgConfirm = wxImportConfirmDialog(self, data, rows, cols)
				try:
					dlgConfirm.ShowModal()
				finally:
					dlgConfirm.Destroy()

				wx.EndBusyCursor()

		except Exception as error:
			raise
			wx.EndBusyCursor()
			self.Reset()
			dlg.Destroy()
			errorBox(self, "Unable to load array.\nPlease check file format.")

	def OnMnuFileAppexitMenu(self, event):
		self.Close()

	def OnMnuToolsExpsetMenu(self, event):
		self.nbMain.SetSelection(0)

	def OnMnuToolsPreprocMenu(self, event):
		self.nbMain.SetSelection(1)

	def OnMnuToolsMnupcaMenu(self, event):
		self.nbMain.SetSelection(3)

	def OnMnuToolsMnuclusterMenu(self, event):
		self.nbMain.SetSelection(4)

	def OnMnuToolsMnuplsrMenu(self, event):
		self.nbMain.SetSelection(6)

	def OnMnuToolsMnudfaMenu(self, event):
		self.nbMain.SetSelection(5)

	def OnMnuToolsMnugadfaMenu(self, event):
		self.nbMain.SetSelection(7)

	def OnMnuToolsMnugaplscMenu(self, event):
		self.nbMain.SetSelection(8)

	def OnMnuToolsMnuunivariateMenu(self, event):
		self.nbMain.SetSelection(2)

	def OnMnuGridDeleteColumn(self, event):
		grid = self.data["gridsel"]
		col = grid.GetGridCursorCol()
		this = 0
		if grid == self.plExpset.grdNames:
			if col != 0:
				count = {"Label": 0, "Class": 0, "Validation": 0}
				heads = []
				for i in range(1, grid.GetNumberCols()):
					count[grid.GetCellValue(0, i)] += 1
					heads.append(grid.GetColLabelValue(i))
				this = count[grid.GetCellValue(0, col)]
			if this > 1:
				##				  flag = 1
				##				  #check this col isn't used in a saved workspace
				##				  if self.data['exppath'] is not None:
				##					  tree = ET.ElementTree(file=self.data['exppath'])
				##					  root = tree.getroot()
				##					  #get workspaces subelement
				##					  WSnode = root.findall("Workspaces")[0]
				##					  workspaces = WSnode
				##					  #run through each workspace to see it grid col used
				##					  for each in workspaces:
				##						  for item in each:
				##							  if item.tag == 'Lists':
				##								  for list in item:
				##									  if list.tag == 'depvarsel':
				##										  L = list.text.split('\t')
				##										  Didx = []
				##										  for iL in range(len(L)-1):
				##											  Didx.append(int(iL))
				##						  for Lind in Didx:
				##							  if (Lind < 0) & (-Lind == col) is True:
				##								  flag = 0
				##								  wsdel = each
				##				  if flag == 1:
				msg = "Are you sure you want to delete the column?"
				##				  else:
				##					  msg = 'The workspace "' + wsdel + '" uses this column, if you delete this ' +\
				##							'entry then the workspace must also be deleted.	 Are you sure you want ' +\
				##							'to continue?'
				##
				dlg = wx.MessageDialog(self, msg, "Confirm", wx.OK | wx.CANCEL | wx.ICON_WARNING)
				try:
					if dlg.ShowModal() == wx.ID_OK:
						grid.DeleteCols(col)
						# restore col headings
						del heads[col - 1]
						for i in range(1, len(heads) + 1):
							grid.SetColLabelValue(i, heads[i - 1])
				finally:
					dlg.Destroy()
		else:
			if (grid.GetNumberCols() > 2) & (col > 1) is True:
				dlg = wx.MessageDialog(self, "Are you sure you want to delete the column?", "Confirm", wx.OK | wx.CANCEL | wx.ICON_WARNING)
				try:
					if dlg.ShowModal() == wx.ID_OK:
						heads = []
						for i in range(1, grid.GetNumberCols()):
							heads.append(grid.GetColLabelValue(i))
						grid.DeleteCols(col)
						# restore col headings
						del heads[col - 1]
						for i in range(1, len(heads) + 1):
							grid.SetColLabelValue(i, heads[i - 1])
				finally:
					dlg.Destroy()

	def OnMnuGridResetSort(self, event):
		# order rows in grid by row number
		grid = self.data["gridsel"]
		order = []
		# get index
		for i in range(2, grid.GetNumberRows()):
			order.append(int(grid.GetRowLabelValue(i)))
		index = scipy.argsort(order)
		# create list of grid contents
		gList = []
		for i in index:
			tp = []
			for j in range(grid.GetNumberCols()):
				tp.append(grid.GetCellValue(i + 2, j))
			gList.append(tp)
		# replace current grid contents with ordered
		for i in range(len(gList)):
			grid.SetRowLabelValue(i + 2, str(i + 1))
			for j in range(grid.GetNumberCols()):
				grid.SetCellValue(i + 2, j, gList[i][j])

	def OnMnuGridRowDel(self, event):
		# delete user defined variable row from grdIndLabels
		GridRowDel(self.data["gridsel"], self.data)
		# update experiment details
		self.GetExperimentDetails(case=1)

	def OnMnuGridRenameColumn(self, event):
		grid = self.data["gridsel"]
		col = grid.GetGridCursorCol()
		dlg = wx.TextEntryDialog(self, "", "Enter new column heading", "")
		try:
			if dlg.ShowModal() == wx.ID_OK:
				answer = dlg.GetValue()
				col = grid.GetGridCursorCol()
				grid.SetColLabelValue(col, answer)
		finally:
			dlg.Destroy()

	def OnMnuGridPaste(self, event):
		# Paste cells
		grid = self.data["gridsel"]
		wx.TheClipboard.Open()
		Data = wx.TextDataObject("")
		wx.TheClipboard.GetData(Data)
		wx.TheClipboard.Close()
		Data = Data.GetText()
		X = grid.GetGridCursorRow()
		Y = grid.GetGridCursorCol()
		if grid == self.plExpset.grdNames:
			if X < 2:
				X = 2
			if Y < 1:
				Y = 1
		elif grid == self.plExpset.grdIndLabels:
			if X < 1:
				X = 1
			if Y < 1:
				Y = 1
		Data = Data.split("\n")
		for i in range(len(Data)):
			if X + i < grid.GetNumberRows():
				for j in range(len(Data[0].split("\t"))):
					if Y + j < grid.GetNumberCols():
						item = Data[i].split("\r")[0]
						item = item.split("\t")[j]
						grid.SetCellValue(X + i, Y + j, item)

	def OnMnuGridCopy(self, event):
		grid = self.data["gridsel"]

		From = grid.GetSelectionBlockTopLeft()
		To = grid.GetSelectionBlockBottomRight()
		row = grid.GetGridCursorRow()
		col = grid.GetGridCursorCol()

		if len(From) > 0:
			From = From[0]
			To = To[0]
		else:
			From = (row, col)
			To = (row, col)

		Data = ""
		for i in range(From[0], To[0] + 1):
			for j in range(From[1], To[1] + 1):
				if j < To[1]:
					Data = Data + grid.GetCellValue(i, j) + "\t"
				else:
					Data = Data + grid.GetCellValue(i, j)
			if i < To[0]:
				Data = Data + "\n"

		wx.TheClipboard.Open()
		wx.TheClipboard.SetData(wx.TextDataObject(Data))
		wx.TheClipboard.Close()

	def Reset(self, case=0):
		varList = "'split':None,'processlist':[]," + "'pcscores':None,'pcloads':None,'pcpervar':None," + "'pceigs':None,'pcadata':None,'niporsvd':None," + "'plsloads':None,'pcatype':None," + "'dfscores':None,'dfloads':None,'dfeigs':None," + "'gadfachroms':None,'gadfascores':None," + "'gadfacurves':None,'gaplschroms':None," + "'gaplsscores':None,'gaplscurves':None," + "'gadfadfscores':None,'gadfadfaloads':None," + "'gaplsplsloads':None,'gridsel':None,'plotsel':None," + "'tree':None,'order':None,'plsfactors':None," + "'rmsec':None,'rmsepc':None,'rmsept':None," + "'gacurrentchrom':None,'plspred':None,'pcaloadsym':None," + "'dfaloadsym':None,'plsloadsym':None,'plst':None," + "'plstype':0,'pls_class':None,'gaplstreeorder':None," + "'gadfatreeorder':None,'utest':None,'p_aur':None," + "'indvarlist':None,'depvarlist':None,'plotp':None"

		if case == 0:
			exec('self.data = {"raw":None,"proc":None,"exppath":None,"indlabels":None,' + '"class":None,"label":None,"validation":None,"xaxis":[],' + '"sampleidx":None,"variableidx":None,"rawtrunc":None,' + '"proctrunc":None,' + varList + "}")
			# disable options on file menu
			mb = self.GetMenuBar()
			mb.Enable(wxID_PYCHEMMAINMNUFILESAVEEXP, False)
			mb.Enable(wxID_PYCHEMMAINMNUFILESAVEWS, False)
			mb.Enable(wxID_PYCHEMMAINMNUFILELOADWS, False)
		else:
			exec('self.data = {"raw":self.data["raw"],"proc":self.data["raw"],' + '"exppath":self.data["exppath"],"indlabels":self.data["indlabels"],' + '"class":self.data["class"],"label":self.data["label"],' + '"validation":self.data["validation"],"xaxis":self.data["xaxis"],' + '"sampleidx":self.data["sampleidx"],"variableidx":self.data["variableidx"],' + '"rawtrunc":self.data["rawtrunc"],"proctrunc":self.data["proctrunc"],' + varList + "}")

		# for returning application to default settings
		self.plPreproc.Reset()
		self.plExpset.Reset(case)
		self.plPca.Reset()
		self.plDfa.Reset()
		self.plCluster.Reset()
		self.plPls.Reset()
		self.plGadfa.Reset()
		self.plGapls.Reset()
		self.plUnivariate.Reset()

		# make data dictionary available to modules
		self.plExpset.depTitleBar.getData(self.data)
		self.plExpset.indTitleBar.getData(self.data)
		self.plPreproc.titleBar.getData(self.data)
		self.plPca.titleBar.getData(self.data)
		self.plCluster.titleBar.getData(self.data)
		self.plDfa.titleBar.getData(self.data)
		self.plPls.titleBar.getData(self.data)
		self.plUnivariate.titleBar.getData(self.data)
		self.plGadfa.titleBar.getData(self.data)
		self.plGadfa.titleBar.getExpGrid(self.plExpset.grdNames)
		self.plGadfa.titleBar.getValSplitPc(self.plExpset.depTitleBar.spcGenMask.GetValue())
		self.plGapls.titleBar.getData(self.data)
		self.plGapls.titleBar.getValSplitPc(self.plExpset.depTitleBar.spcGenMask.GetValue())
		self.plGapls.titleBar.getExpGrid(self.plExpset.grdNames)

	def xmlSave(self, path, workspace, type=None):
		# type is either "new" (in which case workspace = "Default")
		# or path to saved xml file

		wx.BeginBusyCursor()

		proceed = 1
		if type is "new":
			# build a tree structure
			root = ET.Element("pychem_305_experiment")
			# save raw data
			rawdata = ET.SubElement(root, "rawdata")
			rawdata.set("key", "array")
			rawdata.text = str_array(self.data["raw"], col_sep="\t")
			# save grdindlabels content
			indgrid = ET.SubElement(root, "indgrid")
			# get data
			g = self.getGrid(self.plExpset.grdIndLabels)
			# save grid
			indgrid.set("key", "indgrid")
			indgrid.text = g
			# add workspace subelement
			Workspaces = ET.SubElement(root, "Workspaces")
			nws = 1
		else:
			tree = ET.ElementTree(file=type)
			root = tree.getroot()
			# delete old raw data and exp setup stuff
			for each in root:
				if each.tag in ["rawdata", "indgrid"]:
					root.remove(each)
			# save raw data in case any user defined variables created
			rawdata = ET.SubElement(root, "rawdata")
			rawdata.set("key", "array")
			rawdata.text = str_array(self.data["raw"], col_sep="\t")
			# save grdindlabels content
			indgrid = ET.SubElement(root, "indgrid")
			# get data
			g = self.getGrid(self.plExpset.grdIndLabels)
			# save grid
			indgrid.set("key", "indgrid")
			indgrid.text = g
			# get workspaces subelement
			ch = root
			for each in ch:
				if each.tag == "Workspaces":
					Workspaces = each
			# check that workspace name is not currently used
			cWs = Workspaces
			nws = len(Workspaces)
			for each in cWs:
				if each.tag == workspace:
					dlg = wx.MessageDialog(self, "The workspace name provided is currently used\n" " for this experiment, please try again", "Error!", wx.OK | wx.ICON_ERROR)
					try:
						dlg.ShowModal()
						proceed = 0
					finally:
						dlg.Destroy()

		# add new workspace
		if proceed == 1:
			try:
				locals()[workspace] = ET.SubElement(Workspaces, workspace)

				# save experiment setup stuff
				wxGrids = ["plExpset.grdNames", "plExpset.grdIndLabels"]
				grid = ET.SubElement(locals()[workspace], "grid")
				for each in wxGrids:
					name = each.split(".")[len(each.split(".")) - 1]
					# get data
					g = self.getGrid(getByPath(self, each))
					locals()[name] = ET.SubElement(grid, each)
					# save grid
					locals()[name].set("key", "grid")
					locals()[name].text = g

				# get preprocessing options
				if len(self.data["processlist"]) != 0:
					ppOptions = ET.SubElement(locals()[workspace], "ppOptions")
					for each in self.data["processlist"]:
						item = ET.SubElement(ppOptions, "item")
						item.set("key", "int")
						item.text = str(each)

				##				  #save 1D lists as a string
				##				  Lists = ET.SubElement(locals()[workspace],"Lists")
				##				  #lists
				##				  listOfLists = ['depvarsel']
				##
				##				  for each in listOfLists:
				##					  L = self.data[each]
				##					  sL = ''
				##					  for item in L:
				##						  sL = sL + str(item) + '\t'
				##					  locals()[each] = ET.SubElement(Lists, each)
				##					  locals()[each].set("key", "list")
				##					  locals()[each].text = sL

				# save spin, string and boolean ctrl values
				Controls = ET.SubElement(locals()[workspace], "Controls")
				# spin controls
				spinCtrls = ["plGadfa.titleBar.spnGaScoreFrom", "plGadfa.titleBar.spnGaScoreTo", "plGadfa.optDlg.spnGaMaxFac", "plGadfa.optDlg.spnGaMaxGen", "plGadfa.optDlg.spnGaVarsFrom", "plGadfa.optDlg.spnGaVarsTo", "plGadfa.optDlg.spnGaNoInds", "plGadfa.optDlg.spnGaNoRuns", "plGadfa.optDlg.spnGaRepUntil", "plGadfa.optDlg.spnResample", "plGapls.titleBar.spnGaScoreFrom", "plGapls.titleBar.spnGaScoreTo", "plGapls.optDlg.spnGaMaxFac", "plGapls.optDlg.spnGaMaxGen", "plGapls.optDlg.spnGaVarsFrom", "plGapls.optDlg.spnGaVarsTo", "plGapls.optDlg.spnGaNoInds", "plGapls.optDlg.spnGaNoRuns", "plGapls.optDlg.spnGaRepUntil", "plGapls.optDlg.spnResample", "plPls.titleBar.spnPLSmaxfac", "plPls.titleBar.spnPLSfactor1", "plPls.titleBar.spnPLSfactor2", "plPca.titleBar.spnNumPcs1", "plPca.titleBar.spnNumPcs2", "plPca.titleBar.spnPCAnum", "plDfa.titleBar.spnDfaDfs", "plDfa.titleBar.spnDfaScore1", "plDfa.titleBar.spnDfaScore2", "plDfa.titleBar.spnDfaPcs"]

				for each in spinCtrls:
					name = each.split(".")[len(each.split(".")) - 1]
					locals()[name] = ET.SubElement(Controls, each)
					locals()[name].set("key", "int")
					locals()[name].text = str(getByPath(self, each).GetValue())

				# string controls
				stringCtrls = ["plExpset.indTitleBar.stcRangeFrom", "plExpset.indTitleBar.stcRangeTo", "plGadfa.optDlg.stGaXoverRate", "plGadfa.optDlg.stGaMutRate", "plGadfa.optDlg.stGaInsRate", "plGapls.optDlg.stGaXoverRate", "plGapls.optDlg.stGaMutRate", "plGapls.optDlg.stGaInsRate"]

				for each in stringCtrls:
					# quick fix!
					if each == "plExpset.indTitleBar.stcRangeFrom":
						if self.plExpset.indTitleBar.stcRangeFrom.GetValue() in [""]:
							self.plExpset.indTitleBar.stcRangeFrom.SetValue("1")
					if each == "plExpset.indTitleBar.stcRangeTo":
						if self.plExpset.indTitleBar.stcRangeTo.GetValue() in [""]:
							self.plExpset.indTitleBar.stcRangeTo.SetValue(str(self.data["raw"].shape[1]))

					name = each.split(".")[len(each.split(".")) - 1]

					locals()[name] = ET.SubElement(Controls, each)
					locals()[name].set("key", "str")
					locals()[name].text = getByPath(self, each).GetValue()

				boolCtrls = ["plCluster.optDlg.rbKmeans", "plCluster.optDlg.rbKmedian", "plCluster.optDlg.rbKmedoids", "plCluster.optDlg.rbHcluster", "plCluster.optDlg.rbSingleLink", "plCluster.optDlg.rbMaxLink", "plCluster.optDlg.rbAvLink", "plCluster.optDlg.rbCentLink", "plCluster.optDlg.rbEuclidean", "plCluster.optDlg.rbCorrelation", "plCluster.optDlg.rbAbsCorr", "plCluster.optDlg.rbUncentredCorr", "plCluster.optDlg.rbAbsUncentCorr", "plCluster.optDlg.rbSpearmans", "plCluster.optDlg.rbKendalls", "plCluster.optDlg.rbCityBlock", "plCluster.optDlg.rbPlotName", "plCluster.optDlg.rbPlotColours", "plGadfa.optDlg.cbGaRepUntil", "plGadfa.optDlg.cbGaMaxGen", "plGadfa.optDlg.cbGaMut", "plGadfa.optDlg.cbGaXover", "plDfa.titleBar.cbDfaXval"]

				for each in boolCtrls:
					name = each.split(".")[len(each.split(".")) - 1]
					locals()[name] = ET.SubElement(Controls, each)
					locals()[name].set("key", "bool")
					locals()[name].text = str(getByPath(self, each).GetValue())

				# save choice options
				Choices = ET.SubElement(locals()[workspace], "Choices")
				choiceCtrls = ["plPls.titleBar.cbxData", "plPca.titleBar.cbxPcaType", "plPca.titleBar.cbxPreprocType", "plPca.titleBar.cbxData", "plDfa.titleBar.cbxData", "plCluster.titleBar.cbxData", "plGadfa.titleBar.cbxFeature1", "plGadfa.titleBar.cbxFeature2", "plGapls.titleBar.cbxFeature1", "plGapls.titleBar.cbxFeature2", "plGadfa.titleBar.cbxData", "plGapls.titleBar.cbxData", "plPls.titleBar.cbxType", "plPls.titleBar.cbxPreprocType", "plUnivariate.titleBar.cbxData", "plUnivariate.titleBar.cbxVariable", "plUnivariate.titleBar.cbxTest"]

				for each in choiceCtrls:
					name = each.split(".")[len(each.split(".")) - 1]
					locals()[name] = ET.SubElement(Choices, each)
					locals()[name].set("key", "int")
					locals()[name].text = str(getByPath(self, each).GetCurrentSelection())

				# any scipy arrays
				scipyArrays = ["pcscores", "pcloads", "pcpervar", "pceigs", "plsloads", "dfscores", "dfloads", "dfeigs", "gadfachroms", "gadfascores", "gadfacurves", "gaplschroms", "gaplsscores", "gaplscurves", "gadfadfscores", "gadfadfloads", "gaplsplsloads", "p_aur"]

				Array = ET.SubElement(locals()[workspace], "Array")
				for each in scipyArrays:
					try:
						# save array elements
						isthere = self.data[each]
						if isthere != None:
							if each not in ["p_aur"]:  # for numeric array
								locals()["item" + each] = ET.SubElement(Array, each)
								arrData = str_array(self.data[each],col_sep="\t")
								locals()["item" + each].set("key", "array")
								locals()["item" + each].text = arrData
							else:  # for string array type
								target = self.data[each]
								arrData = ""
								for row in target:
									for element in row:
										arrData = arrData + element + "\t"
									arrData = arrData[0 : len(arrData) - 1] + "\n"
								locals()["item" + each] = ET.SubElement(Array, each)
								locals()["item" + each].set("key", "array")
								locals()["item" + each].text = arrData[0:len(arrData)-1]
					except:
						continue

				# create run clustering flag
				Flags = ET.SubElement(locals()[workspace], "Flags")

				doClustering = ET.SubElement(Flags, "doClustering")
				doClustering.set("key", "int")
				if (self.data["tree"] is not None) is True:
					doClustering.text = "1"
				else:
					doClustering.text = "0"

				# create run plsr flag global variable
				doPlsr = ET.SubElement(Flags, "doPlsr")
				doPlsr.set("key", "int")
				if self.data["plsloads"] is not None:
					doPlsr.text = "1"
				else:
					doPlsr.text = "0"

				# create plot univariate flag
				doUni = ET.SubElement(Flags, "doUni")
				doUni.set("key", "int")
				if self.data["plotp"] is not None:
					doUni.text = str(self.data["plotp"])
				else:
					doUni.text = "0"

				# wrap it in an ElementTree instance, and save as XML
				tree = ET.ElementTree(root)
				tree.write(path)

				# enable menu options
				self.mnuMain.Enable(wxID_PYCHEMMAINMNUFILESAVEWS, True)
				self.mnuMain.Enable(wxID_PYCHEMMAINMNUFILELOADWS, True)

			except Exception as error:
				raise
				dlg = wx.MessageDialog(self, "Unable to save under current name.\n\nCharacters " + 'such as "%", "&", "-", "+" can not be used for the workspace name', "Error!", wx.OK | wx.ICON_ERROR)
				try:
					dlg.ShowModal()
				finally:
					dlg.Destroy()

		# end busy cursor
		wx.EndBusyCursor()

	def xmlLoad(self, tree, workspace, type="new"):
		# load pychem experiments from saved xml files
		##		  if type == 'new':
		# load raw data
		rdArray = []
		getRows = tree.findtext("rawdata")
		rows = getRows.split("\n")
		for each in rows:
			newRow = []
			items = each.split("\t")
			for item in items:
				if item not in ["", " "]:
					newRow.append(float(item))
			rdArray.append(newRow)
		self.data["raw"] = np.array(rdArray)
		self.data["proc"] = self.data["raw"]
		# load grdindlabels
		gCont = tree.findtext("indgrid")
		rows = gCont.split("\n")
		r = len(rows) - 3
		c = len(rows[0].split("\t")) - 2
		# size grid accordingly
		expSetup.ResizeGrids(self.plExpset.grdIndLabels, r, c - 1, type=-1)
		# add column labels
		cl = rows[0].split("\t")
		for col in range(1, len(cl)):
			self.plExpset.grdIndLabels.SetColLabelValue(col - 1, cl[col])
		for row in range(1, len(rows) - 1):
			items = rows[row].split("\t")
			self.plExpset.grdIndLabels.SetRowLabelValue(row - 1, items[0])
			for ci in range(1, len(items) - 1):
				self.plExpset.grdIndLabels.SetCellValue(row - 1, ci - 1, items[ci])
		# set read only and grey background
		grid = self.plExpset.grdIndLabels
		for rx in range(1, grid.GetNumberRows()):
			if len(grid.GetRowLabelValue(rx).split("U")) > 1:
				grid.SetReadOnly(rx, 1, 1)
				grid.SetCellBackgroundColour(rx, 1, wx.LIGHT_GREY)
			else:
				break

		# load workspace
		getWsElements = tree.getroot().findall("".join(("*/", workspace)))[0]

		for each in getWsElements:
			if each.tag == "grid":
				gName = each
				for item in gName:
					gCont = item.text
					rows = gCont.split("\n")
					r = len(rows) - 3
					c = len(rows[0].split("\t")) - 2
					# size grid accordingly
					if item.tag in ["plExpset.grdNames"]:
						expSetup.ResizeGrids(getByPath(self, item.tag), r, c - 1, type=0)
						##					  else:
						##						  expSetup.ResizeGrids(getByPath(self, item.tag), r, c-1, type=-1)
						# add column labels
						cl = rows[0].split("\t")
						for col in range(1, len(cl)):
							getByPath(self, item.tag).SetColLabelValue(exec(str(col - 1) + "," + '"' + cl[col] + '"'))
						for row in range(1, len(rows) - 1):
							items = rows[row].split("\t")
							getByPath(self, item.tag).SetRowLabelValue(exec(str(row - 1) + "," + '"' + items[0] + '"'))
							for ci in range(1, len(items) - 1):
								getByPath(self, item.tag).SetCellValue(exec(str(row - 1) + "," + str(ci - 1) + "," + '"' + items[ci] + '"'))
						# set read only and grey background
						grid = getByPath(self, item.tag)
						for rx in range(1, grid.GetNumberRows()):
							if len(grid.GetRowLabelValue(rx).split("U")) > 1:
								grid.SetReadOnly(rx, 1, 1)
								grid.SetCellBackgroundColour(rx, 1, wx.LIGHT_GREY)
							else:
								break
						# Validation column renderer for grdnames
						##						  if grid == self.plExpset.grdNames:
						expSetup.SetValidationEditor(grid)

					else:  # just set check boxes for grdindlabels
						for row in range(1, len(rows) - 1):
							items = rows[row].split("\t")
							if len(items[0].split("U")) == 1:  # spectral variable
								self.plExpset.grdIndLabels.SetCellValue(row - 1, 0, items[1])

				# set exp details
				self.GetExperimentDetails()

			# apply preprocessing steps
			if each.tag == "ppOptions":
				getOpts = each
				for item in getOpts:
					self.plPreproc.optDlg.lbSpectra1.SetSelection(int(item.text) - 1)
					Selected = self.plPreproc.optDlg.lbSpectra1.GetSelection()
					SelectedText = self.plPreproc.optDlg.lbSpectra1.GetStringSelection()
					if SelectedText[0:2] == "  ":
						self.data["processlist"].append(int(item.text))
						self.plPreproc.optDlg.lbSpectra2.Append(SelectedText[2 : len(SelectedText)])
				self.plPreproc.titleBar.RunProcessingSteps()

			##			  #load lists
			##			  if each.tag == 'Lists':
			##				  getLists = each
			##				  for item in getLists:
			##					  L = item.text.split('\t')
			##					  lL = []
			##					  for iL in range(len(L)-1):
			##						  lL.append(int(L[iL]))#wrong!!
			##						  if int(L[iL]) < 0: #set column selections here
			##							  self.plExpset.grdNames.SetCellValue(1,iL+1,'1')
			##						  else:
			##							  self.plExpset.grdNames.SetCellValue(1,iL+1,'0')
			##					  self.data[item.tag]=lL

			# load ctrl values
			if each.tag == "Controls":
				getVars = each
				for item in getVars:
					getByPath(self, item.tag).SetValue(exec(list(item.items())[0][1] + "(" + item.text + ")"))

			# load choice values
			if each.tag == "Choices":
				getVars = each
				for item in getVars:
					getByPath(self, item.tag).SetSelection(exec(list(item.items())[0][1] + "(" + item.text + ")"))

			# load arrays
			if each.tag == "Array":
				getArrays = each
				for array in getArrays:
					try:
						newArray = []
						makeArray = array.text
						makeArray = makeArray.split("\n")
						for row in makeArray:
							getRow = []
							row = row.split("\t")
							for element in row:
								if array.tag not in ["p_aur"]:
									getRow.append(float(element))
								else:
									getRow.append(element)
							newArray.append(getRow)
						self.data[array.tag] = np.array(newArray)

					except:
						self.data[array.tag] = None

				# reload any plots
				for array in getArrays:
					for i in ["pc", "dfs", "gadfa", "gapls"]:
						if len(array.tag.split(i)) > 1:
							if i == "pc":
								# set spn limits
								self.plPca.titleBar.spnNumPcs1.SetRange(1, len(self.data["pceigs"]))
								self.plPca.titleBar.spnNumPcs2.SetRange(1, len(self.data["pceigs"]))
								# check for metadata & setup limits for dfa
								if (sum(self.data["class"][:, 0]) != 0) and (self.data["class"] is not None):
									self.plDfa.titleBar.spnDfaPcs.SetRange(2, len(self.data["pceigs"]))
									self.plDfa.titleBar.spnDfaDfs.SetRange(1, len(scipy.unique(self.data["class"][:, 0])) - 1)
								# plot pca results
								self.plPca.titleBar.PlotPca()
							elif i == "dfs":
								# set spn limits
								self.plDfa.titleBar.spnDfaScore1.SetRange(1, self.data["dfeigs"].shape[1])
								self.plDfa.titleBar.spnDfaScore2.SetRange(1, self.data["dfeigs"].shape[1])
								# plot results
								self.plDfa.titleBar.plotDfa()

							elif i == "gadfa":
								try:
									self.plGadfa.titleBar.CreateGaResultsTree(self.plGadfa.optDlg.treGaResults, gacurves=self.data["gadfacurves"], chroms=self.data["gadfachroms"], varfrom=self.plGadfa.optDlg.spnGaVarsFrom.getValue(), varto=self.plGadfa.optDlg.spnGaVarsTo.getValue(), runs=self.plGadfa.optDlg.spnGaNoRuns.getValue() - 1)
								except:
									continue
							elif i == "gapls":
								try:
									self.plGapls.titleBar.CreateGaResultsTree(self.plGapls.optDlg.treGaResults, gacurves=self.data["gaplscurves"], chroms=self.data["gaplschroms"], varfrom=self.plGapls.optDlg.spnGaVarsFrom.getValue(), varto=self.plGapls.optDlg.spnGaVarsTo.getValue(), runs=self.plGapls.optDlg.spnGaNoRuns.getValue() - 1)
								except:
									continue

			# load flags for re-running cluster
			# analysis, plsr and plotting univariate test output
			if each.tag == "Flags":
				getVars = each
				for item in getVars:
					if (item.tag == "doClustering") & (item.text == "1") is True:
						self.plCluster.titleBar.RunClustering()
					elif (item.tag == "doPlsr") & (item.text == "1") is True:
						self.plPls.titleBar.runPls()
					elif (item.tag == "doUni") & (item.text != "0") is True:
						if self.plUnivariate.titleBar.cbxData.GetSelection() == 0:
							x = scipy.take(self.data["rawtrunc"], [self.plUnivariate.titleBar.cbxVariable.GetSelection()], 1)
						elif self.plUnivariate.titleBar.cbxData.GetSelection() == 1:
							x = scipy.take(self.data["proctrunc"], [self.plUnivariate.titleBar.cbxVariable.GetSelection()], 1)
						if self.plUnivariate.titleBar.cbxTest.GetSelection() < 2:
							self.data["utest"] = [self.plUnivariate.titleBar.cbxTest.GetSelection(), self.plUnivariate.titleBar.cbxData.GetSelection()]
							self.plUnivariate._init_class_sizers()
							self.plUnivariate.titleBar.PlotResults(x, float(item.text), scipy.unique(np.array(self.data["label"])), ["black", "blue", "red", "cyan", "green"], psum=True)
						else:
							self.data["utest"] = None
							self.plUnivariate._init_corr_sizers()
							self.plUnivariate.titleBar.RunUnivariate()

		# unlock ctrls
		self.EnableCtrls()

	##		  #gather data
	##		  self.GetExperimentDetails()

	def getGrid(self, grid):
		r = grid.GetNumberRows()
		c = grid.GetNumberCols()

		# get column labels
		gridout = "\t"
		for i in range(c):
			gridout = gridout + grid.GetColLabelValue(i) + "\t"
		gridout = gridout + "\n"
		# get grid contents & row labels
		for i in range(r):
			row = ""
			row = row + grid.GetRowLabelValue(i) + "\t"
			for j in range(c):
				row = row + grid.GetCellValue(i, j) + "\t"
			gridout = gridout + row + "\n"

		return gridout

	def GetExperimentDetails(self, case=0):
		if self.data["raw"] is not None:
			self.plExpset.grdNames.SetGridCursor(2, 0)
			self.plExpset.grdIndLabels.SetGridCursor(1, 0)
			# show busy egg timer
			wx.BeginBusyCursor()
			# count active samples and get index to sort by
			countActive, order = 0, []
			for i in range(2, self.plExpset.grdNames.GetNumberRows()):
				if self.plExpset.grdNames.GetCellValue(i, 0) == "1":
					order.append(int(self.plExpset.grdNames.GetRowLabelValue(i)))
					countActive += 1
			index = scipy.argsort(order)
			# index for removing samples from analysis
			self.data["sampleidx"] = scipy.sort(np.array(order) - 1).tolist()
			# get col headings
			colHeads, self.data["class"], classCols = [], [], 0
			for i in range(1, self.plExpset.grdNames.GetNumberCols()):
				colHeads.append(self.plExpset.grdNames.GetColLabelValue(i))
				# get label vector
				if (self.plExpset.grdNames.GetCellValue(0, i) == "Label") and (self.plExpset.grdNames.GetCellValue(1, i) == "1") is True:
					self.data["label"] = []
					for j in range(2, self.plExpset.grdNames.GetNumberRows()):
						if self.plExpset.grdNames.GetCellValue(j, 0) == "1":
							##							  self.data['sampleidx'].append(j-2) #for removing samples from analysis
							self.data["label"].append(self.plExpset.grdNames.GetCellValue(j, i))

					# reorder by index
					##					  self.data['sampleidx'] = np.array(self.data['sampleidx'])[index].tolist()
					self.data["label"] = np.array(self.data["label"])[index].tolist()

				# get class vector
				if (self.plExpset.grdNames.GetCellValue(0, i) == "Class") and (self.plExpset.grdNames.GetCellValue(1, i) == "1") is True:

					if self.data["class"] == []:
						self.data["class"] = scipy.zeros((countActive, 1))
					else:
						self.data["class"] = scipy.concatenate((self.data["class"], scipy.zeros((countActive, 1))), 1)

					countSample = 0
					for j in range(2, self.plExpset.grdNames.GetNumberRows()):
						if self.plExpset.grdNames.GetCellValue(j, 0) == "1":
							try:
								self.data["class"][countSample, classCols] = float(self.plExpset.grdNames.GetCellValue(j, i))
							except:
								pass
							countSample += 1
					classCols += 1

					# reorder by index
					self.data["class"] = self.data["class"][index, :]

					# set max dfs that can be calculated
					self.plDfa.titleBar.spnDfaDfs.SetRange(1, len(scipy.unique(self.data["class"][:, 0])) - 1)
				##				  self.plCluster.titleBar.dlg.spnNumClass.SetValue(max(self.data['class']))

				# get validation vector
				if (self.plExpset.grdNames.GetCellValue(0, i) == "Validation") and (self.plExpset.grdNames.GetCellValue(1, i) == "1") is True:
					self.data["validation"] = []
					for j in range(2, self.plExpset.grdNames.GetNumberRows()):
						if self.plExpset.grdNames.GetCellValue(j, 0) == "1":
							try:
								if self.plExpset.grdNames.GetCellValue(j, i) == "Train":
									self.data["validation"].append(0)
								elif self.plExpset.grdNames.GetCellValue(j, i) == "Validation":
									self.data["validation"].append(1)
								elif self.plExpset.grdNames.GetCellValue(j, i) == "Test":
									self.data["validation"].append(2)
								else:
									self.data["validation"].append(0)
							except:
								continue
					self.data["validation"] = np.array(self.data["validation"])

					# reorder by index
					self.data["validation"] = self.data["validation"][index]

			# get x-axis labels/values
			self.plUnivariate.titleBar.cbxVariable.Clear()
			for j in range(1, self.plExpset.grdIndLabels.GetNumberCols()):
				if self.plExpset.grdIndLabels.GetCellValue(0, j) == "1":
					self.data["variableidx"] = []
					self.data["indlabelsfull"] = []
					self.data["xaxisfull"] = []
					for i in range(1, self.plExpset.grdIndLabels.GetNumberRows()):
						val = self.plExpset.grdIndLabels.GetCellValue(i, j)
						self.data["indlabelsfull"].append(val)
						# for removing variables from analysis
						if self.plExpset.grdIndLabels.GetCellValue(i, 0) == "1":
							self.data["variableidx"].append(i - 1)
							# append to list of variables for univariate testing
							self.plUnivariate.titleBar.cbxVariable.Append(val)
						# check for float or txt
						try:
							self.data["xaxisfull"].append(float(val))
						except:
							self.data["xaxisfull"].append(val)

			self.plUnivariate.titleBar.cbxVariable.SetSelection(0)

			self.data["xaxis"] = []
			for each in self.data["variableidx"]:
				self.data["xaxis"].append(self.data["xaxisfull"][each])
			self.data["xaxis"] = np.array(self.data["xaxis"])[:, nA]
			num = 1
			for row in range(len(self.data["xaxis"])):
				try:
					val = float(self.data["xaxis"][row, 0])
				except:
					num = 0
			# xaxis values not numeric therefore define xaxis range
			if num == 0:
				self.data["xaxisfull"] = scipy.arange(1, self.data["raw"].shape[1] + 1)
				self.data["xaxis"] = scipy.take(self.data["xaxisfull"], self.data["variableidx"])[:, nA]

			self.data["indlabels"] = scipy.take(np.array(self.data["indlabelsfull"]), self.data["variableidx"]).tolist()

			##			  #if any udv's have been calculated then possible that data array larger than
			##			  #number of rows in indlabels
			##			  nL = self.plExpset.grdIndLabels.GetNumberRows()-1
			##			  rS = self.data['raw'].shape[1]
			##			  if rS > nL:
			##				  self.data['raw'] = self.data['raw'][:,rS-nL:rS]
			##				  #run pre-processing funcs
			##				  self.plPreproc.titleBar.RunProcessingSteps()

			# remove any unwanted samples & variables, always following any preprocessing
			self.data["rawtrunc"] = scipy.take(self.data["raw"], self.data["variableidx"], 1)
			self.data["rawtrunc"] = scipy.take(self.data["rawtrunc"], self.data["sampleidx"], 0)

			if self.data["proc"] is not None:
				self.data["proctrunc"] = scipy.take(self.data["proc"], self.data["variableidx"], 1)
				self.data["proctrunc"] = scipy.take(self.data["proctrunc"], self.data["sampleidx"], 0)

			# change ga results lists
			try:
				self.plGapls.titleBar.CreateGaResultsTree(self.plGapls.optDlg.treGaResults, gacurves=self.data["gaplscurves"], chroms=self.data["gaplschroms"], varfrom=self.plGapls.optDlg.spnGaVarsFrom.GetValue(), varto=self.plGapls.optDlg.spnGaVarsTo.GetValue(), runs=self.plGapls.optDlg.spnGaNoRuns.GetValue() - 1)
				self.plGapls.titleBar.btnExportGa.Enable(1)
			except:
				pass

			try:
				self.plGadfa.titleBar.CreateGaResultsTree(self.plGadfa.optDlg.treGaResults, gacurves=self.data["gadfacurves"], chroms=self.data["gadfachroms"], varfrom=self.plGadfa.optDlg.spnGaVarsFrom.GetValue(), varto=self.plGadfa.optDlg.spnGaVarsTo.GetValue(), runs=self.plGadfa.optDlg.spnGaNoRuns.GetValue() - 1)
				self.plGadfa.titleBar.btnExportGa.Enable(1)
			except:
				pass

			try:  # set number of centroids for cluster analysis based on class structure
				self.plCluster.optDlg.spnNumClass.SetValue(len(scipy.unique(self.data["class"][:, 0])))
			except:
				pass

			# check if necessary to do a soft reset
			if case == 0:
				if self.data["indvarlist"] is not None:
					if (self.data["indvarlist"] != self.data["variableidx"]) | (self.data["depvarlist"] != self.data["sampleidx"]) is True:
						dlg = wx.MessageDialog(self, "Changes have been made to the samples and/or " + "variables selected for analysis, the system must be reset.	Would you " + "like to continue without saving your current work?", caption="Attention!", style=wx.OK | wx.CANCEL | wx.CENTRE | wx.ICON_QUESTION)
						if dlg.ShowModal() == wx.ID_OK:
							# clear all modelling screens
							self.Reset(1)
						else:
							# set checkmarks to original
							for ri in range(2, self.plExpset.grdNames.GetNumberRows()):
								if ri - 2 in self.data["depvarlist"]:
									self.plExpset.grdNames.SetCellValue(ri, 0, "1")
								else:
									self.plExpset.grdNames.SetCellValue(ri, 0, "0")
							for ri in range(1, self.plExpset.grdIndLabels.GetNumberRows()):
								if ri - 1 in self.data["indvarlist"]:
									self.plExpset.grdIndLabels.SetCellValue(ri, 0, "1")
								else:
									self.plExpset.grdIndLabels.SetCellValue(ri, 0, "0")
					else:
						# save indices to compare to next
						self.data["indvarlist"] = self.data["variableidx"]
						self.data["depvarlist"] = self.data["sampleidx"]
				else:
					# save indices to compare to next
					self.data["indvarlist"] = self.data["variableidx"]
					self.data["depvarlist"] = self.data["sampleidx"]
			else:
				# save indices to compare to next
				self.data["indvarlist"] = self.data["variableidx"]
				self.data["depvarlist"] = self.data["sampleidx"]

			# remove egg timer
			wx.EndBusyCursor()

	def EnableCtrls(self):
		self.plExpset.grdNames.Enable(1)
		self.plExpset.depTitleBar.btnImportMetaData.Enable(1)
		self.plExpset.depTitleBar.btnAddName.Enable(1)
		self.plExpset.depTitleBar.btnAddClass.Enable(1)
		self.plExpset.depTitleBar.btnAddMask.Enable(1)

		self.plExpset.grdIndLabels.Enable(1)
		self.plExpset.indTitleBar.btnImportIndVar.Enable(1)
		self.plExpset.indTitleBar.btnInsertRange.Enable(1)

		self.plPreproc.titleBar.btnPlot.Enable(1)
		self.plPreproc.titleBar.btnInteractive.Enable(1)
		self.plPreproc.titleBar.btnExportData.Enable(1)

		self.plPca.titleBar.btnRunPCA.Enable(1)

		self.plCluster.titleBar.btnRunClustering.Enable(1)

		self.plDfa.titleBar.btnRunDfa.Enable(1)

		self.plPls.titleBar.btnRunFullPls.Enable(1)

		self.plGadfa.titleBar.btnRunGa.Enable(1)

		self.plGapls.titleBar.btnRunGa.Enable(1)

		self.plUnivariate.titleBar.btnRunTest.Enable(1)

	def OnNbMainNotebookPageChanging(self, event):
		if self.nbMain.GetSelection() == 0:
			self.GetExperimentDetails()


class wxImportConfirmDialog(wx.Dialog):
	def _init_importconf_ctrls(self, prnt):
		# generated method, don't edit
		wx.Dialog.__init__(self, id=wxID_WXIMPORTCONFIRMDIALOG, name="wx.ImportDialog", parent=prnt, pos=wx.Point(483, 225), size=wx.Size(313, 319), style=wx.DEFAULT_DIALOG_STYLE, title="Import Complete")
		self.SetClientSize(wx.Size(305, 285))
		self.SetToolTip("")
		self.Center(wx.BOTH)

		self.swLoadX = wx.adv.SashWindow(id=wxID_WXIMPORTCONFIRMDIALOGSWLOADX, name="swLoadX", parent=self, pos=wx.Point(0, 0), size=wx.Size(408, 352), style=wx.CLIP_CHILDREN | wx.adv.SW_3D)
		self.swLoadX.SetToolTip("")

		self.btnOK = wx.Button(id=wxID_WXIMPORTCONFIRMDIALOGBTNOK, label="OK", name="btnOK", parent=self.swLoadX, pos=wx.Point(104, 248), size=wx.Size(104, 26), style=0)
		self.btnOK.Bind(wx.EVT_BUTTON, self.OnBtnOKButton, id=wxID_WXIMPORTCONFIRMDIALOGBTNOK)

		self.grdSampleData = wx.grid.Grid(id=wxID_WXIMPORTCONFIRMDIALOGGRDSAMPLEDATA, name="grdSampleData", parent=self.swLoadX, pos=wx.Point(16, 24), size=wx.Size(272, 208), style=wx.DOUBLE_BORDER)
		self.grdSampleData.SetDefaultColSize(80)
		self.grdSampleData.SetDefaultRowSize(20)
		self.grdSampleData.Enable(True)
		self.grdSampleData.EnableEditing(False)
		self.grdSampleData.SetToolTip("")
		self.grdSampleData.SetColLabelSize(20)
		self.grdSampleData.SetRowLabelSize(20)

		self.staticText1 = wx.StaticText(id=wxID_WXIMPORTCONFIRMDIALOGSTATICTEXT1, label="Sample Data: ", name="staticText1", parent=self.swLoadX, pos=wx.Point(16, 8), size=wx.Size(67, 13), style=0)
		self.staticText1.SetToolTip("")

		self.stRows = wx.StaticText(id=wxID_WXIMPORTCONFIRMDIALOGSTROWS, label="0", name="stRows", parent=self.swLoadX, pos=wx.Point(88, 8), size=wx.Size(32, 13), style=0)

		self.staticText2 = wx.StaticText(id=wxID_WXIMPORTCONFIRMDIALOGSTATICTEXT2, label="rows by ", name="staticText2", parent=self.swLoadX, pos=wx.Point(128, 8), size=wx.Size(39, 13), style=0)

		self.stCols = wx.StaticText(id=wxID_WXIMPORTCONFIRMDIALOGSTCOLS, label="0", name="stCols", parent=self.swLoadX, pos=wx.Point(176, 8), size=wx.Size(32, 13), style=0)

		self.staticText4 = wx.StaticText(id=wxID_WXIMPORTCONFIRMDIALOGSTATICTEXT4, label="columns", name="staticText4", parent=self.swLoadX, pos=wx.Point(216, 8), size=wx.Size(39, 13), style=0)

	def __init__(self, parent, data, rows, cols):
		self._init_importconf_ctrls(parent)

		# create grid
		self.grdSampleData.CreateGrid(data.shape[0], data.shape[1])

		# report rows x cols
		self.stRows.SetLabel(str(rows))
		self.stCols.SetLabel(str(cols))

		# populate grid
		for i in range(data.shape[0]):
			for j in range(data.shape[1]):
				self.grdSampleData.SetCellValue(i, j, str(data[i, j]))

	def OnBtnOKButton(self, event):
		self.Close()


class wxImportDialog(wx.Dialog):
	def _init_coll_gbsImportDialog_Items(self, parent):

		parent.Add(self.fileBrowse, (0, 0), border=10, flag=wx.EXPAND, span=(1, 4))
		parent.Add(wx.Size(0, 0), (1, 0), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.cbTranspose, (1, 1), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.btnCancel, (1, 2), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.btnOK, (1, 3), border=10, flag=wx.EXPAND, span=(1, 1))

	def _init_coll_gbsImportDialog_Growables(self, parent):

		parent.AddGrowableCol(0)
		parent.AddGrowableCol(1)
		parent.AddGrowableCol(2)
		parent.AddGrowableCol(3)

	def _init_plot_prop_sizers(self):

		self.gbsImportDialog = wx.GridBagSizer(hgap=4, vgap=4)
		self.gbsImportDialog.SetCols(4)
		self.gbsImportDialog.SetRows(2)

		self._init_coll_gbsImportDialog_Items(self.gbsImportDialog)
		self._init_coll_gbsImportDialog_Growables(self.gbsImportDialog)

		self.SetSizer(self.gbsImportDialog)

	def _init_import_ctrls(self, prnt):
		# generated method, don't edit
		wx.Dialog.__init__(self, id=-1, name="wx.ImportDialog", parent=prnt, pos=wx.Point(496, 269), size=wx.Size(400, 120), style=wx.DEFAULT_DIALOG_STYLE, title="Import X-data File")
		self.SetToolTip("")
		self.Center(wx.BOTH)

		self.btnOK = wx.Button(id=-1, label="OK", name="btnOK", parent=self, pos=wx.Point(0, 0), size=wx.Size(85, 21), style=0)
		self.btnOK.Bind(wx.EVT_BUTTON, self.OnBtnOk)

		self.btnCancel = wx.Button(id=-1, label="Cancel", name="btnCancel", parent=self, pos=wx.Point(0, 0), size=wx.Size(85, 21), style=0)
		self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancel)

		self.fileBrowse = wx.lib.filebrowsebutton.FileBrowseButton(buttonText="Browse", dialogTitle="Choose a file", fileMask="*.*", id=-1, initialValue="", labelText="", parent=self, pos=wx.Point(48, 40), size=wx.Size(296, 48), startDirectory=".", style=wx.TAB_TRAVERSAL, toolTip="Type filename or click browse to choose file")

		self.cbTranspose = wx.CheckBox(id=-1, label="Transpose", name="cbTranspose", parent=self, pos=wx.Point(160, 128), size=wx.Size(73, 23), style=0)
		self.cbTranspose.SetValue(False)
		self.cbTranspose.SetToolTip("")

		self.staticLine = wx.StaticLine(id=-1, name="staticLine", parent=self, pos=wx.Point(400, 5), size=wx.Size(1, 2), style=0)

		self._init_plot_prop_sizers()

	def __init__(self, parent):
		self._init_import_ctrls(parent)

		self.chkOK = 0

	def isOK(self):
		return self.chkOK

	def getFile(self):
		return self.fileBrowse.GetValue()

	def Transpose(self):
		return self.cbTranspose.GetValue()

	def OnBtnCancel(self, event):
		self.chkOK = 0
		self.Close()

	def OnBtnOk(self, event):
		self.chkOK = 1
		self.Close()


class wxWorkspaceDialog(wx.Dialog):
	def _init_coll_lbSaveWorkspace_Columns(self, parent):
		# generated method, don't edit

		parent.InsertColumn(col=0, format=wx.LIST_FORMAT_LEFT, heading="Workspaces", width=260)

	def _init_savews_ctrls(self, prnt):
		# generated method, don't edit
		wx.Dialog.__init__(self, id=wxID_WXWORKSPACEDIALOG, name="wxWorkspaceDialog", parent=prnt, pos=wx.Point(453, 245), size=wx.Size(374, 280), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.CAPTION | wx.MAXIMIZE_BOX, title="Save Workspace")
		self.SetClientSize(wx.Size(366, 246))
		self.SetToolTip("")
		self.SetAutoLayout(True)
		self.Center(wx.BOTH)

		self.btnDelete = wx.Button(id=wxID_WXWORKSPACEDIALOGBTNDELETE, label="Delete", name="btnDelete", parent=self, pos=wx.Point(16, 7), size=wx.Size(70, 23), style=0)
		self.btnDelete.SetToolTip("")
		self.btnDelete.SetAutoLayout(True)
		self.btnDelete.Bind(wx.EVT_BUTTON, self.OnBtnDeleteButton, id=wxID_WXWORKSPACEDIALOGBTNDELETE)

		self.btnCancel = wx.Button(id=wxID_WXWORKSPACEDIALOGBTNCANCEL, label="Cancel", name="btnCancel", parent=self, pos=wx.Point(16, 40), size=wx.Size(72, 23), style=0)
		self.btnCancel.SetToolTip("")
		self.btnCancel.SetAutoLayout(True)
		self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancelButton, id=wxID_WXWORKSPACEDIALOGBTNCANCEL)

		self.btnEdit = wx.Button(id=wxID_WXWORKSPACEDIALOGBTNEDIT, label="Edit", name="btnEdit", parent=self, pos=wx.Point(16, 152), size=wx.Size(70, 23), style=0)
		self.btnEdit.SetToolTip("")
		self.btnEdit.SetAutoLayout(True)
		self.btnEdit.Show(False)
		self.btnEdit.Bind(wx.EVT_BUTTON, self.OnBtnEditButton, id=wxID_WXWORKSPACEDIALOGBTNEDIT)

		self.btnOK = wx.Button(id=wxID_WXWORKSPACEDIALOGBTNOK, label="OK", name="btnOK", parent=self, pos=wx.Point(16, 71), size=wx.Size(72, 23), style=0)
		self.btnOK.SetToolTip("")
		self.btnOK.SetAutoLayout(True)
		self.btnOK.Show(True)
		self.btnOK.Bind(wx.EVT_BUTTON, self.OnBtnOKButton, id=wxID_WXWORKSPACEDIALOGBTNOK)

		self.lbSaveWorkspace = wx.ListCtrl(id=wxID_WXWORKSPACEDIALOGLBSAVEWORKSPACE, name="lbSaveWorkspace", parent=self, pos=wx.Point(96, 8), size=wx.Size(264, 232), style=wx.LC_REPORT | wx.LC_SORT_ASCENDING | wx.LC_SINGLE_SEL)
		self.lbSaveWorkspace.SetConstraints(LayoutAnchors(self.lbSaveWorkspace, True, True, True, True))
		self.lbSaveWorkspace.SetAutoLayout(True)
		self.lbSaveWorkspace.SetToolTip("")
		self._init_coll_lbSaveWorkspace_Columns(self.lbSaveWorkspace)
		self.lbSaveWorkspace.Bind(wx.EVT_LEFT_DCLICK, self.OnLbSaveWorkspaceLeftDclick)
		self.lbSaveWorkspace.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnLbSaveWorkspaceListEndLabelEdit, id=wxID_WXWORKSPACEDIALOGLBSAVEWORKSPACE)
		self.lbSaveWorkspace.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnLbSaveWorkspaceListItemSelected, id=wxID_WXWORKSPACEDIALOGLBSAVEWORKSPACE)

	def __init__(self, parent, filename="", dtype="Load"):
		# type to be either "load" or "save"
		self._init_savews_ctrls(parent)

		# set some defaults
		self.SetTitle(dtype + " Workspace")
		self.dtype = dtype
		self.filename = filename
		self.tree = None
		self.workSpace = 0

		# need to populate listbox
		try:
			# check that it's a pychem file
			if self.filename not in [""]:
				self.tree = ET.ElementTree(file=self.filename)
				workspaces = self.tree.getroot().findall("Workspaces")[0]
				self.lbSaveWorkspace.SetColumnWidth(0, 260)
				for each in workspaces:
					index = self.lbSaveWorkspace.InsertItem(sys.maxsize, each.tag)
					self.lbSaveWorkspace.SetItem(index, 0, each.tag.replace("_", " "))

				# behaviour for save dialog
				if dtype == "Save":
					self.btnCancel.Enable(0)
		except:
			raise
			dlg = wx.MessageDialog(self, "Unable to load data - this is not a " + "PyChem Experiment file", "Error!", wx.OK | wx.ICON_ERROR)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()

	def OnBtnDeleteButton(self, event):
		if self.lbSaveWorkspace.GetItemCount() > 1:
			# need to delete the workspace in the xml file
			WSnode = self.tree.getroot().findall("Workspaces")[0]
			workspaces = WSnode
			for each in workspaces:
				if each.tag == self.lbSaveWorkspace.GetItemText(self.currentItem).replace(" ", "_"):
					WSnode.remove(each)
			self.tree.write(self.filename)

			# delete listbox entry
			self.lbSaveWorkspace.DeleteItem(self.currentItem)

	def OnBtnCancelButton(self, event):
		self.Close()

	def OnBtnEditButton(self, event):
		event.Skip()

	def getWorkspace(self):
		if (self.filename not in [""]) & (self.workSpace != 0) is True:
			return self.workSpace.replace(" ", "_")
		else:
			return 0

	def appendWorkspace(self, ws):
		index = self.lbSaveWorkspace.InsertItem(sys.maxsize, ws)
		self.lbSaveWorkspace.SetItem(index, 0, ws)

	def OnBtnOKButton(self, event):
		if self.dtype == "Load":
			try:
				self.workSpace = self.lbSaveWorkspace.GetItemText(self.currentItem)
				self.Close()
			except:
				dlg = wx.MessageDialog(self, "Please select a Workspace to load", "Error!", wx.OK | wx.ICON_ERROR)
				try:
					dlg.ShowModal()
				finally:
					dlg.Destroy()
		else:
			self.Close()

	def OnLbSaveWorkspaceLeftDclick(self, event):
		# get workspace
		if self.dtype == "Load":
			self.workSpace = self.lbSaveWorkspace.GetItemText(self.currentItem)
			self.Close()
		else:
			event.Skip()

	def OnLbSaveWorkspaceListEndLabelEdit(self, event):
		self.lbSaveWorkspace.SetColumnWidth(0, wx.LIST_AUTOSIZE)

	def OnLbSaveWorkspaceListItemSelected(self, event):
		self.currentItem = event.m_itemIndex

	def getTree(self):
		return self.tree
