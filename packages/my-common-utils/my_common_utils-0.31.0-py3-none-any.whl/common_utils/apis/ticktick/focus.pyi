from _typeshed import Incomplete
from common_utils.apis.ticktick.cookies_login import get_authenticated_ticktick_headers as get_authenticated_ticktick_headers
from common_utils.logger import create_logger as create_logger
from common_utils.time_utils import get_timestamp_from_offset as get_timestamp_from_offset
from datetime import datetime
from pydantic import BaseModel

class TickTickFocusTime(BaseModel):
    id: str
    type: int
    start_time: str | datetime
    end_time: str | datetime
    status: int
    pause_duration: int
    total_duration: int | None
    @staticmethod
    def to_camel(field_name: str) -> str: ...
    model_config: Incomplete

class TicktickFocusHandler:
    log: Incomplete
    headers: Incomplete
    raise_exceptions: Incomplete
    def __init__(self, cookies_path: str | None = None, always_raise_exceptions: bool = False, headless: bool = True, undetected: bool = False, download_driver: bool = False, username_env: str = 'TICKTICK_EMAIL', password_env: str = 'TICKTICK_PASSWORD') -> None: ...
    def get_all_focus_times(self, to_timestamp: int | None = None, days_offset: int | None = None) -> list[TickTickFocusTime] | None: ...
