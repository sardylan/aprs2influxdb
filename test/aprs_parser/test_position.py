import pytest

from parser import Parser


@pytest.fixture(name="parser_instance")
def get_parser():
    yield Parser()


def test_position(parser_instance):
    data_input: dict = {
        "raw": "IR0UBN>APDW16,WIDE1-1,qAR,IS0ANU-12:!3924.97N/00929.74E#PHG3110/A=002526E.R.A. Cagliari Digipeater - Genn'Argiolas - Loc: JM49rj",
        "from": "IR0UBN",
        "to": "APDW16",
        "path": ["WIDE1-1", "qAR", "IS0ANU-12"],
        "via": "IS0ANU-12",
        "messagecapable": False,
        "format": "uncompressed",
        "posambiguity": 0,
        "symbol": "#",
        "symbol_table": "/",
        "latitude": 39.41616666666667,
        "longitude": 9.495666666666667,
        "phg": "3110",
        "phg_power": 9,
        "phg_height": 6.096,
        "phg_gain": 1.2589254117941673,
        "phg_dir": "omni",
        "phg_range": 8.830411247154684,
        "altitude": 769.9248,
        "comment": "E.R.A. Cagliari Digipeater - Genn'Argiolas - Loc: JM49rj"
    }

    data_expected: str = 'packet,format=uncompressed latitude=39.41616666666667,longitude=9.495666666666667,posambiguity=0,altitude=769.9248,from="IR0UBN",to="APDW16",messagecapable="False",phg="3110",via="IS0ANU-12",path="WIDE1-1,qAR,IS0ANU-12",comment="E.R.A. Cagliari Digipeater - Genn\\\'Argiolas - Loc: JM49rj",raw="IR0UBN>APDW16,WIDE1-1,qAR,IS0ANU-12:!3924.97N/00929.74E#PHG3110/A=002526E.R.A. Cagliari Digipeater - Genn\\\'Argiolas - Loc: JM49rj",symbol="#",symbol_table="/"'

    data_actual: str = parser_instance.parse_uncompressed(data_input)

    assert data_actual == data_expected
