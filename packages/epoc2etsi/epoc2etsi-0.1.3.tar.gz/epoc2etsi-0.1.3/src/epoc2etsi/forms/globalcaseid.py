from datetime import date
from re import compile
from uuid import uuid4, UUID
from bitarray import bitarray

INSTRUMENTS = [
    "EIO",
    "MLA",
    "ITN",
    "EPOC",
    "EPOCPR",
    "SODA",
    "SODB",
    "SODX",
    "TOEA",
    "TOEL",
    "TOEX",
]

GCI_REGEX = compile(r"(EIO|MLA|ITN|EPOC|EPOCPR|SODA|SODB|SODX|TOEA|TOEL|TOEX)-[A-Z]{2}-[A-Z]{2}-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{4}-[0-9]+")

class GlobalCaseID:
    
    @staticmethod
    def parse_from_gci(s: str):
        if not GCI_REGEX.match(s):
            raise ValueError(f"String {s} does not match GCI regex")
        parts = s.split("-")
        return GlobalCaseID(parts[0],
            parts[1],
            parts[2],
            date.fromisoformat(f"{parts[3]}-{parts[4]}-{parts[5]}"),
            int(parts[6]),
            int(parts[7]))

    @staticmethod
    def parse_from_uuid(s: str):
        uuid = UUID(s)
        parts = s.split("-")
        return GlobalCaseID(
            INSTRUMENTS[int(parts[4][0:2], 16)],
            GlobalCaseID.hex_to_country(parts[2][1:]),
            GlobalCaseID.hex_to_country(parts[3][1:]),
            date.fromisoformat(parts[0]),
            int(parts[1]),
            int(parts[4][4:], 16)
        )

    @staticmethod
    def a_to_z_as_int(c: str):
        if len(c) != 1:
            raise ValueError(f"Input value {c} not a single character")
        return ord(c[0]) - ord('A')

    @staticmethod
    def int_as_a_to_z(i: int):
        return chr(i + ord('A'))

    @staticmethod
    def country_to_hex(c: str):
        if len(c) != 2:
            raise ValueError(f"Input value {c} not a valid ISO country code")
        i_hi = GlobalCaseID.a_to_z_as_int(c[0])
        i_lo = GlobalCaseID.a_to_z_as_int(c[1])
        i = (i_hi << 5) + i_lo
        return f"{i:0>3X}"


    @staticmethod
    def hex_to_country(h: str):
        i = int(h, 16)
        i_lo = (i & 0x19)
        i_hi = i - i_lo
        return GlobalCaseID.int_as_a_to_z(i_hi >> 5) + GlobalCaseID.int_as_a_to_z(i_lo)
    
    def __init__(self, instrument, issuing_country, executing_country, issue_date, issue_date_sequence, national_id):
        self.instrument = instrument
        self.issuing_country = issuing_country
        self.executing_country = executing_country
        self.issue_date = issue_date
        self.issue_date_sequence = issue_date_sequence
        self.national_id = national_id

    def as_gci(self):
        return f"{self.instrument}-{self.issuing_country}-{self.executing_country}-{self.issue_date.isoformat()}-{self.issue_date_sequence:04}-{self.national_id}"

    def as_uuid(self):
        return f"{self.issue_date.isoformat().replace("-","")}-"\
               f"{self.issue_date_sequence:04}-"\
               f"4{GlobalCaseID.country_to_hex(self.issuing_country)}-"\
               f"9{GlobalCaseID.country_to_hex(self.executing_country)}-"\
               f"{INSTRUMENTS.index(self.instrument):0>2X}{self.national_id:0>10X}"

def uuid_from_global_case_id (global_case_id: str):
    return GlobalCaseID.parse_from_gci(global_case_id)

def global_case_id_from_uuid (uuid: str):
    return GlobalCaseID.parse_from_uuid(uuid)


from sys import argv

def gci2uuid () -> None:
    uuid_str = uuid_from_global_case_id(argv[1]).as_uuid()
    print(uuid_str)

def uuid2gci () -> None:
    gci = GlobalCaseID.parse_from_uuid(argv[1])
    print(gci.as_gci())
