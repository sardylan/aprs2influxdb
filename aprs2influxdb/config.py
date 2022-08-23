import logging

from default import *

_logger = logging.getLogger(__name__)


class ConfigParams:
    _aprs_server: str
    _aprs_port: int
    _aprs_callsign: str
    _aprs_filter: str
    _aprs_heartbeat_interval: datetime.timedelta

    _influxdb_host: str
    _influxdb_port: int
    _influxdb_username: str
    _influxdb_password: str
    _influxdb_database: str
    _influxdb_ssl: bool

    def __init__(self) -> None:
        super().__init__()

        self._aprs_server = DEFAULT_APRS_SERVER
        self._aprs_port = DEFAULT_APRS_PORT
        self._aprs_callsign = DEFAULT_APRS_CALLSIGN
        self._aprs_filter = DEFAULT_APRS_FILTER
        self._aprs_heartbeat_interval = DEFAULT_APRS_HEARTBEAT_INTERVAL

        self._influxdb_host = DEFAULT_INFLUXDB_HOST
        self._influxdb_port = DEFAULT_INFLUXDB_PORT
        self._influxdb_username = DEFAULT_INFLUXDB_USERNAME
        self._influxdb_password = DEFAULT_INFLUXDB_PASSWORD
        self._influxdb_database = DEFAULT_INFLUXDB_DATABASE
        self._influxdb_ssl = DEFAULT_INFLUXDB_SSL

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
    def influxdb_host(self) -> str:
        return self._influxdb_host

    @influxdb_host.setter
    def influxdb_host(self, influxdb_host: str = DEFAULT_INFLUXDB_HOST) -> None:
        self._influxdb_host = influxdb_host

    @property
    def influxdb_port(self) -> int:
        return self._influxdb_port

    @influxdb_port.setter
    def influxdb_port(self, influxdb_port: int = DEFAULT_INFLUXDB_PORT) -> None:
        self._influxdb_port = influxdb_port

    @property
    def influxdb_username(self) -> str:
        return self._influxdb_username

    @influxdb_username.setter
    def influxdb_username(self, influxdb_username: str = DEFAULT_INFLUXDB_USERNAME) -> None:
        self._influxdb_username = influxdb_username

    @property
    def influxdb_password(self) -> str:
        return self._influxdb_password

    @influxdb_password.setter
    def influxdb_password(self, influxdb_password: str = DEFAULT_INFLUXDB_PASSWORD) -> None:
        self._influxdb_password = influxdb_password

    @property
    def influxdb_database(self) -> str:
        return self._influxdb_database

    @influxdb_database.setter
    def influxdb_database(self, influxdb_database: str = DEFAULT_INFLUXDB_DATABASE) -> None:
        self._influxdb_database = influxdb_database

    @property
    def influxdb_ssl(self) -> bool:
        return self._influxdb_ssl

    @influxdb_ssl.setter
    def influxdb_ssl(self, influxdb_ssl: bool = DEFAULT_INFLUXDB_SSL) -> None:
        self._influxdb_ssl = influxdb_ssl

    def log(self) -> None:
        _logger.debug(f"APRS")
        _logger.debug(f"  - Server: {self._aprs_server}")
        _logger.debug(f"  - Port: {self._aprs_port}")
        _logger.debug(f"  - Callsign: {self._aprs_callsign}")
        _logger.debug(f"  - Filter: {self._aprs_filter}")
        _logger.debug(f"  - Heartbeat interval: {self._aprs_heartbeat_interval}")

        _logger.debug(f"InfluxDB")
        _logger.debug(f"  - Host: {self._influxdb_host}")
        _logger.debug(f"  - Port: {self._influxdb_port}")
        _logger.debug(f"  - Username: {self._influxdb_username}")
        _logger.debug(f"  - Password: {self._influxdb_password}")
        _logger.debug(f"  - Database: {self._influxdb_database}")
        _logger.debug(f"  - SSL: {self._influxdb_ssl}")
