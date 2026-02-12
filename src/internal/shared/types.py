from enum import Enum
from typing import TypeAlias


UnixTimestamp: TypeAlias = int


class ContestPublicationKind(str, Enum):
    PLANNED = "planned"
    ON_FINISH = "on_finish"


class ContestFinishKind(str, Enum):
    PLANNED = "planned"
    ON_WINNERS_NUM = "on_winners_num"


class ContestState(str, Enum):
    ONEDIT = "on_edit"
    PUBLISHED = "published"
    ACTIVE = "active"
    FINISHED = "finished"
    ARCHIVED = "archived"
