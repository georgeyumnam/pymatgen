# coding: utf-8

from __future__ import division, unicode_literals

"""
FIXME: Proper module docstring
"""


__author__ = "Shyue Ping Ong"
__copyright__ = "Copyright 2012, The Materials Project"
__version__ = "0.1"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyuep@gmail.com"
__date__ = "Aug 26, 2012"

import unittest

from pymatgen.util.string_utils import generate_latex_table, str_delimited, \
    str_aligned, formula_double_format, latexify, latexify_spacegroup


class FuncTest(unittest.TestCase):

    def test_latexify(self):
        self.assertEqual(latexify("Li3Fe2(PO4)3"),
                         "Li$_{3}$Fe$_{2}$(PO$_{4}$)$_{3}$")
        self.assertEqual(latexify("Li0.2Na0.8Cl"),
                         "Li$_{0.2}$Na$_{0.8}$Cl")

    def test_latexify_spacegroup(self):
        self.assertEqual(latexify_spacegroup("Fd-3m"), "Fd$\overline{3}$m")
        self.assertEqual(latexify_spacegroup("P2_1/c"), "P2$_{1}$/c")

    def test_str_aligned_delimited(self):
        data = [["a", "bb"], ["ccc", "dddd"]]
        ans = """  a     bb
ccc   dddd"""
        self.assertEqual(str_aligned(data), ans)
        self.assertEqual(str_aligned(data, header=["X", "Y"]),
                         '  X      Y\n----------\n  a     bb\nccc   dddd')
        self.assertEqual(str_delimited(data), 'a\tbb\nccc\tdddd')

    def test_generate_latex_table(self):
        data = [["a", "bb"], ["ccc", "dddd"]]
        self.assertEqual(generate_latex_table(data), '\\begin{table}[H]\n\\caption{Caption}\n\\label{Label}\n\\begin{tabular*}{\\textwidth}{@{\\extracolsep{\\fill}}cc}\n\\hline\na & bb\\\\\nccc & dddd\\\\\n\\hline\n\\end{tabular*}\n\\end{table}')

    def test_formula_double_format(self):
        self.assertEqual(formula_double_format(1.00), "")
        self.assertEqual(formula_double_format(2.00), "2")
        self.assertEqual(formula_double_format(2.10), "2.1")
        self.assertEqual(formula_double_format(2.10000000002), "2.1")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
