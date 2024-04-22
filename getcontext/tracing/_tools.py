import inspect
import os
from typing import Callable

from langsmith.run_helpers import get_current_run_tree
from langsmith import traceable
from langsmith import client as ls_client
from getcontext.tracing._helpers import modified_environ
from getcontext.tracing.trace import Trace

# TASK: Try capture gloabl langsmith client, change on begin capture trace and end capture trace
# Looks like clients try to connect on instantiation, unknown if there is a way to override this

CONTEXT_TRACE_ENDPOINT = "https://with.context.ai/api/v1/evaluations/traces"


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


def dynamic_traceable(func: Callable,
                      run_type: ls_client.RUN_TYPE_T = 'chain',
                      name: str = None) -> Callable:
    """
    Dynamically create a traceable function.
    
    Useful when you want to dynamically name a trace or you don't have access to the function definition (e.g. openai SDK functions)

    Args:
        func (Callable): The function to be traced.
        run_type (ls_client.RUN_TYPE_T, optional): The type of tracing to be applied. Defaults to 'chain'.
        name (str, optional): The name of the trace. Defaults to function name.

    Returns:
        Callable: The wrapped function.
        
    Example:
    .. code-block:: python
        import openai
        from getcontext.tracing import dynamic_traceable, capture_trace, Evaluator
        
        openai_client = openai.Client()
        openai_chat = dynamic_traceable(
            openai_client.chat.completions.create,
            run_type='llm',
            name='openai_hello_world')
        
        trace = capture_trace(
            openai_chat,
            messages=[{"role": "user", "content": "Tell me a fun fact about the world."}],
            model="gpt-3.5-turbo")
            
        evaluator = Evaluator('golden_response', {'golden_response': 'Hello, world'})

        trace.add_evaluator('openai_hello_world', evaluator)
        trace.evaluate()
    """
    if not callable(func):
        raise TypeError("func argument is not callable.")
    
    if name is None:
        name = func.__name__

    @traceable(run_type=run_type, name=name)
    def wrapper_fn(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper_fn.__name__ = name

    return wrapper_fn


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
    return os.environ.get("CONTEXT_TRACE_ENDPOINT", CONTEXT_TRACE_ENDPOINT)


def __context_API_key():
    return os.environ.get("GETCONTEXT_TOKEN")
