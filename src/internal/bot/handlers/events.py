from aiogram.filters import (
    ADMINISTRATOR,
    KICKED,
    LEFT,
    ChatMemberUpdatedFilter,
)
from aiogram.types import ChatMemberUpdated
from aiogram import Router, F

from shared.exceptions import NotFoundError

from .base import contest_app


router = Router()


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=ADMINISTRATOR)
)
async def hanel_chat_member(event: ChatMemberUpdated):
    print('added to channel', event.chat.id)
    channel_id = event.chat.id
    channel_name = event.chat.full_name
    channel = contest_app.get_channel(channel_id)
    if channel is None:
        contest_app.add_channel(channel_id, channel_name)
        await contest_app._notify_users_about_new_channel(channel_name)
    else:
        await contest_app._notify_users_about_channel_already_added(channel_name)


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=KICKED)
)
@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=LEFT)
)
async def handle_chat_member(event: ChatMemberUpdated):
    print('deleted from channel', event.chat.id)
    channel_id = event.chat.id
    if channel_id is None:
        return

    channel = contest_app.get_channel(channel_id)
    if channel is None:
        return

    contest_app.delete_channel(channel_id)
    await contest_app._notify_users_about_channel_kick(channel.channel_tg_name)
