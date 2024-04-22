import inspect
import os

from langsmith.run_helpers import get_current_run_tree
from langsmith import traceable
from getcontext.tracing._helpers import modified_environ
from getcontext.tracing.trace import Trace

# TASK: Try capture gloabl langsmith client, change on begin capture trace and end capture trace
# Looks like clients try to connect on instantiation, unknown if there is a way to override this

DEVELOPMENT_ENDPOINT = "http://api.localtest.me:3000/api/v1/evaluations/traces"
PRODUCTION_ENDPOINT = "https://with.context.ai/api/v1/evaluations/traces"


def capture_trace(func, *args, **kwargs) -> Trace:
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

    trace = None

    @traceable(run_type='chain', name=__find_test_parent_function_name())
    def __user_function_wrapper(func, *args, **kwargs):     
        nonlocal trace
        results = func(*args, **kwargs)
        run_tree = get_current_run_tree()

        trace = Trace(results, run_tree) 

    # run function with temporarily modified environmental variables
    with modified_environ(**__context_enviromental_variables()):
        __user_function_wrapper(func, *args, **kwargs)

    return trace


def __context_enviromental_variables():
    return {
        "LANGCHAIN_ENDPOINT": __context_endpoint(),
        "LANGCHAIN_API_KEY": __context_API_key(),
        "LANGCHAIN_TRACING_V2": "true",
    }


def __find_test_parent_function_name():
    # iterate through the stack to find the parent function name
    for frame in inspect.stack():
        function_name = frame.function.lower()

        if function_name.startswith('test') or function_name.endswith('test'):
            return frame.function
        
    raise ValueError("No test function found in stack. Make sure your test name starts or ends with 'test'.")


def __context_endpoint():
    return DEVELOPMENT_ENDPOINT if os.environ.get("CONTEXT_SDK_DEV") else PRODUCTION_ENDPOINT


def __context_API_key():
    return os.environ.get("GETCONTEXT_TOKEN")
