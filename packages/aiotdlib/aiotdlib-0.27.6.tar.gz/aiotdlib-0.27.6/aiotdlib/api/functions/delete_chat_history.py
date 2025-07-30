# =============================================================================== #
#                                                                                 #
#    This file has been generated automatically!! Do not change this manually!    #
#                                                                                 #
# =============================================================================== #
from __future__ import annotations

import typing

from pydantic import Field

from ..types.base import *


class DeleteChatHistory(BaseObject):
    """
    Deletes all messages in the chat. Use chat.can_be_deleted_only_for_self and chat.can_be_deleted_for_all_users fields to find whether and how the method can be applied to the chat

    :param chat_id: Chat identifier
    :type chat_id: :class:`Int53`
    :param remove_from_chat_list: Pass true to remove the chat from all chat lists
    :type remove_from_chat_list: :class:`Bool`
    :param revoke: Pass true to delete chat history for all users
    :type revoke: :class:`Bool`
    """

    ID: typing.Literal["deleteChatHistory"] = Field("deleteChatHistory", validation_alias="@type", alias="@type")
    chat_id: Int53
    remove_from_chat_list: Bool = False
    revoke: Bool = False
