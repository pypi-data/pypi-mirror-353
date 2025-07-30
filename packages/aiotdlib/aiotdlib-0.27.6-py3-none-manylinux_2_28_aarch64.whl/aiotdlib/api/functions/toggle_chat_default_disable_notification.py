# =============================================================================== #
#                                                                                 #
#    This file has been generated automatically!! Do not change this manually!    #
#                                                                                 #
# =============================================================================== #
from __future__ import annotations

import typing

from pydantic import Field

from ..types.base import *


class ToggleChatDefaultDisableNotification(BaseObject):
    """
    Changes the value of the default disable_notification parameter, used when a message is sent to a chat

    :param chat_id: Chat identifier
    :type chat_id: :class:`Int53`
    :param default_disable_notification: New value of default_disable_notification
    :type default_disable_notification: :class:`Bool`
    """

    ID: typing.Literal["toggleChatDefaultDisableNotification"] = Field(
        "toggleChatDefaultDisableNotification", validation_alias="@type", alias="@type"
    )
    chat_id: Int53
    default_disable_notification: Bool
