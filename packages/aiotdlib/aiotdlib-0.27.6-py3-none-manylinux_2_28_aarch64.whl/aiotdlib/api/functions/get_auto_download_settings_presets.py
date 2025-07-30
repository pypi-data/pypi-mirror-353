# =============================================================================== #
#                                                                                 #
#    This file has been generated automatically!! Do not change this manually!    #
#                                                                                 #
# =============================================================================== #
from __future__ import annotations

import typing

from pydantic import Field

from ..types.base import *


class GetAutoDownloadSettingsPresets(BaseObject):
    """
    Returns auto-download settings presets for the current user
    """

    ID: typing.Literal["getAutoDownloadSettingsPresets"] = Field(
        "getAutoDownloadSettingsPresets", validation_alias="@type", alias="@type"
    )
