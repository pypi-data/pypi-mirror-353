# =============================================================================== #
#                                                                                 #
#    This file has been generated automatically!! Do not change this manually!    #
#                                                                                 #
# =============================================================================== #
from __future__ import annotations

import typing

from pydantic import Field

from ..types.base import *


class CreateSupergroupChat(BaseObject):
    """
    Returns an existing chat corresponding to a known supergroup or channel

    :param supergroup_id: Supergroup or channel identifier
    :type supergroup_id: :class:`Int53`
    :param force: Pass true to create the chat without a network request. In this case all information about the chat except its type, title and photo can be incorrect
    :type force: :class:`Bool`
    """

    ID: typing.Literal["createSupergroupChat"] = Field("createSupergroupChat", validation_alias="@type", alias="@type")
    supergroup_id: Int53
    force: Bool = False
