# -----------------------------------------------------------------------------
# Name:		   fitfun.py
# Purpose:
#
# Author:	   Roger Jarvis
#
# Created:	   2006/06/20
# RCS-ID:	   $Id$
# Copyright:   (c) 2006
# Licence:	   GNU General Public License
# Description: Fitness functions for use in genetic algorithm optimisation
# -----------------------------------------------------------------------------

import copy
import string

import scipy
from expSetup import valSplit
from scipy import newaxis as nA

from .chemometrics import *
from .chemometrics import __BW__, __diag__, __flip__, __slice__, __split__, _index, _put
from .genetic import _remdup
from .process import *


def __group__(x, mrep):
	grp = []
	for n in range(1, x.shape[0] / mrep + 1, 1):
		for cnt in range(0, mrep, 1):
			grp.append(n)
	return scipy.reshape(scipy.asarray(grp, "i"), (len(grp), 1))


def call_dfa(chrom, xdata, DFs, folds, data, grid, pc):
	"""Runs DFA on subset of variables from "xdata" as
	defined by "chrom" and returns a vector of fitness
	scores to be fed back into the GA
	"""
	Y = []
	for x in range(len(chrom)):
		if _remdup(chrom[x]) == 0:
			# extract vars from xdata
			slice = meancent(__slice__(xdata, chrom[x]))
			collate = 0
			for nF in range(folds):
				# split in to training and test
				if nF == 0:
					tr_slice, cv_slice, ts_slice, tr_grp, cv_grp, ts_grp, tr_nm, cv_nm, ts_nm = __split__(slice, data["class"], data["validation"], data["label"])
				else:
					fMask = valSplit(grid, data, pc)
					tr_slice, cv_slice, ts_slice, tr_grp, cv_grp, ts_grp, tr_nm, cv_nm, ts_nm = __split__(slice, data["class"], fMask, data["label"])
				try:
					u, v, eigs, dummy = DFA(tr_slice, tr_grp, DFs)
					projU = scipy.dot(cv_slice, v)
					u = scipy.concatenate((u, projU), 0)
					group2 = scipy.concatenate((tr_grp, cv_grp), 0)

					B, W = __BW__(u, group2)
					L, A = scipy.linalg.eig(B, W)
					order = __flip__(scipy.argsort(scipy.reshape(L.real, (len(L),))))
					Ls = __flip__(scipy.sort(L.real))
					eigval = Ls[0:DFs]

					collate += 1 / sum(eigval)
				except:
					continue

			if collate != 0:
				Y.append(collate / float(folds))
			else:
				Y.append(10**5)
		else:
			Y.append(10.0**5 / float(folds))

	return np.array(Y)[:, nA]


def rerun_dfa(chrom, xdata, mask, groups, names, DFs):
	"""Run DFA in min app"""
	# extract vars from xdata
	slice = meancent(__slice__(xdata, chrom))

	# split in to training and test
	tr_slice, cv_slice, ts_slice, tr_grp, cv_grp, ts_grp, tr_nm, cv_nm, ts_nm = __split__(slice, groups, mask, names)

	# get indexes
	idx = scipy.arange(xdata.shape[0])[:, nA]
	tr_idx = scipy.take(idx, _index(mask, 0), 0)
	cv_idx = scipy.take(idx, _index(mask, 1), 0)
	ts_idx = scipy.take(idx, _index(mask, 2), 0)

	# model DFA on training samples
	u, v, eigs, dummy = DFA(tr_slice, tr_grp, DFs)

	# project xval and test samples
	projUcv = scipy.dot(cv_slice, v)
	projUt = scipy.dot(ts_slice, v)

	uout = scipy.zeros((xdata.shape[0], DFs), "d")
	_put(uout, scipy.reshape(tr_idx, (len(tr_idx),)).tolist(), u)
	_put(uout, scipy.reshape(cv_idx, (len(cv_idx),)).tolist(), projUcv)
	_put(uout, scipy.reshape(ts_idx, (len(ts_idx),)).tolist(), projUt)

	return uout, v, eigs


def call_pls(chrom, xdata, factors, data, folds, grid, pc):
	"""Runs pls on a subset of X-variables"""
	scores = []

	for i in range(chrom.shape[0]):
		if _remdup(chrom[i]) == 0:
			# extract vars from xdata
			slice = scipy.take(xdata, chrom[i, :].tolist(), 1)
			collate = 0
			for nF in range(folds):
				# split in to training and test
				if nF == 0:
					mask = data["validation"]
				else:
					mask = valSplit(grid, data, pc)

				W, T, P, Q, facs, predy, predyv, predyt, RMSEC, RMSEPC, rmsec, rmsepc, RMSEPT, b = PLS(slice, np.array(data["class"], "f")[:, nA], mask, factors)

				if min(rmsec) <= min(rmsepc):
					collate += RMSEPC
				else:
					collate += 10.0**5

			if collate != 0:
				scores.append(collate / float(folds))
			else:
				scores.append(10**5)
		else:
			scores.append(10.0**5)

	return scipy.asarray(scores)[:, nA]


def rerun_pls(chrom, xdata, groups, mask, factors):
	"""rerun pls on a subset of X-variables"""

	slice = scipy.take(xdata, chrom, 1)

	return PLS(slice, groups, mask, factors)


if __name__ == "__main__":
	import doctest

	from . import fitfun

	doctest.testmod(fitfun, verbose=True)
