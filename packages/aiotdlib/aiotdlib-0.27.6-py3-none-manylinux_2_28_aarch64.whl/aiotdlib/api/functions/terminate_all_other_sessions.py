# =============================================================================== #
#                                                                                 #
#    This file has been generated automatically!! Do not change this manually!    #
#                                                                                 #
# =============================================================================== #
from __future__ import annotations

import typing

from pydantic import Field

from ..types.base import *


class TerminateAllOtherSessions(BaseObject):
    """
    Terminates all other sessions of the current user
    """

    ID: typing.Literal["terminateAllOtherSessions"] = Field(
        "terminateAllOtherSessions", validation_alias="@type", alias="@type"
    )
