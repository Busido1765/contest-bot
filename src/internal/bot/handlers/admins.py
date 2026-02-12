from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

from bot.base import BOT, States
from bot.keyboards import *
from bot.messages import *

from app.dto.users import AdminCreate

from .base import admin_app


router = Router()


@router.message(
    StateFilter(States.admin_admin_actions),
    F.text == markups_dict["ADMIN_PAGE_ADMIN_ACTIONS"]["GET_ADMINS"]
)
async def handle_add_admin_action_get(message: Message, state: FSMContext):
    if message.from_user is None:
        return

    admin = admin_app.get_admin_by_tg_id(message.from_user.id)

    if admin is None:
        return

    all_admins = admin_app.get_all_admins()
    markup = make_admin_list_markup(all_admins, ADMIN_LIST_MESSAGE, "admin_action")

    await message.reply(text="Администраторы:", reply_markup=markup)


@router.callback_query(
    F.data.startswith("admin_action")
)
async def show_admin_actions(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        return

    admin_tg_id = int(callback.data.split("admin_action")[-1])

    await BOT.send_message(
        callback.from_user.id,
        text="Выберите действие:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="Удалить администратора", callback_data=f"del_admin_yes_{admin_tg_id}"),
            ]]
        )
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("del_admin_yes_")
)
async def handle_del_admin_action(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        return

    admin_tg_id = int(callback.data.split("del_admin_yes_")[-1])
    admin = admin_app.get_admin_by_tg_id(admin_tg_id)
    if admin is None:
        await callback.answer("Админ не найден")
        return

    try:
        admin_app.delete_admin(admin.phone_number)
    except:
        await callback.answer(ERROR_UKNOWN)
        return

    await BOT.send_message(callback.from_user.id, text="Администратор удален")
    await callback.answer()


@router.message(
    StateFilter(States.admin_admin_actions),
    F.text == markups_dict["ADMIN_PAGE_ADMIN_ACTIONS"]["ADD_ADMIN"]
)
async def handle_add_admin_action(message: Message, state: FSMContext):
    await message.reply(text=ASK_ADMIN_PHONE_NUMBER_MESSAGE)
    await state.set_state(States.admin_add_admin_actions_add_admin)


@router.message(
    StateFilter(States.admin_add_admin_actions_add_admin),
)
async def handle_add_admin_action_finish_add(message: Message, state: FSMContext):
    if message.from_user is None or message.text is None:
        return

    try:
        tg_id = int(message.text)
    except Exception:
        await message.reply(text="Неверный формат номер телфона и айди")
        return

    try:
        admin_app.add_admin(
            AdminCreate(phone_number=-1, tg_id=tg_id)
        )
    except:
        await message.reply(text="Ошибка добавления администратора")
        return

    await message.reply(text=NEW_ADMIN_ADDED_MESSAGE)
    await state.set_state(States.admin_admin_actions)


# @router.message(
#     StateFilter(States.admin_admin_actions),
#     F.text == markups_dict["ADMIN_PAGE_ADMIN_ACTIONS"]["DELETE_ADMIN"]
# )
# async def handle_add_admin_action_del(message: Message, state: FSMContext):
#     await message.reply(text=ASK_ADMIN_PHONE_MESSAGE)
#     await state.set_state(States.admin_delete_admin_actions)
# 
# 
# @router.message(
#     StateFilter(States.admin_delete_admin_actions),
# )
# async def handle_add_admin_action_del_finish(message: Message, state: FSMContext):
#     if message.text is None:
#         return
# 
#     try:
#         phone = int(message.text)
#     except:
#         await message.answer(ERROR_INVALID_PHONE)
#         return
# 
#     admin = admin_app.get_admin(phone)
# 
#     if admin is not None:
#         admin_app.delete_admin(phone)
#         await message.reply(text=ADMIN_DELETED_MESSAGE)
#         await state.set_state(States.admin_admin_actions)
#     else:
#         await message.reply(text=ADMIN_DOESNT_EXISTS_MESSAGE)
