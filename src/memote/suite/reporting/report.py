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


"""Provide an abstract report base class that sets the interface."""


import logging
from string import Template
from typing import TYPE_CHECKING, Set

from importlib_resources import read_text
from pandas import DataFrame

import memote.suite.templates as templates
from memote.suite.reporting.report_configuration import ReportCard
from memote.utils import jsonify

from ..results import MemoteResult, ParametrizedTestCaseResult


if TYPE_CHECKING:
    from memote import ReportConfiguration


logger = logging.getLogger(__name__)


class Report:
    """
    Determine the abstract report interface.

    Attributes
    ----------
    result : memote.MemoteResult
        The dictionary structure of results.
    configuration : memote.MemoteConfiguration
        A memote configuration structure.

    """

    def __init__(
        self, result: "MemoteResult", configuration: "ReportConfiguration", **kwargs
    ):
        """
        Fuse a collective result with a report configuration.

        Parameters
        ----------
        result : memote.MemoteResult
            The dictionary structure of results.
        configuration : memote.ReportConfiguration
            A memote report configuration structure.

        """
        super(Report, self).__init__(**kwargs)
        self.result = result
        self.config = configuration
        self._report_type = None
        self._template = Template(read_text(templates, "index.html", encoding="utf-8"))

    def render_json(self, pretty=False):
        """
        Render the report results as JSON.

        Parameters
        ----------
        pretty : bool, optional
            Whether to format the resulting JSON in a more legible way (default False).

        """
        # TODO: Create combined results + config object.
        return jsonify(dict(self.result.dict(), **self.config.dict()), pretty=pretty)

    def render_html(self):
        """Render an HTML report."""
        return self._template.safe_substitute(
            report_type=self._report_type, results=self.render_json()
        )

    def get_configured_tests(self) -> Set[str]:
        """Get tests explicitly configured."""
        scored_tests = {
            test
            for card in self.config.sections.scored.cards.values()
            for test in card.cases
        }
        unscored_tests = {
            test
            for card in self.config.sections.unscored.cards.values()
            for test in card.cases
        }
        shared = scored_tests.intersection(unscored_tests)
        if shared:
            logger.error(
                "Bad report configuration. The following test(s) appear both in the "
                "scored and unscored section: %s",
                ", ".join(shared),
            )
        return scored_tests.union(unscored_tests)

    def determine_miscellaneous_tests(self) -> None:
        """
        Identify tests not explicitly configured in test organization.

        List them as an additional card called `Misc`, which is where they will
        now appear in the report.

        """
        unconfigured_tests = set(self.result.tests) - self.get_configured_tests()
        if unconfigured_tests:
            misc = self.config.sections.unscored.cards.setdefault(
                "misc", ReportCard(title="Misc. Tests", cases=[])
            )
            misc.cases.extend(unconfigured_tests)

    def compute_score(self):
        """Calculate the overall test score using the configuration."""
        scores = DataFrame({"score": 0.0, "max": 1.0}, index=sorted(self.result.tests))
        # Calculate the scores for each test individually.
        for test, result in self.result.tests.items():
            # Test metric may be a dictionary for a parametrized test.
            if isinstance(result, ParametrizedTestCaseResult):
                total = 0.0
                for key, value in result.metric.items():
                    value = 1.0 - value
                    total += value
                    result.score[key] = value
                # For some reason there are parametrized tests without cases.
                if len(result.metric) == 0:
                    score = 0.0
                else:
                    score = total / len(result.metric)
            else:
                result.score = 1.0 - result.metric
                score = result.score
            scores.at[test, "score"] = score
            scores.loc[test, :] *= self.config.weights.get(test, 1.0)
        score = 0.0
        maximum = 0.0
        # Calculate the scores for each section considering the individual test
        # case scores.
        for card_id, card in self.config.sections.scored.cards.items():
            if not card.cases:
                continue
            card_score = scores.loc[card.cases, "score"].sum()
            card_total = scores.loc[card.cases, "max"].sum()
            card.score = card_score / card_total
            score += card_score * card.weight
            maximum += card_total * card.weight
        self.config.sections.scored.score = score / maximum
