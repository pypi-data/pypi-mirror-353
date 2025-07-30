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
    MessageSender,
)


class GetStarRevenueStatistics(BaseObject):
    """
    Returns detailed Telegram Star revenue statistics

    :param owner_id: Identifier of the owner of the Telegram Stars; can be identifier of the current user, an owned bot, or a supergroup or a channel chat with supergroupFullInfo.can_get_star_revenue_statistics == true
    :type owner_id: :class:`MessageSender`
    :param is_dark: Pass true if a dark theme is used by the application
    :type is_dark: :class:`Bool`
    """

    ID: typing.Literal["getStarRevenueStatistics"] = Field(
        "getStarRevenueStatistics", validation_alias="@type", alias="@type"
    )
    owner_id: MessageSender
    is_dark: Bool = False
