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

""" module for testing the IO of the Polynomial """

import os
import pytest

from quark import Polynomial
from quark.io import hdf5, txt


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"
FILE_H5 = "polynomial.h5"
FILE_TXT = "polynomial.txt"
FILENAME_H5_TMP = TEST_DIR + FILE_H5
FILENAME_TXT_TMP = TEST_DIR + FILE_TXT
FILENAME_H5_FIX = TEST_DIR + "testdata/" + FILE_H5
FILENAME_TXT_FIX = TEST_DIR + "testdata/" + FILE_TXT

POLY_FIX = Polynomial({(("x", 1),): 2.5, (("x", 2), ("y", 0, 0)): 2.0, (): 5.5})
POLYS = [Polynomial({(1,): 5, (2,): 6, (3, 1): 3, (2, 4): 3, (4,): 1, (): 3}),
         Polynomial({(2,): 1, (2, 4): 1, (3, 4): 3, (5,): 7}),
         Polynomial({(1,): 7, (2,): 2, (3,): 3, (4,): 1}),
         Polynomial({}),
         Polynomial({(): 55}),
         Polynomial({(): 55, (1,): 66}),
         Polynomial({(): 55, (1,): 66, (1, 2): 77}),
         Polynomial({(1,): 66, (1, 2): 77}),
         Polynomial({(1,): 1.5, (2,): 2.5}),
         Polynomial({((1,),): 1.0, ((1, 2),): 2.0, ((1, 2), (1, 2), (1, 3)): 2.0, (): 5.5}),
         POLY_FIX]


def test_load():
    """ test hdf5 io """
    loaded = hdf5.load(Polynomial, FILENAME_H5_FIX)
    assert loaded == POLY_FIX

    loaded = txt.load(Polynomial, FILENAME_TXT_FIX)
    assert loaded == POLY_FIX

@pytest.mark.parametrize("poly", POLYS)
def test_io(poly):
    """ test hdf5 io round trip """
    hdf5.save(poly, FILENAME_H5_TMP)
    loaded = hdf5.load(Polynomial, FILENAME_H5_TMP)
    assert loaded == poly

    txt.save(poly, FILENAME_TXT_TMP)
    loaded = txt.load(Polynomial, FILENAME_TXT_TMP)
    assert loaded == poly

    if poly.is_flat():
        str_poly = str(poly)
        loaded = Polynomial.read_from_string(str_poly)
    assert loaded == poly

    os.remove(FILENAME_H5_TMP)
    os.remove(FILENAME_TXT_TMP)

@pytest.mark.parametrize("poly", POLYS)
def test_io_methods(poly):
    """ test hdf5 io round trip """
    poly.save_hdf5(FILENAME_H5_TMP)
    loaded = Polynomial.load_hdf5(FILENAME_H5_TMP)
    assert loaded == poly

    poly.save_txt(FILENAME_TXT_TMP)
    loaded = Polynomial.load_txt(FILENAME_TXT_TMP)
    assert loaded == poly

    os.remove(FILENAME_H5_TMP)
    os.remove(FILENAME_TXT_TMP)

def test_existence_save_load():
    assert hasattr(Polynomial, "save_hdf5")
    assert hasattr(Polynomial, "load_hdf5")
    assert hasattr(Polynomial, "exists_hdf5")
    assert hasattr(Polynomial, "save_txt")
    assert hasattr(Polynomial, "load_txt")
    assert hasattr(Polynomial, "exists_txt")
