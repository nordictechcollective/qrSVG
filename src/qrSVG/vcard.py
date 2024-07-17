from datetime import datetime
from itertools import chain


# https://www.evenx.com/vcard-3-0-format-specification
# https://sv.wikipedia.org/wiki/V-card
class VCard:
    def __init__(self, name, surname):
        self._bucket = [
            f"N:{surname};{name}",
            f"FN:{name} {surname}",
        ]

    def add_organization(self, organization):
        self._bucket.append(f"ORG:{organization}")

    def add_title(self, title):
        self._bucket.append(f"TITLE:{title}")

    def add_work_phone(self, number):
        self._bucket.append(f"TEL;TYPE=WORK,VOICE:{number}")

    def add_home_phone(self, number):
        self._bucket.append(f"TEL;TYPE=HOME,VOICE:{number}")

    def add_work_address(self, street, city, state, zip_code, country):  # noqa: PLR0913
        self._bucket.extend(
            [
                f"ADR;TYPE=WORK:;;{street};{city};{state};{zip_code};{country}",
                f"LABEL;TYPE=WORK:{street}\n{city}, {state} {zip_code}\n{country}",
            ]
        )

    def add_home_address(self, address, city, state, zip_code, country):  # noqa: PLR0913
        self._bucket.extend(
            [
                f"ADR;TYPE=HOME:;;{address};{city};{state};{zip_code};{country}",
                f"LABEL;TYPE=HOME:{address}\n{city}, {state} {zip_code}\n{country}",
            ]
        )

    def add_email(self, email):
        self._bucket.append(f"EMAIL;TYPE=PREF,INTERNET:{email}")

    def add_url(self, website):
        self._bucket.append(f"URL:{website}")

    def add_note(self, note):
        self._bucket.append(f"NOTE:{note}")

    def __str__(self):
        start = (
            "BEGIN:VCARD",
            "VERSION:3.0",
        )
        end = (
            f"REV:{datetime.now().strftime("%Y%m%dT%H%M%SZ")}",
            "END:VCARD",
        )
        return "\n".join(chain(start, self._bucket, end))
