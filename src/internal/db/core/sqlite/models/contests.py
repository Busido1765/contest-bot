from peewee import CharField, IntegerField, Model, UUIDField
from peewee_extra_fields import EnumField, JSONField

from db.core.sqlite.base import get_db

from shared.types import ContestFinishKind, ContestPublicationKind, ContestState


class Contest(Model):
    contest_id = UUIDField(unique=True, null=False)
    contest_name = CharField(max_length=255)
    channel_tg_name = CharField()

    text = CharField(max_length=1000)
    text_entities = JSONField(null=True)
    text_link = CharField(max_length=1000, null=True)
    num_of_winners = IntegerField()

    pulication_kind = EnumField(enum=ContestPublicationKind)
    publication_date = IntegerField(null=True)

    finish_kind = EnumField(enum=ContestFinishKind)
    num_of_users_to_finish = IntegerField(default=None, null=True)
    finish_date = IntegerField(null=True)

    post_message_id = IntegerField(null=True)

    media = JSONField()
    participants = JSONField()
    winners = JSONField(null=True)
    required_subs = JSONField(null=True)

    state = EnumField(enum=ContestState)

    class Meta:
        table_name: str = "contests"
        database = get_db()


class Channel(Model):
    channel_id = IntegerField()
    channel_tg_name = CharField(max_length=255)

    class Meta:
        table_name: str = "channels"
        database = get_db()
