import logging
import math
from typing import Optional

_logger = logging.getLogger(__name__)


class Parser:
    telemetry_dictionary: dict

    def __init__(self) -> None:
        super().__init__()

        self.telemetry_dictionary = {}

    def json_to_line_protocol(self, json_data):
        """Converts JSON APRS-IS packet to influxdb line protocol

        Takes in a JSON packet from aprslib (raw=false) and parses it into an
        influxdb line protocol compliant string to insert into database. Returns
        a valid line protocol string ready to be inserted into the database.

        keyword arguments:
        json_data -- aprslib parsed JSON packet
        """

        try:
            if json_data["format"] == "uncompressed":
                # Parse uncompressed APRS packet
                return self.parse_uncompressed(json_data)

            if json_data["format"] == "mic-e":
                # Parse mic-e APRS packet
                return self.parse_mic_e(json_data)

            if json_data["format"] == "object":
                # Parse object APRS packet
                return self.parse_object(json_data)

            if json_data["format"] == "compressed":
                # Parse compressed APRS packet
                return self.parse_compressed(json_data)

            if json_data["format"] == "status":
                # Parse status APRS packet
                return self.parse_status(json_data)

            if json_data["format"] == "wx":
                # Parse wx APRS packet
                return self.parse_wx(json_data)

            if json_data["format"] == "beacon":
                # Parse beacon APRS packet
                return self.parse_beacon(json_data)

            if json_data["format"] == "bulletin":
                # Parse bulletin APRS packet
                return self.parse_bulletin(json_data)

            if json_data["format"] == "message":
                # Parse message APRS packet
                return self.parse_message(json_data)

            if json_data["format"] == "telemetry-message":
                # Parse telemetry-message APRS packet
                # Currently only support scaling values
                return self.parse_telemetry_scaling(json_data)

            # All other formats not yes parsed
            _logger.debug("Not parsing {0} packets".format(json_data))

        except Exception as e:
            _logger.error(e)
            _logger.error("Packet: {0}".format(json_data))

    def parse_telemetry(self, json_data: dict, field_list: list):
        """parse telemetry from packets

        Iterates through a packet to extra telemetry data: sequence, bits, and
        values. These are placed into the field_list which is returned at the end of
        the function.

        keyword arguments:
        json_data -- JSON packet from aprslib
        field_list -- list of field items currently parsed
        """

        # Check for telemetry in packet
        if "telemetry" in json_data:
            items = json_data.get("telemetry")
            # Extract telemetry sequency
            if "seq" in items:
                field_list.append("seq={0}".format(items.get("seq")))
            # Extract IO bits
            if "bits" in items:
                field_list.append("bits={0}".format(items.get("bits")))
            # Attempt to retrieve scaling values from telemetry_dictionary
            try:
                channels = self.telemetry_dictionary[json_data["from"]]
            except KeyError:
                # No scaling values found, assign generic scaling to channels
                channels = []
                for eqn in range(5):
                    # Create a scaling dictionary for all five measurements
                    equations = {"a": 0, "b": 0, "c": 0, }
                    equations["a"] = 0
                    equations["b"] = 1
                    equations["c"] = 0
                    channels.append(equations)

            # Extract analog values from telemtry packet
            if "vals" in items:
                values = items.get("vals")
                for analog in range(5):
                    # Apply scaling equation A*V**2 + B*V + C
                    telemVal = channels[analog]["a"] * math.pow(values[analog], 2) + channels[analog]["b"] * values[
                        analog] + channels[analog]["c"]
                    field_list.append("analog{0}={1}".format(analog + 1, telemVal))

        # Return field_list with found items appended
        return field_list

    @staticmethod
    def parse_equations(json_data: dict) -> Optional[list]:
        """
        Iterates through a telemetry-message packet for tEQNs values which are
        scaling parameters for telemetry data. Places each equation coefficient into
        a dictionary which is then placed into a list for each measurement.
        Returns a channels list or None

        keyword arguments:
        json_data -- JSON packet from aprslib
        """

        if "tEQNS" not in json_data:
            return None

        # Exists, initialize channels list and extract equations list
        channels: list = []

        items = json_data.get("tEQNS")
        for eqn in items:
            # Iterate through each measurement coefficient list, assign to dictionary
            channels.append({
                "a": eqn[0],
                "b": eqn[1],
                "c": eqn[2]
            })

        return channels

    @staticmethod
    def parse_weather(json_data: dict, field_list: list) -> list:
        """parse weather data from packets

        Iterates through a packet to extra weather data. Items which are found are
        appended to the field_list which is returned.

        keyword arguments:
        json_data -- JSON packet from aprslib
        field_list -- list of field items currently parsed
        """

        # Check for weather data key
        if "weather" in json_data:
            items = json_data.get("weather")

            # Define weather items to check for
            wx_fields = ["humidity", "pressure", "rain_1h", "rain_24h", "rain_since_midnight", "temperature",
                         "wind_direction", "wind_gust", "wind_speed"]
            for key in wx_fields:
                if key in items:
                    field_list.append("{0}={1}".format(key, items.get(key)))

        # Return field_list with found items appended
        return field_list

    def parse_uncompressed(self, json_data: dict) -> str:
        """Parse uncompressed APRS packets into influxedb line protocol. Returns a
        valid line protocol string.

        keyword arguments:
        json_data -- aprslib parsed JSON packet
        """

        ## Schema
        # field = from
        # field = to
        # field = symbol_table
        # field = symbol
        # tag = format
        # field = via
        # field = messagecapable
        # field = latitude
        # field = longitude
        # field = posAmbiguity
        # field = altitude
        # field = raw
        # field = speed
        # field = course
        # field = raw_timestamp
        # field = seq
        # field = analog1
        # field = analog2
        # field = analog3
        # field = analog4
        # field = analog5
        # field = bits
        # field = phg
        # field = rng
        # field = comment
        # field = path
        # field = pressure
        # field = rain_1h
        # field = rain_24h
        # field = rain_since_midnight
        # field = temperature
        # field = wind_direction
        # field = wind_gust
        # field = wind_speed

        # initialize variables
        tags = []
        fields = []

        # Set measurement to "packet"
        measurement = "packet"

        # Obtain tags
        #
        tags.append("format={0}".format(json_data.get("format")))

        # Join tags into comma separated string
        tag_str = ",".join(tags)

        # Create field key lists to iterate through
        field_num_keys = ["latitude", "longitude", "posambiguity", "altitude", "speed", "course"]
        field_text_keys = ["from", "to", "messagecapable", "phg", "rng", "via"]

        # Extract number fields from packet
        for key in field_num_keys:
            if key in json_data:
                fields.append("{0}={1}".format(key, json_data.get(key)))

        # Extract text fields from packet
        for key in field_text_keys:
            if key in json_data:
                fields.append("{0}=\"{1}\"".format(key, json_data.get(key)))

        # Extract path
        if "path" in json_data:
            fields.append(Parser.parse_path(json_data.get("path")))

        # Extract comment
        if "comment" in json_data:
            comment = Parser.parse_text_string(json_data.get("comment"), "comment")
            if len(json_data.get("comment")) > 0:
                fields.append(comment)

        # Extract raw packet
        if "raw" in json_data:
            comment = Parser.parse_text_string(json_data.get("raw"), "raw")
            if len(json_data.get("raw")) > 0:
                fields.append(comment)

        # Extract APRS symbol
        if "symbol" in json_data:
            comment = Parser.parse_text_string(json_data.get("symbol"), "symbol")
            if len(json_data.get("symbol")) > 0:
                fields.append(comment)

        # Extract APRS symbol table
        if "symbol_table" in json_data:
            comment = Parser.parse_text_string(json_data.get("symbol_table"), "symbol_table")
            if len(json_data.get("symbol_table")) > 0:
                fields.append(comment)

        # Extract raw timestamp from packet
        if "raw_timestamp" in json_data:
            rawtimestamp = Parser.parse_text_string(json_data.get("raw_timestamp"), "raw_timestamp")
            if len(json_data.get("raw_timestamp")) > 0:
                fields.append(rawtimestamp)

        # Parse telemetry data
        fields = self.parse_telemetry(json_data, fields)

        # Parse weather data
        fields = Parser.parse_weather(json_data, fields)

        # Combine all fields into a valid line protocol string
        fields_str = ",".join(fields)

        # Combine final valid line protocol string
        return measurement + "," + tag_str + " " + fields_str

    @staticmethod
    def parse_mic_e(json_data: dict) -> str:
        """Parse mic-e APRS packets into influxedb line protocol. Returns a
        valid line protocol string.

        keyword arguments:
        json_data -- aprslib parsed JSON packet
        """

        ## Schema
        # measurement = packet
        # field = from
        # field = symbol_table
        # field = symbol
        # tag = format
        # field = via
        # field = latitude
        # field = longitude
        # field = posambiguity
        # field = altitude
        # field = speed
        # field = course
        # field = comment
        # field = path
        # field = mbits
        # field = mtype
        # field = raw
        # field = to
        # field = daodatumbyte
        # field = path

        # initialize variables
        tags = []
        fields = []

        # Set measurement to "packet"
        measurement = "packet"

        # Obtain tags
        tags.append("format={0}".format(json_data.get("format")))

        # Join tags into comma separated string
        tag_str = ",".join(tags)

        # Create field key lists to iterate through
        field_num_keys = ["latitude", "longitude", "posambiguity", "altitude", "speed", "course", "mbits"]
        field_text_keys = ["from", "via", "to", "mtype", "daodatumbyte"]

        # Extract number fields from packet
        for key in field_num_keys:
            if key in json_data:
                fields.append("{0}={1}".format(key, json_data.get(key)))

        # Extract text fields from packet
        for key in field_text_keys:
            if key in json_data:
                fields.append("{0}=\"{1}\"".format(key, json_data.get(key)))

        # Extract path
        if "path" in json_data:
            fields.append(Parser.parse_path(json_data.get("path")))

        # Extract comment
        if "comment" in json_data:
            comment = Parser.parse_text_string(json_data.get("comment"), "comment")
            if len(json_data.get("comment")) > 0:
                fields.append(comment)
            else:
                pass

        # Extract raw packet
        if "raw" in json_data:
            comment = Parser.parse_text_string(json_data.get("raw"), "raw")
            if len(json_data.get("raw")) > 0:
                fields.append(comment)

        # Extract APRS symbol
        if "symbol" in json_data:
            comment = Parser.parse_text_string(json_data.get("symbol"), "symbol")
            if len(json_data.get("symbol")) > 0:
                fields.append(comment)

        # Extract APRS symbol table
        if "symbol_table" in json_data:
            comment = Parser.parse_text_string(json_data.get("symbol_table"), "symbol_table")
            if len(json_data.get("symbol_table")) > 0:
                fields.append(comment)

        # Combine final valid line protocol string
        fields_str = ",".join(fields)

        return measurement + "," + tag_str + " " + fields_str

    def parse_object(self, json_data: dict) -> str:
        """Parse Object APRS packets into influxedb line protocol

        keyword arguments:
        json_data -- aprslib parsed JSON packet
        """
        # Converts aprslib JSON to influxdb line protocol
        # Schema
        # measurement = packet
        # field = from
        # field = to
        # field = symbol_table
        # field = symbol
        # tag = format
        # field = via
        # field = alive
        # field = object_format
        # field = object_name
        # field = latitude
        # field = longitude
        # field = posambiguity
        # field = raw_timestamp
        # field = timestamp
        # field = speed
        # field = course
        # field = altitude
        # field = comment
        # field = path
        # field  = raw
        # field = daodatumbyte
        # field = rng
        # field = bits
        # field = seq
        # field = analog1
        # field = analog2
        # field = analog3
        # field = analog4
        # field = analog5

        # initialize variables
        tags = []
        fields = []

        # Set measurement to "packet"
        measurement = "packet"

        # Obtain tags
        # tags.append("from={0}".format(json_data.get("from")))
        tags.append("format={0}".format(json_data.get("format")))

        # Join tags into comma separated string
        tag_str = ",".join(tags)

        # Create field key lists to iterate through
        field_num_keys = ["latitude", "longitude", "posambiguity", "speed", "course", "timestamp", "altitude"]
        field_text_keys = ["from", "alive", "via", "to", "object_format", "object_name", "rng", "daodatumbyte"]

        # Extract number fields from packet
        for key in field_num_keys:
            if key in json_data:
                fields.append("{0}={1}".format(key, json_data.get(key)))

        # Extract text fields from packet
        for key in field_text_keys:
            if key in json_data:
                fields.append("{0}=\"{1}\"".format(key, json_data.get(key)))

        # Extract path
        if "path" in json_data:
            fields.append(Parser.parse_path(json_data.get("path")))

        # Extract comment
        if "comment" in json_data:
            comment = Parser.parse_text_string(json_data.get("comment"), "comment")
            if len(json_data.get("comment")) > 0:
                fields.append(comment)

        # Parse telemetry
        fields = self.parse_telemetry(json_data, fields)

        # Extract raw packet
        if "raw" in json_data:
            comment = Parser.parse_text_string(json_data.get("raw"), "raw")
            if len(json_data.get("raw")) > 0:
                fields.append(comment)

        # Extract symbol
        if "symbol" in json_data:
            comment = Parser.parse_text_string(json_data.get("symbol"), "symbol")
            if len(json_data.get("symbol")) > 0:
                fields.append(comment)

        # Extract symbol table
        if "symbol_table" in json_data:
            comment = Parser.parse_text_string(json_data.get("symbol_table"), "symbol_table")
            if len(json_data.get("symbol_table")) > 0:
                fields.append(comment)

        # Extract raw_timestamp
        if "raw_timestamp" in json_data:
            rawtimestamp = Parser.parse_text_string(json_data.get("raw_timestamp"), "raw_timestamp")
            if len(json_data.get("raw_timestamp")) > 0:
                fields.append(rawtimestamp)

        # Combine final valid line protocol string
        fields_str = ",".join(fields)

        return measurement + "," + tag_str + " " + fields_str

    def parse_status(self, json_data: dict) -> str:
        """Parse Status APRS packets into influxedb line protocol

        keyword arguments:
        json_data -- aprslib parsed JSON packet
        """

        ## Schema
        # measurement = packet
        # field = from
        # field = to
        # tag = format
        # field = via
        # field = status
        # field = path
        # field = timestamp
        # field = raw
        # field = raw_timestamp

        # initialize variables
        tags = []
        fields = []

        # Set measurement to "packet"
        measurement = "packet"

        # Obtain tags
        tags.append("format={0}".format(json_data.get("format")))

        # Join tags into comma separated string
        tag_str = ",".join(tags)

        # Create field key lists to iterate through
        field_num_keys = ["timestamp"]
        field_text_keys = ["from", "via", "to"]

        # Extract number fields from packet
        for key in field_num_keys:
            if key in json_data:
                fields.append("{0}={1}".format(key, json_data.get(key)))

        # Extract text fields from packet
        for key in field_text_keys:
            if key in json_data:
                fields.append("{0}=\"{1}\"".format(key, json_data.get(key)))

        # Extract path
        if "path" in json_data:
            fields.append(Parser.parse_path(json_data.get("path")))

        # Extract telemetry
        fields = self.parse_telemetry(json_data, fields)

        # Extract status
        if "status" in json_data:
            comment = Parser.parse_text_string(json_data.get("status"), "status")
            if len(json_data.get("status")) > 0:
                fields.append(comment)

        # Extract raw packet
        if "raw" in json_data:
            comment = Parser.parse_text_string(json_data.get("raw"), "raw")
            if len(json_data.get("raw")) > 0:
                fields.append(comment)

        # Extract raw timestamp
        if "raw_timestamp" in json_data:
            rawtimestamp = Parser.parse_text_string(json_data.get("raw_timestamp"), "raw_timestamp")
            if len(json_data.get("raw_timestamp")) > 0:
                fields.append(rawtimestamp)

        # Combine final valid line protocol string
        fields_str = ",".join(fields)

        return measurement + "," + tag_str + " " + fields_str

    def parse_compressed(self, json_data: dict) -> str:
        """Parse Compressed APRS packets into influxedb line protocol

        keyword arguments:
        json_data -- aprslib parsed JSON packet
        """

        ## Schema
        # measurement = packet
        # field = from
        # field = to
        # field = symbol_table
        # field = symbol
        # tag = format
        # field = via
        # field = messagecapable
        # field = latitude
        # field = longitude
        # field = gpsfixstatus
        # field = altitude
        # field = seq
        # field = analog1
        # field = analog2
        # field = analog3
        # field = analog4
        # field = analog5
        # field = bits
        # field = comment
        # field = path
        # field = phg
        # field = raw
        # field = timestamp
        # field = pressure
        # field = rain_1h
        # field = rain_24h
        # field = rain_since_midnight
        # field = temperature
        # field = wind_direction
        # field = wind_gust
        # field = wind_speed
        # field = speed
        # field = course

        # initialize variables
        tags = []
        fields = []

        # Set measurement to "packet"
        measurement = "packet"

        # Obtain tags
        tags.append("format={0}".format(json_data.get("format")))

        # Join tags into comma separated string
        tag_str = ",".join(tags)

        # Create field key lists to iterate through
        field_num_keys = ["latitude", "longitude", "gpsfixstatus", "altitude", "speed", "course", "timestamp"]
        field_text_keys = ["from", "to", "messagecapable", "phg", "via"]

        # Extract number fields from packet
        for key in field_num_keys:
            if key in json_data:
                fields.append("{0}={1}".format(key, json_data.get(key)))

        # Extract text fields from packet
        for key in field_text_keys:
            if key in json_data:
                fields.append("{0}=\"{1}\"".format(key, json_data.get(key)))

        # Extract path
        if "path" in json_data:
            fields.append(Parser.parse_path(json_data.get("path")))

        # Extract comment
        if "comment" in json_data:
            comment = Parser.parse_text_string(json_data.get("comment"), "comment")
            if len(json_data.get("comment")) > 0:
                fields.append(comment)

        # Extract telemetry
        fields = self.parse_telemetry(json_data, fields)

        # Extract weather data
        fields = Parser.parse_weather(json_data, fields)

        # Extract raw packet
        if "raw" in json_data:
            comment = Parser.parse_text_string(json_data.get("raw"), "raw")
            if len(json_data.get("raw")) > 0:
                fields.append(comment)

        # Extract APRS symbol
        if "symbol" in json_data:
            comment = Parser.parse_text_string(json_data.get("symbol"), "symbol")
            if len(json_data.get("symbol")) > 0:
                fields.append(comment)

        # Extract APRS symbol table
        if "symbol_table" in json_data:
            comment = Parser.parse_text_string(json_data.get("symbol_table"), "symbol_table")
            if len(json_data.get("symbol_table")) > 0:
                fields.append(comment)

        # Combine final valid line protocol string
        fields_str = ",".join(fields)

        return measurement + "," + tag_str + " " + fields_str

    def parse_wx(self, json_data: dict) -> str:
        """Parse WX APRS packets into influxedb line protocol

        keyword arguments:
        json_data -- aprslib parsed JSON packet
        """

        ## Schema
        # measurement = packet*
        # field = from
        # field = to
        # tag = format
        # field = via
        # field = wx_raw_timestamp
        # field = comment
        # field = humidity
        # field = pressure
        # field = rain_1h
        # field = rain_24h
        # field = rain_since_midnight
        # field = temperature
        # field = wind_direction
        # field = wind_gust
        # field = wind_speed
        # field = path
        # field = raw

        # initialize variables
        tags = []
        fields = []

        # Set measurement to "packet"
        measurement = "packet"

        # Obtain tags
        tags.append("format={0}".format(json_data.get("format")))

        # Join tags into comma separated string
        tag_str = ",".join(tags)

        # Create field key lists to iterate through
        field_text_keys = ["from", "to", "via"]

        # Extract text fields from packet
        for key in field_text_keys:
            if key in json_data:
                fields.append("{0}=\"{1}\"".format(key, json_data.get(key)))

        # Extract path
        if "path" in json_data:
            fields.append(Parser.parse_path(json_data.get("path")))

        # Extract comment
        if "comment" in json_data:
            comment = Parser.parse_text_string(json_data.get("comment"), "comment")
            if len(json_data.get("comment")) > 0:
                fields.append(comment)

        # Extract raw from packet
        if "raw" in json_data:
            comment = Parser.parse_text_string(json_data.get("raw"), "raw")
            if len(json_data.get("raw")) > 0:
                fields.append(comment)

        # Extract wx_raw_timestamp from packet
        if "wx_raw_timestamp" in json_data:
            rawtimestamp = Parser.parse_text_string(json_data.get("wx_raw_timestamp"), "wx_raw_timestamp")
            if len(json_data.get("wx_raw_timestamp")) > 0:
                fields.append(rawtimestamp)

        # Obtain weather data
        fields = Parser.parse_weather(json_data, fields)

        # Combine final valid line protocol string
        fields_str = ",".join(fields)

        return measurement + "," + tag_str + " " + fields_str

    @staticmethod
    def parse_beacon(json_data: dict) -> str:
        """Parse Beacon APRS packets into influxedb line protocol

        keyword arguments:
        json_data -- aprslib parsed JSON packet
        """

        ## Schema
        # measurement = packet
        # field = from
        # field = to
        # tag = format
        # field = via
        # field = text
        # field = path
        # field = raw

        # initialize variables
        tags = []
        fields = []

        # Set measurement to "packet"
        measurement = "packet"

        # Obtain tags
        tags.append("format={0}".format(json_data.get("format")))

        # Join tags into comma separated string
        tag_str = ",".join(tags)

        # Create field key lists to iterate through
        field_text_keys = ["from", "to", "via"]

        # Extract text fields from packet
        for key in field_text_keys:
            if key in json_data:
                fields.append("{0}=\"{1}\"".format(key, json_data.get(key)))

        # Extract path
        if "path" in json_data:
            fields.append(Parser.parse_path(json_data.get("path")))

        # Extract text
        if "text" in json_data:
            comment = Parser.parse_text_string(json_data.get("text"), "text")
            if len(json_data.get("text")) > 0:
                fields.append(comment)

        # Extract raw packet
        if "raw" in json_data:
            comment = Parser.parse_text_string(json_data.get("raw"), "raw")
            if len(json_data.get("raw")) > 0:
                fields.append(comment)

        # Combine final valid line protocol string
        fields_str = ",".join(fields)

        return measurement + "," + tag_str + " " + fields_str

    def parse_bulletin(self, json_data: dict) -> str:
        """Parse Bulletin APRS packets into influxedb line protocol

        keyword arguments:
        json_data -- aprslib parsed JSON packet
        """

        ## Schema
        # measurement = packet
        # field = from
        # field = to
        # tag = format
        # field = via
        # field = message_text
        # field = bid
        # field = identifier
        # field = path
        # field = raw

        # initialize variables
        tags = []
        fields = []

        # Set measurement to "packet"
        measurement = "packet"

        # Obtain tags
        tags.append("format={0}".format(json_data.get("format")))

        # Join tags into comma separated string
        tag_str = ",".join(tags)

        # Create field key lists to iterate through
        field_num_keys = ["bid"]
        field_text_keys = ["from", "to", "via"]

        # Extract number fields from packet
        for key in field_num_keys:
            if key in json_data:
                fields.append("{0}={1}".format(key, json_data.get(key)))

        # Extract text fields from packet
        for key in field_text_keys:
            if key in json_data:
                fields.append("{0}=\"{1}\"".format(key, json_data.get(key)))

        # Extract path
        if "path" in json_data:
            fields.append(Parser.parse_path(json_data.get("path")))

        # Extract message text
        if "message_text" in json_data:
            message = Parser.parse_text_string(json_data.get("message_text"), "message_text")
            if len(json_data.get("message_text")) > 0:
                fields.append(message)

        # Extract identifier
        if "identifier" in json_data:
            identifier = Parser.parse_text_string(json_data.get("identifier"), "identifier")
            if len(json_data.get("identifier")) > 0:
                fields.append(identifier)

        # Extract raw packet
        if "raw" in json_data:
            comment = Parser.parse_text_string(json_data.get("raw"), "raw")
            if len(json_data.get("raw")) > 0:
                fields.append(comment)

        # Combine final valid line protocol string
        fields_str = ",".join(fields)

        return measurement + "," + tag_str + " " + fields_str

    @staticmethod
    def parse_message(json_data: dict):
        """Parse Message APRS packets into influxedb line protocol

        keyword arguments:
        json_data -- aprslib parsed JSON packet
        """

        ## Schema
        # measurement = packet
        # field = from
        # field = to
        # tag = format
        # field = via
        # field = addresse
        # field = message_text
        # field = path
        # field = raw
        # field = msgNo
        # field = response

        # initialize variables
        tags: list = []
        fields: list = []

        # Set measurement to "packet"
        measurement = "packet"

        # Obtain tags
        tags.append("format={0}".format(json_data.get("format")))

        # Join tags into comma separated string
        tag_str = ",".join(tags)

        # Create field key lists to iterate through
        field_num_keys = ["msgNo"]
        field_text_keys = ["from", "to", "via", "addresse"]

        # Extract number fields from packet
        for key in field_num_keys:
            if key in json_data:
                fields.append("{0}={1}".format(key, json_data.get(key)))

        # Extract text fields from packet
        for key in field_text_keys:
            if key in json_data:
                fields.append("{0}=\"{1}\"".format(key, json_data.get(key)))

        # Extract path
        if "path" in json_data:
            fields.append(Parser.parse_path(json_data.get("path")))

        # Extract message text
        if "message_text" in json_data:
            message = Parser.parse_text_string(json_data.get("message_text"), "message_text")
            if len(json_data.get("message_text")) > 0:
                fields.append(message)

        # Extract response
        if "response" in json_data:
            message = Parser.parse_text_string(json_data.get("response"), "response")
            if len(json_data.get("response")) > 0:
                fields.append(message)

        # Extract raw from packet
        if "raw" in json_data:
            comment = Parser.parse_text_string(json_data.get("raw"), "raw")
            if len(json_data.get("raw")) > 0:
                fields.append(comment)

        # Combine final valid line protocol string
        fields_str = ",".join(fields)

        return measurement + "," + tag_str + " " + fields_str

    def parse_telemetry_scaling(self, json_data):
        """Parse Telemetry-Message APRS scaling value packets into influxedb line protocol

        keyword arguments:
        json_data -- aprslib parsed JSON packet
        """

        # Parse packet for equations
        equations = self.parse_equations(json_data)

        if equations:
            # If equations present, then add to dictionary of station
            # This is not ideal but required until Grafana supports SELECT queries
            # in templates.
            self.telemetry_dictionary[json_data.get("from")] = equations

    @staticmethod
    def parse_text_string(raw_text: str, name) -> str:
        """Parse text strings for invalid characters. Properly escape for
        line protocol strings if found.

        keyword arguments:
        rawText -- String to be checked
        name -- Name of field
        """

        # Check if length is valid
        if len(raw_text) <= 0:
            return raw_text

        try:
            # Convert to ASCII and replace invalid characters
            text: str = raw_text
            text = text.replace("\\", "\\\\")
            text = text.replace("\'", "\\\'")
            text = text.replace("\"", "\\\"")

            return f"{name}=\"{text}\""

        except UnicodeError as e:
            _logger.error(e)

        except TypeError as e:
            _logger.error(e)

    @staticmethod
    def parse_path(path: list) -> str:
        """Take path and turn into a string

        keyword arguments:
        path -- list of paths from aprslib
        """

        # Join path items into a string separated by commas, valid line protocol
        temp: str = ",".join(path)
        path_str: str = f"path=\"{temp}\""

        # Return line protocol string
        return path_str
