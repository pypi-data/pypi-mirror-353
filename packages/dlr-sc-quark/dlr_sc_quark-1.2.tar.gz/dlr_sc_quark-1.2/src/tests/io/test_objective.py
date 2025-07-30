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

""" module for testing the IO of the Objective """

import os
import pytest

from quark import PolyIsing, Objective
from quark.io import hdf5
from quark.testing import ExampleObjective


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"
FILE = "objective.h5"
FILENAME_TMP = TEST_DIR + FILE
FILENAME_FIX = TEST_DIR + "testdata/" + FILE

NAME = "test_objective"
CONSTRUCTED_NAME = 'colored_edges1.000000e+00_one_color_per_node7.000000e+00'


def test_load_hdf5(objective, objective_direct_impl):
    """ test hdf5 io """
    loaded = hdf5.load(Objective, FILENAME_FIX, name=CONSTRUCTED_NAME)
    assert loaded == objective

    loaded = hdf5.load(ExampleObjective, FILENAME_FIX)
    assert loaded == objective_direct_impl

def test_io_hdf5(objective, objective_direct_impl):
    """ test hdf5 io round trip """
    hdf5.save(objective, FILENAME_TMP)
    loaded = hdf5.load(Objective, FILENAME_TMP, name=objective.name)
    assert loaded == objective

    hdf5.save(objective_direct_impl, FILENAME_TMP)
    loaded = hdf5.load(ExampleObjective, FILENAME_TMP)
    assert loaded == objective_direct_impl

    os.remove(FILENAME_TMP)


@pytest.fixture
def objective_no_impl():
    """ provide the Objective test object built upon an example implementation inheriting from the base class """
    poly = PolyIsing({(("y", 2, 3), ("x", 1)): 2, (("y", 1, 2),): 3}, inverted=True)
    objective = Objective(poly, NAME)
    yield objective

def test_load_hdf5_no_impl(objective_no_impl):
    """ test hdf5 io """
    loaded = hdf5.load(Objective, FILENAME_FIX, name=NAME)
    assert loaded == objective_no_impl

def test_io_hdf5_no_impl(objective_no_impl):
    """ test hdf5 io round trip """
    hdf5.save(objective_no_impl, FILENAME_TMP)
    loaded = hdf5.load(Objective, FILENAME_TMP, name=objective_no_impl.name)
    assert loaded == objective_no_impl
    os.remove(FILENAME_TMP)
