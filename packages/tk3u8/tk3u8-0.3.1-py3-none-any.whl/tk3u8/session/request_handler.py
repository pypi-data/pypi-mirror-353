import logging
import random
import requests
from tk3u8.constants import USER_AGENT_LIST, OptionKey
from tk3u8.exceptions import RequestFailedError
from tk3u8.options_handler import OptionsHandler


logger = logging.getLogger(__name__)


class RequestHandler:
    def __init__(self, options_handler: OptionsHandler) -> None:
        self._options_handler = options_handler
        self._session = requests.Session()
        self._setup_cookies()
        self._setup_proxy()
        self._session.headers.update({
            "User-Agent": self.get_random_user_agent()
        })
        self._response: requests.Response

    def get_data(self, url: str) -> requests.Response:
        self._response = self._session.get(url)

        if self._response.status_code != 200:
            logger.exception(f"{RequestFailedError.__name__}: {RequestFailedError(self._response.status_code)}")
            raise RequestFailedError(status_code=self._response.status_code)

        return self._response

    def update_proxy(self, proxy: str | None) -> None:
        if proxy:
            self._session.proxies.update({
                    "http": proxy,
                    "https": proxy
            })

            logger.debug(f"Proxy updated to: {proxy}")

    def _setup_cookies(self) -> None:
        sessionid_ss = self._options_handler.get_option_val(OptionKey.SESSIONID_SS)
        tt_target_idc = self._options_handler.get_option_val(OptionKey.TT_TARGET_IDC)

        assert isinstance(sessionid_ss, (str, type(None)))
        assert isinstance(tt_target_idc, (str, type(None)))

        if sessionid_ss is None and tt_target_idc is None:
            return

        if sessionid_ss:
            self._session.cookies.update({
                "sessionid_ss": sessionid_ss
            })
            logger.debug(f"'sessionid_ss' cookie set to: {sessionid_ss}")

        if tt_target_idc:
            self._session.cookies.update({
                "tt-target-idc": tt_target_idc
            })
            logger.debug(f"'tt-target-idc' cookie set to: {tt_target_idc}")

    def _setup_proxy(self) -> None:
        proxy = self._options_handler.get_option_val(OptionKey.PROXY)
        assert isinstance(proxy, (str, type(None)))

        if proxy:
            self.update_proxy(proxy)

    def get_random_user_agent(self) -> str:
        random_ua = random.choice(USER_AGENT_LIST)

        logger.debug(f"Random User-Agent selected: {random_ua}")
        return random_ua
