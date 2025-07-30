import logging
from tk3u8.constants import OptionKey, Quality
from tk3u8.core.downloader import Downloader
from tk3u8.core.stream_metadata_handler import StreamMetadataHandler
from tk3u8.options_handler import OptionsHandler
from tk3u8.path_initializer import PathInitializer
from tk3u8.session.request_handler import RequestHandler


logger = logging.getLogger(__name__)


class Tk3u8:
    def __init__(self, program_data_dir: str | None = None) -> None:
        logger.debug("Initializing Tk3u8 class")
        self._paths_handler = PathInitializer(program_data_dir)
        self._options_handler = OptionsHandler()
        self._request_handler = RequestHandler(self._options_handler)
        self._stream_metadata_handler = StreamMetadataHandler(
            self._request_handler,
            self._options_handler
        )
        self._downloader = Downloader(
            self._stream_metadata_handler,
            self._options_handler
        )

    def download(
            self,
            username: str,
            quality: str = Quality.ORIGINAL.value,
            wait_until_live: bool = False,
            timeout: int = 30
    ) -> None:
        self._options_handler.save_args_values(
            wait_until_live=wait_until_live,
            timeout=timeout
        )
        self._stream_metadata_handler.initialize_data(username)
        self._downloader.download(quality)

    def set_proxy(self, proxy: str | None) -> None:
        self._options_handler.save_args_values({OptionKey.PROXY.value: proxy})

        new_proxy = self._options_handler.get_option_val(OptionKey.PROXY)
        assert isinstance(new_proxy, (str, type(None)))

        self._request_handler.update_proxy(new_proxy)
