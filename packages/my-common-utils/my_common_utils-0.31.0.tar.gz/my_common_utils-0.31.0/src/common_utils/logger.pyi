import logging
from _typeshed import Incomplete

format_str: str
client: Incomplete

class FixedWidthFormatter(logging.Formatter):
    name_length: Incomplete
    def __init__(self, fmt: Incomplete | None = None, datefmt: Incomplete | None = None, name_length: int = 16) -> None: ...
    def format(self, record, name_length: int = 16): ...

def create_logger(name: str, long_date_format: bool = False, name_length: int = 18) -> logging.Logger: ...
