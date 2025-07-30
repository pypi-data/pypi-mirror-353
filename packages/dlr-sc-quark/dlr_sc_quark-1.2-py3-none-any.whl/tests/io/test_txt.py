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

""" module for testing the IO with txt files """

import os
import pytest

from quark import Polynomial
from quark.io import txt


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"
FILE = "polynomial.txt"
FILENAME_TMP = TEST_DIR + FILE
FILENAME_FIX = TEST_DIR + "testdata/" + FILE

POLY = Polynomial({(): 5.5, (("x", 1),): 2.5, (("x", 2), ("y", 0, 0)): 2.0})


def test_save():
    """ testing if the polynomial is correctly saved to the file """
    txt.save(POLY, FILENAME_TMP)
    with open(FILENAME_TMP) as txt_file:
        loaded_lines = txt_file.readlines()
    expected_lines = ["Polynomial\n", "{(): 5.5,\n", " (('x', 1),): 2.5,\n", " (('x', 2),\n", " ('y', 0, 0)): 2.0}\n"]
    assert loaded_lines == expected_lines
    os.remove(FILENAME_TMP)

def test_load():
    """ testing if the polynomial is correctly loaded from the file """
    loaded_poly = txt.load(Polynomial, FILENAME_FIX)
    assert loaded_poly == POLY

def test_exists():
    """ testing if the polynomial is correctly found in the file """
    wrong_filename = TEST_DIR + "testdata/poly_ising.txt"
    assert txt.exists(Polynomial, FILENAME_FIX)
    assert not txt.exists(Polynomial, wrong_filename)

def test_save_load_several():
    """ testing the loading and saving of several polynomials in one file """
    poly1 = Polynomial({(1, 2, 3): 100})
    poly2 = Polynomial({(1, 2): 1, (2, 3): 2, (3, 4): 3})

    txt.save(POLY, FILENAME_TMP)
    txt.save(poly1, FILENAME_TMP, "a")
    txt.save(poly2, FILENAME_TMP, "a")

    with open(FILENAME_TMP) as txt_file:
        loaded_lines = txt_file.readlines()

    exp_lines = ["Polynomial\n", "{(): 5.5,\n", " (('x', 1),): 2.5,\n", " (('x', 2),\n", " ('y', 0, 0)): 2.0}\n", "\n",
                 "Polynomial\n", "{(1, 2, 3): 100}\n", "\n",
                 "Polynomial\n", "{(1, 2): 1,\n", " (2, 3): 2,\n", " (3, 4): 3}\n"]
    assert loaded_lines == exp_lines

    loaded_poly0 = txt.load(Polynomial, FILENAME_TMP)
    loaded_poly1 = txt.load(Polynomial, FILENAME_TMP, index=1)
    loaded_poly2 = txt.load(Polynomial, FILENAME_TMP, index=2)

    assert loaded_poly0 == POLY
    assert loaded_poly1 == poly1
    assert loaded_poly2 == poly2

    with pytest.raises(ValueError, match="The file does not contain so much objects of type 'Polynomial'"):
        txt.load(Polynomial, FILENAME_TMP, index=3)

    with pytest.raises(ValueError, match="The file does not contain any object of type 'Polynomial'"):
        wrong_filename = TEST_DIR + "testdata/poly_ising.txt"
        txt.load(Polynomial, wrong_filename)

    os.remove(FILENAME_TMP)
