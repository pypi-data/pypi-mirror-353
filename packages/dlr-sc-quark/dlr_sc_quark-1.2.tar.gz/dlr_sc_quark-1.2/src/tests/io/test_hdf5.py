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

""" module for testing the IO with HDF5 files """

import os
import pytest
import numpy as np
import h5py

from quark.io import hdf5, hdf5_datasets


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"
FILE = "example_object.h5"
FILENAME_TMP = TEST_DIR + FILE
FILENAME_FIX = TEST_DIR + "testdata/" + FILE

NAME = "example_object"
VALUE = 99
DATA = {"z" : 1.0, "y" : 2.5, "x" : 4.0}

PREFIX = "Prefix"
EXAMPLE_OBJECT = "ExampleObject"
HALF_GROUP_NAME = "ExampleObject/example_object"
FULL_GROUP_NAME_99 = "ExampleObject/example_object/99"


class ExampleObject:
    """ an object with an io implementation """

    def __init__(self, data=None, name=None, value=None):
        self.data = data
        self.name = name
        self.value = value

    @staticmethod
    def get_identifying_attributes():
        """ identifying attributes """
        return ["name", "value"]

    def write_hdf5(self, group):
        """ necessary write method for io """
        hdf5_datasets.write_dataset(group, "data", self)

    @staticmethod
    def read_hdf5(group):
        """ necessary read method for io """
        data = hdf5_datasets.read_dataset(group, "data")
        return dict(data=data)

class ExampleObjectWrongIO:
    """ an object with an io implementation """

    def __init__(self, name, data, value=None):
        self.data = data
        self.name = name
        self.value = value

    @staticmethod
    def get_identifying_attributes():
        """ identifying attributes """
        return ["name", "value"]

    @staticmethod
    def read_hdf5(group):
        """ necessary read method for io """
        return dict()

class ExampleObjectWithoutIO:
    """ a different object without an io implementation """

    def __init__(self):
        pass

class TwoLevelExampleObject:
    """ a new object with an io implementation but calling ExampleObjectWithoutIO's non-existing io directly """

    def __init__(self):
        self.obj = ExampleObjectWithoutIO()

    def write_hdf5(self, group):
        """ necessary write method for io """
        hdf5.save_in(self.obj, group)

    @staticmethod
    def read_hdf5(group):
        """ necessary read method for io """
        return hdf5.load_data_from(ExampleObjectWithoutIO, group)

class InheritingExampleObject(ExampleObjectWithoutIO):
    """ a new object with an io implementation but calling ExampleObjectWithoutIO's non-existing io by inheritance """

    def write_hdf5(self, group):
        """ necessary write method for io """
        hdf5.save_in(super(), group)

    @staticmethod
    def read_hdf5(group):
        """ necessary read method for io """
        return hdf5.load_data_from(super(InheritingExampleObject, InheritingExampleObject), group)

@pytest.fixture
def example_object():
    """ provide test object of example class """
    yield ExampleObject(DATA, NAME, VALUE)


def test_exists():
    """ test exist method """
    # check for full identifying attributes - ExampleObject/example_object/99 exists
    assert hdf5.exists(ExampleObject, FILENAME_FIX, name=NAME, value=VALUE)

    # check for only name as identifying attributes - ExampleObject/example_object exists
    assert hdf5.exists(ExampleObject, FILENAME_FIX, name=NAME)

    # check for only value as identifying attributes - ExampleObject/99 does not exist (name inbetween missing)
    assert not hdf5.exists(ExampleObject, FILENAME_FIX, value=VALUE)

    # check for some group name - ExampleObject/example_object exists
    assert hdf5.exists(ExampleObject, FILENAME_FIX, full_group_name=HALF_GROUP_NAME)

    # check for full group name - ExampleObject/example_object/99 exists
    assert hdf5.exists(ExampleObject, FILENAME_FIX, full_group_name=FULL_GROUP_NAME_99)

    # check for full group name - ExampleObject/example_object/100 does not exist
    assert not hdf5.exists(ExampleObject, FILENAME_FIX, full_group_name=HALF_GROUP_NAME + "/100")

    # check for file - does not exist
    assert not hdf5.exists(ExampleObject, "testdata/no_object.h5", name=NAME)

    # check for prefixed versions - do exist
    assert hdf5.exists(ExampleObject, FILENAME_FIX, prefix_group_name=PREFIX, name=NAME, value=VALUE)
    assert hdf5.exists(ExampleObject, FILENAME_FIX, full_group_name=PREFIX + "/" + FULL_GROUP_NAME_99)

    # check for option clash
    with pytest.raises(ValueError, match="Either provide prefix for default group name or full group name"):
        assert hdf5.exists(ExampleObject, FILENAME_FIX, prefix_group_name=PREFIX, full_group_name=FULL_GROUP_NAME_99)

def test_save(example_object):
    """ test if the object is saved correctly, where we will use here ExampleObject exemplary """
    hdf5.save(example_object, FILENAME_TMP)
    # check if the expected groups are in the file
    with h5py.File(FILENAME_TMP, "r") as h5file:
        subgroup = _check_structure_get_data_group(h5file)
        assert "keys" in subgroup
        assert "values" in subgroup
        assert np.array_equal(subgroup["keys"][()], [b"z", b"y", b"x"])
        assert np.array_equal(subgroup["values"][()], [1.0, 2.5, 4.0])

    # creating new ExampleObject with different Polynomial but same name
    new_data = {"c": 2, "a": 3, "b": 4}
    new_obj = ExampleObject(new_data, NAME, VALUE)

    message = f"Group 'ExampleObject/example_object/99' already existed in file '.*{FILE}' and got deleted"
    with pytest.warns(UserWarning, match=message):
        hdf5.save(new_obj, FILENAME_TMP, mode="a")
    # should have overwritten the old ExampleObject in the file
    with h5py.File(FILENAME_TMP, "r") as h5file:
        subgroup = _check_structure_get_data_group(h5file)
        assert np.array_equal(subgroup["keys"][()], [b"c", b"a", b"b"])
        assert np.array_equal(subgroup["values"][()], [2, 3, 4])

    # creating new ExampleObject with different value
    new_value = 100
    new_obj = ExampleObject(DATA, NAME, new_value)
    hdf5.save(new_obj, FILENAME_TMP)
    # now there should be two ExampleObjects in the file
    with h5py.File(FILENAME_TMP, "r") as h5file:
        assert EXAMPLE_OBJECT in h5file
        group = h5file[EXAMPLE_OBJECT][NAME]
        assert str(VALUE) in group
        assert str(new_value) in group

    hdf5.save(new_obj, FILENAME_TMP, full_group_name="Elsewhere/different", mode="a")
    with h5py.File(FILENAME_TMP, "r") as h5file:
        assert "Elsewhere" in h5file
        group = h5file["Elsewhere"]["different"]
        assert "data" in group

    with pytest.raises(ValueError, match="Either provide prefix for default group name or full group name"):
        assert hdf5.save(ExampleObject, FILENAME_TMP, prefix_group_name=PREFIX, full_group_name=FULL_GROUP_NAME_99)

    with pytest.raises(ValueError, match="Object of type 'ExampleObjectWrongIO' does not have a write_hdf5 method"):
        hdf5.save(ExampleObjectWrongIO("name", 1), FILENAME_TMP)

    os.remove(FILENAME_TMP)

def _check_structure_get_data_group(h5file):
    assert EXAMPLE_OBJECT in h5file
    group = h5file[EXAMPLE_OBJECT]
    assert NAME in group
    subgroup = group[NAME]
    assert str(VALUE) in subgroup
    subgroup = subgroup[str(VALUE)]
    assert "data" in subgroup
    subgroup = subgroup["data"]
    return subgroup

def test_save_without_all_identifying_attributes():
    """
    testing if the object is saved correctly
    we will use here ExampleObject exemplary
    """
    # with name but without value
    example_object = ExampleObject(DATA, name=NAME)
    hdf5.save(example_object, FILENAME_TMP)
    # check if the expected groups are in the file
    with h5py.File(FILENAME_TMP, "r") as h5file:
        assert EXAMPLE_OBJECT in h5file
        group = h5file[EXAMPLE_OBJECT]
        assert NAME in group
        subgroup = group[NAME]
        assert not str(VALUE) in subgroup
        assert "data" in subgroup
    os.remove(FILENAME_TMP)

    # with value but without name
    example_object = ExampleObject(DATA, value=VALUE)
    with pytest.warns(UserWarning, match="Intermediate identifier is None, group name cannot be parsed back"):
        hdf5.save(example_object, FILENAME_TMP)
    # check if the expected groups are in the file
    with h5py.File(FILENAME_TMP, "r") as h5file:
        assert EXAMPLE_OBJECT in h5file
        group = h5file[EXAMPLE_OBJECT]
        assert not NAME in group
        assert str(VALUE) in group
        subgroup = group[str(VALUE)]
        assert "data" in subgroup
    os.remove(FILENAME_TMP)

    # without name and value
    example_object = ExampleObject(DATA)
    hdf5.save(example_object, FILENAME_TMP)
    # check if the expected groups are in the file
    with h5py.File(FILENAME_TMP, "r") as h5file:
        assert EXAMPLE_OBJECT in h5file
        group = h5file[EXAMPLE_OBJECT]
        assert not NAME in group
        assert not str(VALUE) in group
        assert "data" in group
    os.remove(FILENAME_TMP)

def test_load(example_object):
    """
    testing if the object is loaded correctly
    we will use here ExampleObject exemplary
    """
    # load with all identifying attributes - ExampleObject/example_object/99
    loaded = hdf5.load(ExampleObject, FILENAME_FIX, name=NAME, value=VALUE)
    _check_loaded(loaded, example_object)

    # load with all identifying attributes and prefix - Prefix/ExampleObject/example_object/99
    loaded = hdf5.load(ExampleObject, FILENAME_FIX, prefix_group_name=PREFIX, name=NAME, value=VALUE)
    _check_loaded(loaded, example_object)

    # load with full group name containing all identifying attributes - ExampleObject/example_object/99
    with pytest.warns(UserWarning, match="Experimental parsing of attributes"):
        loaded = hdf5.load(ExampleObject, FILENAME_FIX, full_group_name=FULL_GROUP_NAME_99)
    _check_loaded(loaded, example_object)

    # missing identifying attributes
    with pytest.raises(ValueError, match=f"Did not find dataset 'data' in group '/{EXAMPLE_OBJECT}' in HDF5 file"):
        hdf5.load(ExampleObject, FILENAME_FIX)
    with pytest.raises(ValueError, match=f"Did not find dataset 'data' in group '/{HALF_GROUP_NAME}' in HDF5 file"):
        hdf5.load(ExampleObject, FILENAME_FIX, name=NAME)

    wrong_name = EXAMPLE_OBJECT + '/wrong_name'
    with pytest.raises(ValueError, match=f"Did not find group '{wrong_name}' in HDF5 file '.*{FILE}'"):
        hdf5.load(ExampleObject, FILENAME_FIX, name='wrong_name')
    with pytest.warns(UserWarning, match='Experimental parsing of attributes'):
        with pytest.raises(ValueError, match=f"Did not find group '{wrong_name}' in HDF5 file '.*{FILE}'"):
            hdf5.load(ExampleObject, FILENAME_FIX, full_group_name=wrong_name)
    with pytest.raises(ValueError, match='Either provide prefix for default group name or full group name'):
        assert hdf5.load(ExampleObject, FILENAME_FIX, prefix_group_name=PREFIX, full_group_name=FULL_GROUP_NAME_99)
    with pytest.raises(AssertionError, match="IO is not implemented correctly"):
        with pytest.warns(UserWarning, match='Experimental parsing of attributes'):
            hdf5.load(ExampleObjectWrongIO, FILENAME_FIX, full_group_name=FULL_GROUP_NAME_99)
    with pytest.raises(ValueError, match="Either give identifier 'name' of the class or a full group name"):
        hdf5.load(ExampleObjectWrongIO, FILENAME_FIX, value="example_object/99")

def test_load_identifiers(example_object):
    """ test save and load round trip with different identifier settings """
    # with all identifiers
    hdf5.save(example_object, filename=FILENAME_TMP)
    loaded = hdf5.load(ExampleObject, FILENAME_TMP, name=NAME, value=VALUE)
    _check_loaded(loaded, example_object)
    with pytest.warns(UserWarning, match="Experimental parsing of attributes from group name"):
        loaded = hdf5.load(ExampleObject, FILENAME_TMP, full_group_name=FULL_GROUP_NAME_99)
    _check_loaded(loaded, example_object)
    os.remove(FILENAME_TMP)

    # with name but without value
    example_object = ExampleObject(DATA, NAME, None)
    hdf5.save(example_object, filename=FILENAME_TMP)
    loaded = hdf5.load(ExampleObject, FILENAME_TMP, name=NAME)
    _check_loaded(loaded, example_object)
    loaded = hdf5.load(ExampleObject, FILENAME_TMP, name=NAME, value=None)
    _check_loaded(loaded, example_object)
    with pytest.warns(UserWarning, match="Experimental parsing of attributes from group name"):
        loaded = hdf5.load(ExampleObject, FILENAME_TMP, full_group_name=HALF_GROUP_NAME)
    _check_loaded(loaded, example_object)
    os.remove(FILENAME_TMP)

    # without name and value
    example_object = ExampleObject(DATA, None, None)
    hdf5.save(example_object, filename=FILENAME_TMP)
    loaded = hdf5.load(ExampleObject, FILENAME_TMP)
    _check_loaded(loaded, example_object)
    loaded = hdf5.load(ExampleObject, FILENAME_TMP, name=None)
    _check_loaded(loaded, example_object)
    os.remove(FILENAME_TMP)

    # with value but without name
    example_object = ExampleObject(DATA, None, VALUE)
    with pytest.warns(UserWarning, match="Intermediate identifier is None, group name cannot be parsed back"):
        hdf5.save(example_object, filename=FILENAME_TMP)
    loaded = hdf5.load(ExampleObject, FILENAME_TMP, name=None, value=VALUE)
    _check_loaded(loaded, example_object)
    loaded = hdf5.load(ExampleObject, FILENAME_TMP, value=VALUE)
    _check_loaded(loaded, example_object)

    with pytest.warns(UserWarning, match="Experimental parsing of attributes from group name"):
        loaded = hdf5.load(ExampleObject, FILENAME_TMP, full_group_name="ExampleObject/99")
    assert loaded.data == example_object.data
    # here something went wrong because it cannot be retrieved which identifier was set to None
    # as the ordering of the identifiers is important!
    assert loaded.name == example_object.value
    assert loaded.value is None
    os.remove(FILENAME_TMP)

def _check_loaded(loaded, saved):
    assert loaded.name == saved.name
    assert loaded.value == saved.value
    assert loaded.data == saved.data

def test_error():
    """ testing non-existing io on two test objects """
    _test_error_on(ExampleObjectWithoutIO)
    _test_error_on(TwoLevelExampleObject)

def _test_error_on(cls):
    example_object = cls()
    # trying to store the object is failing
    with pytest.raises(ValueError, match="Object of type 'ExampleObjectWithoutIO' does not have a write_hdf5 method"):
        hdf5.save(example_object, FILENAME_TMP)
    with pytest.raises(ValueError, match="Class 'ExampleObjectWithoutIO' does not have a read_hdf5 method"):
        hdf5.load(cls, FILENAME_TMP)
    os.remove(FILENAME_TMP)

def test_inheritance_error():
    """ testing non-existing io on inheriting object """
    example_object = InheritingExampleObject()
    # trying to store the object is failing
    with pytest.raises(ValueError, match="Object of type 'super' does not have a write_hdf5 method"):
        hdf5.save(example_object, FILENAME_TMP)
    with pytest.raises(ValueError, match=r"\(Super\?\) Class does not have a read_hdf5 method"):
        hdf5.load(InheritingExampleObject, FILENAME_TMP)
    os.remove(FILENAME_TMP)

def test_is_subgroup():
    """ test helper method for subgroups """
    with h5py.File(FILENAME_FIX, "r") as h5file:
        assert hdf5.is_subgroup(h5file, EXAMPLE_OBJECT)
        group = h5file[EXAMPLE_OBJECT]
        assert hdf5.is_subgroup(group, NAME)
        assert not hdf5.is_subgroup(group, "wrong_name")

def test_parse_identifiers_from_group_name():
    """ test helper method for identifiers """
    exp_identifiers = {"name" : NAME, "value" : 100}
    with pytest.warns(UserWarning, match="Experimental parsing of attributes from group name"):
        identifiers = hdf5.parse_identifiers_from_group_name(ExampleObject, HALF_GROUP_NAME + "/100")
    assert identifiers == exp_identifiers

def test_get_all_subgroup_names():
    """ test helper method for getting all subgroups """
    names = hdf5.get_all_subgroup_names(FILENAME_FIX)
    assert names == [EXAMPLE_OBJECT, "ExampleObjectWrongIO", PREFIX]

    names = hdf5.get_all_subgroup_names(FILENAME_FIX, EXAMPLE_OBJECT)
    assert names == [HALF_GROUP_NAME]

    names = hdf5.get_all_subgroup_names(FILENAME_FIX, EXAMPLE_OBJECT, depth=1, complete=False)
    assert names == [NAME + "/98", NAME + "/99"]

    names = hdf5.get_all_subgroup_names(FILENAME_FIX, EXAMPLE_OBJECT, depth=2, complete=False)
    assert names == [NAME + "/98/data", NAME + "/99/data"]

    names = hdf5.get_all_subgroup_names(FILENAME_FIX, EXAMPLE_OBJECT, depth=1, complete=True)
    assert names == [HALF_GROUP_NAME + "/98", HALF_GROUP_NAME + "/99"]

    assert not hdf5.get_all_subgroup_names(FILENAME_FIX, "NotExistingObject")

def test_load_all():
    """ test loading of several objects """
    with pytest.warns(UserWarning, match="Experimental parsing of attributes from group name"):
        objs = hdf5.load_all(ExampleObject, FILENAME_FIX)
        _check_loaded_objs(objs)

        objs = hdf5.load_all(ExampleObject, FILENAME_FIX, prefix_group_name=HALF_GROUP_NAME, used_default=False)
        _check_loaded_objs(objs)

        objs = hdf5.load_all(ExampleObject, FILENAME_FIX, index_range=[1])
        assert len(objs) == 1
        assert objs[0].name == NAME
        assert objs[0].value == VALUE

def _check_loaded_objs(objs):
    assert len(objs) == 2
    assert objs[0].name == NAME
    assert objs[0].value == 98
    assert objs[1].name == NAME
    assert objs[1].value == VALUE
