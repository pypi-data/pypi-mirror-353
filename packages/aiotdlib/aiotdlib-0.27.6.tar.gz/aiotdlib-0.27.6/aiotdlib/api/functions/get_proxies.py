# =============================================================================== #
#                                                                                 #
#    This file has been generated automatically!! Do not change this manually!    #
#                                                                                 #
# =============================================================================== #
from __future__ import annotations

import typing

from pydantic import Field

from ..types.base import *


class GetProxies(BaseObject):
    """
    Returns the list of proxies that are currently set up. Can be called before authorization
    """

    ID: typing.Literal["getProxies"] = Field("getProxies", validation_alias="@type", alias="@type")
