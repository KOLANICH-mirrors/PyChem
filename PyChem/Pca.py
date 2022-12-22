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

import copy
import os
import string

import scipy

import wx
import wx.aui
import wx.lib.agw.buttonpanel as bp
import wx.lib.agw.foldpanelbar as fpb
import wx.lib.buttons
import wx.lib.plot
import wx.lib.stattext
from scipy import newaxis as nA
from wx.lib.anchors import LayoutAnchors

from . import thisDir
from .mva import chemometrics
from .mva.chemometrics import _index
from .utils import getByPath
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
	MNUPLOTCOORDS,
] = [wx.NewIdRef() for _init_plot_menu_Items in range(5)]


def errorBox(window, error):
	dlg = wx.MessageDialog(window, "".join(("The following error occured:\n\n", error)), "Error!", wx.OK | wx.ICON_ERROR)
	try:
		dlg.ShowModal()
	finally:
		dlg.Destroy()


def SetButtonState(s1, s2, tb):
	# toolbar button enabled condition
	if s1 == s2:
		tb.tbLoadLabels.Enable(False)
		tb.tbLoadLabStd1.Enable(False)
		tb.tbLoadLabStd2.Enable(False)
		tb.tbLoadSymStd2.Enable(False)
	else:
		tb.tbLoadLabels.Enable(True)
		tb.tbLoadLabStd1.Enable(True)
		tb.tbLoadLabStd2.Enable(True)
		tb.tbLoadSymStd2.Enable(True)


def CreateSymColSelect(canvas, output):
	# populate symbol select pop-up
	# first destroy current
	canvas.tbMain.SymPopUpWin.Destroy()
	# create empty ctrl
	canvas.tbMain.SymPopUpWin = SymColSelectTool(canvas.tbMain)
	# create ctrls
	count = 0
	# apply button
	canvas.tbMain.SymPopUpWin.btnApply = wx.Button(canvas.tbMain.SymPopUpWin, wx.NewIdRef(), "Apply")
	canvas.tbMain.SymPopUpWin.Bind(wx.EVT_BUTTON, canvas.tbMain.SymPopUpWin.OnBtnApply, canvas.tbMain.SymPopUpWin.btnApply)
	# close button
	canvas.tbMain.SymPopUpWin.btnClose = wx.Button(canvas.tbMain.SymPopUpWin, wx.NewIdRef(), "Close")
	canvas.tbMain.SymPopUpWin.Bind(wx.EVT_BUTTON, canvas.tbMain.SymPopUpWin.OnBtnClose, canvas.tbMain.SymPopUpWin.btnClose)
	# spacer
	canvas.tbMain.SymPopUpWin.stSpacer = wx.StaticText(canvas.tbMain.SymPopUpWin, -1, "")
	# dynamic ctrls
	canvas.tbMain.SymPopUpWin.colctrls = []
	canvas.tbMain.SymPopUpWin.symctrls = []
	for each in output:
		exec("canvas.tbMain.SymPopUpWin.st" + str(count) + " = wx.StaticText(canvas.tbMain.SymPopUpWin, -1," + "each[0])")
		exec("canvas.tbMain.SymPopUpWin.btn" + str(count) + " = wx.BitmapButton(canvas.tbMain.SymPopUpWin, " + 'bitmap=wx.Bitmap(str(thisDir / "bmp" / "' + each[1] + '.bmp"), wx.BITMAP_TYPE_BMP), id=-1)')
		exec("canvas.tbMain.SymPopUpWin.btn" + str(count) + '.symname = "' + each[1] + '"')
		exec("canvas.tbMain.SymPopUpWin.btn" + str(count) + ".Bind(wx.EVT_BUTTON, canvas.tbMain.SymPopUpWin.OnBtnSymbol" + ")")
		exec("canvas.tbMain.SymPopUpWin.cp" + str(count) + " = wx.ColourPickerCtrl(canvas.tbMain.SymPopUpWin," + "-1, col=" + str(each[2]) + ", style=wx.CLRP_DEFAULT_STYLE)")
		# output ctrl names to use later
		canvas.tbMain.SymPopUpWin.colctrls.append("cp" + str(count))
		canvas.tbMain.SymPopUpWin.symctrls.append("btn" + str(count))
		count += 1
	# create sizer
	canvas.tbMain.SymPopUpWin.grsSelect = wx.GridSizer(cols=3, hgap=2, rows=count + 1, vgap=2)
	# add standard ctrls
	canvas.tbMain.SymPopUpWin.grsSelect.Add(canvas.tbMain.SymPopUpWin.btnClose, 0, border=0, flag=wx.EXPAND)
	canvas.tbMain.SymPopUpWin.grsSelect.Add(canvas.tbMain.SymPopUpWin.btnApply, 0, border=0, flag=wx.EXPAND)
	canvas.tbMain.SymPopUpWin.grsSelect.Add(canvas.tbMain.SymPopUpWin.stSpacer, 0, border=0, flag=wx.EXPAND)
	# add dynamic ctrls to sizer
	for nwin in range(count):
		canvas.tbMain.SymPopUpWin.grsSelect.Add(getByPath(canvas.tbMain.SymPopUpWin, "st" + str(nwin)), 0, border=0, flag=wx.EXPAND)
		canvas.tbMain.SymPopUpWin.grsSelect.Add(getByPath(canvas.tbMain.SymPopUpWin, "btn" + str(nwin)), 0, border=0, flag=wx.EXPAND)
		canvas.tbMain.SymPopUpWin.grsSelect.Add(getByPath(canvas.tbMain.SymPopUpWin, "cp" + str(nwin)), 0, border=0, flag=wx.EXPAND)

	# set sizer and resize
	canvas.tbMain.SymPopUpWin.SetSizer(canvas.tbMain.SymPopUpWin.grsSelect)
	canvas.tbMain.SymPopUpWin.SetSize(wx.Size(canvas.tbMain.SymPopUpWin.GetSize()[0], count * 35))


def BoxPlot(canvas, x, labels, **_attr):
	"""Box and whisker plot; x is a column vector, labels a list of strings"""

	objects, count = [], 1
	uG = scipy.unique(np.array(labels))
	for each in uG:
		# get values
		group = x[np.array(labels) == each]
		# calculate group median
		m = scipy.median(group)
		# lower (first) quartile
		lq = scipy.median(group[group < m])
		# upper (third) quartile
		uq = scipy.median(group[group > m])
		# interquartile range
		iqr = uq - lq
		# lower whisker
		lw = m - (1.5 * iqr)
		# upper whisker
		uw = m + (1.5 * iqr)
		# lower outlier
		lo = group[group < lw]
		# upper outlier
		uo = group[group > uw]
		# plot b&w
		objects.append(wx.lib.plot.PolyLine([[count - 0.25, m], [count + 0.25, m]], width=1, colour="blue", style=wx.SOLID))
		objects.append(wx.lib.plot.PolyLine([[count - 0.25, lq], [count + 0.25, lq]], width=1, colour="black", style=wx.SOLID))
		objects.append(wx.lib.plot.PolyLine([[count - 0.25, uq], [count + 0.25, uq]], width=1, colour="black", style=wx.SOLID))
		objects.append(wx.lib.plot.PolyLine([[count - 0.25, lq], [count - 0.25, uq]], width=1, colour="black", style=wx.SOLID))
		objects.append(wx.lib.plot.PolyLine([[count + 0.25, lq], [count + 0.25, uq]], width=1, colour="black", style=wx.SOLID))
		objects.append(wx.lib.plot.PolyLine([[count, lq], [count, lw]], width=1, colour="black", style=wx.SOLID))
		objects.append(wx.lib.plot.PolyLine([[count, uq], [count, uw]], width=1, colour="black", style=wx.SOLID))
		objects.append(wx.lib.plot.PolyLine([[count - 0.1, lw], [count + 0.1, lw]], width=1, colour="black", style=wx.SOLID))
		objects.append(wx.lib.plot.PolyLine([[count - 0.1, uw], [count + 0.1, uw]], width=1, colour="black", style=wx.SOLID))
		if len(lo) > 0:
			objects.append(wx.lib.plot.PolyMarker(scipy.concatenate((scipy.ones((len(lo), 1)) * count, lo[:, nA]), 1), colour="red", fillcolour="red", marker="circle", size=1))
		if len(uo) > 0:
			objects.append(wx.lib.plot.PolyMarker(scipy.concatenate((scipy.ones((len(uo), 1)) * count, uo[:, nA]), 1), colour="red", fillcolour="red", marker="circle", size=1))
		count += 1

	canvas.xSpec = "udef"
	canvas.Draw(wx.lib.plot.PlotGraphics(objects, title, xLabel, yLabel, xTickLabels=uG))


def plotErrorBar(canvas, **_attr):
	"""Errorbar plot
	Defaults:
		'x'= None			- xaxis values, column vector
		'y'= None			- average, column vector
		'validation'= None	- list of 0's & 1's & 2's
		'title'= '',		- plot title
		'xLabel'= '',		- x-axis label
		'yLabel'= '',		- y-axis label
		'lsfit'=False,		- show linear fit
		'usesym'=[]
		'usecol'=[]
	"""

	# defaults
	colours = ["black", "red", "blue"]
	usesym = ["square", "circle", "triangle"]
	ledgtext = ["Train", "Validation", "Test"]
	# user defined
	if usesym != []:
		symbols = usesym
	if usecol != []:
		colours = usecol

	objects = []
	if lsfit is True:
		# show linear fit
		objects.append(wx.lib.plot.PolyLine(np.array([[x.min(), x.min()], [x.max(), x.max()]]), legend="Linear fit", colour="cyan", width=1, style=wx.SOLID))

	for val in range(max(validation) + 1):
		# get average and stdev of predictions for each calibration point
		average, stdev = [], []
		xsub = scipy.take(x, _index(validation, val), 0)
		uXsub = scipy.unique(xsub)
		ysub = scipy.take(y, _index(validation, val), 0)
		for item in range(len(uXsub)):
			average.append(scipy.mean(scipy.take(ysub, _index(xsub, uXsub[item]))))
			stdev.append(scipy.std(scipy.take(ysub, _index(xsub, uXsub[item]))))

		# markers
		objects.append(wx.lib.plot.PolyMarker(scipy.concatenate((uXsub[:, nA], np.array(average)[:, nA]), 1), legend=ledgtext[val], colour=colours[val], marker=usesym[val], size=1.5, fillstyle=wx.SOLID))

		# errorbars & horizontal bars
		for line in range(len(uXsub)):
			# errorbars
			objects.append(wx.lib.plot.PolyLine(np.array([[uXsub[line], average[line] - stdev[line]], [uXsub[line], average[line] + stdev[line]]]), colour=colours[val], width=1, style=wx.SOLID))
			# horizontal bars +ve
			objects.append(wx.lib.plot.PolyLine(np.array([[uXsub[line] - (0.01 * abs(max(uXsub))), average[line] + stdev[line]], [uXsub[line] + (0.01 * abs(max(uXsub))), average[line] + stdev[line]]]), colour=colours[val], width=1, style=wx.SOLID))
			# horizontal bars -ve
			objects.append(wx.lib.plot.PolyLine(np.array([[uXsub[line] - (0.01 * abs(max(uXsub))), average[line] - stdev[line]], [uXsub[line] + (0.01 * abs(max(uXsub))), average[line] - stdev[line]]]), colour=colours[val], width=1, style=wx.SOLID))

	# axis limits
	xAx = (x.min() - (0.05 * x.max()), x.max() + (0.05 * x.max()))
	yAx = (y.min() - (0.05 * y.max()), y.max() + (0.05 * y.max()))

	canvas.Draw(wx.lib.plot.PlotGraphics(objects, title, xLabel, yLabel), xAx, yAx)


def PlotPlsModel(canvas, model="full", tbar=None, **_attr):
	"""Plot PLS predictions or scores; model = 'full' for PLSR,
	   model = 'ga' for GA-PLS feature selection

	**_attr - key word _attributes
			Defaults:
				'predictions'= None		- pls predictions
				'cL' = None				- constituents
				'scores'	 = None		- pls spectral scores
				'plScL'		 = None		- false class for pls-da
				'validation' = None,	- split data
				'factors'	 = 1,		- no. latent variables
				'type'		 = 0		- plsr or pls-da
				'symbols'	 = False	- plot with symbols
				'usetxt'	 = True		- plot with text labels
				'RMSEPT'	 = 0		- RMSE for independent test samples
				'col1'		 = 0		- col for xaxis
				'col2'		 = 1		- col for yaxis
	"""

	if model in ["full"]:
		canvPref = "plcPredPls"
		prnt = canvas.prnt.prnt
		nBook = canvas.prnt
	elif model in ["ga"]:
		canvPref = "plcGaModelPlot"
		prnt = canvas.prnt.prnt.prnt.splitPrnt
		nBook = canvas.prnt

	if predictions.shape[1] > 1:
		canvas.prnt.SetTabSize((80, 15))
	else:
		canvas.prnt.SetTabSize((0, 1))
		canvas.prnt.SetPageText(0, "")

	if type == 0:
		numPlots = predictions.shape[1]
	else:
		numPlots = predictions.shape[1] + 1

	# delete pages
	nBook.SetSelection(0)
	for page in range(nBook.GetPageCount() - 1, -1, -1):
		nBook.DeletePage(page)

	for const in range(numPlots):
		if type == 0:
			cL = cL[:, const][:, nA]
			pRed = predictions[:, const][:, nA]
		elif (type == 1) & (const > 0) is True:
			cL = plScL[:, const - 1][:, nA]
			pRed = predictions[:, const - 1][:, nA]

		# create new canvas
		exec("prnt." + canvPref + str(const + 1) + "= MyPlotCanvas(id=-1," + "name='" + canvPref + str(const + 1) + "', parent=nBook, " + "pos=wx.Point(0, 0), size=wx.Size(302, 246)," + "style=0, toolbar=tbar)")
		getByPath(prnt, canvPref + str(const + 1)).SetFontSizeAxis(8)
		getByPath(prnt, canvPref + str(const + 1)).SetFontSizeTitle(10)
		getByPath(prnt, canvPref + str(const + 1)).SetEnableZoom(True)
		getByPath(prnt, canvPref + str(const + 1)).SetToolTip('')
		getByPath(prnt, canvPref + str(const + 1)).SetEnableLegend(True)
		getByPath(prnt, canvPref + str(const + 1)).SetFontSizeLegend(8)
		getByPath(prnt, canvPref + str(const + 1)).SetAutoLayout(True)
		exec("prnt." + canvPref + str(const + 1) + ".SetConstraints(LayoutAnchors(prnt." + canvPref + str(const + 1) + ",True,True, True, True))")
		# 		 exec("prnt." + canvPref + str(const+1) + ".SetFont(wx.Font(10," + \
		# 			   "wx.SWISS, wx.NORMAL, wx.NORMAL,False, 'Microsoft Sans Serif'))")

		# create new nb page
		if predictions.shape[1] > 1:
			exec("nBook.AddPage(imageId=-1, page=prnt." + canvPref + str(const + 1) + ", select=False, text='PLS Predictions " + str(const + 1) + "')")
		else:
			exec("nBook.AddPage(imageId=-1, page=prnt." + canvPref + str(const + 1) + ", select=False, text='')")

		# use it for plotting
		exec("ncanv = prnt." + canvPref + str(const + 1))

		if (type == 1) and (const == 0) is True:
			# plot pls-da scores
			plotScores(ncanv, scores, cl=cL[:, 0], labels=label, validation=validation, col1=col1, col2=col2, title="PLS Scores", xLabel="t[" + str(col1 + 1) + "]", yLabel="t[" + str(col2 + 1) + "]", xval=True, pconf=False, symb=symbols, text=usetxt, usecol=usecol, usesym=usesym)

		else:
			if symbols is True:
				# pls predictions as errorbar plot
				plotErrorBar(ncanv, x=cL, y=pRed, validation=validation, title="PLS Predictions: " + str(factors + 1) + " factors, RMS(Indep. Test) " + "%.2f" % RMSEPT, xLabel="Actual", yLabel="Predicted", lsfit=True, usesym=usesym, usecol=usecol)
			else:
				# pls predictions as scatter plot
				TrnPnts, ValPnts, TstPnts = scipy.zeros((1, 2), "d"), scipy.zeros((1, 2), "d"), scipy.zeros((1, 2), "d")
				for i in range(len(cL)):
					if int(scipy.reshape(validation[i], ())) == 0:
						y = float(scipy.reshape(cL[i], ()))
						py = float(scipy.reshape(pRed[i], ()))
						TrnPnts = scipy.concatenate((TrnPnts, scipy.reshape((y, py), (1, 2))), 0)
					elif int(scipy.reshape(validation[i], ())) == 1:
						y = float(scipy.reshape(cL[i], ()))
						py = float(scipy.reshape(pRed[i], ()))
						ValPnts = scipy.concatenate((ValPnts, scipy.reshape((y, py), (1, 2))), 0)
					elif int(scipy.reshape(validation[i], ())) == 2:
						y = float(scipy.reshape(cL[i], ()))
						py = float(scipy.reshape(pRed[i], ()))
						TstPnts = scipy.concatenate((TstPnts, scipy.reshape((y, py), (1, 2))), 0)

				TrnPnts = TrnPnts[1 : len(TrnPnts) + 1]
				ValPnts = ValPnts[1 : len(ValPnts) + 1]
				TstPnts = TstPnts[1 : len(TstPnts) + 1]

				TrnPntObj = wx.lib.plot.PolyMarker(TrnPnts, legend="Train", colour="black", marker="square", size=1.5, fillstyle=wx.TRANSPARENT)

				ValPntObj = wx.lib.plot.PolyMarker(ValPnts, legend="Cross Val.", colour="red", marker="circle", size=1.5, fillstyle=wx.TRANSPARENT)

				TstPntObj = wx.lib.plot.PolyMarker(TstPnts, legend="Indep. Test", colour="blue", marker="triangle", size=1.5, fillstyle=wx.TRANSPARENT)

				LinearObj = wx.lib.plot.PolyLine(np.array([[cL.min(), cL.min()], [cL.max(), cL.max()]]), legend="Linear fit", colour="cyan", width=1, style=wx.SOLID)

				PlsModel = wx.lib.plot.PlotGraphics([TrnPntObj, ValPntObj, TstPntObj, LinearObj], " ".join(("PLS Predictions:", str(factors + 1), "factors, RMS(Indep. Test)", "%.2f" % RMSEPT)), "Actual", "Predicted")

				xAx = (cL.min() - (0.05 * cL.max()), cL.max() + (0.05 * cL.max()))

				ys = scipy.concatenate((TrnPnts, ValPnts), 0)

				yAx = (ys.min() - (0.05 * ys.max()), ys.max() + (0.05 * ys.max()))

				ncanv.Draw(PlsModel, xAx, yAx)

	# return canvas
	nBook.SetSelection(0)
	exec("canvas = prnt." + canvPref + str(1))

	return canvas


def plotLine(plotCanvas, plotArr, **_attr):
	"""Line plot
	**_attr - key word _attributes
		Defaults:
			'xaxis' = None,	   - Vector of x-axis values
			'rownum' = 0,	   - Row of plotArr to plot
			'tit'= '',		   - A small domestic bird
			'xLabel'= '',	   - The desired x-axis label
			'yLabel'= '',	   - The desired y-axis label
			'type'= 'single',  - 'single' or 'multi'
			'ledge'= [],	   - Figure legend labels
			'wdth'= 1,		   - Line width
	"""

	colourList = [wx.NamedColour("blue"), wx.NamedColour("red"), wx.NamedColour("green"), wx.NamedColour("light_grey"), wx.NamedColour("cyan"), wx.NamedColour("black")]

	if type == "single":
		pA = plotArr[rownum, 0 : len(xaxis)][:, nA]
		Line = wx.lib.plot.PolyLine(scipy.concatenate((xaxis, pA), 1), colour="black", width=wdth, style=wx.SOLID)
		NewplotLine = wx.lib.plot.PlotGraphics([Line], tit, xLabel, yLabel)
	elif type == "multi":
		ColourCount = 0
		Line = []
		for i in range(plotArr.shape[0]):
			pA = plotArr[i]
			pA = pA[:, nA]
			if ledge is not None:
				Line.append(wx.lib.plot.PolyLine(scipy.concatenate((xaxis, pA), 1), legend=ledge[i], colour=colourList[ColourCount], width=wdth, style=wx.SOLID))
			else:
				Line.append(wx.lib.plot.PolyLine(scipy.concatenate((xaxis, pA), 1), colour=colourList[ColourCount], width=wdth, style=wx.SOLID))
			ColourCount += 1
			if ColourCount == len(colourList):
				ColourCount = 0
		NewplotLine = wx.lib.plot.PlotGraphics(Line, tit, xLabel, yLabel)

	plotCanvas.Draw(NewplotLine)  # ,xAxis=(xaxis.min(),


##			xaxis.max()))


def plotStem(plotCanvas, plotArr, **_attr):
	"""Stem plot
	**_attr - key word _attributes
		Defaults:
			'tit'= '',	   - Figure title
			'xLabel'= '',  - The desired x-axis label
			'yLabel'= '',  - The desired y-axis label
			'wdth'= 1,	   - Line width
	"""

	# plotArr is an n x 2 array
	plotStem = []
	for i in range(plotArr.shape[0]):
		newCoords = np.array([[plotArr[i, 0], 0], [plotArr[i, 0], plotArr[i, 1]]])
		plotStem.append(wx.lib.plot.PolyLine(newCoords, colour="black", width=wdth, style=wx.SOLID))

	plotStem.append(wx.lib.plot.PolyLine(np.array([[plotArr[0, 0] - (0.1 * plotArr[0, 0]), 0], [plotArr[len(plotArr) - 1, 0] + (0.1 * plotArr[0, 0]), 0]]), colour="black", width=1, style=wx.SOLID))

	plotStem = wx.lib.plot.PlotGraphics(plotStem, tit, xLabel, yLabel)

	plotCanvas.Draw(plotStem)


def plotSymbols(plotCanvas, coords, **_attr):
	"""Symbol plot
	**_attr - key word _attributes
		Defaults:
			'mask' = [],	- List of zeros, ones and/or twos to
							  define train, cross-validation and
							  test samples
			'cLass' = [],	- List of integers from 1:n, where
							  n=no. of groups
			'col1' = 0,		- Column to plot along abscissa
			'col2' = 1,		- Column to plot along ordinate
			'tit'= '',		- A small domestic bird
			'xL'= '',		- The desired x-axis label
			'yL'= '',		- The desired y-axis label
			'text'= [],		- List of labels to use in legend
			'usemask'= True,- Flag to define whether to use 'mask'
			'usecol'=[],	- Use a list of colours
			'usesym'= [],	- List of symbols for plotting
	"""

	desCl = scipy.unique(text)
	eCount = 0
	if usecol == []:
		colours = [wx.NamedColour("blue"), wx.NamedColour("red"), wx.NamedColour("green"), wx.NamedColour("cyan"), wx.NamedColour("black")]
	else:
		colours = usecol

	if usesym == []:
		symbols = ["circle", "square", "plus", "triangle", "cross", "triangle_down"]
	else:
		symbols = usesym

	# plot scores using symbols
	valSym = ["circle", "square"]
	plotSym, countSym, countColour, output = [], 0, 0, []
	for each in desCl:
		if countSym > len(symbols) - 1:
			countSym = 0
		if countColour > len(colours) - 1:
			countColour = 0

		# slice coords
		list = coords[np.array(text) == each, :]

		if col1 != col2:
			list = scipy.take(list, (col1, col2), 1)
		else:
			sCount = copy.deepcopy(eCount) + 1
			eCount = eCount + len(list)
			list = scipy.concatenate((scipy.arange(sCount, eCount + 1)[:, nA], list[:, col1][:, nA]), 1)

		##		  col = wx.Colour(round(scipy.rand(1).tolist()[0]*255),
		##				round(scipy.rand(1).tolist()[0]*255),
		##				round(scipy.rand(1).tolist()[0]*255))

		output.append([each, symbols[countSym], colours[countColour]])

		if usemask is False:
			plotSym.append(wx.lib.plot.PolyMarker(list, marker=symbols[countSym], fillcolour=colours[countColour], colour=colours[countColour], size=2, legend=each))

		else:
			listM = mask[np.array(text) == each]
			for m in range(3):
				if m == 0:  # include legend entry
					plotSym.append(wx.lib.plot.PolyMarker(list[listM == m], marker=symbols[countSym], fillcolour=colours[countColour], colour=colours[countColour], size=2.5, legend=each))
				else:  # no legend
					plotSym.append(wx.lib.plot.PolyMarker(list[listM == m], marker=symbols[countSym], fillcolour=colours[countColour], colour=colours[countColour], size=2.5))
					if m > 0:
						if symbols[countSym] not in ["cross", "plus"]:
							# overlay white circle/square to indicate validation/test sample
							plotSym.append(wx.lib.plot.PolyMarker(list[listM == m], marker=valSym[m - 1], colour=wx.NamedColour("white"), fillcolour=wx.NamedColour("white"), size=1))
						else:
							# overlay white square to indicate validation sample
							plotSym.insert(len(plotSym) - 1, wx.lib.plot.PolyMarker(list[listM == m], marker=valSym[m - 1], colour=wx.NamedColour("black"), fillcolour=wx.NamedColour("white"), size=2.5))

		countSym += 1
		countColour += 1

	draw_plotSym = wx.lib.plot.PlotGraphics(plotSym, tit, xLabel=xL, yLabel=yL)

	if plotCanvas is not None:
		plotCanvas.Draw(draw_plotSym)

	return plotSym, output


def plotText(plotCanvas, coords, **_attr):
	"""Text label plot
	**_attr - key word _attributes
		Defaults:
			'mask' = [],	- List of zeros, ones and/or twos to
							  define train, cross-validation and
							  test samples
			'cLass' = [],	- List of integers from 1:n, where
							  n=no. of groups
			'col1' = 0,		- Column to plot along abscissa
			'col2' = 1,		- Column to plot along ordinate
			'tit'= '',		- A small domestic bird
			'xL'= '',		- The desired x-axis label
			'yL'= '',		- The desired y-axis label
			'text'= [],		- List of labels to use in plotting
			'usemask'= True,- Flag to define whether to use 'mask'
	"""

	# make sure label string
	nt = []
	for i in range(len(text)):
		nt.append(str(text[i]))
	text = nt

	plotText = []
	colours = ["black", "blue", "red"]
	if usemask is True:
		colRange = 3
	else:
		colRange = 1

	if (coords.shape[1] > 1) & (col1 != col2) is True:  # plot 2d
		for getColour in range(colRange):  # set text colour - black=train, blue=val, red=test
			if colRange == 3:
				idx = _index(mask, getColour)
			else:
				idx = list(range(len(coords)))
			plotText.append(wx.lib.plot.PolyMarker(scipy.take(scipy.take(coords, [col1, col2], 1), idx, 0), marker="text", labels=scipy.take(text, idx, 0), text_colour=colours[getColour]))
	else:  # plot 1d
		points = scipy.take(coords, [col1], 1)
		nCl = scipy.unique(text)
		eCount = 0
		for each in nCl:
			slice = points[np.array(text) == each]
			lbls = np.array(text)[np.array(text) == each]

			sCount = copy.deepcopy(eCount) + 1
			eCount = eCount + len(slice)

			pointSub = scipy.concatenate((scipy.arange(sCount, eCount + 1)[:, nA], slice), 1)

			if usemask is False:
				plotText.append(wx.lib.plot.PolyMarker(pointSub, marker="text", labels=lbls.tolist()))
			else:
				msk = np.array(mask)[np.array(text) == each].tolist()
				for each in range(3):
					plotText.append(wx.lib.plot.PolyMarker(scipy.take(pointSub, _index(msk, each), 0), marker="text", labels=scipy.take(lbls, _index(msk, each)).tolist(), text_colour=colours[each]))

	if (coords.shape[1] > 1) & (col1 != col2) is True:
		draw_plotText = wx.lib.plot.PlotGraphics(plotText, tit, xLabel=xL, yLabel=yL)
	else:
		draw_plotText = wx.lib.plot.PlotGraphics(plotText, tit, xLabel="", yLabel=yL)

	if plotCanvas is not None:
		plotCanvas.Draw(draw_plotText)

	return plotText


def plotLoads(canvas, loads, **_attr):
	"""Model loadings plot
	**_attr - key word _attributes
		Defaults:
			'xaxis' = [],	- Vector of x-axis values
			'col1' = 0,		- Column to plot along abscissa
			'col2' = 1,		- Column to plot along ordinate
			'title'= '',	- Figure title
			'xLabel'= '',	- The desired x-axis label
			'yLabel'= '',	- The desired y-axis label
			'type'= 0,		- List of labels to use in plotting
			'usecol'= [],	- List of colours for symbol plot
			'usesym'= [],	- List of symbols for plotting
	"""

	# for model loadings plots
	plot = []

	if (col1 != col2) & (loads is not None) is True:
		# standard deviation
		select = scipy.concatenate((loads[:, col1][:, nA], loads[:, col2][:, nA]), 1)
		meanCoords = scipy.reshape(scipy.mean(select, 0), (1, 2))
		std = scipy.mean(scipy.std(select))
		if type == 0:
			# plot labels
			labels = []
			textPlot = plotText(None, select, mask=None, cLass=None, text=xaxis, usemask=False, col1=0, col2=1, tit="", xL="", yL="")
			for each in textPlot:
				plot.append(each)

		else:
			test = scipy.sqrt((loads[:, col1] - meanCoords[0, 0]) ** 2 + (loads[:, col2] - meanCoords[0, 1]) ** 2)
			index = scipy.arange(len(xaxis))

			if type == 1:
				# >1*std error & labels
				outIdx = index[test > std]
				inIdx = index[test <= std]

				getOutliers = scipy.take(select, outIdx, 0)

				# plot labels
				labels = []
				for each in outIdx:
					labels.append(xaxis[each])
				textPlot = plotText(None, getOutliers, mask=None, cLass=None, text=labels, usemask=False, col1=0, col2=1, tit="", xL="", yL="")
				for each in textPlot:
					plot.append(each)

			elif type == 2:
				# >2*std error & labels
				outIdx = index[test > std * 2]
				inIdx = index[test <= std * 2]

				getOutliers = scipy.take(select, outIdx, 0)

				# plot labels
				labels = []
				for each in outIdx:
					labels.append(xaxis[each])
				textPlot = plotText(None, getOutliers, mask=None, cLass=None, text=labels, usemask=False, col1=0, col2=1, tit="", xL="", yL="")
				for each in textPlot:
					plot.append(each)

			elif type == 3:
				# >2*std error & symbols
				outIdx = index[test > std * 2]
				inIdx = index[test <= std * 2]

				# loadings > 2*std
				getOutliers = scipy.take(select, outIdx, 0)

				# identify regions
				newxvar = scipy.take(xaxis, outIdx)
				regions = [outIdx[0]]
				for i in range(len(outIdx) - 1):
					if outIdx[i + 1] - 1 != outIdx[i]:
						regions.append(outIdx[i])
						regions.append(outIdx[i + 1])
				if scipy.mod(len(regions), 2) == 1:
					regions.append(outIdx[i + 1])

				# plot regions by symbol/colour
				cl, labels, i = [], [], 0
				while i < len(regions):
					cl.extend(
						(
							scipy.ones(
								regions[i + 1] - regions[i] + 1,
							)
							* i
						).tolist()
					)
					for j in range(regions[i + 1] - regions[i] + 1):
						labels.append(str(xaxis[regions[i]]) + " - " + str(xaxis[regions[i + 1]]))
					i += 2

				symPlot, output = plotSymbols(None, getOutliers, mask=None, cLass=np.array(cl), text=labels, usemask=False, col1=0, col2=1, tit="", xL="", yL="", usecol=usecol, usesym=usesym)

				# create window in background for changing symbols/colours
				CreateSymColSelect(canvas, output)

				for each in symPlot:
					plot.append(each)

			# ellipse boundary
			plot.append(wx.lib.plot.PolyMarker([[meanCoords[0, 0] - (std * 2), meanCoords[0, 1] - (std * 2)], [meanCoords[0, 0] + (std * 2), meanCoords[0, 1] + (std * 2)]], colour="white", size=1, marker="circle"))
			# centroid
			plot.append(wx.lib.plot.PolyMarker(meanCoords, colour="blue", size=2, marker="plus"))
			# plot 1 std
			plot.append(wx.lib.plot.PolyEllipse(meanCoords, colour="green", width=1, dim=(std * 2, std * 2), style=wx.SOLID))
			# plot 2 stds
			plot.append(wx.lib.plot.PolyEllipse(meanCoords, colour="green", width=1, dim=(std * 4, std * 4), style=wx.SOLID))

		# draw it
		canvas.Draw(wx.lib.plot.PlotGraphics(plot, title, xLabel, yLabel))


def plotScores(canvas, scores, **_attr):
	"""Model scores plot
	**_attr - key word _attributes
		Defaults:
			'cl' = []			- List of integers
			'labels' = []		- List of sample labels
			'validation' = []	- List of zeros, ones and/or twos
			'col1' = 0,			- Column to plot along abscissa
			'col2' = 1,			- Column to plot along ordinate
			'title'= '',		- Figure title
			'xLabel'= '',		- The desired x-axis label
			'yLabel'= '',		- The desired y-axis label
			'xval'= False,		- Cross-validation used flag
			'text'= True,		- Text label plotting used flag
			'pconf'= True,		- 95% confidence limits plotted flag
			'symb'= False,		- Symbol plotting used flag
			'usecol'= [],		- List of colours to use in plotting
			'usesym'= [],		- List of symbols for plotting
	"""

	# make sure we can plot txt

	if (canvas.GetName() not in ["plcDFAscores"]) & (len(canvas.GetName().split("plcGaModelPlot")) == 1) is True:
		canvas.tbMain.tbConf.SetValue(False)
		if (canvas.tbMain.tbPoints.GetValue() is not True) & (canvas.tbMain.tbSymbols.GetValue() is not True) is True:
			canvas.tbMain.tbPoints.SetValue(True)
			text = True

	# get mean centres
	# nb for a dfa/cva plot scaled to unit variance 95% confidence radius is 2.15
	sHape = scores.shape
	nCl = scipy.unique(cl)

	plot = []
	if (sHape[1] > 1) & (col1 != col2) is True:
		canvas.xSpec = "auto"

		scores = scipy.concatenate((scores[:, col1][:, nA], scores[:, col2][:, nA]), 1)

		mScores = scipy.zeros((1, 2))
		for i in range(len(nCl)):
			mScores = scipy.concatenate((mScores, scipy.mean(scipy.take(scores, _index(cl, nCl[i]), 0), 0)[nA, :]), 0)
		mScores = mScores[1 : len(mScores)]

		if symb is True:
			# plot symbols
			symPlot, output = plotSymbols(None, scores, mask=validation, cLass=cl, text=labels, usemask=xval, col1=0, col2=1, tit="", xL="", yL="", usecol=usecol, usesym=usesym)

			# create window in background for changing symbols/colours
			CreateSymColSelect(canvas, output)

			for each in symPlot:
				plot.append(each)

		if text is True:
			# plot labels
			textPlot = plotText(None, scores, mask=validation, cLass=cl, text=labels, col1=0, col2=1, usemask=xval, tit="", xL="", yL="")
			for each in textPlot:
				plot.append(each)

		if pconf is True:
			# 95% confidence interval
			plot.append(wx.lib.plot.PolyEllipse(mScores, colour="black", width=1, dim=(2.15 * 2, 2.15 * 2), style=wx.SOLID))
			# 95% confidence about the mean
			plot.append(wx.lib.plot.PolyEllipse(mScores, colour="blue", width=1, dim=((1.95 / scipy.sqrt(len(nCl)) * 2), (1.95 / scipy.sqrt(len(nCl)) * 2)), style=wx.SOLID))
			# class centroids
			plot.append(wx.lib.plot.PolyMarker(mScores[:, 0:2], colour="black", size=2, marker="plus"))
			# force boundary
			plot.append(wx.lib.plot.PolyMarker([[min(mScores[:, 0] - 2.15), min(mScores[:, 1] - 2.15)], [max(mScores[:, 0] + 2.15), max(mScores[:, 1] + 2.15)]], colour="white", size=1, marker="circle"))

			# class centroid label
			if (symb is False) & (text is False) is True:
				uC, centLab, centLabOrds = scipy.unique(cl), [], []
				for gC in range(len(uC)):
					Idx = _index(cl, uC[gC])[0]
					centLab.append(labels[Idx])
					centLabOrds.append(scipy.reshape(mScores[gC, :], (scores.shape[1],)).tolist())

				# print centroid labels
				centPlot = plotText(None, np.array(centLabOrds), cLass=scipy.arange(1, len(centLab) + 1), text=centLab, col1=0, col2=1, tit="", xL="", yL="", usemask=False)
				for each in centPlot:
					plot.append(each)

		canvas.Draw(wx.lib.plot.PlotGraphics(plot, title, xLabel, yLabel))

	else:
		canvas.xSpec = "none"
		if text is True:
			# plot labels
			textPlot = plotText(None, scores, mask=validation, cLass=cl, text=labels, col1=col1, col2=col1, tit=title, xL="Arbitrary", yL=yLabel, usemask=xval)
			for each in textPlot:
				plot.append(each)

		if symb is True:
			# plot symbols
			symPlot, output = plotSymbols(None, scores, mask=validation, cLass=cl, text=labels, usemask=xval, col1=col1, col2=col1, tit="", xL="", yL="", usecol=usecol, usesym=usesym)

			# create window in background for changing symbols/colours
			CreateSymColSelect(canvas, output)

			for each in symPlot:
				plot.append(each)

		if (text is True) | (symb is True) is True:
			canvas.Draw(wx.lib.plot.PlotGraphics(plot, title, "", yLabel))


class SymColSelectTool(wx.Dialog):
	def __init__(self, prnt):
		wx.Dialog.__init__(self, parent=prnt, style=0)
		self.SetSize(wx.Size(300, 0))
		self.SetAutoLayout(True)
		self.prnt = prnt

	def OnBtnClose(self, evt):
		self.Show(False)

	def OnBtnApply(self, evt):
		# get list of new colours
		collist = []
		for each in self.colctrls:
			collist.append(getByPath(self, each).GetColour())
		# get list of new symbols
		symlist = []
		for each in self.symctrls:
			symlist.append(getByPath(self, each).symname)
		# plot loadings
		self.prnt.doPlot(loadType=3, symcolours=collist, symsymbols=symlist)
		self.prnt.loadIdx = 3

	def OnBtnSymbol(self, evt):
		# symbol select dialog
		btn = evt.GetEventObject()
		dlg = SymDialog(self, btn)
		pos = btn.ClientToScreen((0, 0))
		sz = btn.GetSize()
		dlg.SetPosition(wx.Point(pos[0] - 155, pos[1] + sz[1]))
		dlg.ShowModal()


class SymDialog(wx.Dialog):
	def _init_sizers(self):
		# generated method, don't edit
		self.grsSymDialog = wx.GridSizer(cols=2, hgap=2, rows=3, vgap=2)

		self._init_coll_grsSymDialog_Items(self.grsSymDialog)

		self.SetSizer(self.grsSymDialog)

	def _init_coll_grsSymDialog_Items(self, parent):
		# generated method, don't edit

		parent.Add(self.tbSquare, 0, border=0, flag=wx.EXPAND)
		parent.Add(self.tbCircle, 0, border=0, flag=wx.EXPAND)
		parent.Add(self.tbPlus, 0, border=0, flag=wx.EXPAND)
		parent.Add(self.tbTriangleUp, 0, border=0, flag=wx.EXPAND)
		parent.Add(self.tbTriangleDown, 0, border=0, flag=wx.EXPAND)
		parent.Add(self.tbCross, 0, border=0, flag=wx.EXPAND)

	def _init_ctrls(self, prnt):
		# generated method, don't edit
		wx.Dialog.__init__(self, id=-1, name="SymDialog", parent=prnt, pos=wx.Point(589, 316), size=wx.Size(156, 155), style=wx.DEFAULT_DIALOG_STYLE, title="Select Symbol")
		self.SetClientSize(wx.Size(140, 119))
		self.SetToolTip("")

		self.tbSquare = wx.BitmapButton(bitmap=wx.Bitmap(str(thisDir / "bmp" / "square.bmp"), wx.BITMAP_TYPE_BMP), id=-1, name="tbSquare", parent=self, pos=wx.Point(0, 0), size=wx.Size(69, 38), style=0)
		self.tbSquare.Bind(wx.EVT_BUTTON, self.OnTbSquareButton)

		self.tbCircle = wx.BitmapButton(bitmap=wx.Bitmap(str(thisDir / "bmp" / "circle.bmp"), wx.BITMAP_TYPE_BMP), id=-1, name="tbCircle", parent=self, pos=wx.Point(71, 0), size=wx.Size(69, 38), style=0)
		self.tbCircle.Bind(wx.EVT_BUTTON, self.OnTbCircleButton)

		self.tbPlus = wx.BitmapButton(bitmap=wx.Bitmap(str(thisDir / "bmp" / "plus.bmp"), wx.BITMAP_TYPE_BMP), id=-1, name="tbPlus", parent=self, pos=wx.Point(0, 40), size=wx.Size(69, 38), style=0)
		self.tbPlus.Bind(wx.EVT_BUTTON, self.OnTbPlusButton)

		self.tbTriangleUp = wx.BitmapButton(bitmap=wx.Bitmap(str(thisDir / "bmp" / "triangle.bmp"), wx.BITMAP_TYPE_BMP), id=-1, name="tbTriangleUp", parent=self, pos=wx.Point(71, 40), size=wx.Size(69, 38), style=0)
		self.tbTriangleUp.Bind(wx.EVT_BUTTON, self.OnTbTriangleUpButton)

		self.tbTriangleDown = wx.BitmapButton(bitmap=wx.Bitmap(str(thisDir / "bmp" / "triangle_down.bmp"), wx.BITMAP_TYPE_BMP), id=-1, name="tbTriangleDown", parent=self, pos=wx.Point(0, 80), size=wx.Size(69, 38), style=0)
		self.tbTriangleDown.Bind(wx.EVT_BUTTON, self.OnTbTriangleDownButton)

		self.tbCross = wx.BitmapButton(bitmap=wx.Bitmap(str(thisDir / "bmp" / "cross.bmp"), wx.BITMAP_TYPE_BMP), id=-1, name="tbCross", parent=self, pos=wx.Point(71, 80), size=wx.Size(69, 38), style=0)
		self.tbCross.Bind(wx.EVT_BUTTON, self.OnTbCrossButton)

		self._init_sizers()

	def __init__(self, parent, btn):
		self._init_ctrls(parent)

		self.btn = btn

	def OnTbSquareButton(self, event):
		self.btn.SetBitmapLabel(wx.Bitmap(str(thisDir / "bmp" / "square.bmp")))
		self.btn.symname = "square"
		self.Destroy()

	def OnTbCircleButton(self, event):
		self.btn.SetBitmapLabel(wx.Bitmap(str(thisDir / "bmp" / "circle.bmp")))
		self.btn.symname = "circle"
		self.Destroy()

	def OnTbPlusButton(self, event):
		self.btn.SetBitmapLabel(wx.Bitmap(str(thisDir / "bmp" / "plus.bmp")))
		self.btn.symname = "plus"
		self.Destroy()

	def OnTbTriangleUpButton(self, event):
		self.btn.SetBitmapLabel(wx.Bitmap(str(thisDir / "bmp" / "triangle.bmp")))
		self.btn.symname = "triangle"
		self.Destroy()

	def OnTbTriangleDownButton(self, event):
		self.btn.SetBitmapLabel(wx.Bitmap(str(thisDir / "bmp" / "triangle_down.bmp")))
		self.btn.symname = "triangle_down"
		self.Destroy()

	def OnTbCrossButton(self, event):
		self.btn.SetBitmapLabel(wx.Bitmap(str(thisDir / "bmp" / "cross.bmp")))
		self.btn.symname = "cross"
		self.Destroy()


class MyPlotCanvas(wx.lib.plot.PlotCanvas):
	def _init_plot_menu_Items(self, parent):

		parent.Append(id=MNUPLOTCOPY, item="Copy Figure", helpString="", kind=wx.ITEM_NORMAL)
		parent.Append(id=MNUPLOTCOORDS, item="Copy Coordinates", helpString="", kind=wx.ITEM_NORMAL)
		parent.Append(id=MNUPLOTPRINT, item="Print", helpString="", kind=wx.ITEM_NORMAL)
		parent.Append(id=MNUPLOTSAVE, item="Save", helpString="", kind=wx.ITEM_NORMAL)
		##		  parent.Append(id=MNUPLOTPROPS, item="Properties", helpString="", kind=wx.ITEM_NORMAL)
		self.Bind(wx.EVT_MENU, self.OnMnuPlotCopy, id=MNUPLOTCOPY)
		self.Bind(wx.EVT_MENU, self.OnMnuPlotPrint, id=MNUPLOTPRINT)
		self.Bind(wx.EVT_MENU, self.OnMnuPlotSave, id=MNUPLOTSAVE)
		##		  self.Bind(wx.EVT_MENU, self.OnMnuPlotProperties, id=MNUPLOTPROPS)
		self.Bind(wx.EVT_MENU, self.OnMnuPlotCoords, id=MNUPLOTCOORDS)

	def _init_utils(self):
		self.plotMenu = wx.Menu(title="")

		self._init_plot_menu_Items(self.plotMenu)

	def __init__(self, parent, id, pos, size, style, name, toolbar):
		wx.lib.plot.PlotCanvas.__init__(self, parent, id, pos, size, style, name)
		self.xSpec = "min"
		self.ySpec = "min"
		self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)

		self._init_utils()

		self.prnt = parent

		self.tbMain = toolbar

	def OnMnuPlotCopy(self, event):
		# for windows
		self.Redraw(wx.MetaFileDC()).SetClipboard()

		# for linux

	##		  wx.TheClipboard.Open()
	##		  wx.TheClipboard.SetData(self.Copy())
	##		  wx.TheClipboard.Close()

	def OnMnuPlotPrint(self, event):
		self.Printout()

	def OnMnuPlotSave(self, event):
		self.SaveFile()

	##	  def OnMnuPlotProperties(self, event):
	##		  dlg = plotProperties(self)
	##		  dlg.SetSize(wx.Size(450,350))
	##		  dlg.Center(wx.BOTH)
	##
	##		  #Set up dialog for specific cases
	##		  if self.GetName() in ['plcDFAscores', 'plcPCAscore', 'plcGaFeatPlot']: #dfa & pca score plots
	##			  dlg.scoreSets.Enable(True)
	##		  if self.GetName() in ['plcPCAscore', 'plcGaFeatPlot']: #pca score plots minus conf intervals
	##			  dlg.tbConf.Enable(False)
	##			  dlg.tbConf.SetValue(False)
	##		  if self.GetName() in ['plcGaModelPlot1']:#ga-dfa score plots
	##			  if self.prnt.prnt.splitPrnt.type in ['DFA']:
	##				  dlg.scoreSets.Enable(True)
	##		  if self.GetName() in ['plcPcaLoadsV','plcDfaLoadsV','plcGaSpecLoad','plcPLSloading']:
	##			  dlg.loadSets.Enable(True)
	##		  dlg.Iconize(False)
	##		  dlg.ShowModal()

	def OnMnuPlotCoords(self, event):
		# send coords to clipboard
		getPoints = self.last_draw[0].objects
		coords = []
		for each in getPoints:
			coords.extend(each._points.tolist())

		data = str_array(coords, col_sep="\t")
		wx.TheClipboard.Open()
		wx.TheClipboard.SetData(wx.TextDataObject("X\tY\n" + data))
		wx.TheClipboard.Close()

	def OnMouseRightDown(self, event):
		pt = event.GetPosition()
		self.PopupMenu(self.plotMenu, pt)

	def OnMouseLeftDown(self, event):
		# put info in tb
		self.PopulateToolbar()
		# get coords for zoom centre
		self._zoomCorner1[0], self._zoomCorner1[1] = self._getXY(event)
		self._screenCoordinates = np.array(event.GetPosition())
		if self._dragEnabled:
			self.SetCursor(self.GrabHandCursor)
			self.tbMain.canvas.CaptureMouse()
		if self._interEnabled:
			if self.last_draw is not None:
				graphics, xAxis, yAxis = self.last_draw
				xy = self.PositionScreenToUser(self._screenCoordinates)
				graphics.objects.append(wx.lib.plot.PolyLine([[xy[0], yAxis[0]], [xy[0], yAxis[1]]], colour="red"))
				self._Draw(graphics, xAxis, yAxis)

	def PopulateToolbar(self):
		# enable plot toolbar
		self.tbMain.Enable(True)
		self.tbMain.Refresh()

		# populate plot toolbar
		self.tbMain.canvas = self
		self.tbMain.graph = self.last_draw[0]

		self.tbMain.txtPlot.SetValue(self.tbMain.graph.getTitle())
		self.tbMain.txtXlabel.SetValue(self.tbMain.graph.getXLabel())
		self.tbMain.txtYlabel.SetValue(self.tbMain.graph.getYLabel())

		self.tbMain.spnAxesFont.SetValue(self.GetFontSizeAxis())
		self.tbMain.spnTitleFont.SetValue(self.GetFontSizeTitle())

		self.minXrange = self.GetXCurrentRange()[0]
		self.maxXrange = self.GetXCurrentRange()[1]
		self.minYrange = self.GetYCurrentRange()[0]
		self.maxYrange = self.GetYCurrentRange()[1]

		self.tbMain.Increment = (self.maxXrange - self.minXrange) / 100

		self.tbMain.txtXmin.SetValue("%.2f" % self.minXrange)
		self.tbMain.txtXmax.SetValue("%.2f" % self.maxXrange)
		self.tbMain.txtYmax.SetValue("%.2f" % self.maxYrange)
		self.tbMain.txtYmin.SetValue("%.2f" % self.minYrange)

		# enable controls
		if self.GetName() not in ["plcPcaLoadsV", "plcDfaLoadsV", "plcGaSpecLoad", "plcPLSloading", "plcGaModelPlot1", "plcDFAscores", "plcGaFeatPlot"]:  # disable for general case
			self.tbMain.tbConf.Enable(False)
			self.tbMain.tbPoints.Enable(False)
			self.tbMain.tbSymbols.Enable(False)

		if self.GetName() in ["plcPCAscore", "plcGaFeatPlot"]:
			self.tbMain.tbPoints.Enable(True)
			self.tbMain.tbSymbols.Enable(True)

		if len(self.GetName().split("plcPredPls")) > 1:
			if self.parent.prnt.prnt.parent.data["plstype"] == 1:
				self.tbMain.tbPoints.Enable(True)
				self.tbMain.tbSymbols.Enable(True)
			else:
				self.tbMain.tbSymbols.Enable(True)

		if self.GetName() in ["plcDFAscores"]:  # dfa score plots
			self.tbMain.tbConf.Enable(True)
			self.tbMain.tbPoints.Enable(True)
			self.tbMain.tbSymbols.Enable(True)
		else:
			self.tbMain.tbConf.Enable(False)

		if len(self.GetName().split("plcGaModelPlot")) > 1:  # ga-dfa score plots
			if self.prnt.prnt.prnt.splitPrnt.type in ["DFA"]:
				self.tbMain.tbConf.Enable(True)
				self.tbMain.tbPoints.Enable(True)
				self.tbMain.tbSymbols.Enable(True)
			else:
				self.tbMain.tbConf.Enable(False)
				self.tbMain.tbPoints.Enable(False)
				self.tbMain.tbSymbols.Enable(True)

		if self.GetName() in ["plcPcaLoadsV", "plcDfaLoadsV", "plcPLSloading"]:
			self.tbMain.tbLoadLabels.Enable(True)
			self.tbMain.tbLoadLabStd1.Enable(True)
			self.tbMain.tbLoadLabStd2.Enable(True)
			self.tbMain.tbLoadSymStd2.Enable(True)
			self.tbMain.tbPoints.Enable(False)
			self.tbMain.tbSymbols.Enable(False)
		else:
			self.tbMain.tbLoadLabels.Enable(False)
			self.tbMain.tbLoadLabStd1.Enable(False)
			self.tbMain.tbLoadLabStd2.Enable(False)
			self.tbMain.tbLoadSymStd2.Enable(False)


class Pca(wx.Panel):
	# principal component analysis
	def _init_coll_grsPca1_Items(self, parent):
		# generated method, don't edit

		parent.Add(self.plcPCAscore, 0, border=0, flag=wx.EXPAND)
		parent.Add(self.plcPcaLoadsV, 0, border=0, flag=wx.EXPAND)
		parent.Add(self.plcPCvar, 0, border=0, flag=wx.EXPAND)
		parent.Add(self.plcPCeigs, 0, border=0, flag=wx.EXPAND)

	def _init_coll_bxsPca1_Items(self, parent):
		# generated method, don't edit

		parent.Add(self.bxsPca2, 1, border=0, flag=wx.EXPAND)

	def _init_coll_bxsPca2_Items(self, parent):
		# generated method, don't edit

		parent.Add(self.titleBar, 0, border=0, flag=wx.EXPAND)
		parent.Add(self.grsPca1, 1, border=0, flag=wx.EXPAND)

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
		self.prnt = prnt

		self.plcPCeigs = MyPlotCanvas(id=-1, name="plcPCeigs", parent=self, pos=wx.Point(589, 283), size=wx.Size(200, 200), style=0, toolbar=self.prnt.parent.tbMain)
		self.plcPCeigs.SetToolTip("")
		self.plcPCeigs.fontSizeTitle = 10
		self.plcPCeigs.enableZoom = True
		self.plcPCeigs.fontSizeAxis = 8
		self.plcPCeigs.SetConstraints(LayoutAnchors(self.plcPCeigs, False, True, False, True))
		self.plcPCeigs.fontSizeLegend = 8

		self.plcPCvar = MyPlotCanvas(id=-1, name="plcPCvar", parent=self, pos=wx.Point(176, 283), size=wx.Size(200, 200), style=0, toolbar=self.prnt.parent.tbMain)
		self.plcPCvar.fontSizeAxis = 8
		self.plcPCvar.fontSizeTitle = 10
		self.plcPCvar.enableZoom = True
		self.plcPCvar.SetToolTip("")
		self.plcPCvar.fontSizeLegend = 8

		self.plcPCAscore = MyPlotCanvas(parent=self, id=-1, name="plcPCAscore", pos=wx.Point(0, 24), size=wx.Size(200, 200), style=0, toolbar=self.prnt.parent.tbMain)
		self.plcPCAscore.fontSizeTitle = 10
		self.plcPCAscore.fontSizeAxis = 8
		self.plcPCAscore.enableZoom = True
		self.plcPCAscore.enableLegend = True
		self.plcPCAscore.SetToolTip("")
		self.plcPCAscore.fontSizeLegend = 8

		self.plcPcaLoadsV = MyPlotCanvas(id=-1, name="plcPcaLoadsV", parent=self, pos=wx.Point(0, 24), size=wx.Size(200, 200), style=0, toolbar=self.prnt.parent.tbMain)
		self.plcPcaLoadsV.SetToolTip("")
		self.plcPcaLoadsV.fontSizeTitle = 10
		self.plcPcaLoadsV.enableZoom = True
		self.plcPcaLoadsV.fontSizeAxis = 8
		self.plcPcaLoadsV.enableLegend = True
		self.plcPcaLoadsV.fontSizeLegend = 8

		self.titleBar = TitleBar(self, id=-1, text="Principal Component Analysis", style=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self._init_sizers()

	def __init__(self, parent, id, pos, size, style, name):
		self._init_ctrls(parent)

		self.parent = parent

	def Reset(self):
		self.titleBar.spnNumPcs1.Enable(0)
		self.titleBar.spnNumPcs2.Enable(0)
		self.titleBar.spnNumPcs1.SetValue(1)
		self.titleBar.spnNumPcs2.SetValue(2)

		objects = {"plcPCeigs": ["Eigenvalues", "Principal Component", "Eigenvalue"], "plcPCvar": ["Percentage Explained Variance", "Principal Component", "Cumulative % Variance"], "plcPCAscore": ["PCA Scores", "t[1]", "t[2]"], "plcPcaLoadsV": ["PCA Loading", "w[1]", "w[2]"]}
		curve = wx.lib.plot.PolyLine([[0, 0], [1, 1]], colour="white", width=1, style=wx.TRANSPARENT)

		for each in list(objects.keys()):
			exec("self." + each + ".Draw(wx.lib.plot.PlotGraphics([curve]," + 'objects["' + each + '"][0],' + 'objects["' + each + '"][1],' + 'objects["' + each + '"][2]))')


class TitleBar(bp.ButtonPanel):
	def _init_btnpanel_ctrls(self, prnt):
		bp.ButtonPanel.__init__(self, parent=prnt, id=-1, text="Principal Component Analysis", agwStyle=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)
		self.Bind(wx.EVT_PAINT, self.OnButtonPanelPaint)

		self.btnRunPCA = bp.ButtonInfo(self, -1, wx.Bitmap(str(thisDir / "bmp" / "run.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Run PCA", longHelp="Run Principal Component Analysis")
		self.btnRunPCA.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnRunPCAButton, id=self.btnRunPCA.GetId())

		self.btnExportPcaResults = bp.ButtonInfo(self, -1, wx.Bitmap(str(thisDir / "bmp" / "export.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Export PCA Results", longHelp="Export PCA Results")
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

		self.spnNumPcs1 = wx.SpinCtrl(id=ID_NUMPCS1, initial=1, max=100, min=1, name="spnNumPcs1", parent=self, pos=wx.Point(240, 184), size=wx.Size(46, 23), style=wx.SP_ARROW_KEYS)
		self.spnNumPcs1.Enable(0)
		self.spnNumPcs1.Bind(wx.EVT_SPINCTRL, self.OnSpnNumPcs1, id=-1)

		self.spnNumPcs2 = wx.SpinCtrl(id=ID_NUMPCS2, initial=1, max=100, min=1, name="spnNumPcs2", parent=self, pos=wx.Point(240, 184), size=wx.Size(46, 23), style=wx.SP_ARROW_KEYS)
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
				f = open(saveFile, "w")
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
		# Run principal component analysis
		try:
			self.spnNumPcs1.Enable(1)
			self.spnNumPcs2.Enable(1)
			self.spnNumPcs1.SetValue(1)
			self.spnNumPcs2.SetValue(2)

			if self.cbxData.GetSelection() == 0:
				xdata = self.data["rawtrunc"]
			elif self.cbxData.GetSelection() == 1:
				xdata = self.data["proctrunc"]

			if self.cbxPreprocType.GetSelection() == 0:
				self.data["pcatype"] = "covar"
			elif self.cbxPreprocType.GetSelection() == 1:
				self.data["pcatype"] = "corr"

			if self.cbxPcaType.GetSelection() == 1:
				# run PCA using SVD
				self.data["pcscores"], self.data["pcloads"], self.data["pcpervar"], self.data["pceigs"] = chemometrics.pca_svd(xdata, self.data["pcatype"])

				self.data["pcscores"] = self.data["pcscores"][:, 0 : len(self.data["pceigs"])]

				self.data["pcloads"] = self.data["pcloads"][0 : len(self.data["pceigs"]), :]

				self.data["niporsvd"] = "svd"

			elif self.cbxPcaType.GetSelection() == 0:
				# run PCA using NIPALS
				self.data["pcscores"], self.data["pcloads"], self.data["pcpervar"], self.data["pceigs"] = chemometrics.pca_nipals(xdata, self.spnPCAnum.GetValue(), self.data["pcatype"], self.parent.parent.parent.sbMain)

				self.data["niporsvd"] = "nip"

			# Enable ctrls
			self.btnExportPcaResults.Enable(1)
			self.spnNumPcs1.SetRange(1, len(self.data["pceigs"]))
			self.spnNumPcs1.SetValue(1)
			self.spnNumPcs2.SetRange(1, len(self.data["pceigs"]))
			self.spnNumPcs2.SetValue(2)

			# check for metadata & setup limits for dfa
			if (sum(self.data["class"][:, 0]) != 0) and (self.data["class"] is not None):
				self.parent.parent.parent.plDfa.titleBar.cbxData.SetSelection(0)
				self.parent.parent.parent.plDfa.titleBar.spnDfaPcs.SetRange(2, len(self.data["pceigs"]))
				self.parent.parent.parent.plDfa.titleBar.spnDfaDfs.SetRange(1, len(scipy.unique(self.data["class"][:, 0])) - 1)

			# plot results
			self.PlotPca()

		except Exception as error:
			errorBox(self, "%s" % str(error))

	##			  raise

	def PlotPca(self):
		# Plot pca scores and loadings
		xL = "t[" + str(self.spnNumPcs1.GetValue()) + "] (" + "%.2f" % (self.data["pcpervar"][self.spnNumPcs1.GetValue()] - self.data["pcpervar"][self.spnNumPcs1.GetValue() - 1]) + "%)"

		yL = "t[" + str(self.spnNumPcs2.GetValue()) + "] (" + "%.2f" % (self.data["pcpervar"][self.spnNumPcs2.GetValue()] - self.data["pcpervar"][self.spnNumPcs2.GetValue() - 1]) + "%)"

		plotScores(self.parent.plcPCAscore, self.data["pcscores"], cl=self.data["class"][:, 0], labels=self.data["label"], validation=self.data["validation"], col1=self.spnNumPcs1.GetValue() - 1, col2=self.spnNumPcs2.GetValue() - 1, title="PCA Scores", xLabel=xL, yLabel=yL, xval=False, pconf=False, symb=self.parent.parent.parent.tbMain.tbSymbols.GetValue(), text=self.parent.parent.parent.tbMain.tbPoints.GetValue(), usecol=[], usesym=[])

		# Plot loadings
		if self.spnNumPcs1.GetValue() != self.spnNumPcs2.GetValue():
			plotLoads(self.parent.plcPcaLoadsV, scipy.transpose(self.data["pcloads"]), xaxis=self.data["indlabels"], col1=self.spnNumPcs1.GetValue() - 1, col2=self.spnNumPcs2.GetValue() - 1, title="PCA Loadings", xLabel="w[" + str(self.spnNumPcs1.GetValue()) + "]", yLabel="w[" + str(self.spnNumPcs2.GetValue()) + "]", type=self.parent.parent.parent.tbMain.GetLoadPlotIdx(), usecol=[], usesym=[])
		else:
			idx = self.spnNumPcs1.GetValue() - 1
			plotLine(self.parent.plcPcaLoadsV, self.data["pcloads"], xaxis=self.data["xaxis"], rownum=idx, tit="PCA Loadings", type="single", xLabel="Variable", yLabel="w[" + str(idx + 1) + "]", wdth=1, ledge=[])

		# Plot % variance
		plotLine(self.parent.plcPCvar, scipy.transpose(self.data["pcpervar"]), xaxis=scipy.arange(0, len(self.data["pcpervar"]))[:, nA], rownum=0, tit="Percentage Explained Variance", type="single", xLabel="Principal Component", yLabel="Cumulative % Variance", wdth=3, ledge=[])

		# Plot eigenvalues
		plotLine(self.parent.plcPCeigs, scipy.transpose(self.data["pceigs"]), xaxis=scipy.arange(1, len(self.data["pceigs"]) + 1)[:, nA], rownum=0, tit="Eigenvalues", xLabel="Principal Component", yLabel="Eigenvalue", wdth=3, type="single", ledge=[])

		# make sure ctrls enabled
		self.spnNumPcs1.Enable(True)
		self.spnNumPcs2.Enable(True)
		self.btnExportPcaResults.Enable(True)

	def OnSpnNumPcs1(self, event):
		self.PlotPca()
		SetButtonState(self.spnNumPcs1.GetValue(), self.spnNumPcs2.GetValue(), self.parent.parent.parent.tbMain)

	def OnSpnNumPcs2(self, event):
		self.PlotPca()
		SetButtonState(self.spnNumPcs1.GetValue(), self.spnNumPcs2.GetValue(), self.parent.parent.parent.tbMain)


class plotProperties(wx.Dialog):
	def _init_grsDfscores(self):
		# generated method, don't edit
		self.grsDfScores = wx.GridSizer(cols=2, hgap=4, rows=2, vgap=4)

		self._init_coll_grsDfscores_Items(self.grsDfScores)

		self.scorePnl.SetSizer(self.grsDfScores)

	def _init_coll_grsDfscores_Items(self, parent):
		# generated method, don't edit

		parent.Add(self.tbConf, 0, border=0, flag=wx.EXPAND)
		parent.Add(self.tbPoints, 0, border=0, flag=wx.EXPAND)
		parent.Add(self.tbSymbols, 0, border=0, flag=wx.EXPAND)

	def _init_grsLoadings(self):
		# generated method, don't edit
		self.grsLoadings = wx.GridSizer(cols=2, hgap=4, rows=2, vgap=4)

		self._init_coll_grsLoadings_Items(self.grsLoadings)

		self.loadPnl.SetSizer(self.grsLoadings)

	def _init_coll_grsLoadings_Items(self, parent):
		# generated method, don't edit

		parent.Add(self.tbLoadLabels, 0, border=0, flag=wx.EXPAND)
		parent.Add(self.tbLoadLabStd1, 0, border=0, flag=wx.EXPAND)
		parent.Add(self.tbLoadLabStd2, 0, border=0, flag=wx.EXPAND)
		parent.Add(self.tbLoadSymStd2, 0, border=0, flag=wx.EXPAND)

	def _init_coll_gbsPlotProps_Items(self, parent):
		# generated method, don't edit

		parent.Add(self.stTitle, (0, 0), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.txtTitle, (0, 1), border=4, flag=wx.EXPAND, span=(1, 5))
		parent.Add(wx.StaticText(self.genPnl, -1, "Axes font", style=wx.ALIGN_LEFT), (1, 0), flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.spnFontSizeAxes, (1, 1), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(wx.StaticText(self.genPnl, -1, "Title font", style=wx.ALIGN_LEFT), (1, 2), flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.spnFontSizeTitle, (1, 3), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.stXlabel, (2, 0), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.txtXlabel, (2, 1), border=4, flag=wx.EXPAND, span=(1, 5))
		parent.Add(self.stYlabel, (3, 0), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.txtYlabel, (3, 1), border=4, flag=wx.EXPAND, span=(1, 5))
		parent.Add(self.stXfrom, (4, 0), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.txtXmin, (4, 1), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.spnXmin, (4, 2), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.stXto, (4, 3), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.txtXmax, (4, 4), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.spnXmax, (4, 5), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.stYfrom, (5, 0), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.txtYmin, (5, 1), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.spnYmin, (5, 2), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.stYto, (5, 3), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.txtYmax, (5, 4), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.spnYmax, (5, 5), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.tbDrag, (6, 1), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.tbGrid, (6, 2), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.tbPointLabel, (6, 3), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.tbZoom, (6, 4), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.cbApply, (7, 0), border=4, flag=wx.EXPAND, span=(1, 1))
		parent.Add(self.btnApply, (7, 1), border=4, flag=wx.EXPAND, span=(1, 5))
		parent.Add(wx.Size(8, 8), (8, 0), flag=wx.EXPAND, span=(2, 6))

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
		self.gbsPlotProps = wx.GridBagSizer(8, 8)
		self.gbsPlotProps.SetCols(6)
		self.gbsPlotProps.SetRows(6)
		self.gbsPlotProps.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
		self.gbsPlotProps.SetMinSize(wx.Size(250, 439))
		self.gbsPlotProps.SetEmptyCellSize(wx.Size(0, 0))
		self.gbsPlotProps.SetFlexibleDirection(wx.HORIZONTAL)

		self._init_coll_gbsPlotProps_Items(self.gbsPlotProps)
		self._init_coll_gbsPlotProps_Growables(self.gbsPlotProps)

		self.genPnl.SetSizer(self.gbsPlotProps)

	def _init_plot_prop_ctrls(self, prnt):
		wx.Dialog.__init__(self, id=-1, name="", parent=prnt, pos=wx.Point(0, 0), size=wx.Size(530, 480), style=wx.MAXIMIZE_BOX | wx.DIALOG_MODAL | wx.DEFAULT_DIALOG_STYLE, title="Plot Properties")
		self.SetAutoLayout(True)

		self.foldPnl = fpb.FoldPanelBar(self, -1, wx.DefaultPosition, (525, 450), 0, fpb.FPB_EXCLUSIVE_FOLD)
		self.foldPnl.SetConstraints(LayoutAnchors(self.foldPnl, True, True, True, True))
		self.foldPnl.SetAutoLayout(True)

		icons = wx.ImageList(16, 16)
		icons.Add(wx.Bitmap(str(thisDir / "bmp" / "arrown.png"), wx.BITMAP_TYPE_PNG))
		icons.Add(wx.Bitmap(str(thisDir / "bmp" / "arrows.png"), wx.BITMAP_TYPE_PNG))

		self.genSets = self.foldPnl.AddFoldPanel("General properties", collapsed=True, foldIcons=icons)

		self.scoreSets = self.foldPnl.AddFoldPanel("Score plots", collapsed=True, foldIcons=icons)
		self.scoreSets.Enable(False)

		self.loadSets = self.foldPnl.AddFoldPanel("Loadings plots", collapsed=True, foldIcons=icons)
		self.loadSets.Enable(False)

		self.genPnl = wx.Panel(id=-1, name="genPnl", parent=self.genSets, pos=wx.Point(0, 0), size=wx.Size(20, 250), style=wx.TAB_TRAVERSAL)
		self.genPnl.SetToolTip("")

		self.scorePnl = wx.Panel(id=-1, name="scorePnl", parent=self.scoreSets, pos=wx.Point(0, 0), size=wx.Size(20, 100), style=wx.TAB_TRAVERSAL)
		self.scorePnl.SetToolTip("")

		self.loadPnl = wx.Panel(id=-1, name="loadPnl", parent=self.loadSets, pos=wx.Point(0, 0), size=wx.Size(20, 100), style=wx.TAB_TRAVERSAL)
		self.loadPnl.SetToolTip("")

		self.stTitle = wx.StaticText(id=-1, label="Title", name="stTitle", parent=self.genPnl, pos=wx.Point(0, 0), size=wx.Size(21, 24), style=0)
		self.stTitle.SetToolTip("")

		self.stYfrom = wx.StaticText(id=-1, label="Y-Axis From:", name="stYfrom", parent=self.genPnl, pos=wx.Point(0, 131), size=wx.Size(42, 24), style=0)
		self.stYfrom.SetToolTip("")

		self.stYto = wx.StaticText(id=-1, label="To:", name="stYto", parent=self.genPnl, pos=wx.Point(144, 131), size=wx.Size(40, 21), style=0)
		self.stYto.SetToolTip("")

		self.stXfrom = wx.StaticText(id=-1, label="X-Axis From:", name="stXfrom", parent=self.genPnl, pos=wx.Point(0, 103), size=wx.Size(40, 21), style=0)
		self.stXfrom.SetToolTip("")

		self.stXto = wx.StaticText(id=-1, label="To:", name="stXto", parent=self.genPnl, pos=wx.Point(144, 103), size=wx.Size(40, 21), style=0)
		self.stXto.SetToolTip("")

		self.stXlabel = wx.StaticText(id=-1, label="X label", name="stXlabel", parent=self.genPnl, pos=wx.Point(0, 53), size=wx.Size(40, 21), style=0)
		self.stXlabel.SetToolTip("")

		self.stYlabel = wx.StaticText(id=-1, label="Y label", name="stYlabel", parent=self.genPnl, pos=wx.Point(0, 78), size=wx.Size(40, 21), style=0)
		self.stYlabel.SetToolTip("")

		self.txtTitle = wx.TextCtrl(id=-1, name="txtTitle", parent=self.genPnl, pos=wx.Point(15, 0), size=wx.Size(40, 21), style=0, value="")
		self.txtTitle.SetToolTip("")
		self.txtTitle.Bind(wx.EVT_TEXT, self.OnTxtTitle)

		self.txtYlabel = wx.TextCtrl(id=-1, name="txtYlabel", parent=self.genPnl, pos=wx.Point(15, 78), size=wx.Size(40, 21), style=0, value="")
		self.txtYlabel.SetToolTip("")

		self.txtXlabel = wx.TextCtrl(id=-1, name="txtXlabel", parent=self.genPnl, pos=wx.Point(15, 53), size=wx.Size(40, 21), style=0, value="")
		self.txtXlabel.SetToolTip("")

		self.txtXmin = wx.TextCtrl(id=-1, name="txtXmin", parent=self.genPnl, pos=wx.Point(15, 103), size=wx.Size(40, 21), style=0, value="")
		self.txtXmin.SetToolTip("")

		self.spnXmin = wx.SpinButton(id=-1, name="spnXmin", parent=self.genPnl, pos=wx.Point(96, 103), size=wx.Size(15, 21), style=wx.SP_VERTICAL)
		self.spnXmin.SetToolTip("")
		self.spnXmin.Bind(wx.EVT_SPIN_DOWN, self.OnSpnXminSpinDown)
		self.spnXmin.Bind(wx.EVT_SPIN_UP, self.OnSpnXminSpinUp)
		self.spnXmin.Bind(wx.EVT_SPIN, self.OnSpnXmin)

		self.spnXmax = wx.SpinButton(id=-1, name="spnXmax", parent=self.genPnl, pos=wx.Point(240, 103), size=wx.Size(15, 21), style=wx.SP_VERTICAL)
		self.spnXmax.SetToolTip("")
		self.spnXmax.Bind(wx.EVT_SPIN_DOWN, self.OnSpnXmaxSpinDown)
		self.spnXmax.Bind(wx.EVT_SPIN_UP, self.OnSpnXmaxSpinUp)
		self.spnXmax.Bind(wx.EVT_SPIN, self.OnSpnXmax)

		self.spnYmax = wx.SpinButton(id=-1, name="spnYmax", parent=self.genPnl, pos=wx.Point(240, 131), size=wx.Size(15, 21), style=wx.SP_VERTICAL)
		self.spnYmax.SetToolTip("")
		self.spnYmax.Bind(wx.EVT_SPIN_DOWN, self.OnSpnYmaxSpinDown)
		self.spnYmax.Bind(wx.EVT_SPIN_UP, self.OnSpnYmaxSpinUp)
		self.spnYmax.Bind(wx.EVT_SPIN, self.OnSpnYmax)

		self.spnYmin = wx.SpinButton(id=-1, name="spnYmin", parent=self.genPnl, pos=wx.Point(96, 131), size=wx.Size(15, 21), style=wx.SP_VERTICAL)
		self.spnYmin.SetToolTip("")
		self.spnYmin.Bind(wx.EVT_SPIN_DOWN, self.OnSpnYminSpinDown)
		self.spnYmin.Bind(wx.EVT_SPIN_UP, self.OnSpnYminSpinUp)
		self.spnYmin.Bind(wx.EVT_SPIN, self.OnSpnYmin)

		self.txtXmax = wx.TextCtrl(id=-1, name="txtXmax", parent=self.genPnl, pos=wx.Point(192, 103), size=wx.Size(40, 21), style=0, value="")
		self.txtXmax.SetToolTip("")

		self.txtYmax = wx.TextCtrl(id=-1, name="txtYmax", parent=self.genPnl, pos=wx.Point(192, 131), size=wx.Size(40, 21), style=0, value="")
		self.txtYmax.SetToolTip("")

		self.txtYmin = wx.TextCtrl(id=-1, name="txtYmin", parent=self.genPnl, pos=wx.Point(15, 131), size=wx.Size(40, 21), style=0, value="")
		self.txtYmin.SetToolTip("")

		self.stFont = wx.StaticText(id=-1, label="Font size axes and title (pt)", name="stFont", parent=self.genPnl, pos=wx.Point(0, 28), size=wx.Size(40, 21), style=0)
		self.stFont.SetToolTip("")

		self.spnFontSizeAxes = wx.SpinCtrl(id=-1, initial=8, max=76, min=4, name="spnFontSizeAxes", parent=self.genPnl, pos=wx.Point(15, 28), size=wx.Size(40, 21), style=wx.SP_ARROW_KEYS)
		self.spnFontSizeAxes.SetToolTip("")
		self.spnFontSizeAxes.SetValue(8)
		self.spnFontSizeAxes.SetRange(4, 76)
		self.spnFontSizeAxes.Bind(wx.EVT_SPIN, self.OnSpnFontSizeAxes)

		self.spnFontSizeTitle = wx.SpinCtrl(id=-1, initial=8, max=76, min=4, name="spnFontSizeTitle", parent=self.genPnl, pos=wx.Point(15, 28), size=wx.Size(40, 21), style=wx.SP_ARROW_KEYS)
		self.spnFontSizeTitle.SetToolTip("")
		self.spnFontSizeTitle.SetValue(8)
		self.spnFontSizeTitle.SetRange(4, 76)
		self.spnFontSizeTitle.Bind(wx.EVT_SPIN, self.OnSpnFontSizeTitle)

		self.tbGrid = wx.lib.buttons.GenToggleButton(id=-1, label="Grid", name="tbGrid", parent=self.genPnl, pos=wx.Point(248, 48), size=wx.Size(40, 21), style=0)
		self.tbGrid.SetValue(False)
		self.tbGrid.SetToolTip("")
		self.tbGrid.Bind(wx.EVT_BUTTON, self.OnTbGridButton)

		self.tbDrag = wx.lib.buttons.GenToggleButton(id=-1, label="Drag", name="tbDrag", parent=self.genPnl, pos=wx.Point(248, 48), size=wx.Size(40, 21), style=0)
		self.tbDrag.SetValue(False)
		self.tbDrag.SetToolTip("")
		self.tbDrag.Bind(wx.EVT_BUTTON, self.OnTbDragButton)

		self.tbPointLabel = wx.lib.buttons.GenToggleButton(id=-1, label="Points", name="tbPointLabel", parent=self.genPnl, pos=wx.Point(248, 48), size=wx.Size(40, 21), style=0)
		self.tbPointLabel.SetValue(False)
		self.tbPointLabel.SetToolTip("")
		self.tbPointLabel.Bind(wx.EVT_BUTTON, self.OnTbPointLabelButton)

		self.tbZoom = wx.lib.buttons.GenToggleButton(id=-1, label="Zoom", name="tbZoom", parent=self.genPnl, pos=wx.Point(248, 48), size=wx.Size(40, 21), style=0)
		self.tbZoom.SetValue(True)
		self.tbZoom.SetToolTip("")
		self.tbZoom.Bind(wx.EVT_BUTTON, self.OnTbZoomButton)

		self.cbApply = wx.CheckBox(id=-1, label="Immediate Apply", name="cbApply", parent=self.genPnl, pos=wx.Point(48, 96), size=wx.Size(70, 13), style=0)

		self.btnApply = wx.Button(id=-1, label="Apply & Close", name="btnApply", parent=self.genPnl, pos=wx.Point(192, 136), size=wx.Size(40, 21), style=0)
		self.btnApply.Bind(wx.EVT_BUTTON, self.OnBtnApply)

		self.tbConf = wx.lib.buttons.GenToggleButton(id=-1, label="95% Confidence Circles", name="tbConf", parent=self.scorePnl, pos=wx.Point(248, 48), size=wx.Size(40, 21))
		self.tbConf.SetValue(True)
		self.tbConf.SetToolTip("")
		self.tbConf.Bind(wx.EVT_BUTTON, self.OnTbConfButton)

		self.tbPoints = wx.lib.buttons.GenToggleButton(id=-1, label="Labels", name="tbPoints", parent=self.scorePnl, pos=wx.Point(248, 48), size=wx.Size(40, 21))
		self.tbPoints.SetValue(True)
		self.tbPoints.SetToolTip("")
		self.tbPoints.Bind(wx.EVT_BUTTON, self.OnTbPointsButton)

		self.tbSymbols = wx.lib.buttons.GenToggleButton(id=-1, label="Symbols", name="tbSymbols", parent=self.scorePnl, pos=wx.Point(248, 48), size=wx.Size(40, 21))
		self.tbSymbols.SetValue(False)
		self.tbSymbols.SetToolTip("")
		self.tbSymbols.Bind(wx.EVT_BUTTON, self.OnTbSymbolsButton)

		self.tbLoadLabels = wx.Button(id=-1, label="Labels", name="tbLoadLabels", parent=self.loadPnl, pos=wx.Point(248, 48), size=wx.Size(40, 21))
		self.tbLoadLabels.SetToolTip("")
		self.tbLoadLabels.Bind(wx.EVT_BUTTON, self.OnTbLoadLabelsButton)

		self.tbLoadLabStd1 = wx.Button(id=-1, label="Labels & 1 Std", name="tbLoadLabStd1", parent=self.loadPnl, pos=wx.Point(248, 48), size=wx.Size(40, 21))
		self.tbLoadLabStd1.SetToolTip("")
		self.tbLoadLabStd1.Bind(wx.EVT_BUTTON, self.OnTbLoadLabStd1Button)

		self.tbLoadLabStd2 = wx.Button(id=-1, label="Labels & 2 Std", name="tbLoadLabStd2", parent=self.loadPnl, pos=wx.Point(248, 48), size=wx.Size(40, 21))
		self.tbLoadLabStd2.SetToolTip("")
		self.tbLoadLabStd2.Bind(wx.EVT_BUTTON, self.OnTbLoadLabStd2Button)

		self.tbLoadSymStd2 = wx.Button(id=-1, label="Symbols & 2 Std", name="tbLoadSymStd2", parent=self.loadPnl, pos=wx.Point(248, 48), size=wx.Size(40, 21))
		self.tbLoadSymStd2.SetToolTip("")
		self.tbLoadSymStd2.Bind(wx.EVT_BUTTON, self.OnTbLoadSymStd2Button)

		self.foldPnl.AddFoldPanelWindow(self.genSets, self.genPnl, fpb.FPB_ALIGN_WIDTH)
		self.foldPnl.AddFoldPanelWindow(self.scoreSets, self.scorePnl, fpb.FPB_ALIGN_WIDTH)
		self.foldPnl.AddFoldPanelWindow(self.loadSets, self.loadPnl, fpb.FPB_ALIGN_WIDTH)

		##		  self.btnFont = wx.Button(id=-1, label='Font',
		##				name='btnFont', parent=self.genSets, pos=wx.Point(192, 136),
		##				size=wx.Size(40, 21), style=0)
		##		  self.btnFont.Bind(wx.EVT_BUTTON, self.OnBtnFont)

		self._init_plot_prop_sizers()

		self._init_grsDfscores()

		self._init_grsLoadings()

	def __init__(self, parent):
		self._init_plot_prop_ctrls(parent)

		self.foldPnl.Expand(self.genSets)
		self.foldPnl.Collapse(self.scoreSets)
		self.foldPnl.Collapse(self.loadSets)

		self.graph = parent.last_draw[0]
		self.canvas = parent

		self.minXrange = parent.GetXCurrentRange()[0]
		self.maxXrange = parent.GetXCurrentRange()[1]
		self.minYrange = parent.GetYCurrentRange()[0]
		self.maxYrange = parent.GetYCurrentRange()[1]

		self.Increment = (self.maxXrange - self.minXrange) / 100

		self.txtXmin.SetValue("%.3f" % self.minXrange)
		self.txtXmax.SetValue("%.3f" % self.maxXrange)
		self.txtYmin.SetValue("%.3f" % self.minYrange)
		self.txtYmax.SetValue("%.3f" % self.maxYrange)

		self.txtTitle.SetValue(self.graph.getTitle())
		self.txtXlabel.SetValue(self.graph.getXLabel())
		self.txtYlabel.SetValue(self.graph.getYLabel())

		self.spnFontSizeAxes.SetValue(parent.GetFontSizeAxis())
		self.spnFontSizeTitle.SetValue(parent.GetFontSizeTitle())

		if self.canvas.GetEnableGrid() is True:
			self.tbGrid.SetValue(1)
		if self.canvas.GetEnableZoom() is True:
			self.tbZoom.SetValue(1)
		if self.canvas.GetEnableDrag() is True:
			self.tbDrag.SetValue(1)
		if self.canvas.GetEnablePointLabel() is True:
			self.tbPointLabel.SetValue(1)

	def OnTbLoadLabelsButton(self, event):
		# plot loadings
		self.doPlot(loadType=0)

	def OnTbLoadLabStd1Button(self, event):
		# plot loadings
		self.doPlot(loadType=1)

	def OnTbLoadLabStd2Button(self, event):
		# plot loadings
		self.doPlot(loadType=2)

	def OnTbLoadSymStd2Button(self, event):
		# plot loadings
		self.doPlot(loadType=3)

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

	def doPlot(self, loadType=0):
		if self.canvas.GetName() in ["plcDFAscores"]:
			plotScores(self.canvas, self.canvas.prnt.titleBar.data["dfscores"], cl=self.canvas.prnt.titleBar.data["class"][:, 0], labels=self.canvas.prnt.titleBar.data["label"], validation=self.canvas.prnt.titleBar.data["validation"], col1=self.canvas.prnt.titleBar.spnDfaScore1.GetValue() - 1, col2=self.canvas.prnt.titleBar.spnDfaScore2.GetValue() - 1, title=self.graph.title, xLabel=self.graph.xLabel, yLabel=self.graph.yLabel, xval=self.canvas.prnt.titleBar.cbDfaXval.GetValue(), text=self.tbPoints.GetValue(), pconf=self.tbConf.GetValue(), symb=self.tbSymbols.GetValue(), usecol=[], usesym=[])

		elif self.canvas.GetName() in ["plcPCAscore"]:
			plotScores(self.canvas, self.canvas.prnt.titleBar.data["pcscores"], cl=self.canvas.prnt.titleBar.data["class"][:, 0], labels=self.canvas.prnt.titleBar.data["label"], validation=self.canvas.prnt.titleBar.data["validation"], col1=self.canvas.prnt.titleBar.spnNumPcs1.GetValue() - 1, col2=self.canvas.prnt.titleBar.spnNumPcs2.GetValue() - 1, title=self.graph.title, xLabel=self.graph.xLabel, yLabel=self.graph.yLabel, xval=False, text=self.tbPoints.GetValue(), pconf=False, symb=self.tbSymbols.GetValue(), usecol=[], usesym=[])

		elif len(self.GetName().split("plcPredPls")) > 1:
			self.canvas = PlotPlsModel(self.canvas, model="full", tbar=self.canvas.prnt.prnt.prnt.parent.tbMain, cL=self.canvas.prnt.titleBar.data["class"][:, nA], label=self.canvas.prnt.titleBar.data["label"], scores=self.canvas.prnt.titleBar.data["plst"], predictions=self.canvas.prnt.titleBar.data["plspred"], validation=np.array(self.canvas.prnt.titleBar.data["validation"], "i")[:, nA], RMSEPT=self.canvas.prnt.titleBar.data["RMSEPT"], factors=self.canvas.prnt.titleBar.data["plsfactors"], type=self.canvas.prnt.titleBar.data["plstype"], col1=self.canvas.prnt.titleBar.spnPLSfactor1.GetValue() - 1, col2=self.canvas.prnt.titleBar.spnPLSfactor2.GetValue() - 1, symbols=self.tbSymbols.GetValue(), usetxt=self.tbPoints.GetValue(), plScL=self.canvas.prnt.titleBar.data["pls_class"])

		elif self.canvas.GetName() in ["plcGaFeatPlot"]:
			plotScores(self.canvas, self.canvas.prnt.prnt.splitPrnt.titleBar.data["gavarcoords"], cl=self.canvas.prnt.prnt.splitPrnt.titleBar.data["class"][:, 0], labels=self.canvas.prnt.prnt.splitPrnt.titleBar.data["label"], validation=self.canvas.prnt.prnt.splitPrnt.titleBar.data["validation"], col1=0, col2=1, title=self.graph.title, xLabel=self.graph.xLabel, yLabel=self.graph.yLabel, xval=True, text=self.tbPoints.GetValue(), pconf=False, symb=self.tbSymbols.GetValue(), usecol=[], usesym=[])

		elif len(self.GetName().split("plcGaModelPlot")) > 1:
			if self.canvas.prnt.prnt.splitPrnt.type in ["DFA"]:
				plotScores(self.canvas, self.canvas.prnt.prnt.splitPrnt.titleBar.data["gadfadfscores"], cl=self.canvas.prnt.prnt.splitPrnt.titleBar.data["class"][:, 0], labels=self.canvas.prnt.prnt.splitPrnt.titleBar.data["label"], validation=self.canvas.prnt.prnt.splitPrnt.titleBar.data["validation"], col1=self.canvas.prnt.prnt.splitPrnt.titleBar.spnGaScoreFrom.GetValue() - 1, col2=self.canvas.prnt.prnt.splitPrnt.titleBar.spnGaScoreTo.GetValue() - 1, title=self.graph.title, xLabel=self.graph.xLabel, yLabel=self.graph.yLabel, xval=True, text=self.tbPoints.GetValue(), pconf=self.tbConf.GetValue(), symb=self.tbSymbols.GetValue(), usecol=[], usesym=[])
			else:
				self.canvas = PlotPlsModel(self.canvas, model="ga", tbar=self.canvas.prnt.prnt.splitPrnt.prnt.parent.tbMain, cL=self.canvas.prnt.prnt.splitPrnt.titleBar.data["class"][:, 0], scores=None, label=self.canvas.prnt.prnt.splitPrnt.titleBar.data["label"], predictions=self.canvas.prnt.prnt.splitPrnt.titleBar.data["gaplsscores"], validation=self.canvas.prnt.prnt.splitPrnt.titleBar.data["validation"], RMSEPT=self.canvas.prnt.prnt.splitPrnt.titleBar.data["gaplsrmsept"], factors=self.canvas.prnt.prnt.splitPrnt.titleBar.data["gaplsfactors"], type=0, col1=self.canvas.prnt.prnt.splitPrnt.titleBar.spnGaScoreFrom.GetValue() - 1, col2=self.canvas.prnt.prnt.splitPrnt.titleBar.spnGaScoreTo.GetValue() - 1, symbols=self.tbSymbols.GetValue(), usetxt=self.tbPoints.GetValue(), usecol=[], usesym=[], plScL=self.canvas.prnt.prnt.splitPrnt.titleBar.data["pls_class"])

		elif self.canvas.GetName() in ["plcPcaLoadsV"]:
			plotLoads(self.canvas, scipy.transpose(self.canvas.prnt.titleBar.data["pcloads"]), xaxis=self.canvas.prnt.titleBar.data["indlabels"], col1=self.canvas.prnt.titleBar.spnNumPcs1.GetValue() - 1, col2=self.canvas.prnt.titleBar.spnNumPcs2.GetValue() - 1, title=self.graph.title, xLabel=self.graph.xLabel, yLabel=self.graph.yLabel, type=loadType, usecol=[], usesym=[])

		elif self.canvas.GetName() in ["plcPLSloading"]:
			plotLoads(self.canvas, self.canvas.prnt.titleBar.data["plsloads"], xaxis=self.canvas.prnt.titleBar.data["indlabels"], col1=self.canvas.prnt.titleBar.spnPLSfactor1.GetValue() - 1, col2=self.canvas.prnt.titleBar.spnPLSfactor2.GetValue() - 1, title=self.graph.title, xLabel=self.graph.xLabel, yLabel=self.graph.yLabel, type=loadType, usecol=[], usesym=[])

		elif self.canvas.GetName() in ["plcDfaLoadsV"]:
			plotLoads(self.canvas, self.canvas.prnt.titleBar.data["dfloads"], xaxis=self.canvas.prnt.titleBar.data["indlabels"], col1=self.canvas.prnt.titleBar.spnDfaScore1.GetValue() - 1, col2=self.canvas.prnt.titleBar.spnDfaScore2.GetValue() - 1, title=self.graph.title, xLabel=self.graph.xLabel, yLabel=self.graph.yLabel, type=loadType, usecol=[], usesym=[])

		elif self.canvas.GetName() in ["plcGaSpecLoad"]:
			if self.canvas.prnt.prnt.prnt.splitPrnt.type in ["DFA"]:
				labels = []
				for each in self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["gacurrentchrom"]:
					labels.append(self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["indlabels"][int(each)])
				plotLoads(self.canvas, self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["gadfadfaloads"], xaxis=labels, title=self.graph.title, xLabel=self.graph.xLabel, yLabel=self.graph.yLabel, type=loadType, usecol=[], usesym=[])

		elif self.canvas.GetName() in ["plcGaSpecLoad"]:
			if self.canvas.prnt.prnt.splitPrnt.type in ["PLS"]:
				labels = []
				for each in self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["gacurrentchrom"]:
					labels.append(self.canvas.prnt.prnt.prnt.splitPrnt.titleBar.data["indlabels"][int(each)])
				plotLoads(self.canvas, self.canvas.prnt.prnt.splitPrnt.titleBar.data["gaplsplsloads"], xaxis=labels, title=self.graph.title, xLabel=self.graph.xLabel, yLabel=self.graph.yLabel, type=loadType, usecol=[], usesym=[])

	##	  def OnBtnFont(self, event):
	##		  data = wx.FontData()
	##		  data.EnableEffects(True)
	##		  data.SetColour(self.canvas.GetForegroundColour())
	##		  data.SetInitialFont(self.canvas.GetFont())
	##
	##		  dlg = wx.FontDialog(self, data)
	##		  if dlg.ShowModal() == wx.ID_OK:
	##			  self.font = dlg.GetFontData().GetChosenFont()
	##			  self.colour = dlg.GetFontData().GetColour()
	##
	##		  if self.cbApply.GetValue() is True:
	##			  self.canvas.SetFont(self.font)
	##			  self.canvas.SetForegroundColour(self.colour)
	##			  self.canvas.Redraw()

	def OnTxtTitle(self, event):
		if self.cbApply.GetValue() is True:
			self.graph.setTitle(self.txtTitle.GetValue())
			self.canvas.Redraw()

	def OnTbGridButton(self, event):
		self.canvas.SetEnableGrid(self.tbGrid.GetValue())

	def OnTbDragButton(self, event):
		self.canvas.SetEnableDrag(self.tbDrag.GetValue())

	def OnTbPointLabelButton(self, event):
		self.canvas.SetEnablePointLabel(self.tbPointLabel.GetValue())

	def OnTbZoomButton(self, event):
		self.canvas.enableZoom = self.tbZoom.GetValue()

	def OnBtnApply(self, event):
		self.canvas.fontSizeAxis = self.spnFontSizeAxes.GetValue()
		self.canvas.fontSizeTitle = self.spnFontSizeTitle.GetValue()

		self.graph.setTitle(self.txtTitle.GetValue())
		self.graph.setXLabel(self.txtXlabel.GetValue())
		self.graph.setYLabel(self.txtYlabel.GetValue())

		if (float(self.txtXmin.GetValue()) < float(self.txtXmax.GetValue())) and (float(self.txtYmin.GetValue()) < float(self.txtYmax.GetValue())) is True:
			self.canvas.last_draw = [self.canvas.last_draw[0], np.array([float(self.txtXmin.GetValue()), float(self.txtXmax.GetValue())]), np.array([float(self.txtYmin.GetValue()), float(self.txtYmax.GetValue())])]

		self.canvas.Redraw()

		self.Close()

	def OnSpnFontSizeAxes(self, event):
		if self.cbApply.GetValue() is True:
			self.canvas.fontSizeAxis = self.spnFontSizeAxes.GetValue()
			self.canvas.Redraw()

	def OnSpnFontSizeTitle(self, event):
		if self.cbApply.GetValue() is True:
			self.canvas.fontSizeTitle = self.spnFontSizeTitle.GetValue()
			self.canvas.Redraw()

	def resizeAxes(self):
		if (float(self.txtXmin.GetValue()) < float(self.txtXmax.GetValue())) and (float(self.txtYmin.GetValue()) < float(self.txtYmax.GetValue())) and (self.cbApply.GetValue() is True) is True:
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
