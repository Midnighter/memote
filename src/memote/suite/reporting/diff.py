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


"""Compare two or more models with one another side-by-side."""


from typing import Dict

from memote.suite.reporting.report import Report
from .report_configuration import ReportConfiguration
from ..results import MemoteResult
from ...utils import jsonify


class DiffReport(Report):
    """
    Render a report displaying the results of two or more models side-by-side.

    Attributes
    ----------
    diff_results : dict
        A map from model identifiers to `memote.MemoteResult` objects.
    configuration : memote.ReportConfiguration
        A memote configuration structure.

    """

    def __init__(self, diff_results: Dict[str, MemoteResult],
                 configuration: ReportConfiguration, **kwargs):
        """Initialize the data."""
        super().__init__(
            result=None, configuration=configuration, **kwargs
        )
        self._report_type = "diff"
        self.result = self.format_and_score_diff_data(diff_results)
        self.result.update(self.config)

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

    def format_and_score_diff_data(self, diff_results: Dict[str, MemoteResult]):
        """Reformat the api results to work with the front-end."""
        base = dict()
        meta = base.setdefault("meta", dict())
        tests = base.setdefault("tests", dict())
        score = base.setdefault("score", dict())
        for model_filename, result in diff_results.items():
            result_obj = result.dict()
            if meta == dict():
                meta = result_obj["meta"]
            for test_id, test_results in result_obj["tests"].items():
                tests.setdefault(test_id, dict())
                if tests[test_id] == dict():
                    tests[test_id]["summary"] = test_results["summary"]
                    tests[test_id]["title"] = test_results["title"]
                    tests[test_id]["format_type"] = test_results["format_type"]
                if isinstance(test_results["metric"], dict):
                    tests[test_id].setdefault("diff", dict())
                    for param in test_results["metric"]:
                        tests[test_id]["diff"].setdefault(param, list()).append(
                            {
                                "model": model_filename,
                                "data": test_results["data"].setdefault(param),
                                "duration": test_results["duration"].setdefault(param),
                                "message": test_results["message"].setdefault(param),
                                "metric": test_results["metric"].setdefault(param),
                                "result": test_results["result"].setdefault(param),
                            }
                        )
                else:
                    tests[test_id].setdefault("diff", list())
                    tests[test_id]["diff"].append(
                        {
                            "model": model_filename,
                            "data": test_results.setdefault("data"),
                            "duration": test_results.setdefault("duration"),
                            "message": test_results.setdefault("message"),
                            "metric": test_results.setdefault("metric"),
                            "result": test_results.setdefault("result"),
                        }
                    )
            self.result = result
            self.compute_score()
            score.setdefault("total_score", dict()).setdefault("diff", list())
            score.setdefault("sections", dict()).setdefault("diff", list())
            score["total_score"]["diff"].append(
                {
                    "model": model_filename,
                    "total_score": self.config.sections.scored.score
                }
            )
            for section in self.result["score"]["sections"]:
                section.update({"model": model_filename})
                score["sections"]["diff"].append(section)
        return base
