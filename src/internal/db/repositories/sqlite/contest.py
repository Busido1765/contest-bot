from typing import List
from peewee import SqliteDatabase

from aiogram.types import MessageEntity

from db.core.sqlite.base import get_db
from db.core.sqlite.models.contests import Channel, Contest
from db.repositories.abstract import ABCAsyncContestRepository, PaginationHasNextFlag

from app.dto.contest import ChannelCreate, ChannelGet, ContestCreate, ContestGet, ContestUpdate

from shared.types import ContestState
from shared.uids import get_id


class AsyncSqliteContestRespository(ABCAsyncContestRepository):
    def __init__(self, db_client: SqliteDatabase) -> None:
        self.db_client = db_client or get_db()

    def get_one(self, contest_id: str) -> ContestGet | None:
        try:
            result = Contest.get(Contest.contest_id==contest_id)
        except:
            return

        return ContestGet(
            id=str(result.contest_id),
            channel_tg_name=result.channel_tg_name,
            contest_name=result.contest_name,
            text=result.text,
            entities=list(result.text_entities),
            text_link=result.text_link,
            num_of_winners=result.num_of_winners,
            num_of_users_to_finish=result.num_of_users_to_finish,
            pulication_kind=result.pulication_kind,
            publication_date=result.publication_date,
            finish_kind=result.finish_kind,
            finish_date=result.finish_date,
            media=result.media["media"],
            participants=result.participants["participants"],
            winners=result.winners["winners"],
            required_subs=result.required_subs["required_subs"],
            post_message_id=result.post_message_id,
            state=result.state,
        )

    def get_many(self, page: int = 0, num: int = 1000) -> tuple[List[ContestGet], PaginationHasNextFlag]:
        total = Contest.select().count()
        has_next = True if total > page*num+num else False

        data = [
            ContestGet(
                id=str(con.contest_id),
                channel_tg_name=con.channel_tg_name,
                contest_name=con.contest_name,
                text=con.text,
                entities=list(con.text_entities),
                text_link=con.text_link,
                num_of_winners=con.num_of_winners,
                num_of_users_to_finish=con.num_of_users_to_finish,
                pulication_kind=con.pulication_kind,
                publication_date=con.publication_date,
                finish_kind=con.finish_kind,
                finish_date=con.finish_date,
                media=con.media["media"],
                participants=con.participants["participants"],
                winners=con.winners["winners"],
                required_subs=con.required_subs["required_subs"],
                post_message_id=con.post_message_id,
                state=con.state,
            )
            for con in Contest.select().offset(page*num).limit(num)
        ]

        return data, has_next

    def create(self, contest: ContestCreate) -> str:
        new_contest = Contest(
            contest_id=get_id(),
            channel_tg_name=contest.channel_tg_name,
            contest_name=contest.contest_name,
            text=contest.text,
            text_entities=contest.entities,
            text_link=contest.text_link,
            num_of_winners=contest.num_of_winners,
            num_of_users_to_finish=contest.num_of_users_to_finish,
            pulication_kind=contest.pulication_kind,
            publication_date=contest.publication_date,
            finish_kind=contest.finish_kind,
            finish_date=contest.finish_date,
            post_message_id=contest.post_message_id,
            state=contest.state,
            media={"media": contest.media},
            winners={"winners": contest.winners},
            participants={"participants": contest.participants},
            required_subs={"required_subs": contest.required_subs},
        )
        new_contest.save(force_insert=True)
        return str(new_contest.contest_id)

    def add_channel(self, channel: ChannelCreate) -> str:
        new_channel = Channel(
            channel_id=channel.channel_id,
            channel_tg_name=channel.channel_tg_name,
        )
        new_channel.save(force_insert=True)
        return str(new_channel.channel_id)

    def remove_channel(self, channel_id: int):
        Channel.delete().where(Channel.channel_id==channel_id).execute()
        self.db_client.commit()

    def update(self, contest_id: str, contest: ContestUpdate):
        (
            Contest
            .update(
                state=contest.state,
                channel_tg_name=contest.channel_tg_name,
                text=contest.text,
                text_entities=contest.entities,
                text_link=contest.text_link,
                num_of_winners=contest.num_of_winners,
                pulication_kind=contest.pulication_kind,
                publication_date=contest.publication_date,
                finish_kind=contest.finish_kind,
                finish_date=contest.finish_date,
                post_message_id=contest.post_message_id,
                media={"media": contest.media},
                winners={"winners": contest.winners},
                participants={"participants": contest.participants},
                required_subs={"required_subs": contest.required_subs},
            )
            .where(Contest.contest_id==contest_id)
            .execute()
        )

    def update_contest_name(self, contest_id: str, name: str):
        (
            Contest
            .update(contest_name=name)
            .where(Contest.contest_id == contest_id)
            .execute()
        )

    def update_contest_description(self, contest_id: str, description: str, photo: str, entities: list[MessageEntity]):
        (
            Contest
            .update(
                text=description,
                media={"media": photo},
                text_entities={"text_entities": entities},
            )
            .where(Contest.contest_id == contest_id)
            .execute()
        )

    def update_contest_finish_kind(self, contest_id: str, finish_kind: str, **kwargs):
        print('kwargs', kwargs)
        print('finish_kind', finish_kind)
        (
            Contest
            .update(
                finish_kind=finish_kind,
                **kwargs
            )
            .where(Contest.contest_id == contest_id)
            .execute()
        )

    def get_channels(self, page: int = 0, num: int = 1000) -> list[ChannelGet]:
        data = [
            ChannelGet(
                id=str(con.channel_id),
                channel_tg_name=con.channel_tg_name,
                channel_id=con.channel_id,
            )
            for con in Channel.select().offset(page*num).limit(num)
        ]

        return data

    def get_channel(self, channel_id: int) -> ChannelGet | None:
        try:
            result = Channel.get(Channel.channel_id==channel_id)
        except:
            return
        return ChannelGet(
            id=str(result.channel_id),
            channel_id=result.channel_id,
            channel_tg_name=result.channel_tg_name,
        )

    def get_channel_by_name(self, channel_name: str) -> ChannelGet | None:
        try:
            result = Channel.get(Channel.channel_tg_name==channel_name)
        except:
            return
        return ChannelGet(
            id=str(result.channel_id),
            channel_id=result.channel_id,
            channel_tg_name=result.channel_tg_name,
        )

    def delete_contest(self, contest_id: str):
        Contest.delete().where(Contest.contest_id == contest_id).execute()

    def get_active_contests(self, page=0, num=1000) -> list[ContestGet]:
        data = [
            ContestGet(
                id=str(con.contest_id),
                channel_tg_name=con.channel_tg_name,
                contest_name=con.contest_name,
                text=con.text,
                entities=list(con.text_entities),
                text_link=con.text_link,
                num_of_winners=con.num_of_winners,
                num_of_users_to_finish=con.num_of_users_to_finish,
                pulication_kind=con.pulication_kind,
                publication_date=con.publication_date,
                finish_kind=con.finish_kind,
                finish_date=con.finish_date,
                post_message_id=con.post_message_id,
                media=con.media["media"],
                participants=con.participants["participants"],
                winners=con.winners["winners"],
                required_subs=con.required_subs["required_subs"],
                state=con.state,
            )
            for con in (
                Contest
                .select()
                .where(Contest.state != ContestState.FINISHED)
                .offset(page*num)
                .limit(num)
            )
        ]

        return data
