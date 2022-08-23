import abc
import logging
import threading
from typing import Optional

_logger = logging.getLogger(__name__)


class StoppableThread(abc.ABC):
    _thread_lock: threading.Lock
    _thread_name: str
    _thread: Optional[threading.Thread]

    _keep_running: bool

    def __init__(self, thread_name: str = "") -> None:
        super().__init__()

        self._thread_lock = threading.Lock()
        self._thread_name = thread_name
        self._thread = None
        self._keep_running = False

    def start(self) -> None:
        _logger.info("START")

        with self._thread_lock:
            if self._thread:
                return

            self._thread = threading.Thread(target=self._loop, name=self._thread_name)

            self._keep_running = True
            self._thread.start()

    def stop(self) -> None:
        _logger.info("STOP")

        with self._thread_lock:
            if not self._thread:
                return

            self._keep_running = False

    def join(self) -> None:
        _logger.info("JOIN")

        if not self._thread:
            return

        try:
            self._thread.join()
        except KeyboardInterrupt:
            pass

    def _loop(self) -> None:
        _logger.info("LOOP")

        while self._keep_running:
            self._job()

    @abc.abstractmethod
    def _job(self) -> None:
        raise NotImplementedError
