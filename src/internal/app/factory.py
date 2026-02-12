from enum import Enum
from abc import ABC, abstractmethod

from peewee import SqliteDatabase

from db.repositories.sqlite.contest import AsyncSqliteContestRespository
from db.repositories.sqlite.users import AsyncSqliteAdminsRespository, AsyncSqliteUsersRespository
from db.core.sqlite.base import get_db

from .contest import ContestApplication
from .users import UsersApplication, AdminApplication


class AppKind(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    CONTEST = "CONTEST"


class AbstractApplicationFactory(ABC):
    @abstractmethod
    def __init__(self, db_client) -> None:
        pass

    @abstractmethod
    def get_users_app(self) -> UsersApplication:
        raise NotImplemented

    @abstractmethod
    def get_contest_app(self) -> ContestApplication:
        raise NotImplemented

    @abstractmethod
    def get_admins_app(self) -> AdminApplication:
        raise NotImplemented


class SqliteBasedApplicationFactory(AbstractApplicationFactory):
    def __init__(self, db_client: SqliteDatabase | None = None) -> None:
        self.db_client = db_client or get_db()

        urepo = AsyncSqliteUsersRespository(self.db_client)
        arepo = AsyncSqliteAdminsRespository(self.db_client)

        self._users_app = UsersApplication(urepo)
        self._contest_app = ContestApplication(AsyncSqliteContestRespository(self.db_client), urepo, arepo)
        self._admin_app = AdminApplication(arepo, urepo)

    def get_users_app(self) -> UsersApplication:
        return self._users_app

    def get_contest_app(self) -> ContestApplication:
        return self._contest_app

    def get_admins_app(self) -> AdminApplication:
        return self._admin_app


class ApplicationFactory:
    def __init__(self, factory: AbstractApplicationFactory | None = None) -> None:
        self._factory = factory or SqliteBasedApplicationFactory()
        self._user_app = self._factory.get_users_app()
        self._admin_app = self._factory.get_admins_app()
        self._contest_app = self._factory.get_contest_app()

    def get(self, app_kind: AppKind):
        if app_kind == AppKind.USER:
            return self._user_app
        if app_kind == AppKind.ADMIN:
            return self._admin_app
        if app_kind == AppKind.CONTEST:
            return self._contest_app


SQLITE_APP_FACTORY = ApplicationFactory(SqliteBasedApplicationFactory())
IN_MEMORY_APP_FACTORY = ApplicationFactory()
