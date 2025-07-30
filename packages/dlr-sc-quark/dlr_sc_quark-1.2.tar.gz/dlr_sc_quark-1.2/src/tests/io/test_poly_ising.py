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

""" module for testing the IO of the PolyIsing """

import os
import pytest

from quark import PolyIsing
from quark.io import hdf5, txt


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"
FILE_H5 = "poly_ising.h5"
FILE_TXT = "poly_ising.txt"
FILENAME_H5_TMP = TEST_DIR + FILE_H5
FILENAME_TXT_TMP = TEST_DIR + FILE_TXT
FILENAME_H5_FIX = TEST_DIR + "testdata/" + FILE_H5
FILENAME_TXT_FIX = TEST_DIR + "testdata/" + FILE_TXT

POLY_FIX = PolyIsing({(("x", 1),): 2.5, (("x", 2), ("y", 0, 0)): 2.0, (): 5.5})
POLYS = [PolyIsing({(1,): 5, (2,): 6, (3, 1): 3, (2, 4): 3, (4,): 1, (): 3}),
         PolyIsing({(2,): 1, (2, 4): 1, (3, 4): 3, (5,): 7}, inverted=True),
         PolyIsing({(1,): 7, (2,): 2, (3,): 3, (4,): 1}),
         PolyIsing({}, inverted=True),
         PolyIsing({(): 55}),
         PolyIsing({(): 55, (1,): 66}, inverted=True),
         PolyIsing({(): 55, (1,): 66, (1, 2): 77}),
         PolyIsing({(1,): 66, (1, 2): 77}, inverted=True),
         PolyIsing({(1,): 1.5, (2,): 2.5}),
         PolyIsing({((1,),): 1.0, ((1, 2),): 2.0, ((1, 2), (1, 2), (1, 3)): 2.0, (): 5.5}, inverted=True),
         POLY_FIX]


def test_load():
    """ test hdf5 io """
    loaded = hdf5.load(PolyIsing, FILENAME_H5_FIX)
    assert loaded == POLY_FIX

    loaded = txt.load(PolyIsing, FILENAME_TXT_FIX)
    assert loaded == POLY_FIX

@pytest.mark.parametrize("poly", POLYS)
def test_io(poly):
    """ test hdf5 io round trip """
    hdf5.save(poly, FILENAME_H5_TMP)
    loaded = hdf5.load(PolyIsing, FILENAME_H5_TMP)
    assert loaded == poly
    assert loaded.is_inverted() == poly.is_inverted()
    os.remove(FILENAME_H5_TMP)

    txt.save(poly, FILENAME_TXT_TMP)
    loaded = txt.load(PolyIsing, FILENAME_TXT_TMP)
    assert loaded == poly
    assert loaded.is_inverted() == poly.is_inverted()
    os.remove(FILENAME_TXT_TMP)
