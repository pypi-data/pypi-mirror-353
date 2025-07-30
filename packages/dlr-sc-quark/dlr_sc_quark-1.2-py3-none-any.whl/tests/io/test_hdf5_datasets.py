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

""" module for testing the IO of datasets in HDF5 files """

import os
import pytest
import numpy as np
import h5py

from quark.io import hdf5_datasets


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"
FILE = "datasets.h5"
FILENAME_TMP = TEST_DIR + FILE
FILENAME_FIX = TEST_DIR + "testdata/" + FILE
GROUP_NAME = "testgroup_datasets"

SUPPORTED_DATASETS = {
    "empty_list": [],
    "1d_int": [1, 2, 3, 4, 5],
    "1d_float": [1.0, 2.5, 3.333333],
    "1d_mixed": [1, 2.5, 3],
    "1d_strings": ["one", "two", "three"],
    "2d_fixed_len_int": [[1, 2, 3], [4, 5, 6]],
    "2d_fixed_len_float": [[1.5, 2.0, 3.0], [4.0, 5.0, 6.0]],
    "2d_var_len_int": [[1, 2], [1], [], [1, 2, 3]],
    "2d_var_len_int_tuples": [(1, 2), (1,), (), (1, 2, 3)],
    "2d_var_len_numeric": [[1.0, 2.1], [1.8], [], [0, 2, 3.99]],
    "2d_empty_tuple": [()],
    "dict_int_to_int": {1: 2, 2: 2, 3: 3},
    "dict_string_to_float": {"qubits": 16, "annealing_time": 0.001},
    "dict_int_tuple_to_scalar": {(0,): 2.5, (1, 2, 3): 2.0, (): 5.5},
    "dict_int_tuple_to_scalar2": {(): 55, (2,): 66},
    "dict_empty_tuple": {(): 2.5},
    "dict_int_tuple_one_entry": {(1,): 2.5},
    "dict_int_to_string": {1: "x", 2: "y", 50: "test"},
    "empty_dict": {},
    "numpy_array": np.array([1, 2, 3, 4, 5]),
}

NOT_SUPPORTED_DATASETS = {
    "2d_var_len_string": [("x", "0"), ("reduction", "x", "0", "y", "0")],
    "2d_var_len_mixed_type": [("x", 1), ("y", 0, 0)],
    "dict_tuple_key_ints": {((10, 1),): 2.5, ((10, 2), (11, 0, 0)): 2.0, (): 5.5},
    "dict_tuple_key_mixed": {(("x", 1),): 2.5, (("x", 2), ("y", 0, 0)): 2.0, (): 5.5}
}

OTHER_DATASET = [-1.0, -10]

class ExampleObject:
    """ some test object """
    pass


@pytest.mark.parametrize("name, dataset", SUPPORTED_DATASETS.items())
def test_read_write_dataset(name, dataset):
    """
    test the read and write functions in hdf5_datasets

    :param name: the name of the dataset
    :param dataset: the dataset to read and write
    """
    with h5py.File(FILENAME_TMP, "w") as h5file:
        group = h5file.create_group(GROUP_NAME)
        hdf5_datasets.write_dataset(group, name, dataset=dataset)

    with h5py.File(FILENAME_TMP, "r") as h5file:
        group = h5file[GROUP_NAME]
        dataset_from_file = hdf5_datasets.read_dataset(group, name)

    _check_datasets(dataset, dataset_from_file)
    os.remove(FILENAME_TMP)

@pytest.mark.parametrize("name, dataset", NOT_SUPPORTED_DATASETS.items())
def test_not_supported_dataset(name, dataset):
    """
    test the read and write functions in hdf5_datasets

    :param name: the name of the dataset
    :param dataset: the dataset to read and write
    """
    with pytest.raises(NotImplementedError, match="Storing of dataset"):
        with h5py.File(FILENAME_TMP, "w") as h5file:
            group = h5file.create_group(GROUP_NAME)
            hdf5_datasets.write_dataset(group, name, dataset=dataset)

def test_other_datasets():
    """ test write function in hdf5_datasets throwing an error for attributes """
    with pytest.raises(ValueError, match="Given dataset is just a scalar, create attribute instead"):
        with h5py.File(FILENAME_TMP, "w") as h5file:
            hdf5_datasets.write_dataset(h5file, "test_string", dataset="string")

    with h5py.File(FILENAME_TMP, "w") as h5file:
        group = h5file.create_group(GROUP_NAME)
        hdf5_datasets.write_dataset(group, "None", dataset=None)

        with pytest.raises(ValueError, match="Storing of dataset with type"):
            hdf5_datasets.write_dataset(group, "numpy_array_object", dataset=np.array([1, 2, 3, 4, 5], dtype=object))
        with pytest.raises(NotImplementedError, match="Storing of dataset with type list over '<class 'type'>'"):
            hdf5_datasets.write_dataset(group, "numpy_string", dataset=[object, object])
        with pytest.raises(TypeError, match="Dictionary keys are not of homogeneous type"):
            hdf5_datasets.write_dataset(group, "dict_keys_var_len_mixed_type", dataset={("x", 1): 1, "y0": 2})
        with pytest.raises(TypeError, match="Key items are not of homogeneous type"):
            hdf5_datasets.write_dataset(group, "dict_keys_var_len_mixed_type", dataset={("x", 1): 1, ("y", 0, 0): 2})

    with h5py.File(FILENAME_TMP, "r") as h5file:
        group = h5file[GROUP_NAME]
        dataset_from_file = hdf5_datasets.read_dataset(group, "None")
        assert dataset_from_file is None

    os.remove(FILENAME_TMP)

def test_write_read_datasets_obj():
    example_object = ExampleObject()
    for name, ds in SUPPORTED_DATASETS.items():
        example_object.__setattr__(name, ds)


    with h5py.File(FILENAME_TMP, "w") as h5file:
        group = h5file.create_group(GROUP_NAME)
        # test with overwrite
        hdf5_datasets.write_dataset(group, "other", dataset=[])
        # tests taking the datasets from the object and additionally the keyword plus its value
        hdf5_datasets.write_datasets(group, example_object, *SUPPORTED_DATASETS.keys(), other=OTHER_DATASET)

    with h5py.File(FILENAME_TMP, "r") as h5file:
        group = h5file[GROUP_NAME]
        read_datasets = hdf5_datasets.read_datasets(group, "other", *SUPPORTED_DATASETS.keys())

        assert len(read_datasets) == len(SUPPORTED_DATASETS) + 1
        for name in SUPPORTED_DATASETS.keys():
            # checking if they read in datasets are equal to the stored ones
            _check_datasets(getattr(example_object, name), read_datasets[name])
        _check_datasets(OTHER_DATASET, read_datasets["other"])

    os.remove(FILENAME_TMP)

def test_read_datasets():
    with h5py.File(FILENAME_FIX, "r") as h5file:
        group = h5file[GROUP_NAME]
        read_datasets = hdf5_datasets.read_datasets(group, "other", *SUPPORTED_DATASETS.keys())

        assert len(read_datasets) == len(SUPPORTED_DATASETS) + 1
        for name, ds in SUPPORTED_DATASETS.items():
            # checking whether the read in datasets are as we expect them
            _check_datasets(ds, read_datasets[name])
        _check_datasets(OTHER_DATASET, read_datasets["other"])

        with pytest.raises(ValueError, match="Mismatched dictionary dataset"):
            hdf5_datasets.read_dataset(group, "dict_unreadable")


def _check_datasets(dataset, dataset_from_file):
    if isinstance(dataset, dict):
        assert dataset_from_file == dataset
    else:
        assert len(dataset) == len(dataset_from_file)
        assert all(np.array_equal(a, b) for a, b in zip(dataset, dataset_from_file))
