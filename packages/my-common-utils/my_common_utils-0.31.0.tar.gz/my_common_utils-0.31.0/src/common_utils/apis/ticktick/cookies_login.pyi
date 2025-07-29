from common_utils.config import ROOT_DIR as ROOT_DIR
from common_utils.logger import create_logger as create_logger
from common_utils.web.cookies_handler import CookiesManager as CookiesManager, LoginData as LoginData, LoginSelectors as LoginSelectors

def get_authenticated_ticktick_headers(cookies_path: str | None = None, username_env: str = 'TICKTICK_EMAIL', password_env: str = 'TICKTICK_PASSWORD', headless: bool = True, undetected: bool = False, download_driver: bool = False): ...
