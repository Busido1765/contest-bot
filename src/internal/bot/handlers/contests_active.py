from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

from bot.base import BOT, States
from bot.keyboards import *
from bot.messages import *

from .base import contest_app


router = Router()


@router.message(
    StateFilter(States.admin_all_contest_actions),
    F.text == markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS"]["GET_ACTIVE_CONTESTS"]
)
async def handle_get_active_contests(message: Message, state: FSMContext):
    contests = contest_app.get_active_contests()
    if contests == []:
        await message.reply(text="Нет доступных активных конкурсов")
        return

    markup = make_active_contest_markup(contests, "active_contest_action")
    await message.reply(text="Активные конкурсы:", reply_markup=markup)


@router.callback_query(
    F.data.startswith("active_contest_action")
)
async def handle_contest_action(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        return

    contest_id = callback.data.split("active_contest_action")[-1]
    contest = contest_app.get_contest(contest_id)

    if contest is None:
        await callback.answer(ERROR_CONTEST_NOT_FOUND)
        return
    
    message = make_contest_result_message([contest], message="")

    await BOT.send_message(
        chat_id=callback.from_user.id,
        text=message,
        reply_markup=(
            InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Обновить результаты", callback_data=f"upd_cnts_res_{contest_id}")],
                    [InlineKeyboardButton(text="Обновить конкурс", callback_data=f"upd_contest_data_{contest_id}")],
                ]
            )
        )
    )


@router.callback_query(
    F.data.startswith("upd_contest_data_")
)
async def handle_contest_update(callback: CallbackQuery, state: FSMContext):
    await BOT.send_message(callback.from_user.id, "Этот раздел находится в разработке")
    await callback.answer()
