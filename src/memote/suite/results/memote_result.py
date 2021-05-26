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


"""Provide a collective access to a test suite result.."""


from datetime import datetime
from enum import Enum, unique
from platform import python_version, release, system  # noqa: F401
from typing import Dict, List, Optional, Tuple, Union

from depinfo import get_pkg_info
from pydantic import BaseModel, Field


__all__ = (
    "MemoteResult",
    "TestCaseOutcome",
    "TestCaseResult",
    "ParametrizedTestCaseResult",
    "MetaInformation",
    "GitCommitInfo",
)


@unique
class FormatType(Enum):
    """Define types for displaying a test result."""

    number = "number"
    count = "count"
    percent = "percent"
    raw = "raw"


@unique
class TestCaseOutcome(Enum):
    """Define the possible pytest test case outcomes."""

    Passed = "passed"
    Failed = "failed"
    Skipped = "skipped"


class GitCommitInfo(BaseModel):
    """Define git commit information."""

    hexsha: Optional[str] = None
    author: Optional[str] = None
    email: Optional[str] = None
    authored_on: Optional[datetime] = None


class MetaInformation(BaseModel):
    """Define the meta information."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    platform: str = Field(default_factory=system)
    release: str = Field(default_factory=release)  # noqa: F811
    python: str = Field(default_factory=python_version)
    packages: Dict[str, str] = get_pkg_info("memote")
    git_info: Optional[GitCommitInfo] = None


Scalar = Union[float, int, bool, str]
Equilibrator = Tuple[List[Tuple[str, float]], List[str], List[str], List[str]]
MinStoichiometry = List[List[str]]


class TestCaseResult(BaseModel):
    """Define the data model for a singular test case result."""

    title: str
    summary: str
    format_type: FormatType
    result: Optional[TestCaseOutcome] = None
    duration: Optional[float] = None
    message: Optional[str] = None
    metric: Optional[float] = None
    score: Optional[float] = None
    data: Optional[
        Union[Equilibrator, MinStoichiometry, List[Scalar], Dict, Scalar]
    ] = None


class ParametrizedTestCaseResult(BaseModel):
    """Define the data model for a parametrized test case result."""

    title: str
    summary: str
    format_type: FormatType
    result: Dict[str, TestCaseOutcome] = {}
    duration: Dict[str, float] = {}
    message: Dict[str, str] = {}
    metric: Dict[str, float] = {}
    score: Dict[str, float] = {}
    data: Dict[str, Optional[Union[Dict, List[Scalar], Scalar]]] = {}


class MemoteResult(BaseModel):
    """Define a MEMOTE result structure."""

    meta: MetaInformation = Field(default_factory=MetaInformation)
    tests: Dict[str, Union[ParametrizedTestCaseResult, TestCaseResult]] = {}
