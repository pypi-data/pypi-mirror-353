# Copyright 2024 DLR-SC
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

""" module for testing the IO of the PolyBinary """

import os
import pytest

from quark import PolyBinary
from quark.io import hdf5, txt


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"
FILE_H5 = "poly_binary.h5"
FILE_TXT = "poly_binary.txt"
FILE_BP = "poly_binary.bp"
FILE_BP_LARGE = "ising2.5-100_5555.bq"
FILENAME_H5_TMP = TEST_DIR + FILE_H5
FILENAME_TXT_TMP = TEST_DIR + FILE_TXT
FILENAME_BP_TMP = TEST_DIR + FILE_BP
FILENAME_H5_FIX = TEST_DIR + "testdata/" + FILE_H5
FILENAME_TXT_FIX = TEST_DIR + "testdata/" + FILE_TXT
FILENAME_BP_FIX = TEST_DIR + "testdata/" + FILE_BP
FILENAME_BP_LARGE_FIX = TEST_DIR + "testdata/" + FILE_BP_LARGE

POLY_FIX = PolyBinary({(("x", 1),): 2.5, (("x", 2), ("y", 0, 0)): 2.0, (): 5.5})
POLYS = [PolyBinary({(1,): 5, (2,): 6, (3, 1): 3, (2, 4): 3, (4,): 1}),
         PolyBinary({(2,): 1, (2, 4): 1, (3, 4): 3, (5,): 7}),
         PolyBinary({(1,): 7, (2,): 2, (3,): 3, (4,): 1}),
         PolyBinary({(1,): 66, (1, 2): 77}),
         PolyBinary({(1,): 1.5, (2,): 2.5})]

POLYS_NOT = [PolyBinary({((1,),): 1.0, ((1, 2),): 2.0, ((1, 2), (1, 2), (1, 3)): 2.0, (): 5.5}),
             PolyBinary({}),
             PolyBinary({(): 55}),
             PolyBinary({(): 55, (1,): 66}),
             PolyBinary({(): 55, (1,): 66, (1, 2): 77})]

def test_load():
    """ test io """
    loaded = hdf5.load(PolyBinary, FILENAME_H5_FIX)
    assert loaded == POLY_FIX

    loaded = txt.load(PolyBinary, FILENAME_TXT_FIX)
    assert loaded == POLY_FIX

    loaded = PolyBinary.load_bp(FILENAME_BP_FIX)
    assert loaded == POLYS[0]

@pytest.mark.parametrize("poly", POLYS + POLYS_NOT)
def test_io(poly):
    """ test io round trip """
    hdf5.save(poly, FILENAME_H5_TMP)
    loaded = hdf5.load(PolyBinary, FILENAME_H5_TMP)
    assert loaded == poly
    os.remove(FILENAME_H5_TMP)

    txt.save(poly, FILENAME_TXT_TMP)
    loaded = txt.load(PolyBinary, FILENAME_TXT_TMP)
    assert loaded == poly
    os.remove(FILENAME_TXT_TMP)

@pytest.mark.parametrize("poly", POLYS)
def test_io_bp(poly):
    """ test io round trip """
    assert not PolyBinary.exists_bp(FILENAME_BP_TMP)
    poly.save_bp(FILENAME_BP_TMP)
    assert PolyBinary.exists_bp(FILENAME_BP_TMP)

    loaded = PolyBinary.load_bp(FILENAME_BP_TMP)
    assert loaded == poly
    os.remove(FILENAME_BP_TMP)

def test_io_bp_not():
    """ test io failure """
    for poly in POLYS_NOT[:3]:
        with pytest.raises(ValueError, match="Can only write"):
            poly.save_bp(FILENAME_BP_TMP)
    for poly in POLYS_NOT[3:]:
        with pytest.warns(UserWarning, match="Offset will be ignored"):
            poly.save_bp(FILENAME_BP_TMP)
    os.remove(FILENAME_BP_TMP)

def test_io_bp_large():
    """ test large instance """
    loaded = PolyBinary.load_bp(FILENAME_BP_LARGE_FIX)
    assert loaded.get_variable_num() == 100
    assert len(loaded) == 4981
    assert loaded.get_coefficient(47, 55) == -1086

def test_bp_exist():
    """ test existence """
    with open("empty_file.txt", mode="w"):
        pass
    assert not PolyBinary.exists_bp("empty_file.txt")
    os.remove("empty_file.txt")

    with open("wrong_format.txt", mode="w", encoding="utf-8") as wrong_format_file:
        # get the corresponding function for writing and call it
        wrong_format_file.write(f"1 1")  # wrong format -> no variables
    assert not PolyBinary.exists_bp("wrong_format.txt")
    os.remove("wrong_format.txt")

    with open("wrong_format.txt", mode="w", encoding="utf-8") as wrong_format_file:
        # get the corresponding function for writing and call it
        wrong_format_file.write(f"1 1 1")  # wrong format -> header is not set
    assert not PolyBinary.exists_bp("wrong_format.txt")
    os.remove("wrong_format.txt")
