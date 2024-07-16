from argparse import ArgumentParser, Namespace
from datetime import datetime
from pathlib import Path

from qrSVG.qr import QR


class Parser(Namespace):
    logo: Path
    output: Path


parser = ArgumentParser()
parser.add_argument("logo", type=Path)
parser.add_argument(*("-o", "--output"), type=Path, default=Path.cwd() / "output.svg")
args = parser.parse_args(namespace=Parser())


# https://sv.wikipedia.org/wiki/V-card

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

# qr.add_data("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

_data = data.strip().format(date=datetime.now().strftime("%Y%m%dT%H%M%SZ"))
print(_data)

QR(_data).with_logo(args.logo, args.output)
