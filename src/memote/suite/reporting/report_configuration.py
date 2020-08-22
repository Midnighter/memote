# Copyright 2020, Moritz E. Beber.
# Copyright 2017 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
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


"""Configure the layout and scoring of test reports."""


import logging
from typing import Dict, List, Optional

from importlib_resources import open_text
from pydantic import BaseModel
from ruamel.yaml import YAML

import memote.suite.templates as templates


__all__ = ("ReportConfiguration",)


logger = logging.getLogger(__name__)
yaml = YAML(typ="safe")


class ReportCard(BaseModel):

    title: str
    cases: List[str]


class UnscoredSection(BaseModel):

    title: str
    cards: Dict[str, ReportCard]
    description: Optional[str] = None


class ScoredReportCard(ReportCard):

    weight: float = 1.0


class ScoredSection(UnscoredSection):

    cards: Dict[str, ScoredReportCard]


class Sections(BaseModel):

    scored: ScoredSection
    unscored: UnscoredSection


class ReportConfiguration(BaseModel):
    """Collect the metabolic model test suite results."""

    sections: Sections
    weights: Dict[str, float]

    @classmethod
    def load(cls, filename=None) -> "ReportConfiguration":
        """Load a test report configuration."""
        if filename is None:
            logger.debug("Loading default configuration.")
            with open_text(
                templates, "test_config.yml", encoding="utf-8"
            ) as file_handle:
                content = yaml.load(file_handle)
        else:
            logger.debug("Loading custom configuration '%s'.", filename)
            try:
                with open(filename, encoding="utf-8") as file_handle:
                    content = yaml.load(file_handle)
            except IOError as err:
                logger.error(
                    "Failed to load the custom configuration '%s'. Skipping.", filename
                )
                logger.debug(str(err))
                content = {}
        return cls.parse_obj(content)

    def merge(self, other: "ReportConfiguration") -> "ReportConfiguration":
        """Merge a custom configuration."""
        return type(self).parse_obj(self.dict().update(other.dict()))
