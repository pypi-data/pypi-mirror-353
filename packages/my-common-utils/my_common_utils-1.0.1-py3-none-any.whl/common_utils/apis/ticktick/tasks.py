import requests
from pydantic import BaseModel, ConfigDict

from common_utils.apis.ticktick.cookies_login import get_authenticated_ticktick_headers
from common_utils.logger import create_logger


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
    column_id: str | None = None
    is_all_day: bool | None = None
    start_date: str | None = None
    due_date: str | None = None
    content: str | None = None

    @staticmethod
    def to_camel(field_name: str) -> str:
        """
        Convert a snake_case field name into camelCase.
        E.g. 'checkin_stamp' -> 'checkinStamp'
        """
        parts = field_name.split('_')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow"
    )



class TicktickTaskHandler:
    log = create_logger("TickTick Task Handler")
    url_get_tasks = 'https://api.ticktick.com/api/v2/batch/check/0'

    def __init__(
            self,
            cookies_path: str | None = None,
            always_raise_exceptions: bool = False,
            headless: bool = True,
            undetected: bool = False,
            download_driver: bool = False,
            username_env: str = 'TICKTICK_EMAIL',
            password_env: str = 'TICKTICK_PASSWORD',
    ):
        self.headers = get_authenticated_ticktick_headers(
            cookies_path=cookies_path,
            username_env=username_env,
            password_env=password_env,
            headless=headless,
            undetected=undetected,
            download_driver=download_driver,
        )
        self.raise_exceptions = always_raise_exceptions

    def get_all_tasks(self) -> list[TickTickTask] | None:
        """
        Get all TickTick tasks

        Returns:
            List of TickTickTask pydantic BaseModel objects. Objects can be converted via .dict()
        """
        response = requests.get(url=self.url_get_tasks, headers=self.headers).json()
        tasks_data = response.get('syncTaskBean', {}).get('update', None)
        if tasks_data is None:
            self.log.error("Getting Tasks failed")
            if self.raise_exceptions:
                raise ValueError("Getting Tasks failed")
            return None

        tasks = []
        for data in tasks_data:
            tasks.append(TickTickTask(**data))
        # tasks = [TickTickTask(**task_data) for task_data in tasks_data]

        return tasks


if __name__ == '__main__':
    TicktickTaskHandler().get_all_tasks()