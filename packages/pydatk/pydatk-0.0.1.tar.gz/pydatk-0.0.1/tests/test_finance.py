import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
import pydatk as ptk

class TestFinance(unittest.TestCase):

    def test_effective_rate(self):
        er = round(100 * ptk.finance.effective_rate(0.06, 12), 2)
        self.assertEqual(er, 6.17)