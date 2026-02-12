from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import (
    CommandStart,
    StateFilter
)

from bot.base import States
from bot.keyboards import *
from bot.messages import *

from app.factory import SqliteBasedApplicationFactory


user_app = SqliteBasedApplicationFactory().get_users_app()
admin_app = SqliteBasedApplicationFactory().get_admins_app()
contest_app = SqliteBasedApplicationFactory().get_contest_app()


### General ###


router = Router()


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext):
    # print("WHTT", message)
    if message.from_user is None:
        return

    admin = admin_app.get_admin_by_tg_id(message.from_user.id)
    if admin is not None:
        await message.answer(ADMIN_HELLO_MESSAGE, reply_markup=ADMIN_START_MARKUP)
        await state.set_state(States.admin_start)
    else:
        await message.answer(ERROR_UNABLE_TO_LOGIN)


@router.message(F.text == markups_dict["BACK_ACTION"]["BACK"])
async def handle_back_state(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state in [
        States.admin_all_channel_actions,
        States.admin_all_contest_actions,
        States.admin_all_blacklist_actions,
        States.admin_admin_actions,
        States.admin_bl_add_user_action,
        States.admin_bl_add_user_choose_num_of_block_action,
        States.admin_bl_del_user_action,
        States.admin_add_admin_actions,
        States.admin_add_admin_actions_add_admin,
        States.admin_delete_admin_actions,
    ]:
        await message.answer(ADMIN_HELLO_MESSAGE, reply_markup=ADMIN_START_MARKUP)
        await state.set_state(States.admin_start)
    if current_state in [
        States.admin_contest_get_contest_result_action
    ]:
        await message.answer(ADMIN_ACTIONS_MESSAGE, reply_markup=ADMIN_PAGE_ADMIN_ACTIONS)
        await state.set_state(States.admin_all_contest_actions)
    if current_state in [
        States.admin_bl_add_user_action
    ]:
        await state.set_state(States.admin_all_blacklist_actions)
    if current_state in [
        States.admin_contest_add_contest_choose_finish_get_data_num_of_users,
        States.admin_contest_add_contest_choose_channel_for_sub_check,
        States.admin_contest_get_contest_result_action,
        States.admin_contest_delete_contest,
        States.admin_contest_add_contest_choose_channel,
        States.admin_contest_add_contest_name,
        States.admin_contest_add_contest_add_text,
        States.admin_contest_add_contest_add_media,
        States.admin_contest_add_contest_add_num_of_users,
        States.admin_contest_add_contest_choose_publication,
        States.admin_contest_add_contest_choose_publication_values,
        States.admin_contest_add_contest_add_subs,
        States.admin_contest_add_contest_choose_finish,
        States.admin_contest_add_contest_choose_finish_get_data,
        States.admin_contest_add_contest_preview,
        States.admin_contest_add_contest_done,
    ]:
        try:
            contest_app.delete_contest_temp(message.from_user.id)
        except Exception:
            pass
        await message.answer('Конкурс удален', reply_markup=ADMIN_PAGE_CONTESTS_ACTIONS)
        await state.set_state(States.admin_all_contest_actions)
    if current_state in [
        States.admin_contest_change_winner
    ]:
        await state.set_state(States.admin_all_contest_actions)
        await message.answer(text='Отмена', reply_markup=ADMIN_PAGE_CONTESTS_ACTIONS)


@router.message(
    F.text == markups_dict["CANCEL_ACTION"]["CANCEL"],
)
async def handle_cancel_state(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state in [
        States.admin_contest_add_contest_choose_channel,
        States.admin_contest_add_contest_add_text,
        States.admin_contest_add_contest_add_media,
        States.admin_contest_add_contest_add_num_of_users,
        States.admin_contest_add_contest_choose_publication,
        States.admin_contest_add_contest_choose_publication_values,
        States.admin_contest_add_contest_add_subs,
        States.admin_contest_add_contest_choose_finish,
        States.admin_contest_add_contest_choose_finish_get_data,
        States.admin_contest_add_contest_preview,
        States.admin_contest_upd_contest_result,
        States.admin_contest_upd_winners_shuffle,
        States.admin_contest_upd_winners_del,
        States.admin_contest_upd_winners,
    ]:
        try:
            del contest_app._temp_contest_storage[message.from_user.id]
        except:
            pass
        await message.reply(text=CANCEL_ADMIN_CONTEST_MESSAGE, reply_markup=ADMIN_PAGE_CONTESTS_ACTIONS)
        await state.set_state(States.admin_all_contest_actions)
    elif current_state in [
        States.admin_bl_add_user_action,
        States.admin_bl_remove_user_action,
        States.admin_bl_add_user_choose_num_of_block_action,
        States.admin_bl_del_user_action,
        States.admin_all_blacklist_actions,
    ]:
        await state.set_state(States.admin_all_blacklist_actions)
        await message.reply(text=CANCEL_ACTION_MESSAGE, reply_markup=ADMIN_PAGE_BLACKLIST_ACTIONS)


@router.message(
    StateFilter(States.start),
    F.contact
)
async def handle_contact(message: Message, state: FSMContext):
    if message.contact is None:
        return
    if message.from_user is None:
        return
    if message.contact.user_id != message.from_user.id:
        await message.answer(WRONG_NUMBER_MESSAGE)

    try:
        phone = int(message.contact.phone_number)
    except:
        await message.answer(ERROR_INVALID_PHONE)
        return

    admin = admin_app.get_admin(phone)

    if admin is not None:
        await message.answer(ADMIN_HELLO_MESSAGE, reply_markup=ADMIN_START_MARKUP)
        await state.set_state(States.admin_start)
    else:
        await message.answer(ERROR_UNABLE_TO_LOGIN)


## Sub menus ###


@router.message(
    StateFilter(States.admin_start),
    F.text == markups_dict["ADMIN_START_MARKUP"]["ADMINS"]
)
async def handle_admin_start_admins(message: Message, state: FSMContext):
    await message.reply(text=ADMIN_ACTIONS_MESSAGE, reply_markup=ADMIN_PAGE_ADMIN_ACTIONS)
    await state.set_state(States.admin_admin_actions)


@router.message(
    StateFilter(States.admin_start),
    F.text == markups_dict["ADMIN_START_MARKUP"]["BLACKLIST"]
)
async def handle_admin_start_blacklist(message: Message, state: FSMContext):
    await message.reply(text=BLACKLIST_ACTIONS_MESSAGE, reply_markup=ADMIN_PAGE_BLACKLIST_ACTIONS)
    await state.set_state(States.admin_all_blacklist_actions)


@router.message(
    StateFilter(States.admin_start),
    F.text == markups_dict["ADMIN_START_MARKUP"]["CONTESTS"]
)
async def handle_admin_start_contests(message: Message, state: FSMContext):
    await message.reply(text=CONTEST_ACTIONS_MESSAGE, reply_markup=ADMIN_PAGE_CONTESTS_ACTIONS)
    await state.set_state(States.admin_all_contest_actions)


@router.message(
    StateFilter(States.admin_start),
    F.text == markups_dict["ADMIN_START_MARKUP"]["CHANNELS"]
)
async def handle_admin_start_channels(message: Message, state: FSMContext):
    await message.reply(text=CHANNEL_ACTIONS_MESSAGES, reply_markup=ADMIN_PAGE_CHANNELS_ACTIONS)
    await state.set_state(States.admin_all_channel_actions)
