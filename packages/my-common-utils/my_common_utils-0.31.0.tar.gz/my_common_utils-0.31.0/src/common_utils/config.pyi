from _typeshed import Incomplete
from common_utils.logger import create_logger as create_logger

logged_root_dirs: Incomplete

def get_root_dir(dunder_file: str) -> str | None: ...
def load_config_yaml(file_path: str) -> dict | None: ...
def config_entry(key): ...

logger: Incomplete
ROOT_DIR: Incomplete
CONFIG: Incomplete
