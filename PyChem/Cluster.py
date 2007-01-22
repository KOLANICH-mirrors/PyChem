# Boa:FramePanel:Cluster

import string

import scipy
import wx
import wx.lib.agw.buttonpanel as bp
import wx.lib.buttons
import wx.lib.plot
from Bio.Cluster import *
from wx.lib.anchors import LayoutAnchors

from . import chemometrics
from .chemometrics import _index

[
	wxID_CLUSTER,
] = [wx.NewIdRef() for _init_ctrls in range(1)]

[
	wxID_SELFUN,
	wxID_SELFUNCBAVLINK,
	wxID_SELFUNCBCENTLINK,
	wxID_SELFUNCBMAXLINK,
	wxID_SELFUNCBSINGLELINK,
	wxID_SELFUNCBUSECLASS,
	wxID_SELFUNRBABSCORR,
	wxID_SELFUNRBABSUNCENTCORR,
	wxID_SELFUNRBCITYBLOCK,
	wxID_SELFUNRBCORRELATION,
	wxID_SELFUNRBEUCLIDEAN,
	wxID_SELFUNRBHARMONICEUC,
	wxID_SELFUNRBHCLUSTER,
	wxID_SELFUNRBKENDALLS,
	wxID_SELFUNRBKMEANS,
	wxID_SELFUNRBKMEDIAN,
	wxID_SELFUNRBKMEDOIDS,
	wxID_SELFUNRBPLOTCOLOURS,
	wxID_SELFUNRBPLOTNAME,
	wxID_SELFUNRBSPEARMANS,
	wxID_SELFUNRBUNCENTREDCORR,
	wxID_SELFUNSPNNOPASS,
	wxID_SELFUNSTATICBOX1,
	wxID_SELFUNSTATICBOX2,
	wxID_SELFUNSTNOPASS,
] = [wx.NewIdRef() for _init_selfun_ctrls in range(25)]


def errorBox(window, error):
	dlg = wx.MessageDialog(window, "".join(("The following error occured:\n\n", error)), "Error!", wx.OK | wx.ICON_ERROR)
	try:
		dlg.ShowModal()
	finally:
		dlg.Destroy()


class Cluster(wx.Panel):
	def _init_coll_grsPlc_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.plcCluster, 0, border=0, flag=wx.EXPAND)

	def _init_coll_grsTxt_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.txtCluster, 0, border=0, flag=wx.EXPAND)

	def _init_coll_bxsClus1_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.bxsClus2, 1, border=0, flag=wx.EXPAND)

	def _init_coll_bxsClus2_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.titleBar, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.grsClus, 1, border=0, flag=wx.EXPAND)

	def _init_plc_sizers(self):
		# generated method, don't edit
		self.bxsClus1 = wx.BoxSizer(orient=wx.HORIZONTAL)

		self.bxsClus2 = wx.BoxSizer(orient=wx.VERTICAL)

		self.grsClus = wx.GridSizer(cols=1, hgap=2, rows=1, vgap=2)

		self._init_coll_bxsClus1_Items(self.bxsClus1)
		self._init_coll_bxsClus2_Items(self.bxsClus2)
		self._init_coll_grsPlc_Items(self.grsClus)

		self.SetSizer(self.bxsClus1)

	def _init_txt_sizers(self):
		# generated method, don't edit
		self.bxsClus1 = wx.BoxSizer(orient=wx.HORIZONTAL)

		self.bxsClus2 = wx.BoxSizer(orient=wx.VERTICAL)

		self.grsClus = wx.GridSizer(cols=1, hgap=2, rows=1, vgap=2)

		self._init_coll_bxsClus1_Items(self.bxsClus1)
		self._init_coll_bxsClus2_Items(self.bxsClus2)
		self._init_coll_grsTxt_Items(self.grsClus)

		self.SetSizer(self.bxsClus1)

	def _init_ctrls(self, prnt):
		# generated method, don't edit
		wx.Panel.__init__(self, id=wxID_CLUSTER, name="Cluster", parent=prnt, pos=wx.Point(72, 35), size=wx.Size(907, 670), style=wx.TAB_TRAVERSAL)
		self.SetClientSize(wx.Size(899, 636))
		self.SetToolTip("")
		self.SetAutoLayout(True)
		self.SetBackgroundColour(wx.Colour(167, 167, 243))

		self.plcCluster = wx.lib.plot.PlotCanvas(id=-1, name="plcCluster", parent=self, pos=wx.Point(248, 0), size=wx.Size(731, 594), style=wx.SUNKEN_BORDER)
		self.plcCluster.SetToolTip("")
		self.plcCluster.enableZoom = True
		self.plcCluster.fontSizeTitle = 12
		self.plcCluster.fontSizeAxis = 12
		self.plcCluster.SetForegroundColour(wx.Colour(0, 0, 0))
		self.plcCluster.xSpec = "none"
		self.plcCluster.ySpec = "none"
		self.plcCluster.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Small Fonts"))
		##		  self.plcCluster.Bind(wx.EVT_RIGHT_DOWN, self.OnPlcClusterRightDown,
		##				id=-1)

		self.txtCluster = wx.TextCtrl(id=-1, name="tcCluster", parent=self, pos=wx.Point(248, 0), size=wx.Size(1730, 1225), style=wx.TE_DONTWRAP | wx.HSCROLL | wx.TE_READONLY | wx.TE_MULTILINE | wx.VSCROLL, value="")
		self.txtCluster.SetToolTip("")
		self.txtCluster.Show(False)

		self.titleBar = TitleBar(self, id=-1, text="Cluster Analysis", style=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self._init_plc_sizers()

	def __init__(self, parent, id, pos, size, style, name):
		self._init_ctrls(parent)

		self.parent = parent

	def Reset(self):
		curve = wx.lib.plot.PolyLine([[0, 0], [1, 1]], colour="white", width=1, style=wx.TRANSPARENT)
		curve = wx.lib.plot.PlotGraphics([curve], "Hierarchical Cluster Analysis", "", "")
		self.plcCluster.Draw(curve)

		self.txtCluster.SetValue("")


class TitleBar(bp.ButtonPanel):
	def _init_btnpanel_ctrls(self, prnt):
		bp.ButtonPanel.__init__(self, parent=prnt, id=-1, text="Cluster Analysis", agwStyle=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self.cbxData = wx.Choice(choices=["Raw spectra", "Processed spectra", "PC Scores", "DF Scores"], id=-1, name="cbxData", parent=self, pos=wx.Point(118, 21), size=wx.Size(100, 23), style=0)
		self.cbxData.SetSelection(0)

		self.btnRunClustering = wx.lib.buttons.GenButton(id=-1, label="Run", name="btnRunClustering", parent=self, pos=wx.Point(8, 592), size=wx.Size(60, 23), style=0)
		self.btnRunClustering.SetToolTip("")
		self.btnRunClustering.Enable(False)
		self.btnRunClustering.Bind(wx.EVT_BUTTON, self.OnBtnRunClusteringButton, id=-1)

		self.btnExportCluster = wx.lib.buttons.GenButton(id=-1, label="Export", name="btnExportCluster", parent=self, pos=wx.Point(136, 592), size=wx.Size(60, 23), style=0)
		self.btnExportCluster.SetToolTip("")
		self.btnExportCluster.Enable(False)
		self.btnExportCluster.Bind(wx.EVT_BUTTON, self.OnBtnExportClusterButton, id=-1)

		self.setParams = wx.Button(id=-1, label="Set Cluster Method", name="setParams", parent=self, pos=wx.Point(136, 592), size=wx.Size(120, 23), style=0)
		self.setParams.SetToolTip("")
		self.setParams.Bind(wx.EVT_BUTTON, self.OnBtnSetParamsButton, id=-1)

	def __init__(self, parent, id, text, style, alignment):

		self._init_btnpanel_ctrls(parent)

		self.CreateButtons()

		self.dlg = selFun(self)

		self.parent = parent

	def CreateButtons(self):
		self.Freeze()

		self.SetProperties()

		self.AddControl(self.setParams)
		self.AddControl(self.cbxData)
		self.AddControl(self.btnRunClustering)
		self.AddControl(self.btnExportCluster)

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

	def getData(self, data):
		self.data = data

	def OnBtnExportClusterButton(self, event):
		event.Skip()

	def OnBtnSetParamsButton(self, event):
		height = self.parent.parent.parent.GetSize()[1]
		self.dlg.SetSize(wx.Size(200, height))
		self.dlg.SetPosition(wx.Point(0, int((wx.GetDisplaySize()[1] - height) / 2.0)))
		self.parent.parent.parent.SetSize(wx.Size(wx.GetDisplaySize()[0] - 200, height))
		self.parent.parent.parent.SetPosition(wx.Point(200, int((wx.GetDisplaySize()[1] - height) / 2.0)))
		self.dlg.Iconize(False)
		self.dlg.Show()

	def OnBtnRunClusteringButton(self, event):
		self.RunClustering()

	def RunClustering(self):
		try:
			# get x-data
			if self.cbxData.GetSelection() == 0:
				xdata = self.data["rawtrunc"]
			elif self.cbxData.GetSelection() == 1:
				xdata = self.data["proctrunc"]
			elif self.cbxData.GetSelection() == 2:
				xdata = self.data["pcscores"]
			elif self.cbxData.GetSelection() == 3:
				xdata = self.data["dfscores"]

			# get distance measure
			if self.dlg.rbEuclidean.GetValue() is True:
				seldist = "e"
			elif self.dlg.rbCorrelation.GetValue() is True:
				seldist = "c"
			elif self.dlg.rbAbsCorr.GetValue() is True:
				seldist = "a"
			elif self.dlg.rbUncentredCorr.GetValue() is True:
				seldist = "u"
			elif self.dlg.rbAbsUncentCorr.GetValue() is True:
				seldist = "x"
			elif self.dlg.rbSpearmans.GetValue() is True:
				seldist = "s"
			elif self.dlg.rbKendalls.GetValue() is True:
				seldist = "k"
			elif self.dlg.rbHarmonicEuc.GetValue() is True:
				seldist = "h"
			elif self.dlg.rbCityBlock.GetValue() is True:
				seldist = "b"

			# run clustering
			if self.dlg.rbKmeans.GetValue() is True:
				if self.dlg.cbUseClass.GetValue() is True:
					cl = np.array(self.data["class"], "i") - 1
					self.clusterid, error, nfound = kcluster(xdata, nclusters=int(max(self.data["class"])), transpose=0, npass=self.dlg.spnNoPass.GetValue(), method="a", dist=seldist, initialid=cl.tolist())

				else:
					self.clusterid, error, nfound = kcluster(xdata, nclusters=int(max(self.data["class"])), transpose=0, npass=self.dlg.spnNoPass.GetValue(), method="a", dist=seldist)

				self.parent._init_txt_sizers()

				self.parent.plcCluster.Show(False)
				self.parent.txtCluster.Show(True)

				sizeMask = xdata.shape

				centroids, mask = clustercentroid(xdata, mask=ones(sizeMask), clusterid=self.clusterid, method="a", transpose=0)

				self.ReportPartitioning(self.parent.txtCluster, self.clusterid, error, nfound, "k-means Summary", centroids)

			elif self.dlg.rbKmedian.GetValue() is True:
				if self.dlg.cbUseClass.GetValue() is True:
					cl = np.array(self.data["class"], "i") - 1
					self.clusterid, error, nfound = kcluster(xdata, nclusters=int(max(self.data["class"])), transpose=0, npass=self.dlg.spnNoPass.GetValue(), method="m", dist=seldist, initialid=cl.tolist())

				else:
					self.clusterid, error, nfound = kcluster(xdata, nclusters=int(max(self.data["class"])), transpose=0, npass=self.dlg.spnNoPass.GetValue(), method="m", dist=seldist)
				self.parent._init_txt_sizers()

				self.parent.plcCluster.Show(False)
				self.parent.txtCluster.Show(True)

				sizeMask = xdata.shape

				centroids, mask = clustercentroid(xdata, mask=ones(sizeMask), clusterid=self.clusterid, method="m", transpose=0)

				self.ReportPartitioning(self.parent.txtCluster, self.clusterid, error, nfound, "k-medians Summary", centroids)

			elif self.dlg.rbKmedoids.GetValue() == 1:
				distance = self.ConvDist(xdata, seldist)
				if self.dlg.cbUseClass.GetValue() is True:
					cl = np.array(self.data["class"], "i") - 1
					self.clusterid, error, nfound = cluster.kmedoids(distance, nclusters=int(max(self.data["class"])), npass=self.dlg.spnNoPass.GetValue(), initialid=cl.tolist())

				else:
					self.clusterid, error, nfound = cluster.kmedoids(distance, nclusters=int(max(self.data["class"])), npass=self.dlg.spnNoPass.GetValue())

				# rename cluster ids
				for i in range(len(self.clusterid)):
					self.clusterid[i] = self.data["class"][self.clusterid[i]] - 1

				self.parent._init_txt_sizers()

				self.parent.plcCluster.Show(False)
				self.parent.txtCluster.Show(True)

				self.ReportPartitioning(self.parent.txtCluster, self.clusterid, error, nfound, "k-medoids Summary")

			elif self.dlg.rbHcluster.GetValue() is True:
				# get clustering method
				if self.dlg.rbSingleLink.GetValue() is True:
					Hmeth = "s"
				elif self.dlg.rbMaxLink.GetValue() is True:
					Hmeth = "m"
				elif self.dlg.rbAvLink.GetValue() is True:
					Hmeth = "a"
				elif self.dlg.rbCentLink.GetValue() is True:
					Hmeth = "c"

				# run hca
				tree, self.linkdist = treecluster(data=xdata, method=Hmeth, dist=seldist)
				self.Atree = tree

				# determine tree structure
				tree, self.order = self.savetree(tree, self.linkdist, scipy.arange(len(tree) + 1), transpose=0)
				self.output = tree

				# draw tree
				self.PlotCluster = self.DrawTree(self.parent.plcCluster, tree, self.order, self.data["label"])

				self.parent._init_plc_sizers()

				self.parent.plcCluster.Show(True)
				self.parent.txtCluster.Show(False)

		##			  #enable export
		##			  if self.rbHcluster.GetValue() is True:
		##				  self.btnExportCluster.Enable(1)
		##			  else:
		##				  self.btnExportCluster.Enable(0)
		except Exception as error:
			errorBox(self, "%s" % str(error))

	def savetree(self, clusters, linkdist, order, transpose):
		# determine hierarchical tree structure
		from Bio.Cluster import data

		nnodes = len(clusters)
		nodeID = scipy.zeros((nnodes, 4), "d")
		nodecounts = scipy.zeros(nnodes)
		nodeorder = scipy.zeros(nnodes, "d")
		nodedist = np.array(linkdist)
		for nodeindex in range(nnodes):
			min1 = clusters[nodeindex][0]
			min2 = clusters[nodeindex][1]
			nodeID[nodeindex, 0] = nodeindex
			if min1 < 0:
				index1 = -min1 - 1
				order1 = nodeorder[index1]
				counts1 = nodecounts[index1]
				nodeID[nodeindex, 1] = min1
			else:
				order1 = order[min1]
				counts1 = 1
				nodeID[nodeindex, 1] = min1
			if min2 < 0:
				index2 = -min2 - 1
				order2 = nodeorder[index2]
				counts2 = nodecounts[index2]
				nodeID[nodeindex, 2] = min2
			else:
				order2 = order[min2]
				counts2 = 1
				nodeID[nodeindex, 2] = min2
			nodeID[nodeindex, 3] = nodedist[nodeindex]
			nodecounts[nodeindex] = counts1 + counts2
			nodeorder[nodeindex] = (counts1 * order1 + counts2 * order2) / (counts1 + counts2)
		# Now set up order based on the tree structure
		index = data.treesort(order, nodeorder, nodecounts, clusters)
		return nodeID, index

	def DrawTree(self, canvas, tree, order, name):
		colourList = ["BLUE", "BROWN", "CYAN", "GREY", "GREEN", "MAGENTA", "ORANGE", "PURPLE", "VIOLET"]

		# set font size
		font_size = 7

		canvas.fontSizeAxis = font_size
		canvas.enableLegend = 0
		# do level 1
		List, Cols, ccount = [], [], 0
		for i in range(len(tree)):
			if self.data["class"][i] not in List:
				List.append(self.data["class"][i])
				Cols.append(colourList[ccount])
				ccount += 1
				if ccount == len(colourList):
					ccount = 0
		minx = 0
		if self.dlg.rbPlotColours.GetValue() is True:
			canvas.enableLegend = 1
			Line, List, Nlist, Store = [], [], [], {}
			count = 0
			for i in range(len(order)):
				idn = int(self.data["class"][order[i]])
				# plot names
				if idn in List:
					Store[str(idn)] = scipy.concatenate((Store[str(idn)], [[0, count]]), 0)
				else:
					Store[str(idn)] = [[0, count]]
					List.append(self.data["class"][order[i]])
					Nlist.append(self.data["label"][order[i]])
				count += 2

			canvas.SetLegendItems(len(Store))
			for i in range(1, len(Store) + 1):
				Line.append(wx.lib.plot.PolyMarker(Store[str(i)], marker="square", size=font_size, colour=Cols[i - 1], legend=Nlist[i - 1]))

		elif self.dlg.rbPlotName.GetValue() is True:
			Line = []
			count = 0
			for i in range(len(order)):
				Line.append(wx.lib.plot.PolyMarker((0, count), marker="text", names=name[order[i]], text_colour="black"))
				count += 2

		# plot distances
		Line.append(wx.lib.plot.PolyMarker((0, -0.5), marker="text", names="0", text_colour="black"))
		Line.append(wx.lib.plot.PolyMarker((max(tree[:, 3]), -0.5), marker="text", names="% .2f" % max(tree[:, 3]), text_colour="black"))

		idx = scipy.reshape(scipy.arange(len(tree) + 1), (len(tree) + 1,))
		Nodes = {}
		for i in range(len(tree)):
			# just samples
			if tree[i, 1] >= 0:
				if tree[i, 2] >= 0:
					# sample 1
					x1 = 0
					x2 = tree[i, 3]
					pos = order == int(tree[i, 1])
					pos = pos.tolist()
					for iix in range(len(pos)):
						if pos[iix] == 1:
							y1 = iix * 2
					Line.append(wx.lib.plot.PolyLine(np.array([[x1, y1], [x2, y1]]), colour="black", width=1.5, style=wx.SOLID))
					# sample 2
					pos = order == int(tree[i, 2])
					pos = pos.tolist()
					for iix in range(len(pos)):
						if pos[iix] == 1:
							y2 = iix * 2
					Line.append(wx.lib.plot.PolyLine(np.array([[x1, y2], [x2, y2]]), colour="black", width=1.5, style=wx.SOLID))
					# connect
					Line.append(wx.lib.plot.PolyLine(np.array([[x2, y1], [x2, y2]]), colour="black", width=1.5, style=wx.SOLID))
					# save node coord
					Nodes[str((tree[i, 0] + 1) * -1)] = (x2, (y1 + y2) / 2)

		for i in range(len(tree)):
			# nodes & samples
			if tree[i, 1] >= 0:
				if tree[i, 2] < 0:
					if str(tree[i, 2]) in Nodes:
						# sample first
						x1 = 0
						x2 = tree[i, 3]
						pos = order == int(tree[i, 1])
						pos = pos.tolist()
						for iix in range(len(pos)):
							if pos[iix] == 1:
								y1 = iix * 2
						Line.append(wx.lib.plot.PolyLine(np.array([[x1, y1], [x2, y1]]), colour="black", width=1.5, style=wx.SOLID))
						# node next
						if str(tree[i, 2]) in Nodes:
							x1 = Nodes[str(tree[i, 2])][0]
							x2 = tree[i, 3]
							y2 = Nodes[str(tree[i, 2])][1]
							Line.append(wx.lib.plot.PolyLine(np.array([[x1, y2], [x2, y2]]), colour="black", width=1.5, style=wx.SOLID))
						# connect
						Line.append(wx.lib.plot.PolyLine(np.array([[x2, y1], [x2, y2]]), colour="black", width=1.5, style=wx.SOLID))
						# save node coord
						Nodes[str((tree[i, 0] + 1) * -1)] = (x2, (y1 + y2) / 2)

			if tree[i, 1] < 0:
				if tree[i, 2] >= 0:
					if str(tree[i, 1]) in Nodes:
						# sample first
						x1 = 0
						x2 = tree[i, 3]
						pos = order == int(tree[i, 2])
						pos = pos.tolist()
						for iix in range(len(pos)):
							if pos[iix] == 1:
								y1 = iix * 2
						Line.append(wx.lib.plot.PolyLine(np.array([[x1, y1], [x2, y1]]), colour="black", width=1.5, style=wx.SOLID))
						# node next
						if str(tree[i, 1]) in Nodes:
							x1 = Nodes[str(tree[i, 1])][0]
							x2 = tree[i, 3]
							y2 = Nodes[str(tree[i, 1])][1]
							Line.append(wx.lib.plot.PolyLine(np.array([[x1, y2], [x2, y2]]), colour="black", width=1.5, style=wx.SOLID))
						# connect
						Line.append(wx.lib.plot.PolyLine(np.array([[x2, y1], [x2, y2]]), colour="black", width=1.5, style=wx.SOLID))
						# save node coord
						Nodes[str((tree[i, 0] + 1) * -1)] = (x2, (y1 + y2) / 2)

			if tree[i, 1] < 0:
				if tree[i, 2] < 0:
					# nodes and nodes
					# n1
					x1 = Nodes[str(tree[i, 1])][0]
					x2 = tree[i, 3]
					y1 = Nodes[str(tree[i, 1])][1]
					Line.append(wx.lib.plot.PolyLine(np.array([[x1, y1], [x2, y1]]), colour="black", width=1.5, style=wx.SOLID))
					# n2
					x1 = Nodes[str(tree[i, 2])][0]
					x2 = tree[i, 3]
					y2 = Nodes[str(tree[i, 2])][1]
					Line.append(wx.lib.plot.PolyLine(np.array([[x1, y2], [x2, y2]]), colour="black", width=1.5, style=wx.SOLID))
					# connect
					Line.append(wx.lib.plot.PolyLine(np.array([[x2, y1], [x2, y2]]), colour="black", width=1.5, style=wx.SOLID))
					# save node coord
					Nodes[str((tree[i, 0] + 1) * -1)] = (x2, (y1 + y2) / 2)

		NewPlotLine = wx.lib.plot.PlotGraphics(Line)
		xAx = None  # (minx-0.1,max(tree[:,3])+(0.05*max(tree[:,3])))
		yAx = None  # (-2, (2*len(order))-1)
		canvas.Draw(NewPlotLine)  # ,xAxis=xAx,yAxis=yAx)

		return [NewPlotLine, xAx, yAx]

	def ReportPartitioning(self, textctrl, clusterid, error, nfound, title, centroids=None):
		# report summary
		summary = "".join((title, "\n-------------\n\n", "No. clusters\t\tError\t\tNo. optimal soln.\n", "----------------\t\t--------\t\t------------------------\n", str(max(self.clusterid) + 1), "\t\t\t", "% .2f" % error, "\t\t", str(nfound)))

		# cluster centres
		if centroids is not None:
			if centroids.shape[1] < 40:
				centres = "\n\nCluster centres\n--------------------\n\nCluster/X var."
				for i in range(centroids.shape[1]):
					centres = "".join((centres, "\t", str(i + 1)))
				centres = "".join((centres, "\n"))
				for i in range(centroids.shape[0]):
					for j in range(centroids.shape[1]):
						if j == 0:
							centres = "".join((centres, str(i + 1), "\t\t", "% .2f" % centroids[i, j], "\t"))
						elif 0 < j < centroids.shape[1] - 1:
							centres = "".join((centres, "% .2f" % centroids[i, j], "\t"))
						else:
							centres = "".join((centres, "% .2f" % centroids[i, j], "\n"))
			else:
				centres = "\n\n"
		else:
			centres = "\n\n"

		# confusion matrix
		confmat = "\n\nResults confusion matrix\n--------------------------------\n\nExp./Pred."
		for i in range(int(max(self.data["class"]))):
			confmat = "".join((confmat, "\t", str(i + 1)))
		confmat = "".join((confmat, "\n"))

		confarr = scipy.zeros((int(max(self.data["class"])), int(max(self.data["class"]))))
		for row in range(len(self.data["class"])):
			if self.data["class"][row] == self.clusterid[row] + 1:
				confarr[self.clusterid[row], self.clusterid[row]] = confarr[self.clusterid[row], self.clusterid[row]] + 1
			else:
				confarr[int(self.data["class"][row]) - 1, self.clusterid[row]] = confarr[int(self.data["class"][row]) - 1, self.clusterid[row]] + 1

		for i in range(confarr.shape[0]):
			for j in range(confarr.shape[1]):
				if j == 0:
					confmat = "".join((confmat, str(i + 1), "\t\t", str(confarr[i, j])))
				else:
					confmat = "".join((confmat, "\t", str(confarr[i, j])))
			confmat = "".join((confmat, "\n"))

		report = "".join((summary, centres, confmat))

		textctrl.SetValue(report)


class selFun(wx.Frame):
	def _init_coll_gbsCluster_Growables(self, parent):
		# generated method, don't edit

		parent.AddGrowableCol(0)
		parent.AddGrowableCol(1)

	def _init_coll_gbsCluster_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(wx.StaticText(self, -1, "Cluster Method", style=wx.ALIGN_LEFT), (0, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbKmeans, (1, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbKmedian, (2, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbKmedoids, (3, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddSpacer(wx.Size(8, 8), (4, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbHcluster, (5, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbSingleLink, (6, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbMaxLink, (7, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbAvLink, (8, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbCentLink, (9, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddSpacer(wx.Size(8, 8), (10, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(wx.StaticText(self, -1, "Distance Measure", style=wx.ALIGN_LEFT), (11, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbAbsUncentCorr, (12, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbAbsCorr, (13, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbCityBlock, (14, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbCorrelation, (15, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbEuclidean, (16, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbHarmonicEuc, (17, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbKendalls, (18, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbSpearmans, (19, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbUncentredCorr, (20, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddSpacer(wx.Size(8, 8), (21, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.cbUseClass, (22, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.spnNoPass, (23, 0), border=2, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(wx.StaticText(self, -1, "Iterations", style=wx.ALIGN_LEFT), (23, 1), border=2, flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.rbPlotName, (24, 0), border=2, flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbPlotColours, (25, 0), border=2, flag=wx.EXPAND, span=(1, 2))

	def _init_selparam_sizers(self):
		# generated method, don't edit
		self.gbsCluster = wx.GridBagSizer(hgap=4, vgap=4)
		self.gbsCluster.SetCols(2)
		self.gbsCluster.SetRows(26)
		self.gbsCluster.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
		self.gbsCluster.SetMinSize(wx.Size(200, 439))
		self.gbsCluster.SetEmptyCellSize(wx.Size(10, 8))
		self.gbsCluster.SetFlexibleDirection(wx.VERTICAL)

		self._init_coll_gbsCluster_Items(self.gbsCluster)
		self._init_coll_gbsCluster_Growables(self.gbsCluster)

		self.SetSizer(self.gbsCluster)

	def _init_selfun_ctrls(self, prnt):
		# generated method, don't edit
		wx.Frame.__init__(self, id=wxID_SELFUN, name="selFun", parent=prnt, pos=wx.Point(194, 112), size=wx.Size(295, 540), style=wx.DEFAULT_FRAME_STYLE, title="Clustering Functions")
		self.SetClientSize(wx.Size(287, 501))
		self.SetToolTip("")
		self.Center(wx.BOTH)
		self.SetBackgroundColour(wx.Colour(167, 167, 243))
		self.Bind(wx.EVT_CLOSE, self.OnMiniFrameClose)

		self.rbKmeans = wx.RadioButton(id=-1, label="k-means clustering", name="rbKmeans", parent=self, pos=wx.Point(16, 48), size=wx.Size(128, 21), style=wx.RB_GROUP)
		self.rbKmeans.SetValue(True)
		self.rbKmeans.SetBackgroundColour(wx.Colour(167, 167, 243))
		self.rbKmeans.SetToolTip("")

		self.rbKmedian = wx.RadioButton(id=-1, label="k-medians clustering", name="rbKmedian", parent=self, pos=wx.Point(16, 24), size=wx.Size(128, 21), style=0)
		self.rbKmedian.SetValue(False)
		self.rbKmedian.SetBackgroundColour(wx.Colour(167, 167, 243))
		self.rbKmedian.SetToolTip("")

		self.rbKmedoids = wx.RadioButton(id=-1, label="k-medoids clustering", name="rbKmedoids", parent=self, pos=wx.Point(16, 72), size=wx.Size(120, 21), style=0)
		self.rbKmedoids.SetToolTip("")
		self.rbKmedoids.SetValue(False)
		self.rbKmedoids.SetBackgroundColour(wx.Colour(167, 167, 243))

		self.rbHcluster = wx.RadioButton(id=-1, label="Hierarchical clustering", name="rbHcluster", parent=self, pos=wx.Point(16, 96), size=wx.Size(152, 21), style=0)
		self.rbHcluster.SetToolTip("")
		self.rbHcluster.SetBackgroundColour(wx.Colour(167, 167, 243))
		self.rbHcluster.SetValue(False)

		self.rbSingleLink = wx.RadioButton(id=-1, label="Single linkage", name="rbSingleLink", parent=self, pos=wx.Point(168, 144), size=wx.Size(88, 21), style=wx.RB_GROUP)
		self.rbSingleLink.SetValue(True)
		self.rbSingleLink.SetToolTip("")
		self.rbSingleLink.SetBackgroundColour(wx.Colour(167, 167, 243))

		self.rbMaxLink = wx.RadioButton(id=-1, label="Maximum linkage", name="rbMaxLink", parent=self, pos=wx.Point(40, 144), size=wx.Size(104, 21), style=0)
		self.rbMaxLink.SetValue(False)
		self.rbMaxLink.SetToolTip("")
		self.rbMaxLink.SetBackgroundColour(wx.Colour(167, 167, 243))

		self.rbAvLink = wx.RadioButton(id=-1, label="Average linkage", name="rbAvLink", parent=self, pos=wx.Point(40, 120), size=wx.Size(96, 21), style=0)
		self.rbAvLink.SetValue(False)
		self.rbAvLink.SetToolTip("")
		self.rbAvLink.SetBackgroundColour(wx.Colour(167, 167, 243))

		self.rbCentLink = wx.RadioButton(id=-1, label="Centroid linkage", name="rbCentLink", parent=self, pos=wx.Point(168, 120), size=wx.Size(96, 21), style=0)
		self.rbCentLink.SetValue(False)
		self.rbCentLink.SetToolTip("")
		self.rbCentLink.SetBackgroundColour(wx.Colour(167, 167, 243))

		self.rbEuclidean = wx.RadioButton(id=-1, label="Euclidean", name="rbEuclidean", parent=self, pos=wx.Point(16, 304), size=wx.Size(136, 21), style=wx.RB_GROUP)
		self.rbEuclidean.SetValue(True)
		self.rbEuclidean.SetToolTip("")
		self.rbEuclidean.SetBackgroundColour(wx.Colour(167, 167, 243))

		self.rbCorrelation = wx.RadioButton(id=-1, label="Correlation", name="rbCorrelation", parent=self, pos=wx.Point(16, 280), size=wx.Size(136, 21), style=0)
		self.rbCorrelation.SetValue(False)
		self.rbCorrelation.SetToolTip("")
		self.rbCorrelation.SetBackgroundColour(wx.Colour(167, 167, 243))

		self.rbAbsCorr = wx.RadioButton(id=-1, label="Absolute value of correlation", name="rbAbsCorr", parent=self, pos=wx.Point(16, 232), size=wx.Size(184, 21), style=0)
		self.rbAbsCorr.SetValue(False)
		self.rbAbsCorr.SetToolTip("")
		self.rbAbsCorr.SetBackgroundColour(wx.Colour(167, 167, 243))

		self.rbUncentredCorr = wx.RadioButton(id=-1, label="Uncentred correlation", name="rbUncentredCorr", parent=self, pos=wx.Point(16, 400), size=wx.Size(136, 21), style=0)
		self.rbUncentredCorr.SetValue(False)
		self.rbUncentredCorr.SetToolTip("")
		self.rbUncentredCorr.SetBackgroundColour(wx.Colour(167, 167, 243))

		self.rbAbsUncentCorr = wx.RadioButton(id=-1, label="Absolute uncentred correlation", name="rbAbsUncentCorr", parent=self, pos=wx.Point(16, 208), size=wx.Size(176, 21), style=0)
		self.rbAbsUncentCorr.SetValue(False)
		self.rbAbsUncentCorr.SetToolTip("")
		self.rbAbsUncentCorr.SetBackgroundColour(wx.Colour(167, 167, 243))

		self.rbSpearmans = wx.RadioButton(id=-1, label="Spearmans rank correlation", name="rbSpearmans", parent=self, pos=wx.Point(16, 376), size=wx.Size(168, 21), style=0)
		self.rbSpearmans.SetValue(False)
		self.rbSpearmans.SetToolTip("")
		self.rbSpearmans.SetBackgroundColour(wx.Colour(167, 167, 243))

		self.rbKendalls = wx.RadioButton(id=-1, label="Kendalls rho", name="rbKendalls", parent=self, pos=wx.Point(16, 352), size=wx.Size(136, 21), style=0)
		self.rbKendalls.SetValue(False)
		self.rbKendalls.SetToolTip("")
		self.rbKendalls.SetBackgroundColour(wx.Colour(167, 167, 243))

		self.rbHarmonicEuc = wx.RadioButton(id=-1, label="Harmonically summed Euclidean distance", name="rbHarmonicEuc", parent=self, pos=wx.Point(16, 328), size=wx.Size(224, 21), style=0)
		self.rbHarmonicEuc.SetValue(False)
		self.rbHarmonicEuc.SetToolTip("")
		self.rbHarmonicEuc.SetBackgroundColour(wx.Colour(167, 167, 243))

		self.rbCityBlock = wx.RadioButton(id=-1, label="City-block distance", name="rbCityBlock", parent=self, pos=wx.Point(16, 256), size=wx.Size(136, 21), style=0)
		self.rbCityBlock.SetValue(False)
		self.rbCityBlock.SetToolTip("")
		self.rbCityBlock.SetBackgroundColour(wx.Colour(167, 167, 243))

		self.cbUseClass = wx.CheckBox(id=-1, label="Use class structure", name="cbUseClass", parent=self, pos=wx.Point(16, 448), size=wx.Size(112, 21), style=0)
		self.cbUseClass.SetValue(True)
		self.cbUseClass.SetBackgroundColour(wx.Colour(167, 167, 243))
		self.cbUseClass.SetToolTip("")
		self.cbUseClass.Bind(wx.EVT_CHECKBOX, self.OnCbUseClassCheckbox, id=-1)

		##		  self.stNoPass = wx.StaticText(id=-1, label='Repeats', name='stNoPass',
		##				parent=self, pos=wx.Point(144, 448), size=wx.Size(40, 21),
		##				style=0)
		##		  self.stNoPass.SetToolTip('')
		##		  self.stNoPass.Enable(False)

		self.spnNoPass = wx.SpinCtrl(id=-1, initial=1, max=1000, min=1, name="spnNoPass", parent=self, pos=wx.Point(200, 444), size=wx.Size(80, 23), style=wx.SP_ARROW_KEYS)
		self.spnNoPass.SetValue(1)
		self.spnNoPass.SetToolTip("")
		self.spnNoPass.Enable(False)
		self.spnNoPass.SetRange(1, 1000)

		self.rbPlotName = wx.RadioButton(id=-1, label="Plot using labels", name="rbPlotName", parent=self, pos=wx.Point(16, 480), size=wx.Size(104, 21), style=wx.RB_GROUP)
		self.rbPlotName.SetValue(True)
		self.rbPlotName.SetBackgroundColour(wx.Colour(167, 167, 243))
		self.rbPlotName.SetToolTip("")

		self.rbPlotColours = wx.RadioButton(id=-1, label="Plot using colours", name="rbPlotColours", parent=self, pos=wx.Point(144, 480), size=wx.Size(104, 21), style=0)
		self.rbPlotColours.SetValue(False)
		self.rbPlotColours.SetBackgroundColour(wx.Colour(167, 167, 243))
		self.rbPlotColours.SetToolTip("")

		##		  self.staticBox1 = wx.StaticBox(id=wxID_SELFUNSTATICBOX1, label='Method',
		##				name='staticBox1', parent=self, pos=wx.Point(8, 0),
		##				size=wx.Size(272, 176), style=0)
		##
		##		  self.staticBox2 = wx.StaticBox(id=wxID_SELFUNSTATICBOX2,
		##				label='Distance Measure', name='staticBox2', parent=self,
		##				pos=wx.Point(8, 184), size=wx.Size(272, 248), style=0)

		self._init_selparam_sizers()

	def __init__(self, parent):
		self._init_selfun_ctrls(parent)

	def OnCbUseClassCheckbox(self, event):
		if self.cbUseClass.GetValue() is False:
			self.spnNoPass.Enable(True)
			self.stNoPass.Enable(True)
		else:
			self.spnNoPass.Enable(False)
			self.stNoPass.Enable(False)

	def OnMiniFrameClose(self, event):
		self.Hide()
