# =============================================================================== #
#                                                                                 #
#    This file has been generated automatically!! Do not change this manually!    #
#                                                                                 #
# =============================================================================== #
from __future__ import annotations

import typing

from pydantic import Field

from ..types.base import *


class RequestAuthenticationPasswordRecovery(BaseObject):
    """
    Requests to send a 2-step verification password recovery code to an email address that was previously set up. Works only when the current authorization state is authorizationStateWaitPassword
    """

    ID: typing.Literal["requestAuthenticationPasswordRecovery"] = Field(
        "requestAuthenticationPasswordRecovery", validation_alias="@type", alias="@type"
    )
