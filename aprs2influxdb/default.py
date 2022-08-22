import datetime

DEFAULT_APRS_SERVER: str = "rotate.aprs.net"
DEFAULT_APRS_PORT: int = 10152
DEFAULT_APRS_CALLSIGN: str = "nocall"
DEFAULT_APRS_FILTER: str = ""
DEFAULT_APRS_HEARTBEAT_INTERVAL: datetime.timedelta = datetime.timedelta(hours=1)

DEFAULT_INFLUXDB_HOST: str = "influxdb"
DEFAULT_INFLUXDB_PORT: int = 8086
DEFAULT_INFLUXDB_USERNAME: str = "aprs2influxdb"
DEFAULT_INFLUXDB_PASSWORD: str = "aprs2influxdb"
DEFAULT_INFLUXDB_DATABASE: str = "aprs2influxdb"
DEFAULT_INFLUXDB_SSL: bool = False

DEFAULT_DEBUG: bool = False
