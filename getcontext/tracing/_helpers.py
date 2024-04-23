import contextlib
import os


CONTEXT_DOMAIN = "https://api.context.ai"


# Kindly stolen from https://stackoverflow.com/questions/2059482/temporarily-modify-the-current-processs-environment
@contextlib.contextmanager
def modified_environ(*remove, **update):
    """
    Temporarily updates the ``os.environ`` dictionary in-place.

    The ``os.environ`` dictionary is updated in-place so that the modification
    is sure to work in all situations.

    :param remove: Environment variables to remove.
    :param update: Dictionary of environment variables and values to add/update.
    """
    env = os.environ
    update = update or {}
    remove = remove or []

    # List of environment variables being updated or removed.
    stomped = (set(update.keys()) | set(remove)) & set(env.keys())
    # Environment variables and values to restore on exit.
    update_after = {k: env[k] for k in stomped}
    # Environment variables and values to remove on exit.
    remove_after = frozenset(k for k in update if k not in env)

    try:
        env.update(update)
        [env.pop(k, None) for k in remove]
        yield
    finally:
        env.update(update_after)
        [env.pop(k) for k in remove_after]


def context_API_key() -> str:
    """
    Retrieves the API key for the GetContext service from the environment variables.

    Returns:
        str: The API key for the GetContext service.

    Raises:
        KeyError: If the GETCONTEXT_TOKEN environment variable is not set.
    """
    context_token = os.environ.get("GETCONTEXT_TOKEN")
    if context_token is None:
        raise KeyError("GETCONTEXT_TOKEN is not set in the environment variables.")

    return context_token


def context_endpoint() -> str:
    """
    Retrieves the context trace endpoint from the environment variable or the default value.

    Returns:
        str: The context trace endpoint.
    """
    return f"{context_domain()}/api/v1/evaluations/traces"


def context_domain() -> str:
    """
    Retrieves the context domain from the environment variable or the default value.

    Returns:
        str: The context domain.
    """
    return os.environ.get("CONTEXT_DOMAIN", CONTEXT_DOMAIN)


def enforce_https() -> bool:
    """
    Retrieves the enforce_https flag from the environment variable or the default value.

    Returns:
        bool: The enforce_https flag.
    """
    return context_domain().startswith("https")
