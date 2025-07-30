# =============================================================================== #
#                                                                                 #
#    This file has been generated automatically!! Do not change this manually!    #
#                                                                                 #
# =============================================================================== #
from __future__ import annotations

import typing

from pydantic import Field

from ..types.base import *


class ProcessPushNotification(BaseObject):
    """
    Handles a push notification. Returns error with code 406 if the push notification is not supported and connection to the server is required to fetch new data. Can be called before authorization

    :param payload: JSON-encoded push notification payload with all fields sent by the server, and "google.sent_time" and "google.notification.sound" fields added
    :type payload: :class:`String`
    """

    ID: typing.Literal["processPushNotification"] = Field(
        "processPushNotification", validation_alias="@type", alias="@type"
    )
    payload: String
