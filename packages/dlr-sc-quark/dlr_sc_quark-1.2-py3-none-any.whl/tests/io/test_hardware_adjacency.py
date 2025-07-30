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

""" module for testing the IO of the HardwareAdjacency """

import os

from quark import HardwareAdjacency
from quark.io import hdf5


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"
FILE = "hwa.h5"
FILENAME_TMP = TEST_DIR + FILE
FILENAME_FIX = TEST_DIR + "testdata/" + FILE

HWA = HardwareAdjacency([(5, 6), (1, 4), (3, 5)], "test_hwa_fix")


def test_load_hdf5():
    """ test loading from h5 files """
    loaded = hdf5.load(HardwareAdjacency, FILENAME_FIX, name=HWA.name)
    assert loaded == HWA

def test_io_hdf5():
    """ test IO round trip """
    hdf5.save(HWA, FILENAME_TMP)
    loaded = hdf5.load(HardwareAdjacency, FILENAME_TMP, name=HWA.name)
    assert loaded == HWA
    os.remove(FILENAME_TMP)
