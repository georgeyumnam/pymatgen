# coding: utf-8

from __future__ import unicode_literals, division, print_function

import os

from pymatgen.util.testing import PymatgenTest
from pymatgen.core.structure import Structure
from pymatgen.core.units import Ha_to_eV
from pymatgen.io.abinitio.abiobjects import *

import warnings

test_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..",
                        'test_files')


def cif_paths():
    cifpaths = []
    print(test_dir)
    for fname in os.listdir(test_dir):
        fname = os.path.join(test_dir, fname)
        if os.path.isfile(fname) and fname.endswith(".cif"):
            cifpaths.append(fname)

    assert cifpaths
    return cifpaths


class SpinModeTest(PymatgenTest):

    def test_base(self):
        polarized = SpinMode.as_spinmode("polarized")
        other_polarized = SpinMode.as_spinmode("polarized")
        unpolarized = SpinMode.as_spinmode("unpolarized")

        polarized.to_abivars()

        self.assertTrue(polarized is other_polarized)
        self.assertTrue(polarized == other_polarized)
        self.assertTrue(polarized != unpolarized)

        # Test pickle
        self.serialize_with_pickle(polarized)

        # Test dict methods
        self.assertPMGSONable(polarized)
        self.assertPMGSONable(unpolarized)


class SmearingTest(PymatgenTest):
    def test_base(self):
        fd1ev = Smearing.as_smearing("fermi_dirac:1 eV")
        print(fd1ev)
        fd1ev.to_abivars()

        self.assertTrue(fd1ev)

        same_fd = Smearing.as_smearing("fermi_dirac:"+ str(1.0/Ha_to_eV))

        self.assertTrue(same_fd == fd1ev)

        nosmear = Smearing.nosmearing()

        self.assertFalse(nosmear)
        self.assertTrue(nosmear != fd1ev)
        new_fd1ev = Smearing.from_dict(fd1ev.as_dict())
        self.assertTrue(new_fd1ev == fd1ev)

        # Test pickle
        self.serialize_with_pickle(fd1ev)

        # Test dict methods
        self.assertPMGSONable(fd1ev)


class ElectronsAlgorithmTest(PymatgenTest):
    def test_base(self):
        algo = ElectronsAlgorithm(nstep=70)
        print(algo.to_abivars())

        # Test pickle
        self.serialize_with_pickle(algo)


class ElectronsTest(PymatgenTest):
    def test_base(self):
        default_electrons = Electrons()
        self.assertTrue(default_electrons.nsppol==2)
        self.assertTrue(default_electrons.nspinor==1)
        self.assertTrue(default_electrons.nspden==2)

        print(default_electrons.to_abivars())

        #new = Electron.from_dict(default_electrons.as_dict())

        # Test pickle
        self.serialize_with_pickle(default_electrons, test_eq=False)


class KSamplingTest(PymatgenTest):

    def test_base(self):
        monkhorst = KSampling.monkhorst((3, 3, 3), (0.5, 0.5, 0.5), 0, False, False)
        gamma_centered = KSampling.gamma_centered((3, 3, 3), False, False)

        monkhorst.to_abivars()

        # Test dict methods
        self.assertPMGSONable(monkhorst)
        self.assertPMGSONable(gamma_centered)

class RelaxationTest(PymatgenTest):

    def test_base(self):
        atoms_and_cell = RelaxationMethod.atoms_and_cell()
        atoms_only = RelaxationMethod.atoms_only()

        atoms_and_cell.to_abivars()

        # Test dict methods
        self.assertPMGSONable(atoms_and_cell)
        self.assertPMGSONable(atoms_only)


class PPModelTest(PymatgenTest):

    def test_base(self):
        godby = PPModel.as_ppmodel("godby:12 eV")
        print(godby)
        print(repr(godby))
        godby.to_abivars()
        self.assertTrue(godby)

        same_godby = PPModel.as_ppmodel("godby:"+ str(12.0/Ha_to_eV))
        self.assertTrue(same_godby == godby)

        noppm = PPModel.noppmodel()

        self.assertFalse(noppm)
        self.assertTrue(noppm != godby)
        new_godby = PPModel.from_dict(godby.as_dict())
        self.assertTrue(new_godby == godby)

        # Test pickle
        self.serialize_with_pickle(godby)

        # Test dict methods
        self.assertPMGSONable(godby)


if __name__ == '__main__':
    import unittest
    unittest.main()
