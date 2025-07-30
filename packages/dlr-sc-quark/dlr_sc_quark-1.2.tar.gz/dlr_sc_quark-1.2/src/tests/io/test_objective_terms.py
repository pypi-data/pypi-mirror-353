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

from quark import PolyBinary, ObjectiveTerms
from quark.io import hdf5
from quark.testing import ExampleObjectiveTerms


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"
FILE = "objective_terms.h5"
FILENAME_TMP = TEST_DIR + FILE
FILENAME_FIX = TEST_DIR + "testdata/" + FILE


def test_load_hdf5(objective_terms, objective_terms_direct_impl):
    """ test hdf5 io """
    loaded = hdf5.load(ObjectiveTerms, FILENAME_FIX)
    assert loaded == objective_terms

    loaded = hdf5.load(ExampleObjectiveTerms, FILENAME_FIX)
    assert loaded == objective_terms_direct_impl

def test_io_hdf5(objective_terms, objective_terms_direct_impl):
    """ test hdf5 io round trip """
    hdf5.save(objective_terms, FILENAME_TMP)
    loaded = hdf5.load(ObjectiveTerms, FILENAME_TMP)
    assert loaded == objective_terms

    hdf5.save(objective_terms_direct_impl, FILENAME_TMP)
    loaded = hdf5.load(ExampleObjectiveTerms, FILENAME_TMP)
    assert loaded == objective_terms

    os.remove(FILENAME_TMP)


@pytest.fixture
def objective_terms_no_impl():
    """ provide the ObjectiveTerms test object directly using the base class """
    objective = PolyBinary.read_from_string("5 + x0 x1 + x1 x2 + x2 x3 + x0 x3 + x0 x2")
    constraint = PolyBinary.read_from_string("1 - x0")
    ot_dict = dict(objective=objective, constraint=constraint)
    objective_terms = ObjectiveTerms(ot_dict, ["constraint"], name="test_objective_terms")
    yield objective_terms

def test_load_hdf5_no_impl(objective_terms_no_impl):
    """ test hdf5 io """
    loaded = hdf5.load(ObjectiveTerms, FILENAME_FIX, name="test_objective_terms", prefix_group_name="elsewhere")
    assert loaded == objective_terms_no_impl

def test_io_hdf5_no_impl(objective_terms_no_impl):
    """ test hdf5 io round trip """
    hdf5.save(objective_terms_no_impl, FILENAME_TMP, prefix_group_name="elsewhere")
    loaded = hdf5.load(ObjectiveTerms, FILENAME_TMP, name="test_objective_terms", prefix_group_name="elsewhere")
    assert loaded == objective_terms_no_impl

    os.remove(FILENAME_TMP)
