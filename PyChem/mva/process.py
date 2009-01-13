# -----------------------------------------------------------------------------
# Name:		   process.py
# Purpose:
#
# Author:	   Roger Jarvis
#
# Created:	   2006/06/20
# RCS-ID:	   $Id$
# Copyright:   (c) 2004
# Licence:	   GNU General Public License
# Description: Spectral pre-processing
#
# 			   A selection of spectral pre-processing functions including
# 			   scaling, filtering, derivatisation and baseline correction
# 			   for use on vibrational spectroscopic data
# -----------------------------------------------------------------------------

import scipy
from scipy import newaxis as nA

from .chemometrics import MLR


def _padarray(myarray, frame, type):
	"""Used in a number of funcs to pad out array cols at start and
	end so that the original shape of the array is maintained
	following processing"""
	(div, mod) = divmod(frame, 2)  # pad array to keep original shape after averaging
	if mod != 0:
		pad = (frame - 1) / 2
	else:
		pad = frame / 2
	size = myarray.shape
	if type == "av":
		start = scipy.transpose(scipy.resize(scipy.transpose(sum(myarray[:, 0:pad], 1) / pad), (pad, size[0])))
		end = scipy.transpose(scipy.resize(scipy.transpose(sum(myarray[:, size[1] - pad : size[1]], 1) / pad), (pad, size[0])))
	elif type == "zero":
		start = end = scipy.transpose(scipy.resize(scipy.zeros((size[0], 1)), (pad, size[0])))
	padarray = scipy.concatenate((start, myarray, end), 1)
	return padarray, size


def _slice(x, index, axis=0):
	"""for slicing arrays"""
	if axis == 0:
		slice = scipy.reshape(x[:, int(index[0])], (x.shape[0], 1))
		for n in range(1, len(index), 1):
			slice = scipy.concatenate((slice, reshape(x[:, int(index[n])], (x.shape[0], 1))), 1)
	elif axis == 1:
		slice = scipy.reshape(x[int(index[0]), :], (1, x.shape[1]))
		for n in range(1, len(index)):
			slice = scipy.concatenate((slice, reshape(x[int(index[n]), :], (1, x.shape[1]))), 0)
	return slice


def emsc(myarray, order, fit=None):
	"""Extended multiplicative scatter correction (Ref H. Martens)
	myarray -	spectral data for background correction
	order -		order of polynomial
	fit -		if None then use average spectrum, otherwise provide a spectrum
				as a column vector to which all others fitted
	corr -		EMSC corrected data
	mx -		fitting spectrum
	"""

	# choose fitting vector
	if fit:
		mx = fit
	else:
		mx = scipy.mean(myarray, axis=0)[:, nA]

	# do fitting
	corr = scipy.zeros(myarray.shape)
	for i in range(len(myarray)):
		b, f, r = MLR(mx, myarray[i, :][:, nA], order)
		corr[i, :] = scipy.reshape((r / b[0, 0]) + mx, (corr.shape[1],))

	return corr


def norm01(myarray):
	"""Scale lowest bin to 0, highest bin to +1"""
	for a in range(myarray.shape[0]):
		diff_myarray_min = myarray[a, :] - min(myarray[a, :])
		diff_max_min = max(myarray[a, :]) - min(myarray[a, :])
		myarray[a, :] = diff_myarray_min / diff_max_min
	return myarray


def normhigh(myarray):
	"""Normalise highest bin to +1"""
	size = myarray.shape
	a = 0
	while a < size[0]:
		max_row = max(myarray[a, :])
		myarray[a, :] = myarray[a, :] / max_row
		a = a + 1
	return myarray


def normtot(myarray):
	"""Normalises to a total of 1 for each row"""
	size_of_myarray = myarray.shape
	sum_of_cols = scipy.transpose(scipy.resize(scipy.sum(myarray, 1), (size_of_myarray[1], size_of_myarray[0])))
	return_normal = myarray / sum_of_cols
	return return_normal


def meancent(myarray):
	"""Mean-centre array (in-place) along axis 0

	Formerly SP_meancent

	>>> a = np.array([[1,2,3,4],[0.1,0.2,-0.7,0.6]])
	>>> a
	array([[ 1. ,  2. ,	 3. ,  4. ],
		   [ 0.1,  0.2, -0.7,  0.6]])
	>>> scipy.mean(a)
	array([ 2.5 ,  0.05])
	>>> SP_meancent(a)
	>>> a
	array([[ 0.45,	0.9 ,  1.85,  1.7 ],
		   [-0.45, -0.9 , -1.85, -1.7 ]])
	"""
	means = scipy.mean(myarray, axis=0)  # Get the mean of each colm
	return scipy.subtract(myarray, means)


def autoscale(a):
	"""Auto-scale array

	>>> a = array([[1,2,3,4],[0.1,0.2,-0.7,0.6],[5,1,7,9]])
	>>> a
	array([[ 1. ,  2. ,	 3. ,  4. ],
		   [ 0.1,  0.2, -0.7,  0.6],
		   [ 5. ,  1. ,	 7. ,  9. ]])
	>>> a = autoscale(a)
	>>> a
	array([[-0.39616816,  1.03490978, -0.02596746, -0.12622317],
		   [-0.74121784, -0.96098765, -0.98676337, -0.93089585],
		   [ 1.137386  , -0.07392213,  1.01273083,	1.05711902]])
	"""
	mean_cols = scipy.resize(sum(a, 0) / a.shape[0], (a.shape))
	std_cols = scipy.resize(scipy.sqrt((sum((a - mean_cols) ** 2, 0)) / (a.shape[0] - 1)), (a.shape))
	return (a - mean_cols) / std_cols


def avgfilt(myarray, F, dim):
	"""Apply a one dimensional mean filter of frame width F.
	dim == 'r' smooths across axis=0, dim == 'c' smooths
	across axis == 1
	"""
	if dim == "c":
		(padarray, origsize) = _padarray(myarray, F, "av")
		a, b = 0, F
		avarray = scipy.zeros((origsize[0], origsize[1]), "d")
		while b < origsize[1] + F:  # average out across columns
			avarray[:, a] = scipy.sum(padarray[:, a:b], 1) / F
			a, b = a + 1, b + 1
		return avarray
	elif dim == "r":
		(padarray, origsize) = _padarray(scipy.transpose(myarray, (1, 0)), F, "av")
		padarray = scipy.transpose(padarray, (1, 0))
		a, b = 0, F
		avarray = scipy.zeros((origsize[1], origsize[0]), "d")
		while b < origsize[1] + F:  # average out across rows
			avarray[a, :] = scipy.sum(padarray[a:b, :]) / F
			a, b = a + 1, b + 1
		return avarray


def avgclass(myarray, mrepclass):
	"""Perform avgfilt across rows by replicate
	class only
	"""
	avg = scipy.zeros((1, myarray.shape[1]))
	idx = scipy.arange(0, mrepclass.shape[0], 1, "i", (mrepclass.shape[0], 1))
	for x in scipy.arange(1, max(mrepclass) + 1, 1):
		slice = _slice(myarray, idx[mrepclass == x], 1)
		avg = scipy.concatenate((avg, avgfilt(slice, len(idx[mrepclass == x]), "r")), 0)
	return avg[1 : myarray.shape[0] + 2]


def derivlin(myarray, frame):
	"""Derivatisation using crude linear fit over a
	specified frame width
	"""
	(padarray, origsize) = _padarray(myarray, frame, "av")
	a, b = 0, frame - 1
	deriv_array = scipy.zeros((origsize[0], origsize[1]), "d")
	while b < origsize[1] + frame - 1:  # derivatise across columns
		deriv_array[:, a] = (padarray[:, a] - padarray[:, b]) / (a - b)
		a, b = a + 1, b + 1
	return deriv_array


def sgolayfilt(myarray, k, F):
	"""Applies a Savitsky-Golay filter of order k and frame width F.
	The order must be odd and the frame width (F) a positive integer of
	a value greater than k
	"""
	frange = scipy.arange(-(F - 1) / 2, ((F - 1) / 2) + 1)
	f, vande = 0, scipy.zeros((F, F))
	while f < F:  # compute Vandemonde matrix
		vande[f, :] = frange**f
		f = f + 1
	vande = scipy.transpose(vande, (1, 0))
	vande = vande[:, 0 : k + 1]
	Q, R = scipy.linalg.qr(vande, vande.shape[1])  # Do QR decomposition

	print(vande.shape)
	print(Q.shape)
	print(R[0 : vande.shape[1]])
	G = scipy.dot(vande, scipy.dot(scipy.linalg.inv(R[0 : vande.shape[1]]), scipy.transpose(scipy.linalg.inv(R[0 : vande.shape[1]]))))  # Find the matrix of differentiators

	B = scipy.dot(G, scipy.transpose(vande))  # Projection matrix

	myarray = scipy.transpose(myarray)
	extract_array, extract_B = myarray[0:F, :], B[(((F - 1) / 2) + 1) : F, :]
	start_array = scipy.dot(extract_B[::-1], extract_array[::-1])  # first bins

	array_size = myarray.shape
	last, mid_array = (F - 1) / 2, scipy.zeros((array_size[0], array_size[1]), "d")
	extract_B = scipy.reshape(B[((F - 1) / 2), :], (F, 1))
	while last < array_size[0] - ((F - 1) / 2):
		mid_array[last, :] = sum((extract_B * myarray[last - ((F - 1) / 2) : last + ((F - 1) / 2) + 1, :]), 0)  # middle bit
		last = last + 1

	extract_array, extract_B = myarray[array_size[0] - F : array_size[0], :], B[0 : (F - 1) / 2, :]
	end_array = scipy.dot(extract_B[::-1], extract_array[::-1])  # last bins

	mid_array[0 : (F - 1) / 2, :], mid_array[array_size[0] - ((F - 1) / 2) : array_size[0], :] = start_array, end_array
	return scipy.transpose(mid_array)


def sgolayderiv(myarray, F):
	"""Take the Savitsky-Golay derivative, F must be 5,7 or 9
	need to make this better
	"""
	array_size = myarray.shape
	if F == 5:
		conv = np.array([-1, 8, 0, -8, 1])
		numb = 12
	elif F == 7:
		conv = np.array([-22, 67, 58, 0, -58, -67, 22])
		numb = 252
	elif F == 9:
		conv = np.array([-86, 142, 193, 126, 0, -126, -193, -142, 86])
		numb = 1188

	conv_array = scipy.convolve(myarray, conv, 1) / numb

	return conv_array


def baseline1(myarray):
	"""Set first bin of each row to zero"""
	size = myarray.shape
	take_array = scipy.transpose(scipy.resize(scipy.transpose(myarray[:, 0]), (size[1], size[0])))
	return myarray - take_array


def baseline2(myarray):
	"""Subtract average of the first and last bin from each bin"""
	size = myarray.shape
	take_array = scipy.transpose(scipy.resize(scipy.transpose((myarray[:, 0] + myarray[:, size[1] - 1]) / 2), (size[1], size[0])))
	return myarray - take_array


def lintrend(myarray):
	"""Subtract a linearly increasing baseline between first and last bins"""
	size, t = myarray.shape, 0
	sub = scipy.zeros((size[0], size[1]), "d")
	while t < size[0]:
		a = myarray[t, 0]
		b = myarray[t, size[1] - 1]
		div = (b - a) / size[1]
		if div == 0:
			div = 1
		ar = scipy.arange(a, b, div, "d")
		sub[t, :] = scipy.resize(ar, (size[1],))
		t = t + 1
	return myarray - sub


def prewittd(myarray):
	"""Prewitt derivatisation from numarray
	can't find this on scipy, so will just ignore
	for the time being
	"""
	return


##	  return prewitt(myarray,1)


def sobeld(myarray):
	"""Sobel derivatisation from numarray
	can't find this on scipy, so will just ignore
	for the time being
	"""
	return


##	  return sobel(myarray,1)

if __name__ == "__main__":
	import doctest

	from . import process

	doctest.testmod(process, verbose=False)
