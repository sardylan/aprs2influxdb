import aprslib
import influxdb
from influxdb import InfluxDBClient
import logging
import argparse
import sys
import threading
import time
import os

from logging.handlers import TimedRotatingFileHandler

# Globals
#logging.basicConfig(level=logging.INFO)
#logger = logging.getLogger("aprs2influxdb")

# Command line input
parser = argparse.ArgumentParser(description='Connects to APRS-IS and saves stream to local InfluxDB')
parser.add_argument('--dbhost', help='Set InfluxDB host', default="localhost")
parser.add_argument('--dbport', help='Set InfluxDB port', default="8086")
parser.add_argument('--dbuser', help='Set InfluxDB user', default="root")
parser.add_argument('--dbpassword', help='Set InfluxDB password', default="root")
parser.add_argument('--dbname', help='Set InfluxDB database name', default="mydb")
parser.add_argument('--callsign', help='Set APRS-IS login callsign', default="nocall")
parser.add_argument('--port', help='Set APRS-IS port', default="10152")
parser.add_argument('--interval', help='Set APRS-IS heartbeat interval in minutes', default="15")
parser.add_argument('--debug', help='Set logging level to DEBUG', action="store_true")

# Parse the arguments
args = parser.parse_args()


def jsonToLineProtocol(jsonData):
    """Converts JSON APRS-IS packet to influxdb line protocol

    Takes in a JSON packet from aprslib (raw=false) and parses it into an
    influxdb line protocol compliant string to insert into database. Returns
    a valid line protocol string ready to be inserted into the database.

    keyword arguments:
    jsonData -- aprslib parsed JSON packet
    """

    # Parse uncompressed format packets
    if jsonData["format"] == "uncompressed":
        # Parse uncompressed APRS packet
        return parseUncompressed(jsonData)

    if jsonData["format"] == "mic-e":
        # Parse Mice-E APRS packet
        return parseMicE(jsonData)

    if jsonData["format"] == "object":
        # Parse Object APRS packet
        return parseObject(jsonData)

    if jsonData["format"] == "compressed":
        # Parse Object APRS packet
        return parseCompressed(jsonData)

    if jsonData["format"] == "status":
        # Parse status APRS packet
        return parseStatus(jsonData)

    if jsonData["format"] == "wx":
        # Parse WX APRS packet
        return parseWX(jsonData)

    if jsonData["format"] == "beacon":
        # Parse WX APRS packet
        return parseBeacon(jsonData)

    if jsonData["format"] == "bulletin":
        # Parse Bulletin APRS packet
        return parseBulletin(jsonData)

    if jsonData["format"] == "message":
        # Parse Message APRS packet
        return parseMessage(jsonData)

    # Uncomment for all other formats not yes parsed
    #logger.warning(jsonData["format"])

def parseTelemetry(jsonData, fieldList):
    if "telemetry" in jsonData:
        items = jsonData.get("telemetry")
        if "bits" in items:
            fieldList.append("bits={0}".format(items.get("bits")))
        if "vals" in items:
            values = items.get("vals")
            for analog in range(5):
                fieldList.append("analog{0}={1}".format(analog + 1,values[analog]))
    return fieldList

def parseWeather(jsonData, fieldList):
    wxFields = ["humidity","pressure","rain_1h","rain_24h","rain_since_midnight","temperature","wind_direction","wind_gust", "wind_speed"]
    if "weather" in jsonData:
        items = jsonData.get("weather")
        for key in wxFields:
            if key in items:
                fieldList.append("{0}={1}".format(key,items.get(key)))
    return fieldList

def parseUncompressed(jsonData):
    """Parse uncompressed APRS packets into influxedb line protocol

    keyword arguments:
    jsonData -- aprslib parsed JSON packet
    """
    # Converts aprslib JSON to influxdb line protocol
    # Schema
    # measurement = packet
    # tag = from*
    # field = to*
    # field = symbolTable
    # field = symbol
    # tag = format*
    # field = objectFormat
    # field = objectName
    # field = via
    # field = messageCapable
    # field = timestamp
    # field = rawTimestamp
    # field = latitude*
    # field = longitude*
    # field = posAmbiguity*
    # field = altitude*
    # field = speed
    # field = course
    # field = seq*
    # field = analog1*
    # field = analog2*
    # field = analog3*
    # field = analog4*
    # field = analog5*
    # field = bits*
    # field = comment*
    # field = path*
    # field = mbits
    # field = mtype
    # field = pressure
    # field = rain1H
    # field = rain24h
    # field = rainSinceMidnight
    # field = temperature
    # field = windDirection
    # field = windGust
    # field = windSpeed
    # field = wxRawTimestamp
    # field = status
    # field = addresse
    # field = messageText

    # initialize variables
    tags = []
    fields = []

    # Set measurement to "packet"
    measurement = "packet"

    try:
        tags.append("from={0}".format(jsonData.get("from")))
        tags.append("format={0}".format(jsonData.get("format")))

    except KeyError as e:
        logger.error(e)

    tagStr = ",".join(tags)
    fieldNumKeys = ["latitude","longitude","posambiguity","altitude","speed"]
    fieldTextKeys = ["to"]
    fieldTelemetryKeys = ["seq","bits"]

    try:
        for key in fieldNumKeys:
            if key in jsonData:
                fields.append("{0}={1}".format(key,jsonData.get(key)))
        for key in fieldTextKeys:
            if key in jsonData:
                fields.append("{0}=\"{1}\"".format(key,jsonData.get(key)))
        if "path" in jsonData:
            fields.append(parsePath(jsonData.get("path")))
        if "comment" in jsonData:
            comment = parseTextString(jsonData.get("comment"), "comment")
            if len(jsonData.get("comment")) > 0:
                fields.append(comment)
            else:
                pass
        fields = parseTelemetry(jsonData, fields)

    except KeyError as e:
        logger.error(e)

    except ValueError as e:
        logger.error(e)

    except StandardError as e:
        logger.error(e)

    fieldsStr = ",".join(fields)

    return measurement + "," + tagStr + " " + fieldsStr


def parseMicE(jsonData):
    """Parse Mic-e APRS packets into influxedb line protocol

    keyword arguments:
    jsonData -- aprslib parsed JSON packet
    """
    # Converts aprslib JSON to influxdb line protocol
    # Schema
    # measurement = packet*
    # tag = from*
    # field = dest*
    # field = symbolTable
    # field = symbol
    # tag = format*
    # field = via*
    # field = latitude*
    # field = longitude*
    # field = posAmbiguity*
    # field = altitude*
    # field = speed*
    # field = course*
    # field = comment*
    # field = path*
    # field = mbits*
    # field = mtype*

    # initialize variables
    tags = []
    fields = []

    # Set measurement to "packet"
    measurement = "packet"

    try:
        tags.append("from={0}".format(jsonData.get("from")))
        tags.append("format={0}".format(jsonData.get("format")))

    except KeyError as e:
        logger.error(e)

    tagStr = ",".join(tags)

    fieldNumKeys = ["latitude", "longitude", "posambiguity", "altitude", "speed", "course", "mbits"]
    fieldTextKeys = ["via", "to", "mtype"]

    try:
        for key in fieldNumKeys:
            if key in jsonData:
                fields.append("{0}={1}".format(key,jsonData.get(key)))
        for key in fieldTextKeys:
            if key in jsonData:
                fields.append("{0}=\"{1}\"".format(key,jsonData.get(key)))
        if "path" in jsonData:
            fields.append(parsePath(jsonData.get("path")))
        if "comment" in jsonData:
            comment = parseTextString(jsonData.get("comment"), "comment")
            if len(jsonData.get("comment")) > 0:
                fields.append(comment)
            else:
                pass
        fields = parseTelemetry(jsonData, fields)

    except KeyError as e:
        logger.error("KeyError: {0}, Mic-E Packet".format(e))
        logger.error(jsonData)

    fieldsStr = ",".join(fields)

    return measurement + "," + tagStr + " " + fieldsStr


def parseObject(jsonData):
    """Parse Object APRS packets into influxedb line protocol

    keyword arguments:
    jsonData -- aprslib parsed JSON packet
    """
    # Converts aprslib JSON to influxdb line protocol
    # Schema
    # measurement = packet*
    # tag = from*
    # field = to
    # field = symbolTable
    # field = symbol
    # tag = format*
    # field = via
    # field = alive*
    # field = objectFormat*
    # field = objectName*
    # field = latitude*
    # field = longitude*
    # field = posAmbiguity*
    # field = rawTimestamp*
    # field = timestamp*
    # field = speed*
    # field = course*
    # field = comment*
    # field = path*

    # initialize variables
    tags = []
    fields = []

    # Set measurement to "packet"
    measurement = "packet"

    try:
        tags.append("from={0}".format(jsonData.get("from")))
        #tags.append("to={0}".format(jsonData.get("to")))
        tags.append("format={0}".format(jsonData.get("format")))

    except KeyError as e:
        logger.error(e)

    tagStr = ",".join(tags)

    fieldNumKeys = ["latitude", "longitude", "posambiguity", "speed", "course", "timestamp"]
    fieldTextKeys = ["alive", "via", "to", "raw_timestamp", "object_format", "object_name"]

    try:
        for key in fieldNumKeys:
            if key in jsonData:
                fields.append("{0}={1}".format(key,jsonData.get(key)))
        for key in fieldTextKeys:
            if key in jsonData:
                fields.append("{0}=\"{1}\"".format(key,jsonData.get(key)))
        if "path" in jsonData:
            fields.append(parsePath(jsonData.get("path")))
        if "comment" in jsonData:
            comment = parseTextString(jsonData.get("comment"), "comment")
            if len(jsonData.get("comment")) > 0:
                fields.append(comment)
            else:
                pass
        fields = parseTelemetry(jsonData, fields)

    except KeyError as e:
        logger.error("KeyError: {0}, object Packet".format(e))
        logger.error(jsonData)

    fieldsStr = ",".join(fields)

    return measurement + "," + tagStr + " " + fieldsStr


def parseStatus(jsonData):
    """Parse Status APRS packets into influxedb line protocol

    keyword arguments:
    jsonData -- aprslib parsed JSON packet
    """
    # Converts aprslib JSON to influxdb line protocol
    # Schema
    # measurement = packet*
    # tag = from*
    # field = to*
    # tag = format*
    # field = via*
    # field = status*
    # field = path*

    # initialize variables
    tags = []
    fields = []

    # Set measurement to "packet"
    measurement = "packet"

    try:
        tags.append("from={0}".format(jsonData.get("from")))
        tags.append("format={0}".format(jsonData.get("format")))

    except KeyError as e:
        logger.error(e)

    tagStr = ",".join(tags)

    fieldTextKeys = ["via", "to"]

    try:
        for key in fieldTextKeys:
            if key in jsonData:
                fields.append("{0}=\"{1}\"".format(key,jsonData.get(key)))
        if "path" in jsonData:
            fields.append(parsePath(jsonData.get("path")))
        fields = parseTelemetry(jsonData, fields)

        if "status" in jsonData:
            comment = parseTextString(jsonData.get("status"), "status")
            if len(jsonData.get("status")) > 0:
                fields.append(comment)
            else:
                pass

    except KeyError as e:
        logger.error("KeyError: {0}, object Packet".format(e))
        logger.error(jsonData)

    fieldsStr = ",".join(fields)

    return measurement + "," + tagStr + " " + fieldsStr


def parseCompressed(jsonData):
    """Parse Compressed APRS packets into influxedb line protocol

    keyword arguments:
    jsonData -- aprslib parsed JSON packet
    """
    # Converts aprslib JSON to influxdb line protocol
    # Schema
    # measurement = packet
    # tag = from*
    # field = to*
    # field = symbolTable
    # field = symbol
    # tag = format*
    # field = via*
    # field = messageCapable*
    # field = latitude*
    # field = longitude*
    # field = gpsFixStatus*
    # field = altitude*
    # field = seq*
    # field = analog1*
    # field = analog2*
    # field = analog3*
    # field = analog4*
    # field = analog5*
    # field = bits*
    # field = comment*
    # field = path*

    # initialize variables
    tags = []
    fields = []

    # Set measurement to "packet"
    measurement = "packet"

    try:
        tags.append("from={0}".format(jsonData.get("from")))
        #tags.append("to={0}".format(jsonData.get("to")))
        tags.append("format={0}".format(jsonData.get("format")))

    except KeyError as e:
        logger.error(e)

    tagStr = ",".join(tags)

    fieldNumKeys = ["latitude","longitude","gpsfixstatus","altitude"]
    fieldTextKeys = ["to", "messagecapable"]
    fieldTelemetryKeys = ["seq","bits"]

    try:
        for key in fieldNumKeys:
            if key in jsonData:
                fields.append("{0}={1}".format(key,jsonData.get(key)))
        for key in fieldTextKeys:
            if key in jsonData:
                fields.append("{0}=\"{1}\"".format(key,jsonData.get(key)))
        if "path" in jsonData:
            fields.append(parsePath(jsonData.get("path")))
        if "comment" in jsonData:
            comment = parseTextString(jsonData.get("comment"), "comment")
            if len(jsonData.get("comment")) > 0:
                fields.append(comment)
            else:
                pass
        fields = parseTelemetry(jsonData, fields)

    except KeyError as e:
        # Expect many KeyErrors for stations not sending telemetry
        pass

    fieldsStr = ",".join(fields)

    return measurement + "," + tagStr + " " + fieldsStr


def parseWX(jsonData):
    """Parse WX APRS packets into influxedb line protocol

    keyword arguments:
    jsonData -- aprslib parsed JSON packet
    """
    # Converts aprslib JSON to influxdb line protocol
    # Schema
    # measurement = packet*
    # tag = from
    # field = to
    # tag = format
    # field = via
    # field = wxRawTimestamp
    # field = comment
    # field = humidity
    # field = pressure
    # field = rain1h
    # field = rain24h
    # field = rainSinceMidnight
    # field = temperature
    # field = windDirection
    # field = windGust
    # field = windSpeed
    # field = path*

    # initialize variables
    tags = []
    fields = []

    # Set measurement to "packet"
    measurement = "packet"

    try:
        tags.append("from={0}".format(jsonData.get("from")))
        tags.append("format={0}".format(jsonData.get("format")))

    except KeyError as e:
        logger.error(e)

    tagStr = ",".join(tags)

    fieldTextKeys = ["to", "via", "wx_raw_timestamp"]

    try:
        fields = parseWeather(jsonData, fields)
        for key in fieldTextKeys:
            if key in jsonData:
                fields.append("{0}=\"{1}\"".format(key,jsonData.get(key)))
        if "path" in jsonData:
            fields.append(parsePath(jsonData.get("path")))
        if "comment" in jsonData:
            comment = parseTextString(jsonData.get("comment"), "comment")
            if len(jsonData.get("comment")) > 0:
                fields.append(comment)
            else:
                pass

    except KeyError as e:
        # Expect many KeyErrors for stations not sending telemetry
        pass

    fieldsStr = ",".join(fields)

    return measurement + "," + tagStr + " " + fieldsStr


def parseBeacon(jsonData):
    """Parse Beacon APRS packets into influxedb line protocol

    keyword arguments:
    jsonData -- aprslib parsed JSON packet
    """
    # Converts aprslib JSON to influxdb line protocol
    # Schema
    # measurement = packet
    # tag = from
    # field = to
    # tag = format
    # field = via
    # field = text*
    # field = path*

    # initialize variables
    tags = []
    fields = []

    # Set measurement to "packet"
    measurement = "packet"

    try:
        tags.append("from={0}".format(jsonData.get("from")))
        tags.append("format={0}".format(jsonData.get("format")))

    except KeyError as e:
        logger.error(e)

    tagStr = ",".join(tags)


    fieldTextKeys = ["to", "via"]

    try:
        for key in fieldTextKeys:
            if key in jsonData:
                fields.append("{0}=\"{1}\"".format(key,jsonData.get(key)))
        if "path" in jsonData:
            fields.append(parsePath(jsonData.get("path")))
        if "text" in jsonData:
            comment = parseTextString(jsonData.get("text"), "text")
            if len(jsonData.get("text")) > 0:
                fields.append(comment)
            else:
                pass

    except KeyError as e:
        # Expect many KeyErrors for stations not sending telemetry
        pass

    fieldsStr = ",".join(fields)

    return measurement + "," + tagStr + " " + fieldsStr


def parseBulletin(jsonData):
    """Parse Bulletin APRS packets into influxedb line protocol

    keyword arguments:
    jsonData -- aprslib parsed JSON packet
    """
    # Converts aprslib JSON to influxdb line protocol
    # Schema
    # measurement = packet
    # tag = from
    # field = to
    # tag = format
    # field = via
    # field = messageText
    # field = bid
    # field = identifier (empty)
    # field = path*

    # initialize variables
    tags = []
    fields = []

    # Set measurement to "packet"
    measurement = "packet"

    try:
        tags.append("from={0}".format(jsonData.get("from")))
        #tags.append("to={0}".format(jsonData.get("to")))
        tags.append("format={0}".format(jsonData.get("format")))

    except KeyError as e:
        logger.error(e)

    tagStr = ",".join(tags)

    try:
        text = parseTextString(jsonData["message_text"], "messageText")
        if len(jsonData.get("message_text")) > 0:
            fields.append(text)
        else:
            pass

    except KeyError:
        # happens
        pass

    if jsonData.get("via"):
        fields.append("via=\"{0}\"".format(jsonData.get("via")))
    fields.append("to=\"{0}\"".format(jsonData.get("to")))
    fields.append("bid=\"{0}\"".format(jsonData.get("bid", 0)))
    if jsonData.get("identifier"):
        fields.append("identifier=\"{0}\"".format(jsonData.get("identifier")))
    if jsonData.get("path"):
        fields.append(parsePath(jsonData.get("path")))

    fieldsStr = ",".join(fields)

    return measurement + "," + tagStr + " " + fieldsStr


def parseMessage(jsonData):
    """Parse Message APRS packets into influxedb line protocol

    keyword arguments:
    jsonData -- aprslib parsed JSON packet
    """
    # Converts aprslib JSON to influxdb line protocol
    # Schema
    # measurement = packet
    # tag = from
    # field = to
    # tag = format
    # field = via
    # field = addresse
    # field = messageText
    # field = bid
    # field = identifier (empty)
    # field = path*

    # initialize variables
    tags = []
    fields = []

    # Set measurement to "packet"
    measurement = "packet"

    try:
        tags.append("from={0}".format(jsonData.get("from")))
        #tags.append("to={0}".format(jsonData.get("to")))
        tags.append("format={0}".format(jsonData.get("format")))

    except KeyError as e:
        logger.error(e)

    tagStr = ",".join(tags)

    try:
        text = parseTextString(jsonData["message_text"], "messageText")
        if len(jsonData.get("message_text")) > 0:
            fields.append(text)
        else:
            pass

    except KeyError:
        # happens
        pass

    fields.append("addresse=\"{0}\"".format(jsonData.get("addresse")))
    if jsonData.get("via"):
        fields.append("via=\"{0}\"".format(jsonData.get("via")))
    fields.append("to=\"{0}\"".format(jsonData.get("to")))
    fields.append("bid=\"{0}\"".format(jsonData.get("bid", 0)))
    if jsonData.get("identifier"):
        fields.append("identifier={0}".format(jsonData.get("identifier")))
    if jsonData.get("path"):
        fields.append(parsePath(jsonData.get("path")))

    fieldsStr = ",".join(fields)

    return measurement + "," + tagStr + " " + fieldsStr


def parseTextString(rawText, name):
    if len(rawText) > 0:
        try:
            text = rawText.encode('ascii', 'replace')
            text = text.replace("\\", "\\\\")
            text = text.replace("\'", "\\\'")
            text = text.replace("\"", "\\\"")
            textStr = ("{0}=\"{1}\"".format(name, text))

        except UnicodeError as e:
            logger.error(e)

        except TypeError as e:
            logger.error(e)

        return textStr

    else:
        return rawText


def parsePath(path):
    """Take path and turn into a string

    keyword arguments:
    path -- list of paths
    """

    temp = ",".join(path)
    pathStr = ("path=\"{0}\"".format(temp))

    return pathStr


def callback(packet):
    """aprslib callback for every packet received from APRS-IS connection

    keyword arguments:
    packet -- APRS-IS packet from aprslib connection
    """
    #logger.info(packet)

    # Open a new connection every time, probably SLOWWWW
    influxConn = connectInfluxDB()
    try:
        line = jsonToLineProtocol(packet)
    except StandardError as e:
        logger.error(e)

    if line:
        #logger.debug(line)
        try:
            influxConn.write_points([line], protocol='line')

        except StandardError as e:
            logger.error(e)
            logger.error(packet)

        except influxdb.exceptions.InfluxDBClientError as e:
            logger.error(packet["raw"])
            logger.error(e)

        except influxdb.exceptions.InfluxDBServerError as e:
            logger.error(packet["raw"])
            logger.error(e)



def connectInfluxDB():
    """Connect to influxdb database with configuration values"""

    return InfluxDBClient(args.dbhost,
                          args.dbport,
                          args.dbuser,
                          args.dbpassword,
                          args.dbname)


def consumer(conn):
    """Start consumer function for thread

    keyword arguments:
    conn -- APRS-IS connection from aprslib
    """
    logger.debug("starting consumer thread")
    # Obtain raw APRS-IS packets and sent to callback when received
    conn.consumer(callback, immortal=True, raw=False)


def heartbeat(conn, callsign, interval):
    """Send out an APRS status message to keep connection alive

    keyword arguments:
    conn -- APRS-IS connction from aprslib
    callsign -- Callsign of status message
    interval -- Minutes betwee status messages
    """
    logger.debug("Starting heartbeat thread")
    while True:
        # Create timestamp
        timestamp = int(time.time())

        # Create APRS status message
        status = "{0}>APRS,TCPIP*:>aprs2influxdb heartbeat {1}"
        conn.sendall(status.format(callsign, timestamp))
        logger.debug("Sent heartbeat")

        # Sleep for specified time
        time.sleep(float(interval) * 60)  # Sent every interval minutes


def createLog(path, debug=False):
    """Create a rotating log at the specified path and return logger

    keyword arguments:
    path -- path to log file
    debug -- Boolean to set DEBUG log level,
    """
    tempLogger = logging.getLogger(__name__)

    # Add handler for rotating file
    handler = TimedRotatingFileHandler(path,
                                       when="h",
                                       interval=1,
                                       backupCount=5)
    tempLogger.addHandler(handler)

    # Add handler for stdout printing
    screenHandler = logging.StreamHandler(sys.stdout)
    tempLogger.addHandler(screenHandler)

    # Set logging level
    if debug:
        tempLogger.setLevel(logging.DEBUG)
    else:
        tempLogger.setLevel(logging.WARNING)

    return tempLogger


def main():
    """Main function of aprs2influxdb

    Reads in configuration values and starts connection to APRS-IS with aprslib.
    Then two threads are started, one to monitor for APRS-IS packets and
    another to periodically send status packets to APRS-IS in order to keep
    the connection alive.
    """
    # Create logger, must be global for functions and threads
    global logger

    # Log to sys.prefix + aprs2influxdb.log
    log = os.path.join(sys.prefix, "aprs2influxdb.log")
    logger = createLog(log, args.debug)

    # Start login for APRS-IS
    logger.info("Logging into APRS-IS as {0} on port {1}".format(args.callsign, args.port))
    if args.callsign == "nocall":
        logger.warning("APRS-IS ignores the callsign \"nocall\"!")

    # Open APRS-IS connection
    passcode = aprslib.passcode(args.callsign)
    AIS = aprslib.IS(args.callsign,
                     passwd=passcode,
                     port=args.port)

    AIS.logger = logger
    try:
        AIS.connect()

    except aprslib.exceptions.LoginError as e:
        logger.error(e)
        logger.info("APRS Login Callsign: {0} Port: {1}".format(args.callsign, args.port))
        sys.exit(1)

    except aprslib.exceptions.ConnectionError as e:
        logger.error(e)
        sys.exit(1)

    # Create heartbeat
    t1 = threading.Thread(target=heartbeat, args=(AIS, args.callsign, args.interval))

    # Create consumer
    t2 = threading.Thread(target=consumer, args=(AIS,))

    # Start threads
    t1.start()
    t2.start()


if __name__ == "__main__":
    main()
