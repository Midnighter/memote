# Copyright 2021, Moritz E. Beber.
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


"""Provide a snapshot report that combines test outcomes and configuration."""


from typing import Dict, Union

from pydantic import BaseModel, Field

from ..results import MetaInformation, ParametrizedTestCaseResult, TestCaseResult
from .report_configuration import Sections


__all__ = ("SnapshotResult",)


class SnapshotResult(BaseModel):
    """Collect the metabolic model test suite results and the report configuration."""

    meta: MetaInformation = Field(default_factory=MetaInformation)
    tests: Dict[str, Union[ParametrizedTestCaseResult, TestCaseResult]] = {}
    sections: Sections
    weights: Dict[str, float]
