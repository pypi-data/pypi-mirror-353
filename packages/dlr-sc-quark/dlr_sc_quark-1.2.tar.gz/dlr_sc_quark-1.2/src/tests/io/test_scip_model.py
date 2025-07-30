# Copyright 2023 DLR-SC
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

""" module for testing the ScipModel with loaded ObjectiveTerms """

import os
import pytest

from quark import ScipModel, ConstrainedObjective
from quark.io import hdf5


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"
FILE = "constrained_objective.h5"
FILENAME_FIX = TEST_DIR + "testdata/"+ FILE


def test_init_with_load_hdf5():
    """ test ScipModel with hdf5 io (probably causing issues due to numpy arrays) """
    # TODO: set up other example without warnings
    with pytest.warns(UserWarning) as record:
        loaded_const_obj = hdf5.load(ConstrainedObjective, FILENAME_FIX, full_group_name="PFConstrainedObjective")
    assert len(record) == 2
    assert str(record[0].message).startswith("Experimental parsing")
    assert str(record[1].message).startswith("The two variables '('prime1', 1)' and '('prime2', 1)'")

    model = ScipModel.get_from_constrained_objective(loaded_const_obj)
    assert len(model.getConss()) == 18
