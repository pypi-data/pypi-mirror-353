from _typeshed import Incomplete
from common_utils.apis.ticktick.cookies_login import get_authenticated_ticktick_headers as get_authenticated_ticktick_headers
from common_utils.logger import create_logger as create_logger
from pydantic import BaseModel

class TickTickTask(BaseModel):
    id: str
    project_id: str
    title: str
    status: int
    priority: int
    deleted: int
    created_time: str
    creator: int
    items: list
    column_id: str | None
    is_all_day: bool | None
    start_date: str | None
    due_date: str | None
    content: str | None
    @staticmethod
    def to_camel(field_name: str) -> str: ...
    model_config: Incomplete

class TicktickTaskHandler:
    log: Incomplete
    url_get_tasks: str
    headers: Incomplete
    raise_exceptions: Incomplete
    def __init__(self, cookies_path: str | None = None, always_raise_exceptions: bool = False, headless: bool = True, undetected: bool = False, download_driver: bool = False, username_env: str = 'TICKTICK_EMAIL', password_env: str = 'TICKTICK_PASSWORD') -> None: ...
    def get_all_tasks(self) -> list[TickTickTask] | None: ...
