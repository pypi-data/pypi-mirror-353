# =============================================================================== #
#                                                                                 #
#    This file has been generated automatically!! Do not change this manually!    #
#                                                                                 #
# =============================================================================== #
from __future__ import annotations

import typing

from pydantic import Field

from ..types.base import *


class GetDefaultChatPhotoCustomEmojiStickers(BaseObject):
    """
    Returns default list of custom emoji stickers for placing on a chat photo
    """

    ID: typing.Literal["getDefaultChatPhotoCustomEmojiStickers"] = Field(
        "getDefaultChatPhotoCustomEmojiStickers", validation_alias="@type", alias="@type"
    )
