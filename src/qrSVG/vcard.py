from datetime import datetime
from itertools import chain


class VCard:
    def __init__(self, name, surname):
        self.bucket = [
            f"N:{surname};{name}",
            f"FN:{name} {surname}",
        ]

    def add_organization(self, organization):
        self.bucket.append(f"ORG:{organization}")

    def add_title(self, title):
        self.bucket.append(f"TITLE:{title}")

    def add_work_phone(self, number):
        self.bucket.append(f"TEL;TYPE=WORK,VOICE:{number}")

    def add_home_phone(self, number):
        self.bucket.append(f"TEL;TYPE=HOME,VOICE:{number}")

    def add_work_address(self, address, city, state, zip_code, country):
        self.bucket.extend(
            [
                f"ADR;TYPE=WORK:;;{address};{city};{state};{zip_code};{country}",
                f"LABEL;TYPE=WORK:{address}\n{city}, {state} {zip_code}\n{country}",
            ]
        )

    def add_home_address(self, address, city, state, zip_code, country):
        self.bucket.extend(
            [
                f"ADR;TYPE=HOME:;;{address};{city};{state};{zip_code};{country}",
                f"LABEL;TYPE=HOME:{address}\n{city}, {state} {zip_code}\n{country}",
            ]
        )

    def add_email(self, email):
        self.bucket.append(f"EMAIL;TYPE=PREF,INTERNET:{email}")

    def __str__(self):
        start = (
            "BEGIN:VCARD",
            "VERSION:3.0",
        )
        end = (
            f"REV:{datetime.now().strftime("%Y%m%dT%H%M%SZ")}",
            "END:VCARD",
        )
        return "\n".join(chain(start, self.bucket, end))


data = """
BEGIN:VCARD
VERSION:3.0
N:Gump;Forrest
FN:Forrest Gump
ORG:Bubba Gump Shrimp Co.
TITLE:Shrimp Man
TEL;TYPE=WORK,VOICE:(111) 555-1212
ADR;TYPE=WORK:;;100 Waters Edge;Baytown;LA;30314;United States of America
LABEL;TYPE=WORK:100 Waters Edge\nBaytown, LA 30314\nUnited States of America
EMAIL;TYPE=PREF,INTERNET:forrestgump@example.com
REV:{date}
END:VCARD
"""
