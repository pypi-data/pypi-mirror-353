# =============================================================================== #
#                                                                                 #
#    This file has been generated automatically!! Do not change this manually!    #
#                                                                                 #
# =============================================================================== #
from __future__ import annotations

import typing

from pydantic import Field

from ..types.base import *

from ..types.all import (
    DraftMessage,
)


class SetChatDraftMessage(BaseObject):
    """
    Changes the draft message in a chat

    :param chat_id: Chat identifier
    :type chat_id: :class:`Int53`
    :param message_thread_id: If not 0, the message thread identifier in which the draft was changed
    :type message_thread_id: :class:`Int53`
    :param draft_message: New draft message; pass null to remove the draft. All files in draft message content must be of the type inputFileLocal. Media thumbnails and captions are ignored, defaults to None
    :type draft_message: :class:`DraftMessage`, optional
    """

    ID: typing.Literal["setChatDraftMessage"] = Field("setChatDraftMessage", validation_alias="@type", alias="@type")
    chat_id: Int53
    message_thread_id: Int53 = 0
    draft_message: typing.Optional[DraftMessage] = None
