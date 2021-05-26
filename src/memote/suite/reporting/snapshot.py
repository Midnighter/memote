# -*- coding: utf-8 -*-

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


"""Render a one-time model report."""


from ...utils import jsonify
from .report import Report
from .snapshot_result import SnapshotResult


class SnapshotReport(Report):
    """
    Render a one-time report from the given model results.

    Attributes
    ----------
    result : memote.MemoteResult
        The dictionary structure of results.
    configuration : memote.MemoteConfiguration
        A memote configuration structure.

    """

    def __init__(self, **kwargs):
        """Initialize the snapshot report."""
        super(SnapshotReport, self).__init__(**kwargs)
        self._report_type = "snapshot"
        self.determine_miscellaneous_tests()
        self.compute_score()

    def render_json(self, pretty=False):
        """
        Render the snapshot report results as JSON.

        Parameters
        ----------
        pretty : bool, optional
            Whether to format the resulting JSON in a more legible way (default False).

        """
        return jsonify(
            SnapshotResult(
                meta=self.result.meta,
                tests=self.result.tests,
                sections=self.config.sections,
                weights=self.config.weights,
            ),
            pretty=pretty,
        )
