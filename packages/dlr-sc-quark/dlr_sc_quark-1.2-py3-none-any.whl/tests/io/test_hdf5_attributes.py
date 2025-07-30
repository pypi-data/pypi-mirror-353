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

""" module for testing the IO of attributes in HDF5 files """

import os
import pytest
import numpy as np
import h5py

from quark.io import hdf5_attributes


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"
FILE = "attributes.h5"
FILENAME_TMP = TEST_DIR + FILE
FILENAME_FIX = TEST_DIR + "testdata/" + FILE
GROUP_NAME = "testgroup_attributes"

ATTRS = {"a1_int":   1,
         "a2_str":   "two",
         "a3_bool":  True,
         "a4_list":  [1, 2],
         "a5_tuple": (1, 2),
         "a6_set":   {1, 2},
         "a7_None":  None}

class ExampleObject:
    """ some test object with data """

    def __init__(self):
        self.a1_int = 1
        self.a2_str = "two"
        self.a3_bool = True
        self.a4_list = [1, 2]
        self.a5_tuple = (1, 2)
        self.a6_set = {1, 2}


def test_write_attributes_dict():
    """ test write_attribute function with dictionary of names and values """
    with h5py.File(FILENAME_TMP, "w") as h5file:
        group = h5file.create_group(GROUP_NAME)
        hdf5_attributes.write_attributes(group, a0_float=1.4, **ATTRS)

        with pytest.raises(ValueError, match="Given value does not have an easy data structure, create dataset instead"):
            hdf5_attributes.write_attributes(group, a10_invalid=[(1, 3), (3, 4)])

        with pytest.raises(ValueError, match="Given value does not have an easy data structure, create dataset instead"):
            hdf5_attributes.write_attributes(group, a10_invalid={1 : 3})

    _check_and_remove_file()

def test_write_attributes_obj():
    """ test write_attribute function with provided object """
    example_object = ExampleObject()

    with h5py.File(FILENAME_TMP, "w") as h5file:
        group = h5file.create_group(GROUP_NAME)
        # for testing overwrite
        hdf5_attributes.write_attribute(group, "a1_int", value=2)
        # tests taking the attributes from the object and additionally the keyword plus its value
        hdf5_attributes.write_attributes(group, example_object, *ATTRS.keys(), a0_float=1.4)
        # test to store an attribute that the object does not have (results in storing None)
        hdf5_attributes.write_attribute(group, "a7_None", example_object)

    _check_and_remove_file()

def test_read_attributes():
    """ test write_attribute function """
    with h5py.File(FILENAME_FIX, "r") as h5file:
        group = h5file[GROUP_NAME]

        loaded_attr = hdf5_attributes.read_attributes(group, *ATTRS.keys())
        assert loaded_attr["a1_int"] == 1
        assert loaded_attr["a2_str"] == "two"
        assert loaded_attr["a3_bool"]
        assert list(loaded_attr["a4_list"]) == [1, 2]
        assert tuple(loaded_attr["a5_tuple"]) == (1, 2)
        assert set(loaded_attr["a6_set"]) == {1, 2}
        assert loaded_attr["a7_None"] is None

        not_existing_no_check = hdf5_attributes.read_attributes(group, "a10_whatever", check_existence=False)
        assert not_existing_no_check["a10_whatever"] is None

        with pytest.raises(ValueError, match="Did not find attribute 'a10_whatever' at group '/" + GROUP_NAME):
            hdf5_attributes.read_attributes(group, "a10_whatever")


def _check_and_remove_file():
    with h5py.File(FILENAME_TMP, "r") as h5file:
        group = h5file[GROUP_NAME]

        for name in ATTRS.keys():
            assert name in group.attrs
        assert "a0_float" in group.attrs

        assert group.attrs["a1_int"] == 1
        assert group.attrs["a2_str"].decode() == "two"
        assert group.attrs["a3_bool"]
        assert list(group.attrs["a4_list"]) == [1, 2]
        assert tuple(group.attrs["a5_tuple"]) == (1, 2)
        assert set(group.attrs["a6_set"]) == {1, 2}
        assert np.isnan(group.attrs["a7_None"])
        assert group.attrs["a0_float"] == 1.4

    os.remove(FILENAME_TMP)
