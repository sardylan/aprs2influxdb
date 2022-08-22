import pytest

from parser import Parser


@pytest.fixture(name="parser_instance")
def get_parser():
    yield Parser()


def test_uncompressed(parser_instance):
    data_input: dict = {
        "raw": "N0CALL>APRS,WIDE1-1,qAR,N0CALL:!0.00N/0.00E#MESSAGE",
        "from": "N0CALL",
        "to": "APRS",
        "path": ["WIDE1-1", "qAR", "N0CALL"],
        "via": "N0CALL",
        "messagecapable": False,
        "format": "uncompressed",
        "posambiguity": 0,
        "symbol": "#",
        "symbol_table": "/",
        "latitude": 0,
        "longitude": 0,
        "comment": "MESSAGE"
    }

    data_expected: str = 'packet,format=uncompressed latitude=0,longitude=0,posambiguity=0,from="N0CALL",to="APRS",messagecapable="False",via="N0CALL",path="WIDE1-1,qAR,N0CALL",comment="MESSAGE",raw="N0CALL>APRS,WIDE1-1,qAR,N0CALL:!0.00N/0.00E#MESSAGE",symbol="#",symbol_table="/"'

    data_actual: str = parser_instance.parse_uncompressed(data_input)

    assert data_actual == data_expected
