# =============================================================================== #
#                                                                                 #
#    This file has been generated automatically!! Do not change this manually!    #
#                                                                                 #
# =============================================================================== #
from __future__ import annotations

import typing

from pydantic import Field

from ..types.base import *


class GetGroupCall(BaseObject):
    """
    Returns information about a group call

    :param group_call_id: Group call identifier
    :type group_call_id: :class:`Int32`
    """

    ID: typing.Literal["getGroupCall"] = Field("getGroupCall", validation_alias="@type", alias="@type")
    group_call_id: Int32
