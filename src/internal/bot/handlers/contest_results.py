from random import shuffle

from aiogram import F, Router

import random

from app.dto.contest import ContestUpdate
from .contests import *


router = Router()


@router.callback_query(
    F.data.startswith("changeWinner_"),
)
async def handle_change_winner(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        return

    contest_id = callback.data.split("changeWinner_")[-1]

    await state.update_data({"contest_id": contest_id})
    await callback.message.answer(text="Введите номер победителя для изменения", reply_markup=CANCEL_ACTION)
    await state.set_state(States.admin_contest_change_winner)
    await callback.answer()


@router.message(
    StateFilter(States.admin_contest_change_winner),
    F.text.isdigit(),
)
async def handle_change_winner_input(message: Message, state: FSMContext):

    winner_id = int(message.text) - 1
    contest_id = (await state.get_data())["contest_id"]

    try:
        results = contest_app.get_contest_results(contest_id)
        print(results)
        if results is None:
            await message.reply(ERROR_CONTEST_NOT_FOUND)
            return
    except Exception as e:
        print(e)
        await message.reply(ERROR_UKNOWN)
        return 
    if winner_id > len(results.winners) or winner_id < 0:
        await message.reply("Значение победителя не может быть больше количества победителей или меньше 0. Попробуйте снова")
        return

    participants = results.participants
    tries = 0
    while True:
        new_winner = random.choice(participants)
        if new_winner not in results.winners:
            break
        tries += 1
        if tries > 10:
            break

    results.winners[winner_id] = new_winner
    contest_app.update_contest(contest_id, results)
    user = user_app.get_user_by_tg_id(new_winner)
    if user is None:
        await message.reply(f"Победитель изменен на {new_winner}")
    else:
        await message.reply(f"Победитель изменен на {user.nickname}")
    await state.set_state(States.admin_admin_actions)
    users = user_app.get_many_by_tg_id(set(results.winners + results.participants)) 
    new_results_text = make_contest_result_message([results], 'Предварительные результаты конкурса', users)
    await BOT.send_message(message.from_user.id, new_results_text, reply_markup=CHANGE_WINNER_MARKUP(contest_id))


@router.callback_query(
    F.data.startswith("changeWinners_")
)
async def change_winners(callback: CallbackQuery, state: FSMContext):
    
    contest_id = callback.data.split('_')[1]

    contest = contest_app.get_contest_results(contest_id)
    if contest is None:
        await callback.answer(ERROR_CONTEST_NOT_FOUND)
        return

    participants = contest.participants
    new_winners = random.sample(participants, k=len(contest.winners))
    contest.winners = new_winners
    contest_app.update_contest(contest_id, contest)
    users = user_app.get_many_by_tg_id(set(contest.winners + contest.participants))
    new_winners_text = make_contest_result_message([contest], CONTEST_RESULT_MESSAGE, users)
    await callback.message.answer(new_winners_text, reply_markup=CHANGE_WINNER_MARKUP(contest_id))
    await callback.answer()


@router.message(
    StateFilter(States.admin_all_contest_actions),
    F.text.lower() == markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS"]["UPD_CONTEST_RESULT"].lower()
)
async def handle_editing_results_for_contest(message: Message, state: FSMContext):
    if message.from_user is None:
        return

    contests = contest_app.get_contests_for_results()
    if contests == []:
        await message.answer("Нет доступных активных конкурсов")
        return

    markup = build_contest_choice_inline_kbd_for_results(contests, callback_data_prefix="upd_cnts_res_")

    await message.reply(text=ASK_FOR_CONTENT_RESULT_ID_MESSAGE, reply_markup=markup)
    await message.reply(text=".", reply_markup=CANCEL_ACTION)
    await state.set_state(States.admin_contest_upd_contest_result)


@router.callback_query(
    F.data.startswith("upd_cnts_res_"),
    StateFilter(States.admin_contest_upd_contest_result),
)
async def handle_upd_contest_info(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        return

    contest_id = callback.data.split("upd_cnts_res_")[-1]

    try:
        results = contest_app.get_contest_results(contest_id)
        if results is None:
            await callback.answer(ERROR_CONTEST_NOT_FOUND)
            return
    except:
        await callback.answer(ERROR_UKNOWN)
        return 

    messge_ = make_contest_result_message([results.model_dump()], CONTEST_RESULT_MESSAGE)
    await BOT.send_message(
        chat_id=callback.from_user.id,
        text=messge_,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Удалить победителя", callback_data=f"change_winners_{contest_id}")],
                [InlineKeyboardButton(text="Перемешать список победителей", callback_data=f"shuffle_winners_{contest_id}")],
            ]
        )
    )
    await state.set_state(States.admin_contest_upd_winners)
    await callback.answer()


@router.callback_query(
    F.data.startswith("change_winners_"),
    StateFilter(States.admin_contest_upd_winners),
)
async def handle_change_winners(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        return

    contest_id = callback.data.split("change_winners_")[-1]

    try:
        results = contest_app.get_contest_results(contest_id)
        if results is None:
            await callback.answer(ERROR_CONTEST_NOT_FOUND)
            return
    except:
        await callback.answer(ERROR_UKNOWN)
        return 

    await BOT.send_message(callback.from_user.id, text="Введите айди победителя")
    await state.set_state(States.admin_contest_upd_winners_del)
    await state.set_data({"contest_id": contest_id})
    await callback.answer()


@router.message(
    StateFilter(States.admin_contest_upd_winners_del),
)
async def handle_change_winners_del_winner(message: Message, state: FSMContext):
    if message.text is None:
        return

    raw = await state.get_data()
    contest_id = raw["contest_id"]

    winner_id = int(message.text)

    try:
        results = contest_app.get_contest_results(contest_id)
        if results is None:
            await message.reply(ERROR_CONTEST_NOT_FOUND)
            return
    except:
        await message.reply(ERROR_UKNOWN)
        return 
    
    if winner_id not in results.participants:
        await message.reply("Победителя с таким айди не существует")
        return
    
    try:
        dump_ = results.model_dump()
        dump_["media"] = dump_["media"]["media"]
        dump_["participants"] = dump_["participants"]["participants"]
        dump_["winners"] = dump_["winners"]["winners"]
        upd = ContestUpdate.model_validate(dump_)
        upd.winners.remove(winner_id)

        contest_app.update_contest(contest_id, upd)
    except:
        await message.reply(ERROR_UKNOWN)
        return
    
    await message.reply("Победитель удален")
    await state.set_state(States.admin_contest_upd_winners)


@router.callback_query(
    F.data.startswith("shuffle_winners_"),
)
async def handle_change_winners_shuffle(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        return

    contest_id = callback.data.split("shuffle_winners_")[-1]

    try:
        results = contest_app.get_contest_results(contest_id)
        if results is None:
            await callback.answer(ERROR_CONTEST_NOT_FOUND)
            return
    except:
        await callback.answer(ERROR_UKNOWN)
        return 

    try:
        dump_ = results.model_dump()
        dump_["media"] = dump_["media"]["media"]
        dump_["participants"] = dump_["participants"]["participants"]
        dump_["winners"] = dump_["winners"]["winners"]

        upd = ContestUpdate.model_validate(dump_)
        winners = upd.winners
        shuffle(winners)
        upd.winners = winners

        contest_app.update_contest(contest_id, upd)
    except:
        await callback.answer(ERROR_UKNOWN)
        return
    
    await BOT.send_message(callback.from_user.id, "Победители перемешаны")
    await state.set_state(States.admin_contest_upd_winners)
