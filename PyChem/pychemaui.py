#!/usr/bin/env python

import os

import wx
import wx.aui
import wx.grid
import wx.lib.agw.customtreectrl as ctc
import wx.lib.filebrowsebutton as fbb
import wx.wizard
from numpy import loadtxt

from . import thisDir
from .mva import chemometrics


def create(parent):
	return Pychem(parent)


[ExpWizId] = [wx.NewIdRef() for _init_ctrls in range(1)]


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

	def __init__(self, name, variables, sample_labels, variable_labels):
		self.name = name
		self.variables = variables
		self.sample_labels = sample_labels
		self.variable_labels = variable_labels


class Data(Experiment):
	"""data class
	sample_ids is a list of integers relating giving retained samples
	variable_ids is a list of integers giving retained variables"""

	# 	 name = self.name
	# 	 variables = self.variables
	# 	 sample_labels = self.sample_labels
	# 	 variable_labels = self.variable_labels

	def slice(self, sample_ids, variable_ids, split_ids):
		"""select only samples in sample_ids"""
		variable_select = numpy.take(variables, sample_ids, 0)
		"""select only variables in variable_ids"""
		variable_select = numpy.take(variable_select, variable_ids, 0)
		"""prune sample labels"""
		sample_label_select = numpy.take(sample_labels, sample_ids, 0)
		"""prune variable labels"""
		variable_label_select = numpy.take(parent.variable_labels, variable_ids, 0)


class Model(Data):
	"""modelling class"""

	"""holder for model output"""
	model_outputs = {}

	def pca(self, factors):
		"""principal component analysis"""
		pcscores, pcloads, pev, eigs = chemometrics.pca_nipals(self.variable_select, factors)
		"""place in holder"""
		model_outputs["pcscores"] = pcscores
		model_outputs["pcloads"] = pcloads
		model_outputs["pev"] = pev
		model_outputs["eigs"] = eigs


class Pychem(wx.Frame):
	def _init_statusbar(self, parent):
		parent.SetFieldsCount(5)
		parent.SetStatusText(text="Status", i=0)
		parent.SetStatusText(text="", i=1)
		parent.SetStatusText(text="", i=2)
		parent.SetStatusText(text="", i=3)
		parent.SetStatusText(text="", i=4)

		parent.SetStatusWidths([-2, -2, -2, -2, -5])

	def _init_ctrls(self, prnt):
		wx.Frame.__init__(self, id=-1, name="Pychem", parent=prnt, pos=wx.Point(124, 10), size=wx.Size(950, 698), style=wx.DEFAULT_FRAME_STYLE | wx.SUNKEN_BORDER | wx.CLIP_CHILDREN, title="PyChem 4.0")
		self.SetIcon(wx.Icon(str(thisDir / "ico" / "pychem.ico"), wx.BITMAP_TYPE_ICO))
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
		self.tbModelling.Bind(wx.EVT_TOOL, self.OnTbModellingClick, id=101)
		# 		 self.tbModelling.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=20)
		self.tbModelling.AddLabelTool(102, "Create Model", bmp)
		self.tbModelling.Bind(wx.EVT_TOOL, self.OnTbModellingClick, id=102)
		self.tbModelling.AddLabelTool(103, "Run PCA", bmp)
		self.tbModelling.Bind(wx.EVT_TOOL, self.OnTbModellingClick, id=103)
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
		"""make sure text in centre of panel"""
		sz = self.plViews.GetSize()
		w, h = self.plViewstext.GetTextExtent(self.plViewstext.GetLabel())
		self.plViewstext.SetPosition(((sz.width - w) / 2, (sz.height - h) / 2))

	def OnTbModellingClick(self, event):
		"""manage modelling events"""
		"""101 = create exp; 102 = create model, 103 = run pca"""
		en = event.GetId()
		if en == 101:
			"""create experiment"""
			self.ImportWizard = NewExperimentWizard(self)
			self.ImportWizard.RunWizard(self.ImportWizard.load_variables_page)


class NewExperimentWizard(wx.wizard.Wizard, Pychem):
	"""wizard to manage the import of data and metadata"""

	def _init_ctrls(self, prnt):
		wx.wizard.Wizard.__init__(self, id=ExpWizId, bitmap=wx.NullBitmap, pos=wx.Point(-1, -1), parent=prnt, title="Define New Experiment")
		self.Bind(wx.wizard.EVT_WIZARD_FINISHED, self.OnFinished, id=ExpWizId)

		self.load_variables_page = wx.wizard.WizardPageSimple(self)

		self.fbbImportVariables = fbb.FileBrowseButton(self.load_variables_page, -1, size=(450, -1), changeCallback=self.fbbCallback, labelText="Select File")

		# 		 self.grdImportVariables =

		self.show_variables_page = wx.wizard.WizardPageSimple(self)

	# 		 self.p1Sizer = makePageTitle(self.page1, "Study Details")

	# 		 self.p1Sizer.Add(self.StudyInfo, 0, wx.EXPAND|wx.ALL, 5)

	# 		 self.page2 = wx.wizard.WizardPageSimple(self)
	#
	# 		 self.SettingsInfo = SettingsPanel(self.page2, root)

	# 		 self.p2Sizer = makePageTitle(self.page2, "Experiment Details")

	# 		 self.p2Sizer.Add(self.SettingsInfo, 0, wx.EXPAND|wx.ALL, 5)

	def __init__(self, parent):
		self._init_ctrls(parent)

		self.FitToPage(self.load_variables_page)
		# 		 self.FitToPage(self.page2)

		# 		 wx.wizard.WizardPageSimple_Chain(self.load_variables_page,
		# 			   self.load_variables_page)#, self.page2)

		self.GetPageAreaSizer().Add(self.load_variables_page)

	def fbbCallback(self, event):
		"""import data"""
		filename = event.GetString()
		try:
			self.variables = loadtxt(filename)
		except Exception as error:
			# 			 raise
			dlg = wx.MessageDialog(self, "Unable to load array, please check file format", "Error!", wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()

	def OnFinished(self, event):
		"""create experiment"""
		try:
			Experiment("New Experiment", self.variables, [[1, 1, 1, 2, 2, 2, 3, 3, 3, 3]], [["1", "1", "1", "2", "2", "2", "3", "3", "3", "3"]])

			exp = self.ctcRoot.AppendItem(Pychem, "New Experiment", ct_type=0)

			self.ctcRoot.SetItemBold(exp, True)

		except Exception as error:
			raise
			dlg = wx.MessageDialog(self, "%s" % str(error), "Error!", wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()


class ViewVarGrid(NewExperimentWizard):
	def __init__(self, parent, variables):
		wx.grid.Grid.__init__(self, parent, id, size=wx.Size(0, 0))
		self.SetEnableCellControl(False)
		self.SetRowLabelSize(0)
		self.SetMargins(0, 0)
		self.AutoSizeColumns(False)
