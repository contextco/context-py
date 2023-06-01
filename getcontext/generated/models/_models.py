# coding=utf-8
# pylint: disable=too-many-lines
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator (autorest: 3.9.6, generator: @autorest/python@6.4.15)
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

import datetime
import sys
from typing import Any, List, Optional, TYPE_CHECKING, Union

from .. import _serialization

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from .. import models as _models
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object


class Conversation(_serialization.Model):
    """Conversation.

    :ivar messages:
    :vartype messages: list[~context_api.models.Message]
    :ivar metadata: Any object.
    :vartype metadata: JSON
    """

    _attribute_map = {
        "messages": {"key": "messages", "type": "[Message]"},
        "metadata": {"key": "metadata", "type": "object"},
    }

    def __init__(
        self, *, messages: Optional[List["_models.Message"]] = None, metadata: Optional[JSON] = None, **kwargs: Any
    ) -> None:
        """
        :keyword messages:
        :paramtype messages: list[~context_api.models.Message]
        :keyword metadata: Any object.
        :paramtype metadata: JSON
        """
        super().__init__(**kwargs)
        self.messages = messages
        self.metadata = metadata


class Message(_serialization.Model):
    """Message.

    All required parameters must be populated in order to send to Azure.

    :ivar role: Required. Known values are: "system", "assistant", and "user".
    :vartype role: str or ~context_api.models.MessageRole
    :ivar message: Required.
    :vartype message: str
    :ivar event_timestamp:
    :vartype event_timestamp: ~datetime.datetime
    :ivar rating: Known values are: -1, 0, and 1.
    :vartype rating: int or ~context_api.models.Rating
    """

    _validation = {
        "role": {"required": True},
        "message": {"required": True},
    }

    _attribute_map = {
        "role": {"key": "role", "type": "str"},
        "message": {"key": "message", "type": "str"},
        "event_timestamp": {"key": "event_timestamp", "type": "iso-8601"},
        "rating": {"key": "rating", "type": "int"},
    }

    def __init__(
        self,
        *,
        role: Union[str, "_models.MessageRole"],
        message: str,
        event_timestamp: Optional[datetime.datetime] = None,
        rating: Optional[Union[int, "_models.Rating"]] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword role: Required. Known values are: "system", "assistant", and "user".
        :paramtype role: str or ~context_api.models.MessageRole
        :keyword message: Required.
        :paramtype message: str
        :keyword event_timestamp:
        :paramtype event_timestamp: ~datetime.datetime
        :keyword rating: Known values are: -1, 0, and 1.
        :paramtype rating: int or ~context_api.models.Rating
        """
        super().__init__(**kwargs)
        self.role = role
        self.message = message
        self.event_timestamp = event_timestamp
        self.rating = rating


class PathsLi5TynApiV1LogConversationPostRequestbodyContentApplicationJsonSchema(_serialization.Model):
    """PathsLi5TynApiV1LogConversationPostRequestbodyContentApplicationJsonSchema.

    :ivar conversation:
    :vartype conversation: ~context_api.models.Conversation
    """

    _attribute_map = {
        "conversation": {"key": "conversation", "type": "Conversation"},
    }

    def __init__(self, *, conversation: Optional["_models.Conversation"] = None, **kwargs: Any) -> None:
        """
        :keyword conversation:
        :paramtype conversation: ~context_api.models.Conversation
        """
        super().__init__(**kwargs)
        self.conversation = conversation
