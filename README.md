# aprs2influxdb

[![Build Status](https://travis-ci.org/FaradayRF/aprs2influxdb.svg?branch=master)](https://travis-ci.org/FaradayRF/aprs2influxdb)

This program interfaces ham radio APRS-IS servers and saves packet data into an InfluxDB 2 database.

aprs2influxdb handles the connection, parsing, and saving of data into an InfluxDB 2 database from APRS-IS using line
protocol formatted strings.

Periodically, a status message is also sent to the APRS-IS server in order to maintain the connection with the APRS-IS
server by preventing a timeout.

Supported APRS Packet Formats:

- uncompressed
- mic-e
- object
- compressed
- status
- wx
- beacon
- bulletin
- message
- telemetry

Non-ASCII characters in APRS packets are replaced!

## Getting started

~~aprs2influxdb installs using pip can can be installed in editable mode with the source code or from
[PyPI](https://pypi.python.org/pypi).~~

### Prerequisites

You must install and configure an [InfluxDB](https://www.influxdata.com/) database.

Here is their open source [project documentation on GitHub](https://github.com/influxdata/influxdb).

### Installing

It is highly recommended to install `aprs2influxdb` in a virtual environment using `virtualenv`.
This helps smooth out installation on Windows and Linux.

The executable may not be found and return a "ImportError: 'module' object has no attribute..." indicating that the
installed scripts cannot find the installed files. Virtualenv fixes all this.

It's not necessary to install in a discrete virtual environment, as long as it is separate from the python
installation.

#### PyPI

```bash
pip install aprs2influxdb
```

#### Source Code

If you are just installing with source code then navigate to the source directory and run:

```bash
pip install .
```

if you are installing in editable mode for development then navigate to the source directory and run:

```bash
pip install -e .
```

### Running aprs2influxdb

The program defaults use standard influxdb login information as well as example APRS-IS login information.

If you properly installed influxdb you will need to specify your own database information. Additionally, you will need
an amateur radio license with which you may login to APRS-IS with your callsign.

#### Command Line Options

| Option                      | Env Var                   | Description                     | Default value          |
|-----------------------------|---------------------------|---------------------------------|------------------------|
| `--help`                    |                           | show this help message and exit |                        |
| `--influxdb-url`            | `INFLUXDB_URL`            | InfluxDB URL                    | `http://influxdb:8086` |
| `--influxdb-token`          | `INFLUXDB_TOKEN`          | InfluxDB Token                  | ``                     |
| `--influxdb-org`            | `INFLUXDB_ORG`            | InfluxDB Organization name      | `aprs2influxdb`        |
| `--influxdb-bucket`         | `INFLUXDB_BUCKET`         | InfluxDB Bucket name            | ``                     |
| `--aprs-server`             | `APRS_SERVER`             | APRS-IS to connect              | `rotate.aprs.net`      |
| `--aprs-port`               | `APRS_PORT`               | APRS-IS to connect              | `14580`                |
| `--aprs-callsign`           | `APRS_CALLSIGN`           | APRS-IS login callsign          | `N0CALL`               |
| `--aprs-filter`             | `APRS_FILTER`             | APRS-IS server-sidd filter      | ``                     |
| `--aprs-heartbeat-interval` | `APRS_HEARTBEAT_INTERVAL` | APRS-IS heartbeat interval      | `15` minutes           |
| `--debug`                   |                           | logging level to DEBUG          | False                  |

#### Example

Starting aprs2influxdb assuming an influxdb server is running and configured with a user, an organization, a bucket
and an API Token with related permissions.

Please note that APRS-IS ignores logins from "nocall" so you will connect but likely see nothing if you do not specify
your amateur radio callsign.

Assuming that you have already created a Virtualenv, you can run the software with this command:

```bash
./venv/bin/python3 \
  ./aprs2influxdb/main.py \
    --influxdb-url="http://127.0.0.1:8086" \
    --influxdb-token="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" \
    --influxdb-org="aprs2influxdb" \
    --influxdb-bucket="IR0UBN" \
    --aprs-callsign="IS0GVH-12" \
    --aprs-filter="p/IR0UBN" \
    --aprs-heartbeat-interval="1" \
    --debug
```

The above command uses default values for the options not specified.

APRS-IS port `14580`, which is the port in which a user can specify custom server-side filters.
The default `10152` could be used, but it's the full stream port in which no filter could be set.

Although a specific APRS-IS hostnmae could be specified, default value is `rotate.aprs.net` (same of `aprslib`) in
order to pick an APRS core server.
Please see [APRS-IS Servers](http://www.aprs-is.net/aprsservers.aspx) for more information.

To exit `aprs2influxdb` just use `CTRL + C`.

## Running the tests

~~Unit testing will be implemented in a future pull request.~~

Tests use `pytest` library. Just run `pytest` and all tests will run.

Just be sure to add into PYTHONPATH both `aprs2influxdb` and `test` folders.

## Deployment

~~This has been tested on a Debian 9 (Stretch) server as well as locally with Windows 7 during development.~~

The software is tested on Python 3.10 environment using InfluxDB 2.4.

## Authors

* **Bryce Salmi** - *Initial work and main parsing logic* - [KB1LQC](https://github.com/kb1lqc)
* **Luca Cireddu** - *Class py3 refactoring, InfluxDB 2 and containerization* - [IS0GVH](https://github.com/sardylan)
* **Stefano Lande** - *Telemetry parsing, containerization and testing* - [IS0EIR](https://github.com/stefanolande)

See also the list of [contributors](https://github.com/FaradayRF/aprs2influxdb/contributors) who participated in this
project.

## Acknowledgments

* [@PhirePhly](https://github.com/PhirePhly) for answering my APRS questions!
* [@hessu](https://github.com/hessu) for also answering my APRS and aprsc questions as well as providing the awesome
  [aprs.fi](https://www.aprs.fi) website.
