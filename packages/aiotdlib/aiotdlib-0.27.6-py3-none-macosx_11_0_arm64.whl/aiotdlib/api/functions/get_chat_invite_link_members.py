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
    ChatInviteLinkMember,
)


class GetChatInviteLinkMembers(BaseObject):
    """
    Returns chat members joined a chat via an invite link. Requires administrator privileges and can_invite_users right in the chat for own links and owner privileges for other links

    :param chat_id: Chat identifier
    :type chat_id: :class:`Int53`
    :param invite_link: Invite link for which to return chat members
    :type invite_link: :class:`String`
    :param limit: The maximum number of chat members to return; up to 100
    :type limit: :class:`Int32`
    :param only_with_expired_subscription: Pass true if the link is a subscription link and only members with expired subscription must be returned
    :type only_with_expired_subscription: :class:`Bool`
    :param offset_member: A chat member from which to return next chat members; pass null to get results from the beginning, defaults to None
    :type offset_member: :class:`ChatInviteLinkMember`, optional
    """

    ID: typing.Literal["getChatInviteLinkMembers"] = Field(
        "getChatInviteLinkMembers", validation_alias="@type", alias="@type"
    )
    chat_id: Int53
    invite_link: String
    limit: Int32
    only_with_expired_subscription: Bool = False
    offset_member: typing.Optional[ChatInviteLinkMember] = None
