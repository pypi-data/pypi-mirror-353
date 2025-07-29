from _typeshed import Incomplete
from common_utils.apis.ticktick.cookies_login import get_authenticated_ticktick_headers as get_authenticated_ticktick_headers
from common_utils.logger import create_logger as create_logger
from common_utils.time_utils import get_datetime_now_utc_millisecond as get_datetime_now_utc_millisecond
from common_utils.web.api_request import post_request as post_request
from pydantic import BaseModel
from typing import Literal

class TickTickHabitEntry(BaseModel):
    habit_id: str
    checkin_stamp: int
    goal: float | int
    value: float | int
    status: Literal[0, 1, 2]
    id: str | None
    checkin_time: str | None
    op_time: str | None
    @classmethod
    def init(cls, habit_id: str, date_stamp: int, habit_goal: int, status: Literal[0, 1, 2] | None = None, value: int | float | None = None) -> TickTickHabitEntry: ...
    @staticmethod
    def to_camel(field_name: str) -> str: ...
    model_config: Incomplete

class TicktickHabitHandler:
    status_codes: Incomplete
    url_habits: str
    url_batch_checkin: str
    url_query_checkin: str
    log: Incomplete
    headers: Incomplete
    raise_exceptions: Incomplete
    def __init__(self, cookies_path: str | None = None, always_raise_exceptions: bool = False, headless: bool = True, undetected: bool = False, download_driver: bool = False, username_env: str = 'TICKTICK_EMAIL', password_env: str = 'TICKTICK_PASSWORD') -> None: ...
    def post_checkin(self, habit_name: str, date_stamp: int, status: int | None = None, value: int | None = None, raise_exception: bool = False) -> None: ...
    def get_checkin(self, habit_id: str, date_stamp: int, raise_exception: bool = False) -> TickTickHabitEntry | None: ...
    def get_all_checkins(self, after_stamp: int = 19700101, habit_names: list[str] | str | None = None, raise_exception: bool = False) -> dict[str, list[TickTickHabitEntry]] | None: ...
