# -----------------------------------------------------------------------------
# Name:		   Cluster.py
# Purpose:
#
# Author:	   Roger Jarvis
#
# Created:	   2007/05/22
# RCS-ID:	   $Id$
# Copyright:   (c) 2006
# Licence:	   GNU General Public Licence
# -----------------------------------------------------------------------------
# Boa:FramePanel:Cluster

import os
import string

import scipy
import wx
import wx.lib.agw.buttonpanel as bp
import wx.lib.agw.foldpanelbar as fpb
import wx.lib.buttons
import wx.lib.plot
from Bio.Cluster import *
from scipy import newaxis as nA
from wx.lib.anchors import LayoutAnchors

from .mva import chemometrics
from .mva.chemometrics import _index
from .Pca import MyPlotCanvas

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
	def _init_coll_bxsClust1_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.bxsClust2, 1, border=0, flag=wx.EXPAND)

	def _init_coll_bxsClust2_Items(self, parent):
		# generated method, don't edit

		parent.AddWindow(self.titleBar, 0, border=0, flag=wx.EXPAND)
		parent.AddWindow(self.Splitter, 1, border=0, flag=wx.EXPAND)

	def _init_cluster_sizers(self):
		# generated method, don't edit
		self.bxsClust1 = wx.BoxSizer(orient=wx.HORIZONTAL)

		self.bxsClust2 = wx.BoxSizer(orient=wx.VERTICAL)

		self._init_coll_bxsClust1_Items(self.bxsClust1)
		self._init_coll_bxsClust2_Items(self.bxsClust2)

		self.SetSizer(self.bxsClust1)

	def _init_ctrls(self, prnt):
		# generated method, don't edit
		wx.Panel.__init__(self, id=wxID_CLUSTER, name="Cluster", parent=prnt, pos=wx.Point(72, 35), size=wx.Size(907, 670), style=wx.TAB_TRAVERSAL)
		self.SetToolTip("")
		self.SetAutoLayout(True)
		self.prnt = prnt

		self.Splitter = wx.SplitterWindow(id=-1, name="Splitter", parent=self, pos=wx.Point(16, 24), size=wx.Size(272, 168), style=wx.SP_3D | wx.SP_LIVE_UPDATE)
		self.Splitter.SetAutoLayout(True)
		self.Splitter.Bind(wx.EVT_SPLITTER_DCLICK, self.OnSplitterDclick)

		self.p1 = wx.Panel(self.Splitter)
		self.p1.SetAutoLayout(True)
		self.p1.Show(True)

		self.optDlg = selFun(self.Splitter)

		self.plcCluster = MyPlotCanvas(id=-1, name="plcCluster", parent=self.p1, pos=wx.Point(0, 0), size=wx.Size(200, 200), style=wx.SUNKEN_BORDER, toolbar=self.prnt.parent.tbMain)
		self.plcCluster.SetToolTip("")
		self.plcCluster.enableZoom = True
		self.plcCluster.fontSizeTitle = 12
		self.plcCluster.fontSizeAxis = 12
		self.plcCluster.xSpec = "none"
		self.plcCluster.ySpec = "none"
		self.plcCluster.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Small Fonts"))
		self.plcCluster.SetConstraints(LayoutAnchors(self.plcCluster, True, True, True, True))

		self.txtCluster = wx.TextCtrl(id=-1, name="txtCluster", parent=self.p1, pos=wx.Point(0, 0), size=wx.Size(200, 200), style=wx.TE_DONTWRAP | wx.HSCROLL | wx.TE_READONLY | wx.SUNKEN_BORDER | wx.TE_MULTILINE | wx.VSCROLL, value="")
		self.txtCluster.SetToolTip("")
		self.txtCluster.SetConstraints(LayoutAnchors(self.txtCluster, True, True, True, True))
		self.txtCluster.Show(False)

		self.titleBar = TitleBar(self, id=-1, text="Cluster Analysis", style=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self.Splitter.SplitVertically(self.optDlg, self.p1, 1)
		self.Splitter.SetMinimumPaneSize(1)

		self._init_cluster_sizers()

	def __init__(self, parent, id, pos, size, style, name):
		self._init_ctrls(parent)

		self.parent = parent

	def Reset(self):
		curve = wx.lib.plot.PolyLine([[0, 0], [1, 1]], colour="white", width=1, style=wx.TRANSPARENT)
		curve = wx.lib.plot.PlotGraphics([curve], "Hierarchical Cluster Analysis", "", "")
		self.plcCluster.Draw(curve)

	def OnSplitterDclick(self, event):
		if self.Splitter.GetSashPosition() <= 5:
			self.Splitter.SetSashPosition(250)
		else:
			self.Splitter.SetSashPosition(1)


class TitleBar(bp.ButtonPanel):
	def _init_btnpanel_ctrls(self, prnt):
		bp.ButtonPanel.__init__(self, parent=prnt, id=-1, text="Cluster Analysis", agwStyle=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

		self.cbxData = wx.Choice(choices=["Raw spectra", "Processed spectra", "PC Scores", "DF Scores"], id=-1, name="cbxData", parent=self, pos=wx.Point(118, 21), size=wx.Size(100, 23), style=0)
		self.cbxData.SetSelection(0)

		self.btnRunClustering = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "run.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Run Cluster Analysis", longHelp="Run Cluster Analysis")
		self.btnRunClustering.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnRunClusteringButton, id=self.btnRunClustering.GetId())

		self.btnExportCluster = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "export.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Export Cluster Results", longHelp="Export Cluster Results")
		self.btnExportCluster.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBtnExportClusterButton, id=self.btnExportCluster.GetId())

		self.setParams = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join("bmp", "params.png"), wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp="Clustering Options", longHelp="Clustering Options")
		self.Bind(wx.EVT_BUTTON, self.OnBtnSetParamsButton, id=self.setParams.GetId())

	def __init__(self, parent, id, text, style, alignment):

		self._init_btnpanel_ctrls(parent)

		self.CreateButtons()

		self.parent = parent

	def CreateButtons(self):
		self.Freeze()

		self.SetProperties()

		self.AddControl(self.cbxData)
		self.AddSeparator()
		self.AddButton(self.setParams)
		self.AddSeparator()
		self.AddButton(self.btnRunClustering)
		self.AddSeparator()
		self.AddButton(self.btnExportCluster)

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

	def getData(self, data):
		self.data = data

	def OnBtnExportClusterButton(self, event):
		event.Skip()

	def OnBtnSetParamsButton(self, event):
		if self.parent.Splitter.GetSashPosition() <= 5:
			self.parent.Splitter.SetSashPosition(250)
		else:
			self.parent.Splitter.SetSashPosition(1)

	def OnBtnRunClusteringButton(self, event):
		self.RunClustering()

	def RunClustering(self):
		# hierarchical cluster analysis
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
			if self.parent.optDlg.rbEuclidean.GetValue() is True:
				seldist = "e"
			elif self.parent.optDlg.rbCorrelation.GetValue() is True:
				seldist = "c"
			elif self.parent.optDlg.rbAbsCorr.GetValue() is True:
				seldist = "a"
			elif self.parent.optDlg.rbUncentredCorr.GetValue() is True:
				seldist = "u"
			elif self.parent.optDlg.rbAbsUncentCorr.GetValue() is True:
				seldist = "x"
			elif self.parent.optDlg.rbSpearmans.GetValue() is True:
				seldist = "s"
			elif self.parent.optDlg.rbKendalls.GetValue() is True:
				seldist = "k"
			elif self.parent.optDlg.rbCityBlock.GetValue() is True:
				seldist = "b"

			# run clustering
			if self.parent.optDlg.rbKmeans.GetValue() is True:
				if self.parent.optDlg.spnNoPass.GetValue() == 1:
					stid = (np.array(self.data["class"][:, 0], "i") - 1).tolist()
					self.clusterid, error, nfound = kcluster(xdata, nclusters=len(scipy.unique(self.data["class"])), transpose=0, npass=1, method="a", dist=seldist, initialid=stid)
				else:
					self.clusterid, error, nfound = kcluster(xdata, nclusters=len(scipy.unique(self.data["class"][:, 0])), transpose=0, npass=self.parent.optDlg.spnNoPass.GetValue(), method="a", dist=seldist)

				self.parent.plcCluster.Show(False)
				self.parent.txtCluster.Show(True)

				centroids, mask = cluster.clustercentroids(xdata, clusterid=self.clusterid, method="a", transpose=0)

				self.ReportPartitioning(self.parent.txtCluster, self.clusterid, error, nfound, "K-means Summary", centroids)

			elif self.parent.optDlg.rbKmedian.GetValue() is True:
				if self.parent.optDlg.spnNoPass.GetValue() == 1:
					stid = (np.array(self.data["class"][:, 0], "i") - 1).tolist()
					self.clusterid, error, nfound = kcluster(xdata, nclusters=len(scipy.unique(self.data["class"][:, 0])), npass=1, method="m", dist=seldist, initialid=stid)
				else:
					self.clusterid, error, nfound = kcluster(xdata, nclusters=len(scipy.unique(self.data["class"][:, 0])), npass=self.parent.optDlg.spnNoPass.GetValue(), method="m", dist=seldist)

				self.parent.plcCluster.Show(False)
				self.parent.txtCluster.Show(True)

				centroids, mask = cluster.clustercentroids(xdata, mask=ones(xdata.shape), clusterid=self.clusterid, method="m", transpose=0)

				self.ReportPartitioning(self.parent.txtCluster, self.clusterid, error, nfound, "K-medians Summary", centroids)

			elif self.parent.optDlg.rbKmedoids.GetValue() is True:
				# generate distance matrix
				distance = cluster.distancematrix(xdata, transpose=0, dist=seldist)

				if self.parent.optDlg.spnNoPass.GetValue() == 1:
					stid = (np.array(self.data["class"][:, 0], "i") - 1).tolist()
					self.clusterid, error, nfound = cluster.kmedoids(distance, nclusters=len(scipy.unique(self.data["class"][:, 0])), npass=1, initialid=stid)
				else:
					self.clusterid, error, nfound = cluster.kmedoids(distance, nclusters=len(scipy.unique(self.data["class"][:, 0])), npass=self.parent.optDlg.spnNoPass.GetValue())

				# rename cluster ids
				for i in range(len(self.clusterid)):
					self.clusterid[i] = self.data["class"][:, 0][self.clusterid[i]] - 1

				self.parent.plcCluster.Show(False)
				self.parent.txtCluster.Show(True)

				self.ReportPartitioning(self.parent.txtCluster, self.clusterid, error, nfound, "K-medoids Summary")

			elif self.parent.optDlg.rbHcluster.GetValue() is True:
				# get clustering method
				if self.parent.optDlg.rbSingleLink.GetValue() is True:
					Hmeth = "s"
				elif self.parent.optDlg.rbMaxLink.GetValue() is True:
					Hmeth = "m"
				elif self.parent.optDlg.rbAvLink.GetValue() is True:
					Hmeth = "a"
				elif self.parent.optDlg.rbCentLink.GetValue() is True:
					Hmeth = "c"

				# run hca
				tree = treecluster(data=xdata, method=Hmeth, dist=seldist)

				# scale tree
				tree.scale()

				# divide into clusters
				##				  tree.cut(len(scipy.unique(self.data['class'][:,0])))

				# determine tree structure
				self.data["tree"], self.data["order"] = self.treestructure(tree, scipy.arange(len(tree) + 1))

				# draw tree
				self.drawTree(self.parent.plcCluster, self.data["tree"], self.data["order"], self.data["label"])

				self.parent.plcCluster.Show(True)
				self.parent.txtCluster.Show(False)

		##			  #enable export
		##			  if self.parent.optDlg.rbHcluster.GetValue() is True:
		##				  self.btnExportCluster.Enable(1)
		##			  else:
		##				  self.btnExportCluster.Enable(0)
		except Exception as error:
			errorBox(self, "%s" % str(error))
			raise

	def treestructure(self, tree, order):
		# determine hierarchical tree structure
		clusters, nodedist = [], []
		nodes = tree[:]

		for i in range(len(tree)):
			clusters.append([nodes[i].left, nodes[i].right])
			nodedist.append([nodes[i].distance])

		nnodes = len(tree)

		nodeid = scipy.zeros((nnodes, 4), "d")
		nodecounts = scipy.zeros(nnodes)
		nodeorder = scipy.zeros(nnodes, "d")
		nodedist = np.array(nodedist)
		for nodeindex in range(nnodes):
			min1 = clusters[nodeindex][0]
			min2 = clusters[nodeindex][1]
			nodeid[nodeindex, 0] = nodeindex
			if min1 < 0:
				index1 = -min1 - 1
				order1 = nodeorder[index1]
				counts1 = nodecounts[index1]
				nodeid[nodeindex, 1] = min1
			else:
				order1 = order[min1]
				counts1 = 1
				nodeid[nodeindex, 1] = min1
			if min2 < 0:
				index2 = -min2 - 1
				order2 = nodeorder[index2]
				counts2 = nodecounts[index2]
				nodeid[nodeindex, 2] = min2
			else:
				order2 = order[min2]
				counts2 = 1
				nodeid[nodeindex, 2] = min2
			nodeid[nodeindex, 3] = nodedist[nodeindex]
			nodecounts[nodeindex] = counts1 + counts2
			nodeorder[nodeindex] = (counts1 * order1 + counts2 * order2) / (counts1 + counts2)

		# Now set up order based on the tree structure
		index = self.treeindex(clusters, nodedist, order)

		return nodeid, index

	def treeindex(self, clusters, linkdist, order):
		nodeindex = 0
		nnodes = len(clusters)
		nodecounts = scipy.zeros(nnodes)
		nodeorder = scipy.zeros(nnodes, "d")
		nodedist = np.array(linkdist)
		for nodeindex in range(nnodes):
			min1 = clusters[nodeindex][0]
			min2 = clusters[nodeindex][1]
			if min1 < 0:
				index1 = -min1 - 1
				order1 = nodeorder[index1]
				counts1 = nodecounts[index1]
				nodedist[nodeindex] = max(nodedist[nodeindex], nodedist[index1])
			else:
				order1 = order[min1]
				counts1 = 1

			if min2 < 0:
				index2 = -min2 - 1
				order2 = nodeorder[index2]
				counts2 = nodecounts[index2]
				nodedist[nodeindex] = max(nodedist[nodeindex], nodedist[index2])
			else:
				order2 = order[min2]
				counts2 = 1
			nodecounts[nodeindex] = counts1 + counts2
			nodeorder[nodeindex] = (counts1 * order1 + counts2 * order2) / (counts1 + counts2)
		# Now set up order based on the tree structure
		index = self.treesort(order, nodeorder, nodecounts, clusters)
		return index

	def treesort(self, order, nodeorder, nodecounts, NodeElement):
		nNodes = len(NodeElement)
		nElements = nNodes + 1
		neworder = scipy.zeros(nElements, "d")
		clusterids = list(range(nElements))
		for i in range(nNodes):
			i1 = NodeElement[i][0]
			i2 = NodeElement[i][1]
			if i1 < 0:
				order1 = nodeorder[-i1 - 1]
				count1 = nodecounts[-i1 - 1]
			else:
				order1 = order[i1]
				count1 = 1
			if i2 < 0:
				order2 = nodeorder[-i2 - 1]
				count2 = nodecounts[-i2 - 1]
			else:
				order2 = order[i2]
				count2 = 1
			# If order1 and order2 are equal, their order is determined by the order in which they were clustered
			if i1 < i2:
				if order1 < order2:
					increase = count1
				else:
					increase = count2
				for j in range(nElements):
					clusterid = clusterids[j]
					if clusterid == i1 and order1 >= order2:
						neworder[j] += increase
					if clusterid == i2 and order1 < order2:
						neworder[j] += increase
					if clusterid == i1 or clusterid == i2:
						clusterids[j] = -i - 1
			else:
				if order1 <= order2:
					increase = count1
				else:
					increase = count2
				for j in range(nElements):
					clusterid = clusterids[j]
					if clusterid == i1 and order1 > order2:
						neworder[j] += increase
					if clusterid == i2 and order1 <= order2:
						neworder[j] += increase
					if clusterid == i1 or clusterid == i2:
						clusterids[j] = -i - 1
		return scipy.argsort(neworder)

	def drawTree(self, canvas, tree, order, labels, tit="", xL="", yL=""):
		##		  colourList = ['BLUE', 'BROWN', 'CYAN','GREY', 'GREEN', 'MAGENTA',
		##					  'ORANGE', 'PURPLE', 'VIOLET']

		# set font size
		font_size = 8

		canvas.fontSizeAxis = font_size
		canvas.enableLegend = 0

		##		  #do level 1
		##		  List,Cols,ccount = [],[],0
		##		  for i in range(len(tree)):
		##			  if self.data['class'][:,0][i] not in List:
		##				  List.append(self.data['class'][:,0][i])
		####				Cols.append(colourList[ccount])
		##				  ccount += 1
		##				  if ccount == len(colourList):
		##					  ccount = 0
		minx = 0
		##		  if self.parent.optDlg.rbPlotColours.GetValue() is True:
		##			  pass
		##			  canvas.enableLegend = (1)
		##			  Line,List,Nlist,Store = [],[],[],{}
		##			  count = 0
		##			  for i in range(len(order)):
		##				  idn = int(self.data['class'][:,0][order[i]])
		##				  #plot names
		##				  if idn in List:
		##					  Store[str(idn)] = scipy.concatenate((Store[str(idn)],[[0,count]]),0)
		##				  else:
		##					  Store[str(idn)] = [[0,count]]
		##					  List.append(self.data['class'][:,0][order[i]])
		##					  Nlist.append(self.data['label'][order[i]])
		##				  count += 2
		##
		##			  canvas.SetLegendItems(len(Store))
		##			  for i in range(1,len(Store)+1):
		##				  Line.append(wx.lib.plot.PolyMarker(Store[str(i)],marker='square',size=font_size,
		##											  colour=Cols[i-1],legend=Nlist[i-1]))

		##		  elif self.parent.optDlg.rbPlotName.GetValue() is True:
		Line = []
		count = 0
		for i in range(len(order)):
			Line.append(wx.lib.plot.PolyMarker(np.array([[0, count], [0, count]]), marker="text", labels=[labels[int(order[i])], labels[int(order[i])]]))
			count += 2

		# plot distances
		Line.append(wx.lib.plot.PolyMarker(np.array([[0, -2]]), marker="text", labels="0"))
		Line.append(wx.lib.plot.PolyMarker(np.array([[max(tree[:, 3]), -2]]), marker="text", labels="% .2f" % max(tree[:, 3])))

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

		canvas.Draw(wx.lib.plot.PlotGraphics(Line, title=tit, xLabel=xL, yLabel=yL))

	def ReportPartitioning(self, textctrl, clusterid, error, nfound, title, centroids=None):
		# report summary
		summary = "".join((title, "\n-----------------------\n\n", "No. clusters\t\tError\t\tNo. optimal soln.\n", "----------------\t\t--------\t\t------------------------\n", str(max(self.clusterid) + 1), "\t\t\t", "% .2f" % error, "\t\t", str(nfound)))

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
		for i in range(int(max(self.data["class"][:, 0]))):
			confmat = "".join((confmat, "\t", str(i + 1)))
		confmat = "".join((confmat, "\n"))

		confarr = scipy.zeros((int(max(self.data["class"][:, 0])), int(max(self.data["class"][:, 0]))))
		for row in range(len(self.data["class"][:, 0])):
			if self.data["class"][:, 0][row] == self.clusterid[row] + 1:
				confarr[self.clusterid[row], self.clusterid[row]] = confarr[self.clusterid[row], self.clusterid[row]] + 1
			else:
				confarr[int(self.data["class"][:, 0][row]) - 1, self.clusterid[row]] = confarr[int(self.data["class"][:, 0][row]) - 1, self.clusterid[row]] + 1

		for i in range(confarr.shape[0]):
			for j in range(confarr.shape[1]):
				if j == 0:
					confmat = "".join((confmat, str(i + 1), "\t\t", str(confarr[i, j])))
				else:
					confmat = "".join((confmat, "\t", str(confarr[i, j])))
			confmat = "".join((confmat, "\n"))

		report = "".join((summary, centres, confmat))

		textctrl.SetValue(report)


class selFun(fpb.FoldPanelBar):
	def _init_coll_gbsClusterMethod_Items(self, parent):
		parent.AddWindow(self.rbKmeans, (0, 0), flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbKmedian, (1, 0), flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbKmedoids, (2, 0), flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(self.rbHcluster, (3, 0), flag=wx.EXPAND, span=(1, 2))
		parent.AddWindow(wx.StaticText(self.methPnl, -1, "No. iterations", style=wx.ALIGN_LEFT), (4, 0), flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.spnNoPass, (4, 1), flag=wx.EXPAND, span=(1, 1))
		parent.AddSpacer(wx.Size(8, 8), (5, 0), flag=wx.EXPAND, span=(2, 2))

	def _init_coll_gbsLinkageMethod_Items(self, parent):
		parent.AddWindow(self.rbSingleLink, (0, 0), flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.rbMaxLink, (1, 0), flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.rbAvLink, (2, 0), flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.rbCentLink, (3, 0), flag=wx.EXPAND, span=(1, 1))
		parent.AddSpacer(wx.Size(8, 8), (4, 0), flag=wx.EXPAND, span=(1, 1))

	def _init_coll_gbsDistanceMeasure_Items(self, parent):
		parent.AddWindow(self.rbAbsUncentCorr, (0, 0), flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.rbAbsCorr, (1, 0), flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.rbCityBlock, (2, 0), flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.rbCorrelation, (3, 0), flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.rbEuclidean, (4, 0), flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.rbKendalls, (5, 0), flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.rbSpearmans, (6, 0), flag=wx.EXPAND, span=(1, 1))
		parent.AddWindow(self.rbUncentredCorr, (7, 0), flag=wx.EXPAND, span=(1, 1))
		parent.AddSpacer(wx.Size(8, 8), (8, 0), flag=wx.EXPAND, span=(2, 1))

	def _init_selparam_sizers(self):
		self.gbsClusterMethod = wx.GridBagSizer(5, 5)

		self.gbsLinkageMethod = wx.GridBagSizer(5, 5)

		self.gbsDistanceMeasure = wx.GridBagSizer(5, 5)

		self._init_coll_gbsClusterMethod_Items(self.gbsClusterMethod)
		self._init_coll_gbsLinkageMethod_Items(self.gbsLinkageMethod)
		self._init_coll_gbsDistanceMeasure_Items(self.gbsDistanceMeasure)

		self.gbsClusterMethod.AddGrowableCol(0)
		self.gbsClusterMethod.AddGrowableCol(1)
		self.gbsLinkageMethod.AddGrowableCol(0)
		self.gbsDistanceMeasure.AddGrowableCol(0)

		self.clustType.SetSizer(self.gbsClusterMethod)
		self.linkType.SetSizer(self.gbsLinkageMethod)
		self.distType.SetSizer(self.gbsDistanceMeasure)

	def _init_selfun_ctrls(self, prnt):
		fpb.FoldPanelBar.__init__(self, prnt, -1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=fpb.FPB_DEFAULT_STYLE | fpb.FPB_SINGLE_FOLD)
		self.SetConstraints(LayoutAnchors(self, True, True, True, True))
		self.SetAutoLayout(True)

		icons = wx.ImageList(16, 16)
		icons.Add(wx.Bitmap(os.path.join("bmp", "arrown.png"), wx.BITMAP_TYPE_PNG))
		icons.Add(wx.Bitmap(os.path.join("bmp", "arrows.png"), wx.BITMAP_TYPE_PNG))

		self.clustType = self.AddFoldPanel("Cluster method", collapsed=True, foldIcons=icons)

		self.distType = self.AddFoldPanel("Distance measure", collapsed=True, foldIcons=icons)

		self.linkType = self.AddFoldPanel("Linkage method (HCA)", collapsed=True, foldIcons=icons)

		self.methPnl = wx.Panel(id=-1, name="methPnl", parent=self.clustType, pos=wx.Point(0, 0), size=wx.Size(200, 220), style=wx.TAB_TRAVERSAL)
		self.methPnl.SetToolTip("")

		self.distPnl = wx.Panel(id=-1, name="distPnl", parent=self.distType, pos=wx.Point(0, 0), size=wx.Size(200, 290), style=wx.TAB_TRAVERSAL)
		self.distPnl.SetToolTip("")

		self.linkPnl = wx.Panel(id=-1, name="linkPnl", parent=self.linkType, pos=wx.Point(0, 0), size=wx.Size(200, 150), style=wx.TAB_TRAVERSAL)
		self.linkPnl.SetToolTip("")

		self.rbKmeans = wx.RadioButton(id=-1, label="k-means clustering", name="rbKmeans", parent=self.methPnl, pos=wx.Point(16, 48), size=wx.Size(128, 21), style=wx.RB_GROUP)
		self.rbKmeans.SetValue(True)
		self.rbKmeans.SetToolTip("")

		self.rbKmedian = wx.RadioButton(id=-1, label="k-medians clustering", name="rbKmedian", parent=self.methPnl, pos=wx.Point(16, 24), size=wx.Size(128, 21), style=0)
		self.rbKmedian.SetValue(False)
		self.rbKmedian.SetToolTip("")

		self.rbKmedoids = wx.RadioButton(id=-1, label="k-medoids clustering", name="rbKmedoids", parent=self.methPnl, pos=wx.Point(16, 72), size=wx.Size(120, 21), style=0)
		self.rbKmedoids.SetToolTip("")
		self.rbKmedoids.SetValue(False)

		self.rbHcluster = wx.RadioButton(id=-1, label="Hierarchical clustering", name="rbHcluster", parent=self.methPnl, pos=wx.Point(16, 96), size=wx.Size(152, 21), style=0)
		self.rbHcluster.SetToolTip("")
		self.rbHcluster.SetValue(True)

		self.rbSingleLink = wx.RadioButton(id=-1, label="Single linkage", name="rbSingleLink", parent=self.linkPnl, pos=wx.Point(168, 144), size=wx.Size(88, 21), style=wx.RB_GROUP)
		self.rbSingleLink.SetValue(True)
		self.rbSingleLink.SetToolTip("")

		self.rbMaxLink = wx.RadioButton(id=-1, label="Maximum linkage", name="rbMaxLink", parent=self.linkPnl, pos=wx.Point(40, 144), size=wx.Size(104, 21), style=0)
		self.rbMaxLink.SetValue(False)
		self.rbMaxLink.SetToolTip("")

		self.rbAvLink = wx.RadioButton(id=-1, label="Average linkage", name="rbAvLink", parent=self.linkPnl, pos=wx.Point(40, 120), size=wx.Size(96, 21), style=0)
		self.rbAvLink.SetValue(False)
		self.rbAvLink.SetToolTip("")

		self.rbCentLink = wx.RadioButton(id=-1, label="Centroid linkage", name="rbCentLink", parent=self.linkPnl, pos=wx.Point(168, 120), size=wx.Size(96, 21), style=0)
		self.rbCentLink.SetValue(False)
		self.rbCentLink.SetToolTip("")

		self.rbEuclidean = wx.RadioButton(id=-1, label="Euclidean", name="rbEuclidean", parent=self.distPnl, pos=wx.Point(16, 304), size=wx.Size(136, 21), style=wx.RB_GROUP)
		self.rbEuclidean.SetValue(True)
		self.rbEuclidean.SetToolTip("")

		self.rbCorrelation = wx.RadioButton(id=-1, label="Correlation", name="rbCorrelation", parent=self.distPnl, pos=wx.Point(16, 280), size=wx.Size(136, 21), style=0)
		self.rbCorrelation.SetValue(False)
		self.rbCorrelation.SetToolTip("")

		self.rbAbsCorr = wx.RadioButton(id=-1, label="Absolute value of correlation", name="rbAbsCorr", parent=self.distPnl, pos=wx.Point(16, 232), size=wx.Size(184, 21), style=0)
		self.rbAbsCorr.SetValue(False)
		self.rbAbsCorr.SetToolTip("")

		self.rbUncentredCorr = wx.RadioButton(id=-1, label="Uncentred correlation", name="rbUncentredCorr", parent=self.distPnl, pos=wx.Point(16, 400), size=wx.Size(136, 21), style=0)
		self.rbUncentredCorr.SetValue(False)
		self.rbUncentredCorr.SetToolTip("")

		self.rbAbsUncentCorr = wx.RadioButton(id=-1, label="Absolute uncentred correlation", name="rbAbsUncentCorr", parent=self.distPnl, pos=wx.Point(16, 208), size=wx.Size(176, 21), style=0)
		self.rbAbsUncentCorr.SetValue(False)
		self.rbAbsUncentCorr.SetToolTip("")

		self.rbSpearmans = wx.RadioButton(id=-1, label="Spearmans rank correlation", name="rbSpearmans", parent=self.distPnl, pos=wx.Point(16, 376), size=wx.Size(168, 21), style=0)
		self.rbSpearmans.SetValue(False)
		self.rbSpearmans.SetToolTip("")

		self.rbKendalls = wx.RadioButton(id=-1, label="Kendalls rho", name="rbKendalls", parent=self.distPnl, pos=wx.Point(16, 352), size=wx.Size(136, 21), style=0)
		self.rbKendalls.SetValue(False)
		self.rbKendalls.SetToolTip("")

		self.rbCityBlock = wx.RadioButton(id=-1, label="City-block distance", name="rbCityBlock", parent=self.distPnl, pos=wx.Point(16, 256), size=wx.Size(136, 21), style=0)
		self.rbCityBlock.SetValue(False)
		self.rbCityBlock.SetToolTip("")

		##		  self.cbUseClass = wx.CheckBox(id=-1, label='Use class structure',
		##				name='cbUseClass', parent=self.methPnl, pos=wx.Point(16, 448),
		##				size=wx.Size(112, 21), style=0)
		##		  self.cbUseClass.SetValue(True)
		##		  self.cbUseClass.SetToolTip('')
		##		  self.cbUseClass.Bind(wx.EVT_CHECKBOX, self.OnCbUseClassCheckbox, id=-1)

		self.spnNoPass = wx.SpinCtrl(id=-1, initial=1, max=1000, min=1, name="spnNoPass", parent=self.methPnl, pos=wx.Point(200, 444), size=wx.Size(80, 23), style=wx.SP_ARROW_KEYS)
		self.spnNoPass.SetValue(1)
		self.spnNoPass.SetToolTip("")
		self.spnNoPass.SetRange(1, 1000)

		self.spnNumClass = wx.SpinCtrl(id=-1, initial=1, max=1000, min=1, name="spnNumClass", parent=self.methPnl, pos=wx.Point(200, 444), size=wx.Size(80, 23), style=wx.SP_ARROW_KEYS)
		self.spnNumClass.SetValue(1)
		self.spnNumClass.SetToolTip("")
		self.spnNumClass.SetRange(1, 1000)

		self.rbPlotName = wx.RadioButton(id=-1, label="Plot using labels", name="rbPlotName", parent=self.distPnl, pos=wx.Point(16, 480), size=wx.Size(104, 21), style=wx.RB_GROUP)
		self.rbPlotName.SetValue(True)
		self.rbPlotName.SetToolTip("")
		self.rbPlotName.Show(False)

		self.rbPlotColours = wx.RadioButton(id=-1, label="Plot using colours", name="rbPlotColours", parent=self.distPnl, pos=wx.Point(144, 480), size=wx.Size(104, 21), style=0)
		self.rbPlotColours.SetValue(False)
		self.rbPlotColours.SetToolTip("")
		self.rbPlotColours.Show(False)

		self.AddFoldPanelWindow(self.clustType, self.methPnl, fpb.FPB_ALIGN_WIDTH)
		self.AddFoldPanelWindow(self.distType, self.distPnl, fpb.FPB_ALIGN_WIDTH)
		self.AddFoldPanelWindow(self.linkType, self.linkPnl, fpb.FPB_ALIGN_WIDTH)

		self._init_selparam_sizers()

	def __init__(self, parent):
		self._init_selfun_ctrls(parent)

		self.Expand(self.clustType)
		self.Expand(self.distType)
		self.Expand(self.linkType)

	def OnCbUseClassCheckbox(self, event):
		if self.cbUseClass.GetValue() is False:
			self.spnNoPass.Enable(True)
		else:
			self.spnNoPass.Enable(False)
