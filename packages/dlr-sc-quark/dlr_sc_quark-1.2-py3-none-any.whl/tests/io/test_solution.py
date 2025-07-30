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

""" module for testing the IO of the Solution """

import os
import pytest

from quark import Solution
from quark.io import hdf5


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"
FILE = "solution.h5"
FILENAME_TMP = TEST_DIR + FILE
FILENAME_FIX = TEST_DIR + "testdata/" + FILE

NAME = "test_solution"
NAME_EMPTY = "empty_solution"
NAME_NON_COMPACT = "non-compact_solution"


@pytest.fixture
def solutions():
    """ set up method """
    solving_time = 12
    solving_success = True
    solving_status = "optimal"
    objective_value = -12.1
    var_assignment = {0: 0, 1: 1, 2: 1, 3: 0, 4: 0, 5: 1, 6: 0, 7: 0, 8: 1}
    dual_gap = 1.1
    dual_bound = 0.1
    
    solution = Solution(var_assignments=var_assignment,
                        objective_value=objective_value,
                        solving_success=solving_success,
                        solving_status=solving_status,
                        solving_time=solving_time,
                        dual_gap=dual_gap,
                        dual_bound=dual_bound,
                        name=NAME)

    solution_empty = Solution(var_assignments={},
                              objective_value=objective_value,
                              solving_success=solving_success,
                              solving_status=solving_status,
                              solving_time=solving_time,
                              dual_gap=dual_gap,
                              dual_bound=dual_bound,
                              name=NAME_EMPTY)

    solution_nc = Solution(var_assignments={('x', 0, 1): 1, ('y', 3): 0},
                           objective_value=objective_value,
                           solving_success=solving_success,
                           solving_status=solving_status,
                           solving_time=solving_time,
                           dual_gap=dual_gap,
                           dual_bound=dual_bound,
                           name=NAME_NON_COMPACT)

    yield solution, solution_empty, solution_nc
        
def test_load_hdf5(solutions):
    """ test hdf5 io """
    solution, solution_empty, solution_nc = solutions

    loaded = hdf5.load(Solution, FILENAME_FIX, name=NAME)
    assert loaded == solution

    loaded = hdf5.load(Solution, FILENAME_FIX, name=NAME_EMPTY)
    assert loaded == solution_empty

    loaded = hdf5.load(Solution, FILENAME_FIX, name=NAME_NON_COMPACT)
    assert loaded == solution_nc

def test_io_hdf5(solutions):
    """ test hdf5 io round trip """
    solution, solution_empty, solution_nc = solutions

    hdf5.save(solution, FILENAME_TMP)
    loaded = hdf5.load(Solution, FILENAME_TMP, name=NAME)
    assert loaded == solution

    hdf5.save(solution_empty, FILENAME_TMP)
    loaded = hdf5.load(Solution, FILENAME_TMP, name=NAME_EMPTY)
    assert loaded == solution_empty

    hdf5.save(solution_nc, FILENAME_TMP)
    loaded = hdf5.load(Solution, FILENAME_TMP, name=NAME_NON_COMPACT)
    assert loaded == solution_nc

    os.remove(FILENAME_TMP)
