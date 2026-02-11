from abc import ABC, abstractmethod
from typing import List, Tuple, TypeAlias

from aiogram.types import MessageEntity

from app.dto.contest import ChannelCreate, ChannelGet, ContestCreate, ContestGet, ContestUpdate
from app.dto.users import AdminCreate, AdminGet, AdminUpdate, BlackListRecordCreate, BlackListRecordGet, UserCreate, UserGet, UserUpdate


PaginationHasNextFlag: TypeAlias = bool


class ABCAsyncContestRepository(ABC):
    @abstractmethod
    def __init__(self, db_client) -> None:
        pass

    @abstractmethod
    def get_one(self, contest_id: str) -> ContestGet | None:
        pass

    @abstractmethod
    def update_contest_name(self, contest_id: str, name: str):
        pass

    @abstractmethod
    def update_contest_description(self, contest_id: str, description: str, photo: str, entities: list[MessageEntity]):
        pass

    @abstractmethod
    def update_contest_finish_kind(self, contest_id: str, finish_kind: str, **kwargs):
        pass

    @abstractmethod
    def get_channels(self, page: int = 0, num: int = 1000) -> list[ChannelGet]:
        pass

    @abstractmethod
    def get_channel(self, channel_id: int) -> ChannelGet | None:
        pass

    @abstractmethod
    def get_channel_by_name(self, channel_name: str) -> ChannelGet | None:
        pass

    @abstractmethod
    def delete_contest(self, contest_id: str):
        pass

    @abstractmethod
    def get_active_contests(self, page=0, num=1000) -> list[ContestGet]:
        pass

    @abstractmethod
    def get_many(self, page: int = 0, num: int = 1000) -> Tuple[List[ContestGet], PaginationHasNextFlag]:
        pass

    @abstractmethod
    def create(self, contest: ContestCreate) -> str:
        pass

    @abstractmethod
    def add_channel(self, channel: ChannelCreate) -> str:
        pass

    @abstractmethod
    def remove_channel(self, channel_id: int):
        pass

    @abstractmethod
    def update(self, contest_id: str, contest: ContestUpdate):
        pass


class ABCAsyncUsersRespository(ABC):
    @abstractmethod
    def __init__(self, db_client) -> None:
        pass

    @abstractmethod
    def get_one(self, user_id: str) -> UserGet | None:
        pass

    @abstractmethod
    def get_by_tg_id(self, tg_id: int) -> UserGet | None:
        pass

    @abstractmethod
    def get_many_by_tg_id(self, tg_ids: list[int]) -> list[UserGet]:
        pass

    @abstractmethod
    def get_by_nickname(self, nickname: str) -> UserGet | None:
        pass

    @abstractmethod
    def get_from_blacklist(self, user_tg_id: int) -> BlackListRecordGet | None:
        pass

    @abstractmethod
    def get_many(self, page: int = 0, num: int = 1000) -> Tuple[List[UserGet], PaginationHasNextFlag]:
        pass

    @abstractmethod
    def create(self, user: UserCreate) -> str:
        pass

    @abstractmethod
    def update(self, user_id: str, user: UserUpdate):
        pass


class ABCAsyncAdminsRespository(ABC):
    @abstractmethod
    def __init__(self, db_client) -> None:
        pass

    @abstractmethod
    def get_all_from_blacklist(self):
        pass

    @abstractmethod
    def get_one(self, admin_id: str) -> AdminGet | None:
        pass

    @abstractmethod
    def get_by_phone(self, phone_number: int) -> AdminGet | None:
        pass

    @abstractmethod
    def get_many(self, page: int = 0, num: int = 1000) -> Tuple[List[AdminGet], PaginationHasNextFlag]:
        pass

    @abstractmethod
    def create(self, admin: AdminCreate) -> str:
        pass

    @abstractmethod
    def get_blacklist(self, page: int = 0, num: int = 25)  -> Tuple[List[BlackListRecordGet], PaginationHasNextFlag]:
        pass

    @abstractmethod
    def add_to_blacklist(self, record: BlackListRecordCreate) -> str:
        pass

    @abstractmethod
    def remove_from_blacklist(self, user_tg_id: int):
        pass

    @abstractmethod
    def update(self, admin_id: str, admin: AdminUpdate):
        pass

    @abstractmethod
    def get_one_by_tg_id(self, tg_id: int) -> AdminGet | None:
        pass

    @abstractmethod
    def delete_admin(self, phone: int):
        pass
