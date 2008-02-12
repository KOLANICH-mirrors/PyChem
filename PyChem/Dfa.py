# -----------------------------------------------------------------------------
# Name:		   Dfa.py
# Purpose:
#
# Author:	   Roger Jarvis
#
# Created:	   2007/05/22
# RCS-ID:	   $Id$
# Copyright:   (c) 2006
# Licence:	   GNU General Public Licence
# -----------------------------------------------------------------------------
# Boa:FramePanel:Dfa

import os
import string

import scipy
import wx
import wx.lib.agw.buttonpanel as bp
import wx.lib.buttons
import wx.lib.plot
import wx.lib.stattext
from Bio.Cluster import *
from scipy import newaxis as nA
from wx.lib.anchors import LayoutAnchors

from .mva import chemometrics
from .mva.chemometrics import _index
from .Pca import MyPlotCanvas, SetButtonState, plotLine, plotLoads, plotScores, plotStem, plotText
from .utils.io import str_array

[
	wxID_DFA,
	wxID_DFABTNEXPDFA,
	wxID_DFABTNGOGADFA,
	wxID_DFABTNGOPCA,
	wxID_DFAbtnRunDfa,
	wxID_DFACBDFAXVAL,
	wxID_DFAPLCDFAEIGS,
	wxID_DFAPLCDFAERROR,
	wxID_DFAPLCDFALOADSV,
	wxID_DFAPLCDFASCORES,
	wxID_DFAPLDFALOADS,
	wxID_DFAPLDFASCORES,
	wxID_DFARBDFAPROCDATA,
	wxID_DFARBDFARAWDATA,
	wxID_DFARBDFAUSEPCSCORES,
	wxID_DFASASHWINDOW5,
	wxID_DFASPNDFABILOAD1,
	wxID_DFASPNDFABILOAD2,
	wxID_DFASPNDFADFS,
	wxID_DFASPNDFAPCS,
	wxID_DFASPNDFASCORE1,
	wxID_DFASPNDFASCORE2,
	wxID_DFASTATICTEXT2,
	wxID_DFASTATICTEXT23,
	wxID_DFASTATICTEXT24,
	wxID_DFASTATICTEXT28,
	wxID_DFASTATICTEXT3,
	wxID_DFASTATICTEXT4,
	wxID_DFASTATICTEXT5,
	wxID_DFASTATICTEXT7,
	wxID_DFASTATICTEXT8,
	wxID_DFASTDFA6,
	wxID_DFASTDFA7,
] = [wx.NewIdRef() for _init_ctrls in range(33)]


def errorBox(window, error):
	dlg = wx.MessageDialog(window, "".join(("The following error occured:\n\n", error)), "Error!", wx.OK | wx.ICON_ERROR)
	try:
		dlg.ShowModal()
	finally:
		dlg.Destroy()


class Dfa(wx.Panel):
	# discriminant function analysis
	def _init_coll_grsDfa_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.plcDFAscores, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.plcDfaLoadsV, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.plcDfaCluster, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.plcDFAeigs, 0, border=0, flag=wx.EXPAND)

	def _init_coll_bxsDfa1_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.bxsDfa2, 1, border=0, flag=wx.EXPAND)

	def _init_coll_bxsDfa2_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.titleBar, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.grsDfa, 1, border=0, flag=wx.EXPAND)

	def _init_sizers(self):
		# generated method, don't edit
		self.bxsDfa1 = wx.BoxSizer(orient=wx.HORIZONTAL)

		self.bxsDfa2 = wx.BoxSizer(orient=wx.VERTICAL)

		self.grsDfa = wx.GridSizer(cols=2, hgap=2, rows=2, vgap=2)

		self._init_coll_bxsDfa1_Items(self.bxsDfa1)
		self._init_coll_bxsDfa2_Items(self.bxsDfa2)
		self._init_coll_grsDfa_Items(self.grsDfa)

		self.SetSizer(self.bxsDfa1)

	def _init_ctrls(self, prnt):
		# generated method, don't edit
		wx.Panel.__init__(self, id=wxID_DFA, name="Dfa", parent=prnt, pos=wx.Point(47, 118), size=wx.Size(796, 460), style=wx.TAB_TRAVERSAL)
		self.SetClientSize(wx.Size(788, 426))
		self.SetToolTip("")
		self.SetAutoLayout(True)
		self.prnt = prnt

		self.plcDFAscores = MyPlotCanvas(id=-1, name="plcDFAscores", parent=self, pos=wx.Point(0, 24), size=wx.Size(24, 20), style=0, toolbar=self.prnt.parent.tbMain)
		self.plcDFAscores.fontSizeTitle = 10
		self.plcDFAscores.fontSizeAxis = 8
		self.plcDFAscores.enableZoom = True
		self.plcDFAscores.enableLegend = True
		self.plcDFAscores.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "MS Sans Serif"))
		self.plcDFAscores.SetToolTip("")
		self.plcDFAscores.SetAutoLayout(True)
		self.plcDFAscores.SetConstraints(LayoutAnchors(self.plcDFAscores, True, True, True, True))
		self.plcDFAscores.fontSizeLegend = 8

		self.plcDfaLoadsV = MyPlotCanvas(id=-1, name="plcDfaLoadsV", parent=self, pos=wx.Point(-5, 24), size=wx.Size(24, 20), style=0, toolbar=self.prnt.parent.tbMain)
		self.plcDfaLoadsV.fontSizeAxis = 8
		self.plcDfaLoadsV.fontSizeTitle = 10
		self.plcDfaLoadsV.enableZoom = True
		self.plcDfaLoadsV.enableLegend = True
		self.plcDfaLoadsV.SetToolTip("")
		self.plcDfaLoadsV.SetAutoLayout(True)
		self.plcDfaLoadsV.SetConstraints(LayoutAnchors(self.plcDfaLoadsV, True, True, True, True))
		self.plcDfaLoadsV.fontSizeLegend = 8
		self.plcDfaLoadsV.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))

		self.plcDFAeigs = MyPlotCanvas(id=-1, name="plcDFAeigs", parent=self, pos=wx.Point(483, 214), size=wx.Size(305, 212), style=0, toolbar=self.prnt.parent.tbMain)
		self.plcDFAeigs.fontSizeAxis = 8
		self.plcDFAeigs.fontSizeTitle = 10
		self.plcDFAeigs.enableZoom = True
		self.plcDFAeigs.SetToolTip("")
		self.plcDFAeigs.SetAutoLayout(True)
		self.plcDFAeigs.SetConstraints(LayoutAnchors(self.plcDFAeigs, False, True, False, True))
		self.plcDFAeigs.fontSizeLegend = 8
		self.plcDFAeigs.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))

		self.plcDfaCluster = MyPlotCanvas(id=-1, name="plcDfaCluster", parent=self, pos=wx.Point(176, 214), size=wx.Size(305, 212), style=0, toolbar=self.prnt.parent.tbMain)
		self.plcDfaCluster.fontSizeAxis = 8
		self.plcDfaCluster.fontSizeTitle = 10
		self.plcDfaCluster.enableZoom = True
		self.plcDfaCluster.enableLegend = False
		self.plcDfaCluster.SetToolTip("")
		self.plcDfaCluster.SetAutoLayout(True)
		self.plcDfaCluster.xSpec = "none"
		self.plcDfaCluster.ySpec = "none"
		self.plcDfaCluster.SetConstraints(LayoutAnchors(self.plcDfaCluster, True, True, False, True))
		self.plcDfaCluster.fontSizeLegend = 8
		self.plcDfaCluster.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))

		self.titleBar = TitleBar(self, id=-1, text="Discriminant Function Analysis", style=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self._init_sizers()

	def __init__(self, parent, id, pos, size, style, name):
		self._init_ctrls(parent)

		self.parent = parent

	def Reset(self):
		self.titleBar.spnDfaScore1.Enable(0)
		self.titleBar.spnDfaScore2.Enable(0)
		self.titleBar.spnDfaScore1.SetValue(1)
		self.titleBar.spnDfaScore2.SetValue(2)

		objects = {"plcDFAeigs": ["Eigenvalues", "Discriminant Function", "Eigenvalue"], "plcDfaCluster": ["Hierarchical Cluster Analysis", "Distance", "Sample"], "plcDFAscores": ["DFA Scores", "DF 1", "DF 2"], "plcDfaLoadsV": ["DFA Loading", "Arbitrary", "Arbitrary"]}
		curve = wx.lib.plot.PolyLine([[0, 0], [1, 1]], colour="white", width=1, style=wx.TRANSPARENT)

		for each in list(objects.keys()):
			exec("self." + each + ".Draw(wx.lib.plot.PlotGraphics([curve]," + 'objects["' + each + '"][0],' + 'objects["' + each + '"][1],' + 'objects["' + each + '"][2]))')


class TitleBar(bp.ButtonPanel):
	def _init_btnpanel_ctrls(self, prnt):
		bp.ButtonPanel.__init__(self, parent=prnt, id=-1, text="Discriminant Function Analysis", agwStyle=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self.cbxData = wx.Choice(choices=["PC Scores", "PLS Scores", "Raw spectra", "Processed spectra"], id=-1, name="cbxData", parent=self, pos=wx.Point(118, 21), size=wx.Size(100, 23), style=0)
		self.cbxData.SetSelection(0)
		self.Bind(wx.EVT_CHOICE, self.OnCbxData, id=self.cbxData.GetId())

		self.btnRunDfa = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "run.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Run DFA", longHelp="Run Discriminant Function Analysis")
		self.btnRunDfa.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnRunDfaButton, id=self.btnRunDfa.GetId())

		self.spnDfaPcs = wx.SpinCtrl(id=-1, initial=1, max=100, min=3, name="spnDfaPcs", parent=self, pos=wx.Point(104, 104), size=wx.Size(46, 23), style=wx.SP_ARROW_KEYS)
		self.spnDfaPcs.SetValue(3)
		self.spnDfaPcs.SetToolTip("")

		self.spnDfaDfs = wx.SpinCtrl(id=-1, initial=1, max=100, min=2, name="spnDfaDfs", parent=self, pos=wx.Point(57, 168), size=wx.Size(46, 23), style=wx.SP_ARROW_KEYS)
		self.spnDfaDfs.SetValue(2)
		self.spnDfaDfs.SetToolTip("")

		self.cbDfaXval = wx.CheckBox(id=-1, label="", name="cbDfaXval", parent=self, pos=wx.Point(16, 216), size=wx.Size(14, 13), style=0)
		self.cbDfaXval.SetValue(False)
		self.cbDfaXval.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "MS Sans Serif"))
		self.cbDfaXval.SetToolTip("")

		self.btnExpDfa = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "export.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Export DFA Results", longHelp="Export DFA Results")
		self.btnExpDfa.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnExpDfaButton, id=self.btnExpDfa.GetId())

		self.spnDfaScore1 = wx.SpinCtrl(id=-1, initial=1, max=100, min=1, name="spnDfaScore1", parent=self, pos=wx.Point(199, 4), size=wx.Size(46, 23), style=wx.SP_ARROW_KEYS)
		self.spnDfaScore1.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "MS Sans Serif"))
		self.spnDfaScore1.SetToolTip("")
		self.spnDfaScore1.Enable(0)
		self.spnDfaScore1.Bind(wx.EVT_SPINCTRL, self.OnSpnDfaScore1Spinctrl, id=-1)

		self.spnDfaScore2 = wx.SpinCtrl(id=-1, initial=1, max=100, min=1, name="spnDfaScore2", parent=self, pos=wx.Point(287, 4), size=wx.Size(46, 23), style=wx.SP_ARROW_KEYS)
		self.spnDfaScore2.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "MS Sans Serif"))
		self.spnDfaScore2.SetToolTip("")
		self.spnDfaScore2.Enable(0)
		self.spnDfaScore2.Bind(wx.EVT_SPINCTRL, self.OnSpnDfaScore2Spinctrl, id=-1)

	def __init__(self, parent, id, text, style, alignment):

		self._init_btnpanel_ctrls(parent)

		self.parent = parent

		self.CreateButtons()

	def CreateButtons(self):
		self.Freeze()

		self.SetProperties()

		self.AddControl(self.cbxData)
		self.AddControl(wx.lib.stattext.GenStaticText(self, -1, "No. LVs", style=wx.TRANSPARENT_WINDOW))
		self.AddControl(self.spnDfaPcs)
		self.AddControl(wx.lib.stattext.GenStaticText(self, -1, "No. DFs", style=wx.TRANSPARENT_WINDOW))
		self.AddControl(self.spnDfaDfs)
		self.AddControl(wx.lib.stattext.GenStaticText(self, -1, "Cross validate?", style=wx.TRANSPARENT_WINDOW))
		self.AddControl(self.cbDfaXval)
		self.AddSeparator()
		self.AddControl(wx.lib.stattext.GenStaticText(self, -1, "DF ", style=wx.TRANSPARENT_WINDOW))
		self.AddControl(self.spnDfaScore1)
		self.AddControl(wx.lib.stattext.GenStaticText(self, -1, " vs. ", style=wx.TRANSPARENT_WINDOW))
		self.AddControl(self.spnDfaScore2)
		self.AddSeparator()
		self.AddButton(self.btnRunDfa)
		self.AddSeparator()
		self.AddButton(self.btnExpDfa)

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

	def getData(self, data):
		self.data = data

	def OnCbxData(self, event):
		if self.cbxData.GetSelection() == 0:
			if self.data["pcscores"] is not None:
				self.spnDfaPcs.SetRange(1, self.data["pcscores"].shape[1])
				if self.data["pcscores"].shape[1] < self.spnDfaPcs.GetValue():
					self.spnDfaPcs.SetValue(self.data["pcscores"].shape[1])
		elif self.cbxData.GetSelection() == 1:
			if self.data["plst"] is not None:
				self.spnDfaPcs.SetRange(1, self.data["plst"].shape[1])
				if self.data["plst"].shape[1] < self.spnDfaPcs.GetValue():
					self.spnDfaPcs.SetValue(self.data["plst"].shape[1])

	def OnBtnRunDfaButton(self, event):
		try:
			# run discriminant function analysis
			if self.cbxData.GetSelection() == 0:
				xdata = self.data["pcscores"][:, 0 : self.spnDfaPcs.GetValue()]
				loads = self.data["pcloads"]
			elif self.cbxData.GetSelection() == 1:
				xdata = self.data["plst"][:, 0 : self.spnDfaPcs.GetValue()]
				loads = scipy.transpose(self.data["plsloads"])
			elif self.cbxData.GetSelection() == 2:
				xdata = self.data["rawtrunc"]
			elif self.cbxData.GetSelection() == 3:
				xdata = self.data["proctrunc"]

			# if using xval
			# select data
			if self.parent.parent.parent.plPca.titleBar.cbxData.GetSelection() == 0:
				xvaldata = self.data["rawtrunc"]
			elif self.parent.parent.parent.plPca.titleBar.cbxData.GetSelection() == 1:
				xvaldata = self.data["proctrunc"]

			# select pca method
			if self.parent.parent.parent.plPca.titleBar.cbxPcaType.GetSelection() == 0:
				self.data["niporsvd"] = "nip"
			elif self.parent.parent.parent.plPca.titleBar.cbxPcaType.GetSelection() == 1:
				self.data["niporsvd"] = "svd"

			# check appropriate number of pcs/dfs
			if self.spnDfaPcs.GetValue() <= self.spnDfaDfs.GetValue():
				self.spnDfaDfs.SetValue(self.spnDfaPcs.GetValue() - 1)

			# check for pca preproc method
			if self.parent.parent.parent.plPca.titleBar.cbxPreprocType.GetSelection() == 0:
				self.data["pcatype"] = "covar"
			elif self.parent.parent.parent.plPca.titleBar.cbxPreprocType.GetSelection() == 1:
				self.data["pcatype"] = "corr"

			# Reset controls
			self.spnDfaScore1.Enable(1)
			self.spnDfaScore2.Enable(1)
			self.spnDfaScore1.SetRange(1, self.spnDfaDfs.GetValue())
			self.spnDfaScore1.SetValue(1)
			self.spnDfaScore2.SetRange(1, self.spnDfaDfs.GetValue())
			self.spnDfaScore2.SetValue(2)
			self.btnExpDfa.Enable(1)

			if self.cbDfaXval.GetValue() is False:
				# just a fix to recover original loadings when using PC-DFA
				if self.cbxData.GetSelection() > 1:
					self.data["dfscores"], self.data["dfloads"], self.data["dfeigs"], dummy = mva.chemometrics.DFA(xdata, self.data["class"][:, 0], self.spnDfaDfs.GetValue())
				else:
					self.data["dfscores"], dummy, self.data["dfeigs"], self.data["dfloads"] = mva.chemometrics.DFA(xdata, self.data["class"][:, 0], self.spnDfaDfs.GetValue(), loads[0 : self.spnDfaPcs.GetValue(), :])

			elif self.cbDfaXval.GetValue() is True:
				if self.cbxData.GetSelection() > 1:
					# run dfa
					self.data["dfscores"], self.data["dfloads"], self.data["dfeigs"] = mva.chemometrics.DFA_XVALRAW(xdata, self.data["class"][:, 0], self.data["validation"], self.spnDfaDfs.GetValue())

				elif self.cbxData.GetSelection() == 0:
					# run pc-dfa
					if self.data["niporsvd"] in ["nip"]:
						self.data["dfscores"], self.data["dfloads"], self.data["dfeigs"] = mva.chemometrics.DFA_XVAL_PCA(xvaldata, "NIPALS", self.spnDfaPcs.GetValue(), self.data["class"][:, 0], self.data["validation"], self.spnDfaDfs.GetValue(), ptype=self.data["pcatype"])

					elif self.data["niporsvd"] in ["svd"]:
						self.data["dfscores"], self.data["dfloads"], self.data["dfeigs"] = mva.chemometrics.DFA_XVAL_PCA(xvaldata, "SVD", self.spnDfaPcs.GetValue(), self.data["class"][:, 0], self.data["validation"], self.spnDfaDfs.GetValue(), ptype=self.data["pcatype"])

				elif self.cbxData.GetSelection() == 1:
					# run pls-dfa
					self.data["dfscores"], self.data["dfloads"], self.data["dfeigs"] = mva.chemometrics.DFA_XVAL_PLS(self.data["plst"], self.data["plsloads"], self.spnDfaPcs.GetValue(), self.data["class"][:, 0], self.data["validation"], self.spnDfaDfs.GetValue())

			# plot dfa results
			self.plotDfa()

		except Exception as error:
			errorBox(self, "%s" % str(error))

	##			  raise

	def OnBtnExpDfaButton(self, event):
		dlg = wx.FileDialog(self, "Choose a file", ".", "", "Any files (*.*)|*.*", wx.FD_SAVE)
		try:
			if dlg.ShowModal() == wx.ID_OK:
				saveFile = dlg.GetPath()
				out = "#DISCRIMINANT_FUNCTION_SCORES\n" + str_array(self.data["dfscores"], col_sep="\t") + "\n" + "#DISCRIMINANT_FUNCTION_LOADINGS\n" + str_array(self.data["dfloads"], col_sep="\t") + "\n" + "#EIGENVALUES\n" + str_array(self.data["dfeigs"], col_sep="\t")
				f = file(saveFile, "w")
				f.write(out)
				f.close()
		finally:
			dlg.Destroy()

	def OnSpnDfaScore1Spinctrl(self, event):
		self.plotDfa()
		SetButtonState(self.spnDfaScore1.GetValue(), self.spnDfaScore2.GetValue(), self.parent.parent.parent.tbMain)

	def OnSpnDfaScore2Spinctrl(self, event):
		self.plotDfa()
		SetButtonState(self.spnDfaScore1.GetValue(), self.spnDfaScore2.GetValue(), self.parent.parent.parent.tbMain)

	def plotDfa(self):
		# plot scores
		plotScores(self.parent.plcDFAscores, self.data["dfscores"], cl=self.data["class"][:, 0], labels=self.data["label"], validation=self.data["validation"], col1=self.spnDfaScore1.GetValue() - 1, col2=self.spnDfaScore2.GetValue() - 1, title="DFA Scores", xLabel="t[" + str(self.spnDfaScore1.GetValue()) + "]", yLabel="t[" + str(self.spnDfaScore2.GetValue()) + "]", xval=self.cbDfaXval.GetValue(), symb=self.parent.parent.parent.tbMain.tbSymbols.GetValue(), text=self.parent.parent.parent.tbMain.tbPoints.GetValue(), pconf=self.parent.parent.parent.tbMain.tbConf.GetValue(), usecol=[], usesym=[])

		# plot loadings
		if self.cbxData.GetSelection() == 0:
			label = "PC-DFA Loadings"
		else:
			label = "DFA Loadings"

		if self.spnDfaScore1.GetValue() != self.spnDfaScore2.GetValue():
			plotLoads(self.parent.plcDfaLoadsV, self.data["dfloads"], xaxis=self.data["indlabels"], col1=self.spnDfaScore1.GetValue() - 1, col2=self.spnDfaScore2.GetValue() - 1, title=label, xLabel="w[" + str(self.spnDfaScore1.GetValue()) + "]", yLabel="w[" + str(self.spnDfaScore2.GetValue()) + "]", type=self.parent.parent.parent.tbMain.GetLoadPlotIdx(), usecol=[], usesym=[])

		else:
			idx = self.spnDfaScore1.GetValue() - 1
			plotLine(self.parent.plcDfaLoadsV, scipy.transpose(self.data["dfloads"]), xaxis=self.data["xaxis"], tit=label, rownum=idx, xLabel="Variable", yLabel="w[" + str(idx + 1) + "]", wdth=1, ledge=[], type="single")

		# calculate and plot hierarchical clustering using euclidean distance
		# get average df scores for each class
		mS, mSn = [], []
		for each in scipy.unique(self.data["class"][:, 0]):
			mS.append(scipy.mean(self.data["dfscores"][self.data["class"][:, 0] == each, :], 0))
			mSn.append(self.data["label"][_index(self.data["class"][:, 0], each)[0]])

		tree = treecluster(data=mS, method="m", dist="e")
		tree, order = self.parent.parent.parent.plCluster.titleBar.treestructure(tree, scipy.arange(len(tree) + 1))
		self.parent.parent.parent.plCluster.titleBar.drawTree(self.parent.plcDfaCluster, tree, order, mSn, tit="Hierarchical Cluster Analysis", xL="Euclidean Distance", yL="Sample")

		# Plot eigs
		self.DrawDfaEig = plotLine(self.parent.plcDFAeigs, self.data["dfeigs"], xaxis=scipy.arange(1, self.data["dfeigs"].shape[1] + 1)[:, nA], rownum=0, tit="Eigenvalues", xLabel="Discriminant Function", yLabel="Eigenvalues", wdth=3, type="single", ledge=[])

		# make sure ctrls enabled
		self.spnDfaScore1.Enable(True)
		self.spnDfaScore2.Enable(True)
		self.btnExpDfa.Enable(True)
