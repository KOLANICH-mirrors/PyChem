# -----------------------------------------------------------------------------
# Name:		   expSetup.py
# Purpose:
#
# Author:	   Roger Jarvis
#
# Created:	   2007/05/22
# RCS-ID:	   $Id$
# Copyright:   (c) 2007
# Licence:	   GNU General Public Licence
# -----------------------------------------------------------------------------
# Boa:FramePanel:expSetup

import os
import string

import scipy
import wx
import wx.adv
import wx.grid
import wx.lib.agw.buttonpanel as bp
import wx.lib.agw.foldpanelbar as fpb
import wx.lib.stattext
from wx.lib.anchors import LayoutAnchors

from .mva.chemometrics import _index, _sample

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


def valSplit(grid, data, pc, trunc="yes"):
	# get class col(s)
	cL1, cL2, currClass = [], [], []
	for i in range(grid.GetNumberCols()):
		# get active class col
		if grid.GetCellValue(0, i) in ["Class"]:
			if grid.GetCellValue(1, i) == "1":
				currClass.append(i)

	# no class structure therefore random split
	if currClass == []:
		PerSplit = pc / 100.0
		NoX = data["raw"].shape[0]
		Idx = _sample(NoX - 1, int(scipy.around(NoX * PerSplit)))
		Ntest = Idx[0 : int(scipy.around(len(Idx) / 2))]
		Nval = Idx[int(scipy.around(len(Idx) / 2)) + 1 : len(Idx)]
		mask = [0] * NoX
		for each in Ntest:
			mask[each] = 1
		for each in Nval:
			mask[each] = 2

	# split based upon class structure
	else:
		for i in range(data["raw"].shape[0]):
			cL1.append(int(grid.GetCellValue(i + 2, currClass[len(currClass) - 1])))
			cL, subCl = cL1, cL1
			if len(currClass) > 1:
				cL2.append(int(grid.GetCellValue(i + 2, currClass[len(currClass) - 2])))
				if max(cL1) > max(cL2):
					subCl, cL = cL1, cL2
				else:
					subCl, cL = cL2, cL1
		# no subclass of machine reps for instance
		if abs(len(scipy.unique(np.array(cL))) - len(scipy.unique(np.array(subCl)))) < 2:
			mask = [0] * len(cL)
			cL = np.array(cL)
			ucL = scipy.unique(cL)
			for i in range(len(ucL)):
				thisId = _index(cL, ucL[i])
				gS = len(thisId)
				nV = round(gS * (pc / 100.0))
				iNs = []
				while len(iNs) < nV:
					iNs = scipy.unique(scipy.around(scipy.rand(gS) * (gS - 1)))[0:nV]
				count = 1
				for each in iNs:
					if count <= round(nV / 2.0):
						mask[thisId[int(each)]] = 1
					else:
						mask[thisId[int(each)]] = 2
					count += 1
		else:
			mask = [0] * len(cL)
			cL = np.array(cL)
			ucL = scipy.unique(cL)
			for i in range(len(ucL)):
				thisId = _index(cL, ucL[i])
				thisSubCl = scipy.take(np.array(subCl), _index(cL, ucL[i]))
				gS = len(scipy.unique(thisSubCl))
				nV = round(gS * (pc / 100.0))
				if (nV > 1) & (gS > 3) is True:
					iNs = []
					while len(iNs) < nV:
						iNs = scipy.unique(scipy.around(scipy.rand(nV) * (gS - 1)))
					count = 1
					for each in iNs:
						vId = _index(np.array(subCl), scipy.unique(thisSubCl)[int(each)])
						if count <= int(round(nV / 2.0)):
							for item in vId:
								mask[int(item)] = 1
						else:
							for item in vId:
								mask[int(item)] = 2
						count += 1
				else:
					list = ["dummy"]
					end = 3
					if gS < 3:
						end = gS
					for i in range(1, end):
						seL = "dummy"
						while seL in list:
							seL = scipy.around(scipy.rand(1) * (gS - 1))[0]
						if seL not in list:
							list.append(seL)
							vId = _index(np.array(subCl), scipy.unique(thisSubCl)[seL])
							for item in vId:
								mask[int(item)] = i

	# remove for samples ot selected in grid
	if trunc in ["yes"]:
		for i in range(data["raw"].shape[0]):
			if grid.GetCellValue(i + 2, 0) == "0":
				del mask[i]

	return mask


def GetXaxis(From, To, Bins, Grid):
	if From and To not in [""]:
		# generate vector of x-labels
		int = (float(From) - float(To)) / (1 - Bins)
		ax = float(From) - int
		xaxis = scipy.dot(int, scipy.arange(1, Bins + 1)) + ax
		xaxis = scipy.around(scipy.reshape(xaxis, (len(xaxis), 1)), 2)
		# determine if any user defined variables present
		count = 0
		for r in range(1, Grid.GetNumberRows()):
			if len(Grid.GetRowLabelValue(r).split("U")) == 2:
				count += 1
			else:
				break
		# Append row to independent label grid
		Grid.SetCellAlignment(0, Grid.GetNumberCols() - 1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
		Grid.SetCellEditor(0, Grid.GetNumberCols() - 1, wx.grid.GridCellBoolEditor())
		Grid.SetCellRenderer(0, Grid.GetNumberCols() - 1, wx.grid.GridCellBoolRenderer())
		Grid.SetCellValue(0, Grid.GetNumberCols() - 1, "1")
		Grid.SetColLabelValue(Grid.GetNumberCols() - 1, "X-axis")
		# set variables for user defined data
		for i in range(1, count + 1):
			Grid.SetCellValue(i, Grid.GetNumberCols() - 1, Grid.GetCellValue(i, 1))
		# set variables for experimental data
		for i in range(count + 1, count + xaxis.shape[0] + 1):
			Grid.SetCellValue(i, Grid.GetNumberCols() - 1, "%.2f" % xaxis[i - count - 1, 0])

	return xaxis


def ResizeGrids(grid, rows, cols, type=None):
	grid.ClearGrid()
	if grid.GetNumberCols() - 1 > cols + 1:
		grid.DeleteCols(cols + 1, grid.GetNumberCols())
	elif grid.GetNumberCols() - 1 < cols + 1:
		grid.AppendCols(cols + 1 - grid.GetNumberCols())

	if grid.GetNumberRows() > rows + 1:
		grid.DeleteRows(rows + 1, grid.GetNumberRows())
	elif grid.GetNumberRows() < rows + 1:
		grid.AppendRows(rows + 1 - grid.GetNumberRows())

	if type in [0]:
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

	if type in [1, 2]:
		grid.AppendRows(1)
		grid.SetRowLabelValue(0, "Type")
		grid.SetRowLabelValue(1, "Iterative")
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
		grid.SetRowLabelValue(0, "Iterative")
		for i in range(1, grid.GetNumberRows()):
			grid.SetRowLabelValue(i, str(i))
			grid.SetReadOnly(i, 1, 0)
			grid.SetCellBackgroundColour(i, 1, wx.WHITE)
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

	if type == -1:
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

		parent.Add(self.bxsDep2, 1, border=0, flag=wx.EXPAND)

	def _init_coll_bxsDep2_Items(self, parent):
		# generated method, don't edit

		parent.Add(self.depTitleBar, 0, border=0, flag=wx.EXPAND)
		parent.Add(self.pnl, 1, border=0, flag=wx.EXPAND)

	def _init_dep_sizers(self):
		# generated method, don't edit
		self.bxsDep1 = wx.BoxSizer(orient=wx.HORIZONTAL)

		self.bxsDep2 = wx.BoxSizer(orient=wx.VERTICAL)

		self._init_coll_bxsDep1_Items(self.bxsDep1)
		self._init_coll_bxsDep2_Items(self.bxsDep2)

		self.SetSizer(self.bxsDep1)

	def _init_coll_bxsInd1_Items(self, parent):
		# generated method, don't edit

		parent.Add(self.bxsInd2, 1, border=0, flag=wx.EXPAND)

	def _init_coll_bxsInd2_Items(self, parent):
		# generated method, don't edit

		parent.Add(self.indTitleBar, 0, border=0, flag=wx.EXPAND)
		parent.Add(self.pnl, 1, border=0, flag=wx.EXPAND)

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
		self.pnl.SetConstraints(LayoutAnchors(self.pnl, True, True, True, True))
		self.pnl.SetAutoLayout(True)
		##		  self.pnl.Bind(wx.EVT_SIZE,self.OnPanelSize)

		self.depTitleBar = DepTitleBar(self, id=-1, text="Experiment setup", style=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self.indTitleBar = IndTitleBar(self, id=-1, text="Experiment setup", style=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)
		self.indTitleBar.Show(0)

		self._init_dep_sizers()

	def __init__(self, parent, id, pos, size, style, name):
		self._init_ctrls(parent)

		self.InitialiseFoldBar()

	##	  def OnPanelSize(self, event):
	##		  self.Refresh()

	def Reset(self, case=0):
		if case == 0:
			# create dependent variables grid
			self.grdNames.ClearGrid()
			ResizeGrids(self.grdNames, 100, 3, 2)
			# create independent variables grid
			self.grdIndLabels.ClearGrid()
			ResizeGrids(self.grdIndLabels, 100, 1, 3)

	def InitialiseFoldBar(self):
		# get fold panel icons
		icons = wx.ImageList(16, 16)
		icons.Add(wx.Bitmap(os.path.join("bmp", "arrown.png"), wx.BITMAP_TYPE_PNG))
		icons.Add(wx.Bitmap(os.path.join("bmp", "arrows.png"), wx.BITMAP_TYPE_PNG))

		# meta-data input
		self.depparamsitem = self.pnl.AddFoldPanel("Experiment setup parameters", collapsed=False, foldIcons=icons)
		self.depparamsitem.Bind(wx.EVT_SIZE, self.OnDepWinSize, id=-1)
		self.depparamsitem.Bind(fpb.EVT_CAPTIONBAR, self.OnSelectDep, id=-1)

		self.grdNames = wx.grid.Grid(self.depparamsitem, id=wx.ID_ANY, pos=wx.Point(0, 23), size=wx.Size(40, 40), style=wx.SUNKEN_BORDER | wx.HSCROLL | wx.VSCROLL)
		self.grdNames.SetColLabelSize(20)
		self.grdNames.SetDefaultCellFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "MS Shell Dlg"))
		self.grdNames.SetLabelFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD, False, "MS Shell Dlg"))
		self.grdNames.SetConstraints(LayoutAnchors(self.grdNames, True, True, True, True))
		self.grdNames.SetRowLabelSize(50)
		self.grdNames.SetToolTip("")
		self.grdNames.SetDefaultCellBackgroundColour(wx.Colour(255, 255, 255))
		self.grdNames.Enable(False)
		self.grdNames.Bind(wx.grid.EVT_GRID_EDITOR_SHOWN, self.OnGrdNamesEditorShown)
		self.grdNames.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnGrdNamesRightDown)
		self.grdNames.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnGrdNamesCellLeftDown)
		self.grdNames.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnGrdNamesLabelLeftClick)
		self.grdNames.CreateGrid(1, 3)

		# variable id input
		self.indparamsitem = self.pnl.AddFoldPanel("Independent variable labels", collapsed=True, foldIcons=icons)
		self.indparamsitem.Bind(wx.EVT_SIZE, self.OnIndWinSize, id=-1)
		self.indparamsitem.Bind(fpb.EVT_CAPTIONBAR, self.OnSelectInd, id=-1)

		self.grdIndLabels = wx.grid.Grid(self.indparamsitem, id=wx.ID_ANY, pos=wx.Point(0, 23), size=wx.Size(40, 40), style=wx.SUNKEN_BORDER | wx.HSCROLL | wx.VSCROLL)
		self.grdIndLabels.SetColLabelSize(20)
		self.grdIndLabels.SetConstraints(LayoutAnchors(self.grdIndLabels, True, True, True, True))
		self.grdIndLabels.SetRowLabelSize(50)
		self.grdIndLabels.SetToolTip("")
		self.grdIndLabels.SetDefaultCellBackgroundColour(wx.Colour(255, 255, 255))
		self.grdIndLabels.Enable(False)
		self.grdIndLabels.Bind(wx.grid.EVT_GRID_EDITOR_SHOWN, self.OnGrdIndLabelsEditorShown)
		self.grdIndLabels.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnGrdIndLabelsCellRightDown)
		self.grdIndLabels.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnGrdIndLabelsCellLeftDown)
		self.grdIndLabels.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.OnGrdIndLabelsLabelRightDown)
		self.grdIndLabels.CreateGrid(100, 1)

		self.pnl.AddFoldPanelWindow(self.depparamsitem, self.grdNames, fpb.FPB_ALIGN_WIDTH)
		self.pnl.AddFoldPanelWindow(self.indparamsitem, self.grdIndLabels, fpb.FPB_ALIGN_WIDTH)

		self.depTitleBar.getGrid(self.grdNames)
		self.indTitleBar.getGrid(self.grdIndLabels)

	##		  depsizer = wx.BoxSizer(wx.VERTICAL)
	##		  depsizer.Add(self.grdNames, 0, wx.EXPAND)
	##		  self.depparamsitem.SetSizer(depsizer)
	##
	##		  indsizer = wx.BoxSizer(wx.VERTICAL)
	##		  indsizer.Add(self.grdIndLabels, 0, wx.EXPAND)
	##		  self.indparamsitem.SetSizer(indsizer)

	def getFrame(self, frameParent):
		frameParent._init_utils()
		self.frameParent = frameParent

	def OnGrdIndLabelsCellRightDown(self, event):
		pt = event.GetPosition()
		self.indTitleBar.data["gridsel"] = self.grdIndLabels
		self.frameParent.PopupMenu(self.frameParent.gridMenu, pt)

	def OnGrdIndLabelsLabelRightDown(self, event):
		# menu to delete udef row
		pt = event.GetPosition()
		self.indTitleBar.data["gridsel"] = self.grdIndLabels
		self.frameParent.PopupMenu(self.frameParent.indRowMenu, pt)

	def OnGrdNamesRightDown(self, event):
		pt = event.GetPosition()
		self.depTitleBar.data["gridsel"] = self.grdNames
		self.frameParent.PopupMenu(self.frameParent.gridMenu, pt)

	def OnGrdNamesLabelLeftClick(self, event):
		# create index based on selected column order
		col = event.GetCol()
		order, rLab = [], []
		for i in range(2, self.grdNames.GetNumberRows()):
			rLab.append(self.grdNames.GetRowLabelValue(i))
			order.append(self.grdNames.GetCellValue(i, col))
		index = scipy.argsort(order)
		# create list of grid contents
		gList = []
		for i in index:
			tp = []
			for j in range(self.grdNames.GetNumberCols()):
				tp.append(self.grdNames.GetCellValue(i + 2, j))
			gList.append(tp)
		# replace current grid contents with ordered
		for i in range(len(gList)):
			self.grdNames.SetRowLabelValue(i + 2, rLab[index[i]])
			for j in range(self.grdNames.GetNumberCols()):
				self.grdNames.SetCellValue(i + 2, j, gList[i][j])

	def OnGrdIndLabelsCellLeftDown(self, event):
		# get position
		r, c = event.GetRow(), event.GetCol()
		# reposition cursor
		self.grdIndLabels.SetGridCursor(event.GetRow(), event.GetCol())
		# if first column of grid then change chkbox
		if c == 0:
			if self.grdIndLabels.GetCellValue(r, 0) == "0":
				sel = "1"
			else:
				sel = "0"
			if r < 1:
				self.grdIndLabels.SetCellValue(r, 0, sel)
			else:
				if self.grdIndLabels.GetCellValue(0, 0) == "0":
					self.grdIndLabels.SetCellValue(r, 0, sel)
				else:
					for row in range(r, self.grdIndLabels.GetNumberRows()):
						self.grdIndLabels.SetCellValue(row, 0, sel)

	##		  #manage column idx
	##		  if (r == 0) and (c>0) is True:
	##			  self.data['indvarsel'][c-1] = -1*self.data['indvarsel'][c-1]

	def OnGrdNamesCellLeftDown(self, event):
		# get position
		r, c = event.GetRow(), event.GetCol()
		# reposition cursor
		self.grdNames.SetGridCursor(event.GetRow(), event.GetCol())
		# if first column of grid then change chkbox
		if c == 0:
			if self.grdNames.GetCellValue(r, 0) == "0":
				sel = "1"
			else:
				sel = "0"
			if 0 < r < 2:
				self.grdNames.SetCellValue(r, 0, sel)
			else:
				if self.grdNames.GetCellValue(1, 0) == "0":
					self.grdNames.SetCellValue(r, 0, sel)
				else:
					for row in range(r, self.grdNames.GetNumberRows()):
						self.grdNames.SetCellValue(row, 0, sel)

	##		  #manage column idx
	##		  if (r == 1) and (c>0) is True:
	##			  self.depTitleBar.data['depvarsel'][c-1] = -1*self.depTitleBar.data['depvarsel'][c-1]

	def OnGrdNamesEditorShown(self, event):
		if (self.grdNames.GetGridCursorCol() == 0) & (self.grdNames.GetGridCursorRow() == 1) is True:
			if self.grdNames.GetCellValue(1, 0) in ["0", ""]:
				value = "1"
			else:
				value = "0"

	##				  for i in range(2,self.grdNames.GetNumberRows()):
	##					  self.grdNames.SetCellValue(i,0,value)

	def OnGrdIndLabelsEditorShown(self, event):
		if (self.grdIndLabels.GetGridCursorCol() == 0) & (self.grdIndLabels.GetGridCursorRow() == 0) is True:
			if self.grdIndLabels.GetCellValue(1, 0) in ["0", ""]:
				value = "1"
			else:
				value = "0"

	##				  for i in range(1,self.grdIndLabels.GetNumberRows()):
	##					  self.grdIndLabels.SetCellValue(i,0,value)

	def SizeGrdNames(self):
		self.depTitleBar.SetSize((self.pnl.GetSize()[0], 49))
		self.grdNames.SetSize((self.grdNames.GetSize()[0], self.pnl.GetSize()[1] - 30))
		self.pnl.Refresh()

	def OnDepWinSize(self, event):
		self.SizeGrdNames()

	def SizeGrdIndLabels(self):
		self.indTitleBar.SetSize((self.pnl.GetSize()[0], 49))
		self.grdIndLabels.SetSize((self.grdIndLabels.GetSize()[0], self.pnl.GetSize()[1] - 30))
		self.pnl.Refresh()

	def OnIndWinSize(self, event):
		self.SizeGrdIndLabels()

	def OnSelectInd(self, event):
		self.indTitleBar.Show(0)
		self.depTitleBar.Show(1)
		self.pnl.Collapse(self.indparamsitem)
		self.pnl.Expand(self.depparamsitem)
		self._init_dep_sizers()

	def OnSelectDep(self, event):
		self.indTitleBar.Show(1)
		self.depTitleBar.Show(0)
		self.pnl.Collapse(self.depparamsitem)
		self.pnl.Expand(self.indparamsitem)
		self._init_ind_sizers()


class DepTitleBar(bp.ButtonPanel):
	def _init_depbtnpanel_ctrls(self, prnt):
		bp.ButtonPanel.__init__(self, parent=prnt, id=-1, text="Experiment setup", agwStyle=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self.btnImportMetaData = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "import.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Import metadata", longHelp="Import metadata describing the samples")
		self.btnImportMetaData.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnImportMetaDataButton, id=self.btnImportMetaData.GetId())

		self.btnAddName = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "addlabel.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Add label column", longHelp="Add label column")
		self.btnAddName.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnAddNameButton, id=self.btnAddName.GetId())

		self.btnAddClass = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "addclass.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Add class column", longHelp="Add class column")
		self.btnAddClass.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnAddClassButton, id=self.btnAddClass.GetId())

		self.btnAddMask = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "addvalidation.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Add validation column", longHelp="Add validation column")
		self.btnAddMask.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnAddMaskButton, id=self.btnAddMask.GetId())

		self.spcGenMask = wx.SpinCtrl(parent=self, id=-1, initial=1, max=50, min=1, pos=wx.Point(444, 30), size=wx.Size(46, 23), style=wx.TAB_TRAVERSAL | wx.SP_ARROW_KEYS)
		self.spcGenMask.SetValue(50)
		self.spcGenMask.SetToolTip("")

		self.cbGenerateMask = wx.CheckBox(parent=self, id=-1, label="", pos=wx.Point(355, 33), size=wx.Size(14, 13), style=wx.TAB_TRAVERSAL | wx.TRANSPARENT_WINDOW)
		self.cbGenerateMask.SetValue(False)
		self.cbGenerateMask.SetToolTip("")

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

		self.AddButton(self.btnImportMetaData)
		self.AddSeparator()
		self.AddButton(self.btnAddName)
		self.AddButton(self.btnAddClass)
		self.AddButton(self.btnAddMask)
		self.AddControl(self.cbGenerateMask)
		self.AddControl(wx.lib.stattext.GenStaticText(self, -1, "Split data", style=wx.TRANSPARENT_WINDOW))
		self.AddControl(self.spcGenMask)
		self.AddControl(wx.lib.stattext.GenStaticText(self, -1, " %", style=wx.TRANSPARENT_WINDOW))

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

	def OnBtnAddNameButton(self, event):
		self.insertExpcols("Label")

	def OnBtnAddMaskButton(self, event):
		self.insertExpcols("Validation")

	def OnBtnAddClassButton(self, event):
		self.insertExpcols("Class")

	def insertExpcols(self, type):
		# insert new columns in exp setup grid
		colHeads, currClass = [], []
		last = -1
		for i in range(self.grid.GetNumberCols()):
			colHeads.append(self.grid.GetColLabelValue(i))
			if self.grid.GetCellValue(0, i) == type:
				last = i
			# get active class col
			if self.grid.GetCellValue(0, i) in ["Class"]:
				if self.grid.GetCellValue(1, i) == "1":
					currClass.append(i)

		# sort out column headings
		temp = colHeads[last + 1 : len(colHeads)]
		colHeads = colHeads[0 : last + 1]
		colHeads.append(type)
		colHeads = colHeads + temp

		##		  #sort out column indexing
		##		  nI = max(abs(np.array(self.data['depvarsel'])))+1
		##		  temp = self.data['depvarsel'][last+1:len(colHeads)-1]
		##		  self.data['depvarsel'] = self.data['depvarsel'][0:last+1]
		##		  self.data['depvarsel'].append(nI)
		##		  self.data['depvarsel'].extend(temp)

		self.grid.InsertCols(last + 1, 1)

		for i in range(len(colHeads)):
			self.grid.SetColLabelValue(i, colHeads[i])

		# automatically split data
		if (self.cbGenerateMask.GetValue() is True) & (type == "Validation") is True:
			try:
				mask = valSplit(self.grid, self.data, self.spcGenMask.GetValue(), trunc="no")
				options = ["Train", "Validation", "Test"]
				for i in range(len(mask)):
					self.grid.SetCellValue(i + 2, last + 1, options[int(mask[i])])
			except:
				pass

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
			try:
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
			except Exception as error:
				errorBox(self, "%s" % str(error))
				dlg.Destroy()
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

		self.btnImportIndVar = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "import.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Import independent variable IDs", longHelp="Import independent variable IDs")
		self.btnImportIndVar.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnImportIndVarButton, id=self.btnImportIndVar.GetId())

		self.stcRangeFrom = wx.TextCtrl(id=-1, name="stcRangeFrom", parent=self, pos=wx.Point(136, 56), size=wx.Size(75, 21), style=0, value="")
		self.stcRangeFrom.SetToolTip("")

		self.stcRangeTo = wx.TextCtrl(id=-1, name="stcRangeTo", parent=self, pos=wx.Point(136, 56), size=wx.Size(75, 21), style=0, value="")
		self.stcRangeTo.SetToolTip("")

		self.btnInsertRange = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "insertxvar.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Insert X-variables", longHelp="Insert X-variables using range")
		self.btnInsertRange.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnInsertRangeButton, id=self.btnInsertRange.GetId())

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

		self.AddButton(self.btnImportIndVar)
		self.AddSeparator()
		self.AddControl(wx.lib.stattext.GenStaticText(self, -1, "Insert range: ", style=wx.TRANSPARENT_WINDOW))
		self.AddControl(self.stcRangeFrom)
		self.AddControl(wx.lib.stattext.GenStaticText(self, -1, " to ", style=wx.TRANSPARENT_WINDOW))
		self.AddControl(self.stcRangeTo)
		self.AddButton(self.btnInsertRange)

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
			self.grid.AppendCols(1)
			##			  #keep indexing up to date
			##			  self.data['indvarsel'].append(max(np.array(self.data['indvarsel']))+1)
			# check for user def vars
			countpos = 0
			for r in range(1, self.grid.GetNumberRows()):
				if len(self.grid.GetRowLabelValue(r).split("U")) > 1:
					countpos += 1
				else:
					break
			self.data["xaxis"] = GetXaxis(self.stcRangeFrom.GetValue(), self.stcRangeTo.GetValue(), self.data["raw"].shape[1] - countpos, self.grid)


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

		self.stArray = wx.lib.stattext.GenStaticText(self, -1, "", pos=wx.Point(16, 16), size=wx.Size(296, 23), style=0)

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
			f = open(self.ArrayFile)
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
