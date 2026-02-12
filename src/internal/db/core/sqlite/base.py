from peewee import SqliteDatabase

from shared.settings import SETTINGS


db: dict = {"sqlite": None}


def get_db(uri: str | None = None):
    uri = uri or SETTINGS.SQLITE_DB_URI
    if (db_ := db["sqlite"]) is not None:
        return db_

    db["sqlite"] = SqliteDatabase(uri)
    return db["sqlite"]
