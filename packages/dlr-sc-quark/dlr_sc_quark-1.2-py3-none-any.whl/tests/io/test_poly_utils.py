# Copyright 2020 DLR-SC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" module for testing the helper functions for storing different types of Polynomials """

import os
import pytest
import h5py

from quark import PolyBinary, PolyIsing
from quark.io import hdf5_attributes
from quark.io.poly_utils import write_poly_with_type, read_poly_with_type


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"
FILE = "poly_utils.h5"
FILENAME_TMP = TEST_DIR + FILE
FILENAME_FIX = TEST_DIR + "testdata/" + FILE
GROUP_NAME = "test_group"

NAME = "test_poly_ising"
POLY_ISING = PolyIsing({(("y", 2, 3), ("x", 1)): 2, (("y", 1, 2),): 3}, inverted=True)
POLY_BINARY = PolyBinary({(("x", 1),): 2.5, (("x", 2), ("y", 0, 0)): 2.0, (): 5.5})


def test_write_poly_with_type():
    with h5py.File(FILENAME_TMP, "w") as h5file:
        group = h5file.create_group(GROUP_NAME)

        write_poly_with_type(group, POLY_ISING, NAME)

        assert NAME in group
        poly_group = group[NAME]
        assert "type" in poly_group.attrs
        type_str = hdf5_attributes.read_attribute(poly_group, "type")
        assert type_str == "PolyIsing"

    os.remove(FILENAME_TMP)

def test_read_poly_with_type():
    with h5py.File(FILENAME_FIX, "r") as h5file:
        group = h5file[GROUP_NAME]

        # load Polynomial stored under a name
        poly = read_poly_with_type(group, NAME)
        assert isinstance(poly, PolyIsing)
        assert poly == POLY_ISING

        message = f"Did not find Polynomial 'wrong_name' in group '/test_group' in hdf5 file '.*{FILE}'"
        with pytest.raises(ValueError, match=message):
            read_poly_with_type(group, "wrong_name")

        message = "Found too much Polynomials in group '/test_group'"
        with pytest.raises(ValueError, match=message):
            # there are too much unnamed Polynomials in this group
            read_poly_with_type(group)

        # but if the name corresponds to a valid type we can load it nevertheless
        poly = read_poly_with_type(group, name="PolyBinary")
        assert isinstance(poly, PolyBinary)
        assert poly == POLY_BINARY

        # if the unnamed Polynomial is the only one in the group we can load it, too
        # -> will search in group for PolyIsing, PolyBinary or Polynomial
        group = h5file["without_name"]
        poly = read_poly_with_type(group)
        assert isinstance(poly, PolyBinary)
        assert poly == POLY_BINARY

        group = h5file["empty_group"]
        message = "Found no Polynomials in group '/empty_group'"
        with pytest.raises(ValueError, match=message):
            # there no Polynomials in this group
            read_poly_with_type(group)
