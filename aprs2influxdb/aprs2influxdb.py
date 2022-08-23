import datetime
import logging
import threading
import time
from typing import Optional

import aprslib
from influxdb_client import InfluxDBClient

from config import ConfigParams
from parser import Parser
from utils import StoppableThread

_logger = logging.getLogger(__name__)


class APRS2InfluxDB(StoppableThread):
    _config_params: ConfigParams

    _lock: threading.Lock

    _aprs: Optional[aprslib.IS]
    _influxdb: Optional[InfluxDBClient]

    _heartbeat_thread: Optional[threading.Thread]
    _heartbeat_last: datetime.datetime

    _parser: Parser

    def __init__(self, config_params: ConfigParams) -> None:
        super().__init__(thread_name="APRS-IS")

        self._lock = threading.Lock()

        if not config_params:
            raise ValueError("Invalid config parameters")
        self._config_params = config_params
        self._config_params.log()

        self._config_params.aprs = None
        self._influxdb = None

        self._heartbeat_thread = None
        self._heartbeat_last = datetime.datetime.utcnow()

        self._parser = Parser()

    def start(self) -> None:
        _logger.info("START")

        with self._lock:
            self._aprs_client_start()
            self._influxdb_client_start()
            self._heartbeat_start()
            super().start()

    def stop(self) -> None:
        _logger.info("STOP")

        with self._lock:
            super().stop()
            self._heartbeat_stop()
            self._influxdb_client_stop()
            self._aprs_client_stop()

    def join(self) -> None:
        try:
            self._heartbeat_thread.join()
        except KeyboardInterrupt:
            pass

        super().join()

    def _aprs_client_start(self) -> None:
        _logger.info("APRS Client START")

        _logger.info("Computing passcode")
        passcode: int = aprslib.passcode(self._config_params.aprs_callsign)
        _logger.debug(f"Passcode for {self._config_params.aprs_callsign} id {passcode}")

        self._aprs = aprslib.IS(
            host=self._config_params.aprs_server,
            port=self._config_params.aprs_port,
            callsign=self._config_params.aprs_callsign,
            passwd=passcode
        )

        self._aprs.logger = logging.getLogger("aprslib")

        _logger.info("Setting filter")
        self._aprs.set_filter(self._config_params.aprs_filter)

        _logger.info("Connecting")
        self._aprs.connect()

    def _aprs_client_stop(self) -> None:
        _logger.info("APRS Client STOP")

        self._aprs.close()

    def _influxdb_client_start(self) -> None:
        _logger.info("InfluxDB Client START")

        self._influxdb = InfluxDBClient(
            url=self._config_params.influxdb_url,
            token=self._config_params.influxdb_token,
            org=self._config_params.influxdb_org
        )

    def _influxdb_client_stop(self) -> None:
        _logger.info("InfluxDB Client STOP")

        self._influxdb.close()

    def _heartbeat_start(self) -> None:
        _logger.info("APRS Heartbeat START")

        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, name="Heartbeat")
        self._heartbeat_thread.start()

    def _heartbeat_stop(self) -> None:
        _logger.info("APRS Heartbeat STOP")

    def _heartbeat_loop(self) -> None:
        _logger.info("APRS Heartbeat LOOP")

        while self._keep_running:
            self._heartbeat_job()
            time.sleep(1)

    def _heartbeat_job(self) -> None:
        now: datetime.datetime = datetime.datetime.utcnow()
        interval: datetime.timedelta = now - self._heartbeat_last
        if interval < self._config_params.aprs_heartbeat_interval:
            return

        self._heartbeat_last = now

        callsign: str = self._config_params.aprs_callsign
        ts: int = int(now.timestamp() * 1000)
        heartbeat_message: str = f"{callsign}>APRS,TCPIP*:>aprs2influxdb heartbeat {ts}"

        _logger.debug(f"Sending heartbeat: {heartbeat_message}")
        self._aprs.sendall(heartbeat_message)

    def _job(self) -> None:
        try:
            self._aprs.consumer(callback=self._consume_packet, immortal=True, raw=False)
        except Exception as e:
            _logger.error(e)
            raise e

    def _consume_packet(self, packet) -> None:
        _logger.debug(f"Original packet: {packet}")

        line = self._parser.json_to_line_protocol(packet)
        _logger.debug(f"Parsed line: {line}")

        if not line:
            return

        try:
            _logger.info("Writing data to InfluxDB")

            self._influxdb.write_api().write(
                org=self._config_params.influxdb_org,
                bucket=self._config_params.influxdb_bucket,
                record=line
            )

            _logger.debug("Write completed")

        except Exception as e:
            _logger.error(e)
            raise e
