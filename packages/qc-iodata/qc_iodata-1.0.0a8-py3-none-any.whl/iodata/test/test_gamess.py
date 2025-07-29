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
"""Test iodata.formats.gamess module."""

from importlib.resources import as_file, files

from numpy.testing import assert_allclose, assert_equal

from ..api import load_one
from ..utils import angstrom


def test_load_one_gamess_punch():
    with as_file(files("iodata.test.data").joinpath("PCGamess_PUNCH.dat")) as f:
        data = load_one(str(f))
    size = len(["CL", "H", "H", "H", "H", "F", "F", "F", "F", "H", "F"])
    assert data.title == "Simple example sample optimization with Hessian output for Toon"
    assert data.g_rot == "C1"
    assert_equal(data.atnums.shape, (size,))
    assert_equal(data.atnums[0], 17)
    assert_equal(data.atnums[1], 1)
    assert_equal(data.atnums[-1], 9)
    assert_equal(data.atcoords.shape, (size, 3))
    assert_allclose(data.atcoords[0, 1] / angstrom, -0.1843157808)
    assert_allclose(data.atcoords[3, -1] / angstrom, 1.2926708150)
    assert_allclose(data.atcoords[-1, 0] / angstrom, 3.8608437748)
    assert_allclose(data.energy, -959.9675629527)
    assert_equal(data.atgradient.shape, (size, 3))
    assert data.atgradient[0, 1] - 1.5314677838e-05 < 1e-10
    assert abs(data.atgradient[3, -1] - 8.5221217336e-06) < 1e-10
    assert abs(data.atgradient[-1, 0] - 2.1211421041e-05) < 1e-10
    assert_equal(data.athessian.shape, (3 * size, 3 * size))
    assert abs(data.athessian - data.athessian.transpose()).max() < 1e-10
    assert abs(data.athessian[0, 0] - 2.51645239e-02) < 1e-10
    assert abs(data.athessian[0, -1] - -1.27201108e-04) < 1e-10
    assert abs(data.athessian[-1, 0] - -1.27201108e-04) < 1e-10
    assert abs(data.athessian[-1, -1] - 7.34538698e-03) < 1e-10
    assert_equal(data.atmasses.shape, (size,))
    assert_allclose(data.atmasses[0], 34.96885)
    assert_allclose(data.atmasses[3], 1.00782)
    assert_allclose(data.atmasses[-1], 18.99840)
