# Boa:Frame:PyChemMain

import string
import sys

import cElementTree as ET
import scipy
import wx
import wx.adv
from scipy import newaxis as nA
from wx.lib.anchors import LayoutAnchors

from . import Cluster, Dfa, Ga, Pca, Plsr, expSetup, plotSpectra
from .chemometrics import _index
from .utils import getByPath


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

[wxID_PYCHEMMAINMNUHELPCONTENTS] = [wx.NewIdRef() for _init_coll_mnuHelp_Items in range(1)]

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
	wxID_WXIMPORTDIALOG,
	wxID_WXIMPORTDIALOGBTNBROWSEARRAY,
	wxID_WXIMPORTDIALOGBTNCANCEL,
	wxID_WXIMPORTDIALOGBTNOK,
	wxID_WXIMPORTDIALOGCBCOMMADELIM,
	wxID_WXIMPORTDIALOGCBOTHER,
	wxID_WXIMPORTDIALOGCBSEMIDELIM,
	wxID_WXIMPORTDIALOGCBSPACEDELIM,
	wxID_WXIMPORTDIALOGCBTABDELIM,
	wxID_WXIMPORTDIALOGCBTRANSPOSE,
	wxID_WXIMPORTDIALOGSTARRAY,
	wxID_WXIMPORTDIALOGSWLOADX,
	wxID_WXIMPORTDIALOGTXTOTHER,
] = [wx.NewIdRef() for _init_import_ctrls in range(13)]

[
	wxID_WXSAVEWORKSPACEDIALOG,
	wxID_WXSAVEWORKSPACEDIALOGBTNCANCEL,
	wxID_WXSAVEWORKSPACEDIALOGBTNDELETE,
	wxID_WXSAVEWORKSPACEDIALOGBTNEDIT,
	wxID_WXSAVEWORKSPACEDIALOGBTNOK,
	wxID_WXSAVEWORKSPACEDIALOGLBSAVEWORKSPACE,
] = [wx.NewIdRef() for _init_savews_ctrls in range(6)]


def errorBox(window, error):
	dlg = wx.MessageDialog(window, "".join(("The following error occured:\n\n", error)), "Error!", wx.OK | wx.ICON_ERROR)
	try:
		dlg.ShowModal()
	finally:
		dlg.Destroy()


def load(filename, delim="\t"):
	"""for importing delimited ASCII files"""
	f = file(filename, "r")
	lines = f.readlines()
	f.close()
	c = 0
	lineOut = []
	for row in lines:
		myline = []
		splitrow = row.strip().split("\n")
		splitrow = splitrow[0].strip().split("\r")
		splitrow = splitrow[0].strip().split(delim)

		for item in splitrow:
			try:
				myline.append(float(item))
			except:
				continue

		if myline != []:
			lineOut.append(np.array(myline))

	return np.array(lineOut)


def save(myarray, filename):
	"""Export array to a tab delimited file"""
	size = myarray.shape
	f = file(filename, "w")
	for line in myarray:
		c = 0
		for item in line:
			if c == size[1] - 1:
				f.write(repr(item))
			else:
				f.write(repr(item) + "\t")
				c = c + 1
	f.write("\n")
	f.close()


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
		self.Bind(wx.EVT_MENU, self.OnMnuHelpContentsMenu, id=wxID_PYCHEMMAINMNUHELPCONTENTS)

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

	def _init_utils(self):
		# generated method, don't edit
		self.mnuMain = wx.MenuBar()

		self.mnuFile = wx.Menu(title="")

		self.mnuTools = wx.Menu(title="")

		self.mnuHelp = wx.Menu(title="")

		self._init_coll_mnuMain_Menus(self.mnuMain)
		self._init_coll_mnuFile_Items(self.mnuFile)
		self._init_coll_mnuTools_Items(self.mnuTools)
		self._init_coll_mnuHelp_Items(self.mnuHelp)

	def _init_ctrls(self, prnt):
		# generated method, don't edit
		wx.Frame.__init__(self, id=wxID_PYCHEMMAIN, name="PyChemMain", parent=prnt, pos=wx.Point(0, 0), size=wx.Size(1024, 738), style=wx.DEFAULT_FRAME_STYLE, title="PyChem 3.0.0")
		self._init_utils()
		self.SetClientSize(wx.Size(1016, 704))
		self.SetToolTip("")
		self.SetHelpText("")
		self.Center(wx.BOTH)
		self.SetMinSize(wx.Size(200, 400))
		self.SetMenuBar(self.mnuMain)

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

	def OnMnuHelpContentsMenu(self, event):
		event.Skip()

	def OnMnuFileLoadexpMenu(self, event):
		loadFile = wx.FileSelector("Load PyChem Experiment", "", "", "", "XML files (*.xml)|*.xml")

		dlg = wxSaveWorkspaceDialog(self, loadFile)
		##		  try:
		dlg.ShowModal()
		tree = dlg.getTree()
		dlg.clearTree()
		workSpace = dlg.getWorkspace()
		self.Reset()
		self.xmlLoad(tree, workSpace)
		self.data["exppath"] = loadFile
		self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILESAVEEXP, 1)
		self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILESAVEWS, 1)
		self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILELOADWS, 1)

	##		  except Exception, error:
	##			  errorBox(self,'%s' %str(error))

	def OnMnuFileLoadwsMenu(self, event):
		dlg = wxSaveWorkspaceDialog(self, self.data["exppath"])
		dlg.ShowModal()
		workSpace = dlg.getWorkspace()
		if workSpace is not None:
			tree = dlg.getTree()
			##			  dlg.clearTree()
			self.Reset(1)
			self.xmlLoad(tree, workSpace, "ws")
		else:
			dlg.Close()

	def OnMnuFileSaveexpMenu(self, event):
		dlg = wx.FileDialog(self, "Choose a file", ".", "", "XML files (*.xml)|*.xml", wx.FD_SAVE)
		##		  try:
		if dlg.ShowModal() == wx.ID_OK:
			saveFile = dlg.GetPath()
			self.xmlSave(saveFile, "Default", "new")
			# activate workspace save menu option
			self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILESAVEEXP, 1)
			self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILESAVEWS, 1)
			self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILELOADWS, 1)
			# show workspace dialog so that default can be edited
			dlg = wxSaveWorkspaceDialog(self, saveFile, dtype="Save")
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()

	##		  except Exception, error:
	##			  dlg.Destroy()
	##			  errorBox(self, '%s' %str(error))

	def OnMnuFileSavewsMenu(self, event):
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
			dlg = wxSaveWorkspaceDialog(self, self.data["exppath"], dtype="Save")
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
			if dlg.GetButtonPress() == 1:
				# Apply default settings
				self.Reset()

				# Load arrays
				wx.BeginBusyCursor()
				# import array
				if dlg.Transpose() == 0:
					self.data["raw"] = load(dlg.GetRawData(), dlg.GetDelim())
				else:
					self.data["raw"] = scipy.transpose(load(dlg.GetRawData(), dlg.GetDelim()))

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
				self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILESAVEEXP, 1)
				self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILESAVEWS, 0)
				self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILELOADWS, 0)

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

	def Reset(self, case=0):
		varList = "'proc':None,'class':None,'label':None," + "'split':None,'processlist':[],'xaxis':None," + "'class':None,'label':None,'mask':None," + "'pcscores':None,'pcloads':None,'pcpervar':None," + "'pceigs':None,'pcadata':None,'niporsvd':None," + "'indlabels':None,'plsloads':None,'pcatype':None," + "'dfscores':None,'dfloads':None,'dfeigs':None," + "'sampleidx':None,'variableidx':None," + "'rawtrunc':None,'proctrunc':None," + "'gadfachroms':None,'gadfascores':None," + "'gadfacurves':None,'gaplschroms':None," + "'gaplsscores':None,'gaplscurves':None," + "'gadfadfscores':None,'gadfadfloads':None," + "'gaplsplsloads':None"

		if case == 0:
			exec('self.data = {"raw":None,"exppath":None,' + varList + "}")
		else:
			exec('self.data = {"raw":self.data["raw"],"exppath":self.data["exppath"],' + varList + "}")

		# for returning application to default settings
		self.plExpset.Reset()
		self.plPca.Reset()
		self.plDfa.Reset()
		self.plCluster.Reset()
		self.plPls.Reset()
		self.plGadfa.Reset()
		self.plGapls.Reset()

		# associate algorithm classes with data
		self.plExpset.depTitleBar.getData(self.data)
		self.plExpset.indTitleBar.getData(self.data)
		self.plPreproc.titleBar.getData(self.data)
		self.plPca.titleBar.getData(self.data)
		self.plCluster.titleBar.getData(self.data)
		self.plDfa.titleBar.getData(self.data)
		self.plPls.titleBar.getData(self.data)
		self.plGadfa.titleBar.getData(self.data)
		self.plGapls.titleBar.getData(self.data)

		self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILESAVEEXP, 0)
		self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILESAVEWS, 0)
		self.mnuFile.Enable(wxID_PYCHEMMAINMNUFILELOADWS, 0)

	def xmlSave(self, path, workspace, type=None):
		# type is either "new" (in which case workspace = "Default")
		# or path to saved xml file

		proceed = 1
		if type is "new":
			# build a tree structure
			root = ET.Element("pychem_experiment")
			# save raw data
			rawdata = ET.SubElement(root, "rawdata")
			rawdata.set("key", "array")
			data = str(self.data["raw"]).replace("[[ ", "")
			data = data.replace("	\n		  ", "	 ")
			data = data.replace("\n		   ", "	  ")
			data = data.replace("]\n [ ", "\n")
			data = data.replace("]]", "")
			data = data.replace("  ", "	  ")

			rawdata.text = data

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
				dlg = wx.MessageDialog(self, 'Unable to save under current name.\n\nCharacters such as "%", "&", "-", "+" can not be used for the workspace name', "Error!", wx.OK | wx.ICON_ERROR)
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

			# save spin, string and boolean ctrl values
			Controls = ET.SubElement(locals()[workspace], "Controls")

			# spin controls
			spinCtrls = ["plGadfa.TitleBar.dlg.spnGaMaxFac", "plGadfa.TitleBar.dlg.spnGaMaxGen", "plGadfa.TitleBar.dlg.spnGaVarsFrom", "plGadfa.TitleBar.dlg.spnGaVarsTo", "plGadfa.TitleBar.dlg.spnGaNoInds", "plGadfa.TitleBar.dlg.spnGaNoRuns", "plGadfa.TitleBar.dlg.spnGaRepUntil"]

			for each in spinCtrls:
				name = each.split(".")[len(each.split(".")) - 1]
				locals()[name] = ET.SubElement(Controls, each)
				locals()[name].set("key", "int")
				locals()[name].text = getByPath(self, each).GetValue()

			# string controls
			stringCtrls = ["plExpset.indTitleBar.stcRangeFrom", "plExpset.indTitleBar.stcRangeTo", "plGadfa.TitleBar.dlg.stGaXoverRate", "plGadfa.TitleBar.dlg.stGaMutRate", "plGadfa.TitleBar.dlg.stGaInsRate"]

			##			  , 'stPls2',
			##			  'stPls12', 'stPls1','stPls9', 'stPls4', 'stPls5', 'stPls6', 'stPlsFac',
			##			  'stPls7', 'stPls8', 'stPls13', 'stPlscVarFrom', 'stPlscVarTo', 'stPlscNoInds',
			##			  'stPlscNoRuns', 'stPlscXoverRate', 'stPlscMutRate', 'stPlscInsRate',
			##			  'stPlscMaxFac', 'stPlscMaxGen', 'stPlscRepUntil', 'stPlscSavePer']

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

			boolCtrls = ["plCluster.titleBar.dlg.rbKmeans", "plCluster.titleBar.dlg.rbKmedian", "plCluster.titleBar.dlg.rbKmedoids", "plCluster.titleBar.dlg.rbHcluster", "plCluster.titleBar.dlg.rbSingleLink", "plCluster.titleBar.dlg.rbMaxLink", "plCluster.titleBar.dlg.rbAvLink", "plCluster.titleBar.dlg.rbCentLink", "plCluster.titleBar.dlg.rbEuclidean", "plCluster.titleBar.dlg.rbCorrelation", "plCluster.titleBar.dlg.rbAbsCorr", "plCluster.titleBar.dlg.rbUncentredCorr", "plCluster.titleBar.dlg.rbAbsUncentCorr", "plCluster.titleBar.dlg.rbSpearmans", "plCluster.titleBar.dlg.rbKendalls", "plCluster.titleBar.dlg.rbHarmonicEuc", "plCluster.titleBar.dlg.rbCityBlock", "plCluster.titleBar.dlg.cbUseClass", "plCluster.titleBar.dlg.rbPlotName", "plCluster.titleBar.dlg.rbPlotColours", "plGadfa.TitleBar.dlg.cbGaRepUntil", "plGadfa.TitleBar.dlg.cbGaMaxGen", "plGadfa.TitleBar.dlg.cbGaMut", "plGadfa.TitleBar.dlg.cbGaXover"]

			##			  'cbPls1', 'cbPls2', 'cbPls3', 'cbPls4', 'cbPls5',
			##			  'cbDfaXover', 'cbDfaMut', 'cbDfaMaxGen', 'cbDfaRepUntil', 'cbDfaSavePc',
			##			  'cbPlscXover', 'cbPlscMut', 'cbPlscMaxGen', 'cbPlscRepUntil', 'cbPlscSavePer',

			for each in boolCtrls:
				name = each.split(".")[len(each.split(".")) - 1]
				locals()[name] = ET.SubElement(Controls, each)
				locals()[name].set("key", "bool")
				locals()[name].text = str(getByPath(self, each).GetValue())
			##
			##			  #any integer ctrl values
			##			  intCtrls = ['tcPCAnum', 'spnPLSmaxfac', 'spnDFApcs', 'spnDFAdfs',
			##			  'spnNoPass']
			##			  for each in intCtrls:
			##				  locals()[each] = ET.SubElement(Controls, each)
			##				  locals()[each].set("key", "int")
			##				  exec(each + '.text = str(self.' + each + '.GetValue())')
			##
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
			##
			##			  #any scipy arrays
			##			  scipyArrays = ['DplsCurves', 'DplsPairList', 'DplsChromList',
			##			  'PlscCurves', 'PlscChromList', 'DfaCurves', 'DfaChromList', 'PCscores',
			##			  'PCloadings', 'PCPerVar', 'PCeigs', 'DFscores', 'DFloads', 'DFeigs']
			##			  exec('Array = ET.SubElement(' + workspace + ', "Array")')
			##			  for each in scipyArrays:
			##				  try:
			##				  #save array elements
			##					  exec('Rows = range(self.' + each + '.shape[0])')
			##					  locals()[each] = ET.SubElement(Array, each)
			##					  for i in Rows:
			##						  exec('row = ET.SubElement(' + each + ', "row")')
			##						  exec('Cols = range(self.' + each + '.shape[1])')
			##						  for j in Cols:
			##							  col = ET.SubElement(row, "col")
			##							  col.set("key", "float")
			##							  exec('col.text = str(self.' + each + '[i][j])')
			##				  except: continue
			##
			##			  #any global variables
			##			  gloVars = []
			##			  exec('Variables = ET.SubElement(' + workspace + ', "Variables")')
			##			  for each in gloVars:
			##				  locals()[each] = ET.SubElement(Variables, each)
			##				  locals()[each].set("key", "int")
			##				  exec(each + '.text = str(self.' + each + ')')
			##
			##			  #create run clustering flag global variable
			##			  doClustering = ET.SubElement(Variables, "doClustering")
			##			  doClustering.set("key", "int")
			##			  if (self.linkdist is not None) or (self.clusterid is not None) is True:
			##				  doClustering.text = '1'
			##			  else:
			##				  doClustering.text = '0'
			##
			##			  #create run plsr flag global variable
			##			  doPlsr = ET.SubElement(Variables, "doPlsr")
			##			  doPlsr.set("key", "int")
			##			  if self.Wloads is not None:
			##				  doPlsr.text = '1'
			##			  else:
			##				  doPlsr.text = '0'
			##
			# wrap it in an ElementTree instance, and save as XML
			tree = ET.ElementTree(root)
			tree.write(path)

	def xmlLoad(self, tree, workspace, type="new"):
		# load pychem experiments from saved xml files

		if type == "new":
			# load raw data
			rdArray = []
			getRows = tree.findtext("rawdata")

			rows = getRows.split("\n")

			for each in rows:
				newRow = []
				items = each.split("   ")
				for item in items:
					if item not in ["", " "]:
						newRow.append(float(item))
				rdArray.append(newRow)

			self.data["raw"] = np.array(rdArray)

		# load workspace
		##		  getWsElements = tree.getroot().findall("".join((".//Workspaces/",workspace)))[0]
		getWsElements = tree.getroot().findall("".join(("*/", workspace)))[0]

		for each in getWsElements:
			# apply preprocessing steps
			if each.tag == "ppOptions":
				getOpts = each
				for item in getOpts:
					self.plPreproc.selFun.lbSpectra1.SetSelection(int(item.text) - 1)
					Selected = self.plPreproc.selFun.lbSpectra1.GetSelection()
					SelectedText = self.plPreproc.selFun.lbSpectra1.GetStringSelection()
					if SelectedText[0:2] == "  ":
						self.data["ProcessList"].append(int(item.text))
						self.plPreproc.selFun.lbSpectra2.Append(SelectedText[2 : len(SelectedText)])
				self.RunProcessingSteps()

			##			  #load ctrl values
			##			  if each.tag == 'Controls':
			##				  getVars = each
			##				  for item in getVars:
			##					  exec('self.' + item.tag + '.SetValue(' + item.items()[0][1] + '(' + item.text + '))')

			# load grids
			if each.tag == "Grid":
				grids = each
				for item in grids:
					gName = item.tag
					members = item
					for ind in members:
						if ind.tag == "columnLabels":
							cols = ind
							expSetup.ResizeGrids(getByPath(self, gName), 10, len(cols))
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
		##
		##			  #load arrays
		##			  if each.tag == 'Array':
		##				  getArrays = each
		##				  for array in getArrays:
		##					  newArray = array.tag
		##					  makeArray = []
		##					  for Row in array:
		##						  cols = Row
		##						  getCols = []
		##						  for Col in cols:
		##							  getCols.append(float(Col.text))
		##						  makeArray.append(getCols)
		##					  exec('self.' + newArray + ' = np.array(makeArray)')
		##					  #reload any plots
		##					  for i in ['PC','DF','Dfa','Dpls','Plsc']:
		##						  if len(newArray.split(i)) > 1:
		##							  if i == 'PC':
		##								  try:
		##									  self.PlotPca()
		##								  except: continue
		##							  elif i == 'DF':
		##								  try:
		##									  self.PlotDfa()
		##								  except: continue
		##							  else:
		##								  try:
		##									  exec('self.CreateGa' + i + 'ResultsTrees()')
		##								  except: continue
		##
		##			  #load global variables - currently just flags for re-running cluster
		##			  #analysis and plsr
		##			  if each.tag == 'Variables':
		##				  getVars = each
		##				  for item in getVars:
		##					  if (item.tag == 'doClustering') & (item.text == '1') is True:
		##						  self.RunClustering()
		##					  elif (item.tag == 'doPlsr') & (item.text == '1') is True:
		##						  self.RunFullPls()

		# unlock ctrls
		self.EnableCtrls()

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
		##		  try:
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
		for j in range(1, self.plExpset.grdIndLabels.GetNumberCols()):
			xaxis = []
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

		##		  except Exception, error:
		####			pass
		##			  errorBox(self, '%s' %str(error))

		# change ga results lists
		try:
			self.CreateGaDplsResultsTrees()
		except:
			pass
		try:
			self.CreateGaDfaResultsTrees()
		except:
			pass
		try:
			self.CreateGaPlscResultsTrees()
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
	def _init_import_ctrls(self, prnt):
		# generated method, don't edit
		wx.Dialog.__init__(self, id=wxID_WXIMPORTDIALOG, name="wx.ImportDialog", parent=prnt, pos=wx.Point(496, 269), size=wx.Size(287, 232), style=wx.DEFAULT_DIALOG_STYLE, title="Import X-data File")
		self.SetClientSize(wx.Size(279, 198))
		self.SetToolTip("")
		self.Center(wx.BOTH)

		self.swLoadX = wx.adv.SashWindow(id=wxID_WXIMPORTDIALOGSWLOADX, name="swLoadX", parent=self, pos=wx.Point(0, 0), size=wx.Size(279, 198), style=wx.CLIP_CHILDREN | wx.adv.SW_3D)
		self.swLoadX.SetToolTip("")

		self.btnBrowseArray = wx.Button(id=wxID_WXIMPORTDIALOGBTNBROWSEARRAY, label="Browse...", name="btnBrowseArray", parent=self.swLoadX, pos=wx.Point(192, 24), size=wx.Size(75, 23), style=0)
		self.btnBrowseArray.Bind(wx.EVT_BUTTON, self.OnBtnbrowsearrayButton, id=wxID_WXIMPORTDIALOGBTNBROWSEARRAY)

		self.stArray = wx.lib.bcrtl.user.StaticTextCtrl.StaticTextCtrl(caption="", id=wxID_WXIMPORTDIALOGSTARRAY, name="stArray", parent=self.swLoadX, pos=wx.Point(16, 24), size=wx.Size(160, 23), style=0, value="")

		self.btnOK = wx.Button(id=wxID_WXIMPORTDIALOGBTNOK, label="OK", name="btnOK", parent=self.swLoadX, pos=wx.Point(16, 160), size=wx.Size(104, 23), style=0)
		self.btnOK.Bind(wx.EVT_BUTTON, self.OnBtnOKButton, id=wxID_WXIMPORTDIALOGBTNOK)

		self.btnCancel = wx.Button(id=wxID_WXIMPORTDIALOGBTNCANCEL, label="Cancel", name="btnCancel", parent=self.swLoadX, pos=wx.Point(160, 160), size=wx.Size(107, 23), style=0)
		self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancelButton, id=wxID_WXIMPORTDIALOGBTNCANCEL)

		self.cbTabDelim = wx.CheckBox(id=wxID_WXIMPORTDIALOGCBTABDELIM, label="Tab delimited", name="cbTabDelim", parent=self.swLoadX, pos=wx.Point(16, 64), size=wx.Size(96, 23), style=0)
		self.cbTabDelim.SetValue(True)
		self.cbTabDelim.SetToolTip("")
		self.cbTabDelim.Bind(wx.EVT_CHECKBOX, self.OnCbTabDelimCheckbox, id=wxID_WXIMPORTDIALOGCBTABDELIM)

		self.cbSpaceDelim = wx.CheckBox(id=wxID_WXIMPORTDIALOGCBSPACEDELIM, label="Space delimited", name="cbSpaceDelim", parent=self.swLoadX, pos=wx.Point(160, 64), size=wx.Size(96, 23), style=0)
		self.cbSpaceDelim.SetValue(False)
		self.cbSpaceDelim.SetToolTip("")
		self.cbSpaceDelim.Bind(wx.EVT_CHECKBOX, self.OnCbSpaceDelimCheckbox, id=wxID_WXIMPORTDIALOGCBSPACEDELIM)

		self.cbCommaDelim = wx.CheckBox(id=wxID_WXIMPORTDIALOGCBCOMMADELIM, label="Comma delimited", name="cbCommaDelim", parent=self.swLoadX, pos=wx.Point(160, 96), size=wx.Size(104, 23), style=0)
		self.cbCommaDelim.SetValue(False)
		self.cbCommaDelim.SetToolTip("")
		self.cbCommaDelim.Bind(wx.EVT_CHECKBOX, self.OnCbCommaDelimCheckbox, id=wxID_WXIMPORTDIALOGCBCOMMADELIM)

		self.cbOther = wx.CheckBox(id=wxID_WXIMPORTDIALOGCBOTHER, label="Other", name="cbOther", parent=self.swLoadX, pos=wx.Point(16, 128), size=wx.Size(56, 23), style=0)
		self.cbOther.SetValue(False)
		self.cbOther.SetToolTip("")
		self.cbOther.Bind(wx.EVT_CHECKBOX, self.OnCbOtherCheckbox, id=wxID_WXIMPORTDIALOGCBOTHER)

		self.cbSemiDelim = wx.CheckBox(id=wxID_WXIMPORTDIALOGCBSEMIDELIM, label="Semicolon delimited", name="cbSemiDelim", parent=self.swLoadX, pos=wx.Point(16, 96), size=wx.Size(112, 23), style=0)
		self.cbSemiDelim.SetValue(False)
		self.cbSemiDelim.SetToolTip("")
		self.cbSemiDelim.Bind(wx.EVT_CHECKBOX, self.OnCbSemiDelimCheckbox, id=wxID_WXIMPORTDIALOGCBSEMIDELIM)

		self.txtOther = wx.TextCtrl(id=wxID_WXIMPORTDIALOGTXTOTHER, name="txtOther", parent=self.swLoadX, pos=wx.Point(72, 126), size=wx.Size(40, 23), style=0, value="")
		self.txtOther.SetToolTip("")

		self.cbTranspose = wx.CheckBox(id=wxID_WXIMPORTDIALOGCBTRANSPOSE, label="Transpose", name="cbTranspose", parent=self.swLoadX, pos=wx.Point(160, 128), size=wx.Size(73, 23), style=0)
		self.cbTranspose.SetValue(False)
		self.cbTranspose.SetToolTip("")
		self.cbTranspose.Bind(wx.EVT_CHECKBOX, self.OnCbTransposeCheckbox, id=wxID_WXIMPORTDIALOGCBTRANSPOSE)

	def __init__(self, parent):
		self._init_import_ctrls(parent)
		self.UpdateFlag = 0
		self.ClassFile, self.ArrayFile = "", ""

	def OnBtnbrowsearrayButton(self, event):
		self.ArrayFile = wx.FileSelector("Choose X-Data File")
		self.stArray.SetValue(self.ArrayFile)
		return self.ArrayFile

	def OnBtnOKButton(self, event):
		if "" in [self.ArrayFile]:
			dlg = wx.MessageDialog(self, "Please enter all of the fields", "Error!", wx.OK | wx.ICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
		else:
			self.ButtonPress = 1
			self.Close()

	def OnBtnCancelButton(self, event):
		self.ButtonPress = 0
		self.Close()

	def GetRawData(self):
		return self.ArrayFile

	def GetButtonPress(self):
		return self.ButtonPress

	def GetDelim(self):
		# set delimiter
		if self.cbTabDelim.GetValue() == 1:
			return "\t"
		elif self.cbSpaceDelim.GetValue() == 1:
			return " "
		elif self.cbCommaDelim.GetValue() == 1:
			return ","
		elif self.cbSemiDelim.GetValue() == 1:
			return ";"
		elif self.cbOther.GetValue() == 1:
			return self.txtOther.GetValue()

	def Transpose(self):
		# flag to indicate whether to transpose the array
		if self.cbTranspose.GetValue() == 1:
			return 1
		else:
			return 0

	def OnCbTabDelimCheckbox(self, event):
		self.cbSpaceDelim.SetValue(0)
		self.cbCommaDelim.SetValue(0)
		self.cbSemiDelim.SetValue(0)
		self.cbOther.SetValue(0)

	def OnCbSpaceDelimCheckbox(self, event):
		self.cbTabDelim.SetValue(0)
		self.cbCommaDelim.SetValue(0)
		self.cbSemiDelim.SetValue(0)
		self.cbOther.SetValue(0)

	def OnCbCommaDelimCheckbox(self, event):
		self.cbTabDelim.SetValue(0)
		self.cbSpaceDelim.SetValue(0)
		self.cbSemiDelim.SetValue(0)
		self.cbOther.SetValue(0)

	def OnCbOtherCheckbox(self, event):
		self.cbTabDelim.SetValue(0)
		self.cbSpaceDelim.SetValue(0)
		self.cbCommaDelim.SetValue(0)
		self.cbSemiDelim.SetValue(0)

	def OnCbSemiDelimCheckbox(self, event):
		self.cbTabDelim.SetValue(0)
		self.cbSpaceDelim.SetValue(0)
		self.cbCommaDelim.SetValue(0)
		self.cbOther.SetValue(0)

	def OnCbTransposeCheckbox(self, event):
		event.Skip()


class wxSaveWorkspaceDialog(wx.Dialog):
	def _init_coll_lbSaveWorkspace_Columns(self, parent):
		# generated method, don't edit

		parent.InsertColumn(col=0, format=wx.LIST_FORMAT_LEFT, heading="Workspaces", width=260)

	def _init_savews_ctrls(self, prnt):
		# generated method, don't edit
		wx.Dialog.__init__(self, id=wxID_WXSAVEWORKSPACEDIALOG, name="wxSaveWorkspaceDialog", parent=prnt, pos=wx.Point(453, 245), size=wx.Size(374, 280), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.CAPTION | wx.MAXIMIZE_BOX, title="Save Workspace")
		self.SetClientSize(wx.Size(366, 246))
		self.SetToolTip("")
		self.SetBackgroundColour(wx.Colour(167, 167, 243))
		self.SetAutoLayout(True)
		self.Center(wx.BOTH)

		self.btnDelete = wx.Button(id=wxID_WXSAVEWORKSPACEDIALOGBTNDELETE, label="Delete", name="btnDelete", parent=self, pos=wx.Point(16, 7), size=wx.Size(70, 23), style=0)
		self.btnDelete.SetToolTip("")
		self.btnDelete.SetAutoLayout(True)
		self.btnDelete.Bind(wx.EVT_BUTTON, self.OnBtnDeleteButton, id=wxID_WXSAVEWORKSPACEDIALOGBTNDELETE)

		self.btnCancel = wx.Button(id=wxID_WXSAVEWORKSPACEDIALOGBTNCANCEL, label="Cancel", name="btnCancel", parent=self, pos=wx.Point(16, 40), size=wx.Size(72, 23), style=0)
		self.btnCancel.SetToolTip("")
		self.btnCancel.SetAutoLayout(True)
		self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancelButton, id=wxID_WXSAVEWORKSPACEDIALOGBTNCANCEL)

		self.btnEdit = wx.Button(id=wxID_WXSAVEWORKSPACEDIALOGBTNEDIT, label="Edit", name="btnEdit", parent=self, pos=wx.Point(16, 152), size=wx.Size(70, 23), style=0)
		self.btnEdit.SetToolTip("")
		self.btnEdit.SetAutoLayout(True)
		self.btnEdit.Show(False)
		self.btnEdit.Bind(wx.EVT_BUTTON, self.OnBtnEditButton, id=wxID_WXSAVEWORKSPACEDIALOGBTNEDIT)

		self.btnOK = wx.Button(id=wxID_WXSAVEWORKSPACEDIALOGBTNOK, label="OK", name="btnOK", parent=self, pos=wx.Point(16, 71), size=wx.Size(72, 23), style=0)
		self.btnOK.SetToolTip("")
		self.btnOK.SetAutoLayout(True)
		self.btnOK.Show(True)
		self.btnOK.Bind(wx.EVT_BUTTON, self.OnBtnOKButton, id=wxID_WXSAVEWORKSPACEDIALOGBTNOK)

		self.lbSaveWorkspace = wx.ListCtrl(id=wxID_WXSAVEWORKSPACEDIALOGLBSAVEWORKSPACE, name="lbSaveWorkspace", parent=self, pos=wx.Point(96, 8), size=wx.Size(264, 232), style=wx.LC_REPORT | wx.LC_SORT_ASCENDING | wx.LC_SINGLE_SEL)
		self.lbSaveWorkspace.SetConstraints(LayoutAnchors(self.lbSaveWorkspace, True, True, True, True))
		self.lbSaveWorkspace.SetAutoLayout(True)
		self.lbSaveWorkspace.SetToolTip("")
		self._init_coll_lbSaveWorkspace_Columns(self.lbSaveWorkspace)
		self.lbSaveWorkspace.Bind(wx.EVT_LEFT_DCLICK, self.OnLbSaveWorkspaceLeftDclick)
		self.lbSaveWorkspace.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnLbSaveWorkspaceListEndLabelEdit, id=wxID_WXSAVEWORKSPACEDIALOGLBSAVEWORKSPACE)
		self.lbSaveWorkspace.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnLbSaveWorkspaceListItemSelected, id=wxID_WXSAVEWORKSPACEDIALOGLBSAVEWORKSPACE)

	def __init__(self, parent, filename, dtype="Load"):
		# type to be either "load" or "save"
		self._init_savews_ctrls(parent)

		# set some defaults
		self.SetTitle(dtype + " Workspace")
		self.dtype = dtype
		self.filename = filename

		# need to populate listbox
		try:
			# check that it's a pychem file
			tree = ET.ElementTree(file=self.filename)
			self.tree = tree
			workspaces = tree.getroot().findall("Workspaces")[0]
			self.lbSaveWorkspace.SetColumnWidth(0, 260)
			for each in workspaces:
				index = self.lbSaveWorkspace.InsertItem(sys.maxsize, each.tag)
				self.lbSaveWorkspace.SetItem(index, 0, each.tag.replace("_", " "))

			# behaviour for save dialog
			if dtype == "Save":
				self.btnCancel.Enable(0)

		except Exception as error:
			if self.filename not in [""]:
				dlg = wx.MessageDialog(self, "Unable to load data - this is not a PyChem Experiment file", "Error!", wx.OK | wx.ICON_ERROR)
				try:
					dlg.ShowModal()
				finally:
					dlg.Destroy()
			##				  self.Destroy()
			else:
				pass
			self.Destroy()

	##			  raise

	def OnBtnDeleteButton(self, event):
		if self.lbSaveWorkspace.GetItemCount() > 1:
			# need to delete the workspace in the xml file
			WSnode = tree.getroot().findall("Workspaces")[0]
			workspaces = WSnode
			for each in workspaces:
				if each.tag == self.lbSaveWorkspace.GetItemText(self.currentItem).replace(" ", "_"):
					WSnode.remove(each)
			tree.write(self.filename)

			# delete listbox entry
			self.lbSaveWorkspace.DeleteItem(self.currentItem)

	def OnBtnCancelButton(self, event):
		self.clearTree()
		self.Close()

	def OnBtnEditButton(self, event):
		event.Skip()

	def getWorkspace(self):
		if self.workSpace != 0:
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
				self.clearTree()
				self.Close()
			except:
				dlg = wx.MessageDialog(self, "Please select a Workspace to load", "Error!", wx.OK | wx.ICON_ERROR)
				try:
					dlg.ShowModal()
				finally:
					dlg.Destroy()
		else:
			self.clearTree()
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

	def clearTree(self):
		del self.tree
