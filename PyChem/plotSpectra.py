# -----------------------------------------------------------------------------
# Name:		   plotSpectra.py
# Purpose:
#
# Author:	   Roger Jarvis
#
# Created:	   2007/05/22
# RCS-ID:	   $Id$
# Copyright:   (c) 2007
# Licence:	   GNU General Public Licence
# -----------------------------------------------------------------------------
# Boa:FramePanel:plotSpectra

import copy
import os
import string

import scipy
import wx
import wx.lib.agw.buttonpanel as bp
import wx.lib.agw.foldpanelbar as fpb
import wx.lib.plot
from scipy import newaxis as nA
from wx.lib.anchors import LayoutAnchors

from .mva import process
from .Pca import MyPlotCanvas, plotLine

[IDPLOTSPEC] = [wx.NewIdRef() for _init_ctrls in range(1)]


def errorBox(window, error):
	dlg = wx.MessageDialog(window, "".join(("The following error occured:\n\n", error)), "Error!", wx.OK | wx.ICON_ERROR)
	try:
		dlg.ShowModal()
	finally:
		dlg.Destroy()


def GridRowDel(grid, data):
	# delete user defined variable row from grdIndLabels
	try:
		row = grid.GetSelectedRows()[0]
		lab = grid.GetRowLabelValue(row)
		if len(lab.split("U")) > 1:
			# count user def vars
			count = 1
			for r in range(1, grid.GetNumberRows()):
				if len(grid.GetRowLabelValue(r).split("U")) > 1:
					count += 1
				else:
					break
			data["raw"] = scipy.delete(data["raw"], row - 2, 1)
			data["proc"] = scipy.delete(data["proc"], row - 2, 1)
			grid.DeleteRows(row, 1)
			# renumber rows
			ncount = 1
			for r in range(1, count - 1):
				grid.SetRowLabelValue(r, "U" + str(ncount))
				ncount += 1
			ncount = 1
			for r in range(count - 1, grid.GetNumberRows()):
				grid.SetRowLabelValue(r, str(ncount))
				ncount += 1
		else:
			pass
	except:
		pass


class PeakCalculations(wx.Dialog):
	def _init_pc_sizers(self):
		# generated method, don't edit
		self.grsPeakCalcs = wx.GridSizer(cols=2, hgap=2, rows=4, vgap=2)

		self._init_coll_grsPeakCalcs_Items(self.grsPeakCalcs)

		self.SetSizer(self.grsPeakCalcs)

	def _init_coll_grsPeakCalcs_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.btnIntensity, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.btnIntensityFit, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.btnAreaAxis, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.btnAreaFitAxis, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.btnAreaBaseline, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.btnAreaFitBaseline, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.btnCalculate, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.btnCancel, 0, border=0, flag=wx.EXPAND)

	def _init_pc_ctrls(self, prnt):
		# generated method, don't edit
		wx.Dialog.__init__(self, id=-1, name="", parent=prnt, pos=wx.Point(471, 248), size=wx.Size(264, 165), style=wx.DIALOG_MODAL | wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.CAPTION | wx.MAXIMIZE_BOX, title="Peak Calculations")
		self.SetClientSize(wx.Size(258, 133))
		self.Center(wx.BOTH)

		self.btnIntensity = wx.lib.buttons.GenBitmapToggleButton(bitmap=wx.Bitmap(os.path.join("bmp", "peakimax.png")), id=-1, name="btnIntensity", parent=self, pos=wx.Point(0, 0), size=wx.Size(128, 31), style=0)
		self.btnIntensity.SetToggle(True)
		self.btnIntensity.SetLabel("")
		self.btnIntensity.SetToolTip("Calculate the maximum intensity in the selected region")

		self.btnAreaAxis = wx.lib.buttons.GenBitmapToggleButton(bitmap=wx.Bitmap(os.path.join("bmp", "peakareaaxis.png")), id=-1, name="btnAreaAxis", parent=self, pos=wx.Point(130, 0), size=wx.Size(128, 31), style=0)
		self.btnAreaAxis.SetToggle(True)
		self.btnAreaAxis.SetLabel("")
		self.btnAreaAxis.SetToolTip("Calculate the total area to the axis")

		self.btnAreaBaseline = wx.lib.buttons.GenBitmapToggleButton(bitmap=wx.Bitmap(os.path.join("bmp", "peakareabase.png")), id=-1, name="btnAreaBaseline", parent=self, pos=wx.Point(0, 33), size=wx.Size(128, 31), style=0)
		self.btnAreaBaseline.SetToggle(True)
		self.btnAreaBaseline.SetLabel("")
		self.btnAreaBaseline.SetToolTip("Calculate the total area to the baseline")

		self.btnAreaFitAxis = wx.lib.buttons.GenBitmapToggleButton(bitmap=wx.Bitmap(os.path.join("bmp", "peakcfitareaaxis.png")), id=-1, name="btnAreaFitAxis", parent=self, pos=wx.Point(130, 33), size=wx.Size(128, 31), style=0)
		self.btnAreaFitAxis.SetToggle(True)
		self.btnAreaFitAxis.SetLabel("")
		self.btnAreaFitAxis.SetToolTip("Curvefit peak and calculate area to the X-axis")

		self.btnAreaFitBaseline = wx.lib.buttons.GenBitmapToggleButton(bitmap=wx.Bitmap(os.path.join("bmp", "peakcfitareabase.png")), id=-1, name="btnAreaFitBaseline", parent=self, pos=wx.Point(0, 66), size=wx.Size(128, 31), style=0)
		self.btnAreaFitBaseline.SetToggle(True)
		self.btnAreaFitBaseline.SetLabel("")
		self.btnAreaFitBaseline.SetToolTip("Curvefit peak and calculate area to baseline")

		self.btnIntensityFit = wx.lib.buttons.GenBitmapToggleButton(bitmap=wx.Bitmap(os.path.join("bmp", "peakifitmax.png")), id=-1, name="btnSpare", parent=self, pos=wx.Point(130, 66), size=wx.Size(128, 31), style=0)
		self.btnIntensityFit.SetToggle(True)
		self.btnIntensityFit.SetLabel("")
		self.btnIntensityFit.SetToolTip("Curvefit peak and find maximum intensity")

		self.btnCalculate = wx.Button(id=-1, label="Calculate", name="btnCalculate", parent=self, pos=wx.Point(0, 99), size=wx.Size(128, 31), style=0)
		self.btnCalculate.SetToolTip("")
		self.btnCalculate.Bind(wx.EVT_BUTTON, self.OnBtnCalculateButton, id=self.btnCalculate.GetId())

		self.btnCancel = wx.Button(id=-1, label="Cancel", name="btnCancel", parent=self, pos=wx.Point(130, 99), size=wx.Size(128, 31), style=0)
		self.btnCancel.SetToolTip("")
		self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancelButton, id=self.btnCancel.GetId())

		self._init_pc_sizers()

	def __init__(self, parent, xlim, data, canvas):
		self._init_pc_ctrls(parent)

		self._xlim = xlim
		self._data = data
		self._canvas = canvas
		self._prnt = parent

	def GetXdata(self, start=None):
		# use raw or processed data
		if self._prnt.titleBar.cbxData.GetSelection() == 0:
			xdata = self._data["raw"][:, np.array(self._data["variableidx"])]
			label = "_RAW"
		else:
			xdata = self._data["proc"][:, np.array(self._data["variableidx"])]
			label = "_PROC"
		return xdata, label

	def UpdateVars(self, grid, countpos, fix, x):
		# update ind var labels
		grid.InsertRows(pos=countpos, numRows=1, updateLabels=True)
		# set checkbox in first column
		grid.SetCellEditor(countpos, 0, wx.grid.GridCellBoolEditor())
		grid.SetCellRenderer(countpos, 0, wx.grid.GridCellBoolRenderer())
		grid.SetCellAlignment(countpos, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
		grid.SetCellValue(countpos, 0, "0")
		# set user defined variable row label
		grid.SetRowLabelValue(countpos, "U" + str(countpos))
		# renumber other rows
		for r in range(countpos + 1, grid.GetNumberRows()):
			grid.SetRowLabelValue(r, str(r - countpos))
		# add label
		for c in range(1, grid.GetNumberCols()):
			grid.SetCellValue(countpos, c, fix[0] + "%.2f" % scipy.mean(x) + fix[1])
		# make cell read only in col 1 for referencing
		grid.SetReadOnly(countpos, 1)
		grid.SetCellBackgroundColour(countpos, 1, wx.LIGHT_GREY)

	def InsertVariable(self, pos, var):
		# add new column to raw and proc data
		self._data["raw"] = scipy.concatenate((self._data["raw"][:, 0:pos], var, self._data["raw"][:, pos : self._data["raw"].shape[1]]), 1)
		self._data["proc"] = scipy.concatenate((self._data["proc"][:, 0:pos], var, self._data["proc"][:, pos : self._data["proc"].shape[1]]), 1)

	def OnBtnCalculateButton(self, event):
		# find bin range
		xaxis = self._data["xaxis"][:, 0]
		mnx = min([self._xlim[0], self._xlim[1]])
		mxx = max([self._xlim[0], self._xlim[1]])

		# fix to deal with x-axis orientation
		if xaxis[0] < xaxis[len(xaxis) - 1]:
			bin1 = len(xaxis[xaxis <= mnx])
			bin2 = len(xaxis[xaxis <= mxx])
		else:
			bin1 = len(xaxis[xaxis >= mnx])
			bin2 = len(xaxis[xaxis >= mxx])

		# bin range
		rng = scipy.arange(min([bin1, bin2]), max([bin1, bin2]))
		x = xaxis[rng]

		# replot vertical lines to fit bin
		graphics, xlim, ylim = self._canvas.last_draw
		graphics.objects = [graphics.objects[0]]
		graphics.objects.append(wx.lib.plot.PolyLine([[x[0], ylim[0]], [x[0], ylim[1]]], colour="red"))
		graphics.objects.append(wx.lib.plot.PolyLine([[x[len(x) - 1], ylim[0]], [x[len(x) - 1], ylim[1]]], colour="red"))
		self._canvas.Draw(graphics)  # ,xAxis=tuple(xlim),yAxis=tuple(ylim))
		# get position of most recent user defined variable to be have been added
		grid = self._prnt.parent.parent.plExpset.grdIndLabels
		countpos = 0  # count number of user defined variables
		for r in range(1, grid.GetNumberRows()):
			countpos += 1
			if len(grid.GetRowLabelValue(r).split("U")) == 1:
				break
		# get xdata for calcs
		xdata, label = self.GetXdata(start=countpos - 1)
		# do calculations
		if self.btnIntensity.GetValue():  # max intensity in range
			intensity = xdata[:, rng].max(axis=1)[:, nA]
			# update variable labels grid
			self.UpdateVars(grid, countpos, ["I_", label], x)
			# add new column to raw and proc data
			self.InsertVariable(countpos, intensity)
			countpos += 1
		if self.btnIntensityFit.GetValue():  # max intensity based on curve fit
			intensity_fit = self.CurveFit(xdata, x, rng, type=0)
			# update variable labels grid
			self.UpdateVars(grid, countpos, ["IF_", label], x)
			# add new column to raw and proc data
			self.InsertVariable(countpos, intensity_fit)
			countpos += 1
		if self.btnAreaAxis.GetValue():  # total area in range
			area_axis = scipy.sum(xdata[:, rng], axis=1)[:, nA]
			# update variable labels grid
			self.UpdateVars(grid, countpos, ["AA_", label], x)
			# add new column to raw and proc data
			self.InsertVariable(countpos, area_axis)
			countpos += 1
		if self.btnAreaFitAxis.GetValue():  # total area in range with curve fit
			area_fit_axis = self.CurveFit(xdata, x, rng, type=1)
			# update variable labels grid
			self.UpdateVars(grid, countpos, ["AFA_", label], x)
			# add new column to raw and proc data
			self.InsertVariable(countpos, area_fit_axis)
			countpos += 1
		if self.btnAreaBaseline.GetValue():  # total area in to base of peak
			area_baseline = self.CurveFit(xdata, x, rng, type=3)
			# update variable labels grid
			self.UpdateVars(grid, countpos, ["AB_", label], x)
			# add new column to raw and proc data
			self.InsertVariable(countpos, area_baseline)
			countpos += 1
		if self.btnAreaFitBaseline.GetValue():  # total area in to base of peak with curve fit
			area_fit_baseline = self.CurveFit(xdata, x, rng, type=2)
			# update variable labels grid
			self.UpdateVars(grid, countpos, ["AFB_", label], x)
			# add new column to raw and proc data
			self.InsertVariable(countpos, area_fit_baseline)
		# update experiment setup
		self._prnt.parent.parent.GetExperimentDetails(case=1)
		# destroy dialog
		self.Destroy()

	def OnBtnCancelButton(self, event):
		self.Destroy()

	def CurveFit(self, xdata, x, rng, type=1):
		# fit 2nd order polynomial
		area = []
		favg = scipy.zeros((len(x),))
		for r in range(xdata.shape[0]):
			p = scipy.polyfit(x, xdata[r, rng], 2)
			f = scipy.polyval(p, x)
			if type > 0:
				if type == 3:
					f = xdata[r, rng]
				favg = favg + f
				area.append(scipy.sum(f))
				if type > 1:  # fit straight line
					p1 = scipy.polyfit(x, xdata[r, rng], 1)
					f1 = scipy.polyval(p1, x)
					area[len(area) - 1] = scipy.sum(f - f1)
			else:
				area.append(max(f))

		area = np.array(area)[:, nA]
		if type > 0:
			favg = favg / float(r + 1)  # avg curve fit for plotting
			graphics, xlim, ylim = self._canvas.last_draw
			if type < 3:
				c = "blue"
			elif type == 3:
				c = "green"
			graphics.objects.extend([wx.lib.plot.PolyLine(scipy.concatenate((x[:, nA], favg[:, nA]), 1), colour=c)])
			if type > 1:
				f1avg = scipy.polyfit([x[0], x[len(x) - 1]], [favg[0], favg[len(favg) - 1]], 1)
				f1avg = scipy.polyval(f1avg, x)
				graphics.objects.extend([wx.lib.plot.PolyLine(scipy.concatenate((x[:, nA], f1avg[:, nA]), 1), colour=c)])
			self._canvas.Draw(graphics)  # ,xAxis=tuple(xlim),yAxis=tuple(ylim))

		return area


class plotSpectra(wx.Panel):
	def _init_coll_bxsPspc1_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.bxsPspc2, 1, border=0, flag=wx.EXPAND)

	def _init_coll_bxsPspc2_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.titleBar, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.Splitter, 1, border=0, flag=wx.EXPAND)

	def _init_sizers(self):
		# generated method, don't edit
		self.bxsPspc1 = wx.BoxSizer(orient=wx.HORIZONTAL)

		self.bxsPspc2 = wx.BoxSizer(orient=wx.VERTICAL)

		self._init_coll_bxsPspc1_Items(self.bxsPspc1)
		self._init_coll_bxsPspc2_Items(self.bxsPspc2)

		self.SetSizer(self.bxsPspc1)

	def _init_ctrls(self, prnt):
		# generated method, don't edit
		wx.Panel.__init__(self, id=-1, name="plotSpectra", parent=prnt, pos=wx.Point(88, 116), size=wx.Size(757, 538), style=wx.TAB_TRAVERSAL)
		self.SetClientSize(wx.Size(749, 504))
		self.SetToolTip("")
		self.SetAutoLayout(True)

		self.Splitter = wx.SplitterWindow(id=-1, name="Splitter", parent=self, pos=wx.Point(16, 24), size=wx.Size(272, 168), style=wx.SP_3D | wx.SP_LIVE_UPDATE)
		self.Splitter.SetAutoLayout(True)
		self.Splitter.Bind(wx.EVT_SPLITTER_DCLICK, self.OnSplitterDclick)

		self.p1 = wx.Panel(self.Splitter)
		self.p1.SetAutoLayout(True)
		self.p1.prnt = prnt
		self.p1.parent = self

		self.optDlg = selFun(self.Splitter)

		self.plcPlot = MyPlotCanvas(id=IDPLOTSPEC, name="plcPlot", parent=self.p1, pos=wx.Point(0, 0), size=wx.Size(200, 200), style=wx.SUNKEN_BORDER, toolbar=self.p1.prnt.parent.tbMain)
		self.plcPlot.enableZoom = True
		self.plcPlot.fontSizeTitle = 12
		self.plcPlot.SetToolTip("")
		self.plcPlot.fontSizeAxis = 10
		self.plcPlot.SetConstraints(LayoutAnchors(self.plcPlot, True, True, True, True))

		self.titleBar = TitleBar(self, id=-1, text="Spectral Preprocessing", style=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT, canvasList=[self.plcPlot])

		self.Splitter.SplitVertically(self.optDlg, self.p1, 1)
		self.Splitter.SetMinimumPaneSize(1)

		self._init_sizers()

	def __init__(self, parent, id, pos, size, style, name):
		self._init_ctrls(parent)

		self.parent = parent

	def Reset(self):
		curve = wx.lib.plot.PolyLine([[0, 0], [1, 1]], colour="white", width=1, style=wx.TRANSPARENT)
		curve = wx.lib.plot.PlotGraphics([curve], "Experimental Data", "Arbitrary", "Arbitrary")
		self.plcPlot.Draw(curve)

		self.optDlg.lbSpectra2.Clear()

	def OnSplitterDclick(self, event):
		if self.Splitter.GetSashPosition() <= 5:
			self.Splitter.SetSashPosition(250)
		else:
			self.Splitter.SetSashPosition(1)

	def DoPeakCalculations(self):
		# get x lims for calculating peak areas etc
		coords = self.plcPlot.GetInterXlims()
		# open options dialog
		dlg = PeakCalculations(self, coords, self.titleBar.data, self.plcPlot)
		dlg.ShowModal()


class TitleBar(bp.ButtonPanel):
	def _init_btnpanel_ctrls(self, prnt):
		bp.ButtonPanel.__init__(self, parent=prnt, id=-1, text="Spectral Preprocessing", agwStyle=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self.btnSetProc = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "params.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Select Preprocessing Options", longHelp="Select Preprocessing Options")
		self.Bind(wx.EVT_BUTTON, self.OnBtnSetProcButton, id=self.btnSetProc.GetId())

		self.btnInteractive = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "peak.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Interactive Mode", longHelp="Interactive mode for peak area calculations, intensities etc.")
		self.btnInteractive.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnInteractiveButton, id=self.btnInteractive.GetId())

		self.btnPlot = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "run.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Execute Plot", longHelp="Execute Plot")
		self.btnPlot.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnPlotButton, id=self.btnPlot.GetId())

		self.btnExportData = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "export.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Export Data", longHelp="Export Data")
		self.btnExportData.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnExportDataButton, id=self.btnExportData.GetId())

		self.spcPlotSpectra = wx.SpinCtrl(id=-1, initial=1, max=100, min=1, name="spcPlotSpectra", parent=self, pos=wx.Point(198, 554), size=wx.Size(64, 23), style=wx.SP_ARROW_KEYS)
		self.spcPlotSpectra.SetToolTip("")
		self.spcPlotSpectra.SetValue(1)

		self.cbxData = wx.Choice(choices=["Raw spectra", "Processed spectra"], id=-1, name="cbxData", parent=self, pos=wx.Point(118, 23), size=wx.Size(100, 23), style=0)
		self.cbxData.SetSelection(0)

		self.cbxNumber = wx.Choice(choices=["Single spectrum", "All spectra"], id=-1, name="cbxNumber", parent=self, pos=wx.Point(118, 23), size=wx.Size(100, 23), style=0)
		self.cbxNumber.SetSelection(0)

	def __init__(self, parent, id, text, style, alignment, canvasList):

		self._init_btnpanel_ctrls(parent)

		self.CreateButtons()

		self.parent = parent

		self.canvas = canvasList[0]

	def CreateButtons(self):
		self.Freeze()

		self.SetProperties()

		self.AddControl(self.cbxData)
		self.AddControl(self.cbxNumber)
		self.AddControl(self.spcPlotSpectra)
		self.AddSeparator()
		self.AddButton(self.btnSetProc)
		self.AddSeparator()
		self.AddButton(self.btnPlot)
		self.AddSeparator()
		self.AddButton(self.btnInteractive)
		self.AddSeparator()
		self.AddButton(self.btnExportData)

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

	def OnBtnInteractiveButton(self, event):
		# plot the average spectrum
		self.PlotSpectra(average=True)
		# add details of current plot to toolbar
		self.canvas.PopulateToolbar()
		# interactive mode for plotting screen - allows to calculate peak areas etc
		self.canvas.SetEnableInteractive(True)

	def OnBtnPlotButton(self, event):
		# Set enable zoom just in case
		self.canvas.enableZoom = True
		# Plot spectra
		self.PlotSpectra()

	def PlotSpectra(self, average=False, xlim=None, ylim=None):
		# select data and run processing
		if self.cbxData.GetSelection() == 0:
			if not average:
				xdata = self.data["rawtrunc"]
			else:
				xdata = self.data["raw"][:, np.array(self.data["variableidx"])]
			title = "Raw"
		else:
			self.RunProcessingSteps()
			if not average:
				xdata = self.data["proctrunc"]
			else:
				xdata = self.data["proc"][:, np.array(self.data["variableidx"])]
			title = "Processed"
		# do plotting
		if not average:
			# set busy cursor
			wx.BeginBusyCursor()
			# Plot xdata
			if self.cbxNumber.GetSelection() == 1:
				plotLine(self.canvas, xdata, tit=title, xaxis=self.data["xaxis"], xLabel="Arbitrary", yLabel="Arbitrary", type="multi", wdth=1, ledge=None)

			elif self.cbxNumber.GetSelection() == 0:
				plotLine(self.canvas, xdata, tit=title, xaxis=self.data["xaxis"], xLabel="Arbitrary", yLabel="Arbitrary", type="single", rownum=self.spcPlotSpectra.GetValue() - 1, wdth=1, ledge=[])

			# remove busy cursor
			wx.EndBusyCursor()
		else:
			line = wx.lib.plot.PolyLine(scipy.concatenate((self.data["xaxis"], scipy.mean(xdata, axis=0)[:, scipy.newaxis]), 1))
			line = wx.lib.plot.PlotGraphics([line], title="Average " + title + " Spectrum", xLabel="Arbitrary", yLabel="Average Intensity")
			if self.canvas._justDragged:
				xlim = tuple(self.canvas.GetXCurrentRange())
				ylim = tuple(self.canvas.GetYCurrentRange())

			self.canvas.Draw(line, xAxis=xlim, yAxis=ylim)

	def OnBtnExportDataButton(self, event):
		# export data
		dlg = wx.FileDialog(self, "Choose a file", ".", "", "Text files (*.txt)|*.txt", wx.FD_SAVE)
		try:
			if dlg.ShowModal() == wx.ID_OK:
				if self.cbxData.GetSelection() == 0:
					scipy.io.write_array(dlg.GetPath(), scipy.transpose(self.data["rawtrunc"]), "\t")
				else:
					scipy.io.write_array(dlg.GetPath(), scipy.transpose(self.data["proctrunc"]), "\t")
		finally:
			dlg.Destroy()

	def RunProcessingSteps(self):
		##		  #remove any user defined processed variables
		##		  grid = self.parent.parent.parent.plExpset.grdIndLabels
		##		  for i in range(1,grid.GetNumberRows()):
		##			  if len(grid.GetRowLabelValue(i).split('U')) > 1:
		##				  if grid.GetCellValue(i.split(1),'_')[2] in ['PROC']:
		##					  GridRowDel(grid, self.data) #would need to pass row num (i) for this to work
		##					  #update experiment setup
		##					  self.parent.parent.parent.GetExperimentDetails(case=1)
		##			  else:
		##				  break
		# Run pre-processing
		self.data["proc"] = copy.deepcopy(self.data["raw"])
		for each in self.data["processlist"]:
			if each == 3:
				self.data["proc"] = mva.process.norm01(self.data["proc"])
			elif each == 4:
				self.data["proc"] = mva.process.normhigh(self.data["proc"])
			elif each == 5:
				self.data["proc"] = mva.process.normtot(self.data["proc"])
			elif each == 6:
				self.data["proc"] = mva.process.meancent(self.data["proc"])
			elif each == 7:
				self.data["proc"] = mva.process.autoscale(self.data["proc"])
			elif each == 8:
				self.data["proc"] = scipy.transpose(mva.process.autoscale(scipy.transpose(self.data["proc"])))
			elif each == 9:
				self.data["proc"] = mva.process.emsc(self.data["proc"], 0)
			elif each == 10:
				self.data["proc"] = mva.process.emsc(self.data["proc"], 1)
			elif each == 11:
				self.data["proc"] = mva.process.emsc(self.data["proc"], 2)
			elif each == 12:
				self.data["proc"] = mva.process.emsc(self.data["proc"], 3)
			elif each == 13:
				self.data["proc"] = mva.process.emsc(self.data["proc"], 4)
			elif each == 14:
				self.data["proc"] = mva.process.emsc(self.data["proc"], 5)
			elif each == 15:
				self.data["proc"] = mva.process.emsc(self.data["proc"], 6)
			elif each == 16:
				self.data["proc"] = mva.process.emsc(self.data["proc"], 7)
			elif each == 17:
				self.data["proc"] = mva.process.emsc(self.data["proc"], 8)
			elif each == 18:
				self.data["proc"] = mva.process.emsc(self.data["proc"], 9)
			elif each == 19:
				self.data["proc"] = mva.process.emsc(self.data["proc"], 10)
			elif each == 20:
				self.data["proc"] = mva.process.emsc(self.data["proc"], 11)
			elif each == 21:
				self.data["proc"] = mva.process.emsc(self.data["proc"], 12)
			elif each == 22:
				self.data["proc"] = mva.process.emsc(self.data["proc"], 13)
			elif each == 23:
				self.data["proc"] = mva.process.emsc(self.data["proc"], 14)
			elif each == 24:
				self.data["proc"] = mva.process.emsc(self.data["proc"], 15)

			elif each == 27:
				self.data["proc"] = mva.process.avgfilt(self.data["proc"], 3, "c")
			elif each == 28:
				self.data["proc"] = mva.process.avgfilt(self.data["proc"], 4, "c")
			elif each == 29:
				self.data["proc"] = mva.process.avgfilt(self.data["proc"], 5, "c")
			elif each == 30:
				self.data["proc"] = mva.process.avgfilt(self.data["proc"], 6, "c")
			elif each == 31:
				self.data["proc"] = mva.process.avgfilt(self.data["proc"], 7, "c")
			elif each == 32:
				self.data["proc"] = mva.process.avgfilt(self.data["proc"], 8, "c")
			elif each == 33:
				self.data["proc"] = mva.process.avgfilt(self.data["proc"], 9, "c")
			elif each == 34:
				self.data["proc"] = mva.process.avgfilt(self.data["proc"], 10, "c")

			elif each == 37:
				self.data["proc"] = mva.process.baseline1(self.data["proc"])
			elif each == 38:
				self.data["proc"] = mva.process.baseline2(self.data["proc"])
			elif each == 39:
				self.data["proc"] = mva.process.lintrend(self.data["proc"])

			elif each == 42:
				self.data["proc"] = mva.process.derivlin(self.data["proc"], 3)
			elif each == 43:
				self.data["proc"] = mva.process.derivlin(self.data["proc"], 4)
			elif each == 44:
				self.data["proc"] = mva.process.derivlin(self.data["proc"], 5)
			elif each == 45:
				self.data["proc"] = mva.process.derivlin(self.data["proc"], 6)
			elif each == 46:
				self.data["proc"] = mva.process.derivlin(self.data["proc"], 7)
			elif each == 47:
				self.data["proc"] = mva.process.derivlin(self.data["proc"], 8)
			elif each == 48:
				self.data["proc"] = mva.process.derivlin(self.data["proc"], 9)
			elif each == 49:
				self.data["proc"] = mva.process.derivlin(self.data["proc"], 10)

		self.parent.parent.parent.GetExperimentDetails(case=1)

	def OnBtnSetProcButton(self, event):
		if self.parent.Splitter.GetSashPosition() <= 5:
			self.parent.Splitter.SetSashPosition(250)
		else:
			self.parent.Splitter.SetSashPosition(1)

	def getData(self, data):
		self.data = data
		self.parent.optDlg.getData(data)


class selFun(fpb.FoldPanelBar):
	def _init_coll_gbsSelfun_Growables(self, parent):
		# generated method, don't edit

		parent.AddGrowableRow(0)
		parent.AddGrowableCol(0)
		parent.AddGrowableCol(1)

	def _init_coll_gbsSelfun_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.lbSpectra2, (0, 0), flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.btnSpectraUp, (1, 0), flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.btnSpectraDown, (1, 1), flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.btnSpectraDelete, (2, 0), flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.btnSpectraReset, (2, 1), flag=wx.EXPAND, span=(1, 1))
		parent.AddSpacer(wx.Size(8, 8), (3, 0), flag=wx.EXPAND, span=(2, 2))

	def _init_selparam_sizers(self):
		# generated method, don't edit
		self.gbsSelfun = wx.GridBagSizer(5, 5)
		self.gbsSelfun.SetCols(2)
		self.gbsSelfun.SetRows(5)

		self._init_coll_gbsSelfun_Items(self.gbsSelfun)
		self._init_coll_gbsSelfun_Growables(self.gbsSelfun)

		self.fpSelected.SetSizer(self.gbsSelfun)

	def _init_selfun_ctrls(self, prnt):
		# generated method, don't edit
		fpb.FoldPanelBar.__init__(self, prnt, -1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=fpb.FPB_DEFAULT_STYLE | fpb.FPB_SINGLE_FOLD)
		self.SetConstraints(LayoutAnchors(self, True, True, True, True))
		self.SetAutoLayout(True)

		icons = wx.ImageList(16, 16)
		icons.Add(wx.Bitmap(os.path.join("bmp", "arrown.png"), wx.BITMAP_TYPE_PNG))
		icons.Add(wx.Bitmap(os.path.join("bmp", "arrows.png"), wx.BITMAP_TYPE_PNG))

		self.fpFunctions = self.AddFoldPanel("Preprocessing functions", collapsed=True, foldIcons=icons)
		self.fpFunctions.SetAutoLayout(True)

		self.fpSelected = self.AddFoldPanel("Selected functions", collapsed=True, foldIcons=icons)
		self.fpSelected.SetAutoLayout(True)
		##		  self.fpResults.Bind(wx.EVT_SIZE, self.OnFpbResize)

		self.plSelected = wx.Panel(id=-1, name="plSelected", parent=self.fpSelected, pos=wx.Point(0, 0), size=wx.Size(200, 350), style=wx.TAB_TRAVERSAL)
		self.plSelected.SetToolTip("")
		self.plSelected.SetConstraints(LayoutAnchors(self.plSelected, True, True, True, True))

		self.lbSpectra1 = wx.ListBox(choices=["", "Scaling", "	Normalise to 0 for min, +1 for max.", "  Normalise max. bin to +1", "	Normalise to total", "	Mean centre", "	 Column normalisation", "  Row normalisation", "  Extended multiplicative scatter correction, order 0", "  Extended multiplicative scatter correction, order 1", "	Extended multiplicative scatter correction, order 2", "	 Extended multiplicative scatter correction, order 3", "  Extended multiplicative scatter correction, order 4", "  Extended multiplicative scatter correction, order 5", "	Extended multiplicative scatter correction, order 6", "	 Extended multiplicative scatter correction, order 7", "  Extended multiplicative scatter correction, order 8", "  Extended multiplicative scatter correction, order 9", "	Extended multiplicative scatter correction, order 10", "  Extended multiplicative scatter correction, order 11", "	Extended multiplicative scatter correction, order 12", "  Extended multiplicative scatter correction, order 13", "	Extended multiplicative scatter correction, order 14", "  Extended multiplicative scatter correction, order 15", "", "Filtering", "	 Linear mean filter, frame width 3", "	Linear mean filter, frame width 4", "  Linear mean filter, frame width 5", "  Linear mean filter, frame width 6", "	 Linear mean filter, frame width 7", "	Linear mean filter, frame width 8", "  Linear mean filter, frame width 9", "  Linear mean filter, frame width 10", "", "Baseline Correction", "	 Set first bin to zero", "	Subtract average of first and last bin", "	Subtract a linearly increasing baseline", "", "Derivatisation", "  Linear derivatisation, frame width 3", "	 Linear derivatisation, frame width 4", "  Linear derivatisation, frame width 5", "	 Linear derivatisation, frame width 6", "  Linear derivatisation, frame width 7", "	 Linear derivatisation, frame width 8", "  Linear derivatisation, frame width 9", "	 Linear derivatisation, frame width 10", ""], id=-1, name="lbSpectra1", parent=self.fpFunctions, pos=wx.Point(0, 23), size=wx.Size(250, 280), style=wx.HSCROLL, validator=wx.DefaultValidator)
		self.lbSpectra1.SetToolTip("")
		self.lbSpectra1.Bind(wx.EVT_LISTBOX_DCLICK, self.OnLbspectra1ListboxDclick)

		self.lbSpectra2 = wx.ListBox(choices=[], id=-1, name="lbSpectra2", parent=self.plSelected, pos=wx.Point(0, 0), size=wx.Size(250, 150), style=wx.HSCROLL, validator=wx.DefaultValidator)
		self.lbSpectra2.SetToolTip("")

		self.btnSpectraUp = wx.Button(id=-1, label="Up", name="btnSpectraUp", parent=self.plSelected, pos=wx.Point(0, 0), size=wx.Size(48, 23), style=0)
		self.btnSpectraUp.SetToolTip("Move up")
		self.btnSpectraUp.Bind(wx.EVT_BUTTON, self.OnBtnspectraupButton)

		self.btnSpectraDelete = wx.Button(id=-1, label="Del", name="btnSpectraDelete", parent=self.plSelected, pos=wx.Point(0, 0), size=wx.Size(48, 23), style=0)
		self.btnSpectraDelete.SetToolTip("Delete selected function")
		self.btnSpectraDelete.Bind(wx.EVT_BUTTON, self.OnBtnspectradeleteButton)

		self.btnSpectraDown = wx.Button(id=-1, label="Down", name="btnSpectraDown", parent=self.plSelected, pos=wx.Point(0, 0), size=wx.Size(48, 23), style=0)
		self.btnSpectraDown.SetToolTip("Move down")
		self.btnSpectraDown.Bind(wx.EVT_BUTTON, self.OnBtnspectradownButton)

		self.btnSpectraReset = wx.Button(id=-1, label="Reset", name="btnSpectraReset", parent=self.plSelected, pos=wx.Point(0, 0), size=wx.Size(46, 23), style=0)
		self.btnSpectraReset.SetToolTip("Reset")
		self.btnSpectraReset.Bind(wx.EVT_BUTTON, self.OnBtnspectraresetButton)

		self.AddFoldPanelWindow(self.fpFunctions, self.lbSpectra1, fpb.FPB_ALIGN_WIDTH)
		self.AddFoldPanelWindow(self.fpSelected, self.plSelected, fpb.FPB_ALIGN_WIDTH)

		self._init_selparam_sizers()

	def __init__(self, parent):
		self._init_selfun_ctrls(parent)

		self.Expand(self.fpFunctions)
		self.Expand(self.fpSelected)

	def getData(self, data):
		self.data = data

	def OnLbspectra1ListboxDclick(self, event):
		Selected = self.lbSpectra1.GetSelection()
		SelectedText = self.lbSpectra1.GetStringSelection()
		if SelectedText[0:2] == "  ":
			self.data["processlist"].append(Selected + 1)
			self.lbSpectra2.Append(SelectedText[2 : len(SelectedText)])

	def OnBtnspectraupButton(self, event):
		CurrentPos = self.lbSpectra2.GetSelection()
		if CurrentPos > 0:
			NewList = []
			NewProcessList = []
			for i in range(0, CurrentPos - 1):
				NewList.append(self.lbSpectra2.GetString(i))
				NewProcessList.append(self.data["processlist"][i])

			NewList.append(self.lbSpectra2.GetString(CurrentPos))
			NewList.append(self.lbSpectra2.GetString(CurrentPos - 1))
			NewProcessList.append(self.data["processlist"][CurrentPos])
			NewProcessList.append(self.data["processlist"][CurrentPos - 1])

			for i in range(CurrentPos + 1, self.lbSpectra2.GetCount()):
				NewList.append(self.lbSpectra2.GetString(i))
				NewProcessList.append(self.data["processlist"][i])

			self.data["processlist"] = NewProcessList
			self.lbSpectra2.Clear()
			for i in range(len(NewList)):
				self.lbSpectra2.Append(NewList[i])
			self.lbSpectra2.SetSelection(CurrentPos - 1)

	def OnBtnspectradeleteButton(self, event):
		if len(self.data["processlist"]) > 0:
			del self.data["processlist"][self.lbSpectra2.GetSelection()]
			self.lbSpectra2.Delete(self.lbSpectra2.GetSelection())
			if len(self.data["processlist"]) == 0:
				self.data["processlist"] = []
				self.data["proc"] = None

	def OnBtnspectradownButton(self, event):
		CurrentPos = self.lbSpectra2.GetSelection()
		if CurrentPos < self.lbSpectra2.GetCount() - 1:
			NewList = []
			NewProcessList = []
			if CurrentPos > 0:
				for i in range(0, CurrentPos):
					NewList.append(self.lbSpectra2.GetString(i))
					NewProcessList.append(self.data["processlist"][i])

			NewList.append(self.lbSpectra2.GetString(CurrentPos + 1))
			NewList.append(self.lbSpectra2.GetString(CurrentPos))
			NewProcessList.append(self.data["processlist"][CurrentPos + 1])
			NewProcessList.append(self.data["processlist"][CurrentPos])

			if CurrentPos + 2 <= self.lbSpectra2.GetCount() - 1:
				for i in range(CurrentPos + 2, self.lbSpectra2.GetCount()):
					NewList.append(self.lbSpectra2.GetString(i))
					NewProcessList.append(self.data["processlist"][i])

			self.ProcessList = NewProcessList
			self.lbSpectra2.Clear()
			for i in range(len(NewList)):
				self.lbSpectra2.Append(NewList[i])
			self.lbSpectra2.SetSelection(CurrentPos + 1)

	def OnBtnspectraresetButton(self, event):
		self.lbSpectra2.Clear()
		self.data["processlist"] = []
		self.data["proc"] = None
