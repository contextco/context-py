# coding=utf-8
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator (autorest: 3.9.7, generator: @autorest/python@6.14.3)
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from ._operations import ContextAPIOperationsMixin
from ._operations import EvaluationsOperations
from ._operations import LogOperations
from ._operations import UpdateOperations

from ._patch import __all__ as _patch_all
from ._patch import *  # pylint: disable=unused-wildcard-import
from ._patch import patch_sdk as _patch_sdk

__all__ = [
    "ContextAPIOperationsMixin",
    "EvaluationsOperations",
    "LogOperations",
    "UpdateOperations",
]
__all__.extend([p for p in _patch_all if p not in __all__])
_patch_sdk()
