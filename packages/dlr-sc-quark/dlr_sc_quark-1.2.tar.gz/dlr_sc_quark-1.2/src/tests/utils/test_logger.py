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

""" module for testing the logging helper functions """

import os
import shutil
import logging
from pathlib import Path

from quark.utils import get_logger


TEST_DIR = os.path.abspath(os.path.curdir) + "/"


def test_defaults():
    """ test default initialization """
    logger_default = get_logger(logger_name="logger_default")
    assert logger_default.name == "logger_default"
    assert logger_default.level == logging.INFO
    handlers = logger_default.handlers
    assert len(handlers) == 1
    handler = handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    assert handler.level == logging.INFO

def test_empty_logger():
    """ test empty logger """
    logger_empty = get_logger(logger_name="logger_empty",
                              log_level_console=logging.NOTSET)
    assert logger_empty.handlers == []

def test_threshold_log_level():
    """ test if threshold loglevel overwrites handler loglevels"""
    logger_threshold_loglevel = get_logger(logger_name="logger_threshold_loglevel",
                                           log_level=logging.WARNING)
    assert logger_threshold_loglevel.level == logging.WARNING

def test_file_name_default():
    """ test default values if file logging is enables"""
    logger_file_default = get_logger(logger_name="logger_file_default",
                                     log_level=logging.INFO,
                                     log_level_console=logging.ERROR,
                                     log_level_file=logging.INFO)
    handlers = logger_file_default.handlers
    assert len(handlers) == 2
    console_handler = handlers[0]
    file_handler = handlers[1]
    assert isinstance(console_handler, logging.StreamHandler)
    assert isinstance(file_handler, logging.FileHandler)
    assert console_handler.level == logging.ERROR
    assert file_handler.level == logging.INFO
    logfile = TEST_DIR + "logger_file_default.log"
    assert Path(file_handler.baseFilename) == Path(logfile)
    
    tear_down(logger_file_default, logfile)

def test_file_name_explicit():
    """ test explicit naming of logfile"""
    logger_file_explicit = get_logger(logger_name="logger_file_explicit",
                                      log_level=logging.INFO,
                                      log_level_console=logging.ERROR,
                                      log_level_file=logging.INFO,
                                      log_file="mylogfile.log")
    handlers = logger_file_explicit.handlers
    assert len(handlers) == 2
    file_handler = handlers[1]
    logfile = TEST_DIR + "mylogfile.log"
    assert isinstance(file_handler, logging.FileHandler)
    assert Path(file_handler.baseFilename) == Path(logfile)

    tear_down(logger_file_explicit, logfile)

def test_folder_and_file_name_explicit():
    """ test explicit naming of logfile and logfolder"""
    logger_folder_and_file_explicit = get_logger(logger_name="logger_folder_and_file_explicit",
                                                 log_level=logging.INFO,
                                                 log_level_console=logging.ERROR,
                                                 log_level_file=logging.INFO,
                                                 log_file="mylogfile.log",
                                                 log_folder=TEST_DIR + "mylogfolder/")
    handlers = logger_folder_and_file_explicit.handlers
    assert len(handlers) == 2
    file_handler = handlers[1]
    logfolder = TEST_DIR + "mylogfolder/"
    logfile = logfolder + "mylogfile.log"
    assert isinstance(file_handler, logging.FileHandler)
    assert Path(file_handler.baseFilename) == Path(logfile)

    tear_down(logger_folder_and_file_explicit, logfile, logfolder)

def test_folder_name_explicit():
    """ test explicit naming of logfolder but default nameing of logfile"""
    logger_folder_explicit = get_logger(logger_name="logger_folder_explicit",
                                        log_level=logging.INFO,
                                        log_level_console=logging.ERROR,
                                        log_level_file=logging.INFO,
                                        log_folder=TEST_DIR + "mylogfolder/")
    handlers = logger_folder_explicit.handlers
    assert len(handlers) == 2
    file_handler = handlers[1]
    logfolder = TEST_DIR + "mylogfolder/"
    logfile = logfolder + "logger_folder_explicit.log"
    assert isinstance(file_handler, logging.FileHandler)
    assert Path(file_handler.baseFilename) == Path(logfile)

    tear_down(logger_folder_explicit, logfile, logfolder)


def tear_down(logger, logfile, logfolder=None):
    """ closing handlers and removing file resp. folder """
    logger.close_all_handlers()
    assert os.path.exists(logfile)
    os.remove(logfile)
    if logfolder:
        assert os.path.exists(logfolder)
        shutil.rmtree(logfolder)
