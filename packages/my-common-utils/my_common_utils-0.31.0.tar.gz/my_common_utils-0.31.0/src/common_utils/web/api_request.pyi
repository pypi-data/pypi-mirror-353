from _typeshed import Incomplete
from common_utils.logger import create_logger as create_logger

log: Incomplete

def get_request(url, headers: Incomplete | None = None, catch_exception: bool = False) -> dict | None: ...
def post_request(url, payload, headers: Incomplete | None = None, raise_exception: bool = False) -> dict | None: ...
