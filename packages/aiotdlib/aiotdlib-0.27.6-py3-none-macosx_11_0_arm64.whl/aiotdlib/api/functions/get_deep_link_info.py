# =============================================================================== #
#                                                                                 #
#    This file has been generated automatically!! Do not change this manually!    #
#                                                                                 #
# =============================================================================== #
from __future__ import annotations

import typing

from pydantic import Field

from ..types.base import *


class GetDeepLinkInfo(BaseObject):
    """
    Returns information about a tg:// deep link. Use "tg://need_update_for_some_feature" or "tg:some_unsupported_feature" for testing. Returns a 404 error for unknown links. Can be called before authorization

    :param link: The link
    :type link: :class:`String`
    """

    ID: typing.Literal["getDeepLinkInfo"] = Field("getDeepLinkInfo", validation_alias="@type", alias="@type")
    link: String
