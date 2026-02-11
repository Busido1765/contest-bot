__all__ = [
    "BOT",
    "DISPATCHER",
    "States"
]


from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State

from shared.settings import SETTINGS


class States(StatesGroup):
    start = State()

    admin_start = State()
    user_start = State()

    admin_user_and_admin_actions = State()
    admin_user_actions = State()

    admin_admin_actions = State()
    admin_all_blacklist_actions = State()
    admin_all_contest_actions = State()
    admin_all_channel_actions = State()

    admin_add_admin_actions = State()
    admin_add_admin_actions_add_admin = State()
    admin_delete_admin_actions = State()

    admin_bl_add_user_action = State()
    admin_bl_remove_user_action = State()
    admin_bl_add_user_choose_num_of_block_action = State()
    admin_bl_del_user_action = State()

    admin_channel_del_channel_action = State()
    admin_channel_del_channel_confirm_action = State()
    admin_channel_add_bot_to_channel_action = State()

    admin_contest_add_finiseed_sub_add = State()

    admin_contest_add_contest_choose_finish_get_data_num_of_users = State()
    admin_contest_add_contest_choose_channel_for_sub_check = State()
    admin_contest_get_contest_result_action = State()
    admin_contest_delete_contest = State()
    admin_contest_add_contest_choose_channel = State()
    admin_contest_add_contest_name = State()
    admin_contest_add_contest_add_text = State()
    admin_contest_add_contest_add_media = State()
    admin_contest_add_contest_add_num_of_users = State()
    admin_contest_add_contest_choose_publication = State()
    admin_contest_add_contest_choose_publication_values = State()
    admin_contest_add_contest_add_subs = State()
    admin_contest_add_contest_choose_finish = State()
    admin_contest_add_contest_choose_finish_get_data = State()
    admin_contest_add_contest_preview = State()
    admin_contest_add_contest_done = State()

    admin_contest_upd_contest_result = State()

    admin_contest_upd = State()
    admin_contest_upd_winners = State()
    admin_contest_upd_winners_shuffle = State()
    admin_contest_upd_winners_del = State()
    admin_contest_change_winner = State()
    admin_contest_change_winners = State()

    admin_contest_upd_name = State()
    admin_contest_upd_text = State()
    admin_contest_upd_finish = State()
    admin_contest_upd_finish_get_data = State()
    admin_contest_upd_finish_get_data_num_of_users = State()

DISPATCHER = Dispatcher(
    storage=MemoryStorage(),
    name="c_dispatcher"
)
BOT = Bot(token=SETTINGS.BOT_TOKEN)
