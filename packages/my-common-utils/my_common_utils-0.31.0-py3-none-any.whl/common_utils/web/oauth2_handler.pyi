from _typeshed import Incomplete
from common_utils.config import ROOT_DIR as ROOT_DIR
from common_utils.logger import create_logger as create_logger

class OAuth2Data:
    client_id_env: str
    client_secret_env: str
    redirect_uri_env: str
    scope_env: str
    authorize_url: str
    token_url: str
    state: str | None

class OAuth2Handler:
    log: Incomplete
    auth_code: Incomplete
    client_id: Incomplete
    client_secret: Incomplete
    redirect_uri: Incomplete
    scope: Incomplete
    authorize_url: Incomplete
    token_url: Incomplete
    state: Incomplete
    port: Incomplete
    cache_path: Incomplete
    cache_name: Incomplete
    def __init__(self, data: OAuth2Data, cache_path: str | None = None) -> None: ...
    def callback_app(self, environ, start_response): ...
    def start_temp_server(self) -> None: ...
    def save_token(self, token) -> None: ...
    def load_token(self): ...
    def get_token(self): ...
