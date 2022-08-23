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

    args_parser.add_argument("--dbhost",
                             help="Set InfluxDB host",
                             default=os.environ.get("INFLUXDB_HOST", DEFAULT_INFLUXDB_HOST))

    args_parser.add_argument("--dbport",
                             help="Set InfluxDB port",
                             default=os.environ.get("INFLUXDB_PORT", str(DEFAULT_INFLUXDB_PORT)))

    args_parser.add_argument("--dbuser",
                             help="Set InfluxDB user",
                             default=os.environ.get("INFLUXDB_USERNAME", DEFAULT_INFLUXDB_USERNAME))

    args_parser.add_argument("--dbpassword",
                             help="Set InfluxDB password",
                             default=os.environ.get("INFLUXDB_PASSWORD", DEFAULT_INFLUXDB_PASSWORD))

    args_parser.add_argument("--dbname",
                             help="Set InfluxDB database name",
                             default=os.environ.get("INFLUXDB_DATABASE", DEFAULT_INFLUXDB_DATABASE))

    args_parser.add_argument("--host",
                             help="Set APRS-IS host",
                             default=os.environ.get("APRS_SERVER", DEFAULT_APRS_SERVER))

    args_parser.add_argument("--port",
                             help="Set APRS-IS port",
                             default=os.environ.get("APRS_PORT", str(DEFAULT_APRS_PORT)))

    args_parser.add_argument("--callsign",
                             help="Set APRS-IS login callsign",
                             default=os.environ.get("APRS_CALLSIGN", DEFAULT_APRS_CALLSIGN))

    args_parser.add_argument("--filter",
                             help="Set APRS-IS filter",
                             default=os.environ.get("APRS_FILTER", DEFAULT_APRS_FILTER))

    args_parser.add_argument("--interval",
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

    config_params.aprs_server = args.host
    config_params.aprs_port = int(args.port)
    config_params.aprs_callsign = args.callsign
    config_params.aprs_filter = args.filter

    config_params.influxdb_host = args.dbhost
    config_params.influxdb_port = int(args.dbport)
    config_params.influxdb_username = args.dbuser
    config_params.influxdb_password = args.dbpassword
    config_params.influxdb_database = args.dbname
    config_params.influxdb_ssl = False

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
