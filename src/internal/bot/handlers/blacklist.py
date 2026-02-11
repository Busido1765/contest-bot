from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram import F, Router

from bot.keyboards import *
from bot.messages import *
from bot.base import BOT, States

from shared.exceptions import NotFoundError

from .base import admin_app


router = Router()


@router.message(
    StateFilter(States.admin_all_blacklist_actions),
    F.text == markups_dict["ADMIN_PAGE_BLACKLIST_ACTIONS"]["GET_BLACKLIST"],
)
async def handle_add_admin_action_choose_bl_get(message: Message, state: FSMContext):
    blacklist, _ = admin_app.get_blacklist(num=50)
    if blacklist == []:
        await message.reply("Черный список пустой")
        return

    markup = make_blacklist_markup(blacklist, BLACKLIST_GET_MESSAGE, "bl_action")

    await message.reply(text="Черный список", reply_markup=markup)


@router.callback_query(
    F.data.startswith("bl_action")
)
async def handle_bl_action(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        return

    bl_tg_id = int(callback.data.split("bl_action")[-1])
    await BOT.send_message(
        callback.from_user.id,
        text="Выберите действие:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="Удалить пользователя из черного списка", callback_data=f"del_bl_yes{bl_tg_id}"),
            ]]
        )
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("del_bl_yes")
)
async def handle_del_bl_action(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        return

    bl_tg_id = int(callback.data.split("del_bl_yes")[-1])

    try:
        admin_app.remove_user_from_blacklist(bl_tg_id)
    except:
        await callback.answer(ERROR_UKNOWN)
        return

    await BOT.send_message(callback.from_user.id, text="Пользователь удален из черного списка")
    await callback.answer()


@router.message(
    StateFilter(States.admin_all_blacklist_actions),
    F.text == markups_dict["ADMIN_PAGE_BLACKLIST_ACTIONS"]["ADD_USER"]
)
async def handle_add_admin_action_choose_bl_add(message: Message, state: FSMContext):
    await message.reply(text=ASK_USER_ID_FOR_BLACKLIST_MESSAGE, reply_markup=CANCEL_ACTION)
    await state.set_state(States.admin_bl_add_user_action)


@router.message(
    StateFilter(States.admin_all_blacklist_actions),
    F.text == markups_dict["ADMIN_PAGE_BLACKLIST_ACTIONS"]["REMOVE_USER"]
)
async def handle_add_admin_action_choose_bl_remove(message: Message, state: FSMContext):
    await message.reply(text=ASK_USER_ID_FOR_BLACKLIST_REMOVE_MESSAGE, reply_markup=CANCEL_ACTION)
    await state.set_state(States.admin_bl_remove_user_action)


@router.message(
    StateFilter(States.admin_bl_remove_user_action),
    F.text
)
async def handle_add_admin_action_choose_bl_remove_choose_num_of_days(message: Message, state: FSMContext):
    if message.from_user is None:
        return
    
    users = message.text.split('\n')
    users_removed = 0
    users_failed = 0
    for user in users:
        try:
            admin_app.remove_user_from_blacklist(user)
            users_removed += 1
        except Exception as e:
            print(e)
            users_failed += 1

    await message.reply(
        text=BLACKLIST_REMOVE.format(users_removed=users_removed, users_failed=users_failed)
        )


@router.message(
    StateFilter(States.admin_bl_add_user_action),
    F.text
)
async def handle_add_admin_action_choose_bl_add_choose_num_of_days(message: Message, state: FSMContext):
    if message.from_user is None:
        return
    
    users = message.text.split('\n')
    users_added = 0
    users_failed = 0
    users_duplicate = 0

    for user in users:
        try:
            if not all(x.isdigit() for x in user):
                users_failed += 1
                continue
            admin_app.add_user_to_blacklist_without_ban_days(user, message.from_user.id, force_add=True)
            users_added += 1
        except Exception as e:
            print(e)
            users_duplicate += 1
            continue

    await message.reply(
        text=BLACKLIST_ADD.format(users_added=users_added, users_failed=users_failed, users_duplicate=users_duplicate)
        )


@router.message(
    StateFilter(States.admin_bl_add_user_choose_num_of_block_action),
)
async def handle_add_admin_action_choose_bl_add_finish(message: Message, state: FSMContext):
    if message.text is None or message.from_user is None:
        return

    try:
        days = int(message.text)
    except:
        await message.answer(ERROR_INVALID_DAYS)
        return

    try:
        admin_app.update_blacklist_record_block_days(message.from_user.id, days)
    except NotFoundError:
        await message.reply(text=ERROR_USER_NOT_FOUND)
        return
    except:
        await message.reply(text=ERROR_UKNOWN)
        return

    await message.reply(text=BLACKLIST_DONE_ADDING_BLOCK_DAYS, reply_markup=ADMIN_PAGE_BLACKLIST_ACTIONS)
    await state.set_state(States.admin_all_blacklist_actions)
