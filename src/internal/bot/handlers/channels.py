from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery

from bot.base import States, BOT
from bot.keyboards import *
from bot.messages import *

from .base import contest_app


router = Router()


@router.message(
    StateFilter(States.admin_all_channel_actions),
    F.text == markups_dict["ADMIN_PAGE_CHANNELS_ACTIONS"]["ADD_BOT_TO_CHANNEL"]
)
async def handle_add_admin_action_choose_channels_add_bot(message: Message, state: FSMContext):
    await message.reply(text=CHECK_FOR_CHANNEL_MESSAGE)


@router.message(
    StateFilter(States.admin_all_channel_actions),
    F.text == markups_dict["ADMIN_PAGE_CHANNELS_ACTIONS"]["GET_CHANNELS"]
)
async def handle_add_admin_action_choose_channels_get_channels(message: Message, state: FSMContext):
    channels = contest_app.get_channels()
    markup = make_list_of_channels_markup(channels, LIST_CHANNELS_MESSAGE, callback_data_prefix="channel_action")
    await message.reply(text="Выберите канал:", reply_markup=markup)


@router.callback_query(
    F.data.startswith("channel_action")
)
async def get_channel_actions(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        return

    channel_id = int(callback.data.split("channel_action")[-1])

    await BOT.send_message(
        callback.from_user.id,
        text="Выберите действие:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="Удалить канал", callback_data=f"del_channel_yes{channel_id}"),
            ]]
        )
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("del_channel_yes")
)
async def handle_del_bl_action(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        return

    channel_id = int(callback.data.split("del_channel_yes")[-1])

    try:
        contest_app.delete_channel(channel_id)
        await BOT.send_message(chat_id=callback.from_user.id, text=CHANNEL_DELETED_MESSAGE, reply_markup=ADMIN_PAGE_CHANNELS_ACTIONS)
        await state.set_state(States.admin_all_channel_actions)
        await callback.answer()
    except:
        await callback.answer(ERROR_UKNOWN)
        return


# @router.message(
#     StateFilter(States.admin_all_channel_actions),
#     F.text == markups_dict["ADMIN_PAGE_CHANNELS_ACTIONS"]["DELETE_CHANNEL"]
# )
# async def handle_add_admin_action_choose_channels_del_channels(message: Message, state: FSMContext):
#     channels = contest_app.get_channels()
#     kbd_inline = build_channels_choice_inline_kbd(channels, callback_data_prefix="del_channel_")
#     message_ = make_list_of_channels_message(channels, LIST_CHANNELS_MESSAGE)
#     await message.reply(text=message_, reply_markup=kbd_inline)


# @router.callback_query(
#     F.data.startswith("del_channel_")
# )
# async def del_channel_callback(callback: CallbackQuery, state: FSMContext):
#     if callback.data is None:
#         return
# 
#     channel_id = int(callback.data.split("_")[-1])
# 
#     await BOT.send_message(
#         chat_id=callback.from_user.id,
#         text=CHANNEL_DELETE_CONFIRM_MESSAGE,
#         reply_markup=ADMIN_PAGE_CHANNELS_ACTIONS_DEL_CONFIRM(channel_id)
#     )
#     await state.set_state(States.admin_channel_del_channel_confirm_action)
#     await callback.answer()


# @router.callback_query(
#     StateFilter(States.admin_channel_del_channel_confirm_action),
#     F.data.startswith("channel_ask_del_")
# )
# async def handle_add_admin_action_choose_channels_del_channels_ask_confirm_finish(callback: CallbackQuery, state: FSMContext):
#     if callback.data is None:
#         return
# 
#     if markups_dict["ADMIN_PAGE_CHANNELS_ACTIONS_DEL_CONFIRM"]["YES_CONFIRM"] in str(callback.data):
#         try:
#             channel_id = int(callback.data.split("_")[-1])
#             contest_app.delete_channel(channel_id)
#             await BOT.send_message(chat_id=callback.from_user.id, text=CHANNEL_DELETED_MESSAGE, reply_markup=ADMIN_PAGE_CHANNELS_ACTIONS)
#         except Exception:
#             await BOT.send_message(chat_id=callback.from_user.id, text=ERROR_UNABLE_TO_DEL_CHANNEL)
#     else:
#         await BOT.send_message(chat_id=callback.from_user.id, text=CHANNEL_DELETE_CANCELED_MESSAGE, reply_markup=ADMIN_PAGE_CHANNELS_ACTIONS)
# 
#     await state.set_state(States.admin_all_channel_actions)
#     await callback.answer()
