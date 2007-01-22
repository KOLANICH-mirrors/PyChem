# Boa:FramePanel:expSetup

import string

import scipy
import wx
import wx.adv
import wx.grid
import wx.lib.agw.buttonpanel as bp
import wx.lib.agw.foldpanelbar as fpb
import wx.lib.bcrtl.user.StaticTextCtrl
from wx.lib.anchors import LayoutAnchors

from .chemometrics import _sample

[
	wxID_EXPSETUP,
	ID_BTNIMPIND,
	BTNINSRANGE,
] = [wx.NewIdRef() for _init_indbtnpanel_ctrls in range(3)]

[
	wxID_WXIMPORTMETADATADIALOG,
	wxID_WXIMPORTMETADATADIALOGBTNBROWSEARRAY,
	wxID_WXIMPORTMETADATADIALOGBTNCANCEL,
	wxID_WXIMPORTMETADATADIALOGBTNOK,
	wxID_WXIMPORTMETADATADIALOGSTARRAY,
	wxID_WXIMPORTMETADATADIALOGSWLOADX,
] = [wx.NewIdRef() for _init_import_ctrls in range(6)]

[
	ID_BTNADDNAME,
	ID_BTNADDCLASS,
	ID_BTNADDMASK,
] = [wx.NewIdRef() for _init_depbtnpanel_ctrls in range(3)]


def errorBox(window, error):
	dlg = wx.MessageDialog(window, "".join(("The following error occured:\n\n", error)), "Error!", wx.OK | wx.ICON_ERROR)
	try:
		dlg.ShowModal()
	finally:
		dlg.Destroy()


def GetXaxis(From, To, Bins, Grid):
	if From and To not in [""]:
		# generate vector of x-labels
		int = (float(From) - float(To)) / (1 - Bins)
		ax = float(From) - int
		xaxis = scipy.dot(int, scipy.arange(1, Bins + 1)) + ax
		xaxis = scipy.around(scipy.reshape(xaxis, (len(xaxis), 1)), 2)

		# Append row to independent label grid
		Grid.AppendCols(1)
		Grid.SetCellAlignment(0, Grid.GetNumberCols() - 1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
		Grid.SetCellEditor(0, Grid.GetNumberCols() - 1, wx.grid.GridCellBoolEditor())
		Grid.SetCellRenderer(0, Grid.GetNumberCols() - 1, wx.grid.GridCellBoolRenderer())
		Grid.SetCellValue(0, Grid.GetNumberCols() - 1, "1")
		Grid.SetColLabelValue(Grid.GetNumberCols() - 1, "X-axis")

		for i in range(1, xaxis.shape[0] + 1):
			Grid.SetCellValue(i, Grid.GetNumberCols() - 1, "%.2f" % xaxis[i - 1, 0])

	return xaxis


def ResizeGrids(grid, rows, cols, type=None):
	grid.ClearGrid()

	if grid.GetNumberCols() > cols + 1:
		grid.DeleteCols(cols + 1, grid.GetNumberCols())
	elif grid.GetNumberCols() < cols + 1:
		grid.AppendCols(cols + 1 - grid.GetNumberCols())

	if grid.GetNumberRows() > rows + 1:
		grid.DeleteRows(rows + 1, grid.GetNumberRows())
	elif grid.GetNumberRows() < rows + 1:
		grid.AppendRows(rows + 1 - grid.GetNumberRows())

	if type in [1, 2]:
		grid.AppendRows(1)
		grid.SetRowLabelValue(0, "Type")
		grid.SetRowLabelValue(1, "Select")
		for i in range(grid.GetNumberRows() - 2):
			grid.SetRowLabelValue(i + 2, str(i + 1))
		for i in range(grid.GetNumberCols()):
			grid.SetCellAlignment(0, i, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
			grid.SetCellAlignment(1, i, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
			grid.SetCellTextColour(0, i, wx.RED)
			grid.SetReadOnly(0, i, 1)
			grid.SetCellEditor(1, i, wx.grid.GridCellBoolEditor())
			grid.SetCellRenderer(1, i, wx.grid.GridCellBoolRenderer())
			grid.SetCellValue(1, i, "1")
			if i == 0:
				grid.SetColLabelValue(i, "Sample")
				grid.SetCellValue(0, i, "Select")
				for j in range(2, grid.GetNumberRows()):
					grid.SetCellEditor(j, 0, wx.grid.GridCellBoolEditor())
					grid.SetCellRenderer(j, 0, wx.grid.GridCellBoolRenderer())
					grid.SetCellAlignment(j, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
					grid.SetCellValue(j, 0, "1")

	if type == 2:
		grid.SetColLabelValue(1, "Label")
		grid.SetCellValue(0, 1, "Label")
		grid.SetColLabelValue(2, "Class")
		grid.SetCellValue(0, 2, "Class")
		grid.SetColLabelValue(3, "Validation")
		grid.SetCellValue(0, 3, "Validation")

	if type == 3:
		grid.SetRowLabelValue(0, "Select")
		for i in range(1, grid.GetNumberRows()):
			grid.SetRowLabelValue(i, str(i))
		for i in range(grid.GetNumberCols()):
			grid.SetCellAlignment(0, i, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
			grid.SetCellEditor(0, i, wx.grid.GridCellBoolEditor())
			grid.SetCellRenderer(0, i, wx.grid.GridCellBoolRenderer())
			grid.SetCellValue(0, i, "1")
			if i == 0:
				grid.SetColLabelValue(0, "Variable")
				for j in range(1, grid.GetNumberRows()):
					grid.SetCellEditor(j, 0, wx.grid.GridCellBoolEditor())
					grid.SetCellRenderer(j, 0, wx.grid.GridCellBoolRenderer())
					grid.SetCellAlignment(j, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
					grid.SetCellValue(j, 0, "1")
			else:
				grid.SetColLabelValue(i, "X-axis")

	# Validation column renderer for grdnames
	SetValidationEditor(grid)


def SetValidationEditor(grid):
	for j in range(grid.GetNumberCols()):
		if grid.GetCellValue(0, j) == "Validation":
			for i in range(2, grid.GetNumberRows()):
				# would be good to set a renderer here - not currently available for wxpython
				strChoices = ["Train", "Test", "Validation"]
				grid.SetCellEditor(i, j, wx.grid.GridCellChoiceEditor(strChoices))


class expSetup(wx.Panel):
	def _init_coll_bxsDep1_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.bxsDep2, 1, border=0, flag=wx.EXPAND)

	def _init_coll_bxsDep2_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.depTitleBar, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.pnl, 1, border=0, flag=wx.EXPAND)

	def _init_dep_sizers(self):
		# generated method, don't edit
		self.bxsDep1 = wx.BoxSizer(orient=wx.HORIZONTAL)

		self.bxsDep2 = wx.BoxSizer(orient=wx.VERTICAL)

		self._init_coll_bxsDep1_Items(self.bxsDep1)
		self._init_coll_bxsDep2_Items(self.bxsDep2)

		self.SetSizer(self.bxsDep1)

	def _init_coll_bxsInd1_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.bxsInd2, 1, border=0, flag=wx.EXPAND)

	def _init_coll_bxsInd2_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.indTitleBar, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.pnl, 1, border=0, flag=wx.EXPAND)

	def _init_ind_sizers(self):
		# generated method, don't edit
		self.bxsInd1 = wx.BoxSizer(orient=wx.HORIZONTAL)

		self.bxsInd2 = wx.BoxSizer(orient=wx.VERTICAL)

		self._init_coll_bxsInd1_Items(self.bxsInd1)
		self._init_coll_bxsInd2_Items(self.bxsInd2)

		self.SetSizer(self.bxsInd1)

	def _init_ctrls(self, prnt):
		# generated method, don't edit
		wx.Panel.__init__(self, id=wxID_EXPSETUP, name="expSetup", parent=prnt, pos=wx.Point(44, 58), size=wx.Size(768, 600), style=wx.TAB_TRAVERSAL)
		self.SetClientSize(wx.Size(760, 566))
		self.SetAutoLayout(True)
		self.SetToolTip("")

		self.pnl = fpb.FoldPanelBar(self, -1, wx.DefaultPosition, wx.DefaultSize, fpb.FPB_DEFAULT_STYLE, fpb.FPB_EXCLUSIVE_FOLD)

		self.depTitleBar = DepTitleBar(self, id=-1, text="Experiment setup", style=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self.indTitleBar = IndTitleBar(self, id=-1, text="Experiment setup", style=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)
		self.indTitleBar.Show(0)

		self._init_dep_sizers()

	def __init__(self, parent, id, pos, size, style, name):
		self._init_ctrls(parent)

		self.InitialiseFoldBar()

	def Reset(self):
		# create dependent variables grid
		self.grdNames.ClearGrid()
		ResizeGrids(self.grdNames, 100, 3, 2)

		# create independent variables grid
		self.grdIndLabels.ClearGrid()
		ResizeGrids(self.grdIndLabels, 100, 1, 3)

	def InitialiseFoldBar(self):
		# meta-data input
		self.depparamsitem = self.pnl.AddFoldPanel("Experiment setup parameters", collapsed=False)
		self.depparamsitem.Bind(wx.EVT_SIZE, self.OnDepWinSize, id=-1)
		self.depparamsitem.Bind(fpb.EVT_CAPTIONBAR, self.OnSelectDep, id=-1)

		self.grdNames = wx.grid.Grid(self.depparamsitem, id=wx.ID_ANY, pos=wx.Point(0, 0), size=wx.Size(40, 40), style=wx.SUNKEN_BORDER | wx.HSCROLL | wx.VSCROLL)
		self.grdNames.SetColLabelSize(20)
		self.grdNames.SetDefaultCellFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "MS Shell Dlg"))
		self.grdNames.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "MS Shell Dlg"))
		self.grdNames.SetLabelFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD, False, "MS Shell Dlg"))
		self.grdNames.SetRowLabelSize(50)
		self.grdNames.SetToolTip("")
		self.grdNames.SetDefaultCellBackgroundColour(wx.Colour(255, 255, 255))
		self.grdNames.Enable(False)
		self.grdNames.Bind(wx.grid.EVT_GRID_EDITOR_SHOWN, self.OnGrdNamesEditorShown)
		self.grdNames.CreateGrid(1, 3)

		# variable id input
		self.indparamsitem = self.pnl.AddFoldPanel("Independent variable labels", collapsed=True)
		self.indparamsitem.Bind(wx.EVT_SIZE, self.OnIndWinSize, id=-1)
		self.indparamsitem.Bind(fpb.EVT_CAPTIONBAR, self.OnSelectInd, id=-1)

		self.grdIndLabels = wx.grid.Grid(self.indparamsitem, id=wx.ID_ANY, pos=wx.Point(0, 0), size=wx.Size(40, 40), style=wx.SUNKEN_BORDER | wx.HSCROLL | wx.VSCROLL)
		self.grdIndLabels.SetColLabelSize(20)
		self.grdIndLabels.SetDefaultCellFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "MS Shell Dlg"))
		self.grdIndLabels.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "MS Shell Dlg"))
		self.grdIndLabels.SetLabelFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD, False, "MS Shell Dlg"))
		self.grdIndLabels.SetRowLabelSize(50)
		self.grdIndLabels.SetToolTip("")
		self.grdIndLabels.SetDefaultCellBackgroundColour(wx.Colour(255, 255, 255))
		self.grdIndLabels.Enable(False)
		self.grdIndLabels.Bind(wx.grid.EVT_GRID_EDITOR_SHOWN, self.OnGrdIndLabelsEditorShown)
		self.grdIndLabels.CreateGrid(100, 1)

		self.pnl.AddFoldPanelWindow(self.depparamsitem, self.grdNames, fpb.FPB_ALIGN_WIDTH)
		self.pnl.AddFoldPanelWindow(self.indparamsitem, self.grdIndLabels, fpb.FPB_ALIGN_WIDTH)

		self.depTitleBar.getGrid(self.grdNames)
		self.indTitleBar.getGrid(self.grdIndLabels)

	def OnGrdNamesEditorShown(self, event):
		if (self.grdNames.GetGridCursorCol() == 0) & (self.grdNames.GetGridCursorRow() == 1) is True:
			if self.grdNames.GetCellValue(1, 0) in ["0", ""]:
				value = "1"
			else:
				value = "0"
			for i in range(2, self.grdNames.GetNumberRows()):
				self.grdNames.SetCellValue(i, 0, value)

	def OnGrdIndLabelsEditorShown(self, event):
		if (self.grdIndLabels.GetGridCursorCol() == 0) & (self.grdIndLabels.GetGridCursorRow() == 0) is True:
			if self.grdIndLabels.GetCellValue(1, 0) in ["0", ""]:
				value = "1"
			else:
				value = "0"
			for i in range(1, self.grdIndLabels.GetNumberRows()):
				self.grdIndLabels.SetCellValue(i, 0, value)

	def OnDepWinSize(self, event):
		self.grdNames.SetSize((self.grdNames.GetSize()[0], self.pnl.GetSize()[1] * 0.9))
		self.depTitleBar.SetSize((self.pnl.GetSize()[0], 35))

	def OnIndWinSize(self, event):
		self.grdIndLabels.SetSize((self.grdIndLabels.GetSize()[0], self.pnl.GetSize()[1] * 0.9))
		self.indTitleBar.SetSize((self.pnl.GetSize()[0], 35))

	def OnSelectInd(self, event):
		self.indTitleBar.Show(0)
		self.depTitleBar.Show(1)
		self.pnl.Collapse(self.indparamsitem)
		self.pnl.Expand(self.depparamsitem)
		self._init_dep_sizers()

	def OnSelectDep(self, event):
		sizer = self.depTitleBar.GetSizer()
		self.indTitleBar.Show(1)
		self.depTitleBar.Show(0)
		self.pnl.Collapse(self.depparamsitem)
		self.pnl.Expand(self.indparamsitem)
		self._init_ind_sizers()


class DepTitleBar(bp.ButtonPanel):
	def _init_depbtnpanel_ctrls(self, prnt):
		bp.ButtonPanel.__init__(self, parent=prnt, id=-1, text="Experiment setup", agwStyle=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self.btnImportMetaData = wx.Button(parent=self, id=-1, label="Import", pos=wx.Point(12, 30), size=wx.Size(75, 23), style=0)
		self.btnImportMetaData.SetToolTip("Import sample details")
		self.btnImportMetaData.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))
		self.btnImportMetaData.Enable(False)
		self.btnImportMetaData.Bind(wx.EVT_BUTTON, self.OnBtnImportMetaDataButton, id=-1)

		self.btnAddName = wx.Button(parent=self, id=ID_BTNADDNAME, label="Add Label", pos=wx.Point(176, 30), size=wx.Size(75, 23), style=wx.TAB_TRAVERSAL)
		self.btnAddName.SetToolTip("")
		self.btnAddName.Enable(False)
		self.btnAddName.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))
		self.btnAddName.Bind(wx.EVT_BUTTON, self.OnBtnAddNameButton, id=ID_BTNADDNAME)

		self.btnAddClass = wx.Button(parent=self, id=ID_BTNADDCLASS, label="Add Class", pos=wx.Point(264, 30), size=wx.Size(75, 23), style=wx.TAB_TRAVERSAL)
		self.btnAddClass.SetToolTip("")
		self.btnAddClass.Enable(False)
		self.btnAddClass.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))
		self.btnAddClass.Bind(wx.EVT_BUTTON, self.OnBtnAddClassButton, id=ID_BTNADDCLASS)

		self.btnAddMask = wx.Button(parent=self, id=ID_BTNADDMASK, label="Add Mask", pos=wx.Point(520, 30), size=wx.Size(75, 23), style=wx.TAB_TRAVERSAL)
		self.btnAddMask.SetToolTip("")
		self.btnAddMask.Enable(False)
		self.btnAddMask.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))
		self.btnAddMask.Bind(wx.EVT_BUTTON, self.OnBtnAddMaskButton, id=ID_BTNADDMASK)

		self.spcGenMask = wx.SpinCtrl(parent=self, id=-1, initial=1, max=100, min=1, pos=wx.Point(444, 30), size=wx.Size(46, 23), style=wx.TAB_TRAVERSAL | wx.SP_ARROW_KEYS)
		self.spcGenMask.SetValue(50)
		self.spcGenMask.SetToolTip("")
		self.spcGenMask.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))

		self.cbGenerateMask = wx.CheckBox(parent=self, id=-1, label="Generate Mask", pos=wx.Point(355, 33), size=wx.Size(95, 23), style=wx.TAB_TRAVERSAL)
		self.cbGenerateMask.SetValue(False)
		self.cbGenerateMask.SetBackgroundColour(wx.Colour(167, 167, 243))
		self.cbGenerateMask.SetToolTip("")
		self.cbGenerateMask.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))

	def __init__(self, parent, id, text, style, alignment):

		self._init_depbtnpanel_ctrls(parent)

		self.CreateButtons()

	def getGrid(self, grid):
		self.grid = grid

	def getData(self, data):
		self.data = data

	def CreateButtons(self):
		self.Freeze()

		self.SetProperties()

		self.AddControl(self.btnImportMetaData)
		self.AddControl(self.btnAddName)
		self.AddControl(self.btnAddClass)
		self.AddControl(self.cbGenerateMask)
		self.AddControl(self.spcGenMask)
		self.AddControl(wx.StaticText(self, -1, " %"))
		self.AddControl(self.btnAddMask)

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

	def OnBtnAddNameButton(self, event):
		self.insertExpcols("Label")

	def OnBtnAddMaskButton(self, event):
		self.insertExpcols("Validation")

	def OnBtnAddClassButton(self, event):
		self.insertExpcols("Class")

	def insertExpcols(self, type):
		# insert new columns in exp setup grid
		colHeads = []
		last = -1
		for i in range(self.grid.GetNumberCols()):
			colHeads.append(self.grid.GetColLabelValue(i))
			if self.grid.GetCellValue(0, i) == type:
				last = i

		temp = colHeads[last + 1 : len(colHeads)]
		colHeads = colHeads[0 : last + 1]
		colHeads.append(type)
		colHeads = colHeads + temp

		self.grid.InsertCols(last + 1, 1)

		for i in range(len(colHeads)):
			self.grid.SetColLabelValue(i, colHeads[i])

		# automatically split data
		if (self.cbGenerateMask.GetValue() is True) and (type == "Validation") is True:
			PerSplit = self.spcGenMask.GetValue() / 100.0
			NoX = self.data["raw"].shape[0]
			Idx = _sample(NoX, int(scipy.around(NoX * PerSplit)))
			Ntest = Idx[0 : int(scipy.around(len(Idx) / 2))]
			Nval = Idx[int(scipy.around(len(Idx) / 2)) + 1 : len(Idx)]
			for i in range(NoX):
				self.grid.SetCellValue(i + 2, last + 1, "Train")
			for i in range(len(Ntest)):
				self.grid.SetCellValue(Ntest[i], last + 1, "Validation")
			for i in range(len(Nval)):
				self.grid.SetCellValue(Nval[i], last + 1, "Test")

		self.grid.SetCellAlignment(0, last + 1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
		self.grid.SetCellAlignment(1, last + 1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
		self.grid.SetCellTextColour(0, last + 1, wx.RED)
		self.grid.SetReadOnly(0, last + 1, 1)
		self.grid.SetCellValue(0, last + 1, type)
		self.grid.SetCellEditor(1, last + 1, wx.grid.GridCellBoolEditor())
		self.grid.SetCellRenderer(1, last + 1, wx.grid.GridCellBoolRenderer())
		self.grid.SetCellValue(1, last + 1, "0")
		SetValidationEditor(self.grid)

	def OnBtnImportMetaDataButton(self, event):
		dlg = wxImportMetaDataDialog(self, "dvar")
		if len(self.data["raw"]) > 0:
			##			  try:
			dlg.ShowModal()
			if dlg.GetButtonPress() == 1:
				out = dlg.GetMetaData()
				if len(out) > 0:
					headers = out[0]
					values = out[1]
					if len(values[0][len(values[0]) - 1].split("\r")) == 2:
						delim = "\r"
					else:
						delim = "\n"
					if len(values) == len(self.data["raw"]) + 2:
						ResizeGrids(self.grid, len(values) - 2, len(headers), 1)
						for i in range(1, len(headers) + 1):
							self.grid.SetColLabelValue(i, headers[i - 1])
						for i in range(len(values)):
							for j in range(1, len(values[i]) + 1):
								self.grid.SetCellValue(i, j, values[i][j - 1].split(delim)[0])
						self.grid.Enable(1)
						self.grid.EnableEditing(1)
						self.btnAddClass.Enable(1)
						self.btnAddName.Enable(1)
						self.btnAddMask.Enable(1)
						SetValidationEditor(self.grid)

					else:
						dlg = wx.MessageDialog(self, "The number of rows in" + "the experimental setup file does not\n" + "match the" + "number of rows in the data file", "Error!", wx.OK | wx.ICON_ERROR)
						try:
							dlg.ShowModal()
						finally:
							dlg.Destroy()
		##			  except Exception, error:
		##				  errorBox(self,'%s' %str(error))
		##				  dlg.Destroy()
		##				  raise

		else:
			dlg = wx.MessageDialog(self, "Please import experimental data", "Error", wx.OK | wx.ICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()


class IndTitleBar(bp.ButtonPanel):
	def _init_indbtnpanel_ctrls(self, prnt):
		bp.ButtonPanel.__init__(self, parent=prnt, id=-1, text="Experiment setup", agwStyle=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self.btnImportIndVar = wx.Button(parent=self, id=ID_BTNIMPIND, label="Import", name="btnImportIndVar", pos=wx.Point(636, 30), size=wx.Size(75, 23), style=0)
		self.btnImportIndVar.SetToolTip("Import vector of variables labels or values")
		self.btnImportIndVar.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))
		self.btnImportIndVar.Enable(False)
		self.btnImportIndVar.Bind(wx.EVT_BUTTON, self.OnBtnImportIndVarButton, id=ID_BTNIMPIND)

		self.stcRangeFrom = wx.lib.bcrtl.user.StaticTextCtrl.StaticTextCtrl(parent=self, id=-1, caption="", name="stcRangeFrom", pos=wx.Point(825, 30), size=wx.Size(39, 23), style=wx.TAB_TRAVERSAL, value="")
		self.stcRangeFrom.SetCaptionAlignment(wx.LEFT)
		self.stcRangeFrom.SetCaptionOffset(wx.Point(0, 4))
		self.stcRangeFrom.SetToolTip("")

		self.stcRangeTo = wx.lib.bcrtl.user.StaticTextCtrl.StaticTextCtrl(parent=self, id=-1, caption="", name="stcRangeTo", pos=wx.Point(889, 30), size=wx.Size(39, 23), style=wx.TAB_TRAVERSAL, value="")
		self.stcRangeTo.SetCaptionAlignment(wx.LEFT)
		self.stcRangeTo.SetCaptionOffset(wx.Point(-3, 4))
		self.stcRangeTo.SetToolTip("")

		self.btnInsertRange = wx.Button(parent=self, id=BTNINSRANGE, label="Insert", name="btnInsertRange", pos=wx.Point(932, 30), size=wx.Size(75, 23), style=0)
		self.btnInsertRange.SetToolTip("Insert linear range of real-valued numbers")
		self.btnInsertRange.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))
		self.btnInsertRange.Enable(False)
		self.btnInsertRange.Bind(wx.EVT_BUTTON, self.OnBtnInsertRangeButton, id=BTNINSRANGE)

	def __init__(self, parent, id, text, style, alignment):

		self._init_indbtnpanel_ctrls(parent)

		self.CreateButtons()

	def getGrid(self, grid):
		self.grid = grid

	def getData(self, data):
		self.data = data

	def CreateButtons(self):
		self.Freeze()

		self.SetProperties()

		self.AddControl(self.btnImportIndVar)
		self.AddControl(wx.StaticText(self, -1, "Insert range: "))
		self.AddControl(self.stcRangeFrom)
		self.AddControl(wx.StaticText(self, -1, " to "))
		self.AddControl(self.stcRangeTo)
		self.AddControl(self.btnInsertRange)

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

	def OnBtnImportIndVarButton(self, event):
		dlg = wxImportMetaDataDialog(self, "ivar")
		if len(self.data["raw"]) > 0:
			try:
				dlg.ShowModal()
				if dlg.GetButtonPress() == 1:
					values = dlg.GetMetaData()
					if len(values) - 1 == self.data["raw"].shape[1]:
						ResizeGrids(self.grid, len(values) - 1, len(values[0]), 3)
						for i in range(len(values)):
							for j in range(1, len(values[0]) + 1):
								self.grid.SetCellValue(i, j, values[i][j - 1])
					else:
						dlg = wx.MessageDialog(self, "The number of rows in " + "the import file does not\nmatch the " + "number of columns in the data file", "Error!", wx.OK | wx.ICON_ERROR)
						try:
							dlg.ShowModal()
						finally:
							dlg.Destroy()
			except Exception as error:
				errorBox(self, "%s" % str(error))
				dlg.Destroy()

	##				  raise

	def OnBtnInsertRangeButton(self, event):
		if self.stcRangeFrom.GetValue() and self.stcRangeTo.GetValue() not in [""]:
			self.data["xaxis"] = GetXaxis(self.stcRangeFrom.GetValue(), self.stcRangeTo.GetValue(), self.data["raw"].shape[1], self.grid)


class wxImportMetaDataDialog(wx.Dialog):
	def _init_import_ctrls(self, prnt):
		# generated method, don't edit
		wx.Dialog.__init__(self, id=wxID_WXIMPORTMETADATADIALOG, name="wx.ImportDialog", parent=prnt, pos=wx.Point(431, 325), size=wx.Size(417, 120), style=wx.DEFAULT_DIALOG_STYLE, title="Import")
		self.SetClientSize(wx.Size(409, 86))
		self.SetToolTip("")
		self.Center(wx.BOTH)

		self.swLoadX = wx.adv.SashWindow(id=wxID_WXIMPORTMETADATADIALOGSWLOADX, name="swLoadX", parent=self, pos=wx.Point(0, 0), size=wx.Size(408, 198), style=wx.CLIP_CHILDREN | wx.adv.SW_3D)
		self.swLoadX.SetToolTip("")

		self.btnBrowseArray = wx.Button(id=wxID_WXIMPORTMETADATADIALOGBTNBROWSEARRAY, label="Browse...", name="btnBrowseArray", parent=self.swLoadX, pos=wx.Point(320, 16), size=wx.Size(75, 23), style=0)
		self.btnBrowseArray.Bind(wx.EVT_BUTTON, self.OnBtnbrowsearrayButton, id=wxID_WXIMPORTMETADATADIALOGBTNBROWSEARRAY)

		self.stArray = wx.lib.bcrtl.user.StaticTextCtrl.StaticTextCtrl(caption="", id=wxID_WXIMPORTMETADATADIALOGSTARRAY, name="stArray", parent=self.swLoadX, pos=wx.Point(16, 16), size=wx.Size(296, 23), style=0, value="")

		self.btnOK = wx.Button(id=wxID_WXIMPORTMETADATADIALOGBTNOK, label="OK", name="btnOK", parent=self.swLoadX, pos=wx.Point(96, 48), size=wx.Size(104, 23), style=0)
		self.btnOK.Bind(wx.EVT_BUTTON, self.OnBtnOKButton, id=wxID_WXIMPORTMETADATADIALOGBTNOK)

		self.btnCancel = wx.Button(id=wxID_WXIMPORTMETADATADIALOGBTNCANCEL, label="Cancel", name="btnCancel", parent=self.swLoadX, pos=wx.Point(216, 48), size=wx.Size(107, 23), style=0)
		self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancelButton, id=wxID_WXIMPORTMETADATADIALOGBTNCANCEL)

	def __init__(self, parent, type):
		self._init_import_ctrls(parent)

		self.Type = type

	def OnBtnbrowsearrayButton(self, event):
		if self.Type == "ivar":
			msg = "Choose List of Independent Variable Identifiers"
		elif self.Type == "dvar":
			msg = "Choose Experiment Setup File"
		self.ArrayFile = wx.FileSelector(msg, "", "", "", "CSV files (*.csv)|*.csv")
		self.stArray.SetValue(self.ArrayFile)
		return self.ArrayFile

	def OnBtnOKButton(self, event):
		self.ButtonPress = 1
		self.Close()

	def OnBtnCancelButton(self, event):
		self.ButtonPress = 0
		self.Close()

	def GetMetaData(self):
		try:
			f = file(self.ArrayFile, "r")
			t = f.readlines()
			c = 0
			if self.Type == "dvar":
				values = []
				for each in t:
					a = each.split("\n")[0]
					a = a.split(",")
					if c == 0:
						headers = a
						c += 1
					elif c > 0:
						values.append(a)
				if c > 0:
					return headers, values
				else:
					return ()
			elif self.Type == "ivar":
				values = []
				for each in t:
					a = each.split("\n")[0]
					values.append(a.split(","))
				return values
		except:
			pass

	def GetButtonPress(self):
		return self.ButtonPress
