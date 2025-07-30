# Copyright 2024 DLR-SC
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

""" module for fixtures for sophisticated tests """

import pytest

from quark import PolyBinary, ConstraintBinary, ConstrainedObjective, ObjectiveTerms, Objective, Solution
from quark.testing import ExampleInstance, ExampleObjectiveTerms, ExampleObjective


X = "x"
EXP_NAME = "colored_edges1.000000e+00_one_color_per_node7.000000e+00"
B, G, R = "blue", "green", "red"


@pytest.fixture(name="instance")
def fixture_instance():
    """
    provide the ExampleInstance test object,
    built upon an example implementation inheriting from the base class
    """
    edges = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1), (1, 3), (3, 5)]
    colors = [G, B, R]
    yield ExampleInstance(edges, colors)

@pytest.fixture(name="constrained_objective")
def fixture_constrained_objective(instance):
    """
    provide ConstrainedObjective test object from instance data,
    uses ExampleConstrainedObjective implementation
    """
    yield instance.get_constrained_objective()

@pytest.fixture(name="objective_terms")
def fixture_objective_terms(instance):
    """
    provide ObjectiveTerms test object from instance data,
    uses ExampleConstrainedObjective implementation and automized ObjectiveTerms construction
    """
    yield instance.get_objective_terms()

@pytest.fixture(name="objective")
def fixture_objective(instance):
    """
    provide Objective test object from instance data,
    uses ExampleConstrainedObjective implementation and automized ObjectiveTerms and Objective construction
    """
    yield instance.get_objective(penalty_scale=7)


@pytest.fixture(name="objective_terms_direct_impl")
def fixture_objective_terms_direct_impl(instance):
    """
    provide ObjectiveTerms test object from instance data,
    uses ExampleConstrainedObjective implementation and automized ObjectiveTerms construction
    """
    yield ExampleObjectiveTerms.get_from_instance(instance)

@pytest.fixture(name="objective_direct_impl")
def fixture_objective_direct_impl(instance):
    """
    provide Objective test object from instance data,
    uses ExampleConstrainedObjective implementation and automized ObjectiveTerms and Objective construction
    """
    yield ExampleObjective.get_from_instance(instance)


EXP_OBJECTIVE_POLY = PolyBinary({((X, 1, B), (X, 2, B)): 1, ((X, 1, G), (X, 2, G)): 1, ((X, 1, R), (X, 2, R)): 1,
                                 ((X, 2, B), (X, 3, B)): 1, ((X, 2, G), (X, 3, G)): 1, ((X, 2, R), (X, 3, R)): 1,
                                 ((X, 3, B), (X, 4, B)): 1, ((X, 3, G), (X, 4, G)): 1, ((X, 3, R), (X, 4, R)): 1,
                                 ((X, 4, B), (X, 5, B)): 1, ((X, 4, G), (X, 5, G)): 1, ((X, 4, R), (X, 5, R)): 1,
                                 ((X, 5, B), (X, 1, B)): 1, ((X, 5, G), (X, 1, G)): 1, ((X, 5, R), (X, 1, R)): 1,
                                 ((X, 1, B), (X, 3, B)): 1, ((X, 1, G), (X, 3, G)): 1, ((X, 1, R), (X, 3, R)): 1,
                                 ((X, 3, B), (X, 5, B)): 1, ((X, 3, G), (X, 5, G)): 1, ((X, 3, R), (X, 5, R)): 1})
EXP_PENALTY_TERM = PolyBinary({(): 5,
                               ((X, 1, B),): -1, ((X, 1, G),): -1, ((X, 1, R),): -1,
                               ((X, 2, B),): -1, ((X, 2, G),): -1, ((X, 2, R),): -1,
                               ((X, 3, B),): -1, ((X, 3, G),): -1, ((X, 3, R),): -1,
                               ((X, 4, B),): -1, ((X, 4, G),): -1, ((X, 4, R),): -1,
                               ((X, 5, B),): -1, ((X, 5, G),): -1, ((X, 5, R),): -1,
                               ((X, 1, B), (X, 1, G)): 2, ((X, 1, B), (X, 1, R)): 2, ((X, 1, G), (X, 1, R)): 2,
                               ((X, 2, B), (X, 2, G)): 2, ((X, 2, B), (X, 2, R)): 2, ((X, 2, G), (X, 2, R)): 2,
                               ((X, 3, B), (X, 3, G)): 2, ((X, 3, B), (X, 3, R)): 2, ((X, 3, G), (X, 3, R)): 2,
                               ((X, 4, B), (X, 4, G)): 2, ((X, 4, B), (X, 4, R)): 2, ((X, 4, G), (X, 4, R)): 2,
                               ((X, 5, B), (X, 5, G)): 2, ((X, 5, B), (X, 5, R)): 2, ((X, 5, G), (X, 5, R)): 2})

@pytest.fixture(name="exp_constrained_objective")
def fixture_exp_constrained_objective():
    """ provide the fixed ObjectiveTerms test object """
    constraint_polys = [PolyBinary({((X, 1, B),): 1, ((X, 1, G),): 1, ((X, 1, R),): 1}),
                        PolyBinary({((X, 2, B),): 1, ((X, 2, G),): 1, ((X, 2, R),): 1}),
                        PolyBinary({((X, 3, B),): 1, ((X, 3, G),): 1, ((X, 3, R),): 1}),
                        PolyBinary({((X, 4, B),): 1, ((X, 4, G),): 1, ((X, 4, R),): 1}),
                        PolyBinary({((X, 5, B),): 1, ((X, 5, G),): 1, ((X, 5, R),): 1})]
    exp_constraints = {"one_color_per_node_1": ConstraintBinary(constraint_polys[0], 1, 1),
                       "one_color_per_node_2": ConstraintBinary(constraint_polys[1], 1, 1),
                       "one_color_per_node_3": ConstraintBinary(constraint_polys[2], 1, 1),
                       "one_color_per_node_4": ConstraintBinary(constraint_polys[3], 1, 1),
                       "one_color_per_node_5": ConstraintBinary(constraint_polys[4], 1, 1)}
    yield ConstrainedObjective(EXP_OBJECTIVE_POLY, exp_constraints)

@pytest.fixture(name="exp_objective_terms")
def fixture_exp_objective_terms():
    """ provide the fixed ObjectiveTerms test object """
    exp_terms = {"colored_edges": EXP_OBJECTIVE_POLY,
                 "one_color_per_node": EXP_PENALTY_TERM}
    yield ObjectiveTerms(exp_terms, ["one_color_per_node"])

@pytest.fixture(name="exp_objective")
def fixture_exp_objective():
    """ provide the fixed Objective test object """
    exp_objective_poly = EXP_OBJECTIVE_POLY + 7 * EXP_PENALTY_TERM
    yield Objective(exp_objective_poly, EXP_NAME)


VAR_ASSIGNMENTS = [{(X, 1, B): 1, (X, 1, G): 0, (X, 1, R): 0,
                    (X, 2, B): 0, (X, 2, G): 0, (X, 2, R): 1,
                    (X, 3, B): 0, (X, 3, G): 1, (X, 3, R): 0,
                    (X, 4, B): 1, (X, 4, G): 0, (X, 4, R): 0,
                    (X, 5, B): 0, (X, 5, G): 0, (X, 5, R): 1},
                   {(X, 1, B): 1, (X, 1, G): 0, (X, 1, R): 0,
                    (X, 2, B): 0, (X, 2, G): 1, (X, 2, R): 0,
                    (X, 3, B): 0, (X, 3, G): 0, (X, 3, R): 1,
                    (X, 4, B): 1, (X, 4, G): 0, (X, 4, R): 0,
                    (X, 5, B): 0, (X, 5, G): 1, (X, 5, R): 0}]

@pytest.fixture(name="solution")
def fixture_solution():
    """ provide the Solution test object """
    yield Solution(VAR_ASSIGNMENTS[0], objective_value=0.0, name='from_constrained_objective')

@pytest.fixture(name="solutions")
def fixture_solutions():
    """ provide the Solution test object """
    yield [Solution(var_assignments, objective_value=0.0, name='from_constrained_objective')
           for var_assignments in VAR_ASSIGNMENTS]
