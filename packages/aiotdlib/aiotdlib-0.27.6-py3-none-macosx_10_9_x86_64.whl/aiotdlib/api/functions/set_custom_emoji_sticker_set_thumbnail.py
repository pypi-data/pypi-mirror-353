# =============================================================================== #
#                                                                                 #
#    This file has been generated automatically!! Do not change this manually!    #
#                                                                                 #
# =============================================================================== #
from __future__ import annotations

import typing

from pydantic import Field

from ..types.base import *


class SetCustomEmojiStickerSetThumbnail(BaseObject):
    """
    Sets a custom emoji sticker set thumbnail

    :param name: Sticker set name. The sticker set must be owned by the current user
    :type name: :class:`String`
    :param custom_emoji_id: Identifier of the custom emoji from the sticker set, which will be set as sticker set thumbnail; pass 0 to remove the sticker set thumbnail
    :type custom_emoji_id: :class:`Int64`
    """

    ID: typing.Literal["setCustomEmojiStickerSetThumbnail"] = Field(
        "setCustomEmojiStickerSetThumbnail", validation_alias="@type", alias="@type"
    )
    name: String
    custom_emoji_id: Int64
