from peewee import CharField, Model

from db.core.sqlite.base import get_db


class Info(Model):
    bot_version = CharField(null=False)

    class Meta:
        table_name: str = "info"
        database = get_db()
