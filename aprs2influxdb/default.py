import datetime

DEFAULT_APRS_SERVER: str = "rotate.aprs.net"
DEFAULT_APRS_PORT: int = 14580  # 10152
DEFAULT_APRS_CALLSIGN: str = "N0CALL"
DEFAULT_APRS_FILTER: str = ""
DEFAULT_APRS_HEARTBEAT_INTERVAL: datetime.timedelta = datetime.timedelta(minutes=10)

DEFAULT_INFLUXDB_URL: str = "http://influxdb:8086"
DEFAULT_INFLUXDB_TOKEN: str = ""
DEFAULT_INFLUXDB_ORG: str = "aprs2influxdb"
DEFAULT_INFLUXDB_BUCKET: str = "aprs2influxdb"

DEFAULT_DEBUG: bool = False
