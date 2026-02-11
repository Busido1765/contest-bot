from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.dto.contest import ChannelGet, ContestGet

markups_dict = {
    "START_KEYBOARD_MARKUP": {
        "SEND_CONTACT": "Отправить контакт",
    },
    
    "USER_MARKUP": {
        "PARTICIPATE": "Участвовать",
    },
    
    "BACK_ACTION": {
        "BACK": "Назад",
    },
    
    "CANCEL_ACTION": {
        "CANCEL": "Отмена",
    },
    
    "ADMIN_START_MARKUP": {
        "ADMINS": "Админы",
        "BLACKLIST": "Черный список",
        "CONTESTS": "Конкурсы",
        "CHANNELS": "Каналы",
    },
    
    "ADMIN_PAGE_ADMIN_ACTIONS": {
        "GET_ADMINS": "Список админов",
        "ADD_ADMIN": "Добавить админа",
        "DELETE_ADMIN": "Удалить админа",
        "BACK": "Назад",
    },
    
    "ADMIN_PAGE_BLACKLIST_ACTIONS": {
        "GET_BLACKLIST": "Черный список",
        "ADD_USER": "Добавить пользователя",
        "REMOVE_USER": "Удалить пользователя",
        "BACK": "Назад",
    },
    
    "ADMIN_PAGE_CHANNELS_ACTIONS": {
        "ADD_BOT_TO_CHANNEL": "Добавить бота в канал",
        "GET_CHANNELS": "Список каналов",
        "DELETE_CHANNEL": "Удалить канал",
        "BACK": "Назад",
    },
    
    "ADMIN_PAGE_CHANNELS_ACTIONS_DEL_CONFIRM": {
        "YES_CONFIRM": "Да, подтвердить",
        "NO_FUCK_YOU_NO_WAY": "Нет, спасибо",
    },
    
    "ADMIN_PAGE_CONTESTS_ACTIONS": {
        "GET_ACTIVE_CONTESTS": "Активные конкурсы",
        "GET_CONTEST_RESULT": "Результат конкурса",
        "UPD_CONTEST_RESULT": "Обновить результат конкурса",
        "ADD_CONTEST": "Добавить конкурс",
        "DELETE_CONTEST": "Удалить конкурс",
        "UPDATE_CONTEST": "Обновить конкурс",
        "BACK": "Назад",
    },
    
    "ADMIN_PAGE_CONTESTS_ACTIONS_PUB_TYPE": {
        "PLAN": "Запланировать",
        "NOW": "Сейчас",
    },
    
    "ADMIN_PAGE_CONTESTS_ACTIONS_ADD_SUBS": {
        "NOT_SUBS_NEEDED": "Подписчики не требуются",
        "FINISH_ADD_SUBS": "Закончить добавление"
    },
    
    "ADMIN_PAGE_CONTESTS_ACTIONS_FINISH_TYPE": {
        "PLAN": "Запланировать",
        "NUM_OF_PARTICIPANTS": "Количество участников",
    },
    
    "ADMIN_PAGE_CONTESTS_ACTIONS_FINAL_PUBLISH": {
        "PUBLISH": "Опубликовать",
        "EDIT": "Редактировать",
    },

    "ADMIN_PAGE_PRE_CONTEST_RESULT": {
        "CHANGE_WINNER": "Изменить одного",
        "CHANGE_WINNERS": "Изменить всех",
    },
}

CHANGE_WINNER_MARKUP = lambda contest_id: InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=markups_dict["ADMIN_PAGE_PRE_CONTEST_RESULT"]["CHANGE_WINNER"], 
                callback_data="changeWinner_%s" % contest_id),
            InlineKeyboardButton(
                text=markups_dict["ADMIN_PAGE_PRE_CONTEST_RESULT"]["CHANGE_WINNERS"], 
                callback_data="changeWinners_%s" % contest_id
                ),
        ]
    ]
)   


START_KEYBOARD_MARKUP = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text=markups_dict["START_KEYBOARD_MARKUP"]["SEND_CONTACT"], request_contact=True),
        ]
    ]
)

USER_MARKUP = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text=markups_dict["USER_MARKUP"]["PARTICIPATE"]),
        ]
    ]
)

BACK_ACTION = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text=markups_dict["BACK_ACTION"]["BACK"]),
        ]
    ]
)

CANCEL_ACTION = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text=markups_dict["CANCEL_ACTION"]["CANCEL"]),
        ]
    ]
)

CHOOSE_SUB_CHANNELS_AND_CANCEL_ACTION = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        # [
            # KeyboardButton(text=markups_dict["CANCEL_ACTION"]["CANCEL"]),
        # ],
        [
            KeyboardButton(text=markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS_ADD_SUBS"]["FINISH_ADD_SUBS"]),
        ]
    ]
)

ADMIN_START_MARKUP = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text=markups_dict["ADMIN_START_MARKUP"]["ADMINS"]),
            KeyboardButton(text=markups_dict["ADMIN_START_MARKUP"]["BLACKLIST"]),
        ],
        [
            KeyboardButton(text=markups_dict["ADMIN_START_MARKUP"]["CONTESTS"]),
            KeyboardButton(text=markups_dict["ADMIN_START_MARKUP"]["CHANNELS"]),
        ]
    ]
)

ADMIN_PAGE_ADMIN_ACTIONS = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text=markups_dict["ADMIN_PAGE_ADMIN_ACTIONS"]["GET_ADMINS"]),
            KeyboardButton(text=markups_dict["ADMIN_PAGE_ADMIN_ACTIONS"]["ADD_ADMIN"]),
        ],
        [
            KeyboardButton(text=markups_dict["ADMIN_PAGE_ADMIN_ACTIONS"]["BACK"]),
        ]
    ]
)

ADMIN_PAGE_BLACKLIST_ACTIONS = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            # KeyboardButton(text=markups_dict["ADMIN_PAGE_BLACKLIST_ACTIONS"]["GET_BLACKLIST"]),
            KeyboardButton(text=markups_dict["ADMIN_PAGE_BLACKLIST_ACTIONS"]["ADD_USER"]),
            KeyboardButton(text=markups_dict["ADMIN_PAGE_BLACKLIST_ACTIONS"]["REMOVE_USER"]),
        ],
        [
            KeyboardButton(text=markups_dict["ADMIN_PAGE_BLACKLIST_ACTIONS"]["BACK"]),
        ]
    ]
)

ADMIN_PAGE_CHANNELS_ACTIONS = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text=markups_dict["ADMIN_PAGE_CHANNELS_ACTIONS"]["ADD_BOT_TO_CHANNEL"]),
            KeyboardButton(text=markups_dict["ADMIN_PAGE_CHANNELS_ACTIONS"]["GET_CHANNELS"]),
        ],
        [
            KeyboardButton(text=markups_dict["ADMIN_PAGE_CHANNELS_ACTIONS"]["BACK"]),
        ]
    ]
)

ADMIN_PAGE_CHANNELS_ACTIONS_DEL_CONFIRM = lambda channel_id: (
    InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=markups_dict["ADMIN_PAGE_CHANNELS_ACTIONS_DEL_CONFIRM"]["YES_CONFIRM"],
                    callback_data="channel_ask_del_"+markups_dict["ADMIN_PAGE_CHANNELS_ACTIONS_DEL_CONFIRM"]["YES_CONFIRM"]+f"_{channel_id}",
                ),
                InlineKeyboardButton(
                    text=markups_dict["ADMIN_PAGE_CHANNELS_ACTIONS_DEL_CONFIRM"]["NO_FUCK_YOU_NO_WAY"],
                    callback_data="channel_ask_del_"+markups_dict["ADMIN_PAGE_CHANNELS_ACTIONS_DEL_CONFIRM"]["NO_FUCK_YOU_NO_WAY"]+f"_{channel_id}",
                ),
            ]
        ]
    )
)

ADMIN_PAGE_CONTESTS_ACTIONS = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text=markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS"]["GET_ACTIVE_CONTESTS"]),
        ],
        # [
        #     KeyboardButton(text=markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS"]["GET_CONTEST_RESULT"]),
        #     KeyboardButton(text=markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS"]["UPD_CONTEST_RESULT"]),
        # ],
        [
            KeyboardButton(text=markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS"]["ADD_CONTEST"]),
            # KeyboardButton(text=markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS"]["UPDATE_CONTEST"]),
        ],
        [
            # KeyboardButton(text=markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS"]["DELETE_CONTEST"]),
            KeyboardButton(text=markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS"]["BACK"]),
        ]
    ]
)

UPDATE_CONTEST_RESULT_ACTION = lambda contest_id: InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Редактировать", callback_data="upd_contest_%s" % contest_id),
        ],
        [
            InlineKeyboardButton(text="Удалить", callback_data="del_contest_%s" % contest_id),
        ]
    ]
)

ADMIN_PAGE_CONTESTS_ACTIONS_PUB_TYPE = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text=markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS_PUB_TYPE"]["PLAN"]),
            KeyboardButton(text=markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS_PUB_TYPE"]["NOW"]),
        ],
        [
            KeyboardButton(text=markups_dict["CANCEL_ACTION"]["CANCEL"]),
        ]
    ]
)

ADMIN_PAGE_CONTESTS_ACTIONS_ADD_SUBS = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text=markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS_ADD_SUBS"]["NOT_SUBS_NEEDED"]),
        ],
        [
            KeyboardButton(text=markups_dict["CANCEL_ACTION"]["CANCEL"]),
        ]
    ]
)

ADMIN_PAGE_CONTESTS_ACTIONS_FINISH_TYPE = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text=markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS_FINISH_TYPE"]["PLAN"]),
            KeyboardButton(text=markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS_FINISH_TYPE"]["NUM_OF_PARTICIPANTS"]),
        ],
        [
            KeyboardButton(text=markups_dict["CANCEL_ACTION"]["CANCEL"]),
        ]
    ]
)

ADMIN_PAGE_CONTESTS_ACTIONS_FINAL_PUBLISH = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text=markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS_FINAL_PUBLISH"]["PUBLISH"]),
            KeyboardButton(text=markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS_FINAL_PUBLISH"]["EDIT"]),
        ],
        [
            KeyboardButton(text=markups_dict["ADMIN_PAGE_CONTESTS_ACTIONS"]["BACK"]),
        ]
    ]
)


def build_channels_choice_inline_kbd(channels: list[ChannelGet], callback_data_prefix: str, add_cancel_button: bool = False) -> InlineKeyboardMarkup:
    buttons = []
    for i, channel in enumerate(channels):
        if i % 2 == 0:
            buttons.append([])
        buttons[-1].append(
            InlineKeyboardButton(text=channel.channel_tg_name, callback_data=f"{callback_data_prefix}{channel.channel_id}")
        )
    if add_cancel_button:
        buttons.append([InlineKeyboardButton(text="Finish", callback_data="finish_channel_add")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_contest_choice_inline_kbd_for_results(contests: list[ContestGet], callback_data_prefix: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for con in contests:
        callback_data = f"{callback_data_prefix}{con.id}"
        b.add(InlineKeyboardButton(text=con.channel_tg_name, callback_data=callback_data))
    return b.as_markup()
