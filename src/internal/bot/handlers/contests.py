from datetime import datetime
from time import timezone

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

from bot.base import BOT, DISPATCHER, States
from bot.keyboards import *
from bot.messages import *

from shared.settings import SETTINGS, Environment
from shared.dates import HOUR, MINUTE, dt_to_timestamp, now
from shared.types import ContestFinishKind, ContestPublicationKind
from shared.images import save_images

from .base import contest_app, user_app


router = Router()


@router.message(
    StateFilter(States.admin_all_contest_actions),
    F.text == markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS"]["GET_ACTIVE_CONTESTS"]
)
async def handle_get_active_contests(message: Message, state: FSMContext):
    contests = contest_app.get_active_contests()
    print(contests)
    if contests == []:
        await message.reply(text="Нет доступных активных конкурсов")
        return
    await message.reply(
        text=CONTEST_LIST_MESSAGE, 
        reply_markup=make_contest_choice_markup(contests, callback_data_prefix="get_cnts_res_")
    )


@router.message(
    StateFilter(States.admin_all_contest_actions),
    F.text == markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS"]["GET_CONTEST_RESULT"]
)
async def handle_get_contest_result(message: Message, state: FSMContext):
    # CALBACK BUTTONS
    contests = contest_app.get_contests_for_results()
    if contests == []:
        await message.answer("Нет доступных активных конкурсов")
        return
    markup = build_contest_choice_inline_kbd_for_results(contests, callback_data_prefix="get_cnts_res_")

    await message.reply(text=ASK_FOR_CONTENT_RESULT_ID_MESSAGE, reply_markup=markup)
    await state.set_state(States.admin_contest_get_contest_result_action)


@router.callback_query(
    F.data.startswith("get_cnts_res_")
)
async def get_contests_result(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        return

    contest_id = callback.data.split("get_cnts_res_")[-1]

    contest_result = contest_app.get_contest_results(contest_id)
    messge_ = make_contest_result_message([contest_result], CONTEST_RESULT_MESSAGE)

    await BOT.send_message(chat_id=callback.from_user.id, text=messge_, reply_markup=UPDATE_CONTEST_RESULT_ACTION(contest_id))
    await state.set_state(States.admin_all_contest_actions)
    await callback.answer()


@router.message(
    StateFilter(States.admin_all_contest_actions),
    F.text == markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS"]["DELETE_CONTEST"]
)
async def handle_del_contest(message: Message, state: FSMContext):
    # CALBACK BUTTONS
    contests = contest_app.get_contests()
    if contests == []:
        await message.answer("Нет доступных конкурсов")
        return
    markup = build_contest_choice_inline_kbd_for_results(contests, callback_data_prefix="del_contest_")
    await message.reply(text=ASK_FOR_CONTEST_ID_TO_DEL_MESSAGE, reply_markup=markup)
    await state.set_state(States.admin_contest_delete_contest)


@router.callback_query(
    F.data.startswith("del_contest_")
)
async def del_contest(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        return

    contest_id = callback.data.split("del_contest_")[-1]

    try:
        contest_app.delete_contest(contest_id)
    except:
        await BOT.send_message(chat_id=callback.from_user.id, text=ERROR_UNBLE_TO_DEL_CONTEST)
        await callback.answer()
        return

    await BOT.send_message(chat_id=callback.from_user.id, text=CONTEST_DELETED_MESSAGE)
    await state.set_state(States.admin_all_contest_actions)
    await callback.answer()


@router.message(
    StateFilter(States.admin_all_contest_actions),
    F.text == markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS"]["ADD_CONTEST"]
)
async def handle_add_contest(message: Message, state: FSMContext):
    channels = contest_app.get_channels() 

    markup = build_channels_choice_inline_kbd(channels=channels, callback_data_prefix="choose_channel_for_contest_add")

    if channels == []:
        await message.reply(text=NO_ACTIVE_CHANNELS_MESSAGE, reply_markup=markup)
        await state.set_state(States.admin_all_contest_actions)
    else:
        message_ = make_choose_channels_message([], CHOOSE_CHANNEL_FOR_CONTEST_MESSAGE)
        await message.reply(text=message_, reply_markup=markup)
        # await message.reply(text=".", reply_markup=CANCEL_ACTION)
        await state.set_state(States.admin_contest_add_contest_choose_channel)


@router.callback_query(
    F.data.startswith("choose_channel_for_contest_add")
)
async def choose_channel_for_contest_add(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        return

    channel_id = int(callback.data.split("choose_channel_for_contest_add")[-1])
    channel = contest_app.get_channel(channel_id)

    if channel is None:
        await BOT.send_message(chat_id=callback.from_user.id, text=ERROR_CHANNEL_FOR_CONTEST_NOT_FOUND)
        await callback.answer()
        return

    try:
        contest_app.add_contest_temp(callback.from_user.id, channel_tg_name=channel.channel_tg_name)
    except Exception:
        contest_app.update_contest_temp(callback.from_user.id, channel_tg_name=channel.channel_tg_name)

    await BOT.send_message(chat_id=callback.from_user.id, text=ASK_FOR_CONTEST_NAME_MESSAGE)
    await state.set_state(States.admin_contest_add_contest_name)
    await callback.answer()


@router.message(
    StateFilter(States.admin_contest_add_contest_name),
    F.text
)
async def handle_adding_name_on_contest_create(message: Message, state: FSMContext):

    contest_name = message.text

    try:
        contest_app.update_contest_temp(message.from_user.id, contest_name=contest_name)
    except Exception:
        await message.reply(text=ERROR_UNABLE_TO_ADD_CONTEST_NAME)
        return

    await BOT.send_message(chat_id=message.from_user.id, text=SEND_CONTEST_TEXT_MESSAGE)
    await state.set_state(States.admin_contest_add_contest_add_text)


@router.message(
    StateFilter(States.admin_contest_add_contest_add_text),
)
async def handle_adding_text_on_contest_create(message: Message, state: FSMContext):
    if message.from_user is None or message.photo is None:
        await message.reply("Отсутсвует картинка или отправлен файл")
        return

    img_caption = message.caption
    if img_caption is None:
        await message.reply("Нет подписи к изображению")
        return

    image_paths = await save_images([message.photo[-1]])
    if message.caption_entities:
        entities = [x.model_dump() for x in message.caption_entities]
    else:
        entities = []
    print(entities) 
    text_link = message.get_url()
    print(text_link)

    try:
        contest_app.update_contest_temp(
            message.from_user.id,
            media=image_paths,
            text=img_caption,
            entities=entities,
            text_link=text_link
        )
    except:
        await message.reply(text=ERROR_UNABLE_TO_ADD_CONTEST_MEDIA)
        return

    await message.reply(text=IMAGES_ADDED_AND_ASK_FOR_NUM_OF_USERS_MESSAGE, reply_markup=CANCEL_ACTION)
    await state.set_state(States.admin_contest_add_contest_add_num_of_users)


@router.message(
    StateFilter(States.admin_contest_add_finiseed_sub_add),
)
async def handle_choose_pub_kind_on_contest_create(message: Message, state: FSMContext):
    if message.text is None or message.from_user is None:
        return

    if message.text == markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS_PUB_TYPE"]["PLAN"]:
        try:
            contest_app.update_contest_temp(message.from_user.id, pulication_kind=ContestPublicationKind.PLANNED)
        except:
            await message.reply(text=ERROR_UNABLE_TO_ADD_CONTEST_PUB_TYPE)
            return

        await message.reply(text=ASK_FOR_CONTEST_PUB_DATETIME_MESSAGE)
        await state.set_state(States.admin_contest_add_contest_choose_publication_values)
    else:
        try:
            contest_app.update_contest_temp(message.from_user.id, pulication_kind=ContestPublicationKind.ON_FINISH)
        except:
            await message.reply(text=ERROR_UNABLE_TO_ADD_CONTEST_PUB_TYPE)
            return

        await message.reply(PUB_DATE_ADDED_AND_ASK_FINISH_KIND_MESSAGE, reply_markup=ADMIN_PAGE_CONTESTS_ACTIONS_FINISH_TYPE)
        await state.set_state(States.admin_contest_add_contest_choose_finish)


@router.message(
    StateFilter(
        States.admin_contest_add_contest_choose_publication_values
    ),
)
async def handle_choose_pub_kind_not_needed_on_contest_create(message: Message, state: FSMContext):
    if message.text is None or message.from_user is None:
        return
    
    if message.text == markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS_PUB_TYPE"]["NOW"]:
        timestamp_ = now(timezone=3)
    else:
        try:
            datetime_ = message.text
            dt = datetime.strptime(datetime_, "%d.%m.%Y %H:%M")
            timestamp_ = dt_to_timestamp(dt)
        except Exception:
            await message.reply(ERROR_INVALID_DATE)
            return

    now_ts = now(timezone=3)
    if timestamp_ <= now_ts:
        await message.reply("Время публикации конкурса должно быть в будущем времени")
        return

    try:
        contest_app.update_contest_temp(message.from_user.id, pulication_date=timestamp_)
    except:
        await message.reply(text=ERROR_UNABLE_TO_ADD_CONTEST_PUB_DT)
        return

    await message.reply(PUB_DATE_ADDED_AND_ASK_FINISH_KIND_MESSAGE, reply_markup=ADMIN_PAGE_CONTESTS_ACTIONS_FINISH_TYPE)
    await state.set_state(States.admin_contest_add_contest_choose_finish)


@router.message(
    StateFilter(
        States.admin_contest_add_contest_add_subs,
    ),
)
async def handle_chose_channels_to_sub(message: Message, state: FSMContext):
    if message.text is None or message.from_user is None:
        return

    if message.text == markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS_ADD_SUBS"]["NOT_SUBS_NEEDED"]:
        await message.reply(text=PUB_DATE_ADDED_AND_ASK_FINISH_KIND_MESSAGE, reply_markup=ADMIN_PAGE_CONTESTS_ACTIONS_FINISH_TYPE)
        await state.set_state(States.admin_contest_add_contest_choose_finish)
        return

    try:
        channels = contest_app.get_channels()
        if channels == []:
            await message.reply(text=ERROR_CHANNEL_FOR_CONTEST_NOT_FOUND, reply_markup=ADMIN_PAGE_CONTESTS_ACTIONS_PUB_TYPE)
            await state.set_state(States.admin_contest_add_contest_choose_publication)
            return
    except Exception as err:
        print(err)
        await message.reply(text=ERROR_UKNOWN, reply_markup=ADMIN_PAGE_CONTESTS_ACTIONS_PUB_TYPE)
        await state.set_state(States.admin_contest_add_contest_choose_publication)
        return

    await message.reply(text="Введите адрес каналов (@channel_name):", reply_markup=CHOOSE_SUB_CHANNELS_AND_CANCEL_ACTION)
    await state.set_state(States.admin_contest_add_contest_choose_channel_for_sub_check)


@router.message(
    StateFilter(States.admin_contest_add_contest_choose_channel_for_sub_check)
)
async def handle_choose_channel_for_sub_check(message: Message, state: FSMContext):
    if message.text is None or message.from_user is None:
        return

    if message.text == markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS_ADD_SUBS"]["FINISH_ADD_SUBS"]:
        contest = contest_app.get_contest_temp(message.from_user.id)
        if contest is None:
            await message.reply(text=ERROR_CONTEST_NOT_FOUND)
            return

        if "required_subs" not in contest:
            contest["required_subs"] = []
            contest_app.update_contest_temp(message.from_user.id, required_subs=[])

        await message.reply(text=NUM_OF_USERS_ADDED_AND_ASK_WHEN_TO_PUB_MESSAGE, reply_markup=ADMIN_PAGE_CONTESTS_ACTIONS_PUB_TYPE)
        await state.set_state(States.admin_contest_add_finiseed_sub_add)
    else:
        channel_tg_tag = message.text
        try:
            await BOT.get_chat_member(channel_tg_tag, message.from_user.id)
        except Exception:
            await message.reply(text=ERROR_BOT_NOT_ADMIN_IN_CHANNEL)
            return

        contest = contest_app.get_contest_temp(message.from_user.id)
        if contest is None:
            await message.reply(text=ERROR_CONTEST_NOT_FOUND)
            return

        if "required_subs" not in contest:
            contest["required_subs"] = [channel_tg_tag]
            contest_app.update_contest_temp(message.from_user.id, required_subs=[channel_tg_tag])
        else:
            contest["required_subs"].append(channel_tg_tag)
            contest_app.update_contest_temp(message.from_user.id, required_subs=contest["required_subs"])

        await message.reply("Канал добавлен!")


@router.message(
    StateFilter(States.admin_contest_add_contest_add_num_of_users),
)
async def handle_choose_participants_on_contest_create(message: Message, state: FSMContext):
    if message.text is None or message.from_user is None:
        return

    try:
        num_of_users = int(message.text)
    except Exception:
        await message.reply(text=ERROR_INVALID_NUM_OF_USERS)
        return

    try:
        contest_app.update_contest_temp(message.from_user.id, num_of_winners=num_of_users)
    except Exception:
        await message.reply(text=ERROR_UNABLE_TO_ADD_CONTEST_NUM_OF_USERS)
        return

    await message.reply(text="Введите адрес каналов (@channel_name):", reply_markup=CHOOSE_SUB_CHANNELS_AND_CANCEL_ACTION)
    await state.set_state(States.admin_contest_add_contest_choose_channel_for_sub_check)


@router.message(
    StateFilter(
        States.admin_contest_add_contest_choose_finish
    ),
)
async def handle_choose_finish_kind_not_needed_on_contest_create(message: Message, state: FSMContext):
    if message.text is None or message.from_user is None:
        return

    if message.text == markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS_FINISH_TYPE"]["PLAN"]:
        await message.reply(ASK_FOR_FINISH_PLAN_DATE_MESSAGE)
        await state.set_state(States.admin_contest_add_contest_choose_finish_get_data)
    else:
        await message.reply(ASK_FOR_FINISH_PLAN_NUM_OF_PARTICIPANTS_MESSAGE)
        await state.set_state(States.admin_contest_add_contest_choose_finish_get_data_num_of_users)


@router.message(
    StateFilter(
        States.admin_contest_add_contest_choose_finish_get_data
    ),
)
async def handle_choose_finish_kind_data_not_needed_on_contest_create(message: Message, state: FSMContext):
    if message.text is None or message.from_user is None:
        return
    
    try:
        datetime_ = message.text
        dt = datetime.strptime(datetime_, "%d.%m.%Y %H:%M")
        timestamp_ = dt_to_timestamp(dt)
    except Exception:
        await message.reply(ERROR_INVALID_DATE)
        return

    temp_contest = contest_app.get_contest_temp(message.from_user.id)
    if temp_contest is None:
        await message.reply("Отсутсвует конкурс на редактировании")
        return

    pub_date = temp_contest.get("pulication_date")
    now_ts = now(timezone=3)
    hours_between_start_and_end = HOUR(4) if SETTINGS.ENV == Environment.PROD else MINUTE(4)

    if pub_date is None:
        if timestamp_ <= now_ts:
            await message.reply("Время завершения конкурса должно быть в будущем времени")
            return
        # if (timestamp_ - now_ts) <= hours_between_start_and_end:
        #     await message.reply("Время публикации должно быть не меньше 4-х часов от начала конкурса")
        #     return
    else:
        if timestamp_ <= pub_date:
            await message.reply("Время завершения конкурса должно быть позже времени публикации")
            return
        if (timestamp_ - pub_date) <= hours_between_start_and_end:
            await message.reply("Время публикации должно быть не меньше 4-х часов от начала конкурса")
            return

    try:
        contest_app.update_contest_temp(message.from_user.id, finish_date=timestamp_, finish_kind=ContestFinishKind.PLANNED)
    except:
        await message.reply(text=ERROR_UNABLE_TO_ADD_CONTEST_FINISH_DT)
        return

    try:
        contest = contest_app.get_contest_temp(message.from_user.id)
        if contest is None:
            await message.reply(text=ERROR_CONTEST_NOT_FOUND)
            return
    except:
        await message.reply(text=ERROR_UKNOWN)
        return

    message_ = make_contest_preview_message(contest, CONTEST_PREVIEW_MESSAGE)
    preview_answer_arguments: dict = make_contest_preview_answer_arguments(contest)

    await message.reply(message_, reply_markup=ADMIN_PAGE_CONTESTS_ACTIONS_FINAL_PUBLISH)
    await BOT.send_media_group(message.chat.id, **preview_answer_arguments)
    await state.set_state(States.admin_contest_add_contest_preview)


@router.message(
    StateFilter(
        States.admin_contest_add_contest_choose_finish_get_data_num_of_users
    ),
)
async def handle_choose_num_of_users(message: Message, state: FSMContext):
    if message.text is None or message.from_user is None:
        return

    try:
        num_of_users = int(message.text)
    except:
        await message.reply(text=ERROR_INVALID_NUM_OF_USERS)
        return

    try:
        contest_app.update_contest_temp(message.from_user.id, num_of_users_to_finish=num_of_users, finish_kind=ContestFinishKind.ON_WINNERS_NUM)
    except:
        await message.reply(text=ERROR_UNABLE_TO_ADD_CONTEST_NUM_OF_USERS)
        return

    contest = contest_app.get_contest_temp(message.from_user.id)

    if contest is None:
        await message.reply(text=ERROR_CONTEST_NOT_FOUND)
        return

    message_ = make_contest_preview_message(contest, CONTEST_PREVIEW_MESSAGE)
    preview_answer_arguments: dict = make_contest_preview_answer_arguments(contest)

    await message.reply(message_, reply_markup=ADMIN_PAGE_CONTESTS_ACTIONS_FINAL_PUBLISH)
    await BOT.send_media_group(message.chat.id, **preview_answer_arguments)
    await state.set_state(States.admin_contest_add_contest_preview)


@router.message(
    StateFilter(
        States.admin_contest_add_contest_preview
    ),
)
async def handle_choose_finish_final(message: Message, state: FSMContext):
    if message.text is None or message.from_user is None:
        return
    if message.text == markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS_FINAL_PUBLISH"]["PUBLISH"]:
        try:
            data = await state.get_data()
            is_update = data.get("is_update", False)
            await contest_app.save_and_pubslish_contest_temp(message.from_user.id, is_update)
        except Exception as err:
            print(err)
            await message.reply(text=ERROR_UNABLE_TO_SAVE_CONTEST)
            return
        await message.reply(CONTEST_PUBSLISHED_MESSAGE, reply_markup=ADMIN_PAGE_CONTESTS_ACTIONS)
        await state.set_state(States.admin_all_contest_actions)
    else:
        channels = contest_app.get_channels() 

        if channels == []:
            await message.reply(text=NO_ACTIVE_CHANNELS_MESSAGE)
            await state.set_state(States.admin_all_contest_actions)
        else:
            try:
                contest_app.delete_contest_temp(message.from_user.id)
            except Exception:
                pass
            markup = build_channels_choice_inline_kbd(channels=channels, callback_data_prefix="choose_channel_for_contest_add")
            message_ = make_choose_channels_message([], CHOOSE_CHANNEL_FOR_CONTEST_MESSAGE)
            await message.reply(text=message_, reply_markup=markup)
            await state.set_state(States.admin_contest_add_contest_choose_channel)


@router.message(
    StateFilter(States.admin_all_contest_actions),
    F.text == markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS"]["UPDATE_CONTEST"]
)
async def handle_update_contest(message: Message, state: FSMContext):
    if message.text is None or message.from_user is None:
        return

    contests = contest_app.get_contests()
    if contests == []:
        await message.answer("Нет доступных конкурсов")
        return

    markup = build_contest_choice_inline_kbd_for_results(contests, callback_data_prefix="upd_contest_")
    await message.reply(text=ASK_CONTEST_ID_TO_UPD_MESSAGE, reply_markup=markup)
    await message.reply(text=ASK_CONTEST_ID_TO_UPD_MESSAGE, reply_markup=CANCEL_ACTION)
    await state.set_state(States.admin_contest_upd)


@router.callback_query(
    F.data.startswith("upd_contest_name_"),
)
async def handle_update_contest_name(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        return

    contest_id = callback.data.split("upd_contest_name_")[-1]
    print(callback.data)
    await state.update_data(upd_contest_id=contest_id)

    await callback.message.answer(text='Введите новое название конкурса:', reply_markup=CANCEL_ACTION)
    await state.set_state(States.admin_contest_upd_name)
    await callback.answer()


@router.message(
    StateFilter(States.admin_contest_upd_name),
    F.text,
)
async def handle_update_contest_name_enter(message: Message, state: FSMContext):
    if message.from_user is None:
        return

    await state.update_data(contest_name=message.text)
    contest_id = await state.get_data()
    contest_id = contest_id.get("upd_contest_id")
    contest_app.update_contest_name(contest_id, message.text)

    await message.reply(text=CONTEST_UPDATED_MESSAGE, reply_markup=ADMIN_PAGE_CONTESTS_ACTIONS)
    await state.set_state(States.admin_all_contest_actions)


@router.callback_query(
    F.data.startswith("upd_contest_text_"),
)
async def handle_update_contest_text(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        return

    contest_id = callback.data.split("upd_contest_text_")[-1]
    await state.update_data(upd_contest_id=contest_id)

    await callback.message.answer(text='Введите новую подпись и фото:', reply_markup=CANCEL_ACTION)
    await state.set_state(States.admin_contest_upd_text)
    await callback.answer()


@router.message(
    StateFilter(States.admin_contest_upd_text),
    F.photo,
    F.caption,
)
async def handle_update_contest_text_enter(message: Message, state: FSMContext):
    if message.from_user is None:
        return

    img_caption = message.caption
    if message.caption_entities:
        entities = [x.model_dump() for x in message.caption_entities]
    else:
        entities = []
    if img_caption is None:
        await message.reply("Нет подписи к изображению")
        return

    image_paths = await save_images([message.photo[-1]])

    contest_id = await state.get_data()
    contest_id = contest_id.get("upd_contest_id")

    contest_app.update_contest_description(contest_id, img_caption, image_paths, entities)

    contest = contest_app.get_contest(contest_id)
    if contest.post_message_id:
        await contest_app.publish_contest(contest_id, is_update=True)
    await message.reply(text=CONTEST_UPDATED_MESSAGE, reply_markup=ADMIN_PAGE_CONTESTS_ACTIONS)
    await state.set_state(States.admin_all_contest_actions)


@router.callback_query(
    F.data.startswith("upd_contest_finish_"),
)
async def handle_update_contest_finish(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        return

    contest_id = callback.data.split("upd_contest_finish_")[-1] 
    await state.update_data(upd_contest_id=contest_id)

    await callback.message.answer(text='Выберите способ завершения конкурса:', reply_markup=ADMIN_PAGE_CONTESTS_ACTIONS_FINISH_TYPE)
    await state.set_state(States.admin_contest_upd_finish)
    await callback.answer()


@router.message(
    StateFilter(States.admin_contest_upd_finish),
    F.text,
)
async def handle_update_contest_finish_enter(message: Message, state: FSMContext):
    if message.from_user is None:
        return

    if message.text == markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS_FINISH_TYPE"]["PLAN"]:
        await state.update_data(contest_finish_kind=ContestFinishKind.PLANNED)
        await message.reply(ASK_FOR_FINISH_PLAN_DATE_MESSAGE)
        await state.set_state(States.admin_contest_upd_finish_get_data)
    else:
        await state.update_data(contest_finish_kind=ContestFinishKind.ON_WINNERS_NUM)
        await message.reply(ASK_FOR_FINISH_PLAN_NUM_OF_PARTICIPANTS_MESSAGE)
        await state.set_state(States.admin_contest_upd_finish_get_data_num_of_users)


@router.message(
    StateFilter(States.admin_contest_upd_finish_get_data),
    F.text,
)
async def handle_update_contest_finish_get_data(message: Message, state: FSMContext):
    if message.from_user is None:
        return

    try:
        datetime_ = message.text
        dt = datetime.strptime(datetime_, "%d.%m.%Y %H:%M")
        timestamp_ = dt_to_timestamp(dt)
    except Exception:
        await message.reply(ERROR_INVALID_DATE)
        return

    contest_id = await state.get_data()
    contest_id = contest_id.get("upd_contest_id")   
    contest_app.update_contest_finish_kind(contest_id, finish_date=timestamp_, finish_kind=ContestFinishKind.PLANNED)
    await message.reply(text=CONTEST_UPDATED_MESSAGE, reply_markup=ADMIN_PAGE_CONTESTS_ACTIONS)
    await state.set_state(States.admin_all_contest_actions)


@router.message(
    StateFilter(States.admin_contest_upd_finish_get_data_num_of_users),
    F.text,
)
async def handle_update_contest_finish_get_data_num_of_users(message: Message, state: FSMContext):
    if message.from_user is None:
        return

    try:
        num_of_users = int(message.text)
    except Exception:
        await message.reply(text=ERROR_INVALID_NUM_OF_USERS)
        return

    contest_id = await state.get_data()
    contest_id = contest_id.get("upd_contest_id")   
    contest_app.update_contest_finish_kind(contest_id, num_of_users_to_finish=num_of_users, finish_kind=ContestFinishKind.ON_WINNERS_NUM)
    await message.reply(text=CONTEST_UPDATED_MESSAGE, reply_markup=ADMIN_PAGE_CONTESTS_ACTIONS)
    await state.set_state(States.admin_all_contest_actions)


@router.callback_query(
    F.data.startswith("upd_contest_"),
    # StateFilter(States.admin_contest_upd),
)
async def update_contest_cb(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        return

    contest_id = callback.data.split("upd_contest_")[-1]
    try:
        contest = contest_app.get_contest(contest_id)
        if contest is None:
            await callback.answer(ERROR_CONTEST_NOT_FOUND)
            return
    except:
        await callback.answer(ERROR_UKNOWN)
        return
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Название конкурса", callback_data="upd_contest_name_%s" % contest_id),
        ],
        [
            InlineKeyboardButton(text="Картинка и подпись", callback_data="upd_contest_text_%s" % contest_id),
        ],
        [
            InlineKeyboardButton(text="Способ завершения", callback_data="upd_contest_finish_%s" % contest_id),
        ],
    ])

    await callback.message.edit_text(text=ASK_CONTEST_ID_TO_UPD_MESSAGE, reply_markup=kb)
    await callback.answer()


@router.message(
    StateFilter(States.admin_contest_upd),
)
async def handle_update_contest_update(message: Message, state: FSMContext):
    if message.text is None or message.from_user is None:
        return

    channels = contest_app.get_channels() 

    if channels == []:
        await message.reply(text=NO_ACTIVE_CHANNELS_MESSAGE)
        await state.set_state(States.admin_all_contest_actions)
    else:
        message_ = make_choose_channels_message(channels, CHOOSE_CHANNEL_FOR_CONTEST_MESSAGE)
        await message.reply(text=message_, reply_markup=CANCEL_ACTION)
        await state.set_state(States.admin_contest_add_contest_choose_channel)
