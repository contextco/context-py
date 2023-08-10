# coding=utf-8
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator (autorest: 3.9.6, generator: @autorest/python@6.7.2)
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from ._models import Conversation
from ._models import Message
from ._models import PathsLi5TynApiV1LogConversationPostRequestbodyContentApplicationJsonSchema
from ._models import PathsRai0VpApiV1LogConversationUpsertPostRequestbodyContentApplicationJsonSchema

from ._enums import MessageRole
from ._enums import Rating
from ._patch import __all__ as _patch_all
from ._patch import *  # pylint: disable=unused-wildcard-import
from ._patch import patch_sdk as _patch_sdk

__all__ = [
    "Conversation",
    "Message",
    "PathsLi5TynApiV1LogConversationPostRequestbodyContentApplicationJsonSchema",
    "PathsRai0VpApiV1LogConversationUpsertPostRequestbodyContentApplicationJsonSchema",
    "MessageRole",
    "Rating",
]
__all__.extend([p for p in _patch_all if p not in __all__])
_patch_sdk()
