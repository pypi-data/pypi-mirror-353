from _typeshed import Incomplete
from common_utils.logger import create_logger as create_logger
from common_utils.web.selenium import SeleniumHandler as SeleniumHandler
from dataclasses import dataclass
from selenium import webdriver as webdriver

@dataclass
class LoginSelectors:
    username: str
    password: str
    login_button: str
    popup_close: str | None = ...

@dataclass
class LoginData:
    username_env: str
    password_env: str
    sign_in_url: str
    selectors: LoginSelectors

class CookiesManager:
    login_wait_time: int
    headers: Incomplete
    login_data: Incomplete
    test_cookies_url: Incomplete
    test_cookies_response_fn: Incomplete
    min_num_cookies: Incomplete
    log: Incomplete
    cookies_path: Incomplete
    selenium_handler: Incomplete
    def __init__(self, login_data: LoginData, test_cookies_url: str, test_cookies_response_fn: callable, min_num_cookies: int | None = None, cookies_path: str | None = None, headless: bool = False, undetected: bool = False, download_driver: bool = False) -> None: ...
    def get_headers_with_cookies(self): ...
    def get_cookies(self): ...
    def get_cookies_from_file(self) -> str | None: ...
    def get_cookies_from_browser(self): ...
    def save_cookies_to_path(self, cookies: str): ...
    def test_cookies_valid(self, cookies: str | None) -> bool: ...
