# =============================================================================== #
#                                                                                 #
#    This file has been generated automatically!! Do not change this manually!    #
#                                                                                 #
# =============================================================================== #
from __future__ import annotations

import typing

from pydantic import Field

from ..types.base import *


class GetContacts(BaseObject):
    """
    Returns all contacts of the user
    """

    ID: typing.Literal["getContacts"] = Field("getContacts", validation_alias="@type", alias="@type")
