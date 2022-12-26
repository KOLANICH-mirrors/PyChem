# -----------------------------------------------------------------------------
# Name:		   genetic.py
# Purpose:
#
# Author:	   Roger Jarvis
#
# Created:	   2006/06/20
# RCS-ID:	   $Id$
# Copyright:   (c) 2006
# Licence:	   GNU General Public License
# Description: A simple genetic algorithm for Python
# -----------------------------------------------------------------------------

import copy

import numpy as np
import scipy

from .chemometrics import _flip, _slice


def _sortrows(a, i=0):
	"""Sort rows of "a" in ascending order by column i"""
	keep = copy.deepcopy(a)
	ind, add, c = [], max(a[:, i]) + 10, 0
	for n in range(0, a.shape[0], 1):
		ind.append(scipy.argsort(a[:, i])[0])
		a[ind[n], i] = add
	for x in ind:
		a[c] = keep[x]
		c += 1
	return a


def _remdup(a, amax=None):
	"""Remove duplicates from vector a"""
	scipy.sort(a)
	flag = 0
	for x in range(1, len(a)):
		if (a[x - 1] + 1) - (a[x] + 1) == 0:
			flag = 1
	return flag


def _unique(a):
	id = []
	for count in range(a.shape[0]):
		chk = 0
		ord = scipy.sort(a[count])
		for i in range(1, len(ord)):
			if ord[i - 1] == ord[i]:
				chk = 1
		if chk == 0:
			id.append(count)
	return id


def crtpop(ni, nv, prec):
	"""Create a random population array of size
	ni by nv in the range 0:preci-1.  Use prec = 2
	to create binary string
	"""
	pop = scipy.around(scipy.rand(ni, nv) * (prec - 1))

	return pop


def rank(chrom, score):
	"""Linear ranking of individuals between
	0 (worst) and 2 (best)
	"""
	order = _sortrows(scipy.concatenate((score, chrom), 1))

	ranksc = scipy.zeros((chrom.shape[0], 1), "d")
	for x in range(1, len(score), 1):
		ranksc[x] = 2 * (float(x) / (chrom.shape[0] - 1))
	ranksc = _flip(ranksc)

	chrom = np.array(order[:, 1 : order.shape[1]])
	scores = scipy.reshape(order[:, 0], (order.shape[0], 1))

	return ranksc, chrom, scores


def select(ranksc, chrom, N):
	"""Stochastic universal sampling
	N is the generation gap (i.e. a real number between 0 and 1)
	"""
	N = round(chrom.shape[0] * N)
	cumsum = scipy.cumsum(ranksc, 0)
	susrange = scipy.rand(N, 1) * max(max(cumsum))

	sel = []
	for each in susrange:
		qcount, q0 = 0, cumsum[0]
		for q in cumsum:
			if q0 < each < q:
				sel.append(qcount)
			qcount += 1
			q0 = q
	nchrom = scipy.take(chrom, sel, 0)

	return nchrom


def xover(chrom, N, p):
	"""Single point crossover with probability N,precision p"""
	N = round(chrom.shape[0] * N)
	index1 = scipy.arange(chrom.shape[0])
	index2 = scipy.unique(
		scipy.around(
			scipy.rand(
				chrom.shape[0],
			)
			* chrom.shape[0]
		)
	)[0 : chrom.shape[0] / 2]
	sel1, sel2 = [], []
	for i in range(len(index1)):
		if index1[i] not in index2:
			sel1.append(index1[i])
		else:
			sel2.append(index1[i])
	select1 = sel1[0 : min([int(round(len(sel1) * N)), int(round(len(sel2) * N))])]
	select2 = sel2[0 : min([int(round(len(sel1) * N)), int(round(len(sel2) * N))])]

	# set xover points
	xoverpnt = scipy.around(
		scipy.rand(
			len(select1),
		)
		* (chrom.shape[1] - 1)
	)

	# perform xover
	nchrom = copy.deepcopy(chrom)
	for i in range(len(select1)):
		try:
			slice1 = chrom[select1[i], 0 : int(xoverpnt[i])]
			slice2 = chrom[select2[i], 0 : int(xoverpnt[i])]
			nchrom[select2[i], 0 : int(xoverpnt[i])] = slice1
			nchrom[select1[i], 0 : int(xoverpnt[i])] = slice2
		except:
			nchrom = nchrom

	return nchrom


def mutate(chrom, N, p):
	"""Mutation with probability N and precision p"""
	index = []
	for x in range(int(scipy.around(chrom.shape[0] * chrom.shape[1] * N))):
		index.append(
			(
				int(
					scipy.around(
						scipy.rand(
							1,
						)[0]
						* (chrom.shape[0] - 1)
					)
				),
				int(
					scipy.around(
						scipy.rand(
							1,
						)[0]
						* (chrom.shape[1] - 1)
					)
				),
			)
		)

	for x in index:
		if p == 1:
			if chrom[x] == 1:
				chrom[x] = 0
			else:
				chrom[x] = 1
		else:
			chrom[x] = int(
				scipy.around(
					scipy.rand(
						1,
					)[0]
					* (p - 1)
				)
			)

	return chrom


def reinsert(ch, selch, chsc, selsc):
	"""Reinsert evolved population into original pop
	retaining the best individuals
	"""
	newChrom = scipy.concatenate((ch, selch), 0)
	newScore = scipy.concatenate((chsc, selsc), 0)

	# select only unique chroms - can be removed
	uid = []
	for i in range(len(newChrom)):
		if len(scipy.unique(newChrom[i, :])) == ch.shape[1]:
			uid.append(i)
	newScore = scipy.take(newScore, uid, 0)
	newChrom = scipy.take(newChrom, uid, 0)

	idx = scipy.argsort(newScore, 0)[:, 0].tolist()
	idx = idx[0 : ch.shape[0]]

	newChrom = scipy.take(newChrom, idx, 0)
	newScore = scipy.take(newScore, idx, 0)

	return newChrom, newScore


if __name__ == "__main__":
	import doctest

	from . import genetic

	doctest.testmod(genetic, verbose=True)
