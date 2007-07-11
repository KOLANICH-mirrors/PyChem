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

import cElementTree as ET
import scipy
import wx
import wx.adv
import wx.lib.filebrowsebutton
from scipy import newaxis as nA
from wx.lib.anchors import LayoutAnchors

from . import Cluster, Dfa, Ga, Pca, Plsr, expSetup, mva, plotSpectra
from .mva.chemometrics import _index
from .utils import getByPath
from .utils.io import str_array

# whereami for binary dists etc
whereami = mva.__path__[0].split("mva")[0]
# whereami for stand alone dist
##whereami = mva.__path__[0].split('\library.zip\mva')[0]


def create(parent):
	return PyChemMain(parent)


[
	wxID_PYCHEMMAIN,
	wxID_PYCHEMMAINNBMAIN,
	wxID_PYCHEMMAINPLCLUSTER,
	wxID_PYCHEMMAINPLDFA,
	wxID_PYCHEMMAINPLEXPSET,
	wxID_PYCHEMMAINPLGADFA,
	wxID_PYCHEMMAINPLGADPLS,
	wxID_PYCHEMMAINPLGAPLSC,
	wxID_PYCHEMMAINPLPCA,
	wxID_PYCHEMMAINPLPLS,
	wxID_PYCHEMMAINPLPREPROC,
	wxID_PYCHEMMAINSBMAIN,
] = [wx.NewIdRef() for _init_ctrls in range(12)]

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

[
	MNUGRIDCOPY,
	MNUGRIDPASTE,
	MNUGRIDDELETECOL,
	MNUGRIDRENAMECOL,
] = [wx.NewIdRef() for _init_grid_menu_Items in range(4)]


def errorBox(window, error):
	dlg = wx.MessageDialog(window, "".join(("The following error occured:\n\n", error)), "Error!", wx.OK | wx.ICON_ERROR)
	try:
		dlg.ShowModal()
	finally:
		dlg.Destroy()


class PyChemMain(wx.Frame):
	_custom_classes = {"wx.Panel": ["expSetup", "plotSpectra", "Pca", "Cluster", "Dfa", "Plsr", "Ga"]}

	def _init_coll_mnuTools_Items(self, parent):
		# generated method, don't edit

		parent.Append(help="", id=wxID_PYCHEMMAINMNUTOOLSEXPSET, kind=wx.ITEM_NORMAL, text="Experiment Setup")
		parent.Append(help="", id=wxID_PYCHEMMAINMNUTOOLSPREPROC, kind=wx.ITEM_NORMAL, text="Spectral Pre-processing")
		parent.Append(help="", id=wxID_PYCHEMMAINMNUTOOLSMNUPCA, kind=wx.ITEM_NORMAL, text="Principal Components Analysis (PCA)")
		parent.Append(help="", id=wxID_PYCHEMMAINMNUTOOLSMNUCLUSTER, kind=wx.ITEM_NORMAL, text="Cluster Analysis")
		parent.Append(help="", id=wxID_PYCHEMMAINMNUTOOLSMNUDFA, kind=wx.ITEM_NORMAL, text="Discriminant Function Analysis (DFA)")
		parent.Append(help="", id=wxID_PYCHEMMAINMNUTOOLSMNUPLSR, kind=wx.ITEM_NORMAL, text="Partial Least Squares Regression (PLSR)")
		parent.Append(help="", id=wxID_PYCHEMMAINMNUTOOLSMNUGADFA, kind=wx.ITEM_NORMAL, text="GA-Discriminant Function Analysis")
		parent.Append(help="", id=wxID_PYCHEMMAINMNUTOOLSMNUGAPLSC, kind=wx.ITEM_NORMAL, text="GA-Partial Least Squares Calibration")
		self.Bind(wx.EVT_MENU, self.OnMnuToolsExpsetMenu, id=wxID_PYCHEMMAINMNUTOOLSEXPSET)
		self.Bind(wx.EVT_MENU, self.OnMnuToolsPreprocMenu, id=wxID_PYCHEMMAINMNUTOOLSPREPROC)
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
		parent.AddPage(imageId=-1, page=self.plPca, select=False, text="Principal Components Analysis")
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
		self.Bind(wx.EVT_MENU, self.OnMnuGridCopy, id=MNUGRIDCOPY)
		self.Bind(wx.EVT_MENU, self.OnMnuGridPaste, id=MNUGRIDPASTE)
		self.Bind(wx.EVT_MENU, self.OnMnuGridRenameColumn, id=MNUGRIDRENAMECOL)
		self.Bind(wx.EVT_MENU, self.OnMnuGridDeleteColumn, id=MNUGRIDDELETECOL)

	def _init_utils(self):
		# generated method, don't edit
		self.mnuMain = wx.MenuBar()

		self.mnuFile = wx.Menu(title="")

		self.mnuTools = wx.Menu(title="")

		self.mnuHelp = wx.Menu(title="")

		self.gridMenu = wx.Menu(title="")

		self._init_coll_mnuMain_Menus(self.mnuMain)
		self._init_coll_mnuFile_Items(self.mnuFile)
		self._init_coll_mnuTools_Items(self.mnuTools)
		self._init_coll_mnuHelp_Items(self.mnuHelp)
		self._init_grid_menu_Items(self.gridMenu)

	def _init_ctrls(self, prnt):
		# generated method, don't edit
		wx.Frame.__init__(self, id=wxID_PYCHEMMAIN, name="PyChemMain", parent=prnt, pos=wx.Point(0, 0), size=wx.Size(1024, 738), style=wx.DEFAULT_FRAME_STYLE, title="PyChem 3.0.2 Beta")
		self._init_utils()
		self.SetClientSize(wx.Size(1016, 704))
		self.SetToolTip("")
		self.SetHelpText("")
		self.Center(wx.BOTH)
		self.SetIcon(wx.Icon(os.path.join("ico", "pychem.ico"), wx.BITMAP_TYPE_ICO))
		self.SetMinSize(wx.Size(200, 400))
		self.SetMenuBar(self.mnuMain)
		self.Bind(wx.EVT_SIZE, self.OnMainFrameSize)

		self.nbMain = wx.Notebook(id=wxID_PYCHEMMAINNBMAIN, name="nbMain", parent=self, pos=wx.Point(0, 0), size=wx.Size(1016, 661), style=0)
		self.nbMain.SetToolTip("")
		self.nbMain.SetMinSize(wx.Size(200, 400))
		self.nbMain.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnNbMainNotebookPageChanging, id=wxID_PYCHEMMAINNBMAIN)
		self.nbMain.parent = self

		self.sbMain = wx.StatusBar(id=wxID_PYCHEMMAINSBMAIN, name="sbMain", parent=self, style=0)
		self.sbMain.SetToolTip("")
		self._init_coll_stbMain_Fields(self.sbMain)
		self.SetStatusBar(self.sbMain)

		self.plExpset = expSetup.expSetup(id=wxID_PYCHEMMAINPLEXPSET, name="plExpset", parent=self.nbMain, pos=wx.Point(0, 0), size=wx.Size(1008, 635), style=wx.TAB_TRAVERSAL)
		self.plExpset.getFrame(self)
		self.plExpset.SetToolTip("")

		self.plPreproc = plotSpectra.plotSpectra(id=wxID_PYCHEMMAINPLPREPROC, name="plPreproc", parent=self.nbMain, pos=wx.Point(0, 0), size=wx.Size(1008, 635), style=wx.TAB_TRAVERSAL)
		self.plPreproc.SetToolTip("")

		self.plPca = Pca.Pca(id=wxID_PYCHEMMAINPLPCA, name="plPca", parent=self.nbMain, pos=wx.Point(0, 0), size=wx.Size(1008, 635), style=wx.TAB_TRAVERSAL)
		self.plPca.SetToolTip("")

		self.plCluster = Cluster.Cluster(id=wxID_PYCHEMMAINPLCLUSTER, name="plCluster", parent=self.nbMain, pos=wx.Point(0, 0), size=wx.Size(1008, 635), style=wx.TAB_TRAVERSAL)
		self.plCluster.SetToolTip("")

		self.plDfa = Dfa.Dfa(id=wxID_PYCHEMMAINPLDFA, name="plDfa", parent=self.nbMain, pos=wx.Point(0, 0), size=wx.Size(1008, 635), style=wx.TAB_TRAVERSAL)
		self.plDfa.SetToolTip("")

		self.plPls = Plsr.Plsr(id=wxID_PYCHEMMAINPLPLS, name="plPls", parent=self.nbMain, pos=wx.Point(0, 0), size=wx.Size(1008, 635), style=wx.TAB_TRAVERSAL)
		self.plPls.SetToolTip("")

		self.plGadfa = Ga.Ga(id=wxID_PYCHEMMAINPLGADFA, name="plGadfa", parent=self.nbMain, pos=wx.Point(0, 0), size=wx.Size(1008, 635), style=wx.TAB_TRAVERSAL, type="DFA")
		self.plGadfa.SetToolTip("")

		self.plGapls = Ga.Ga(id=wxID_PYCHEMMAINPLGAPLSC, name="plGaplsc", parent=self.nbMain, pos=wx.Point(0, 0), size=wx.Size(1008, 635), style=wx.TAB_TRAVERSAL, type="PLS")
		self.plGapls.SetToolTip("")

		self._init_coll_nbMain_Pages(self.nbMain)

	def __init__(self, parent):
		self._init_ctrls(parent)

		# set defaults
		self.Reset()

	def OnMainFrameSize(self, event):
		event.Skip()

	def OnMnuHelpContentsMenu(self, event):
		from wx.tools import helpviewer

		helpviewer.main(["", os.path.join("docs", "PAChelp.hhp")])

	def OnMnuAboutContentsMenu(self, event):
		from wx.lib.wordwrap import wordwrap

		info = wx.adv.AboutDialogInfo()
		info.Name = "PyChem"
		info.Version = "3.0.2 Beta"
		info.Copyright = "(C) 2007 Roger Jarvis"
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
				self.Reset()
				if workSpace != 0:
					self.xmlLoad(tree, workSpace)
					self.data["exppath"] = loadFile
					self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILESAVEEXP, True)
					self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILESAVEWS, True)
					self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILELOADWS, True)
		finally:
			dlg.Destroy()

	def OnMnuFileLoadwsMenu(self, event):
		dlg = wxWorkspaceDialog(self, self.data["exppath"])
		if self.data["exppath"] is not None:
			try:
				dlg.ShowModal()
				workSpace = dlg.getWorkspace()
				tree = dlg.getTree()
				self.Reset(1)
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
					saveFile = dlg.GetPath()
					# workspace name entry dialog
					texTdlg = wx.TextEntryDialog(self, "Type in a name under which to save the current workspace", "Save Workspace as...", "Default")
					try:
						if texTdlg.ShowModal() == wx.ID_OK:
							wsName = texTdlg.GetValue()
					finally:
						texTdlg.Destroy()
					self.xmlSave(saveFile, wsName, "new")
					# activate workspace save menu option
					self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILESAVEEXP, True)
					self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILESAVEWS, True)
					self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILELOADWS, True)
					# show workspace dialog so that default can be edited
					dlgws = wxWorkspaceDialog(self, saveFile, dtype="Save")
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
			# text entry dialog
			dlg = wx.TextEntryDialog(self, "Type in a name under which to save the current workspace", "Save Workspace as...", "Default")
			try:
				if dlg.ShowModal() == wx.ID_OK:
					wsName = dlg.GetValue()
			finally:
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

				f = file(dlg.getFile(), "r")
				if dlg.Transpose() == 0:
					self.data["raw"] = scipy.io.read_array(f)
				else:
					self.data["raw"] = scipy.transpose(scipy.io.read_array(f))
				f.close()
				self.data["processed"] = self.data["raw"]

				# Resize grids
				expSetup.ResizeGrids(self.plExpset.grdNames, self.data["raw"].shape[0], 3, 2)
				expSetup.ResizeGrids(self.plExpset.grdIndLabels, self.data["raw"].shape[1], 0, 3)

				# activate ctrls
				self.EnableCtrls()

				# set x-range 1 to n
				self.plExpset.indTitleBar.stcRangeFrom.SetValue("1")
				self.plExpset.indTitleBar.stcRangeTo.SetValue(str(self.data["raw"].shape[1]))

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
				self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILESAVEEXP, True)
				self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILESAVEWS, False)
				self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILELOADWS, False)

				dlgConfirm = wxImportConfirmDialog(self, data, rows, cols)
				try:
					dlgConfirm.ShowModal()
				finally:
					dlgConfirm.Destroy()

				wx.EndBusyCursor()

		except Exception as error:
			wx.EndBusyCursor()
			self.Reset()
			dlg.Destroy()
			errorBox(self, "Unable to load array.\nPlease check file format\nand delimiter selection.")

	def OnMnuFileAppexitMenu(self, event):
		self.Close()

	def OnMnuToolsExpsetMenu(self, event):
		self.nbMain.SetSelection(0)

	def OnMnuToolsPreprocMenu(self, event):
		self.nbMain.SetSelection(1)

	def OnMnuToolsMnupcaMenu(self, event):
		self.nbMain.SetSelection(2)

	def OnMnuToolsMnuclusterMenu(self, event):
		self.nbMain.SetSelection(3)

	def OnMnuToolsMnuplsrMenu(self, event):
		self.nbMain.SetSelection(5)

	def OnMnuToolsMnudfaMenu(self, event):
		self.nbMain.SetSelection(4)

	def OnMnuToolsMnugadfaMenu(self, event):
		self.nbMain.SetSelection(6)

	def OnMnuToolsMnugaplscMenu(self, event):
		self.nbMain.SetSelection(7)

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
				dlg = wx.MessageDialog(self, "Are you sure you want to delete the column?", "Confirm", wx.OK | wx.CANCEL | wx.ICON_WARNING)
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
			if (grid.GetNumberCols() > 2) & (col != 0) is True:
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
		varList = "'proc':None,'class':None,'label':None," + "'split':None,'processlist':[],'xaxis':None," + "'class':None,'label':None,'validation':None," + "'pcscores':None,'pcloads':None,'pcpervar':None," + "'pceigs':None,'pcadata':None,'niporsvd':None," + "'indlabels':None,'plsloads':None,'pcatype':None," + "'dfscores':None,'dfloads':None,'dfeigs':None," + "'sampleidx':None,'variableidx':None," + "'rawtrunc':None,'proctrunc':None," + "'gadfachroms':None,'gadfascores':None," + "'gadfacurves':None,'gaplschroms':None," + "'gaplsscores':None,'gaplscurves':None," + "'gadfadfscores':None,'gadfadfaloads':None," + "'gaplsplsloads':None,'gridsel':None,'plotsel':None," + "'tree':None,'order':None,'plstrnpred':None," + "'plscvpred':None,'plststpred':None,'plsfactors':None," + "'rmsec':None,'rmsepc':None,'rmsept':None," + "'gacurrentchrom':None"

		if case == 0:
			exec('self.data = {"raw":None,"exppath":None,' + varList + "}")
		else:
			exec('self.data = {"raw":self.data["raw"],"exppath":self.data["exppath"],' + varList + "}")

		# for returning application to default settings
		self.plPreproc.Reset()
		self.plExpset.Reset()
		self.plPca.Reset()
		self.plDfa.Reset()
		self.plCluster.Reset()
		self.plPls.Reset()
		self.plGadfa.Reset()
		self.plGapls.Reset()

		# associate algorithm objects with data
		self.plExpset.depTitleBar.getData(self.data)
		self.plExpset.indTitleBar.getData(self.data)
		self.plPreproc.titleBar.getData(self.data)
		self.plPca.titleBar.getData(self.data)
		self.plCluster.titleBar.getData(self.data)
		self.plDfa.titleBar.getData(self.data)
		self.plPls.titleBar.getData(self.data)
		self.plGadfa.titleBar.getData(self.data)
		self.plGapls.titleBar.getData(self.data)

		# disable options on file menu
		self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILESAVEEXP, False)
		self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILESAVEWS, False)
		self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILELOADWS, False)

	def xmlSave(self, path, workspace, type=None):
		# type is either "new" (in which case workspace = "Default")
		# or path to saved xml file

		wx.BeginBusyCursor()

		proceed = 1
		if type is "new":
			# build a tree structure
			root = ET.Element("pychem_experiment")
			# save raw data
			rawdata = ET.SubElement(root, "rawdata")
			rawdata.set("key", "array")
			rawdata.text = str_array(self.data["raw"], col_sep="\t")

			# add workspace subelement
			Workspaces = ET.SubElement(root, "Workspaces")

		else:
			tree = ET.ElementTree(file=type)
			root = tree.getroot()
			# get workspaces subelement
			ch = root
			for each in ch:
				if each.tag == "Workspaces":
					Workspaces = each
			# check that workspace name is not currently used
			cWs = Workspaces
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
			except:
				dlg = wx.MessageDialog(self, "Unable to save under current name.\n\nCharacters " / +'such as "%", "&", "-", "+" can not be used for the workspace name', "Error!", wx.OK | wx.ICON_ERROR)
				try:
					dlg.ShowModal()
				finally:
					dlg.Destroy()

			# get preprocessing options
			if len(self.data["processlist"]) != 0:
				ppOptions = ET.SubElement(locals()[workspace], "ppOptions")
				for each in self.data["processlist"]:
					item = ET.SubElement(ppOptions, "item")
					item.set("key", "int")
					item.text = str(each)

			# save choice options
			Choices = ET.SubElement(locals()[workspace], "Choices")
			choiceCtrls = ["plPls.titleBar.cbxData", "plPca.titleBar.cbxPcaType", "plPca.titleBar.cbxPreprocType", "plPca.titleBar.cbxData", "plDfa.titleBar.cbxData", "plCluster.titleBar.cbxData", "plGadfa.titleBar.cbxFeature1", "plGadfa.titleBar.cbxFeature2", "plGapls.titleBar.cbxFeature1", "plGapls.titleBar.cbxFeature2"]

			for each in choiceCtrls:
				name = each.split(".")[len(each.split(".")) - 1]
				locals()[name] = ET.SubElement(Choices, each)
				locals()[name].set("key", "int")
				locals()[name].text = str(getByPath(self, each).GetCurrentSelection())

			# save spin, string and boolean ctrl values
			Controls = ET.SubElement(locals()[workspace], "Controls")
			# spin controls
			spinCtrls = ["plGadfa.titleBar.spnGaScoreFrom", "plGadfa.titleBar.spnGaScoreTo", "plGadfa.optDlg.spnGaMaxFac", "plGadfa.optDlg.spnGaMaxGen", "plGadfa.optDlg.spnGaVarsFrom", "plGadfa.optDlg.spnGaVarsTo", "plGadfa.optDlg.spnGaNoInds", "plGadfa.optDlg.spnGaNoRuns", "plGadfa.optDlg.spnGaRepUntil", "plGapls.titleBar.spnGaScoreFrom", "plGapls.titleBar.spnGaScoreTo", "plGapls.optDlg.spnGaMaxFac", "plGapls.optDlg.spnGaMaxGen", "plGapls.optDlg.spnGaVarsFrom", "plGapls.optDlg.spnGaVarsTo", "plGapls.optDlg.spnGaNoInds", "plGapls.optDlg.spnGaNoRuns", "plGapls.optDlg.spnGaRepUntil", "plPls.titleBar.spnPLSmaxfac", "plPls.titleBar.spnPLSfactor1", "plPls.titleBar.spnPLSfactor2", "plPca.titleBar.spnNumPcs1", "plPca.titleBar.spnNumPcs2", "plPca.titleBar.spnPCAnum", "plDfa.titleBar.spnDfaDfs", "plDfa.titleBar.spnDfaScore1", "plDfa.titleBar.spnDfaScore2", "plDfa.titleBar.spnDfaPcs"]

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

			# any wxgrid ctrl values
			wxGrids = ["plExpset.grdNames", "plExpset.grdIndLabels"]

			Grid = ET.SubElement(locals()[workspace], "Grid")

			for each in wxGrids:
				name = each.split(".")[len(each.split(".")) - 1]

				g, gn = self.getGrid(getByPath(self, each))

				locals()[name] = ET.SubElement(Grid, each)

				# save grid column labels
				columnLabels = ET.SubElement(locals()[name], "columnLabels")
				for item in gn:
					label = ET.SubElement(columnLabels, "label")
					label.set("key", "str")
					exec('label.text = "' + item + '"')

				# save grid cell values
				gridElements = ET.SubElement(locals()[name], "gridElements")
				for Rows in g:
					row = ET.SubElement(gridElements, "row")
					for Cols in Rows:
						if Cols == "":
							Cols = "0"
						col = ET.SubElement(row, "col")
						col.set("key", "str")
						exec('col.text = "' + Cols + '"')

			# any scipy arrays
			scipyArrays = ["pcscores", "pcloads", "pcpervar", "pceigs", "plsloads", "dfscores", "dfloads", "dfeigs", "gadfachroms", "gadfascores", "gadfacurves", "gaplschroms", "gaplsscores", "gaplscurves", "gadfadfscores", "gadfadfloads", "gaplsplsloads"]

			Array = ET.SubElement(locals()[workspace], "Array")
			for each in scipyArrays:
				try:
					# save array elements
					isthere = self.data[each]
					if isthere != None:
						locals()["item" + each] = ET.SubElement(Array, each)
						arrData = str_array(self.data[each],col_sep="\t")
						locals()["item" + each].set("key", "array")
						locals()["item" + each].text = arrData
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

			# wrap it in an ElementTree instance, and save as XML
			tree = ET.ElementTree(root)
			tree.write(path)

			# enable menu options
			self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILESAVEWS, True)
			self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILELOADWS, True)

		# end busy cursor
		wx.BeginBusyCursor()

	def xmlLoad(self, tree, workspace, type="new"):
		# load pychem experiments from saved xml files
		if type == "new":
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
			self.data["processed"] = self.data["raw"]

		# load workspace
		getWsElements = tree.getroot().findall("".join(("*/", workspace)))[0]

		for each in getWsElements:
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

			# load grids
			if each.tag == "Grid":
				grids = each
				for item in grids:
					gName = item.tag
					members = item
					for ind in members:
						if ind.tag == "columnLabels":
							cols = ind
							expSetup.ResizeGrids(getByPath(self, gName), 10, len(cols) - 1)
							count = 0
							for cName in cols:
								text = cName.text.split("\n")[0]
								exec("self." + gName + ".SetColLabelValue(" + str(count) + "," + '"' + text + '")')
								count += 1
						elif ind.tag == "gridElements":
							Rows = ind

							# grid resize according to type
							if gName == "plExpset.grdNames":
								expSetup.ResizeGrids(getByPath(self, gName), len(Rows) - 2, len(cols) - 1, 1)
							elif gName == "plExpset.grdIndLabels":
								expSetup.ResizeGrids(getByPath(self, gName), len(Rows) - 1, len(cols) - 1, 3)

							rCount = 0
							for r in Rows:
								Cols = r
								cCount = 0
								for c in Cols:
									exec("self." + gName + ".SetCellValue(" + str(rCount) + "," + str(cCount) + "," + '"' + c.text + '")')
									cCount += 1
								rCount += 1

					# Validation column renderer for grdnames
					expSetup.SetValidationEditor(self.plExpset.grdNames)

				# set exp details
				self.GetExperimentDetails()

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
								getRow.append(float(element))
							newArray.append(getRow)
						self.data[array.tag] = np.array(newArray)

					except:
						self.data[array.tag] = None

				# reload any plots
				for array in getArrays:
					for i in ["pc", "dfs", "gadfa", "gapls"]:
						if len(array.tag.split(i)) > 1:
							if i == "pc":
								self.plPca.titleBar.PlotPca()
							elif i == "dfs":
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

			# load global variables - currently just flags for re-running cluster
			# analysis and plsr
			if each.tag == "Flags":
				getVars = each
				for item in getVars:
					if (item.tag == "doClustering") & (item.text == "1") is True:
						self.plCluster.titleBar.RunClustering()
					elif (item.tag == "doPlsr") & (item.text == "1") is True:
						self.plPls.titleBar.runPls()

		# unlock ctrls
		self.EnableCtrls()

		# gather data
		self.GetExperimentDetails()

	def getGrid(self, grid):
		r = grid.GetNumberRows()
		c = grid.GetNumberCols()

		# get column labels
		gridcolhead = []
		for i in range(c):
			gridcolhead.append(grid.GetColLabelValue(i))

		# get grid contents
		gridout = []
		for i in range(r):
			row = []
			for j in range(c):
				row.append(grid.GetCellValue(i, j))
			gridout.append(row)

		return gridout, gridcolhead

	def GetExperimentDetails(self):
		self.plExpset.grdNames.SetGridCursor(2, 0)
		self.plExpset.grdIndLabels.SetGridCursor(1, 0)
		# get col headings
		colHeads = []
		self.data["label"], self.data["class"], self.data["validation"] = [], [], []
		for i in range(1, self.plExpset.grdNames.GetNumberCols()):
			colHeads.append(self.plExpset.grdNames.GetColLabelValue(i))
			# get label vector
			if (self.plExpset.grdNames.GetCellValue(0, i) == "Label") and (self.plExpset.grdNames.GetCellValue(1, i) == "1") is True:
				self.data["sampleidx"] = []
				for j in range(2, self.plExpset.grdNames.GetNumberRows()):
					if self.plExpset.grdNames.GetCellValue(j, 0) == "1":
						self.data["sampleidx"].append(j - 2)  # for removing samples from analysis
						self.data["label"].append(self.plExpset.grdNames.GetCellValue(j, i))

			# get class vector
			if (self.plExpset.grdNames.GetCellValue(0, i) == "Class") and (self.plExpset.grdNames.GetCellValue(1, i) == "1") is True:
				for j in range(2, self.plExpset.grdNames.GetNumberRows()):
					if self.plExpset.grdNames.GetCellValue(j, 0) == "1":
						try:
							self.data["class"].append(float(self.plExpset.grdNames.GetCellValue(j, i)))
						except:
							pass
			##				  self.plCluster.titleBar.dlg.spnNumClass.SetValue(max(self.data['class']))

			# get validation vector
			if (self.plExpset.grdNames.GetCellValue(0, i) == "Validation") and (self.plExpset.grdNames.GetCellValue(1, i) == "1") is True:
				for j in range(2, self.plExpset.grdNames.GetNumberRows()):
					if self.plExpset.grdNames.GetCellValue(j, 0) == "1":
						try:
							if self.plExpset.grdNames.GetCellValue(j, i) == "Train":
								self.data["validation"].append(0)
							elif self.plExpset.grdNames.GetCellValue(j, i) == "Validation":
								self.data["validation"].append(1)
							elif self.plExpset.grdNames.GetCellValue(j, i) == "Test":
								self.data["validation"].append(2)
						except:
							pass
				self.data["validation"] = np.array(self.data["validation"])

		# get x-axis labels/values
		num = 1
		xaxis = []
		for j in range(1, self.plExpset.grdIndLabels.GetNumberCols()):
			if self.plExpset.grdIndLabels.GetCellValue(0, j) == "1":
				self.data["variableidx"] = []
				for i in range(1, self.plExpset.grdIndLabels.GetNumberRows()):
					if self.plExpset.grdIndLabels.GetCellValue(i, 0) == "1":
						try:
							self.data["variableidx"].append(i - 1)  # for removing variables from analysis
							val = self.plExpset.grdIndLabels.GetCellValue(i, j)
							try:
								val = float(val)
								xaxis.append(val)
							except:
								xaxis.append(val)
								num = 0
								continue
						except:
							pass

		try:
			if num == 1:
				self.data["xaxis"] = np.array(xaxis)[:, nA]
			else:
				self.data["xaxis"] = scipy.arange(1, self.data["raw"].shape[1] + 1)[:, nA]

			self.data["indlabels"] = xaxis

			# remove any unwanted samples & variables, always following any preprocessing
			self.data["rawtrunc"] = scipy.take(self.data["raw"], self.data["variableidx"], 1)
			self.data["rawtrunc"] = scipy.take(self.data["rawtrunc"], self.data["sampleidx"], 0)

			if self.data["proc"] is not None:
				self.data["proctrunc"] = scipy.take(self.data["proc"], self.data["variableidx"], 1)
				self.data["proctrunc"] = scipy.take(self.data["proctrunc"], self.data["sampleidx"], 0)
		except:
			pass

		# change ga results lists
		try:
			self.plGapls.titleBar.CreateGaResultsTree(self.plGapls.optDlg.treGaResults, gacurves=self.data["gaplscurves"], chroms=self.data["gaplschroms"], varfrom=self.plGapls.optDlg.spnGaVarsFrom.GetValue(), varto=self.plGapls.optDlg.spnGaVarsTo.GetValue(), runs=self.plGapls.optDlg.spnGaNoRuns.GetValue() - 1)
		except:
			pass

		try:
			self.plGadfa.titleBar.CreateGaResultsTree(self.plGadfa.optDlg.treGaResults, gacurves=self.data["gadfacurves"], chroms=self.data["gadfachroms"], varfrom=self.plGadfa.optDlg.spnGaVarsFrom.GetValue(), varto=self.plGadfa.optDlg.spnGaVarsTo.GetValue(), runs=self.plGadfa.optDlg.spnGaNoRuns.GetValue() - 1)
		except:
			pass

		try:  # set number of centroids for cluster analysis based on class structure
			self.plCluster.optDlg.spnNumClass.SetValue(max(self.data["class"]))
		except:
			pass

	def EnableCtrls(self):
		self.plExpset.grdNames.Enable(1)
		self.plExpset.depTitleBar.btnImportMetaData.Enable(1)
		self.plExpset.depTitleBar.btnAddName.Enable(1)
		self.plExpset.depTitleBar.btnAddClass.Enable(1)
		self.plExpset.depTitleBar.btnAddMask.Enable(1)

		self.plExpset.grdIndLabels.Enable(1)
		self.plExpset.indTitleBar.btnImportIndVar.Enable(1)
		self.plExpset.indTitleBar.btnInsertRange.Enable(1)

		self.plPreproc.titleBar.btnPlotRaw.Enable(1)

		self.plPca.titleBar.btnRunPCA.Enable(1)

		self.plCluster.titleBar.btnRunClustering.Enable(1)

		self.plDfa.titleBar.btnRunDfa.Enable(1)

		self.plPls.titleBar.btnRunFullPls.Enable(1)

		self.plGadfa.titleBar.btnRunGa.Enable(1)

		self.plGapls.titleBar.btnRunGa.Enable(1)

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

		parent.AddWindow(self.fileBrowse, (0, 0), border=10, flag=wx.EXPAND, span=(1, 4))
		parent.AddSpacer(wx.Size(0, 0), (1, 0), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.cbTranspose, (1, 1), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.btnCancel, (1, 2), border=10, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.btnOK, (1, 3), border=10, flag=wx.EXPAND, span=(1, 1))

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
			dlg = wx.MessageDialog(self, "Unable to load data - this is not a PyChem Experiment file", "Error!", wx.OK | wx.ICON_ERROR)
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
