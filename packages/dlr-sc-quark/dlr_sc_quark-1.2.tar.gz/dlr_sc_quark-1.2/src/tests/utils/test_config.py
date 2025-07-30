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

""" module for testing the configuration base class """

import os
import pytest

from quark.utils.config import Config, dict_to_string, _to_string
from quark.testing import ExampleConfig


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"
FILENAME_TMP = TEST_DIR + "test_config.cfg"

DEFAULT_CONFIG = {"float_option": 20.0,
                  "int_option": 10,
                  "list_option": None,
                  "str_option": "some_string",
                  "dict_option": {"default": 0}}


def test_name():
    """ Test if the name gets returned correctly """
    conf = ExampleConfig()
    assert conf.get_name() == "ExampleConfig"

def test_config():
    """ Test the example configuration file, check if parameters get set correctly """
    config = ExampleConfig(1.0, int_option=10)
    assert config.int_option == 10
    assert config["float_option"] == 1.0
    config.int_option = 5
    assert config["int_option"] == 5
    del config["int_option"]
    assert config.int_option is None
    assert config.str_option is None
    config.update(str_option="test", dict_option={"test": 123})
    assert config.str_option == "test"
    assert config["dict_option"] == {"test": 123}
    assert config.int_option is None
    config.str_option = None
    assert config["str_option"] is None
    config.set_defaults(override=False)
    assert config.float_option == 1.0
    assert config.int_option == 10
    assert config["str_option"] == "some_string"
    assert config.dict_option == {"test": 123}
    config.set_defaults()
    assert config.float_option == 20.0
    assert config.int_option == 10
    assert config["str_option"] == "some_string"
    assert config.dict_option == {"default": 0}
    config.str_option = "1"
    assert config.str_option != 1
    assert config.str_option == "1"

    errors = [lambda x: config[x],
              lambda x: config.x,
              lambda x: config.update(**{x: 1}),
              config.__getattr__,
              config.__getitem__,
              config.__delattr__,
              config.__delitem__]
    for call in errors:
        with pytest.raises(AttributeError):
            call("non_existing_key")

    config.num_reads = "string instead of number"
    assert config.num_reads == "string instead of number"

    config.int_option = dict({"test.": 123})
    assert isinstance(config.int_option, dict)

def test_get_options_dict():
    """ Test if the options dict returns contains correct parameters """
    config = ExampleConfig(set_defaults=True)
    options_dict = config.get_options_dict()
    for key, option in DEFAULT_CONFIG.items():
        assert options_dict[key]["default"] == option

    with pytest.raises(NotImplementedError):
        Config.get_options_dict()

def test_io():
    """ test read and write of the example Config """
    config_1 = ExampleConfig(float_option=100.50, int_option=5, str_option="hello_world")
    config_2 = ExampleConfig(float_option=1.0, int_option=1300, set_defaults=True)
    assert config_1.float_option != config_2.float_option
    config_1.save(FILENAME_TMP)
    config_1_loaded = ExampleConfig.load(filename=FILENAME_TMP)
    assert config_1 == config_1_loaded

    config_2.save(FILENAME_TMP)
    config_2_loaded = ExampleConfig.load(FILENAME_TMP)
    assert config_1_loaded != config_2_loaded
    assert config_2 == config_2_loaded

    config_broken = ExampleConfig(float_option="10aa0")
    config_broken.save(FILENAME_TMP)
    with pytest.raises(TypeError, match="The value is of type '<class 'str'>'"):
        config_broken.load(FILENAME_TMP)

    config_broken = ExampleConfig(str_option=10, dict_option=[])
    config_broken.save(FILENAME_TMP)
    with pytest.raises(TypeError, match="The value is of type '<class 'list'>'"):
        config_broken.load(FILENAME_TMP)

    os.remove(FILENAME_TMP)

def test_to_string():
    """ test conversion to strings """
    config = ExampleConfig(float_option=1.23,
                           int_option=1024,
                           list_option=[1.1, 2.2],
                           set_defaults=True)
    expected_string = "_float_option1.230000e+00"
    expected_string += "_int_option1.024000e+03"
    expected_string += "_list_option_1.100000e+00_2.200000e+00"
    expected_string += "_str_option_some_string"
    expected_string += "_dict_option_default0.000000e+00"
    assert config.to_string(max_depth=1) == expected_string

    with pytest.raises(ValueError, match="Level of nested dictionaries exceeds specified maximal depth 0"):
        config.to_string(max_depth=0)

def test_update():
    """ test of the update method """
    config = ExampleConfig(set_defaults=True)
    assert config["float_option"] == 20.0
    config.update(float_option=50.33)
    assert config["float_option"] == 50.33
    with pytest.raises(AttributeError):
        config.update(not_existing_argument=100)

def test_class_methods():
    """ test of the class methods """
    conf = ExampleConfig(set_defaults=True)
    filename_not_exist = "nowhere"
    file_not_exist = TEST_DIR + filename_not_exist
    with pytest.raises(ValueError, match=f"Configuration file '.*{filename_not_exist}' does not exists"):
        conf.load(filename=file_not_exist)

    with open(FILENAME_TMP, mode="a", encoding="utf-8") as txt_file:
        with pytest.raises(ValueError, match="Missing section 'ExampleConfig' in configuration file"):
            conf.load(FILENAME_TMP)

        txt_file.write("[ExampleConfig]\n")

    with pytest.raises(ValueError, match="Missing option 'float_option' in configuration file"):
        conf.load(FILENAME_TMP)

    assert conf.get_defaults() is not None
    assert conf.get_help() is not None

    os.remove(FILENAME_TMP)


STR = "text"
INT = 1024
FLOAT = 1.23
LIST = [1.1, 2.2]
BOOL = True
SUBSUB_DICT = dict({"a": 1, "b": 1.1})
SUB_DICT1 = dict({"answer": "yes", "subsubdict": SUBSUB_DICT})
SUB_DICT2 = dict({"A": 2, "B": 2.2, "to_omit_in_subdict": "some/complicated/path/to/omit/"})
DICTIONARY = {"str"      : STR,
              "int"      : INT,
              "bool"     : BOOL,
              "float"    : FLOAT,
              "subdict1" : SUB_DICT1,
              "subdict2" : SUB_DICT2,
              "list"     : LIST,
              "to_omit"  : "some/complicated/path/to/omit/"}

def test_value_to_string():
    """ test value to string conversion """
    assert _to_string(STR) == STR
    assert _to_string(FLOAT) == "1.230000e+00"
    assert _to_string(INT) == "1.024000e+03"
    with pytest.raises(ValueError, match="Values must be of one of the types int, float, str or bool, not 'NoneType'"):
        _to_string(None)

def test_dict_to_string():
    """ test conversion feasibility check """
    exp_string = "_str_text_int1.024000e+03_boolTrue_float1.230000e+00" \
                 "_subdict1_answer_yes_subsubdict_a1.000000e+00_b1.100000e+00_subdict2_A2.000000e+00_B2.200000e+00" \
                 "_list_1.100000e+00_2.200000e+00"
    string = dict_to_string(DICTIONARY, max_depth=5, omit_keys=["to_omit", "to_omit_in_subdict"])
    assert string == exp_string

    FAULTY_DICT = {1: "text"}
    with pytest.raises(ValueError, match="Keys must be of type str not 'int'"):
        dict_to_string(FAULTY_DICT, max_depth=4)

    FAULTY_DICT = {"text": None}
    with pytest.raises(ValueError, match="of one of the types int, float, str, bool, list or dict, not 'NoneType'"):
        dict_to_string(FAULTY_DICT, max_depth=4)
    with pytest.raises(ValueError, match="Level of nested dictionaries exceeds specified maximal depth 1"):
        dict_to_string(DICTIONARY, max_depth=1)
