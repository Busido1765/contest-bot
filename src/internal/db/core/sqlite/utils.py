import os

from shared.settings import SETTINGS

from db.repositories.sqlite.users import AsyncSqliteAdminsRespository, User, Admin, BlacklistRecord
from db.repositories.sqlite.contest import Contest, Channel

from app.dto.users import AdminCreate

from .base import get_db
from .models.info import Info


def prepare_db():
    if not os.path.exists(SETTINGS.SQLITE_DB_URI):
        path = SETTINGS.SQLITE_DB_URI.split("sqlite://")[-1]

        with open(path, "w"): pass

        db = get_db()

        db.connect()
        db.create_tables([
            User, Admin, BlacklistRecord, Contest, Channel, Info
        ])
    else:
        db = get_db()

    admin_db = AsyncSqliteAdminsRespository(db)

    # for tg_id, phone in zip(SETTINGS.ROOT_ADMIN_TG_IDS, SETTINGS.ROOT_ADMIN_PHONES):
    for tg_id in SETTINGS.ROOT_ADMIN_TG_IDS:
        a = admin_db.get_one_by_tg_id(tg_id)
        if a is not None:
            continue

        try:
            admin_db.create(
                AdminCreate(
                    phone_number=-1,
                    tg_id=tg_id,
                )
            )
        except Exception as err:
            print(err)

    try:
        admin_db.delete_old_admins(SETTINGS.ROOT_ADMIN_TG_IDS)
    except Exception as err:
        print(err)
