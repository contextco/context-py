

class ContextException(Exception):
    pass


class EvaluationsFailedError(ContextException):
    """
    Evaluations did not succeed.
    """
    pass


class InternalContextError(ContextException):
    """
    An error occurred during evaluation.
    """
    pass
