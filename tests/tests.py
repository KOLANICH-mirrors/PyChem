#!/usr/bin/env python3
import itertools
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from collections import OrderedDict

dict = OrderedDict

import PyChem
from PyChem import *


class Tests(unittest.TestCase):
	def testSimple(self):
		raise NotImplementedError


if __name__ == "__main__":
	unittest.main()
