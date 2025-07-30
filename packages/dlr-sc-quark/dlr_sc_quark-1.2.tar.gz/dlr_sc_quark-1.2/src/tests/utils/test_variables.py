# Copyright 2022 DLR-SC
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

""" module for testing the variable utility functions """

import pytest

from quark import PolyIsing
from quark.utils.variables import get_common_type, get_type, check_type_against, are_consecutive, to_string, \
                                  replace_strs_by_ints, to_domain_string


def test_get_common_type():
    """ test finding the type of all variables """
    assert get_common_type([]) is None
    assert get_common_type(["x", "y"]) is str

    with pytest.raises(TypeError, match="Expected variable type 'tuple', but got 'str'"):
        get_common_type([(1, 4), "x"])

def test_get_type():
    """ test finding the type """
    assert get_type(("x", 1)) is tuple

    with pytest.raises(TypeError, match="Variable 'True' has invalid type 'bool'"):
        get_type(True)

    with pytest.raises(ValueError, match="should only contain ints and strings"):
        get_type(("x", 1.4))

def test_check_type_against():
    """ test check whether type is the expected one """
    with pytest.raises(TypeError, match="Expected variable type 'tuple', but got 'str'"):
        check_type_against("x", tuple)

def test_are_consecutive():
    """ test checking of consecutive variables """
    assert are_consecutive([0, 1, 2, 3])
    assert are_consecutive([1, 0, 1, 2, 3])
    assert not are_consecutive([1, 2, 3])
    assert not are_consecutive([1, 0, 4, 0])
    assert not are_consecutive([(0,), (1,), (2,), (3,)])
    assert not are_consecutive([(0,), "x"])

def test_to_string():
    """ test string creation """
    assert to_string(("s", 1, 2)) == "s_1_2"
    assert to_string((1, 2)) == "x_1_2"
    assert to_string(1) == "x1"
    assert to_string(1, PolyIsing) == "s1"

def test_to_domain_string():
    """ test string creation """
    assert to_domain_string(("s", 1, 2)) == "s_*_* in {0, 1}"
    assert to_domain_string((1, 2)) == "x_*_* in {0, 1}"
    assert to_domain_string(1) == "x* in {0, 1}"
    assert to_domain_string((1, 2), "PolyIsing") == "s_*_* in {-1, 1}"
    assert to_domain_string(1, PolyIsing) == "s* in {-1, 1}"

def test_replace_strs_by_ints():
    """ test replacement of string parts """
    expected_tuples = [(4, 5, 1), (6, 2, 3)]
    expected_int_to_str = {4 : "x", 5 : "y", 6 : "z"}
    tuples, int_to_str = replace_strs_by_ints([("x", "y", 1), ("z", 2, 3)])
    assert tuples == expected_tuples
    assert int_to_str == expected_int_to_str
