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

""" module for testing the IO of the Instance """

import os
from abc import ABC
import pytest

from quark.io import hdf5, Instance
from quark.testing import ExampleInstance


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"
FILE = "instance.h5"
FILENAME_TMP = TEST_DIR + FILE
FILENAME_FIX = TEST_DIR + "testdata/" + FILE


def test_consistency(instance):
    """ test consistency checks """
    with pytest.raises(ValueError, match="Instance is not consistent: No edges given"):
        ExampleInstance([], len(instance.colors))
    with pytest.raises(ValueError, match="Instance is not consistent: No colors given"):
        ExampleInstance(instance.edges, 0)
    with pytest.raises(ValueError, match="Instance is not consistent: Edges need to have two nodes"):
        ExampleInstance([(), (), ()], len(instance.colors))

def test_get_name(instance):
    """ test instance name """
    assert instance.get_name() == "ExampleInstance_density_0.7_colors_3"

def test_io_hdf5(instance):
    """ test hdf5 io round trip """
    hdf5.save(instance, FILENAME_TMP)
    assert hdf5.exists(ExampleInstance, FILENAME_TMP)
    loaded = hdf5.load(ExampleInstance, FILENAME_TMP)
    assert loaded.edges == instance.edges
    assert loaded.colors == instance.colors
    os.remove(FILENAME_TMP)

    instance.save_hdf5(FILENAME_TMP)
    assert ExampleInstance.exists_hdf5(FILENAME_TMP)
    loaded = ExampleInstance.load_hdf5(FILENAME_TMP)
    assert loaded.edges == instance.edges
    assert loaded.colors == instance.colors
    os.remove(FILENAME_TMP)

def test_load_hdf5(instance):
    """ test hdf5 io """
    assert hdf5.exists(ExampleInstance, FILENAME_FIX)
    loaded = hdf5.load(ExampleInstance, FILENAME_FIX)
    assert loaded.edges == instance.edges
    assert loaded.colors == instance.colors

    assert ExampleInstance.exists_hdf5(FILENAME_FIX)
    loaded = ExampleInstance.load_hdf5(FILENAME_FIX)
    assert loaded.edges == instance.edges
    assert loaded.colors == instance.colors

class ExampleInstanceWithoutIO(Instance, ABC):
    """ some test instance """
    def check_consistency(self):
        """ test if instance is consistent """
        return True

def test_not_implemented():
    """ test not implemented methods """
    with pytest.raises(NotImplementedError):
        Instance().check_consistency()
    with pytest.raises(NotImplementedError):
        ExampleInstanceWithoutIO().get_name()
    with pytest.raises(NotImplementedError):
        Instance.read_hdf5(FILENAME_FIX)
    with pytest.raises(NotImplementedError):
        ExampleInstanceWithoutIO().write_hdf5(FILENAME_FIX)

    # pylint: disable=protected-access
    with pytest.raises(NotImplementedError):
        ExampleInstanceWithoutIO().get_constrained_objective()
    with pytest.raises(NotImplementedError):
        ExampleInstanceWithoutIO().get_objective_terms()
    with pytest.raises(NotImplementedError):
        ExampleInstanceWithoutIO().get_objective()
