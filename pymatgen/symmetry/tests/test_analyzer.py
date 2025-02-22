# coding: utf-8

from __future__ import division, unicode_literals

"""
Created on Mar 9, 2012
"""


__author__ = "Shyue Ping Ong"
__copyright__ = "Copyright 2012, The Materials Project"
__version__ = "0.1"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyuep@gmail.com"
__date__ = "Mar 9, 2012"

import unittest
import os

import numpy as np

from pymatgen.core.sites import PeriodicSite
from pymatgen.io.vasp.inputs import Poscar
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer, \
    PointGroupAnalyzer, cluster_sites
from pymatgen.io.cif import CifParser
from pymatgen.util.testing import PymatgenTest
from pymatgen.core.structure import Molecule


test_dir_mol = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                            'test_files', "molecules")

test_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                        'test_files')


class SpacegroupAnalyzerTest(PymatgenTest):

    def setUp(self):
        p = Poscar.from_file(os.path.join(test_dir, 'POSCAR'))
        self.structure = p.structure
        self.sg = SpacegroupAnalyzer(self.structure, 0.001)
        self.disordered_structure = self.get_structure('Li10GeP2S12')
        self.disordered_sg = SpacegroupAnalyzer(self.disordered_structure, 0.001)
        s = p.structure.copy()
        site = s[0]
        del s[0]
        s.append(site.species_and_occu, site.frac_coords)
        self.sg3 = SpacegroupAnalyzer(s, 0.001)
        graphite = self.get_structure('Graphite')
        graphite.add_site_property("magmom", [0.1] * len(graphite))
        self.sg4 = SpacegroupAnalyzer(graphite, 0.001)

    def test_get_space_symbol(self):
        self.assertEqual(self.sg.get_spacegroup_symbol(), "Pnma")
        self.assertEqual(self.disordered_sg.get_spacegroup_symbol(),
                         "P4_2/nmc")
        self.assertEqual(self.sg3.get_spacegroup_symbol(), "Pnma")
        self.assertEqual(self.sg4.get_spacegroup_symbol(), "R-3m")

    def test_get_space_number(self):
        self.assertEqual(self.sg.get_spacegroup_number(), 62)
        self.assertEqual(self.disordered_sg.get_spacegroup_number(), 137)
        self.assertEqual(self.sg4.get_spacegroup_number(), 166)

    def test_get_hall(self):
        self.assertEqual(self.sg.get_hall(), '-P 2ac 2n')
        self.assertEqual(self.disordered_sg.get_hall(), 'P 4n 2n -1n')

    def test_get_pointgroup(self):
        self.assertEqual(self.sg.get_point_group(), 'mmm')
        self.assertEqual(self.disordered_sg.get_point_group(), '4/mmm')

    def test_get_symmetry_dataset(self):
        ds = self.sg.get_symmetry_dataset()
        self.assertEqual(ds['international'], 'Pnma')

    def test_get_crystal_system(self):
        crystal_system = self.sg.get_crystal_system()
        self.assertEqual('orthorhombic', crystal_system)
        self.assertEqual('tetragonal', self.disordered_sg.get_crystal_system())

    def test_get_symmetry_operations(self):
        fracsymmops = self.sg.get_symmetry_operations()
        symmops = self.sg.get_symmetry_operations(True)
        self.assertEqual(len(symmops), 8)
        latt = self.structure.lattice
        for fop, op in zip(fracsymmops, symmops):
            for site in self.structure:
                newfrac = fop.operate(site.frac_coords)
                newcart = op.operate(site.coords)
                self.assertTrue(np.allclose(latt.get_fractional_coords(newcart),
                                            newfrac))
                found = False
                newsite = PeriodicSite(site.species_and_occu, newcart, latt,
                                       coords_are_cartesian=True)
                for testsite in self.structure:
                    if newsite.is_periodic_image(testsite, 1e-3):
                        found = True
                        break
                self.assertTrue(found)

    def test_get_refined_structure(self):
        for a in self.sg.get_refined_structure().lattice.angles:
            self.assertEqual(a, 90)
        refined = self.disordered_sg.get_refined_structure()
        for a in refined.lattice.angles:
            self.assertEqual(a, 90)
        self.assertEqual(refined.lattice.a, refined.lattice.b)
        s = self.get_structure('Li2O')
        sg = SpacegroupAnalyzer(s, 0.001)
        self.assertEqual(sg.get_refined_structure().num_sites, 4 * s.num_sites)

    def test_get_symmetrized_structure(self):
        symm_struct = self.sg.get_symmetrized_structure()
        for a in symm_struct.lattice.angles:
            self.assertEqual(a, 90)
        self.assertEqual(len(symm_struct.equivalent_sites), 5)

        symm_struct = self.disordered_sg.get_symmetrized_structure()
        self.assertEqual(len(symm_struct.equivalent_sites), 8)
        self.assertEqual([len(i) for i in symm_struct.equivalent_sites],
                         [16,4,8,4,2,8,8,8])
        s1 = symm_struct.equivalent_sites[1][1]
        s2 = symm_struct[symm_struct.equivalent_indices[1][1]]
        self.assertEqual(s1, s2)
        self.assertEqual(self.sg4.get_symmetrized_structure()[0].magmom, 0.1)

    def test_find_primitive(self):
        """
        F m -3 m Li2O testing of converting to primitive cell
        """
        parser = CifParser(os.path.join(test_dir, 'Li2O.cif'))
        structure = parser.get_structures(False)[0]
        s = SpacegroupAnalyzer(structure)
        primitive_structure = s.find_primitive()
        self.assertEqual(primitive_structure.formula, "Li2 O1")
        # This isn't what is expected. All the angles should be 60
        self.assertAlmostEqual(primitive_structure.lattice.alpha, 60)
        self.assertAlmostEqual(primitive_structure.lattice.beta, 60)
        self.assertAlmostEqual(primitive_structure.lattice.gamma, 60)
        self.assertAlmostEqual(primitive_structure.lattice.volume,
                               structure.lattice.volume / 4.0)

    def test_get_ir_reciprocal_mesh(self):
        grid=self.sg.get_ir_reciprocal_mesh()
        self.assertEqual(len(grid), 216)
        self.assertAlmostEquals(grid[1][0][0], 0.1)
        self.assertAlmostEquals(grid[1][0][1], 0.0)
        self.assertAlmostEquals(grid[1][0][2], 0.0)
        self.assertEqual(grid[1][1], 2)

    def test_get_conventional_standard_structure(self):
        parser = CifParser(os.path.join(test_dir, 'bcc_1927.cif'))
        structure = parser.get_structures(False)[0]
        s = SpacegroupAnalyzer(structure, symprec=1e-2)
        conv = s.get_conventional_standard_structure()
        self.assertAlmostEqual(conv.lattice.alpha, 90)
        self.assertAlmostEqual(conv.lattice.beta, 90)
        self.assertAlmostEqual(conv.lattice.gamma, 90)
        self.assertAlmostEqual(conv.lattice.a, 9.1980270633769461)
        self.assertAlmostEqual(conv.lattice.b, 9.1980270633769461)
        self.assertAlmostEqual(conv.lattice.c, 9.1980270633769461)

        parser = CifParser(os.path.join(test_dir, 'btet_1915.cif'))
        structure = parser.get_structures(False)[0]
        s = SpacegroupAnalyzer(structure, symprec=1e-2)
        conv = s.get_conventional_standard_structure()
        self.assertAlmostEqual(conv.lattice.alpha, 90)
        self.assertAlmostEqual(conv.lattice.beta, 90)
        self.assertAlmostEqual(conv.lattice.gamma, 90)
        self.assertAlmostEqual(conv.lattice.a, 5.0615106678044235)
        self.assertAlmostEqual(conv.lattice.b, 5.0615106678044235)
        self.assertAlmostEqual(conv.lattice.c, 4.2327080177761687)

        parser = CifParser(os.path.join(test_dir, 'orci_1010.cif'))
        structure = parser.get_structures(False)[0]
        s = SpacegroupAnalyzer(structure, symprec=1e-2)
        conv = s.get_conventional_standard_structure()
        self.assertAlmostEqual(conv.lattice.alpha, 90)
        self.assertAlmostEqual(conv.lattice.beta, 90)
        self.assertAlmostEqual(conv.lattice.gamma, 90)
        self.assertAlmostEqual(conv.lattice.a, 2.9542233922299999)
        self.assertAlmostEqual(conv.lattice.b, 4.6330325651443296)
        self.assertAlmostEqual(conv.lattice.c, 5.373703587040775)

        parser = CifParser(os.path.join(test_dir, 'orcc_1003.cif'))
        structure = parser.get_structures(False)[0]
        s = SpacegroupAnalyzer(structure, symprec=1e-2)
        conv = s.get_conventional_standard_structure()
        self.assertAlmostEqual(conv.lattice.alpha, 90)
        self.assertAlmostEqual(conv.lattice.beta, 90)
        self.assertAlmostEqual(conv.lattice.gamma, 90)
        self.assertAlmostEqual(conv.lattice.a, 4.1430033493799998)
        self.assertAlmostEqual(conv.lattice.b, 31.437979757624728)
        self.assertAlmostEqual(conv.lattice.c, 3.99648651)

        parser = CifParser(os.path.join(test_dir, 'monoc_1028.cif'))
        structure = parser.get_structures(False)[0]
        s = SpacegroupAnalyzer(structure, symprec=1e-2)
        conv = s.get_conventional_standard_structure()
        self.assertAlmostEqual(conv.lattice.alpha, 90)
        self.assertAlmostEqual(conv.lattice.beta, 117.53832420192903)
        self.assertAlmostEqual(conv.lattice.gamma, 90)
        self.assertAlmostEqual(conv.lattice.a, 14.033435583000625)
        self.assertAlmostEqual(conv.lattice.b, 3.96052850731)
        self.assertAlmostEqual(conv.lattice.c, 6.8743926325200002)

        parser = CifParser(os.path.join(test_dir, 'rhomb_1170.cif'))
        structure = parser.get_structures(False)[0]
        s = SpacegroupAnalyzer(structure, symprec=1e-2)
        conv = s.get_conventional_standard_structure()
        self.assertAlmostEqual(conv.lattice.alpha, 90)
        self.assertAlmostEqual(conv.lattice.beta, 90)
        self.assertAlmostEqual(conv.lattice.gamma, 120)
        self.assertAlmostEqual(conv.lattice.a, 3.699919902005897)
        self.assertAlmostEqual(conv.lattice.b, 3.699919902005897)
        self.assertAlmostEqual(conv.lattice.c, 6.9779585500000003)

    def test_get_primitive_standard_structure(self):
        parser = CifParser(os.path.join(test_dir, 'bcc_1927.cif'))
        structure = parser.get_structures(False)[0]
        s = SpacegroupAnalyzer(structure, symprec=1e-2)
        prim = s.get_primitive_standard_structure()
        self.assertAlmostEqual(prim.lattice.alpha, 109.47122063400001)
        self.assertAlmostEqual(prim.lattice.beta, 109.47122063400001)
        self.assertAlmostEqual(prim.lattice.gamma, 109.47122063400001)
        self.assertAlmostEqual(prim.lattice.a, 7.9657251015812145)
        self.assertAlmostEqual(prim.lattice.b, 7.9657251015812145)
        self.assertAlmostEqual(prim.lattice.c, 7.9657251015812145)

        parser = CifParser(os.path.join(test_dir, 'btet_1915.cif'))
        structure = parser.get_structures(False)[0]
        s = SpacegroupAnalyzer(structure, symprec=1e-2)
        prim = s.get_primitive_standard_structure()
        self.assertAlmostEqual(prim.lattice.alpha, 105.015053349)
        self.assertAlmostEqual(prim.lattice.beta, 105.015053349)
        self.assertAlmostEqual(prim.lattice.gamma, 118.80658411899999)
        self.assertAlmostEqual(prim.lattice.a, 4.1579321075608791)
        self.assertAlmostEqual(prim.lattice.b, 4.1579321075608791)
        self.assertAlmostEqual(prim.lattice.c, 4.1579321075608791)

        parser = CifParser(os.path.join(test_dir, 'orci_1010.cif'))
        structure = parser.get_structures(False)[0]
        s = SpacegroupAnalyzer(structure, symprec=1e-2)
        prim = s.get_primitive_standard_structure()
        self.assertAlmostEqual(prim.lattice.alpha, 134.78923546600001)
        self.assertAlmostEqual(prim.lattice.beta, 105.856239333)
        self.assertAlmostEqual(prim.lattice.gamma, 91.276341676000001)
        self.assertAlmostEqual(prim.lattice.a, 3.8428217771014852)
        self.assertAlmostEqual(prim.lattice.b, 3.8428217771014852)
        self.assertAlmostEqual(prim.lattice.c, 3.8428217771014852)

        parser = CifParser(os.path.join(test_dir, 'orcc_1003.cif'))
        structure = parser.get_structures(False)[0]
        s = SpacegroupAnalyzer(structure, symprec=1e-2)
        prim = s.get_primitive_standard_structure()
        self.assertAlmostEqual(prim.lattice.alpha, 90)
        self.assertAlmostEqual(prim.lattice.beta, 90)
        self.assertAlmostEqual(prim.lattice.gamma, 164.985257335)
        self.assertAlmostEqual(prim.lattice.a, 15.854897098324196)
        self.assertAlmostEqual(prim.lattice.b, 15.854897098324196)
        self.assertAlmostEqual(prim.lattice.c, 3.99648651)

        parser = CifParser(os.path.join(test_dir, 'monoc_1028.cif'))
        structure = parser.get_structures(False)[0]
        s = SpacegroupAnalyzer(structure, symprec=1e-2)
        prim = s.get_primitive_standard_structure()
        self.assertAlmostEqual(prim.lattice.alpha, 63.579155761999999)
        self.assertAlmostEqual(prim.lattice.beta, 116.42084423747779)
        self.assertAlmostEqual(prim.lattice.gamma, 148.47965136208569)
        self.assertAlmostEqual(prim.lattice.a, 7.2908007159612325)
        self.assertAlmostEqual(prim.lattice.b, 7.2908007159612325)
        self.assertAlmostEqual(prim.lattice.c, 6.8743926325200002)

        parser = CifParser(os.path.join(test_dir, 'rhomb_1170.cif'))
        structure = parser.get_structures(False)[0]
        s = SpacegroupAnalyzer(structure, symprec=1e-2)
        prim = s.get_primitive_standard_structure()
        self.assertAlmostEqual(prim.lattice.alpha, 90)
        self.assertAlmostEqual(prim.lattice.beta, 90)
        self.assertAlmostEqual(prim.lattice.gamma, 120)
        self.assertAlmostEqual(prim.lattice.a, 3.699919902005897)
        self.assertAlmostEqual(prim.lattice.b, 3.699919902005897)
        self.assertAlmostEqual(prim.lattice.c, 6.9779585500000003)



class SpacegroupTest(unittest.TestCase):

    def setUp(self):
        p = Poscar.from_file(os.path.join(test_dir, 'POSCAR'))
        self.structure = p.structure
        self.sg1 = SpacegroupAnalyzer(self.structure, 0.001).get_spacegroup()

    def test_are_symmetrically_equivalent(self):
        sites1 = [self.structure[i] for i in [0, 1]]
        sites2 = [self.structure[i] for i in [2, 3]]
        self.assertTrue(self.sg1.are_symmetrically_equivalent(sites1, sites2,
                                                              1e-3))

        sites1 = [self.structure[i] for i in [0, 1]]
        sites2 = [self.structure[i] for i in [0, 2]]
        self.assertFalse(self.sg1.are_symmetrically_equivalent(sites1, sites2,
                                                               1e-3))



H2O2 = Molecule(["O", "O", "H", "H"],
                [[0, 0.727403, -0.050147], [0, -0.727403, -0.050147],
                 [0.83459, 0.897642, 0.401175],
                 [-0.83459, -0.897642, 0.401175]])

C2H2F2Br2 = Molecule(["C", "C", "F", "Br", "H", "F", "H", "Br"],
                     [[-0.752000, 0.001000, -0.141000],
                      [0.752000, -0.001000, 0.141000],
                      [-1.158000, 0.991000, 0.070000],
                      [-1.240000, -0.737000, 0.496000],
                      [-0.924000, -0.249000, -1.188000],
                      [1.158000, -0.991000, -0.070000],
                      [0.924000, 0.249000, 1.188000],
                      [1.240000, 0.737000, -0.496000]])

H2O = Molecule(["H", "O", "H"],
               [[0, 0.780362, -.456316], [0, 0, .114079],
                [0, -.780362, -.456316]])

C2H4 = Molecule(["C", "C", "H", "H", "H", "H"],
                [[0.0000, 0.0000, 0.6695], [0.0000, 0.0000, -0.6695],
                 [0.0000, 0.9289, 1.2321], [0.0000, -0.9289, 1.2321],
                 [0.0000, 0.9289, -1.2321], [0.0000, -0.9289, -1.2321]])

NH3 = Molecule(["N", "H", "H", "H"],
               [[0.0000, 0.0000, 0.0000], [0.0000, -0.9377, -0.3816],
                [0.8121, 0.4689, -0.3816], [-0.8121, 0.4689, -0.3816]])

BF3 = Molecule(["B", "F", "F", "F"],
               [[0.0000, 0.0000, 0.0000], [0.0000, -0.9377, 0.00],
                [0.8121, 0.4689, 0], [-0.8121, 0.4689, 0]])

CH4 = Molecule(["C", "H", "H", "H", "H"], [[0.000000, 0.000000, 0.000000],
               [0.000000, 0.000000, 1.08],
               [1.026719, 0.000000, -0.363000],
               [-0.513360, -0.889165, -0.363000],
               [-0.513360, 0.889165, -0.363000]])

PF6 = Molecule(["P", "F", "F", "F", "F", "F", "F"],
               [[0, 0, 0], [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0],
                [1, 0, 0], [-1, 0, 0]])


class PointGroupAnalyzerTest(PymatgenTest):

    def test_spherical(self):
        a = PointGroupAnalyzer(CH4)
        self.assertEqual(a.sch_symbol, "Td")
        self.assertEqual(len(a.get_pointgroup()), 24)
        a = PointGroupAnalyzer(PF6)
        self.assertEqual(a.sch_symbol, "Oh")
        self.assertEqual(len(a.get_pointgroup()), 48)
        m = Molecule.from_file(os.path.join(test_dir_mol, "c60.xyz"))
        a = PointGroupAnalyzer(m)
        self.assertEqual(a.sch_symbol, "Ih")

    def test_linear(self):
        coords = [[0.000000, 0.000000, 0.000000],
                  [0.000000, 0.000000, 1.08],
                  [0, 0.000000, -1.08]]
        mol = Molecule(["C", "H", "H"], coords)
        a = PointGroupAnalyzer(mol)
        self.assertEqual(a.sch_symbol, "D*h")
        mol = Molecule(["C", "H", "N"], coords)
        a = PointGroupAnalyzer(mol)
        self.assertEqual(a.sch_symbol, "C*v")

    def test_asym_top(self):
        coords = [[0.000000, 0.000000, 0.000000],
                  [0.000000, 0.000000, 1.08],
                  [1.026719, 0.000000, -0.363000],
                  [-0.513360, -0.889165, -0.363000],
                  [-0.513360, 0.889165, -0.363000]]
        mol = Molecule(["C", "H", "F", "Br", "Cl"], coords)
        a = PointGroupAnalyzer(mol)

        self.assertEqual(a.sch_symbol, "C1")
        self.assertEqual(len(a.get_pointgroup()), 1)
        coords = [[0.000000, 0.000000, 1.08],
                  [1.026719, 0.000000, -0.363000],
                  [-0.513360, -0.889165, -0.363000],
                  [-0.513360, 0.889165, -0.363000]]
        cs_mol = Molecule(["H", "F", "Cl", "Cl"], coords)
        a = PointGroupAnalyzer(cs_mol)
        self.assertEqual(a.sch_symbol, "Cs")
        self.assertEqual(len(a.get_pointgroup()), 2)
        a = PointGroupAnalyzer(C2H2F2Br2)
        self.assertEqual(a.sch_symbol, "Ci")
        self.assertEqual(len(a.get_pointgroup()), 2)

    def test_cyclic(self):
        a = PointGroupAnalyzer(H2O2)
        self.assertEqual(a.sch_symbol, "C2")
        self.assertEqual(len(a.get_pointgroup()), 2)
        a = PointGroupAnalyzer(H2O)
        self.assertEqual(a.sch_symbol, "C2v")
        self.assertEqual(len(a.get_pointgroup()), 4)
        a = PointGroupAnalyzer(NH3)
        self.assertEqual(a.sch_symbol, "C3v")
        self.assertEqual(len(a.get_pointgroup()), 6)
        cs2 = Molecule.from_file(os.path.join(test_dir_mol,
                                              "Carbon_Disulfide.xyz"))
        a = PointGroupAnalyzer(cs2, eigen_tolerance=0.001)
        self.assertEqual(a.sch_symbol, "C2v")

    def test_dihedral(self):
        a = PointGroupAnalyzer(C2H4)
        self.assertEqual(a.sch_symbol, "D2h")
        self.assertEqual(len(a.get_pointgroup()), 8)
        a = PointGroupAnalyzer(BF3)
        self.assertEqual(a.sch_symbol, "D3h")
        self.assertEqual(len(a.get_pointgroup()), 12)
        m = Molecule.from_file(os.path.join(test_dir_mol, "b12h12.xyz"))
        a = PointGroupAnalyzer(m)
        self.assertEqual(a.sch_symbol, "D5d")


class FuncTest(unittest.TestCase):

    def test_cluster_sites(self):
        o, c = cluster_sites(CH4, 0.1)
        self.assertEqual(o.specie.symbol, "C")
        self.assertEqual(len(c), 1)
        o, c = cluster_sites(C2H2F2Br2.get_centered_molecule(), 0.1)
        self.assertIsNone(o)
        self.assertEqual(len(c), 4)


if __name__ == "__main__":
    unittest.main()