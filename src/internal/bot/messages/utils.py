from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity
from aiogram.utils.media_group import MediaGroupBuilder

from app.dto.users import AdminGet, BlackListRecordGet, UserGet
from app.dto.contest import ChannelGet, ContestGet

from shared.dates import timestamp_to_dt


def make_admin_list_markup(list_of_admins: list[AdminGet], message: str, callback_data_prefix: str) -> InlineKeyboardMarkup:
    admins = []
    for i, admin in enumerate(list_of_admins):
        if i % 2 == 0:
            admins.append([])
        admins[-1].append(
            InlineKeyboardButton(text=str(admin.tg_id), callback_data=f"{callback_data_prefix}{admin.tg_id}")
        )
    return InlineKeyboardMarkup(inline_keyboard=admins)


def make_blacklist_markup(blacklist: list[BlackListRecordGet], message: str, callback_data_prefix: str) -> InlineKeyboardMarkup:
    admins = []
    for bl in blacklist:
        admins.append(
            InlineKeyboardButton(text=str(bl.nickname), callback_data=f"{callback_data_prefix}{bl.telegram_id}")
        )
    return InlineKeyboardMarkup(inline_keyboard=[admins])


def make_list_of_channels_markup(list_: list[ChannelGet], message: str, callback_data_prefix: str) -> InlineKeyboardMarkup:
    cnls = []
    for i, channel in enumerate(list_):
        if i % 2 == 0:
            cnls.append([])
        cnls[-1].append(
            InlineKeyboardButton(text=str(channel.channel_tg_name), callback_data=f"{callback_data_prefix}{channel.channel_id}")
        )
    return InlineKeyboardMarkup(inline_keyboard=cnls)


def make_choose_channels_message(list_: list, message: str) -> str:
    els = "\n".join(str(el) for el in list_)
    return f"{message}\n{els}"


def make_active_contest_markup(list_: list[ContestGet], callback_data_prefix: str):
    buttons = []
    for contest in list_:
        buttons.append(
            InlineKeyboardButton(
                text=f"{contest.channel_tg_name} - {contest.text[:8]}",
                callback_data=f"{callback_data_prefix}{contest.id}"
            )
        )
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def make_contest_choice_markup(list_: list[ContestGet], callback_data_prefix: str):
    buttons = []
    for i, contest in enumerate(list_):
        if i % 2 == 0:
            buttons.append([])
        buttons[-1].append(
            InlineKeyboardButton(
                text=f"{contest.contest_name}",
                callback_data=f"{callback_data_prefix}{contest.id}"
            )
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def make_contest_list_message(list_: list[ContestGet], message: str) -> str:
    els = ""
    for el in list_:
        winners = '  \n'.join(str(e) for e in el.winners)
        els += (
            f"{make_contest_preview_message(el.model_dump(), '')}\n"
            f"Количество участников: {len(el.participants)}\n"
            "---\n"
            f"Победители: \n{winners}\n"
            "---\n"
        )
        if el.publication_date:
            pd = timestamp_to_dt(el.publication_date).strftime("%d:%m:%Y %H:%M")
            els += f"Дата публикации: {pd}\n"
        if el.finish_date:
            fd = timestamp_to_dt(el.finish_date).strftime("%d:%m:%Y %H:%M")
            els += f"Дата завершения: {fd}\n"
    return f"{message}\n{els}"


def make_contest_result_message(list_: list[ContestGet], message: str, users: list[UserGet] = None) -> str:
    if users:
        participants_dict = {user.tg_id: user.nickname for user in users}
    else:
        participants_dict = {}
    els = ""
    for el in list_:
        winners = '  \n'.join(f"{i+1}. {participants_dict[int(user_id)]}" if int(user_id) in participants_dict else f"id: {user_id}" for i, user_id in enumerate(el.winners))
        _msg = make_contest_preview_message(el.model_dump(), '')
        els += (
            f"{_msg}\n"
            f"Количество участников: {len(el.participants)}\n"
            "---\n"
            f"Победители: \n{winners}\n"
        )
    return f"{message}\n{els}"


def make_contest_preview_message(contest: dict | ContestGet, message: str) -> str:
    if isinstance(contest, ContestGet):
        contest = contest.model_dump(no_dict=True)
        contest['pulication_date'] = contest['publication_date']
    contest_preview = (
        f"Название конкурса: {contest['contest_name']}\n"
        f"Канал: {contest['channel_tg_name']}\n"
        f"Каналы для подписки: {contest['required_subs']}\n"
        f"Тип публикации: {contest['pulication_kind'].value}\n"
        f"Тип завершения: {contest['finish_kind'].value}\n"
        f"Количество победителей: {contest['num_of_winners']}\n"
    )
    if "pulication_date" in contest and isinstance(contest['pulication_date'], int):
        publication_date_human_readable = timestamp_to_dt(contest['pulication_date']).strftime("%d.%m.%Y %H:%M")
        contest_preview += f"Дата публикации: {publication_date_human_readable}\n"
    if "finish_date" in contest and isinstance(contest['finish_date'], int):
        finish_date_human_readable = timestamp_to_dt(contest['finish_date']).strftime("%d.%m.%Y %H:%M")
        contest_preview += f"Дата завершения: {finish_date_human_readable}\n"
    return f"{message}\n\n{contest_preview}"


def make_contest_preview_answer_arguments(contest: dict) -> dict:
    print(contest)
    if contest.get("entities"):
        entities = [MessageEntity(**x) for x in contest["entities"]]
    else:
        entities = None
    media_group = MediaGroupBuilder(caption=contest["text"], caption_entities=entities)
    for img_path in contest["media"]:
        media_group.add_photo(media=FSInputFile(img_path))
    return {"media": media_group.build()}


def make_added_new_channel_message(channel_name: str, message: str):
    return f"{message} - {channel_name}"


def make_already_added_channel_message(channel_name: str, message: str):
    return f"{message} - {channel_name}"


def make_kick_from_channel_message(channel_name: str, message: str):
    return f"{message} - {channel_name}"
