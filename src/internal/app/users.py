
from db.repositories.abstract import ABCAsyncAdminsRespository, ABCAsyncUsersRespository

from app.dto.users import AdminCreate, AdminGet, BlackListRecordCreate, UserCreate

from shared.dates import now
from shared.exceptions import NotFoundError


class UsersApplication:
    def __init__(self, users_repo: ABCAsyncUsersRespository) -> None:
        self._users_repo = users_repo

    def get_user(self, nickname: str):
        user = self._users_repo.get_by_nickname(nickname)
        return user
    
    def get_user_by_tg_id(self, id: int):
        user = self._users_repo.get_by_tg_id(id)
        return user

    def add_user(self, user: UserCreate):
        id = self._users_repo.create(user)
        return id
    
    def get_many_by_tg_id(self, ids: list[int]):
        users = self._users_repo.get_many_by_tg_id(ids)
        return users


class AdminApplication:
    def __init__(
        self,
        admins_repo: ABCAsyncAdminsRespository,
        users_repo: ABCAsyncUsersRespository
    ) -> None:
        self._admins_repo = admins_repo
        self._users_repo = users_repo
        self._temp_blacklist_storage: dict[int, dict] = {}

    def get_admin(self, phone_number: int):
        a = self._admins_repo.get_by_phone(phone_number)
        return a

    def get_admin_by_tg_id(self, tg_id: int) -> AdminGet | None:
        admin = self._admins_repo.get_one_by_tg_id(tg_id)
        return admin

    def get_all_admins(self) -> list[AdminGet]:
        admins, _ = self._admins_repo.get_many()
        return admins

    def delete_admin(self, phone: int) -> None:
        self._admins_repo.delete_admin(phone)

    def add_user_to_blacklist_without_ban_days(self, user_id: str, admin_tg_id: int, force_add: bool = False) -> None:
        
        if force_add:
            self._admins_repo.add_to_blacklist(
                BlackListRecordCreate(
                    telegram_id=user_id,
                    nickname=None,
                    added_at=now(),
                    days_of_blacklist=9999,
                )
            )
            return

        if admin_tg_id in self._temp_blacklist_storage:
            raise ValueError("Blacklist record already exists for this admin")

        self._temp_blacklist_storage[admin_tg_id] = {
            "telegram_id": user_id,
        }

    def update_blacklist_record_block_days(self, admin_tg_id: int, days: int):
        if admin_tg_id not in self._temp_blacklist_storage:
            raise ValueError("Blacklist record not exists for this admin")

        self._temp_blacklist_storage[admin_tg_id].update({"days_of_blacklist": days, "added_at": now()})

        bl_raw = self._temp_blacklist_storage[admin_tg_id]

        self._admins_repo.add_to_blacklist(
            BlackListRecordCreate(
                telegram_id=bl_raw["telegram_id"],
                nickname=bl_raw["nickname"],
                added_at=bl_raw["added_at"],
                days_of_blacklist=bl_raw["days_of_blacklist"],
            )
        )

        del self._temp_blacklist_storage[admin_tg_id]

    def add_admin(self, admin: AdminCreate):
        self._admins_repo.create(admin)

    def get_blacklist(self, page: int = 0, num: int = 10):
        blacklist = self._admins_repo.get_blacklist(page, num)
        return blacklist

    def add_user_to_blacklist(self, bl: BlackListRecordCreate):
        self._admins_repo.add_to_blacklist(bl)

    def remove_user_from_blacklist(self, user_tg_id: int):
        self._admins_repo.remove_from_blacklist(user_tg_id)

    # cronjobify
    def update_blacklist(self):
        DAY = 24*3600
        today = now()

        blacklist, _ = self.get_blacklist(num=10_000)

        for user_bl in blacklist:
            if user_bl.days_of_blacklist == 0:
                continue

            date_of_bl_expiration = user_bl.added_at + DAY*user_bl.days_of_blacklist

            if today >= date_of_bl_expiration:
                continue

            # push this id to a set and the delete as a whole to reduce number of requests
            self.remove_user_from_blacklist(user_bl.telegram_id)
