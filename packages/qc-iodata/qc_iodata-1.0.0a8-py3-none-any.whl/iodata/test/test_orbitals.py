# IODATA is an input and output module for quantum chemistry.
# Copyright (C) 2011-2019 The IODATA Development Team
#
# This file is part of IODATA.
#
# IODATA is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# IODATA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
# --
"""Unit tests for iodata.orbitals."""

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_equal

from ..orbitals import MolecularOrbitals


def test_wrong_kind():
    with pytest.raises(ValueError):
        MolecularOrbitals("foo", 5, 5)


def test_restricted_empty():
    with pytest.raises(ValueError):
        MolecularOrbitals("restricted", 3, None)
    with pytest.raises(ValueError):
        MolecularOrbitals("restricted", None, 5)
    with pytest.raises(ValueError):
        MolecularOrbitals("restricted", None, None)
    with pytest.raises(ValueError):
        MolecularOrbitals("restricted", 5, 3)
    mo = MolecularOrbitals("restricted", 5, 5)
    assert mo.norba == 5
    assert mo.norbb == 5
    assert mo.nelec is None
    assert mo.nbasis is None
    assert mo.norb == 5
    assert mo.spinpol is None
    assert mo.occsa is None
    assert mo.occsb is None
    assert mo.coeffsa is None
    assert mo.coeffsb is None
    assert mo.energiesa is None
    assert mo.energiesb is None
    assert mo.irrepsa is None
    assert mo.irrepsb is None
    # Test setters for occsa
    occsa = np.array([1, 1, 0.5, 0.5, 0.0])
    mo.occsa = occsa
    assert_allclose(mo.occsa, occsa)
    assert_allclose(mo.occsb, 0.0)
    assert_allclose(mo.occs, occsa)
    assert_allclose(mo.occs_aminusb, occsa)
    # Test setters for occsb
    mo.occs = None
    mo.occs_aminusb = None
    occsb = np.array([0.5, 1, 1, 0.5, 0.0])
    mo.occsb = occsb
    assert_allclose(mo.occsa, 0.0)
    assert_allclose(mo.occsb, occsb)
    assert_allclose(mo.occs, occsb)
    assert_allclose(mo.occs_aminusb, -occsb)


def test_restricted_occs():
    occs = [2, 2, 0, 0, 0]
    with pytest.raises(TypeError):
        MolecularOrbitals("restricted", 3, 3, occs=occs)
    mo = MolecularOrbitals("restricted", 5, 5, occs=occs)
    assert mo.norba == 5
    assert mo.norbb == 5
    assert mo.nelec == 4
    assert mo.nbasis is None
    assert mo.norb == 5
    assert mo.spinpol == 0
    # Test heuristics for ROHF or ROKS
    assert_equal(mo.occsa, [1, 1, 0, 0, 0])
    assert_equal(mo.occsb, [1, 1, 0, 0, 0])
    assert mo.coeffsa is None
    assert mo.coeffsb is None
    assert mo.energiesa is None
    assert mo.energiesb is None
    assert mo.irrepsa is None
    assert mo.irrepsb is None
    # Test setters
    mo.occsa = [1, 0.3, 0.7, 0, 0]
    assert_allclose(mo.occsa, [1, 0.3, 0.7, 0, 0])
    assert_allclose(mo.occsb, [1, 1, 0, 0, 0])
    assert_allclose(mo.occs_aminusb, [0, -0.7, 0.7, 0, 0])
    mo.occs_aminusb = None
    mo.occs = occs
    assert_equal(mo.occsa, [1, 1, 0, 0, 0])
    assert_equal(mo.occsb, [1, 1, 0, 0, 0])
    mo.occsb = [0.2, 0.8, 0, 0, 0]
    assert_allclose(mo.occsa, [1, 1, 0, 0, 0])
    assert_allclose(mo.occsb, [0.2, 0.8, 0, 0, 0])
    assert_allclose(mo.occs_aminusb, [0.8, 0.2, 0, 0, 0])
    # Test heuristics for closed-shell natural orbitals
    mo.occs = [2, 1.8, 0.2, 0, 0]
    mo.occs_aminusb = None
    assert_allclose(mo.occsa, [1, 0.9, 0.1, 0, 0])
    assert_allclose(mo.occsb, [1, 0.9, 0.1, 0, 0])
    assert_allclose(mo.spinpol, 0.0)


def test_restricted_occs_aminusb():
    occs = [2.0, 1.3, 0.7]
    occs_aminusb = [0.0, 0.7, 0.1]
    with pytest.raises(TypeError):
        MolecularOrbitals("restricted", 2, 2, occs=occs, occs_aminusb=occs_aminusb)
    mo = MolecularOrbitals("restricted", 3, 3, occs=occs, occs_aminusb=occs_aminusb)
    assert mo.norba == 3
    assert mo.norbb == 3
    assert_allclose(mo.nelec, 4.0)
    assert mo.nbasis is None
    assert mo.norb == 3
    assert_allclose(mo.occsa, [1.0, 1.0, 0.4])
    assert_allclose(mo.occsb, [1.0, 0.3, 0.3])
    assert_allclose(mo.spinpol, 0.8)
    assert mo.coeffsa is None
    assert mo.coeffsb is None
    assert mo.energiesa is None
    assert mo.energiesb is None
    assert mo.irrepsa is None
    assert mo.irrepsb is None
    # Verify that in-place modification of occsa and occsb does not work.
    with pytest.raises(ValueError):
        mo.occsa[1] = 0.5
    assert_allclose(mo.occsa, [1.0, 1.0, 0.4])
    with pytest.raises(ValueError):
        mo.occsb[1] = 0.5
    assert_allclose(mo.occsb, [1.0, 0.3, 0.3])
    # Verify that shooting in one's own foot is still an option.
    occsa_foo = mo.occsa
    occsa_foo.flags.writeable = True
    occsa_foo[1] = 0.5
    assert_allclose(mo.occsa, [1.0, 1.0, 0.4])
    # Test setters
    mo.occsa = [1.0, 0.3, 0.7]
    assert_allclose(mo.occsa, [1.0, 0.3, 0.7])
    assert_allclose(mo.occsb, [1.0, 0.3, 0.3])
    assert_allclose(mo.occs_aminusb, [0, 0.0, 0.4], atol=1e-10)
    assert_allclose(mo.spinpol, 0.4)
    mo.occsb = [0.2, 0.8, 0.0]
    assert_allclose(mo.occsa, [1.0, 0.3, 0.7])
    assert_allclose(mo.occsb, [0.2, 0.8, 0.0])
    assert_allclose(mo.occs_aminusb, [0.8, -0.5, 0.7])
    assert_allclose(mo.spinpol, 1.0)
    # Test reverting back to heuristics
    assert_allclose(mo.occs, [1.2, 1.1, 0.7])
    mo.occs_aminusb = None
    assert_allclose(mo.occsa, [0.6, 0.55, 0.35])
    assert_allclose(mo.occsb, [0.6, 0.55, 0.35])
    assert_allclose(mo.spinpol, 0.0)


def test_restricted_coeffs():
    rng = np.random.default_rng(1)
    coeffs = rng.uniform(-1, 1, (7, 5))
    with pytest.raises(TypeError):
        MolecularOrbitals("restricted", 3, 3, coeffs=coeffs)
    mo = MolecularOrbitals("restricted", 5, 5, coeffs=coeffs)
    assert mo.norba == 5
    assert mo.norbb == 5
    assert mo.nelec is None
    assert mo.nbasis == 7
    assert mo.norb == 5
    assert mo.spinpol is None
    assert mo.occsa is None
    assert mo.occsb is None
    assert mo.coeffsa is coeffs
    assert mo.coeffsb is coeffs
    assert mo.energiesa is None
    assert mo.energiesb is None
    assert mo.irrepsa is None
    assert mo.irrepsb is None


def test_restricted_energies():
    rng = np.random.default_rng(1)
    energies = rng.uniform(-1, 1, 5)
    with pytest.raises(TypeError):
        MolecularOrbitals("restricted", 3, 3, energies=energies)
    mo = MolecularOrbitals("restricted", 5, 5, energies=energies)
    assert mo.norba == 5
    assert mo.norbb == 5
    assert mo.nelec is None
    assert mo.nbasis is None
    assert mo.norb == 5
    assert mo.spinpol is None
    assert mo.occsa is None
    assert mo.occsb is None
    assert mo.coeffsa is None
    assert mo.coeffsb is None
    assert mo.energiesa is energies
    assert mo.energiesb is energies
    assert mo.irrepsa is None
    assert mo.irrepsb is None


def test_restricted_irreps():
    irreps = ["A", "A", "B", "A", "B"]
    with pytest.raises(TypeError):
        MolecularOrbitals("restricted", 3, 3, irreps=irreps)
    mo = MolecularOrbitals("restricted", 5, 5, irreps=irreps)
    assert mo.norba == 5
    assert mo.norbb == 5
    assert mo.nelec is None
    assert mo.nbasis is None
    assert mo.norb == 5
    assert mo.spinpol is None
    assert mo.occsa is None
    assert mo.occsb is None
    assert mo.coeffsa is None
    assert mo.coeffsb is None
    assert mo.energiesa is None
    assert mo.energiesb is None
    assert mo.irrepsa is irreps
    assert mo.irrepsb is irreps


def test_unrestricted_empty():
    with pytest.raises(ValueError):
        MolecularOrbitals("unrestricted", 3, None)
    with pytest.raises(ValueError):
        MolecularOrbitals("unrestricted", None, 5)
    with pytest.raises(ValueError):
        MolecularOrbitals("unrestricted", None, None)
    mo = MolecularOrbitals("unrestricted", 5, 3)
    assert mo.norba == 5
    assert mo.norbb == 3
    assert mo.nelec is None
    assert mo.nbasis is None
    assert mo.norb == 8
    assert mo.spinpol is None
    assert mo.occsa is None
    assert mo.occsb is None
    assert mo.coeffsa is None
    assert mo.coeffsb is None
    assert mo.energiesa is None
    assert mo.energiesb is None
    assert mo.irrepsa is None
    assert mo.irrepsb is None


def test_unrestricted_occs():
    occs = [1, 1, 0, 0, 0, 1, 0, 0]
    with pytest.raises(TypeError):
        MolecularOrbitals("unrestricted", 3, 2, occs=occs)
    mo = MolecularOrbitals("unrestricted", 5, 3, occs=occs)
    assert mo.norba == 5
    assert mo.norbb == 3
    assert mo.nelec == 3
    assert mo.nbasis is None
    assert mo.norb == 8
    assert mo.spinpol == 1
    assert_equal(mo.occsa, [1, 1, 0, 0, 0])
    assert_equal(mo.occsb, [1, 0, 0])
    assert mo.coeffsa is None
    assert mo.coeffsb is None
    assert mo.energiesa is None
    assert mo.energiesb is None
    assert mo.irrepsa is None
    assert mo.irrepsb is None
    # Test setters for occsa and occsb
    occsa = np.array([1, 1, 0.5, 0.5, 0.0])
    mo.occsa = occsa
    assert_allclose(mo.occsa, occsa)
    occsb = np.array([1, 0.7, 0.3])
    mo.occsb = occsb
    assert_allclose(mo.occsb, occsb)
    assert_allclose(mo.occs, np.concatenate([occsa, occsb]))
    # Test in-place modification of occsa and occsb, which should just work.
    mo.occs = occs
    mo.occsa[:] = occsa
    assert_allclose(mo.occsa, occsa)
    occsb = np.array([1, 0.7, 0.3])
    mo.occsb[:] = occsb
    assert_allclose(mo.occsb, occsb)
    assert_allclose(mo.occs, np.concatenate([occsa, occsb]))


def test_unrestricted_occs_aminusb():
    occs = [2, 1, 0]
    occs_aminusb = [0, 1, 0]
    with pytest.raises(ValueError):
        MolecularOrbitals("unrestricted", 2, 1, occs=occs, occs_aminusb=occs_aminusb)


def test_unrestricted_coeffs():
    rng = np.random.default_rng(1)
    coeffs = rng.uniform(-1, 1, (7, 8))
    with pytest.raises(TypeError):
        MolecularOrbitals("unrestricted", 3, 2, coeffs=coeffs)
    mo = MolecularOrbitals("unrestricted", 5, 3, coeffs=coeffs)
    assert mo.norba == 5
    assert mo.norbb == 3
    assert mo.nelec is None
    assert mo.nbasis == 7
    assert mo.norb == 8
    assert mo.spinpol is None
    assert mo.occsa is None
    assert mo.occsb is None
    assert_equal(mo.coeffsa, coeffs[:, :5])
    assert_equal(mo.coeffsb, coeffs[:, 5:])
    assert mo.energiesa is None
    assert mo.energiesb is None
    assert mo.irrepsa is None
    assert mo.irrepsb is None


def test_unrestricted_energies():
    rng = np.random.default_rng(1)
    energies = rng.uniform(-1, 1, 8)
    with pytest.raises(TypeError):
        MolecularOrbitals("unrestricted", 3, 2, energies=energies)
    mo = MolecularOrbitals("unrestricted", 5, 3, energies=energies)
    assert mo.norba == 5
    assert mo.norbb == 3
    assert mo.nelec is None
    assert mo.nbasis is None
    assert mo.norb == 8
    assert mo.spinpol is None
    assert mo.occsa is None
    assert mo.occsb is None
    assert mo.coeffsa is None
    assert mo.coeffsb is None
    assert_equal(mo.energiesa, energies[:5])
    assert_equal(mo.energiesb, energies[5:])
    assert mo.irrepsa is None
    assert mo.irrepsb is None


def test_unrestricted_irreps():
    irreps = ["A", "A", "B", "A", "B", "B", "B", "A"]
    with pytest.raises(TypeError):
        MolecularOrbitals("unrestricted", 3, 2, irreps=irreps)
    mo = MolecularOrbitals("unrestricted", 5, 3, irreps=irreps)
    assert mo.norba == 5
    assert mo.norbb == 3
    assert mo.nelec is None
    assert mo.nbasis is None
    assert mo.norb == 8
    assert mo.spinpol is None
    assert mo.occsa is None
    assert mo.occsb is None
    assert mo.coeffsa is None
    assert mo.coeffsb is None
    assert mo.energiesa is None
    assert mo.energiesb is None
    # irreps are lists, not arrays
    assert mo.irrepsa == irreps[:5]
    assert mo.irrepsb == irreps[5:]


def test_generalized_empty():
    with pytest.raises(ValueError):
        mo = MolecularOrbitals("generalized", 5, 3)
    with pytest.raises(ValueError):
        mo = MolecularOrbitals("generalized", 5, None)
    with pytest.raises(ValueError):
        mo = MolecularOrbitals("generalized", None, 3)
    mo = MolecularOrbitals("generalized", None, None)
    assert mo.norba is None
    assert mo.norbb is None
    assert mo.nelec is None
    assert mo.nbasis is None
    assert mo.norb is None
    with pytest.raises(NotImplementedError):
        _ = mo.spinpol
    with pytest.raises(NotImplementedError):
        _ = mo.occsa
    with pytest.raises(NotImplementedError):
        _ = mo.occsb
    with pytest.raises(NotImplementedError):
        _ = mo.coeffsa
    with pytest.raises(NotImplementedError):
        _ = mo.coeffsb
    with pytest.raises(NotImplementedError):
        _ = mo.energiesa
    with pytest.raises(NotImplementedError):
        _ = mo.energiesb
    with pytest.raises(NotImplementedError):
        _ = mo.irrepsa
    with pytest.raises(NotImplementedError):
        _ = mo.irrepsb


def test_generalized_occs():
    mo = MolecularOrbitals("generalized", None, None, occs=[1, 1, 1, 1, 1, 0, 0])
    assert mo.norba is None
    assert mo.norbb is None
    assert mo.nelec == 5
    assert mo.nbasis is None
    assert mo.norb == 7
    with pytest.raises(NotImplementedError):
        _ = mo.spinpol
    with pytest.raises(NotImplementedError):
        _ = mo.occsa
    with pytest.raises(NotImplementedError):
        _ = mo.occsb
    with pytest.raises(NotImplementedError):
        _ = mo.coeffsa
    with pytest.raises(NotImplementedError):
        _ = mo.coeffsb
    with pytest.raises(NotImplementedError):
        _ = mo.energiesa
    with pytest.raises(NotImplementedError):
        _ = mo.energiesb
    with pytest.raises(NotImplementedError):
        _ = mo.irrepsa
    with pytest.raises(NotImplementedError):
        _ = mo.irrepsb


def test_generalized_occs_aminusb():
    occs = [2, 1, 0]
    occs_aminusb = [0, 1, 0]
    with pytest.raises(ValueError):
        MolecularOrbitals("generalized", None, None, occs=occs, occs_aminusb=occs_aminusb)


def test_generalized_coeffs():
    rng = np.random.default_rng(1)
    coeffs = rng.uniform(-1, 1, (10, 7))
    mo = MolecularOrbitals("generalized", None, None, coeffs=coeffs)
    assert mo.norba is None
    assert mo.norbb is None
    assert mo.nelec is None
    assert mo.nbasis == 5  # 5 *spatial* basis functions!
    assert mo.norb == 7
    with pytest.raises(NotImplementedError):
        _ = mo.spinpol
    with pytest.raises(NotImplementedError):
        _ = mo.occsa
    with pytest.raises(NotImplementedError):
        _ = mo.occsb
    with pytest.raises(NotImplementedError):
        _ = mo.coeffsa
    with pytest.raises(NotImplementedError):
        _ = mo.coeffsb
    with pytest.raises(NotImplementedError):
        _ = mo.energiesa
    with pytest.raises(NotImplementedError):
        _ = mo.energiesb
    with pytest.raises(NotImplementedError):
        _ = mo.irrepsa
    with pytest.raises(NotImplementedError):
        _ = mo.irrepsb


def test_generalized_energies():
    rng = np.random.default_rng(1)
    energies = rng.uniform(-1, 1, 7)
    mo = MolecularOrbitals("generalized", None, None, energies=energies)
    assert mo.norba is None
    assert mo.norbb is None
    assert mo.nelec is None
    assert mo.nbasis is None
    assert mo.norb == 7
    with pytest.raises(NotImplementedError):
        _ = mo.spinpol
    with pytest.raises(NotImplementedError):
        _ = mo.occsa
    with pytest.raises(NotImplementedError):
        _ = mo.occsb
    with pytest.raises(NotImplementedError):
        _ = mo.coeffsa
    with pytest.raises(NotImplementedError):
        _ = mo.coeffsb
    with pytest.raises(NotImplementedError):
        _ = mo.energiesa
    with pytest.raises(NotImplementedError):
        _ = mo.energiesb
    with pytest.raises(NotImplementedError):
        _ = mo.irrepsa
    with pytest.raises(NotImplementedError):
        _ = mo.irrepsb


def test_generalized_irreps():
    irreps = ["A", "B", "A", "A", "B", "B", "B"]
    mo = MolecularOrbitals("generalized", None, None, irreps=irreps)
    assert mo.norba is None
    assert mo.norbb is None
    assert mo.nelec is None
    assert mo.nbasis is None
    assert mo.norb == 7
    with pytest.raises(NotImplementedError):
        _ = mo.spinpol
    with pytest.raises(NotImplementedError):
        _ = mo.occsa
    with pytest.raises(NotImplementedError):
        _ = mo.occsb
    with pytest.raises(NotImplementedError):
        mo.occsa = [1, 1, 1, 0, 0, 0, 0]
    with pytest.raises(NotImplementedError):
        mo.occsb = [1, 1, 1, 0, 0, 0, 0]
    with pytest.raises(NotImplementedError):
        _ = mo.coeffsa
    with pytest.raises(NotImplementedError):
        _ = mo.coeffsb
    with pytest.raises(NotImplementedError):
        _ = mo.energiesa
    with pytest.raises(NotImplementedError):
        _ = mo.energiesb
    with pytest.raises(NotImplementedError):
        _ = mo.irrepsa
    with pytest.raises(NotImplementedError):
        _ = mo.irrepsb
