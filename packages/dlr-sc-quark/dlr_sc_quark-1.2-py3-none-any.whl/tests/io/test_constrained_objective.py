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

""" module for testing the IO of the ObjectiveTerms """

import os
import pytest

from quark import PolyBinary, ConstraintBinary, ConstrainedObjective
from quark.io import hdf5
from quark.testing import ExampleConstrainedObjective


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"
FILE = "constrained_objective.h5"
FILENAME_TMP = TEST_DIR + FILE
FILENAME_FIX = TEST_DIR + "testdata/"+ FILE


def test_load_hdf5(constrained_objective):
    """ test hdf5 io """
    loaded = hdf5.load(ExampleConstrainedObjective, FILENAME_FIX)
    assert loaded == constrained_objective

def test_io_hdf5(constrained_objective):
    """ test hdf5 io round trip """
    hdf5.save(constrained_objective, FILENAME_TMP)
    loaded = hdf5.load(ExampleConstrainedObjective, FILENAME_TMP)
    assert loaded == constrained_objective
    os.remove(FILENAME_TMP)


@pytest.fixture
def constrained_objective_no_impl():
    """ provide the ConstrainedObjective test object directly using the base class """
    objective_poly = PolyBinary.read_from_string("5 + x0 x1 + x1 x2 + x2 x3 + x0 x3 + x0 x2")
    constraint = ConstraintBinary(PolyBinary.read_from_string("x0 + x1 + x2"), 1, 1)
    constrained_objective = ConstrainedObjective(objective_poly, {"favour_one" : constraint})
    yield constrained_objective

def test_load_hdf5_no_impl(constrained_objective_no_impl):
    """ test hdf5 io """
    loaded = hdf5.load(ConstrainedObjective, FILENAME_FIX)
    assert loaded == constrained_objective_no_impl

def test_io_hdf5_no_impl(constrained_objective_no_impl):
    """ test hdf5 io round trip """
    hdf5.save(constrained_objective_no_impl, FILENAME_TMP)
    loaded = hdf5.load(ConstrainedObjective, FILENAME_TMP)
    assert loaded == constrained_objective_no_impl
    os.remove(FILENAME_TMP)

