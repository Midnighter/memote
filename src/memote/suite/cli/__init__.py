# Copyright 2017 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""memote command line interface."""


import logging

import click

from memote.suite.cli.config import ConfigFileProcessor


logger = logging.getLogger(__name__)

try:
    CONTEXT_SETTINGS = {"default_map": ConfigFileProcessor.read_config()}
except click.BadParameter as error:
    logger.error(
        "Error in configuration file: %s\nAll configured values will be ignored!",
        str(error),
    )
    CONTEXT_SETTINGS = {}
