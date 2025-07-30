# =============================================================================== #
#                                                                                 #
#    This file has been generated automatically!! Do not change this manually!    #
#                                                                                 #
# =============================================================================== #
from __future__ import annotations

import typing

from pydantic import Field

from ..types.base import *


class CheckEmailAddressVerificationCode(BaseObject):
    """
    Checks the email address verification code for Telegram Passport

    :param code: Verification code to check
    :type code: :class:`String`
    """

    ID: typing.Literal["checkEmailAddressVerificationCode"] = Field(
        "checkEmailAddressVerificationCode", validation_alias="@type", alias="@type"
    )
    code: String
