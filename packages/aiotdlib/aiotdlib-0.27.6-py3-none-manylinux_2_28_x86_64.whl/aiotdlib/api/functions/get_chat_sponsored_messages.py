# =============================================================================== #
#                                                                                 #
#    This file has been generated automatically!! Do not change this manually!    #
#                                                                                 #
# =============================================================================== #
from __future__ import annotations

import typing

from pydantic import Field

from ..types.base import *


class GetChatSponsoredMessages(BaseObject):
    """
    Returns sponsored messages to be shown in a chat; for channel chats and chats with bots only

    :param chat_id: Identifier of the chat
    :type chat_id: :class:`Int53`
    """

    ID: typing.Literal["getChatSponsoredMessages"] = Field(
        "getChatSponsoredMessages", validation_alias="@type", alias="@type"
    )
    chat_id: Int53
