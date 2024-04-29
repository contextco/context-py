from typing import Any
import time
import logging

from getcontext.generated.models import (
    Evaluator,
    EvaluationsRunResponse,
    EvaluationReasoning,
)
from getcontext.generated.models._enums import EvaluationsRunResponseStatus
from getcontext import ContextAPI
from getcontext.token import Credential
from getcontext.tracing._helpers import context_API_key, context_domain, enforce_https
from getcontext.tracing.exceptions import EvaluationsFailedError, InternalContextError
from langsmith.run_trees import RunTree


class Trace:
    """
    Represents a trace object used for adding evaluators to spans in a run tree.

    Args:
        result (Any): The result of the trace.
        run_tree (RunTree): The run tree of the trace.
    """

    CONTEXT_AI_OPTIONS = "context_ai_options"  # known key, which is interpreted on the server side
    POLLING_INTERVAL = 0.75  # time in seconds to wait between polling

    def __init__(self, result: Any, run_tree: RunTree):
        self.result = result
        self.run_tree = run_tree

        self.enforce_https = enforce_https()
        self.logger = logging.getLogger("context-ai")

        self.context_client = ContextAPI(
            credential=Credential(context_API_key()),
            endpoint=context_domain(),
        )

    def add_evaluator(self, span_name: str, evaluator: Evaluator):
        """
        Adds an evaluator to the specified span in the run tree.

        Args:
            span_name (str): The name of the span to add the evaluator to.
            evaluator (Evaluator): The evaluator to add to the span.

        Raises:
            ValueError: If the span_name is the same as the unit test function name.
            ValueError: If no run tree is found.
            ValueError: If no matching spans are found.
            ValueError: If multiple matching spans are found and a unique span name is not specified.

        Example:
        .. code-block:: python
            from getcontext.tracing import capture_trace, Evaluator

            # Capture a trace
            trace = capture_trace(my_function)

            # Create an evaluator
            evaluator = Evaluator(
                evaluator="golden_response",
                options={
                    "golden_response": "[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]",
                    "capitalization": "full",
                    "punctuation": "agnostic",
                    "whitespace": "full"
                }
            )

            # Add the evaluator to the span named "my_span"
            trace.add_evaluator("my_span", evaluator)
        """
        if span_name == self.run_tree.name:
            raise ValueError("Cannot add evaluator to unit test function.")

        langsmith_run = self._find_run(span_name)
        if langsmith_run.extra is None:
            langsmith_run.extra = {}
        context_ai_options = langsmith_run.extra.setdefault(
            Trace.CONTEXT_AI_OPTIONS, {}
        )
        evaluators_options = context_ai_options.setdefault("evaluators", [])
        evaluators_options.append(evaluator)

        self.run_tree.client.tracing_queue.join()

        langsmith_run.patch()

    def evaluate(self) -> EvaluationsRunResponse:
        """
        Evaluates the trace by running the evaluations on the context client.

        Returns:
            EvaluationsRunResponse: The response of the evaluations.

        Raises:
            InternalContextError: If the evaluation fails.
            EvaluationsFailedError: If there are any failed, inconclusive, or partially passed evaluations.
        """
        self.logger.info("Awaiting trace updates completion...")
        self.run_tree.client.tracing_queue.join()

        self.logger.info("Requesting evaluation run.")
        run_details = self.context_client.evaluations.run(
            body={
                "test_set_name": str(self.run_tree.trace_id),
                "version": "1",
                "iterations": 1,
            },
            enforce_https=self.enforce_https,
        )

        results = self._poll_for_result(run_details.data.run_id)

        if results.status == EvaluationsRunResponseStatus.ERRORED:
            raise InternalContextError(f"Evaluation failed:\n {results.as_dict()}")

        failed_evaluation_msgs = self._parse_evaluation_results(results)
        failed_msg = self._create_evaluation_fail_msg(failed_evaluation_msgs)

        if failed_msg:
            raise EvaluationsFailedError(failed_msg)

        return results

    def _parse_evaluation_results(self, results: EvaluationsRunResponse):
        outcome_map = {
            "positive": "passed",
            "negative": "failed",
            "partially_passed": "partially passed",
            "inconclusive": "inconclusive",
        }

        failed_evaluation_msgs = []

        for result in results.results:
            test_case_name = result.test_case.name
            for evaluation in result.evaluations:
                msg = (
                    f"{self._symbol(evaluation.outcome == 'positive')} {test_case_name}: "
                    f"Evaluation {outcome_map.get(evaluation.outcome)} for "
                    f"{evaluation.evaluator_name}: {self._create_reasoning_msg(evaluation.reasoning)}"
                )

                if evaluation.outcome != "positive":
                    self.logger.warning(f"\n{msg}")
                    failed_evaluation_msgs.append(msg)
                else:
                    self.logger.info(f"\n{msg}")
        return failed_evaluation_msgs

    def _create_reasoning_msg(self, reasoning: EvaluationReasoning):
        if reasoning is None:
            return ""

        msg = ""
        for res in reasoning.result:
            msg += f"\n\t{self._symbol(res.verdict)} {res.reason}"

        return msg

    def _symbol(self, success: bool):
        tick, x_mark = "\u2705", "\u274C"
        return tick if success else x_mark

    def _create_evaluation_fail_msg(self, failed_evaluation_msgs):
        if failed_evaluation_msgs:
            joined_failed_evaluations = "\n\n".join(failed_evaluation_msgs)
            return f"\n\nEvaluation failed:\n {joined_failed_evaluations}"

    def _poll_for_result(self, run_id: str) -> EvaluationsRunResponse:
        self.logger.info(f"Beginning evaluation polling ({Trace.POLLING_INTERVAL} cadence).")
        result = self.context_client.evaluations.result(
            id=run_id, enforce_https=self.enforce_https
        )
        while result.status in ["running", "pending"]:
            time.sleep(Trace.POLLING_INTERVAL)
            result = self.context_client.evaluations.result(
                id=run_id, enforce_https=self.enforce_https
            )

        self.logger.info(f"Evaluation complete: {result.status}")
        return result

    def _find_run(self, span_name: str) -> RunTree:
        """
        Finds the run with the specified span_name in the run tree.

        Args:
            span_name (str): The name of the run to find.

        Returns:
            RunTree: The matching run.

        Raises:
            ValueError: If no run tree is found.
            ValueError: If no matching spans are found.
            ValueError: If multiple matching spans are found and a unique span_name is not specified.
        """
        if self.run_tree is None:
            raise ValueError("No run tree found.")

        matching_runs = self._find_run_helper(self.run_tree, span_name)

        if len(matching_runs) == 0:
            raise ValueError("No matching spans found.")
        elif len(matching_runs) > 1:
            raise ValueError(
                "Multiple matching spans found. You must specify a unique span name."
            )

        return matching_runs[0]

    def _find_run_helper(self, run_tree: RunTree, span_name: str) -> RunTree:
        """
        Helper function to recursively find the run with the specified span_name in the run tree.

        Args:
            run_tree (RunTree): The current run tree to search.
            span_name (str): The name of the run to find.

        Returns:
            RunTree: The matching run.
        """
        # recursion is fine here because we explicitly don't allow complicated deep trees server side
        matching_runs = []
        for run in run_tree.child_runs:
            if run.name == span_name:
                matching_runs.append(run)
            else:
                matching_runs += self._find_run_helper(run, span_name)

        return matching_runs
