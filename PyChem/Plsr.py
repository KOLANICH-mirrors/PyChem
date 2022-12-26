# -----------------------------------------------------------------------------
# Name:		   Plsr.py
# Purpose:
#
# Author:	   Roger Jarvis
#
# Created:	   2007/05/22
# RCS-ID:	   $Id$
# Copyright:   (c) 2006
# Licence:	   GNU General Public Licence
# -----------------------------------------------------------------------------
# Boa:FramePanel:Plsr

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
from .mva.chemometrics import _BW, _index, _put
from .Pca import MyPlotCanvas, PlotPlsModel, SetButtonState, plotLine, plotLoads, plotScores, plotStem, plotText
from .utils.io import str_array

[
	wxID_PLSR,
	wxID_PLSRBTNEXPPLS,
	wxID_PLSRBTNGOTOGADPLS,
	wxID_PLSRBTNGOTOGAPLS,
	wxID_PLSRBTNRUNFULLPLS,
	wxID_PLSRNBFULLPLS,
	wxID_PLSRPLCPLSERROR,
	wxID_PLSRPLCPLSHETERO,
	wxID_PLSRPLCPLSLOADING,
	wxID_PLSRPLCPLSMODEL,
	wxID_PLSRPLPLSLOADS,
	wxID_PLSRRBPLSUSEPROC,
	wxID_PLSRRBPLSUSERAW,
	wxID_PLSRSASHWINDOW8,
	wxID_PLSRSPNPLSFACTOR,
	wxID_PLSRSPNPLSMAXFAC,
	wxID_PLSRSTATICTEXT10,
	wxID_PLSRSTATICTEXT14,
	wxID_PLSRSTATICTEXT15,
	wxID_PLSRSTUSE,
	wxID_PLSRTXTPLSSTATS,
] = [wx.NewIdRef() for _init_ctrls in range(21)]


def errorBox(window, error):
	dlg = wx.MessageDialog(window, "".join(("The following error occured:\n\n", error)), "Error!", wx.OK | wx.ICON_ERROR)
	try:
		dlg.ShowModal()
	finally:
		dlg.Destroy()


class Plsr(wx.Panel):
	# partial least squares regression

	def _init_coll_bxsPls2_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.titleBar, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.grsPls1, 1, border=0, flag=wx.EXPAND)

	def _init_coll_bxsPls1_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.bxsPls2, 1, border=0, flag=wx.EXPAND)

	def _init_coll_grsPls1_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.nbPlsPreds, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.plcPLSloading, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.nbFullPls, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.plcPlsHetero, 0, border=0, flag=wx.EXPAND)

	def _init_coll_nbFullPls_Pages(self, parent):
		# generated method, don't edit

		parent.AddPage(imageId=-1, page=self.plcPLSerror, select=True, text="PLS Error")
		parent.AddPage(imageId=-1, page=self.plcPlsStats, select=False, text="OLS Results ")

	def _init_coll_nbPlsPreds_Pages(self, parent):
		# generated method, don't edit

		parent.AddPage(imageId=-1, page=self.plcPredPls1, select=True, text="")

	def _init_sizers(self):
		# generated method, don't edit
		self.grsPls1 = wx.GridSizer(cols=2, hgap=2, rows=2, vgap=2)

		self.bxsPls1 = wx.BoxSizer(orient=wx.HORIZONTAL)

		self.bxsPls2 = wx.BoxSizer(orient=wx.VERTICAL)

		self._init_coll_grsPls1_Items(self.grsPls1)
		self._init_coll_bxsPls1_Items(self.bxsPls1)
		self._init_coll_bxsPls2_Items(self.bxsPls2)

		self.SetSizer(self.bxsPls1)

	def _init_ctrls(self, prnt):
		# generated method, don't edit
		wx.Panel.__init__(self, id=wxID_PLSR, name="Plsr", parent=prnt, pos=wx.Point(84, 70), size=wx.Size(796, 460), style=wx.TAB_TRAVERSAL)
		self.SetClientSize(wx.Size(788, 426))
		self.SetAutoLayout(True)
		self.SetToolTip("")
		self.prnt = prnt

		self.nbFullPls = wx.Notebook(id=-1, name="nbFullPls", parent=self, pos=wx.Point(176, 274), size=wx.Size(310, 272), style=wx.NB_BOTTOM)
		self.nbFullPls.SetToolTip("")
		self.nbFullPls.SetAutoLayout(True)
		self.nbFullPls.SetConstraints(LayoutAnchors(self.nbFullPls, True, True, True, True))
		self.nbFullPls.SetTabSize((40, 15))

		self.nbPlsPreds = wx.Notebook(id=-1, name="nbPlsPreds", parent=self, pos=wx.Point(176, 274), size=wx.Size(310, 272), style=wx.NB_BOTTOM)
		self.nbPlsPreds.SetToolTip("")
		self.nbPlsPreds.SetAutoLayout(True)
		self.nbPlsPreds.SetConstraints(LayoutAnchors(self.nbPlsPreds, True, True, True, True))
		self.nbPlsPreds.SetTabSize((0, 1))
		self.nbPlsPreds.prnt = self

		self.plcPLSerror = MyPlotCanvas(id=-1, name="plcPLSerror", parent=self.nbFullPls, pos=wx.Point(0, 0), size=wx.Size(302, 246), style=0, toolbar=self.prnt.parent.tbMain)
		self.plcPLSerror.fontSizeAxis = 8
		self.plcPLSerror.fontSizeTitle = 10
		self.plcPLSerror.enableZoom = True
		self.plcPLSerror.SetToolTip("")
		self.plcPLSerror.enableLegend = True
		self.plcPLSerror.fontSizeLegend = 8
		self.plcPLSerror.SetAutoLayout(True)
		self.plcPLSerror.SetConstraints(LayoutAnchors(self.plcPLSerror, True, True, True, True))
		self.plcPLSerror.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))

		self.plcPlsStats = MyPlotCanvas(id=-1, name="plcPlsStats", parent=self.nbFullPls, pos=wx.Point(176, 0), size=wx.Size(310, 272), style=0, toolbar=self.prnt.parent.tbMain)
		self.plcPlsStats.xSpec = "none"
		self.plcPlsStats.ySpec = "none"
		self.plcPlsStats.SetAutoLayout(True)
		self.plcPlsStats.enableZoom = True
		self.plcPlsStats.SetConstraints(LayoutAnchors(self.plcPlsStats, True, True, True, True))
		self.plcPlsStats.SetFont(wx.Font(6, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Courier New"))
		self.plcPlsStats.SetToolTip("")

		self.plcPredPls1 = MyPlotCanvas(id=-1, name="plcPredPls1", parent=self.nbPlsPreds, pos=wx.Point(176, 0), size=wx.Size(310, 272), style=0, toolbar=self.prnt.parent.tbMain)
		self.plcPredPls1.fontSizeTitle = 10
		self.plcPredPls1.fontSizeAxis = 8
		self.plcPredPls1.enableZoom = True
		self.plcPredPls1.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "MS Sans Serif"))
		self.plcPredPls1.SetToolTip("")
		self.plcPredPls1.enableLegend = True
		self.plcPredPls1.fontSizeLegend = 8
		self.plcPredPls1.SetAutoLayout(True)
		self.plcPredPls1.SetConstraints(LayoutAnchors(self.plcPredPls1, True, True, True, True))

		self.plcPlsHetero = MyPlotCanvas(id=-1, name="plcPlsHetero", parent=self, pos=wx.Point(488, 274), size=wx.Size(310, 272), style=0, toolbar=self.prnt.parent.tbMain)
		self.plcPlsHetero.fontSizeAxis = 8
		self.plcPlsHetero.fontSizeTitle = 10
		self.plcPlsHetero.enableZoom = True
		self.plcPlsHetero.SetToolTip("")
		self.plcPlsHetero.enableLegend = True
		self.plcPlsHetero.fontSizeLegend = 8
		self.plcPlsHetero.SetAutoLayout(True)
		self.plcPlsHetero.SetConstraints(LayoutAnchors(self.plcPlsHetero, True, True, True, True))
		self.plcPlsHetero.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Microsoft Sans Serif"))

		self.plcPLSloading = MyPlotCanvas(id=-1, name="plcPLSloading", parent=self, pos=wx.Point(0, 24), size=wx.Size(330, 292), style=0, toolbar=self.prnt.parent.tbMain)
		self.plcPLSloading.fontSizeTitle = 10
		self.plcPLSloading.fontSizeAxis = 8
		self.plcPLSloading.enableZoom = True
		self.plcPLSloading.enableLegend = True
		self.plcPLSloading.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "MS Sans Serif"))
		self.plcPLSloading.SetToolTip("")
		self.plcPLSloading.fontSizeLegend = 8
		self.plcPLSloading.SetAutoLayout(True)
		self.plcPLSloading.SetConstraints(LayoutAnchors(self.plcPLSloading, True, True, True, True))

		self.titleBar = TitleBar(self, id=-1, text="Partial Least Squares Regression", style=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self._init_coll_nbFullPls_Pages(self.nbFullPls)
		self._init_coll_nbPlsPreds_Pages(self.nbPlsPreds)

		self._init_sizers()

	def __init__(self, parent, id, pos, size, style, name):
		self._init_ctrls(parent)

	def Reset(self):
		self.titleBar.spnPLSfactor1.Enable(0)
		self.titleBar.spnPLSfactor2.Enable(0)
		self.titleBar.spnPLSfactor1.SetValue(1)
		self.titleBar.spnPLSfactor2.SetValue(2)

		# delete multiple scores plots
		self.plcPredPls1.prnt.SetSelection(0)
		self.plcPredPls1.prnt.SetPageText(0, "")
		self.plcPredPls1.prnt.SetTabSize((0, 1))
		for page in range(self.plcPredPls1.prnt.GetPageCount() - 1, 0, -1):
			self.plcPredPls1.prnt.DeletePage(page)

		objects = {"plcPLSerror": ["RMS Error", "Latent Variable", "RMS Error"], "plcPredPls1": ["PLS Predictions", "Actual", "Predicted"], "plcPlsHetero": ["Residuals vs. Predicted Values", "Predicted", "Residuals"], "plcPLSloading": ["PLS Loading", "w*c[1]", "w*c[2]"]}
		curve = wx.lib.plot.PolyLine([[0, 0], [1, 1]], colour="white", width=1, style=wx.TRANSPARENT)

		for each in list(objects.keys()):
			exec("self." + each + ".Draw(wx.lib.plot.PlotGraphics([curve]," + 'objects["' + each + '"][0],' + 'objects["' + each + '"][1],' + 'objects["' + each + '"][2]))')


class TitleBar(bp.ButtonPanel):
	def _init_btnpanel_ctrls(self, prnt):
		bp.ButtonPanel.__init__(self, parent=prnt, id=-1, text="Partial Least Squares Regression", agwStyle=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self.cbxData = wx.Choice(choices=["Raw spectra", "Processed spectra"], id=-1, name="cbxData", parent=self, pos=wx.Point(118, 21), size=wx.Size(90, 23), style=0)
		self.cbxData.SetSelection(0)

		self.cbxType = wx.Choice(choices=["PLSR", "PLS-DA"], id=-1, name="cbxType", parent=self, pos=wx.Point(75, 21), size=wx.Size(50, 23), style=0)
		self.cbxType.SetSelection(0)

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

		self.spnPLSmaxfac = wx.SpinCtrl(id=-1, initial=2, max=100, min=1, name="spnPLSmaxfac", parent=self, pos=wx.Point(54, 72), size=wx.Size(54, 23), style=wx.SP_ARROW_KEYS)
		self.spnPLSmaxfac.SetValue(1)
		self.spnPLSmaxfac.SetToolTip("")

		self.btnRunFullPls = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "run.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Run PLS", longHelp="Run Partial Least Squares")
		self.btnRunFullPls.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnRunFullPlsButton, id=self.btnRunFullPls.GetId())

		self.spnPLSfactor1 = wx.SpinCtrl(id=-1, initial=1, max=100, min=1, name="spnPLSfactor1", parent=self, pos=wx.Point(228, 4), size=wx.Size(46, 23), style=wx.SP_ARROW_KEYS)
		self.spnPLSfactor1.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "MS Sans Serif"))
		self.spnPLSfactor1.SetToolTip("")
		self.spnPLSfactor1.Enable(0)
		self.spnPLSfactor1.Bind(wx.EVT_SPINCTRL, self.OnSpnPLSfactor1Spinctrl, id=-1)

		self.spnPLSfactor2 = wx.SpinCtrl(id=-1, initial=2, max=100, min=1, name="spnPLSfactor2", parent=self, pos=wx.Point(228, 4), size=wx.Size(46, 23), style=wx.SP_ARROW_KEYS)
		self.spnPLSfactor2.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "MS Sans Serif"))
		self.spnPLSfactor2.SetToolTip("")
		self.spnPLSfactor2.Enable(0)
		self.spnPLSfactor2.Bind(wx.EVT_SPINCTRL, self.OnSpnPLSfactor2Spinctrl, id=-1)

		self.btnExpPls = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "export.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Export PLS Results", longHelp="Export PLS Results")
		self.btnExpPls.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnExpPlsButton, id=self.btnExpPls.GetId())

	def __init__(self, parent, id, text, style, alignment):

		self._init_btnpanel_ctrls(parent)

		self.parent = parent

		self.CreateButtons()

	def CreateButtons(self):
		self.Freeze()

		self.SetProperties()

		self.AddControl(self.cbxData)
		self.AddControl(self.cbxType)
		self.AddControl(self.cbxPreprocType)
		self.AddControl(wx.lib.stattext.GenStaticText(self, -1, "Max. factors", style=wx.TRANSPARENT_WINDOW))
		self.AddControl(self.spnPLSmaxfac)
		self.AddSeparator()
		self.AddControl(wx.lib.stattext.GenStaticText(self, -1, "PLS factor", style=wx.TRANSPARENT_WINDOW))
		self.AddControl(self.spnPLSfactor1)
		self.AddControl(wx.lib.stattext.GenStaticText(self, -1, " vs. ", style=wx.TRANSPARENT_WINDOW))
		self.AddControl(self.spnPLSfactor2)
		self.AddSeparator()
		self.AddButton(self.btnRunFullPls)
		self.AddSeparator()
		self.AddButton(self.btnExpPls)

		self.Thaw()

		self.DoLayout()

	def getData(self, data):
		self.data = data

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

	def OnBtnRunFullPlsButton(self, event):
		self.runPls()

	def OnSpnPLSfactor1Spinctrl(self, event):
		self.plotPlsScores()
		self.plotPlsLoads()

	def OnSpnPLSfactor2Spinctrl(self, event):
		self.plotPlsScores()
		self.plotPlsLoads()

	def OnBtnExpPlsButton(self, event):
		dlg = wx.FileDialog(self, "Choose a file", ".", "", "Any files (*.*)|*.*", wx.FD_SAVE)
		try:
			# here
			if dlg.ShowModal() == wx.ID_OK:
				saveFile = dlg.GetPath()
				# prepare prediction output
				pred = []
				pred = scipy.concatenate((np.array(self.data["validation"])[:, nA], self.data["class"], self.data["plspred"]), 1)

				out = "#PARTIAL_LEAST_SQUARES_PREDICTIONS\nValidation\t"
				for i in range(self.data["class"].shape[1]):
					out = out + "Y" + str(i) + "\t"
				for i in range(self.data["class"].shape[1]):
					out = out + "P" + str(i) + "\t"

				out = out + "\n" + str_array(np.array(pred), col_sep="\t") + "\n" + "#PARTIAL_LEAST_SQUARES_LOADINGS\n" + str_array(self.data["plsloads"], col_sep="\t") + "\n" + "#NUMBER_OF_PLS_FACTORS\n" + str(self.data["plsfactors"] + 1) + "\n" + "#ROOT_MEAN_SQUARED_ERROR_OF_CALIBRATION\n" + str(self.data["rmsec"]) + "\n" + "#ROOT_MEAN_SQUARED_ERROR_OF_CROSS_VALIDATION\n" + str(self.data["rmsepc"]) + "\n" + "#ROOT_MEAN_SQUARED_ERROR_FOR_INDEPENDENT_TEST_SAMPLES\n" + str(self.data["rmsept"]) + "\n" + "#PARTIAL_PREDICTION\n" + str_array(self.data["partial_pred"], col_sep="\t") + "\n" + "#SPECTRAL SCORES\n" + str_array(self.data["plst"], col_sep="\t")
				f = open(saveFile, "w")
				f.write(out)
				f.close()
		except Exception as error:
			errorBox(self, "%s" % str(error))
		##			  raise
		finally:
			dlg.Destroy()

	def runPls(self):
		try:
			# Get X
			if self.cbxData.GetSelection() == 0:
				xdata = self.data["rawtrunc"]
			elif self.cbxData.GetSelection() == 1:
				xdata = self.data["proctrunc"]

			# save preproc type
			self.data["plstype"] = self.cbxType.GetSelection()

			# create false pls2 constituent array for pls-da classification
			if self.cbxType.GetSelection() == 1:
				self.data["pls_class"] = -scipy.ones((len(self.data["class"][:, 0]), len(scipy.unique(self.data["class"][:, 0]))))
				uCnt = 0
				for each in scipy.unique(self.data["class"][:, 0]):
					idx = _index(self.data["class"][:, 0], each)
					self.data["pls_class"][idx, uCnt] = scipy.ones((len(idx),))
					uCnt += 1

			else:
				self.data["pls_class"] = self.data["class"]

			# Run PLS
			pls_output = mva.chemometrics.PLS(xdata, self.data["pls_class"], self.data["validation"], self.spnPLSmaxfac.GetValue(), stb=self.parent.prnt.parent.sbMain, type=self.cbxPreprocType.GetSelection())

			self.data["plsloads"] = pls_output["W"]
			self.data["plst"] = pls_output["plsscores"]
			self.data["plsfactors"] = pls_output["facs"]
			self.data["plspred"] = pls_output["predictions"]
			self.data["rmsec"] = pls_output["rmsec"]
			self.data["rmsepc"] = pls_output["rmsepc"]
			self.data["rmsept"] = pls_output["rmsept"]
			self.data["RMSEC"] = pls_output["RMSEC"]
			self.data["RMSEPC"] = pls_output["RMSEPC"]
			self.data["RMSEPT"] = pls_output["RMSEPT"]
			self.data["partial_pred"] = scipy.transpose(pls_output["b"])

			# plot pls error
			plotLine(self.parent.plcPLSerror, scipy.concatenate((np.array(self.data["rmsec"])[nA, :], np.array(self.data["rmsepc"])[nA, :]), 0), xaxis=scipy.arange(1, len(self.data["rmsec"]) + 1)[:, nA], rownum=0, tit="Root Mean Squared Error", xLabel="Latent variable", yLabel="RMS Error", type="multi", ledge=["Trn Err", "Tst Err"], wdth=3)

			# plot predicted vs. residuals for train and validation
			trnPlot, valPlot = scipy.zeros((1, 2)), scipy.zeros((1, 2))
			for p in range(self.data["plspred"].shape[1]):
				trnData = scipy.take(self.data["plspred"][:, p][:, nA], _index(self.data["validation"], 0), axis=0)

				trnPlot = scipy.concatenate((trnPlot, scipy.concatenate((trnData, trnData - scipy.take(np.array(self.data["class"][:, 0])[:, nA], _index(self.data["validation"], 0), 0)), 1)), 0)

				valData = scipy.take(self.data["plspred"][:, p][:, nA], _index(self.data["validation"], 1), axis=0)

				valPlot = scipy.concatenate((valPlot, scipy.concatenate((valData, valData - scipy.take(np.array(self.data["class"][:, 0])[:, nA], _index(self.data["validation"], 1), 0)), 1)), 0)

			trnObj = wx.lib.plot.PolyMarker(trnPlot[1 : len(trnPlot), :], legend="Train", colour="black", marker="square", size=1.25, fillstyle=wx.TRANSPARENT)

			valObj = wx.lib.plot.PolyMarker(valPlot[1 : len(valPlot), :], legend="Val.", colour="red", marker="circle", size=1.25, fillstyle=wx.TRANSPARENT)

			PlsHeteroPlot = wx.lib.plot.PlotGraphics([trnObj, valObj], "Residuals v. Predicted Values", "Predicted", "Residuals")

			self.parent.plcPlsHetero.Draw(PlsHeteroPlot)

			# Set max fac for loadings plot
			self.spnPLSfactor1.Enable(1)
			self.spnPLSfactor2.Enable(1)
			self.spnPLSfactor1.SetRange(1, self.spnPLSmaxfac.GetValue())
			self.spnPLSfactor2.SetRange(1, self.spnPLSmaxfac.GetValue())
			self.spnPLSfactor1.SetValue(1)
			self.spnPLSfactor2.SetValue(2)

			# plot pls model
			self.parent.plcPredPls1 = PlotPlsModel(self.parent.plcPredPls1, model="full", tbar=self.parent.prnt.parent.tbMain, cL=self.data["class"], scores=self.data["plst"], predictions=self.data["plspred"], validation=self.data["validation"], RMSEPT=self.data["RMSEPT"], factors=self.data["plsfactors"], type=self.data["plstype"], col1=0, col2=1, label=self.data["label"], symbols=self.parent.prnt.parent.tbMain.tbSymbols.GetValue(), usetxt=self.parent.prnt.parent.tbMain.tbPoints.GetValue(), usecol=[], usesym=[], errplot=False, plScL=self.data["pls_class"])

			# Draw PLS loadings
			self.plotPlsLoads()

			# for pls export
			self.plsError = scipy.concatenate((scipy.reshape(self.data["rmsec"], (1, len(self.data["rmsec"]))), scipy.reshape(self.data["rmsepc"], (1, len(self.data["rmsepc"])))), 0)

			# Do OLS on results
			self.doOls(self.parent.plcPlsStats, self.data["plspred"], self.data["class"][:, 0], self.data["validation"], self.data["RMSEC"], self.data["RMSEPC"], self.data["RMSEPT"])

			# allow results export
			self.btnExpPls.Enable(1)

		except Exception as error:
			errorBox(self, "%s" % str(error))
			raise

	def doOls(self, writeto, predictions, labels, mask, rmsec, rmsecv, rmset):
		# Do least squares regression on PLS results
		n0, n1, n2 = [], [], []
		for i in range(len(labels)):
			if mask[i] == 0:
				n0.append(labels[i])
			elif mask[i] == 1:
				n1.append(labels[i])
			else:
				n2.append(labels[i])

		predy = scipy.take(predictions, _index(mask, 0), axis=0)
		trngrad, trnyi, trnmserr, trnrmserr, trngerr, trnierr = mva.chemometrics.OLS(n0, predy)

		predyv = scipy.take(predictions, _index(mask, 1), axis=0)
		cvgrad, cvyi, cvmserr, cvrmserr, cvgerr, cvierr = mva.chemometrics.OLS(n1, predyv)

		if max(mask) == 2:
			predyt = scipy.take(predictions, _index(mask, 2), axis=0)
			tstgrad, tstyi, tstmserr, tstrmserr, tstgerr, tstierr = mva.chemometrics.OLS(n2, predyt)
		else:
			tstgrad, tstyi, tstmserr, tstrmserr, tstgerr, tstierr = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

		# Write to textctrl
		write = []
		write.append(wx.lib.plot.PolyMarker(np.array([[0, 12]]), marker="text", labels="Root mean squared error"))

		write.append(wx.lib.plot.PolyMarker(np.array([[0, 10.5]]), marker="text", labels="Calibration"))
		write.append(wx.lib.plot.PolyMarker(np.array([[12, 10.5]]), marker="text", labels="Validation"))
		write.append(wx.lib.plot.PolyMarker(np.array([[24, 10.5]]), marker="text", labels="Test"))
		write.append(wx.lib.plot.PolyLine([[0, 9.5], [8, 9.5]]))
		write.append(wx.lib.plot.PolyLine([[12, 9.5], [20, 9.5]]))
		write.append(wx.lib.plot.PolyLine([[24, 9.5], [32, 9.5]]))
		write.append(wx.lib.plot.PolyMarker(np.array([[0, 9]]), marker="text", labels="% .2f" % rmsec))
		write.append(wx.lib.plot.PolyMarker(np.array([[12, 9]]), marker="text", labels="% .2f" % rmsecv))
		if max(mask) > 1:
			write.append(wx.lib.plot.PolyMarker(np.array([[24, 9]]), marker="text", labels="% .2f" % rmset))

		write.append(wx.lib.plot.PolyMarker(np.array([[0, 7.5]]), marker="text", labels="Least Squares Regression"))

		##		  write.append(wx.lib.plot.PolyMarker(np.array([[0,6]]),marker='text',
		##								  labels='Coefficient'))
		##		  write.append(wx.lib.plot.PolyMarker(np.array([[12,6]]),marker='text',
		##								  labels='Standard Error'))
		##		  write.append(wx.lib.plot.PolyLine([[0,5],[8,5]]))
		##		  write.append(wx.lib.plot.PolyLine([[12,5],[20,5]]))
		##		  write.append(wx.lib.plot.PolyMarker(np.array([[0,4.5]]),marker='text',
		##								  labels='%.2f' %trngerr))
		##		  write.append(wx.lib.plot.PolyMarker(np.array([[12,4.5]]),marker='text',
		##								  labels='%.2f' %trnierr[0]))
		# train
		write.append(wx.lib.plot.PolyMarker(np.array([[0, 6]]), marker="text", labels="Train Intercept (Error)"))
		write.append(wx.lib.plot.PolyMarker(np.array([[12, 6]]), marker="text", labels="Train Slope (Error)"))
		write.append(wx.lib.plot.PolyLine([[0, 5], [8, 5]]))
		write.append(wx.lib.plot.PolyLine([[12, 5], [20, 5]]))
		write.append(wx.lib.plot.PolyMarker(np.array([[0, 4.5]]), marker="text", labels="%.2f" % trnyi[0] + " (" + "%.2f" % trnierr[0] + ")"))
		write.append(wx.lib.plot.PolyMarker(np.array([[12, 4.5]]), marker="text", labels="%.2f" % trngrad[0] + " (" + "%.2f" % trngerr + ")"))

		# cross-validation
		write.append(wx.lib.plot.PolyMarker(np.array([[0, 3]]), marker="text", labels="Val. Intercept (Error)"))
		write.append(wx.lib.plot.PolyMarker(np.array([[12, 3]]), marker="text", labels="Val. Slope (Error)"))
		write.append(wx.lib.plot.PolyLine([[0, 2], [8, 2]]))
		write.append(wx.lib.plot.PolyLine([[12, 2], [20, 2]]))
		write.append(wx.lib.plot.PolyMarker(np.array([[0, 1.5]]), marker="text", labels="%.2f" % cvyi[0] + " (" + "%.2f" % cvierr[0] + ")"))
		write.append(wx.lib.plot.PolyMarker(np.array([[12, 1.5]]), marker="text", labels="%.2f" % cvgrad[0] + " (" + "%.2f" % cvgerr + ")"))

		# test
		if max(mask) > 1:
			write.append(wx.lib.plot.PolyMarker(np.array([[0, 0]]), marker="text", labels="Test Intercept (Error)"))
			write.append(wx.lib.plot.PolyMarker(np.array([[12, 0]]), marker="text", labels="Test Slope (Error)"))
			write.append(wx.lib.plot.PolyLine([[0, -1], [8, -1]]))
			write.append(wx.lib.plot.PolyLine([[12, -1], [20, -1]]))
			write.append(wx.lib.plot.PolyMarker(np.array([[0, -1.5]]), marker="text", labels="%.2f" % tstyi[0] + " (" + "%.2f" % tstierr[0] + ")"))
			write.append(wx.lib.plot.PolyMarker(np.array([[12, -1.5]]), marker="text", labels="%.2f" % tstgrad[0] + " (" + "%.2f" % tstgerr + ")"))

		# filler
		write.append(wx.lib.plot.PolyMarker(np.array([[0, -3]]), marker="text", labels=""))

		write = wx.lib.plot.PlotGraphics(write)

		writeto.Draw(write)

	def plotPlsLoads(self):
		# Plot loadings
		if self.spnPLSfactor1.GetValue() != self.spnPLSfactor2.GetValue():
			plotLoads(self.parent.plcPLSloading, self.data["plsloads"], xaxis=self.data["indlabels"], col1=self.spnPLSfactor1.GetValue() - 1, col2=self.spnPLSfactor2.GetValue() - 1, title="PLS Loadings", xLabel="w*c[" + str(self.spnPLSfactor1.GetValue()) + "]", yLabel="w*c[" + str(self.spnPLSfactor2.GetValue()) + "]", type=self.parent.prnt.parent.tbMain.GetLoadPlotIdx(), usecol=[], usesym=[])
		else:
			idx = self.spnPLSfactor1.GetValue() - 1
			plotLine(self.parent.plcPLSloading, scipy.transpose(self.data["plsloads"]), xaxis=self.data["xaxis"], tit="PLS Loadings", rownum=idx, type="single", xLabel="Variable", yLabel="w*c[" + str(idx + 1) + "]", wdth=1, ledge=[])

	def plotPlsScores(self):
		# Plot scores for pls-da
		if self.data["plstype"] == 1:
			self.parent.plcPredPls1 = PlotPlsModel(self.parent.plcPredPls1, model="full", tbar=self.parent.prnt.parent.tbMain, cL=self.data["class"], scores=self.data["plst"], predictions=None, label=self.data["label"], validation=self.data["validation"], RMSEPT=None, factors=None, type=1, col1=self.spnPLSfactor1.GetValue() - 1, col2=self.spnPLSfactor2.GetValue() - 1, symbols=self.parent.prnt.parent.tbMain.tbSymbols.GetValue(), usetxt=self.parent.prnt.parent.tbMain.tbPoints.GetValue(), usecol=[], usesym=[], plScL=self.data["pls_class"])
