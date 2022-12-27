from io import StringIO

import numpy as np


def str_array(arr: np.ndarray, col_sep: str = " ") -> str:
	"""A limited backport of str_array. Basically, `np.savetxt` into a string."""

	with StringIO() as f:
		np.savetxt(f, arr, delimiter=col_sep, comments="# ", encoding="utf-8")
		return f.getvalue()
