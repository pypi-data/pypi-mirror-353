# =============================================================================== #
#                                                                                 #
#    This file has been generated automatically!! Do not change this manually!    #
#                                                                                 #
# =============================================================================== #
from __future__ import annotations

import typing

from pydantic import Field

from ..types.base import *


class ReadAllChatMentions(BaseObject):
    """
    Marks all mentions in a chat as read

    :param chat_id: Chat identifier
    :type chat_id: :class:`Int53`
    """

    ID: typing.Literal["readAllChatMentions"] = Field("readAllChatMentions", validation_alias="@type", alias="@type")
    chat_id: Int53
