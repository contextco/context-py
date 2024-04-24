

class ContextException(Exception):
    pass


class EvaluationException(ContextException):
    """
    Evaluations did not succeed.
    """
    pass


class EvaluationError(ContextException):
    """
    An error occurred during evaluation.
    """
    pass
