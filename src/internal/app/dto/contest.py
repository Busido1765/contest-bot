from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from aiogram.types import MessageEntity

import json

from shared.uids import get_id
from shared.dates import now

from shared.types import (
    ContestFinishKind,
    ContestPublicationKind,
    ContestState,
    UnixTimestamp
)


class ContestCreate(BaseModel):
    channel_tg_name: str
    contest_name: str
    text: str
    entities: list[dict[str, Any]] | None = Field(default_factory=list)
    text_link: str | None = None
    num_of_winners: int

    pulication_kind: ContestPublicationKind
    publication_date: Optional[UnixTimestamp] = None

    finish_kind: ContestFinishKind
    num_of_users_to_finish: Optional[int] = None
    finish_date: Optional[UnixTimestamp] = None

    media: list[str] = Field(default_factory=list)
    participants: list[str | int] = Field(default_factory=list)
    winners: list[str | int] = Field(default_factory=list)

    required_subs: list[str] = Field(default_factory=list)

    post_message_id: Optional[int] = None

    state: ContestState = ContestState.ONEDIT

    @field_validator("entities", mode="before")
    @classmethod
    def validate_entities(cls, entities: list[MessageEntity]) -> list[dict[str, Any]]:
        print('in validate_entities', entities, type(entities))
        if isinstance(entities, str):
            entities = json.loads(entities)
        if isinstance(entities, dict):
            print(entities)
            return [entities]
        print(entities)
        return [x for x in entities if isinstance(x, dict)] 

    def model_dump(self, no_dict: bool = False, *args, **kwargs) -> dict[str, Any]:
        dict_repr = super().model_dump(*args, **kwargs)
        dict_repr["id"] = get_id()

        if no_dict is False:
            dict_repr["media"] = {"media": self.media}
            dict_repr["participants"] = {"participants": self.participants}
            dict_repr["winners"] = {"winners": self.winners}
            dict_repr["required_subs"] = {"required_subs": self.required_subs}
        else:
            dict_repr["media"] = self.media
            dict_repr["participants"] = self.participants
            dict_repr["winners"] = self.winners
            dict_repr["required_subs"] = self.required_subs

        return dict_repr


class ContestUpdate(ContestCreate):
    pass


class ContestGet(ContestCreate):
    id: str


class ChannelCreate(BaseModel):
    channel_tg_name: str
    channel_id: int

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        dict_repr = super().model_dump(*args, **kwargs)
        dict_repr["id"] = get_id()
        return dict_repr


class ChannelUpdate(ChannelCreate):
    pass


class ChannelGet(ChannelCreate):
    id: str
