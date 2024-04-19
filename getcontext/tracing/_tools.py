import inspect
import os

from langsmith.run_helpers import get_current_run_tree
from langsmith import traceable
from getcontext.tracing._helpers import modified_environ
from getcontext.tracing.trace import Trace


def capture_trace(func, *args, **kwargs):
    """
    Capture a trace of the given function execution.

    Args:
        func: The function to capture the trace for.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        The captured trace.

    Raises:
        TypeError: If the given argument is not callable.
    """

    if not callable(func):
        raise TypeError("The given argument is not callable.")

    parent_function_name = inspect.stack()[1].function

    @traceable(run_type='chain', name=parent_function_name)
    def __user_function_wrapper(func, *args, **kwargs):
        results = func(*args, **kwargs)
        run_tree = get_current_run_tree()  # run_tree is only available while in a traceable context

        # We do not want to return run_tree or Trace() as this will be visible to the user in the UI
        # TODO: find a better way of doing this...
        Trace.HACKY_CONSTANT = Trace(results, run_tree)

    # run function with temporarily modified environmental variables
    with modified_environ(**__context_enviromental_variables()):
        __user_function_wrapper(func, *args, **kwargs)

    return Trace.HACKY_CONSTANT


def __context_enviromental_variables():
    return {
        "LANGCHAIN_ENDPOINT": "http://api.localtest.me:3000/api/v1/evaluations/traces",
        "LANGCHAIN_API_KEY": os.environ.get("GETCONTEXT_TOKEN"),
        "LANGCHAIN_TRACING_V2": "true",
    }
