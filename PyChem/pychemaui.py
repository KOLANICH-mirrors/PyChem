#!/usr/bin/env python

import os

import wx
import wx.aui
import wx.lib.agw.customtreectrl as ctc

from .mva import chemometrics


def create(parent):
	return Pychem(parent)


def _index(values, id):
	"""use this to get tuple index for take"""
	idx = []
	for i in range(len(values)):
		if y[i] == id:
			idx.append(int(i))
	return tuple(idx)


class Experiment:
	"""the experiment class, a holder for
	models variables are numpy array type of samples (rows) by
	variables (columns). sample and variable labels are lists of
	lists containing text entries"""

	def __init__(self, parent, variables, sample_labels, variable_labels):
		self.variables = variables
		self.sample_labels = sample_labels
		self.variable_labels = variable_labels


class Data(Experiment):
	"""data class
	sample_ids is a list of integers relating giving retained samples
	variable_ids is a list of integers giving retained variables"""

	def __init__(self, parent, sample_ids, variable_ids, split_ids):
		"""select only samples in sample_ids"""
		self.variable_select = numpy.take(parent.variables, sample_ids, 0)
		"""select only variables in variable_ids"""
		self.variable_select = numpy.take(self.variable_select, variable_ids, 0)
		"""prune sample labels"""
		self.sample_label_select = numpy.take(parent.sample_labels, sample_ids, 0)
		"""prune variable labels"""
		self.variable_label_select = numpy.take(parent.variable_labels, variable_ids, 0)


class Model(Data):
	"""modelling class"""

	def __init__(self, parent, method):
		"""matrix to model"""
		self.variables = parent.variable_select
		"""holder for model output"""
		self.model_outputs = {}

	def pca(self, factors):
		"""principal component analysis"""
		pcscores, pcloads, pev, eigs = chemometrics.pca_nipals(self.variables, factors)
		"""place in holder"""
		self.model_outputs["pcscores"] = pcscores
		self.model_outputs["pcloads"] = pcloads
		self.model_outputs["pev"] = pev
		self.model_outputs["eigs"] = eigs


class Pychem(wx.Frame):
	def _init_statusbar(self, parent):
		parent.SetFieldsCount(5)
		parent.SetStatusText(number=0, text="Status")
		parent.SetStatusText(number=1, text="")
		parent.SetStatusText(number=2, text="")
		parent.SetStatusText(number=3, text="")
		parent.SetStatusText(number=4, text="")

		parent.SetStatusWidths([-2, -2, -2, -2, -5])

	def _init_ctrls(self, prnt):
		wx.Frame.__init__(self, id=-1, name="Pychem", parent=prnt, pos=wx.Point(124, 10), size=wx.Size(950, 698), style=wx.DEFAULT_FRAME_STYLE | wx.SUNKEN_BORDER | wx.CLIP_CHILDREN, title="PyChem 4.0")
		self.SetIcon(wx.Icon(os.path.join("ico", "pychem.ico"), wx.BITMAP_TYPE_ICO))
		# 		 self._init_utils()
		# 		 self.SetMenuBar(self.mbMain)
		self.SetToolTip("")
		self.SetAutoLayout(True)
		self.Center(wx.BOTH)

		"""create statusbar"""
		self.statusbar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
		self._init_statusbar(self.statusbar)

		"""create modelling toolbar"""
		self.tbModelling = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, wx.TB_FLAT | wx.TB_NODIVIDER | wx.TB_HORZ_TEXT)
		self.tbModelling.SetToolBitmapSize(wx.Size(16, 16))
		bmp = wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16, 16))
		self.tbModelling.AddLabelTool(101, "Create Exp", bmp)
		self.tbModelling.AddLabelTool(101, "Create Model", bmp)
		self.tbModelling.AddLabelTool(101, "Run PCA", bmp)
		self.tbModelling.Realize()

		"""model management tree"""
		self.ctcExperiments = ctc.CustomTreeCtrl(parent=self, id=-1, pos=wx.Point(-12, 22), size=wx.Size(1024, 599), style=wx.SUNKEN_BORDER | ctc.TR_HAS_BUTTONS | ctc.TR_HAS_VARIABLE_ROW_HEIGHT | wx.WANTS_CHARS | ctc.TR_HIDE_ROOT)
		self.ctcExperiments.SetToolTip("")

		"""root node for tree - invisible"""
		self.ctcRoot = self.ctcExperiments.AddRoot("Experiments")  # ,wnd=self.plDecisionBtns)

		"""the panel into which various views will be placed"""
		self.plViews = wx.Panel(id=-1, name="plViews", parent=self, pos=wx.Point(0, 0), size=wx.Size(270, 662), style=wx.TAB_TRAVERSAL)
		self.plViews.SetAutoLayout(True)
		self.plViews.SetToolTip("")
		self.plViews.Bind(wx.EVT_SIZE, self.OnPlviewsSize)

		"""a label to put in the views window"""
		plViewstext = wx.StaticText(self.plViews, -1, "Create Views Here")
		plViewstext.SetToolTip("")
		f = plViewstext.GetFont()
		f.SetWeight(wx.BOLD)
		f.SetPointSize(f.GetPointSize() + 2)
		plViewstext.SetFont(f)
		self.plViewstext = plViewstext

		"""a blank panel for the views centrepane"""
		self.plViewsCentre = wx.Panel(id=-1, name="plViewsCentre", parent=self.plViews, pos=wx.Point(0, 0), size=wx.Size(0, 0), style=wx.TAB_TRAVERSAL)
		self.plViewsCentre.SetBackgroundColour(wx.Colour(163, 243, 183))
		self.plViewsCentre.SetToolTip("")

		"""tell framemanager to manage the parent frame"""
		self._mgr = wx.aui.AuiManager()
		self._mgr.SetManagedWindow(self)

		self._mgr.AddPane(self.tbModelling, wx.aui.AuiPaneInfo().Name("tbModelling").ToolbarPane().Top().LeftDockable(False).RightDockable(False))

		"""make views panel centre pane"""
		self._mgr.AddPane(self.plViews, wx.aui.AuiPaneInfo().CenterPane().Name("Views").BestSize(wx.Size(240, 300)))

		"""add controls pane"""
		self._mgr.AddPane(self.ctcExperiments, wx.aui.AuiPaneInfo().MaximizeButton(True).Name("Experiments").Caption("Experiments").Left().Layer(1).Position(0).BestSize(wx.Size(240, 300)))

		self._mgr.Update()

		"""another framemanager to manage the views frame"""
		self._viewsmgr = wx.aui.AuiManager()
		self._viewsmgr.SetManagedWindow(self.plViews)

		"""dummy centre pane for views panel"""
		self._viewsmgr.AddPane(self.plViewsCentre, wx.aui.AuiPaneInfo().CenterPane().Name("ViewsCentre").Hide())

		self._viewsmgr.Update()

		self._default_perspective = self._mgr.SavePerspective()

	def __init__(self, parent):
		self._init_ctrls(parent)

	def OnPlviewsSize(self, event):
		sz = self.plViews.GetSize()
		w, h = self.plViewstext.GetTextExtent(self.plViewstext.GetLabel())
		self.plViewstext.SetPosition(((sz.width - w) / 2, (sz.height - h) / 2))
