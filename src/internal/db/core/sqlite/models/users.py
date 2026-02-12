from peewee import CharField, Check, IntegerField, Model, UUIDField

from db.core.sqlite.base import get_db


class User(Model):
    user_id = UUIDField(unique=True, null=False)
    tg_id = IntegerField()
    nickname = CharField()

    class Meta:
        table_name: str = "users"
        database = get_db()


class BlacklistRecord(Model):
    blacklist_id = UUIDField(unique=True, null=False)

    telegram_id = IntegerField(unique=True)
    nickname = CharField(null=True)

    added_at = IntegerField(constraints=[Check("added_at > 0")])
    days_of_blacklist = IntegerField(constraints=[Check("days_of_blacklist >= 1")])

    class Meta:
        table_name: str = "blacklist"
        database = get_db()


class Admin(Model):
    admin_id = UUIDField(unique=True, null=False)
    phone_number = IntegerField()
    tg_id = IntegerField()

    class Meta:
        table_name: str = "admins"
        database = get_db()
