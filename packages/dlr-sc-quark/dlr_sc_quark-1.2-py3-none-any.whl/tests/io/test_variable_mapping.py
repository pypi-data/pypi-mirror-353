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

""" module for testing the IO of the VariableMapping """

import os
import pytest

from quark import VariableMapping
from quark.io import hdf5


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"
FILE = "variable_mapping.h5"
FILENAME_TMP = TEST_DIR + FILE
FILENAME_FIX = TEST_DIR + "testdata/" + FILE


@pytest.fixture
def variable_mappings():
    """ provide the test objects """
    vm_wild = VariableMapping({("s", 0): ("x", 1), ("s", 1): ("x", 2), ("s", 2): ("y", 0, 0)})
    vm_consecutive = VariableMapping({0: ("x", 1), 1: ("x", 2), 2: ("y", 0, 0)})
    yield vm_wild, vm_consecutive, vm_consecutive.inverse

def test_load_hdf5(variable_mappings):
    """ test hdf5 io """
    for i, var_mapping in enumerate(variable_mappings):
        loaded = hdf5.load(VariableMapping, FILENAME_FIX, prefix_group_name=str(i))
        assert loaded == var_mapping

def test_io_hdf5(variable_mappings):
    """ test hdf5 io round trip """
    for var_mapping in variable_mappings:
        hdf5.save(var_mapping, FILENAME_TMP)
        loaded = hdf5.load(VariableMapping, FILENAME_TMP)
        assert loaded == var_mapping
        os.remove(FILENAME_TMP)
