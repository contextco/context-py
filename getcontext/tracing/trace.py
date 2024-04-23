from typing import Any

from getcontext.generated.models import Evaluator
from getcontext import ContextAPI
from getcontext.token import Credential
from getcontext.tracing._helpers import context_API_key
from langsmith.run_trees import RunTree


class Trace:
    """
    Represents a trace object used for adding evaluators to spans in a run tree.

    Args:
        result (Any): The result of the trace.
        run_tree (RunTree): The run tree of the trace.
    """

    # known key, which is interpreted on the server side
    CONTEXT_AI_OPTIONS = "context_ai_options"

    def __init__(self, result: Any, run_tree: RunTree):
        self.result = result
        self.run_tree = run_tree

        self.context_client = ContextAPI(credential=Credential(context_API_key()))

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

        langsmith_run.patch()

    def evaluate(self):
        """
        Evaluates the trace by sending it to the server for evaluation.

        Returns:
            dict: The evaluation results.
        """
        raise NotImplementedError("Not implemented yet.")

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
