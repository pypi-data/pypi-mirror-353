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

""" module for testing the IO of the Embedding """

import os
import pytest

from quark import Embedding, HardwareAdjacency
from quark.io import hdf5


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"
FILE = "embedding.h5"
FILENAME_TMP = TEST_DIR + FILE
FILENAME_FIX = TEST_DIR + "testdata/" + FILE

VAR_NODES_MAP = {0: [50, 51, 52], 1: [53, 54, 55, 56], 2: [70]}
VAR_EDGES_MAP = {0: [(50, 51), (51, 52)], 1: [(53, 54), (54, 55), (55, 56)], 2: []}
COUPLING_EDGES_MAP = {(0, 1): [(50, 53)], (1, 2): []}
EMBEDDING = Embedding(VAR_NODES_MAP, COUPLING_EDGES_MAP, VAR_EDGES_MAP, name="test_embedding")
EMBEDDING_INDEX = Embedding(VAR_NODES_MAP, name="test_embedding_index", index=1)

VAR_NODES_MAP_CHIMERA = {0: [4, 0, 24, 48],
                         1: [5, 1, 25, 49],
                         2: [6, 2, 26, 50],
                         3: [7, 3, 27, 51],
                         4: [28, 36, 32, 56],
                         5: [29, 37, 33, 57],
                         6: [30, 38, 34, 58],
                         7: [31, 39, 35, 59],
                         8: [68, 64, 60, 52],
                         9: [69, 65, 61, 53],
                         10: [70, 66, 62, 54],
                         11: [71, 67, 63, 55]}


def test_load_hdf5():
    """ test loading from h5 files """
    loaded = hdf5.load(Embedding, FILENAME_FIX, name=EMBEDDING.name)
    assert loaded == EMBEDDING

def test_io_hdf5():
    """ test io round trip """
    hdf5.save(EMBEDDING, FILENAME_TMP)
    loaded = hdf5.load(Embedding, FILENAME_TMP, name=EMBEDDING.name)
    assert loaded == EMBEDDING

    hdf5.save(EMBEDDING_INDEX, FILENAME_TMP)
    loaded = hdf5.load(Embedding, FILENAME_TMP, name=EMBEDDING_INDEX.name, index=EMBEDDING_INDEX.index)
    assert loaded == EMBEDDING_INDEX

    os.remove(FILENAME_TMP)

def test_complete_graph_embedding():
    """ test complete graph check """
    with pytest.warns(UserWarning, match="Experimental parsing of attributes from group name"):
        chimera_hwa = hdf5.load(HardwareAdjacency,
                                TEST_DIR + "testdata/hwa.h5",
                                full_group_name="ChimeraHWA/full_chimera_3_3_4")
    embedding = Embedding.get_from_hwa(VAR_NODES_MAP_CHIMERA, chimera_hwa)
    assert embedding.are_all_couplings_mapped('complete')
