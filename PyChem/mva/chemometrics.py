# -----------------------------------------------------------------------------
# Name:		   chemometrics.py
# Purpose:
#
# Author:	   Roger Jarvis
#
# Created:	   2006/06/20
# RCS-ID:	   $Id$
# Copyright:   (c) 2004
# Licence:	   GNU General Public Licence
# Description: Chemometrics toolbox for Python
#
# 			   Includes:
# 				-Partial least squares regression (PLS1 and PLS2)
# 				-Principal components analysis
# 				-Canonical variates analysis (CVA)
# -----------------------------------------------------------------------------

import copy
import string

import scipy
import scipy.linalg
from scipy import newaxis as nA


def _fdot(a, b):
	"""Dot product for large arrays, faster than numarrays dot
	depending on the spec of the computer being used"""
	product = scipy.zeros((a.shape[0], b.shape[1]), "d")
	r = 0
	while r < a.shape[0]:
		product[r, :] = scipy.sum(scipy.reshape(a[r, :], (a.shape[1], 1)) * b, 0)
		r = r + 1
	return product


def _meancent(myarray):
	means = scipy.mean(myarray, axis=0)  # Get the mean of each colm
	return scipy.subtract(myarray, means)


def _autoscale(a):
	mean_cols = scipy.resize(sum(a, 0) / a.shape[0], (a.shape))
	std_cols = scipy.resize(scipy.sqrt((sum((a - mean_cols) ** 2, 0)) / (a.shape[0] - 1)), (a.shape))
	return (a - mean_cols) / std_cols


def _mean(a, axis=0):
	"""Find the mean of 2D array along axis = 0 or 1
	default axis is 0
	"""
	return scipy.sum(a, axis) / a.shape[axis]


def _std(a):
	"""Find the standard deviation of 2D array
	along axis = 0
	"""
	m = _mean(a, 0)
	m = scipy.resize(m, (a.shape[0], a.shape[1]))
	return scipy.sqrt(scipy.sum((a - m) ** 2, 0) / (a.shape[0] - 1))


def _diag(a):
	"""Transform vector to diagonal matrix"""
	d = scipy.zeros((len(a), len(a)), "d")
	for i in range(len(a)):
		d[i, i] = a[i]
	return d


def _flip(a, axis=0):
	"""Reverse order of array elements along axis 0 or 1"""
	if axis == 0:
		axa, axb = 0, 1
	elif axis == 1:
		axa, axb = 1, 0

	ind = []
	for x in range(0, a.shape[axa], 1):
		if x == 0:
			ind.append(a.shape[axa] - 1)
		else:
			ind.append(a.shape[axa] - 1 - x)

	b = scipy.zeros((a.shape), "d")
	for x in range(a.shape[axa]):
		if axis == 0:
			b[x] = a[ind[x]]
		elif axis == 1:
			b[:, x] = a[:, ind[x]]
	return b


def _rms(pred, act):
	"""Calculate the root mean squared error of prediction"""
	return scipy.reshape(scipy.sqrt(scipy.sum((act - pred) ** 2) / act.shape[0]), ())


def _min(x, axis=0):
	"""find min of 2d array x along axis 0 or 1"""
	s = scipy.sort(x, axis)
	return scipy.reshape(s[0], ())


def _max(x, axis=0):
	"""find min of 2d array x along axis 0 or 1"""
	s = scipy.sort(x, axis)
	return scipy.reshape(s[x.shape[0] - 1], ())


def _slice(x, index, axis=0):
	"""for slicing arrays"""
	if axis == 0:
		slice = scipy.reshape(x[:, int(index[0])], (x.shape[0], 1))
		for n in range(1, len(index), 1):
			slice = scipy.concatenate((slice, scipy.reshape(x[:, int(index[n])], (x.shape[0], 1))), 1)
	elif axis == 1:
		slice = scipy.reshape(x[int(index[0]), :], (1, x.shape[1]))
		for n in range(1, len(index), 1):
			slice = scipy.concatenate((slice, scipy.reshape(x[int(index[n]), :], (1, x.shape[1]))), 0)
	return slice


def _split(xdata, ydata, mask, labels=None):
	"""Splits x and y inputs into training, cross validation (and
	independent test groups) for use with modelling algorithms.
	If max(mask)==2 return x1,x2,x3,y1,y2,y3,n1,n2,n3 else if max(mask)==1
	return x1,x2,y1,y2,n1,n2
	"""
	x1 = scipy.take(xdata, _index(mask, 0), 0)
	x2 = scipy.take(xdata, _index(mask, 1), 0)
	y1 = scipy.take(ydata, _index(mask, 0), 0)
	y2 = scipy.take(ydata, _index(mask, 1), 0)
	n1, n2 = [], []
	if labels is not None:
		for i in range(len(labels)):
			if mask[i] == 0:
				n1.append(labels[i])
			elif mask[i] == 1:
				n2.append(labels[i])

	if max(mask) == 1:
		return x1, x2, 0, y1, y2, 0, n1, n2, 0
	elif max(mask) == 2:
		x3 = scipy.take(xdata, _index(mask, 2), 0)
		y3 = scipy.take(ydata, _index(mask, 2), 0)
		n3 = []
		if labels is not None:
			for i in range(len(labels)):
				if mask[i] == 2:
					n3.append(labels[i])
		return x1, x2, x3, y1, y2, y3, n1, n2, n3


def _BW(X, group):
	"""Generate B and W matrices for CVA
	Ref. Krzanowski
	"""
	mx = scipy.mean(X, 0)[nA, :]
	tgrp = scipy.unique(group)
	for x in range(len(tgrp)):
		idx = _index(group, tgrp[x])
		L = len(idx)
		meani = scipy.mean(scipy.take(X, idx, 0), 0)
		meani = scipy.resize(meani, (len(idx), X.shape[1]))
		A = scipy.mean(scipy.take(X, idx, 0), 0) - mx
		C = scipy.take(X, idx, 0) - meani
		if x > 1:
			Bo = Bo + L * scipy.dot(scipy.transpose(A), A)
			Wo = Wo + scipy.dot(scipy.transpose(C), C)
		elif x == 1:
			Bo = L * scipy.dot(scipy.transpose(A), A)
			Wo = scipy.dot(scipy.transpose(C), C)

	B = (1.0 / (len(tgrp) - 1)) * Bo
	W = (1.0 / (X.shape[0] - len(tgrp))) * Wo

	return B, W


def _adj(a):
	"""Adjoint of a"""
	div, mod = divmod(a.shape[1], 2)
	adj = scipy.zeros((a.shape), "d")
	for p in range(0, a.shape[0], 1):
		for q in range(0, a.shape[1], 1):
			if mod == 0:
				if p < a.shape[1] / 2:
					if q < a.shape[1] / 2:
						adj[p, q] = (a[p + 1, q + 1] * a[p + 2, q + 2]) - (a[p + 1, q + 2] * a[p + 2, q + 1])
					if q >= a.shape[1] / 2:
						adj[p, q] = (a[p + 1, q - 2] * a[p + 2, q - 1]) - (a[p + 1, q - 1] * a[p + 2, q - 2])
				if p >= a.shape[1] / 2:
					if q < a.shape[1] / 2:
						adj[p, q] = (a[p - 2, q + 1] * a[p - 1, q + 2]) - (a[p - 2, q + 2] * a[p - 1, q + 1])
					if q >= a.shape[1] / 2:
						adj[p, q] = (a[p - 2, q - 2] * a[p - 1, q - 1]) - (a[p - 2, q - 1] * a[p - 1, q - 2])
			if mod != 0:
				if p < a.shape[1] / 2:
					if q < a.shape[1] / 2:
						adj[p, q] = (a[p + 1, q + 1] * a[p + 2, q + 2]) - (a[p + 1, q + 2] * a[p + 2, q + 1])
					if q > a.shape[1] / 2:
						adj[p, q] = (a[p + 1, q - 2] * a[p + 2, q - 1]) - (a[p + 1, q - 1] * a[p + 2, q - 2])
					if q == a.shape[1] / 2:
						adj[p, q] = (a[p + 1, q - 1] * a[p + 2, q + 1]) - (a[p + 1, q + 1] * a[p + 2, q - 1])
				if p > a.shape[1] / 2:
					if q < a.shape[1] / 2:
						adj[p, q] = (a[p - 2, q + 1] * a[p - 1, q + 2]) - (a[p - 2, q + 2] * a[p - 1, q + 1])
					if q > a.shape[1] / 2:
						adj[p, q] = (a[p - 2, q - 2] * a[p - 1, q - 1]) - (a[p - 2, q - 1] * a[p - 1, q - 2])
					if q == a.shape[1] / 2:
						adj[p, q] = (a[p - 2, q - 1] * a[p - 1, q + 1]) - (a[p - 2, q + 1] * a[p - 1, q - 1])
				if p == a.shape[1] / 2:
					if q < a.shape[1] / 2:
						adj[p, q] = (a[p - 1, q + 1] * a[p + 1, q + 2]) - (a[p - 1, q + 2] * a[p + 1, q + 1])
					if q > a.shape[1] / 2:
						adj[p, q] = (a[p - 1, q - 2] * a[p + 1, q - 1]) - (a[p - 1, q - 1] * a[p + 1, q - 2])
					if q == a.shape[1] / 2:
						adj[p, q] = (a[p - 1, q - 1] * a[p + 1, q + 1]) - (a[p - 1, q + 1] * a[p + 1, q - 1])

	for m in range(1, adj.shape[0] + 1, 1):
		for n in range(1, adj.shape[1] + 1, 1):
			if divmod(m, 2)[1] != 0:
				if divmod(n, 2)[1] == 0:
					adj[m - 1, n - 1] = adj[m - 1, n - 1] * -1
			elif divmod(m, 2)[1] == 0:
				if divmod(n, 2)[1] != 0:
					adj[m - 1, n - 1] = adj[m - 1, n - 1] * -1

	return scipy.transpose(adj)


def _inverse(a):
	"""Inverse of a"""
	d = scipy.linalg.det(a)
	if d == 0:
		d = 0.001
	return _adj(a) / d


def _index(y, num):
	"""use this to get tuple index for take"""
	idx = []
	for i in range(len(y)):
		if y[i] == num:
			idx.append(int(i))
	return tuple(idx)


def _put(a, ind, v):
	"""a pvt put function"""
	c = 0
	for each in ind:
		a[each, :] = v[c, :]
		c += 1
	return a


def _sample(x, N):
	"""randomly select N samples from x"""
	select = []
	while len(select) < N:
		a = int(scipy.rand(1) * float(x))
		if a not in select:
			select.append(a)
	return select


def pca_svd(myarray, type="covar"):
	"""Run principal components analysis (PCA) by singular
	value decomposition (SVD)

	>>> import scipy
	>>> a = np.array([[1,2,3],[0,1,1.5],[-1,-6,34],[8,15,2]])
	>>> a
	array([[  1. ,	 2. ,	3. ],
		   [  0. ,	 1. ,	1.5],
		   [ -1. ,	-6. ,  34. ],
		   [  8. ,	15. ,	2. ]])
	>>> # There are four samples, with three variables each
	>>> tt,pp,pr,eigs = PCA_SVD(a)
	>>> tt
	array([[  5.86463567e+00,  -4.28370443e+00,	  1.46798845e-01],
		   [  6.65979784e+00,  -6.16620433e+00,	 -1.25067331e-01],
		   [ -2.56257861e+01,	1.82610701e+00,	 -6.62877855e-03],
		   [  1.31013526e+01,	8.62380175e+00,	 -1.51027354e-02]])
	>>> pp
	array([[ 0.15026487,  0.40643255, -0.90123973],
		   [ 0.46898935,  0.77318935,  0.4268808 ],
		   [ 0.87032721, -0.48681703, -0.07442934]])
	>>> # This is the 'rotation matrix' - you can imagine colm labels
	>>> # of PC1, PC2, PC3 and row labels of variable1, variable2, variable3.
	>>> pr
	array([[  0.		],
		   [ 97.1073744 ],
		   [ 98.88788958],
		   [ 99.98141011]])
	>>> eigs
	array([[ 30.11765617],
		   [ 11.57915467],
		   [  0.1935556 ]])
	>>> a
	array([[  1. ,	 2. ,	3. ],
		   [  0. ,	 1. ,	1.5],
		   [ -1. ,	-6. ,  34. ],
		   [  8. ,	15. ,	2. ]])
	"""
	if type == "covar":
		myarray = _meancent(myarray)
	elif type == "corr":
		myarray = _autoscale(myarray)
	else:
		raise KeyError("'type' must be one of 'covar or 'corr'")

	# I think this may run faster if myarray is converted to a matrix first.
	# (This should be tested - anyone got a large dataset?)
	# mymat = scipy.mat(myarray)
	u, s, v = scipy.linalg.svd(myarray)
	tt = scipy.dot(myarray, scipy.transpose(v))
	pp = v
	pr = (1 - (s / scipy.sum(scipy.sum(myarray**2)))) * 100
	pr = scipy.reshape(pr, (1, len(pr)))
	pr = scipy.concatenate((np.array([[0.0]]), pr), 1)
	pr = scipy.reshape(pr, (pr.shape[1],))
	eigs = s

	return tt, pp, pr[:, nA], eigs[:, nA]


def pca_nipals(myarray, comps, type="covar", stb=None):
	"""Run principal components analysis (PCA) using NIPALS

	Martens,H; Naes,T: Multivariate Calibration, Wiley: New York, 1989

	>>> import scipy
	>>> a = np.array([[1,2,3],[0,1,1.5],[-1,-6,34],[8,15,2]])
	>>> tt,pp,pr,eigs=PCA_NIPALS(a,2)
	>>> tt
	array([[ -5.86560409,  -4.2823783 ],
		   [ -6.66119189,  -6.16469835],
		   [ 25.62619836,	1.82031282],
		   [-13.09940238,	8.62676382]])

	"""

	if type == "covar":
		newarray = _meancent(myarray)
	elif type == "corr":
		newarray = _autoscale(myarray)

	arr_size = newarray.shape
	tt, pp, i = scipy.zeros((arr_size[0], comps), "d"), scipy.zeros((comps, arr_size[1]), "d"), 0

	while i < comps:
		std = scipy.std(newarray, axis=0)
		st2 = scipy.argsort(std)
		ind = st2[
			arr_size[1] - 1,
		]
		t0 = newarray[:, ind]
		c = 0
		while c == 0:  # NIPALS
			p0 = scipy.dot(scipy.transpose(t0), newarray)
			p1 = p0 / scipy.sqrt(scipy.sum(p0**2))
			t1 = scipy.dot(newarray, scipy.transpose(p1))
			if scipy.sqrt(scipy.sum(t1**2)) - scipy.sqrt(scipy.sum(t0**2)) < 5 * 10**-5:
				tt[:, i] = t1
				pp[i, :] = p1
				c = 1
			t0 = t1

		newarray = newarray - scipy.dot(scipy.resize(t1, (arr_size[0], 1)), scipy.resize(p1, (1, arr_size[1])))

		i += 1
		# report progress to status bar
		if stb is not None:
			stb.SetStatusText(" ".join(("Principal component", str(i))), 0)

	# work out percentage explained variance
	if type == "covar":
		newarray = _meancent(myarray)
	elif type == "corr":
		newarray = _autoscale(myarray)

	s0, s = scipy.sum(scipy.sum(newarray**2)), []
	for n in scipy.arange(1, comps + 1, 1):
		E = newarray - scipy.dot(tt[:, 0:n], pp[0:n, :])
		s.append(scipy.sum(scipy.sum(E**2)))

	pr = (1 - ((scipy.asarray(s) / s0))) * 100
	pr = scipy.reshape(pr, (1, len(pr)))
	pr = scipy.concatenate((np.array([[0.0]]), pr), 1)
	pr = scipy.reshape(pr, (pr.shape[1],))
	eigs = np.array(s)

	if stb is not None:
		stb.SetStatusText("Status", 0)

	return tt, pp, pr[:, nA], eigs[:, nA]


def cva(X, group, nodfs, pcloads=None):
	"""Canonical variates analysis

	Ref. Krzanowski

	Manly, B.F.J. Multivariate Statistical Methods: A Primer,
	2nd Ed, Chapman & Hall: New York, 1986

	>>> import scipy
	>>> X = np.array([[ 0.19343116,	0.49655245,	 0.72711322,  0.79482108,  0.13651874],[ 0.68222322,  0.89976918,  0.30929016,	0.95684345,	 0.01175669],[ 0.3027644 ,	0.82162916,	 0.83849604,  0.52259035,  0.89389797],[ 0.54167385,  0.64491038,  0.56807246,	0.88014221,	 0.19913807],[ 0.15087298,	0.81797434,	 0.37041356,  0.17295614,  0.29872301],[ 0.69789848,  0.66022756,  0.70273991,	0.9797469 ,	 0.66144258],[ 0.378373	 ,	0.34197062,	 0.54657115,  0.27144726,  0.28440859],[ 0.8600116 ,  0.2897259 ,  0.4448802 ,	0.25232935,	 0.46922429],[ 0.85365513,	0.34119357,	 0.69456724,  0.8757419 ,  0.06478112],[ 0.59356291,  0.53407902,  0.62131013,	0.73730599,	 0.98833494]])
	>>> group = np.array([[1],[1],[1],[1],[2],[2],[2],[3],[3],[3]])
	>>> B,W = _BW(X,group)
	>>> B
	array([[ 0.12756749, -0.10061061,  0.00366132, -0.00615551,	 0.05378535],
		   [-0.10061061,  0.09289765,  0.00469185,	0.03883801, -0.05465494],
		   [ 0.00366132,  0.00469185,  0.0043456 ,	0.01883603, -0.00530158],
		   [-0.00615551,  0.03883801,  0.01883603,	0.08554211, -0.0332867 ],
		   [ 0.05378535, -0.05465494, -0.00530158, -0.0332867 ,	 0.03372716]])
	>>> W
	array([[ 0.049357  ,  0.00105553, -0.00808075,	0.04037998, -0.02013773],
		   [ 0.00105553,  0.03555862, -0.00982256,	0.00761902,	 0.02439148],
		   [-0.00808075, -0.00982256,  0.03519157,	0.01447587,	 0.03438791],
		   [ 0.04037998,  0.00761902,  0.01447587,	0.10132225, -0.01048251],
		   [-0.02013773,  0.02439148,  0.03438791, -0.01048251,	 0.1417496 ]])
	>>>
	>>> U,As_out,Ls_out,dummy = DFA(X,group,5)
	>>>
	>>> U
	array([[-4.17688874, -4.00309392, -3.30364313, -4.17357019,	 0.09912727],
		   [-3.84164699, -4.48421541, -2.42156782, -4.9040549 ,	 3.20454647],
		   [-3.81085207, -3.81397856, -3.57914463, -7.41611306,	 0.9193002 ],
		   [-3.24935377, -4.45386899, -2.95147097, -4.88934464,	 1.59185795],
		   [-4.13154582, -2.09087065, -3.10069062, -5.44262709,	 2.11303517],
		   [-2.16978732, -4.9634328 , -2.48987133, -5.94427649,	 1.31295895],
		   [-1.5773928 , -2.78409584, -3.60130796, -4.65040852,	 0.93512979],
		   [ 0.99791536, -3.22594943, -3.54773184, -5.49732342,	 2.13121685],
		   [-1.37244426, -5.24757135, -4.44704409, -5.11090375,	 1.55257506],
		   [-0.69651359, -3.79497195, -1.19709398, -5.42908493,	 0.677332  ]])
	>>>
	"""

	# Get B,W
	B, W = _BW(X, group)

	# produce a diagonal matrix L of generalized
	# eigenvalues and a full matrix A whose columns are the
	# corresponding eigenvectors so that B*A = W*A*L.
	L, A = scipy.linalg.eig(B, W)

	# need to normalize A such that Aout'*W*Aout = I
	# introducing Cholesky decomposition K = T'T
	# (see Seber 1984 "Multivariate Observations" pp 270)
	# At the moment
	# A'*W*A = K so substituting Cholesky decomposition
	# A'*W*A = T'*T ; so, inv(T')*A'*W*A*inv(T) = I
	# & [inv(T)]'*A'*W*A*inv(T) = I thus, [A*inv(T)]'*W*[A*inv(T)] = I
	# thus Aout = A*inv(T)
	K = scipy.dot(scipy.transpose(A), scipy.dot(W, A))
	T = scipy.linalg.cholesky(K)
	Aout = scipy.dot(A, scipy.linalg.inv(T))

	# Sort eigenvectors w.r.t eigenvalues
	order = _flip(scipy.argsort(scipy.reshape(L.real, (len(L),))))
	Ls = _flip(scipy.sort(L.real))

	# extract & reduce to required size
	As_out = scipy.take(Aout, order[0:nodfs].tolist(), 1)
	Ls_out = Ls[0:nodfs][nA, :]

	# Create Scores (canonical variates) is the matrix of scores ###
	U = scipy.dot(X, As_out)

	# convert pc-dfa loadings back to original variables if necessary
	if pcloads is not None:
		pcloads = scipy.dot(scipy.transpose(pcloads), As_out)

	return U, As_out, Ls_out, pcloads


def mlr(x, y, order):
	"""Multiple linear regression fit of the columns of matrix x
	(dependent variables) to constituent vector y (independent variables)

	order -		order of a smoothing polynomial, which can be included
				in the set of independent variables. If order is
				not specified, no background will be included.
	b -			fit coeffs
	f -			fit result (m x 1 column vector)
	r -			residual   (m x 1 column vector)
	"""

	if order > 0:
		s = scipy.ones((len(y), 1))
		for j in range(order):
			s = scipy.concatenate((s, (scipy.arange(0, 1 + (1.0 / (len(y) - 1)), 1.0 / (len(y) - 1)) ** j)[:, nA]), 1)
		X = scipy.concatenate((x, s), 1)
	else:
		X = x

	# calc fit b=fit coefficients
	b = scipy.dot(scipy.dot(scipy.linalg.pinv(scipy.dot(scipy.transpose(X), X)), scipy.transpose(X)), y)
	f = scipy.dot(X, b)
	r = y - f

	return b, f, r


def pls(xdata, ydata, mask, factors, stb=None, type=0):
	"""PLS1 for modelling a single Y-variable and
	PLS2 for several Y-variables

	Martens,H; Naes,T: Multivariate Calibration, Wiley: New York, 1989

	The test data defined here were generated at random and do not
	represent accurate calibration data.  The test is for PLS1 only.

	>>> import scipy
	>>> xdata=np.array([[ 0.6 ,	0.57,  0.59,  0.81,	 0.45],[ 0.96,	0.76,  0.99,  0.08,	 0.17],[ 0.99,	0.06,  0.99,  0.28,	 0.98],[ 0.2 ,	0.02,  0.35,  0.12,	 0.34],[ 0.36,	0.02,  0.02,  0.48,	 0.07],[ 0.5 ,	0.5 ,  0.59,  0.26,	 0.81],[ 0.71,	0.07,  0.37,  0.09,	 0.53],[ 0.2 ,	0.88,  0.48,  0.53,	 0.93],[ 0.63,	0.44,  0.47,  0.33,	 0.02],[ 0.63,	0.45,  0.23,  0.5 ,	 0.59]])
	>>> ydata=np.array([[ 0.48],[ 0.55],[ 0.74],[ 0.43],[ 0.52],[ 0.95],[ 0.7 ],[ 0.23],[ 0.08],[ 0.42]])
	>>> mask=np.array([[0],[2],[0],[1],[0],[1],[1],[0],[2],[0]])
	>>> W,T,P,Q,facs,predy,predyv,predyt,RMSEC,RMSEPC,rmsec,rmsepc,RMSEPT,b=PLS(xdata,ydata,mask,3)
	>>> W
	array([[ 0.56264693, -0.06977376,  0.14315076],
		   [-0.66930157, -0.33463909,  0.1648742 ],
		   [ 0.39741966, -0.31939576,  0.60501983],
		   [-0.27048316,  0.40535938,  0.76294239],
		   [-0.06603263, -0.78537788,  0.06476318]])
	>>>

	"""

	output = {}
	x1, x2, x3, y1, y2, y3, dummy1, dummy2, dummy3 = _split(xdata, ydata, mask)  # raw data
	Xm, Xmv = scipy.mean(x1, axis=0), scipy.mean(x2, axis=0)  # get column means
	ym, ymv = scipy.mean(y1, axis=0), scipy.mean(y2, axis=0)

	if max(mask) > 1:
		Xmt, ymt = scipy.mean(x3, axis=0), scipy.mean(y3, axis=0)

	if type == 0:  # use matrix of covariances
		x, y = _meancent(xdata), _meancent(ydata)
	elif type == 1:  # use matrix of correlations
		x, y = _autoscale(xdata), _autoscale(ydata)

	# split into training, cross-validation & test
	train_x, cval_x, test_x, train_y, cval_y, test_y, dummy1, dummy2, dummy3 = _split(x, y, mask)
	X, Xv, Xt = train_x, cval_x, test_x
	y, yv, yt = train_y, cval_y, test_y

	output["rmsec"], output["rmsepc"], output["rmsept"] = [], [], []
	NoY = ydata.shape[1]
	u = y
	for xi in range(factors):
		t0, opt = 0, 0

		if NoY > 1:  # PLS2
			u = u[:, scipy.argsort(scipy.sum(y1**2, axis=0))[0]][:, scipy.newaxis]

		while opt == 0:
			# for training
			c = scipy.dot(scipy.dot(scipy.dot(scipy.transpose(u), X), scipy.transpose(X)), u) ** -0.5  # scaling factor
			w = scipy.transpose(c * scipy.dot(scipy.transpose(u), X))  # vector of loading weights, w'w = 1
			t = scipy.dot(X, w)  # spectral scores
			p = scipy.transpose(scipy.dot(scipy.transpose(X), t) * scipy.linalg.inv(scipy.dot(scipy.transpose(t), t)))  # spectral loadings
			q = scipy.dot(scipy.transpose(t), y) * scipy.linalg.inv(scipy.dot(scipy.transpose(t), t))  # chemical loading

			if NoY == 1:  # PLS1
				opt = 1
			elif float(scipy.reshape(scipy.sum(abs(t - t0)), ())) > 5 * 10**-5:  # PLS2 - check for convergence
				u = scipy.dot(scipy.dot(y, scipy.transpose(q)), scipy.linalg.inv(scipy.dot(q, scipy.transpose(q))))
				t0 = t
			else:
				opt = 1

		X = X - scipy.dot(t, p)  # compute residuals of X which are also X for next iteration
		u = y - scipy.dot(t, q)  # compute residuals of y which are also y for next iteration

		if xi == 0:
			output["W"], output["T"], output["P"], output["Q"] = w, t, p, q
		else:
			output["W"] = scipy.concatenate((output["W"], w), 1)
			output["T"] = scipy.concatenate((output["T"], t), 1)
			output["P"] = scipy.concatenate((output["P"], p), 0)
			output["Q"] = scipy.concatenate((output["Q"], q), 0)

		b = scipy.dot(scipy.transpose(output["Q"]), scipy.transpose(scipy.dot(output["W"], scipy.linalg.inv(scipy.dot(output["P"], output["W"])))))

		output["spec"] = b

		# rms for training data - rmsec
		b0 = ym - scipy.dot(Xm[scipy.newaxis, :], scipy.transpose(b))
		predy = b0 + scipy.dot(x1, scipy.transpose(b))
		output["rmsec"].append(float(_rms(predy, y1)))

		# cross validation prediction
		b1 = ymv - scipy.dot(Xmv[scipy.newaxis, :], scipy.transpose(b))
		predyv = b1 + scipy.dot(x2, scipy.transpose(b))
		output["rmsepc"].append(float(_rms(predyv, y2)))

		# independent test predictions
		if max(mask) > 1:
			b2 = ymt - scipy.dot(Xmt[scipy.newaxis, :], scipy.transpose(b))
			predyt = b2 + scipy.dot(x3, scipy.transpose(b))
			output["rmsept"].append(float(_rms(predyt, y3)))

		# report progress to status bar
		if stb is not None:
			stb.SetStatusText(" ".join(("Extracting factor...", str(xi + 1))), 0)

	# work out number of factors to use by finding the min of
	# the rmsep cross validation - exception for use in GA
	output["facs"] = ind = scipy.argsort(output["rmsepc"])[0]

	# return final rms values
	output["RMSEC"], output["RMSEPC"] = output["rmsec"][ind], output["rmsepc"][ind]

	# claculate partial prediction based on optimal no. of factors
	output["b"] = scipy.dot(scipy.transpose(output["Q"][0 : ind + 1, :]), scipy.transpose(scipy.dot(output["W"][:, 0 : ind + 1], scipy.linalg.inv(scipy.dot(output["P"][0 : ind + 1, :], output["W"][:, 0 : ind + 1])))))

	# predictions based on optimal no. of factors
	# training predictions
	b0 = ym - scipy.dot(Xm[scipy.newaxis, :], scipy.transpose(output["b"]))
	predy = b0 + scipy.dot(x1, scipy.transpose(output["b"]))
	output["RMSEC"] = float(_rms(predy, y1))

	# cross validation prediction
	b1 = ymv - scipy.dot(Xmv[scipy.newaxis, :], scipy.transpose(output["b"]))
	predyv = b1 + scipy.dot(x2, scipy.transpose(output["b"]))
	output["RMSEPC"] = float(_rms(predyv, y2))

	# independent test predictions
	if max(mask) > 1:
		b2 = ymt - scipy.dot(Xmt[scipy.newaxis, :], scipy.transpose(output["b"]))
		predyt = b2 + scipy.dot(x3, scipy.transpose(output["b"]))
		output["RMSEPT"] = float(_rms(predyt, y3))
	else:
		predyt, output["RMSEPT"] = 0.0, 0.0

	if stb is not None:
		stb.SetStatusText("Status", 0)

	# pull pls predictions back toegther
	output["predictions"] = scipy.zeros(ydata.shape)
	output["predictions"] = _put(output["predictions"], _index(mask, 0), predy[:, scipy.newaxis])
	output["predictions"] = _put(output["predictions"], _index(mask, 1), predyv[:, scipy.newaxis])
	if max(mask) > 1:
		output["predictions"] = _put(output["predictions"], _index(mask, 2), predyt[:, scipy.newaxis])

	# recalculate spectral scores for all samples
	output["plsscores"] = scipy.dot(x, output["W"][:, 0 : ind + 1])

	return output


def dfa_xval_raw(X, group, mask, nodfs):
	"""Perform DFA with full cross validation

	>>> import scipy
	>>> X = np.array([[ 0.19343116,	0.49655245,	 0.72711322,  0.79482108,  0.13651874],[ 0.68222322,  0.89976918,  0.30929016,	0.95684345,	 0.01175669],[ 0.3027644 ,	0.82162916,	 0.83849604,  0.52259035,  0.89389797],[ 0.54167385,  0.64491038,  0.56807246,	0.88014221,	 0.19913807],[ 0.15087298,	0.81797434,	 0.37041356,  0.17295614,  0.29872301],[ 0.69789848,  0.66022756,  0.70273991,	0.9797469 ,	 0.66144258],[ 0.378373	 ,	0.34197062,	 0.54657115,  0.27144726,  0.28440859],[ 0.8600116 ,  0.2897259 ,  0.4448802 ,	0.25232935,	 0.46922429],[ 0.85365513,	0.34119357,	 0.69456724,  0.8757419 ,  0.06478112],[ 0.59356291,  0.53407902,  0.62131013,	0.73730599,	 0.98833494]])
	>>> group = np.array([[1],[1],[1],[1],[2],[2],[2],[3],[3],[3]])
	>>> mask = np.array([[0],[1],[0],[0],[0],[0],[1],[0],[0],[1]])
	>>> scores,loads,eigs = DFA_XVALRAW(X,group,mask,2)
	"""

	x1, x2, x3, y1, y2, y3, dummy1, dummy2, dummy3 = _split(X, np.array(group, "i"), mask)

	# get indices
	idxn = scipy.arange(X.shape[0])[:, nA]
	tr_idx = scipy.take(idxn, _index(mask, 0), 0)
	cv_idx = scipy.take(idxn, _index(mask, 1), 0)

	# train
	trscores, loads, eigs, loads2 = DFA(x1, y1, nodfs)

	# cross validation
	cvscores = scipy.dot(x2, loads)

	# independent test
	if max(mask) > 1:
		ts_idx = scipy.take(idxn, _index(mask, 2), 0)
		tstscores = scipy.dot(x3, loads)

		scores = scipy.zeros((X.shape[0], nodfs), "d")

		tr_idx = scipy.reshape(tr_idx, (len(tr_idx),)).tolist()
		cv_idx = scipy.reshape(cv_idx, (len(cv_idx),)).tolist()
		ts_idx = scipy.reshape(ts_idx, (len(ts_idx),)).tolist()
		_put(scores, tr_idx, trscores)
		_put(scores, cv_idx, cvscores)
		_put(scores, ts_idx, tstscores)

	else:
		scores = scipy.concatenate((trscores, cvscores), 0)
		tr_idx = scipy.reshape(tr_idx, (len(tr_idx),)).tolist()
		cv_idx = scipy.reshape(cv_idx, (len(cv_idx),)).tolist()
		_put(scores, tr_idx, trscores)
		_put(scores, cv_idx, cvscores)

	return scores, loads, eigs


def dfa_xval_pca(X, pca, nopcs, group, mask, nodfs, ptype="covar"):
	"""Perform PC-DFA with full cross validation

	>>> import scipy
	>>> X = np.array([[ 0.19343116,	0.49655245,	 0.72711322,  0.79482108,  0.13651874],[ 0.68222322,  0.89976918,  0.30929016,	0.95684345,	 0.01175669],[ 0.3027644 ,	0.82162916,	 0.83849604,  0.52259035,  0.89389797],[ 0.54167385,  0.64491038,  0.56807246,	0.88014221,	 0.19913807],[ 0.15087298,	0.81797434,	 0.37041356,  0.17295614,  0.29872301],[ 0.69789848,  0.66022756,  0.70273991,	0.9797469 ,	 0.66144258],[ 0.378373	 ,	0.34197062,	 0.54657115,  0.27144726,  0.28440859],[ 0.8600116 ,  0.2897259 ,  0.4448802 ,	0.25232935,	 0.46922429],[ 0.85365513,	0.34119357,	 0.69456724,  0.8757419 ,  0.06478112],[ 0.59356291,  0.53407902,  0.62131013,	0.73730599,	 0.98833494]])
	>>> group = np.array([[1],[1],[1],[1],[2],[2],[2],[3],[3],[3]])
	>>> mask = np.array([[0],[1],[0],[0],[0],[0],[1],[0],[0],[1]])
	>>> scores,loads,eigs = DFA_XVAL(X,'NIPALS',3,group,mask,2,'covar')

	"""
	rx1, rx2, rx3, ry1, ry2, ry3, dummy1, dummy2, dummy3 = _split(X, np.array(group, "i")[:, nA], mask[:, nA])

	if pca == "SVD":
		pcscores, pp, pr, pceigs = PCA_SVD(rx1, type=ptype)
	elif pca == "NIPALS":
		pcscores, pp, pr, pceigs = PCA_NIPALS(rx1, nopcs, type=ptype)

	# get indices
	idxn = scipy.arange(X.shape[0])[:, nA]
	tr_idx = scipy.take(idxn, _index(mask, 0), 0)
	cv_idx = scipy.take(idxn, _index(mask, 1), 0)

	# train
	trscores, loads, eigs, dummy = DFA(pcscores[:, 0:nopcs], ry1, nodfs)

	# cross validation
	# Get projected pc scores
	if ptype in ["covar"]:
		rx2 = rx2 - scipy.resize(scipy.mean(rx2, 0), (len(rx2), rx1.shape[1]))
	else:
		rx2 = (rx2 - scipy.resize(scipy.mean(rx2, 0), (len(rx2), rx1.shape[1]))) / scipy.resize(scipy.std(rx2, 0), (len(rx2), rx1.shape[1]))

	pcscores = scipy.dot(rx2, scipy.transpose(pp))

	cvscores = scipy.dot(pcscores[:, 0:nopcs], loads)

	# independent test
	if max(mask) > 1:
		ts_idx = scipy.take(idxn, _index(mask, 2), 0)
		if ptype in ["covar"]:
			rx3 = rx3 - scipy.resize(scipy.mean(rx3, 0), (len(rx3), rx1.shape[1]))
		else:
			rx3 = (rx3 - scipy.resize(scipy.mean(rx3, 0), (len(rx3), rx1.shape[1]))) / scipy.resize(scipy.std(rx3, 0), (len(rx3), rx1.shape[1]))
		pcscores = scipy.dot(rx3, scipy.transpose(pp))
		tstscores = scipy.dot(pcscores[:, 0:nopcs], loads)

		scores = scipy.zeros((X.shape[0], nodfs), "d")

		tr_idx = scipy.reshape(tr_idx, (len(tr_idx),)).tolist()
		cv_idx = scipy.reshape(cv_idx, (len(cv_idx),)).tolist()
		ts_idx = scipy.reshape(ts_idx, (len(ts_idx),)).tolist()
		_put(scores, tr_idx, trscores)
		_put(scores, cv_idx, cvscores)
		_put(scores, ts_idx, tstscores)
	else:
		scores = scipy.concatenate((trscores, cvscores), 0)
		tr_idx = scipy.reshape(tr_idx, (len(tr_idx),)).tolist()
		cv_idx = scipy.reshape(cv_idx, (len(cv_idx),)).tolist()
		_put(scores, tr_idx, trscores)
		_put(scores, cv_idx, cvscores)

	# get loadings for original variables
	loads = scipy.dot(scipy.transpose(pp[0:nopcs, :]), loads)

	return scores, loads, eigs


def DFA_XVAL_PLS(plsscores, plsloads, nolvs, group, mask, nodfs):
	"""Perform PLS-DFA with full cross validation"""
	rx1, rx2, rx3, ry1, ry2, ry3, dummy1, dummy2, dummy3 = _split(plsscores, np.array(group, "i")[:, nA], mask[:, nA])

	# get indices
	idxn = scipy.arange(plsscores.shape[0])[:, nA]
	tr_idx = scipy.take(idxn, _index(mask, 0), 0)
	cv_idx = scipy.take(idxn, _index(mask, 1), 0)

	# train
	cvas, loads, eigs, dummy = DFA(rx1[:, 0:nolvs], ry1, nodfs)

	# cross validation
	cvav = scipy.dot(rx2[:, 0:nolvs], loads)

	# independent test
	if max(mask) > 1:
		cvat = scipy.dot(rx3[:, 0:nolvs], loads)

		scores = scipy.zeros((plsscores.shape[0], nodfs), "d")

		tr_idx = scipy.reshape(tr_idx, (len(tr_idx),)).tolist()
		cv_idx = scipy.reshape(cv_idx, (len(cv_idx),)).tolist()
		ts_idx = scipy.take(idxn, _index(mask, 2), 0)
		ts_idx = scipy.reshape(ts_idx, (len(ts_idx),)).tolist()
		_put(scores, tr_idx, cvas)
		_put(scores, cv_idx, cvav)
		_put(scores, ts_idx, cvat)

	else:
		scores = scipy.concatenate((cvas, cvav), 0)

		tr_idx = scipy.reshape(tr_idx, (len(tr_idx),)).tolist()
		cv_idx = scipy.reshape(cv_idx, (len(cv_idx),)).tolist()
		_put(scores, tr_idx, cvas)
		_put(scores, cv_idx, cvav)

	# get loadings for original variables
	loads = scipy.dot(plsloads[:, 0:nolvs], loads)

	return scores, loads, eigs


def ols(act, pred):
	"""Ordinary least squares regression"""
	act = scipy.reshape(act, (len(act), 1))
	gradient = scipy.sum((act - _mean(act)) * (pred - _mean(pred))) / (sum((act - _mean(act)) ** 2))
	yintercept = _mean(act) - (gradient * _mean(act))
	mserr = pred - _mean(pred)

	rmserr = _rms(act, pred)
	gerr = scipy.sqrt(rmserr**2 / scipy.sum((act - _mean(act)) ** 2))
	ierr = scipy.sqrt((rmserr**2) * ((1 / len(act)) + ((_mean(act) ** 2) / scipy.sum((act - _mean(act)) ** 2))))

	return gradient, yintercept, mserr, rmserr, gerr, ierr


if __name__ == "__main__":
	import doctest

	from . import chemometrics

	doctest.testmod(chemometrics, verbose=True)
