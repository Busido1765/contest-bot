from random import choices
from typing import Optional

from aiogram import Bot
from aiogram.enums import ChatMemberStatus, ParseMode
from aiogram.types import FSInputFile, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity

from emoji import emojize


from db.repositories.abstract import ABCAsyncAdminsRespository, ABCAsyncContestRepository, ABCAsyncUsersRespository

from bot.base import BOT

from bot.messages.admin import ADDED_NEW_CHANNEL_MESSAGE, KICK_FROM_CHANNEL_MESSAGE, ALREADY_ADDED_CHANNEL_MESSAGE
from bot.messages.utils import make_added_new_channel_message, make_already_added_channel_message, make_contest_preview_message
from bot.keyboards.keyboards import CHANGE_WINNER_MARKUP

from app.dto.users import UserCreate
from shared.settings import SETTINGS, Environment
from shared.dates import HOUR, MINUTE, now
from shared.exceptions import AccessError, NotFoundError
from shared.types import ContestFinishKind, ContestPublicationKind, ContestState
from shared.miniapp import generate_miniapp_participate_link

from .dto.contest import ChannelCreate, ChannelGet, ContestCreate, ContestGet, ContestUpdate


class ContestApplication:
    def __init__(
        self,
        contest_repo: ABCAsyncContestRepository,
        user_repo: ABCAsyncUsersRespository,
        admin_repo: ABCAsyncAdminsRespository,
        bot: Optional[Bot] = None
    ):
        self._contest_repo = contest_repo
        self._temp_contest_storage: dict[int, dict] = {}
        self._users_repo = user_repo
        self._admins_repo = admin_repo
        self._bot = bot or BOT

        self._notified_contests: list[str] = []

    def get_channels(self):
        channels = self._contest_repo.get_channels(page=0, num=100)
        return channels

    def get_contests(self):
        contests, _ = self._contest_repo.get_many()
        return contests

    def add_contest_temp(self, user_tg_id: int, replace: bool = False, **data):
        if user_tg_id not in self._temp_contest_storage:
            self._temp_contest_storage[user_tg_id] = data
        else:
            if replace:
                self._temp_contest_storage[user_tg_id] = data
            else:
                raise ValueError(f"Конкурс уже существует")

    def delete_contest_temp(self, user_tg_id: int):
        if user_tg_id in self._temp_contest_storage:
            del self._temp_contest_storage[user_tg_id]

    def update_contest_temp(self, user_tg_id: int, **data):
        if user_tg_id in self._temp_contest_storage:
            for k, v in data.items():
                if v is not None:
                    self._temp_contest_storage[user_tg_id][k] = v
        else:
            raise ValueError(f"Конкурс не найден")

    def get_contest_temp(self, user_tg_id: int) -> dict | None:
        return self._temp_contest_storage.get(user_tg_id)

    def get_channel(self, channel_id: int) -> ChannelGet | None:
        return self._contest_repo.get_channel(channel_id)

    def delete_contest(self, contest_id: str):
        self._contest_repo.delete_contest(contest_id)

    def get_active_contests(self) -> list[ContestGet]:
        contests = self._contest_repo.get_active_contests(page=0, num=100)
        return contests
    
    def get_contests_for_results(self) -> list[ContestGet]:
        contests = self._contest_repo.get_active_contests(page=0, num=100)
        return contests

    def add_contest(self, contest: ContestCreate):
        id = self._contest_repo.create(contest)
        return id
    
    def update_contest_name(self, contest_id: str, name: str):
        self._contest_repo.update_contest_name(contest_id, name)

    def update_contest_description(self, contest_id: str, description: str, photo: str, entities: list[MessageEntity]):
        self._contest_repo.update_contest_description(contest_id, description, photo, entities)

    def update_contest_finish_kind(self, contest_id: str, finish_kind: str, **kwargs):
        self._contest_repo.update_contest_finish_kind(contest_id, finish_kind, **kwargs)

    def update_contest(self, contest_id: str, contest: ContestUpdate):
        self._contest_repo.update(contest_id, contest)

    def get_contest(self, contest_id):
        contest = self._contest_repo.get_one(contest_id)
        return contest
    
    def add_channel(self, channel_id: int, name: str):
        channel = ChannelCreate(channel_tg_name=name, channel_id=channel_id)
        id = self._contest_repo.add_channel(channel)
        return id

    def delete_channel(self, channel_id: int):
        self._contest_repo.remove_channel(channel_id)

    def choose_winners(self, participants: list, num_of_winners: int) -> list[str | int]:
        blacklist = self._admins_repo.get_all_from_blacklist()
        blacklist_ids = [b.user_tg_id for b in blacklist]
        participants = [p for p in participants if p not in blacklist_ids]
        winners = choices(participants, k=num_of_winners if len(participants) >= num_of_winners else len(participants))
        return winners

    def get_contest_results(self, contest_id: str):
        contest = self._contest_repo.get_one(contest_id)
        return contest

    def start_contest(self, contest_id: str):
        contest = self._contest_repo.get_one(contest_id)
        if contest is None:
            raise NotFoundError("Конкурс не найден")

        dump_ = contest.model_dump(no_dict=True)
        contest_upd = ContestUpdate.model_validate(dump_)
        contest_upd.state = ContestState.ACTIVE

        self._contest_repo.update(contest_id, contest_upd)

    async def save_and_pubslish_contest_temp(self, user_tg_id: int, is_update: bool = False):
        raw = self._temp_contest_storage.get(user_tg_id)
        if raw is None:
            raise ValueError(f"Конкурс не найден")

        raw["publication_date"] = raw.get("pulication_date")
        raw['entities'] = raw.get('entities', [])
        validated = ContestCreate.model_validate(raw)
        print(validated)
        validated.state = ContestState.ACTIVE

        del self._temp_contest_storage[user_tg_id]
        
        contest_id = self._contest_repo.create(validated)
        print(contest_id)
        # if validated.channel_tg_name:
        #     await self.publish_contest(contest_id, is_update)
        #     return
        if validated.pulication_kind == ContestPublicationKind.ON_FINISH:
            await self.publish_contest(contest_id, is_update)

    async def publish_contest(self, contest_id: str, is_update: bool = False):
        contest = self._contest_repo.get_one(contest_id)
        if contest is None:
            raise NotFoundError(f"Конкурс {contest_id} не найден")

        channel = self._contest_repo.get_channel_by_name(contest.channel_tg_name)
        if channel is None:
            raise NotFoundError(f"Канал {contest.channel_tg_name} не найден")

        dump_ = contest.model_dump(no_dict=True)
        contest_upd = ContestUpdate.model_validate(dump_)
        bot_name = await self._get_bot_name()

        kwargs = {
            "photo": FSInputFile(contest.media[0]),
            "chat_id": channel.channel_id,
            "caption": contest.text,
            "caption_entities": [MessageEntity(**x) for x in contest.entities],
            "reply_markup": InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(
                        text="Участвовать",
                        url=generate_miniapp_participate_link(contest_id=contest_id, bot_name=bot_name)
                    )
                ]]
            )
        }

        if is_update:
            try:
                kwargs['media'] = InputMediaPhoto(media=FSInputFile(contest.media[0]), caption=kwargs['caption'], caption_entities=contest.entities)
                kwargs['message_id'] = contest.post_message_id
                del kwargs['photo']
                del kwargs['caption']
                del kwargs['caption_entities']
                message = await BOT.edit_message_media(
                    **kwargs
                )
                return
            except Exception as err:
                print(err)
                kwargs['photo'] = FSInputFile(contest.media[0])
                kwargs['caption'] = contest.text
                kwargs['caption_entities'] = [MessageEntity(**x) for x in contest.entities]
                del kwargs['media']
                del kwargs['message_id']
                message = await BOT.send_photo(
                    **kwargs
                )
                contest_upd.state = ContestState.PUBLISHED
                contest_upd.post_message_id = message.message_id

                self._contest_repo.update(contest_id, contest_upd)
                return
        print('kwargs', kwargs)
        message = await BOT.send_photo(
            **kwargs
            )
        contest_upd.state = ContestState.PUBLISHED
        contest_upd.post_message_id = message.message_id

        self._contest_repo.update(contest_id, contest_upd)

    async def _get_bot_name(self) -> str:
        me = await self._bot.get_me()
        if me.username:
            return me.username

        return SETTINGS.BOT_NAME

    async def add_to_contest(self, user_tg_id: int, nickname: str, contest_id: str):
        contst = self._contest_repo.get_one(contest_id)
        if contst is None:
            return

        if contst.state == ContestState.FINISHED:
            return
        
        blacklist = self._admins_repo.get_all_from_blacklist()
        blacklist_ids = [b.user_tg_id for b in blacklist]
        if user_tg_id in blacklist_ids:
            print("blacklist")
            return

        admin = self._admins_repo.get_one_by_tg_id(user_tg_id)
        if admin is not None:
            print("admin")
            return

        if str(user_tg_id) in contst.participants:
            print("participant")
            return

        st = await self._check_subscriptions(user_tg_id, contst)
        if not st:
            print("not sub")
            return

        try:
            new_user = UserCreate(tg_id=user_tg_id, nickname=nickname)
            existing_user = self._users_repo.get_by_tg_id(user_tg_id)
            if existing_user is None:
                self._users_repo.create(new_user)
        except Exception as err:
            print("error", err)
            return

        try:
            contst.participants.append(str(user_tg_id))
            winners = self.choose_winners(contst.participants, contst.num_of_winners)
            contst.winners = winners

            dump_ = contst.model_dump(no_dict=True)
            upd = ContestUpdate.model_validate(dump_)
            self._contest_repo.update(contest_id, upd)
        except Exception as err:
            print("error", err)
            return

    async def participate_in_contest(self, user_tg_id: int, nickname: str, contest_id: str) -> int:
        contst = self._contest_repo.get_one(contest_id)
        if contst is None:
            raise NotFoundError("Конкурс не найден")

        if contst.state == ContestState.FINISHED:
            return 3  #, "Конкурс завершен"
        
        blacklist = self._admins_repo.get_all_from_blacklist()
        blacklist_ids = [b.user_tg_id for b in blacklist]
        if user_tg_id in blacklist_ids:
            raise AccessError("Вы находитесь в черном списке")

        admin = self._admins_repo.get_one_by_tg_id(user_tg_id)
        if admin is not None:
            raise AccessError("Администратор не может участвовать в конкурсе")

        if str(user_tg_id) in contst.participants:
            return 1  # , "Вы уже участвуете"

        st = await self._check_subscriptions(user_tg_id, contst)
        if not st:
            return 2  # , "Не выполнены условия"

        try:
            new_user = UserCreate(tg_id=user_tg_id, nickname=nickname)
            existing_user = self._users_repo.get_by_tg_id(user_tg_id)
            if existing_user is None:
                self._users_repo.create(new_user)
        except Exception as err:
            await self._notify_admins_about_errors("Ошибка участия", str(err), nickname)
            raise err

        try:
            contst.participants.append(str(user_tg_id))
            winners = self.choose_winners(contst.participants, contst.num_of_winners)
            contst.winners = winners

            dump_ = contst.model_dump(no_dict=True)
            upd = ContestUpdate.model_validate(dump_)
            self._contest_repo.update(contest_id, upd)

            if upd.finish_kind == ContestFinishKind.ON_WINNERS_NUM:
                if len(upd.participants) == upd.num_of_users_to_finish:
                    upd.state = ContestState.FINISHED
                    self._contest_repo.update(contst.id, upd)
                    await self._publish_results_as_bot(contest_id)
        except Exception as err:
            await self._notify_admins_about_errors("Ошибка обновления конкурса", str(err), nickname)
            raise err

        return 0  # вы участвуете

    async def check_and_update_contests(self):
        today = now(timezone=3)
        data, _ = self._contest_repo.get_many(num=10_000)

        for contest in data:
            print(contest)
            if contest.state not in [ContestState.ACTIVE, ContestState.PUBLISHED]:
                continue
            if contest.pulication_kind == ContestPublicationKind.PLANNED and contest.state != ContestState.PUBLISHED:
                if contest.publication_date is not None:
                    print(contest.publication_date, today)
                    if today >= contest.publication_date:
                        await self.publish_contest(contest.id)

            if contest.finish_kind == ContestFinishKind.PLANNED:
                if contest.finish_date is not None:
                    if contest.finish_date <= today:
                        contest.state = ContestState.FINISHED
                        self._contest_repo.update(contest.id, contest)
                        await self._publish_results_as_bot(contest_id=contest.id)
                    else:
                        time_to_finish = contest.finish_date - today
                        preresults_flag = False
                        if SETTINGS.ENV == Environment.DEV:
                            if MINUTE(4) <= time_to_finish < MINUTE(4) + 15:
                                preresults_flag = True
                        else:
                            if HOUR(1) <= time_to_finish < HOUR(1) + 15:
                                preresults_flag = True

                        if preresults_flag:
                            if contest.id not in self._notified_contests:
                                await self._notify_admins_about_contest_results(contest.id)
                                self._notified_contests.append(contest.id)

    async def _update_contest_and_post(self, contest_id: str, contest_upd: ContestUpdate):
        self._contest_repo.update(contest_id, contest_upd)

        channel = self._contest_repo.get_channel_by_name(contest_upd.channel_tg_name)
        if channel is None:
            raise NotFoundError("Channel for updating contest not found")

        await BOT.edit_message_caption(
            caption=contest_upd.text,
            message_id=contest_upd.post_message_id,
            chat_id=channel.channel_id
        )
        await BOT.edit_message_media(
            message_id=contest_upd.post_message_id,
            chat_id=channel.channel_id,
            media=FSInputFile(contest_upd.media[0])  # type:ignore
        )

    async def _notify_admins_about_contest_results(self, contest_id: str):
        contest = self._contest_repo.get_one(contest_id)
        if contest is None:
            raise NotFoundError("Contest not found")

        channel = self._contest_repo.get_channel_by_name(contest.channel_tg_name)
        if channel is None:
            raise NotFoundError("Channel not found")

        winners_raw = self._users_repo.get_many_by_tg_id([int(w) for w in contest.winners])  # type:ignore

        winners = " \n".join(f"{i+1}. @{w.nickname}" for i, w in enumerate(winners_raw))
        contest_results_text = (
            f"Предварительные результаты конкурса для {contest.channel_tg_name}:\n"
            f"{make_contest_preview_message(contest, '')}"
            f"Количество участников: {len(contest.participants)}\n"
            f"Победители:\n"
            f"{winners}"
        )

        admins, _ = self._admins_repo.get_many()
        for admin in admins:
            await BOT.send_message(
                chat_id=admin.tg_id,
                text=contest_results_text,
                parse_mode=ParseMode.HTML,
                reply_markup=CHANGE_WINNER_MARKUP(contest_id)
            )

    async def _publish_results_as_bot(self, contest_id: str):
        contest = self._contest_repo.get_one(contest_id)
        if contest is None:
            raise NotFoundError("Contest not found")

        channel = self._contest_repo.get_channel_by_name(contest.channel_tg_name)
        if channel is None:
            raise NotFoundError("Channel not found")

        print("PUBLISH:", contest)
        winners_raw = self._users_repo.get_many_by_tg_id([int(w) for w in contest.winners])  # type:ignore
        winners = " \n".join(f"{place+1}. @{w.nickname}" for place, w in enumerate(winners_raw))
        contest_results_text = (
            f"🎉 Результаты розыгрыша:\n\n"
            f"Победители:\n"
            f"{winners}"
        )

        await BOT.send_message(
            chat_id=channel.id,
            text=emojize(contest_results_text),
            reply_to_message_id=contest.post_message_id
        )

    async def _check_subscriptions(self, user_tg_id: int, contest: ContestGet) -> int:
        channel = self._contest_repo.get_channel_by_name(contest.channel_tg_name)
        if channel is None:
            raise NotFoundError("Channel not found")

        sub_check_result = True
        try:
            member = await BOT.get_chat_member(channel.channel_id, user_tg_id)
            if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
                sub_check_result = False
        except Exception:
            pass

        if not sub_check_result:
            return sub_check_result

        for channel_tag in contest.required_subs:
            try:
                member = await BOT.get_chat_member(channel_tag, user_tg_id)
            except Exception:
                continue
            if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
                sub_check_result = False
                break

        return sub_check_result

    async def _notify_users_about_new_channel(self, channel_name: str):
        users, _ = self._admins_repo.get_many()
        for user in users:
            await BOT.send_message(
                user.tg_id,
                text=make_added_new_channel_message(ADDED_NEW_CHANNEL_MESSAGE, channel_name)
            )

    async def _notify_users_about_channel_already_added(self, channel_name: str):
        users, _ = self._admins_repo.get_many()
        for user in users:
            await BOT.send_message(
                user.tg_id,
                text=make_already_added_channel_message(ALREADY_ADDED_CHANNEL_MESSAGE, channel_name)
            )

    async def _notify_users_about_channel_kick(self, channel_name: str):
        users, _ = self._admins_repo.get_many()
        for user in users:
            await BOT.send_message(
                user.tg_id,
                text=make_added_new_channel_message(KICK_FROM_CHANNEL_MESSAGE, channel_name)
            )

    async def _notify_admins_about_errors(self, message_prefix: str, error: str, user_nick: str):
        users, _ = self._admins_repo.get_many()
        for user in users:
            await BOT.send_message(
                user.tg_id,
                text=f"Ошибка при участии в конкурсе пользователя '{user_nick}' ({message_prefix}): {error}"
            )

    async def _notify_admins_about_new_version(self, new_version: str, description: str):
        users, _ = self._admins_repo.get_many()
        for user in users:
            await BOT.send_message(
                user.tg_id,
                text=f"Обновление: новая версия бота - {new_version}\n{description}"
            )
