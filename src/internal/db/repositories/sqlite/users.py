from typing import List

from peewee import SqliteDatabase

from db.core.sqlite.base import get_db
from db.core.sqlite.models.users import Admin, BlacklistRecord, User
from db.repositories.abstract import ABCAsyncUsersRespository, ABCAsyncAdminsRespository, PaginationHasNextFlag

from app.dto.users import AdminCreate, AdminGet, AdminUpdate, BlackListRecordCreate, BlackListRecordGet, UserCreate, UserGet, UserUpdate
from shared.uids import get_id


class AsyncSqliteUsersRespository(ABCAsyncUsersRespository):
    def __init__(self, db_client: SqliteDatabase) -> None:
        self.db_client = db_client or get_db()

    def get_by_tg_id(self, tg_id: int) -> UserGet | None:
        try:
            result = User.get(User.tg_id == tg_id)
        except:
            return None
        return UserGet(tg_id=result.tg_id, nickname=result.nickname, id=str(result.user_id))

    def get_one(self, user_id: str) -> UserGet | None:
        try:
            result = User.get(User.user_id==user_id)
        except:
            return None
        return UserGet(tg_id=result.tg_id, nickname=result.nickname, id=str(result.user_id))

    def get_by_nickname(self, nickname: str) -> UserGet | None:
        try:
            result = User.get(User.nickname==nickname)
        except:
            return
        return UserGet(tg_id=result.tg_id, nickname=result.nickname, id=str(result.user_id))

    def get_from_blacklist(self, user_tg_id: int) -> BlackListRecordGet | None:
        try:
            user = User.get(User.tg_id == user_tg_id)
            bl = BlacklistRecord.get(BlacklistRecord.telegram_id==user.tg_id)
        except:
            return

        return BlackListRecordGet(
            telegram_id=bl.telegram_id,
            nickname=bl.nickname,
            added_at=bl.added_at,
            days_of_blacklist=bl.days_of_blacklist,
            id=str(bl.blacklist_id)
        )

    def get_many(self, page: int = 0, num: int = 1000) -> tuple[List[UserGet], PaginationHasNextFlag]:
        total = User.select().count()
        has_next = True if total > page*num+num else False

        data = [
            UserGet(tg_id=con.tg_id, nickname=con.nickname, id=str(con.user_id))
            for con in User.select().offset(page*num).limit(num)
        ]

        return data, has_next

    def get_many_by_tg_id(self, tg_ids: list[int]) -> list[UserGet]:
        print("get_many_by_tg_id::tg_ids:", tg_ids)
        data = [
            UserGet(
                id=str(con.user_id),
                tg_id=con.tg_id,
                nickname=con.nickname,
            )
            for con in (
                User
                .select()
                .where(User.tg_id.in_(tg_ids))
            )
        ]
        print("get_many_by_tg_id::data:", data)

        return data

    def create(self, user: UserCreate) -> str:
        new_contest = User(
            user_id=get_id(),
            tg_id=user.tg_id,
            nickname=user.nickname,
        )
        new_contest.save(force_insert=True)
        return str(new_contest.user_id)

    def update(self, user_id: str, user: UserUpdate):
        (
            User
            .update(
                tg_id=user.tg_id,
                nickname=user.nickname
            )
            .where(User.user_id==user_id)
            .execute()
        )


class AsyncSqliteAdminsRespository(ABCAsyncAdminsRespository):
    def __init__(self, db_client: SqliteDatabase) -> None:
        self.db_client = db_client or get_db()

    def get_all_from_blacklist(self):
        return BlacklistRecord.select()

    def get_one(self, admin_id: str) -> AdminGet | None:
        try:
            result = Admin.get(Admin.admin_id==admin_id)
        except:
            return
        return AdminGet(tg_id=result.tg_id, phone_number=result.phone_number, id=str(result.admin_id))

    def get_by_phone(self, phone_number: int) -> AdminGet | None:
        try:
            result = Admin.get(Admin.phone_number==phone_number)
        except:
            return
        return AdminGet(tg_id=result.tg_id, phone_number=result.phone_number, id=str(result.admin_id))

    def add_to_blacklist(self, record: BlackListRecordCreate) -> str:
        new_contest = BlacklistRecord(
            blacklist_id=get_id(),
            telegram_id=record.telegram_id,
            nickname=record.nickname,
            added_at=record.added_at,
            days_of_blacklist=record.days_of_blacklist,
        )
        new_contest.save(force_insert=True)
        return str(new_contest.blacklist_id)

    def remove_from_blacklist(self, user_tg_id: int):
        BlacklistRecord.delete().where(BlacklistRecord.telegram_id == user_tg_id).execute()

    def get_from_blacklist(self, admin_id: str) -> BlackListRecordGet | None:
        try:
            admin: Admin = Admin.get(Admin.admin_id==admin_id)
            bl = BlacklistRecord.get(BlacklistRecord.telegram_id==admin.tg_id)
        except:
            return

        return BlackListRecordGet(
            telegram_id=bl.telegram_id,
            nickname=bl.nickname,
            added_at=bl.added_at,
            days_of_blacklist=bl.days_of_blacklist,
            id=str(bl.blacklist_id)
        )

    def get_many(self, page: int = 0, num: int = 1000) -> tuple[List[AdminGet], PaginationHasNextFlag]:
        total = Admin.select().count()
        has_next = True if total > page*num+num else False

        data = [
            AdminGet(tg_id=con.tg_id, phone_number=con.phone_number, id=str(con.admin_id))
            for con in Admin.select().offset(page*num).limit(num)
        ]

        return data, has_next

    def get_blacklist(self, page: int = 0, num: int = 25)  -> tuple[List[BlackListRecordGet], PaginationHasNextFlag]:
        total = BlacklistRecord.select().count()
        has_next = True if total > page*num+num else False

        data = [
            BlackListRecordGet(
                telegram_id=con.telegram_id,
                nickname=con.nickname,
                added_at=con.added_at,
                days_of_blacklist=con.days_of_blacklist,
                id=str(con.blacklist_id)
            )
            for con in BlacklistRecord.select().offset(page*num).limit(num)
        ]

        return data, has_next

    def create(self, admin: AdminCreate) -> str:
        new_contest = Admin(
            admin_id=get_id(),
            phone_number=admin.phone_number,
            tg_id=admin.tg_id
        )
        new_contest.save(force_insert=True)
        return str(new_contest.admin_id)

    def delete_old_admins(self, new_admins_tg_ids: list[int]):
        Admin.delete().where(Admin.tg_id not in new_admins_tg_ids).execute()

    def update(self, admin_id: str, admin: AdminUpdate):
        (
            Admin
            .update(
                phone_number=admin.phone_number,
                tg_id=admin.tg_id
            )
            .where(Admin.admin_id==admin_id)
        )

    def get_one_by_tg_id(self, tg_id: int) -> AdminGet | None:
        try:
            admin = Admin.get(Admin.tg_id == tg_id)
        except:
            return
        return AdminGet(tg_id=admin.tg_id, phone_number=admin.phone_number, id=str(admin.admin_id))

    def delete_admin(self, phone: int):
        Admin.delete().where(Admin.phone_number == phone).execute()
