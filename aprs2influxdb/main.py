import argparse
import logging
import os
import signal

from aprs2influxdb import APRS2InfluxDB
from config import ConfigParams
from default import *


def parse_command_line():
    args_parser = argparse.ArgumentParser(
        description="Connects to APRS-IS and saves stream to local InfluxDB"
    )

    args_parser.add_argument("--influxdb-url",
                             help="Set InfluxDB URL",
                             default=os.environ.get("INFLUXDB_URL", DEFAULT_INFLUXDB_URL))

    args_parser.add_argument("--influxdb-token",
                             help="Set InfluxDB Token",
                             default=os.environ.get("INFLUXDB_TOKEN", DEFAULT_INFLUXDB_TOKEN))

    args_parser.add_argument("--influxdb-org",
                             help="Set InfluxDB Org",
                             default=os.environ.get("INFLUXDB_ORG", DEFAULT_INFLUXDB_ORG))

    args_parser.add_argument("--influxdb-bucket",
                             help="Set InfluxDB Bucket",
                             default=os.environ.get("INFLUXDB_BUCKET", DEFAULT_INFLUXDB_BUCKET))

    args_parser.add_argument("--aprs-server",
                             help="Set APRS-IS",
                             default=os.environ.get("APRS_SERVER", DEFAULT_APRS_SERVER))

    args_parser.add_argument("--aprs-port",
                             help="Set APRS-IS port",
                             default=os.environ.get("APRS_PORT", str(DEFAULT_APRS_PORT)))

    args_parser.add_argument("--aprs-callsign",
                             help="Set APRS-IS login callsign",
                             default=os.environ.get("APRS_CALLSIGN", DEFAULT_APRS_CALLSIGN))

    args_parser.add_argument("--aprs-filter",
                             help="Set APRS-IS filter",
                             default=os.environ.get("APRS_FILTER", DEFAULT_APRS_FILTER))

    args_parser.add_argument("--aprs-heartbeat-interval",
                             help="Set APRS-IS heartbeat interval in minutes",
                             default=os.environ.get("APRS_HEARTBEAT_INTERVAL",
                                                    str(DEFAULT_APRS_HEARTBEAT_INTERVAL.seconds / 60)))

    args_parser.add_argument("--debug",
                             help="Set logging level to DEBUG",
                             action="store_true",
                             default=os.environ.get("DEBUG", DEFAULT_DEBUG))

    return args_parser.parse_args()


def main() -> None:
    args = parse_command_line()

    logging_level = logging.WARNING
    if args.debug:
        logging_level = logging.DEBUG

    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s [%(levelname)5s] %(name)s {%(threadName)s}: %(message)s"
    )

    config_params: ConfigParams = ConfigParams()

    config_params.aprs_server = args.aprs_server
    config_params.aprs_port = int(args.aprs_port)
    config_params.aprs_callsign = args.aprs_callsign
    config_params.aprs_filter = args.aprs_filter
    config_params.aprs_heartbeat_interval = datetime.timedelta(minutes=int(args.aprs_heartbeat_interval))

    config_params.influxdb_url = args.influxdb_url
    config_params.influxdb_token = args.influxdb_token
    config_params.influxdb_org = args.influxdb_org
    config_params.influxdb_bucket = args.influxdb_bucket

    aprs_to_influx_db: APRS2InfluxDB = APRS2InfluxDB(config_params)

    def signal_handler(signum: int, _) -> None:
        if signum in [signal.SIGINT, signal.SIGTERM, signal.SIGABRT]:
            aprs_to_influx_db.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGABRT, signal_handler)

    aprs_to_influx_db.start()
    aprs_to_influx_db.join()


if __name__ == "__main__":
    main()
