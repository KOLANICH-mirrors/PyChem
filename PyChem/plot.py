#!/usr/bin/env python2.2

# -----------------------------------------------------------------------------
# Name:		   wx.PyPlot.py
# Purpose:
#
# Author:	   Gordon Williams
#
# Created:	   2003/11/03
# RCS-ID:	   $Id$
# Copyright:   (c) 2002
# Licence:	   Use as you wish.
# -----------------------------------------------------------------------------

"""
This is a simple light weight plotting module that can be used with Boa or
easily integrated into your own wx.Python application.	The emphasis is on small
size and fast plotting for large data sets.	 It has a reasonable number of
features to do line and scatter graphs easily.	It is not as sophisticated or as
powerful as SciPy Plt or Chaco.	 Both of these are great packages but consume
huge amounts of computer resources for simple plots.  They can be found at
http://scipy.com

This file contains two parts; first the re-usable library stuff, then, after
a "if __name__=='__main__'" test, a simple frame and a few default plots
for examples and testing.

Based on wx.PlotCanvas
Written by K.Hinsen, R. Srinivasan;
Ported to wx.Python Harm van der Heijden, feb 1999

Major Additions Gordon Williams Feb. 2003 (g_will@cyberus.ca)
	-More style options
	-Zooming using mouse "rubber band"
	-Scroll left, right
	-Grid(graticule)
	-Printing, preview, and page set up (margins)
	-Axis and title labels
	-Cursor xy axis values
	-Doc strings and lots of comments
	-Optimizations for large number of points
	-Legends
	
Did a lot of work here to speed markers up. Only a factor of 4 improvement
though. Lines are much faster than markers, especially filled markers.	Stay
away from circles and triangles unless you only have a few thousand points.

Times for 25,000 points
Line - 0.078 sec
Markers
Square -				   0.22 sec
dot -					   0.10
circle -				   0.87
cross,plus -			   0.28
triangle, triangle_down -  0.90

Thanks to Chris Barker for getting this version working on Linux.

Zooming controls with mouse (when enabled):
	Left mouse drag - Zoom box.
	Left mouse double click - reset zoom.
	Right mouse click - zoom out centred on click location.
"""

import string
import time

import scipy
import wx


#
# Plotting classes...
#
class PolyPoints:
	"""Base Class for lines and markers
	- All methods are private.
	"""

	def __init__(self, points, attr):
		self.points = np.array(points)
		self.currentScale = (1, 1)
		self.currentShift = (0, 0)
		self.scaled = self.points
		self.attributes = {}
		self.attributes.update(self._attributes)
		for name, value in list(attr.items()):
			if name not in list(self._attributes.keys()):
				raise KeyError("Style attribute incorrect. Should be one of %s" % list(self._attributes.keys()))
			self.attributes[name] = value

	def boundingBox(self):
		if len(self.points) == 0:
			# no curves to draw
			# defaults to (-1,-1) and (1,1) but axis can be set in Draw
			minXY = np.array([-1, -1])
			maxXY = np.array([1, 1])
		else:
			minXY = scipy.minimum.reduce(self.points)
			maxXY = scipy.maximum.reduce(self.points)
		return minXY, maxXY

	def scaleAndShift(self, scale=(1, 1), shift=(0, 0)):
		if len(self.points) == 0:
			# no curves to draw
			return
		if (scale is not self.currentScale) or (shift is not self.currentShift):
			# update point scaling
			self.scaled = scale * self.points + shift
			self.currentScale = scale
			self.currentShift = shift
		# else unchanged use the current scaling

	def getLegend(self):
		return self.attributes["legend"]


class PolyEllipse(PolyPoints):
	"""rmj - class for plotting ellipse, specifically
	for dfa error in pychem"""

	_attributes = {"colour": "black", "width": 1, "dim": (1, 1), "style": wx.SOLID}

	def __init__(self, points, **attr):
		"""Creates PolyEllipse object
		points - sequence array of (x,y) points for each ellipse
		**attr - key word attributes
			Defaults:
				'colour'= 'black',			- wx.Pen Colour any wx.NamedColour
				'width'= 1,					- Pen width
				'dim'=(1,1),				- width & height of ellipse
				'style'= wx.SOLID,			 - wx.Pen style

		"""
		PolyPoints.__init__(self, points, attr)

	def draw(self, dc, printerScale, coord=None):
		colour = self.attributes["colour"]
		width = self.attributes["width"] * printerScale
		dim = self.attributes["dim"]
		style = self.attributes["style"]
		dc.SetPen(wx.Pen(wx.NamedColour(colour), int(width), style))
		dc.SetBrush(wx.TRANSPARENT_BRUSH)

		# set ellipse
		width = dim[0]
		height = dim[1]
		rect = scipy.zeros((len(self.scaled), 4), scipy.Float) + [0.0, 0.0, width, height]
		rect[:, 0:2] = self.scaled
		rect[:, 2:4] = self.currentScale * rect[:, 2:4]
		rect[:, 0:2] = self.scaled - (rect[:, 2:4] / 2)
		dc.DrawEllipseList(rect)


class PolyLine(PolyPoints):
	"""Class to define line type and style
	- All methods except __init__ are private.
	"""

	_attributes = {"colour": "black", "width": 1, "style": wx.SOLID, "legend": ""}

	def __init__(self, points, **attr):
		"""Creates PolyLine object
		points - sequence (array, tuple or list) of (x,y) points making up line
		**attr - key word attributes
			Defaults:
				'colour'= 'black',			- wx.Pen Colour any wx.NamedColour
				'width'= 1,					- Pen width
				'style'= wx.SOLID,			 - wx.Pen style
				'legend'= ''				- Line Legend to display
		"""
		PolyPoints.__init__(self, points, attr)

	def draw(self, dc, printerScale, coord=None):
		colour = self.attributes["colour"]
		width = self.attributes["width"] * printerScale
		style = self.attributes["style"]
		dc.SetPen(wx.Pen(wx.NamedColour(colour), int(width), style))
		if coord == None:
			dc.DrawLines(self.scaled)
		else:
			dc.DrawLines(coord)  # draw legend line

	def getSymExtent(self, printerScale):
		"""Width and Height of Marker"""
		h = self.attributes["width"] * printerScale
		w = 5 * h
		return (w, h)


class PolyMarker(PolyPoints):
	"""Class to define marker type and style
	- All methods except __init__ are private.
	"""

	_attributes = {"colour": "black", "width": 1, "size": 2, "fillcolour": None, "fillstyle": wx.SOLID, "marker": "circle", "legend": "", "names": "XXX", "text_colour": "black", "radius": 0.0}

	def __init__(self, points, **attr):
		"""Creates PolyMarker object
		points - sequence (array, tuple or list) of (x,y) points
		**attr - key word attributes
			Defaults:
				'colour'= 'black',			- wx.Pen Colour any wx.NamedColour
				'width'= 1,					- Pen width
				'size'= 2,					- Marker size
				'fillcolour'= same as colour,	   - wx.Brush Colour any wx.NamedColour
				'fillstyle'= wx.SOLID,	  - wx.Brush fill style (use wx.TRANSPARENT for no fill)
				'marker'= 'circle'			- Marker shape
				'legend'= ''				- Marker Legend to display

			Marker Shapes:
				- 'circle'
				- 'dot'
				- 'square'
				- 'triangle'
				- 'triangle_down'
				- 'cross'
				- 'plus'
				- 'ellipse'
		"""

		PolyPoints.__init__(self, points, attr)

	def draw(self, dc, printerScale, coord=None):
		colour = self.attributes["colour"]
		width = self.attributes["width"] * printerScale
		size = self.attributes["size"] * printerScale
		fillcolour = self.attributes["fillcolour"]
		fillstyle = self.attributes["fillstyle"]
		marker = self.attributes["marker"]

		dc.SetPen(wx.Pen(wx.NamedColour(colour), int(width)))
		if fillcolour:
			dc.SetBrush(wx.Brush(wx.NamedColour(fillcolour), fillstyle))
		else:
			dc.SetBrush(wx.Brush(wx.NamedColour(colour), fillstyle))
		if coord == None:
			self._drawmarkers(dc, self.scaled, marker, size)
		else:
			self._drawmarkers(dc, coord, marker, size)  # draw legend marker

	def getSymExtent(self, printerScale):
		"""Width and Height of Marker"""
		s = 5 * self.attributes["size"] * printerScale
		return (s, s)

	def _drawmarkers(self, dc, coords, marker, size=1):
		f = eval("self._" + marker)
		f(dc, coords, size)

	def _circle(self, dc, coords, size=1):
		fact = 2.5 * size
		wh = 5.0 * size
		rect = scipy.zeros((len(coords), 4), scipy.Float) + [0.0, 0.0, wh, wh]
		rect[:, 0:2] = coords - [fact, fact]
		dc.DrawEllipseList(rect.astype(scipy.Int32))

	def _dot(self, dc, coords, size=1):
		dc.DrawPointList(coords)

	def _square(self, dc, coords, size=1):
		fact = 2.5 * size
		wh = 5.0 * size
		rect = scipy.zeros((len(coords), 4), scipy.Float) + [0.0, 0.0, wh, wh]
		rect[:, 0:2] = coords - [fact, fact]
		dc.DrawRectangleList(rect.astype(scipy.Int32))

	def _triangle(self, dc, coords, size=1):
		shape = [(-2.5 * size, 1.44 * size), (2.5 * size, 1.44 * size), (0.0, -2.88 * size)]
		poly = scipy.repeat(coords, 3)
		poly.shape = (len(coords), 3, 2)
		poly += shape
		dc.DrawPolygonList(poly.astype(scipy.Int32))

	def _triangle_down(self, dc, coords, size=1):
		shape = [(-2.5 * size, -1.44 * size), (2.5 * size, -1.44 * size), (0.0, 2.88 * size)]
		poly = scipy.repeat(coords, 3)
		poly.shape = (len(coords), 3, 2)
		poly += shape
		dc.DrawPolygonList(poly.astype(scipy.Int32))

	def _cross(self, dc, coords, size=1):
		fact = 2.5 * size
		for f in [[-fact, -fact, fact, fact], [-fact, fact, fact, -fact]]:
			lines = scipy.concatenate((coords, coords), axis=1) + f
			dc.DrawLineList(lines.astype(scipy.Int32))

	def _plus(self, dc, coords, size=1):
		fact = 2.5 * size
		for f in [[-fact, 0, fact, 0], [0, -fact, 0, fact]]:
			lines = scipy.concatenate((coords, coords), axis=1) + f
			dc.DrawLineList(lines.astype(scipy.Int32))

	def _text(self, dc, coords, size=1):
		dc.SetTextForeground(self.attributes["text_colour"])
		if len(coords) == 1:
			dc.DrawText(self.attributes["names"], coords[0][0], coords[0][1])
		elif len(coords) == 2:
			dc.DrawText(self.attributes["names"], coords[0], coords[1])


class PlotGraphics:
	"""Container to hold PolyXXX objects and graph labels
	- All methods except __init__ are private.
	"""

	def __init__(self, objects, title="", xLabel="", yLabel=""):
		"""Creates PlotGraphics object
		objects - list of PolyXXX objects to make graph
		title - title shown at top of graph
		xLabel - label shown on x-axis
		yLabel - label shown on y-axis
		"""
		if type(objects) not in [list, tuple]:
			raise TypeError("objects argument should be list or tuple")
		self.objects = objects
		self.title = title
		self.xLabel = xLabel
		self.yLabel = yLabel

	def boundingBox(self):
		p1, p2 = self.objects[0].boundingBox()
		for o in self.objects[1:]:
			p1o, p2o = o.boundingBox()
			p1 = scipy.minimum(p1, p1o)
			p2 = scipy.maximum(p2, p2o)
		return p1, p2

	def scaleAndShift(self, scale=(1, 1), shift=(0, 0)):
		for o in self.objects:
			o.scaleAndShift(scale, shift)

	def setPrinterScale(self, scale):
		"""Thickens up lines and markers only for printing"""
		self.printerScale = scale

	def setXLabel(self, xLabel=""):
		"""Set the X axis label on the graph"""
		self.xLabel = xLabel

	def setYLabel(self, yLabel=""):
		"""Set the Y axis label on the graph"""
		self.yLabel = yLabel

	def setTitle(self, title=""):
		"""Set the title at the top of graph"""
		self.title = title

	def getXLabel(self):
		"""Get x axis label string"""
		return self.xLabel

	def getYLabel(self):
		"""Get y axis label string"""
		return self.yLabel

	def getTitle(self, title=""):
		"""Get the title at the top of graph"""
		return self.title

	def draw(self, dc):
		for o in self.objects:
			# t=time.clock()		  #profile info
			o.draw(dc, self.printerScale)
			# dt= time.clock()-t
			# print o, "time=", dt

	def getSymExtent(self, printerScale):
		"""Get max width and height of lines and markers symbols for legend"""
		symExt = self.objects[0].getSymExtent(printerScale)
		for o in self.objects[1:]:
			oSymExt = o.getSymExtent(printerScale)
			symExt = scipy.maximum(symExt, oSymExt)
		return symExt

	def getLegendNames(self):
		"""Returns list of legend names"""
		lst = [None] * len(self)
		for i in range(len(self)):
			lst[i] = self.objects[i].getLegend()
		return lst

	def __len__(self):
		return len(self.objects)

	def __getitem__(self, item):
		return self.objects[item]


# -------------------------------------------------------------------------------
# Main window that you will want to import into your application.


class PlotCanvas(wx.Window):
	"""Subclass of a wx.Window to allow simple general plotting
	of data with zoom, labels, and automatic axis scaling."""

	def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE, name=""):
		"""Constucts a window, which can be a child of a frame, dialog or
		any other non-control window"""

		wx.Window.__init__(self, parent, id, pos, size, style, name)
		self.border = (1, 1)

		self.SetBackgroundColour(wx.NamedColour("white"))

		wx.EVT_PAINT(self, self.OnPaint)
		wx.EVT_SIZE(self, self.OnSize)

		# Create some mouse events for zooming
		wx.EVT_LEFT_DOWN(self, self.OnMouseLeftDown)
		wx.EVT_LEFT_UP(self, self.OnMouseLeftUp)
		wx.EVT_MOTION(self, self.OnMotion)
		wx.EVT_LEFT_DCLICK(self, self.OnMouseDoubleClick)
		wx.EVT_RIGHT_DOWN(self, self.OnMouseRightDown)

		# set curser as cross-hairs
		self.SetCursor(wx.CROSS_CURSOR)

		# Things for printing
		self.print_data = wx.PrintData()
		self.print_data.SetPaperId(wx.PAPER_LETTER)
		self.print_data.SetOrientation(wx.LANDSCAPE)
		self.pageSetupData = wx.PageSetupDialogData()
		self.pageSetupData.SetMarginBottomRight((25, 25))
		self.pageSetupData.SetMarginTopLeft((25, 25))
		self.pageSetupData.SetPrintData(self.print_data)
		self.printerScale = 1
		self.parent = parent

		# Zooming variables
		self._zoomInFactor = 0.5
		self._zoomOutFactor = 2
		self._zoomCorner1 = np.array([0.0, 0.0])  # left mouse down corner
		self._zoomCorner2 = np.array([0.0, 0.0])  # left mouse up corner
		self._zoomEnabled = False
		self._hasDragged = False

		# Drawing Variables
		self.last_draw = None
		self.original_draw = None
		self._pointScale = 1
		self._pointShift = 0
		self._xSpec = "auto"
		self._ySpec = "auto"
		self._gridEnabled = False
		self._legendEnabled = False
		self._legendItems = None

		# Fonts
		self._fontCache = {}
		self._fontSizeAxis = 10
		self._fontSizeTitle = 15
		self._fontSizeLegend = 7

		# OnSize called to make sure the buffer is initialized.
		# This might result in OnSize getting called twice on some
		# platforms at initialization, but little harm done.
		self.OnSize(None)  # sets the initial size based on client size

		# SaveFile
		wx.InitAllImageHandlers()

	def Copy(self):
		return wx.BitmapDataObject(self._Buffer)

	def SaveFile(self, fileName=""):
		"""Saves the file to the type specified in the extension. If no file
		name is specified a dialog box is provided.	 Returns True if sucessful,
		otherwise False.

		.bmp  Save a Windows bitmap file.
		.xbm  Save an X bitmap file.
		.xpm  Save an XPM bitmap file.
		.png  Save a Portable Network Graphics file.
		.jpg  Save a Joint Photographic Experts Group file.
		"""
		if fileName[-3:].lower() not in ["bmp", "xbm", "xpm", "png", "jpg"]:
			dlg1 = wx.FileDialog(self, "Choose a file with extension bmp, gif, xbm, xpm, png, or jpg", ".", "", "BMP files (*.bmp)|*.bmp|XBM files (*.xbm)|*.xbm|XPM file (*.xpm)|*.xpm|PNG files (*.png)|*.png|JPG files (*.jpg)|*.jpg", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
			try:
				while 1:
					if dlg1.ShowModal() == wx.ID_OK:
						fileName = dlg1.GetPath()
						# Check for proper exension
						if fileName[-3:].lower() not in ["bmp", "xbm", "xpm", "png", "jpg"]:
							dlg2 = wx.MessageDialog(self, "File name extension\n" "must be one of\n" "bmp, xbm, xpm, png, or jpg", "File Name Error", wx.OK | wx.ICON_ERROR)
							try:
								dlg2.ShowModal()
							finally:
								dlg2.Destroy()
						else:
							break  # now save file
					else:  # exit without saving
						return False
			finally:
				dlg1.Destroy()

		# File name has required extension
		fType = fileName[-3:].lower()
		if fType == "bmp":
			tp = wx.BITMAP_TYPE_BMP  # Save a Windows bitmap file.
		elif fType == "xbm":
			tp = wx.BITMAP_TYPE_XBM  # Save an X bitmap file.
		elif fType == "xpm":
			tp = wx.BITMAP_TYPE_XPM  # Save an XPM bitmap file.
		elif fType == "jpg":
			tp = wx.BITMAP_TYPE_JPEG  # Save a JPG file.
		else:
			tp = wx.BITMAP_TYPE_PNG  # Save a PNG file.
		# Save Bitmap
		res = self._Buffer.SaveFile(fileName, tp)
		return res

	def PageSetup(self):
		"""Brings up the page setup dialog"""
		data = self.pageSetupData
		data.SetPrintData(self.print_data)
		dlg = wx.PageSetupDialog(self.parent, data)
		try:
			if dlg.ShowModal() == wx.ID_OK:
				data = dlg.GetPageSetupData()  # returns wx.PageSetupDialogData
				# updates page parameters from dialog
				self.pageSetupData.SetMarginBottomRight(data.GetMarginBottomRight())
				self.pageSetupData.SetMarginTopLeft(data.GetMarginTopLeft())
				self.pageSetupData.SetPrintData(data.GetPrintData())
				self.print_data = data.GetPrintData()  # updates print_data
		finally:
			dlg.Destroy()

	def Printout(self, paper=None):
		"""Print current plot."""
		if paper != None:
			self.print_data.SetPaperId(paper)
		pdd = wx.PrintDialogData()
		pdd.SetPrintData(self.print_data)
		printer = wx.Printer(pdd)
		out = plot_printout(self)
		print_ok = printer.Print(self.parent, out)
		if print_ok:
			self.print_data = printer.GetPrintDialogData().GetPrintData()
		out.Destroy()

	def PrintPreview(self):
		"""Print-preview current plot."""
		printout = plot_printout(self)
		printout2 = plot_printout(self)
		self.preview = wx.PrintPreview(printout, printout2, self.print_data)
		if not self.preview.Ok():
			wx.MessageDialog(self, "Print Preview failed.\n" "Check that default printer is configured\n", "Print error", wx.OK | wx.CENTRE).ShowModal()
		self.preview.SetZoom(30)
		# search up tree to find frame instance
		frameInst = self
		while not isinstance(frameInst, wx.Frame):
			frameInst = frameInst.GetParent()
		frame = wx.PreviewFrame(self.preview, frameInst, "Preview")
		frame.Initialize()
		frame.SetPosition(self.GetPosition())
		frame.SetSize((500, 400))
		frame.Centre(wx.BOTH)
		frame.Show(True)

	def SetFontSizeAxis(self, point=10):
		"""Set the tick and axis label font size (default is 10 point)"""
		self._fontSizeAxis = point

	def GetFontSizeAxis(self):
		"""Get current tick and axis label font size in points"""
		return self._fontSizeAxis

	def SetFontSizeTitle(self, point=15):
		"""Set Title font size (default is 15 point)"""
		self._fontSizeTitle = point

	def GetFontSizeTitle(self):
		"""Get current Title font size in points"""
		return self._fontSizeTitle

	def SetFontSizeLegend(self, point=7):
		"""Set Legend font size (default is 7 point)"""
		self._fontSizeLegend = point

	def GetFontSizeLegend(self):
		"""Get current Legend font size in points"""
		return self._fontSizeLegend

	def SetEnableZoom(self, value):
		"""Set True to enable zooming."""
		if value not in [True, False]:
			raise TypeError("Value should be True or False")
		self._zoomEnabled = value

	def GetEnableZoom(self):
		"""True if zooming enabled."""
		return self._zoomEnabled

	def SetEnableGrid(self, value):
		"""Set True to enable grid."""
		if value not in [True, False]:
			raise TypeError("Value should be True or False")
		self._gridEnabled = value
		self.Redraw()

	def GetEnableGrid(self):
		"""True if grid enabled."""
		return self._gridEnabled

	def SetEnableLegend(self, value):
		"""Set True to enable legend."""
		if value not in [True, False]:
			raise TypeError("Value should be True or False")
		self._legendEnabled = value
		self.Redraw()

	def GetEnableLegend(self):
		"""True if Legend enabled."""
		return self._legendEnabled

	def Reset(self):
		"""Unzoom the plot."""
		if self.original_draw is not None:
			self.Draw(self.original_draw[0], self.original_draw[1], self.original_draw[2])

	def ScrollRight(self, units):
		"""Move view right number of axis units."""
		if self.last_draw is not None:
			graphics, xAxis, yAxis = self.last_draw
			xAxis = (xAxis[0] + units, xAxis[1] + units)
			self.Draw(graphics, xAxis, yAxis)

	def ScrollUp(self, units):
		"""Move view up number of axis units."""
		if self.last_draw is not None:
			graphics, xAxis, yAxis = self.last_draw
			yAxis = (yAxis[0] + units, yAxis[1] + units)
			self.Draw(graphics, xAxis, yAxis)

	def GetXY(self, event):
		"""Takes a mouse event and returns the XY user axis values."""
		screenPos = np.array(event.GetPosition())
		x, y = (screenPos - self._pointShift) / self._pointScale
		return x, y

	def SetXSpec(self, type="auto"):
		"""xSpec- defines x axis type. Can be 'none', 'min' or 'auto'
		where:
			'none' - shows no axis or tick mark values
			'min' - shows min bounding box values
			'auto' - rounds axis range to sensible values
		"""
		self._xSpec = type

	def SetYSpec(self, type="auto"):
		"""ySpec- defines x axis type. Can be 'none', 'min' or 'auto'
		where:
			'none' - shows no axis or tick mark values
			'min' - shows min bounding box values
			'auto' - rounds axis range to sensible values
		"""
		self._ySpec = type

	def SetLegendItems(self, num=10**5):
		"""Truncate the legend so that only a few objects are returned"""
		self._legendItems = num

	def GetXSpec(self):
		"""Returns current XSpec for axis"""
		return self._xSpec

	def GetYSpec(self):
		"""Returns current YSpec for axis"""
		return self._ySpec

	def GetXMaxRange(self):
		"""Returns (minX, maxX) x-axis range for displayed graph"""
		graphics = self.last_draw[0]
		p1, p2 = graphics.boundingBox()  # min, max points of graphics
		xAxis = self._axisInterval(self._xSpec, p1[0], p2[0])  # in user units
		return xAxis

	def GetYMaxRange(self):
		"""Returns (minY, maxY) y-axis range for displayed graph"""
		graphics = self.last_draw[0]
		p1, p2 = graphics.boundingBox()  # min, max points of graphics
		yAxis = self._axisInterval(self._ySpec, p1[1], p2[1])
		return yAxis

	def GetXCurrentRange(self):
		"""Returns (minX, maxX) x-axis for currently displayed portion of graph"""
		return self.last_draw[1]

	def GetYCurrentRange(self):
		"""Returns (minY, maxY) y-axis for currently displayed portion of graph"""
		return self.last_draw[2]

	def Draw(self, graphics, xAxis=None, yAxis=None, dc=None):
		"""Draw objects in graphics with specified x and y axis.
		graphics- instance of PlotGraphics with list of PolyXXX objects
		xAxis - tuple with (min, max) axis range to view
		yAxis - same as xAxis
		dc - drawing context - doesn't have to be specified.
		If it's not, the offscreen buffer is used
		"""
		# check Axis is either tuple or none
		if type(xAxis) not in [type(None), tuple]:
			raise TypeError("xAxis should be None or (minX,maxX)")
		if type(yAxis) not in [type(None), tuple]:
			raise TypeError("yAxis should be None or (minY,maxY)")

		# check case for axis = (a,b) where a==b caused by improper zooms
		if xAxis != None:
			if xAxis[0] == xAxis[1]:
				return
		if yAxis != None:
			if yAxis[0] == yAxis[1]:
				return

		if dc == None:
			# allows using floats for certain functions
			dc = FloatDCWrapper(wx.BufferedDC(wx.ClientDC(self), self._Buffer))
			dc.Clear()

		# set font size for every thing but title and legend
		dc.SetFont(self._getFont(self._fontSizeAxis))

		# sizes axis to axis type, create lower left and upper right corners of plot
		if xAxis == None or yAxis == None:
			# One or both axis not specified in Draw
			p1, p2 = graphics.boundingBox()  # min, max points of graphics
			if xAxis == None:
				xAxis = self._axisInterval(self._xSpec, p1[0], p2[0])  # in user units
			if yAxis == None:
				yAxis = self._axisInterval(self._ySpec, p1[1], p2[1])
			# Adjust bounding box for axis spec
			p1[0], p1[1] = xAxis[0], yAxis[0]  # lower left corner user scale (xmin,ymin)
			p2[0], p2[1] = xAxis[1], yAxis[1]  # upper right corner user scale (xmax,ymax)
		else:
			# Both axis specified in Draw
			p1 = np.array([xAxis[0], yAxis[0]])  # lower left corner user scale (xmin,ymin)
			p2 = np.array([xAxis[1], yAxis[1]])  # upper right corner user scale (xmax,ymax)

		if self.last_draw == None:
			self.x, self.y = xAxis, yAxis
		else:
			if abs(xAxis[0] - xAxis[1]) > abs(self.x[0] - self.x[1]):
				self.x = xAxis
			if abs(yAxis[0] - yAxis[1]) > abs(self.y[0] - self.y[1]):
				self.y = yAxis
			self.original_draw = (graphics, self.x, self.y)

		self.last_draw = (graphics, xAxis, yAxis)  # saves most recient values

		# Get ticks and textExtents for axis if required
		if self._xSpec is not "none":
			xticks = self._ticks(xAxis[0], xAxis[1])
			xTextExtent = dc.GetTextExtent(xticks[-1][1])  # w h of x axis text last number on axis
		else:
			xticks = None
			xTextExtent = (0, 0)  # No text for ticks
		if self._ySpec is not "none":
			yticks = self._ticks(yAxis[0], yAxis[1])
			yTextExtentBottom = dc.GetTextExtent(yticks[0][1])
			yTextExtentTop = dc.GetTextExtent(yticks[-1][1])
			yTextExtent = (max(yTextExtentBottom[0], yTextExtentTop[0]), max(yTextExtentBottom[1], yTextExtentTop[1]))
		else:
			yticks = None
			yTextExtent = (0, 0)  # No text for ticks

		# TextExtents for Title and Axis Labels
		titleWH, xLabelWH, yLabelWH = self._titleLablesWH(dc, graphics)

		# TextExtents for Legend
		legendBoxWH, legendSymExt, legendTextExt = self._legendWH(dc, graphics)

		# room around graph area
		rhsW = max(xTextExtent[0], legendBoxWH[0])  # use larger of number width or legend width
		lhsW = yTextExtent[0] + yLabelWH[1]
		bottomH = max(xTextExtent[1], yTextExtent[1] / 2.0) + xLabelWH[1]
		topH = yTextExtent[1] / 2.0 + titleWH[1]
		textSize_scale = np.array([rhsW + lhsW, bottomH + topH])  # make plot area smaller by text size
		textSize_shift = np.array([lhsW, bottomH])  # shift plot area by this amount

		# drawing title and labels text
		dc.SetFont(self._getFont(self._fontSizeTitle))
		titlePos = (self.plotbox_origin[0] + lhsW + (self.plotbox_size[0] - lhsW - rhsW) / 2.0 - titleWH[0] / 2.0, self.plotbox_origin[1] - self.plotbox_size[1])
		dc.DrawText(graphics.getTitle(), titlePos[0], titlePos[1])
		dc.SetFont(self._getFont(self._fontSizeAxis))
		xLabelPos = (self.plotbox_origin[0] + lhsW + (self.plotbox_size[0] - lhsW - rhsW) / 2.0 - xLabelWH[0] / 2.0, self.plotbox_origin[1] - xLabelWH[1])
		dc.DrawText(graphics.getXLabel(), xLabelPos[0], xLabelPos[1])
		yLabelPos = (self.plotbox_origin[0], self.plotbox_origin[1] - bottomH - (self.plotbox_size[1] - bottomH - topH) / 2.0 + yLabelWH[0] / 2.0)
		if graphics.getYLabel():  # bug fix for Linux

			dc.DrawRotatedText(graphics.getYLabel(), yLabelPos[0], yLabelPos[1], 90)

		# drawing legend makers and text
		if self._legendEnabled:
			if len(graphics) > self._legendItems:
				self._drawLegend(dc, graphics, rhsW, topH, legendBoxWH, legendSymExt, legendTextExt, self._legendItems)
			else:
				self._drawLegend(dc, graphics, rhsW, topH, legendBoxWH, legendSymExt, legendTextExt)

		# allow for scaling and shifting plotted points
		scale = (self.plotbox_size - textSize_scale) / (p2 - p1) * np.array((1, -1))
		shift = -p1 * scale + self.plotbox_origin + textSize_shift * np.array((1, -1))
		self._pointScale = scale  # make available for mouse events
		self._pointShift = shift
		self._drawAxes(dc, p1, p2, scale, shift, xticks, yticks)

		graphics.scaleAndShift(scale, shift)
		graphics.setPrinterScale(self.printerScale)  # thicken up lines and markers if printing

		# set clipping area so drawing does not occur outside axis box
		ptx, pty, rectWidth, rectHeight = self._point2ClientCoord(p1, p2)
		dc.SetClippingRegion(ptx, pty, rectWidth, rectHeight)
		# Draw the lines and markers
		# start = time.clock()
		graphics.draw(dc)
		# print "entire graphics drawing took: %f second"%(time.clock() - start)
		# remove the clipping region
		dc.DestroyClippingRegion()

	def Redraw(self, dc=None):
		"""Redraw the existing plot."""
		if self.last_draw is not None:
			graphics, xAxis, yAxis = self.last_draw
			self.Draw(graphics, xAxis, yAxis, dc)
			try:
				return dc.Close()
			except:
				return None

	def Clear(self):
		"""Erase the window."""
		dc = wx.BufferedDC(wx.ClientDC(self), self._Buffer)
		dc.Clear()
		self.last_draw = None

	def Zoom(self, Center, Ratio):
		"""Zoom on the plot
		Centers on the X,Y coords given in Center
		Zooms by the Ratio = (Xratio, Yratio) given
		"""
		x, y = Center
		if self.last_draw != None:
			(graphics, xAxis, yAxis) = self.last_draw
			w = (xAxis[1] - xAxis[0]) * Ratio[0]
			h = (yAxis[1] - yAxis[0]) * Ratio[1]
			xAxis = (x - w / 2, x + w / 2)
			yAxis = (y - h / 2, y + h / 2)
			self.Draw(graphics, xAxis, yAxis)

	# event handlers **********************************
	def OnMotion(self, event):
		if self._zoomEnabled and event.LeftIsDown():
			if self._hasDragged:
				self._drawRubberBand(self._zoomCorner1, self._zoomCorner2)  # remove old
			else:
				self._hasDragged = True
			self._zoomCorner2[0], self._zoomCorner2[1] = self.GetXY(event)
			self._drawRubberBand(self._zoomCorner1, self._zoomCorner2)  # add new

	def OnMouseLeftDown(self, event):
		self._zoomCorner1[0], self._zoomCorner1[1] = self.GetXY(event)

	def OnMouseLeftUp(self, event):
		if self._zoomEnabled:
			if self._hasDragged == True:
				self._drawRubberBand(self._zoomCorner1, self._zoomCorner2)  # remove old
				self._zoomCorner2[0], self._zoomCorner2[1] = self.GetXY(event)
				self._hasDragged = False  # reset flag
				minX, minY = scipy.minimum(self._zoomCorner1, self._zoomCorner2)
				maxX, maxY = scipy.maximum(self._zoomCorner1, self._zoomCorner2)
				if self.last_draw != None:
					self.Draw(self.last_draw[0], xAxis=(minX, maxX), yAxis=(minY, maxY), dc=None)
			# else: # A box has not been drawn, zoom in on a point
			## this interfered with the double click, so I've disables it.
			# 	 X,Y = self.GetXY(event)
			# 	 self.Zoom( (X,Y), (self._zoomInFactor,self._zoomInFactor) )

	def OnMouseDoubleClick(self, event):
		if self._zoomEnabled:
			self.Reset()

	def OnMouseRightDown(self, event):
		if self._zoomEnabled:
			X, Y = self.GetXY(event)
			self.Zoom((X, Y), (self._zoomOutFactor, self._zoomOutFactor))

	def OnPaint(self, event):
		# All that is needed here is to draw the buffer to screen
		dc = wx.BufferedPaintDC(self, self._Buffer)

	def OnSize(self, event):
		# The Buffer init is done here, to make sure the buffer is always
		# the same size as the Window
		Size = self.GetClientSizeTuple()

		# Make new offscreen bitmap: this bitmap will always have the
		# current drawing in it, so it can be used to save the image to
		# a file, or whatever.
		self._Buffer = wx.EmptyBitmap(Size[0], Size[1])
		self._setSize()
		if self.last_draw is None:
			self.Clear()
		else:
			graphics, xSpec, ySpec = self.last_draw
			self.Draw(graphics, xSpec, ySpec)

	# Private Methods **************************************************
	def _setSize(self, width=None, height=None):
		"""DC width and height."""
		if width == None:
			(self.width, self.height) = self.GetClientSizeTuple()
		else:
			self.width, self.height = width, height
		self.plotbox_size = 0.97 * np.array([self.width, self.height])
		xo = 0.5 * (self.width - self.plotbox_size[0])
		yo = self.height - 0.5 * (self.height - self.plotbox_size[1])
		self.plotbox_origin = np.array([xo, yo])

	def _setPrinterScale(self, scale):
		"""Used to thicken lines and increase marker size for print out."""
		# line thickness on printer is very thin at 600 dot/in. Markers small
		self.printerScale = scale

	def _printDraw(self, printDC):
		"""Used for printing."""
		if self.last_draw != None:
			graphics, xSpec, ySpec = self.last_draw
			self.Draw(graphics, xSpec, ySpec, printDC)

	def _drawLegend(self, dc, graphics, rhsW, topH, legendBoxWH, legendSymExt, legendTextExt, items=None):
		"""Draws legend symbols and text"""
		# top right hand corner of graph box is ref corner
		trhc = self.plotbox_origin + (self.plotbox_size - [rhsW, topH]) * [1, -1]
		legendLHS = 0.091 * legendBoxWH[0]  # border space between legend sym and graph box
		lineHeight = max(legendSymExt[1], legendTextExt[1]) * 1.1  # 1.1 used as space between lines
		dc.SetFont(self._getFont(self._fontSizeLegend))
		if items is None:
			length = len(graphics)
		else:
			length = items

		for i in range(length):
			o = graphics[i]
			s = i * lineHeight
			if isinstance(o, PolyMarker):
				# draw marker with legend
				pnt = (trhc[0] + legendLHS + legendSymExt[0] / 2.0, trhc[1] + s + lineHeight / 2.0)
				o.draw(dc, self.printerScale, coord=np.array([pnt]))
			elif isinstance(o, PolyLine):
				# draw line with legend
				pnt1 = (trhc[0] + legendLHS, trhc[1] + s + lineHeight / 2.0)
				pnt2 = (trhc[0] + legendLHS + legendSymExt[0], trhc[1] + s + lineHeight / 2.0)
				o.draw(dc, self.printerScale, coord=np.array([pnt1, pnt2]))
			else:
				raise TypeError("object is neither PolyMarker or PolyLine instance")
			# draw legend txt
			pnt = (trhc[0] + legendLHS + legendSymExt[0], trhc[1] + s + lineHeight / 2.0 - legendTextExt[1] / 2)
			dc.DrawText(o.getLegend(), pnt[0], pnt[1])
		dc.SetFont(self._getFont(self._fontSizeAxis))  # reset

	def _titleLablesWH(self, dc, graphics):
		"""Draws Title and labels and returns width and height for each"""
		# TextExtents for Title and Axis Labels
		dc.SetFont(self._getFont(self._fontSizeTitle))
		title = graphics.getTitle()
		titleWH = dc.GetTextExtent(title)
		dc.SetFont(self._getFont(self._fontSizeAxis))
		xLabel, yLabel = graphics.getXLabel(), graphics.getYLabel()
		xLabelWH = dc.GetTextExtent(xLabel)
		yLabelWH = dc.GetTextExtent(yLabel)
		return titleWH, xLabelWH, yLabelWH

	def _legendWH(self, dc, graphics):
		"""Returns the size in screen units for legend box"""
		if self._legendEnabled != True:
			legendBoxWH = symExt = txtExt = (0, 0)
		else:
			# find max symbol size
			symExt = graphics.getSymExtent(self.printerScale)
			# find max legend text extent
			dc.SetFont(self._getFont(self._fontSizeLegend))
			txtList = graphics.getLegendNames()
			txtExt = dc.GetTextExtent(txtList[0])
			for txt in graphics.getLegendNames()[1:]:
				txtExt = scipy.maximum(txtExt, dc.GetTextExtent(txt))
			maxW = symExt[0] + txtExt[0]
			maxH = max(symExt[1], txtExt[1])
			# padding .1 for lhs of legend box and space between lines
			maxW = maxW * 1.1
			maxH = maxH * 1.1 * len(txtList)
			dc.SetFont(self._getFont(self._fontSizeAxis))
			legendBoxWH = (maxW, maxH)
		return (legendBoxWH, symExt, txtExt)

	def _drawRubberBand(self, corner1, corner2):
		"""Draws/erases rect box from corner1 to corner2"""
		ptx, pty, rectWidth, rectHeight = self._point2ClientCoord(corner1, corner2)
		# draw rectangle
		dc = wx.ClientDC(self)
		dc.BeginDrawing()
		dc.SetPen(wx.Pen(wx.BLACK))
		dc.SetBrush(wx.Brush(wx.WHITE, wx.TRANSPARENT))
		dc.SetLogicalFunction(wx.INVERT)
		dc.DrawRectangle(ptx, pty, rectWidth, rectHeight)
		dc.SetLogicalFunction(wx.COPY)
		dc.EndDrawing()

	def _getFont(self, size):
		"""Take font size, adjusts if printing and returns wx.Font"""
		s = size * self.printerScale
		of = self.GetFont()
		# Linux speed up to get font from cache rather than X font server
		key = (int(s), of.GetFamily(), of.GetStyle(), of.GetWeight())
		font = self._fontCache.get(key, None)
		if font:
			return font  # yeah! cache hit
		else:
			font = wx.Font(int(s), of.GetFamily(), of.GetStyle(), of.GetWeight())
			self._fontCache[key] = font
			return font

	def _point2ClientCoord(self, corner1, corner2):
		"""Converts user point coords to client screen int coords x,y,width,height"""
		c1 = np.array(corner1)
		c2 = np.array(corner2)
		# convert to screen coords
		pt1 = c1 * self._pointScale + self._pointShift
		pt2 = c2 * self._pointScale + self._pointShift
		# make height and width positive
		pul = scipy.minimum(pt1, pt2)  # Upper left corner
		plr = scipy.maximum(pt1, pt2)  # Lower right corner
		rectWidth, rectHeight = plr - pul
		ptx, pty = pul
		return int(ptx), int(pty), int(rectWidth), int(rectHeight)  # return ints

	def _axisInterval(self, spec, lower, upper):
		"""Returns sensible axis range for given spec"""
		if spec == "none" or spec == "min":
			if lower == upper:
				return lower - 0.5, upper + 0.5
			else:
				return lower, upper
		elif spec == "auto":
			range = upper - lower
			if range == 0.0:
				return lower - 0.5, upper + 0.5
			log = scipy.log10(range)
			power = scipy.floor(log)
			fraction = log - power
			if fraction <= 0.05:
				power = power - 1
			grid = 10.0**power
			lower = lower - lower % grid
			mod = upper % grid
			if mod != 0:
				upper = upper - mod + grid
			return lower, upper
		elif type(spec) == type(()):
			lower, upper = spec
			if lower <= upper:
				return lower, upper
			else:
				return upper, lower
		else:
			raise ValueError(str(spec) + ": illegal axis specification")

	def _drawAxes(self, dc, p1, p2, scale, shift, xticks, yticks):

		penWidth = self.printerScale  # increases thickness for printing only
		dc.SetPen(wx.Pen(wx.NamedColour("BLACK"), int(penWidth)))

		# set length of tick marks--long ones make grid
		if self._gridEnabled:
			x, y, width, height = self._point2ClientCoord(p1, p2)
			yTickLength = width / 2.0 + 1
			xTickLength = height / 2.0 + 1
		else:
			yTickLength = 3 * self.printerScale  # lengthens lines for printing
			xTickLength = 3 * self.printerScale

		if self._xSpec is not "none":
			lower, upper = p1[0], p2[0]
			text = 1
			for y, d in [(p1[1], -xTickLength), (p2[1], xTickLength)]:  # miny, maxy and tick lengths
				a1 = scale * np.array([lower, y]) + shift
				a2 = scale * np.array([upper, y]) + shift
				dc.DrawLine(a1[0], a1[1], a2[0], a2[1])  # draws upper and lower axis line
				for x, label in xticks:
					pt = scale * np.array([x, y]) + shift
					dc.DrawLine(pt[0], pt[1], pt[0], pt[1] + d)  # draws tick mark d units
					if text:
						dc.DrawText(label, pt[0], pt[1])
				text = 0  # axis values not drawn on top side

		if self._ySpec is not "none":
			lower, upper = p1[1], p2[1]
			text = 1
			h = dc.GetCharHeight()
			for x, d in [(p1[0], -yTickLength), (p2[0], yTickLength)]:
				a1 = scale * np.array([x, lower]) + shift
				a2 = scale * np.array([x, upper]) + shift
				dc.DrawLine(a1[0], a1[1], a2[0], a2[1])
				for y, label in yticks:
					pt = scale * np.array([x, y]) + shift
					dc.DrawLine(pt[0], pt[1], pt[0] - d, pt[1])
					if text:
						dc.DrawText(label, pt[0] - dc.GetTextExtent(label)[0], pt[1] - 0.5 * h)
				text = 0  # axis values not drawn on right side

	def _ticks(self, lower, upper):
		ideal = (upper - lower) / 7.0
		log = scipy.log10(ideal)
		power = scipy.floor(log)
		fraction = log - power
		factor = 1.0
		error = fraction
		for f, lf in self._multiples:
			e = scipy.fabs(fraction - lf)
			if e < error:
				error = e
				factor = f
		grid = factor * 10.0**power
		if power > 4 or power < -4:
			format = "%+7.1e"
		elif power >= 0:
			digits = max(1, int(power))
			format = "%" + repr(digits) + ".0f"
		else:
			digits = -int(power)
			format = "%" + repr(digits + 2) + "." + repr(digits) + "f"
		ticks = []
		t = -grid * scipy.floor(-lower / grid)
		while t <= upper:
			ticks.append((t, format % (t,)))
			t = t + grid
		return ticks

	_multiples = [(2.0, scipy.log10(2.0)), (5.0, scipy.log10(5.0))]


# -------------------------------------------------------------------------------
# Used to layout the printer page


class plot_printout(wx.Printout):
	"""Controls how the plot is made in printing and previewing"""

	# Do not change method names in this class,
	# we have to override wx.Printout methods here!
	def __init__(self, graph):
		"""graph is instance of plotCanvas to be printed or previewed"""
		wx.Printout.__init__(self)
		self.graph = graph

	def HasPage(self, page):
		if page == 1:
			return True
		else:
			return False

	def GetPageInfo(self):
		return (0, 1, 1, 1)  # disable page numbers

	def OnPrintPage(self, page):
		dc = FloatDCWrapper(self.GetDC())  # allows using floats for certain functions
		##		  print "PPI Printer",self.GetPPIPrinter()
		##		  print "PPI Screen", self.GetPPIScreen()
		##		  print "DC GetSize", dc.GetSize()
		##		  print "GetPageSizePixels", self.GetPageSizePixels()
		# Note PPIScreen does not give the correct number
		# Calulate everything for printer and then scale for preview
		PPIPrinter = self.GetPPIPrinter()  # printer dots/inch (w,h)
		# PPIScreen= self.GetPPIScreen()		  #screen dots/inch (w,h)
		dcSize = dc.GetSizeTuple()  # DC size
		pageSize = self.GetPageSizePixels()  # page size in terms of pixcels
		clientDcSize = self.graph.GetClientSizeTuple()

		# find what the margins are (mm)
		margLeftSize, margTopSize = self.graph.pageSetupData.GetMarginTopLeft()
		margRightSize, margBottomSize = self.graph.pageSetupData.GetMarginBottomRight()

		# calculate offset and scale for dc
		pixLeft = margLeftSize * PPIPrinter[0] / 25.4  # mm*(dots/in)/(mm/in)
		pixRight = margRightSize * PPIPrinter[0] / 25.4
		pixTop = margTopSize * PPIPrinter[1] / 25.4
		pixBottom = margBottomSize * PPIPrinter[1] / 25.4

		plotAreaW = pageSize[0] - (pixLeft + pixRight)
		plotAreaH = pageSize[1] - (pixTop + pixBottom)

		# ratio offset and scale to screen size if preview
		if self.IsPreview():
			ratioW = float(dcSize[0]) / pageSize[0]
			ratioH = float(dcSize[1]) / pageSize[1]
			pixLeft *= ratioW
			pixTop *= ratioH
			plotAreaW *= ratioW
			plotAreaH *= ratioH

		# rescale plot to page or preview plot area
		self.graph._setSize(plotAreaW, plotAreaH)

		# Set offset and scale
		dc.SetDeviceOrigin(pixLeft, pixTop)

		# Thicken up pens and increase marker size for printing
		ratioW = float(plotAreaW) / clientDcSize[0]
		ratioH = float(plotAreaH) / clientDcSize[1]
		aveScale = (ratioW + ratioH) / 2
		self.graph._setPrinterScale(aveScale)  # tickens up pens for printing

		self.graph._printDraw(dc)
		# rescale back to original
		self.graph._setSize()
		self.graph._setPrinterScale(1)

		return True


# Hack to allow plotting real numbers for the methods listed.
# All others passed directly to DC.
# For Drawing it is used as
# dc = FloatDCWrapper(wx.BufferedDC(wx.ClientDC(self), self._Buffer))
# For printing is is used as
# dc = FloatDCWrapper(self.GetDC())
class FloatDCWrapper:
	def __init__(self, aDC):
		self.theDC = aDC

	def DrawLine(self, x1, y1, x2, y2):
		self.theDC.DrawLine(int(x1), int(y1), int(x2), int(y2))

	def DrawText(self, txt, x, y):
		self.theDC.DrawText(txt, int(x), int(y))

	def DrawRotatedText(self, txt, x, y, angle):
		self.theDC.DrawRotatedText(txt, int(x), int(y), angle)

	def SetClippingRegion(self, x, y, width, height):
		self.theDC.SetClippingRegion(int(x), int(y), int(width), int(height))

	def SetDeviceOrigin(self, x, y):
		self.theDC.SetDeviceOrigin(int(x), int(y))

	def __getattr__(self, name):
		return getattr(self.theDC, name)


# ---------------------------------------------------------------------------
# if running standalone...
#
# 	  ...a sample implementation using the above
#


def __test():
	from wx.Python.lib.dialogs import wxScrolledMessageDialog

	def _draw1Objects():
		# 100 points sin function, plotted as green circles
		data1 = 2.0 * scipy.pi * scipy.arange(200) / 200.0
		data1.shape = (100, 2)
		data1[:, 1] = scipy.sin(data1[:, 0])
		markers1 = PolyMarker(data1, legend="Green Markers", colour="green", marker="circle", size=1)

		# 50 points cos function, plotted as red line
		data1 = 2.0 * scipy.pi * scipy.arange(100) / 100.0
		data1.shape = (50, 2)
		data1[:, 1] = scipy.cos(data1[:, 0])
		lines = PolyLine(data1, legend="Red Line", colour="red")

		# A few more points...
		pi = scipy.pi
		markers2 = PolyMarker([(0.0, 0.0), (pi / 4.0, 1.0), (pi / 2, 0.0), (3.0 * pi / 4.0, -1)], legend="Cross Legend", colour="blue", marker="cross")

		return PlotGraphics([markers1, lines, markers2], "Graph Title", "X Axis", "Y Axis")

	def _draw2Objects():
		# 100 points sin function, plotted as green dots
		data1 = 2.0 * scipy.pi * scipy.arange(200) / 200.0
		data1.shape = (100, 2)
		data1[:, 1] = scipy.sin(data1[:, 0])
		line1 = PolyLine(data1, legend="Green Line", colour="green", width=6, style=wx.DOT)

		# 50 points cos function, plotted as red dot-dash
		data1 = 2.0 * scipy.pi * scipy.arange(100) / 100.0
		data1.shape = (50, 2)
		data1[:, 1] = scipy.cos(data1[:, 0])
		line2 = PolyLine(data1, legend="Red Line", colour="red", width=3, style=wx.DOT_DASH)

		# A few more points...
		pi = scipy.pi
		markers1 = PolyMarker([(0.0, 0.0), (pi / 4.0, 1.0), (pi / 2, 0.0), (3.0 * pi / 4.0, -1)], legend="Cross Hatch Square", colour="blue", width=3, size=6, fillcolour="red", fillstyle=wx.CROSSDIAG_HATCH, marker="square")

		return PlotGraphics([markers1, line1, line2], "Big Markers with Different Line Styles")

	def _draw3Objects():
		markerList = ["circle", "dot", "square", "triangle", "triangle_down", "cross", "plus", "circle"]
		m = []
		for i in range(len(markerList)):
			m.append(PolyMarker([(2 * i + 0.5, i + 0.5)], legend=markerList[i], colour="blue", marker=markerList[i]))
		return PlotGraphics(m, "Selection of Markers", "Minimal Axis", "No Axis")

	def _draw4Objects():
		# 25,000 point line
		data1 = scipy.arange(5e5, 1e6, 10)
		data1.shape = (25000, 2)
		line1 = PolyLine(data1, legend="Wide Line", colour="green", width=5)

		# A few more points...
		markers2 = PolyMarker(data1, legend="Square", colour="blue", marker="square")
		return PlotGraphics([line1, markers2], "25,000 Points", "Value X", "")

	def _draw5Objects():
		# Empty graph with axis defined but no points/lines
		points = []
		line1 = PolyLine(points, legend="Wide Line", colour="green", width=5)
		return PlotGraphics([line1], "Empty Plot With Just Axes", "Value X", "Value Y")

	class AppFrame(wx.Frame):
		def __init__(self, parent, id, title):
			wx.Frame.__init__(self, parent, id, title, wx.PyDefaultPosition, wx.Size(600, 400))

			# Now Create the menu bar and items
			self.mainmenu = wx.MenuBar()

			menu = wx.Menu()
			menu.Append(200, "Page Setup...", "Setup the printer page")
			wx.EVT_MENU(self, 200, self.OnFilePageSetup)

			menu.Append(201, "Print Preview...", "Show the current plot on page")
			wx.EVT_MENU(self, 201, self.OnFilePrintPreview)

			menu.Append(202, "Print...", "Print the current plot")
			wx.EVT_MENU(self, 202, self.OnFilePrint)

			menu.Append(203, "Save Plot...", "Save current plot")
			wx.EVT_MENU(self, 203, self.OnSaveFile)

			menu.Append(205, "E&xit", "Enough of this already!")
			wx.EVT_MENU(self, 205, self.OnFileExit)
			self.mainmenu.Append(menu, "&File")

			menu = wx.Menu()
			menu.Append(206, "Draw1", "Draw plots1")
			wx.EVT_MENU(self, 206, self.OnPlotDraw1)
			menu.Append(207, "Draw2", "Draw plots2")
			wx.EVT_MENU(self, 207, self.OnPlotDraw2)
			menu.Append(208, "Draw3", "Draw plots3")
			wx.EVT_MENU(self, 208, self.OnPlotDraw3)
			menu.Append(209, "Draw4", "Draw plots4")
			wx.EVT_MENU(self, 209, self.OnPlotDraw4)
			menu.Append(210, "Draw5", "Draw plots5")
			wx.EVT_MENU(self, 210, self.OnPlotDraw5)

			menu.Append(211, "&Redraw", "Redraw plots")
			wx.EVT_MENU(self, 211, self.OnPlotRedraw)
			menu.Append(212, "&Clear", "Clear canvas")
			wx.EVT_MENU(self, 212, self.OnPlotClear)
			menu.Append(213, "&Scale", "Scale canvas")
			wx.EVT_MENU(self, 213, self.OnPlotScale)
			menu.Append(214, "Enable &Zoom", "Enable Mouse Zoom", kind=wx.ITEM_CHECK)
			wx.EVT_MENU(self, 214, self.OnEnableZoom)
			menu.Append(215, "Enable &Grid", "Turn on Grid", kind=wx.ITEM_CHECK)
			wx.EVT_MENU(self, 215, self.OnEnableGrid)
			menu.Append(220, "Enable &Legend", "Turn on Legend", kind=wx.ITEM_CHECK)
			wx.EVT_MENU(self, 220, self.OnEnableLegend)
			menu.Append(225, "Scroll Up 1", "Move View Up 1 Unit")
			wx.EVT_MENU(self, 225, self.OnScrUp)
			menu.Append(230, "Scroll Rt 2", "Move View Right 2 Units")
			wx.EVT_MENU(self, 230, self.OnScrRt)
			menu.Append(235, "&Plot Reset", "Reset to original plot")
			wx.EVT_MENU(self, 235, self.OnReset)

			self.mainmenu.Append(menu, "&Plot")

			menu = wx.Menu()
			menu.Append(300, "&About", "About this thing...")
			wx.EVT_MENU(self, 300, self.OnHelpAbout)
			self.mainmenu.Append(menu, "&Help")

			self.SetMenuBar(self.mainmenu)

			# A status bar to tell people what's happening
			self.CreateStatusBar(1)

			self.client = PlotCanvas(self)
			# Create mouse event for showing cursor coords in status bar
			wx.EVT_LEFT_DOWN(self.client, self.OnMouseLeftDown)

		def OnMouseLeftDown(self, event):
			s = "Left Mouse Down at Point: (%.4f, %.4f)" % self.client.GetXY(event)
			self.SetStatusText(s)
			event.Skip()

		def OnFilePageSetup(self, event):
			self.client.PageSetup()

		def OnFilePrintPreview(self, event):
			self.client.PrintPreview()

		def OnFilePrint(self, event):
			self.client.Printout()

		def OnSaveFile(self, event):
			self.client.SaveFile()

		def OnFileExit(self, event):
			self.Close()

		def OnPlotDraw1(self, event):
			self.resetDefaults()
			self.client.Draw(_draw1Objects())

		def OnPlotDraw2(self, event):
			self.resetDefaults()
			self.client.Draw(_draw2Objects())

		def OnPlotDraw3(self, event):
			self.resetDefaults()
			self.client.SetFont(wx.Font(10, wx.SCRIPT, wx.NORMAL, wx.NORMAL))
			self.client.fontSizeAxis = 20
			self.client.fontSizeLegend = 12
			self.client.xSpec = "min"
			self.client.ySpec = "none"
			self.client.Draw(_draw3Objects())

		def OnPlotDraw4(self, event):
			self.resetDefaults()
			drawObj = _draw4Objects()
			self.client.Draw(drawObj)

		##			  #profile
		##			  start = time.clock()
		##			  for x in range(10):
		##				  self.client.Draw(drawObj)
		##			  print "10 plots of Draw4 took: %f sec."%(time.clock() - start)
		##			  #profile end

		def OnPlotDraw5(self, event):
			# Empty plot with just axes
			self.resetDefaults()
			drawObj = _draw5Objects()
			# make the axis X= (0,5), Y=(0,10)
			# (default with None is X= (-1,1), Y= (-1,1))
			self.client.Draw(drawObj, xAxis=(0, 5), yAxis=(0, 10))

		def OnPlotRedraw(self, event):
			self.client.Redraw()

		def OnPlotClear(self, event):
			self.client.Clear()

		def OnPlotScale(self, event):
			if self.client.last_draw != None:
				graphics, xAxis, yAxis = self.client.last_draw
				self.client.Draw(graphics, (1, 3.05), (0, 1))

		def OnEnableZoom(self, event):
			self.client.enableZoom = event.IsChecked()

		def OnEnableGrid(self, event):
			self.client.SetEnableGrid(event.IsChecked())

		def OnEnableLegend(self, event):
			self.client.enableLegend = event.IsChecked()

		def OnScrUp(self, event):
			self.client.ScrollUp(1)

		def OnScrRt(self, event):
			self.client.ScrollRight(2)

		def OnReset(self, event):
			self.client.Reset()

		def OnHelpAbout(self, event):
			about = wx.ScrolledMessageDialog(self, __doc__, "About...")
			about.ShowModal()

		def resetDefaults(self):
			"""Just to reset the fonts back to the PlotCanvas defaults"""
			self.client.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
			self.client.fontSizeAxis = 10
			self.client.fontSizeLegend = 7
			self.client.xSpec = "auto"
			self.client.ySpec = "auto"

	class MyApp(wx.App):
		def OnInit(self):
			frame = AppFrame(wx.NULL, -1, "wx.PlotCanvas")
			frame.Show(True)
			self.SetTopWindow(frame)
			return True

	app = MyApp(0)
	app.MainLoop()


if __name__ == "__main__":
	__test()
