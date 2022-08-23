import logging

from default import *

_logger = logging.getLogger(__name__)


class ConfigParams:
    _aprs_server: str
    _aprs_port: int
    _aprs_callsign: str
    _aprs_filter: str
    _aprs_heartbeat_interval: datetime.timedelta

    _influxdb_url: str
    _influxdb_token: str
    _influxdb_org: str
    _influxdb_bucket: str

    def __init__(self) -> None:
        super().__init__()

        self._aprs_server = DEFAULT_APRS_SERVER
        self._aprs_port = DEFAULT_APRS_PORT
        self._aprs_callsign = DEFAULT_APRS_CALLSIGN
        self._aprs_filter = DEFAULT_APRS_FILTER
        self._aprs_heartbeat_interval = DEFAULT_APRS_HEARTBEAT_INTERVAL

        self._influxdb_url = DEFAULT_INFLUXDB_URL
        self._influxdb_token = DEFAULT_INFLUXDB_TOKEN
        self._influxdb_org = DEFAULT_INFLUXDB_ORG
        self._influxdb_bucket = DEFAULT_INFLUXDB_BUCKET

    @property
    def aprs_server(self) -> str:
        return self._aprs_server

    @aprs_server.setter
    def aprs_server(self, aprs_server: str = DEFAULT_APRS_SERVER) -> None:
        self._aprs_server = aprs_server

    @property
    def aprs_port(self) -> int:
        return self._aprs_port

    @aprs_port.setter
    def aprs_port(self, aprs_port: int = DEFAULT_APRS_PORT) -> None:
        self._aprs_port = aprs_port

    @property
    def aprs_callsign(self) -> str:
        return self._aprs_callsign

    @aprs_callsign.setter
    def aprs_callsign(self, aprs_callsign: str = DEFAULT_APRS_CALLSIGN) -> None:
        self._aprs_callsign = aprs_callsign

    @property
    def aprs_filter(self) -> str:
        return self._aprs_filter

    @aprs_filter.setter
    def aprs_filter(self, aprs_filter: str = DEFAULT_APRS_FILTER) -> None:
        self._aprs_filter = aprs_filter

    @property
    def aprs_heartbeat_interval(self) -> datetime.timedelta:
        return self._aprs_heartbeat_interval

    @aprs_heartbeat_interval.setter
    def aprs_heartbeat_interval(self,
                                aprs_heartbeat_interval: datetime.timedelta = DEFAULT_APRS_HEARTBEAT_INTERVAL) -> None:
        self._aprs_heartbeat_interval = aprs_heartbeat_interval

    @property
    def influxdb_url(self) -> str:
        return self._influxdb_url

    @influxdb_url.setter
    def influxdb_url(self, influxdb_url: str = DEFAULT_INFLUXDB_URL) -> None:
        self._influxdb_url = influxdb_url

    @property
    def influxdb_token(self) -> str:
        return self._influxdb_token

    @influxdb_token.setter
    def influxdb_token(self, influxdb_token: str = DEFAULT_INFLUXDB_TOKEN) -> None:
        self._influxdb_token = influxdb_token

    @property
    def influxdb_org(self) -> str:
        return self._influxdb_org

    @influxdb_org.setter
    def influxdb_org(self, influxdb_org: str = DEFAULT_INFLUXDB_ORG) -> None:
        self._influxdb_org = influxdb_org

    @property
    def influxdb_bucket(self) -> str:
        return self._influxdb_bucket

    @influxdb_bucket.setter
    def influxdb_bucket(self, influxdb_bucket: str = DEFAULT_INFLUXDB_BUCKET) -> None:
        self._influxdb_bucket = influxdb_bucket

    def log(self) -> None:
        _logger.debug(f"APRS")
        _logger.debug(f"  - Server: {self._aprs_server}")
        _logger.debug(f"  - Port: {self._aprs_port}")
        _logger.debug(f"  - Callsign: {self._aprs_callsign}")
        _logger.debug(f"  - Filter: {self._aprs_filter}")
        _logger.debug(f"  - Heartbeat interval: {self._aprs_heartbeat_interval}")

        _logger.debug(f"InfluxDB")
        _logger.debug(f"  - URL: {self._influxdb_url}")
        _logger.debug(f"  - Token: {self._influxdb_token}")
        _logger.debug(f"  - Organization: {self._influxdb_org}")
        _logger.debug(f"  - Bucket: {self._influxdb_bucket}")
