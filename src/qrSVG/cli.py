import re
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from importlib.metadata import version
from pathlib import Path

import inquirer

from qrSVG.containers import CorrectionLevel, Offset
from qrSVG.qr import QR
from qrSVG.vcard import VCard


class Parser(Namespace):
    logo: Path
    data: str
    output: Path
    scale: float
    blur: float
    margin: int
    offset: tuple[float, float]
    error_correction: CorrectionLevel


def validate_scale(value: str) -> float:
    _value = float(value)
    if 0.0 < _value <= 1.0:
        return _value
    raise ValueError("scale must be between 0 and 1")


DESCRIPTION = rf"""

                    _____ _____ _____
            ___ ___|   __|  |  |   __|
           | . |  _|__   |  |  |  |  |
           |_  |_| |_____|\___/|_____|
             |_|    v{version("qrSVG")}

a tool to generate QR codes with logos as SVG files.

Always test the QR code before using it, image injection
relies on the fact that QR codes are error tolerant.

https://en.wikipedia.org/wiki/QR_code#Error_correction

-------------------------------------------------------
"""
EPILOG = """
-------------------------------------------------------

EXPERIMENTAL, MAY NOT WORK FOR YOUR USE CASE.

SVG files are finicky and there are ways to write them
that this tool does not support.

Consider using something like Figma or Inkscape create/edit
the logo before use.


\b"""


def main():
    parser = ArgumentParser(
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "logo",
        type=Path,
        metavar="SVG",
        help="file path to the SVG logo to add",
    )
    parser.add_argument(
        "data",
        metavar="DATA",
        nargs="?",
        default=None,
        help="data to encode in the QR code",
    )
    parser.add_argument(
        *("-o", "--output"),
        type=Path,
        metavar="PATH",
        default=Path.cwd() / "output.svg",
        help="output file path (Default; %(default)s)",
    )
    parser.add_argument(
        *("-s", "--scale"),
        type=validate_scale,
        default=0.3,
        metavar="FLOAT",
        help="logo relative to the QR code. (Default: %(default)s)",
    )
    parser.add_argument(
        *("-b", "--blur"),
        type=float,
        metavar="FLOAT",
        default=1,
        help="get less dots inside the logo if logo has transparent elements. (Default: %(default)s)",
    )
    parser.add_argument(
        *("-m", "--margin"),
        type=int,
        default=0,
        metavar="INT",
        help="add margin around the logo.",
    )
    parser.add_argument(
        *("-c", "--correct"),
        type=float,
        default=(0.0, 0.0),
        nargs=2,
        metavar=("X", "Y"),
        dest="offset",
        help="correction of the logo position. (Default: %(default)s)",
    )
    parser.add_argument(
        *("-e", "--error-correction"),
        type=CorrectionLevel.from_string,
        choices=list(CorrectionLevel),
        default="H",
        help="level of error correction to use (Default: %(default)s)",
    )
    args = parser.parse_args(namespace=Parser())

    qr = QR(args.data or interactive(), args.error_correction)
    qr.add_logo(args.logo, args.scale, args.blur, args.margin, Offset(*args.offset))
    qr.save(args.output)


def url_validator(x):
    from urllib.parse import urlparse

    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except AttributeError:
        return False


def url():
    questions = [
        inquirer.Text("url", message="Enter the URL to encode", validate=url_validator),
    ]
    answers = inquirer.prompt(questions)
    if answers is None:
        raise SystemExit(1)

    return answers["url"]


def address_query(prefix: str):
    return [
        inquirer.Text(
            f"{prefix.lower()}_street",
            message=f"Enter the {prefix.capitalize()} Address, street",
            ignore=lambda x: f"{prefix.capitalize()} Address" not in x["fields"],
        ),
        inquirer.Text(
            f"{prefix.lower()}_city",
            message=f"Enter the {prefix.capitalize()} Address, city",
            ignore=lambda x: f"{prefix.capitalize()} Address" not in x["fields"],
        ),
        inquirer.Text(
            f"{prefix.lower()}_state",
            message=f"Enter the {prefix.capitalize()} Address, state",
            ignore=lambda x: f"{prefix.capitalize()} Address" not in x["fields"],
        ),
        inquirer.Text(
            f"{prefix.lower()}_zip",
            message=f"Enter the {prefix.capitalize()} Address, zip code",
            ignore=lambda x: f"{prefix.capitalize()} Address" not in x["fields"],
        ),
        inquirer.Text(
            f"{prefix.lower()}_country",
            message=f"Enter the {prefix.capitalize()} Address, country",
            ignore=lambda x: f"{prefix.capitalize()} Address" not in x["fields"],
        ),
    ]


def contact():
    questions = [
        inquirer.Checkbox(
            "fields",
            message="Select fields to include",
            choices=[
                "Email",
                "Work Phone",
                "Home Phone",
                "Work Address",
                "Home Address",
                "Organization",
                "Title",
                "URL",
                "Note",
            ],
        ),
        inquirer.Text("surname", message="Enter the surname"),
        inquirer.Text("name", message="Enter the name"),
        inquirer.Text(
            "email",
            message="Enter the email",
            validate=lambda _, x: re.match(r"^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$", x),
            ignore=lambda x: "Email" not in x["fields"],
        ),
        inquirer.Text(
            "work_phone",
            message="Enter the work phone",
            ignore=lambda x: "Work Phone" not in x["fields"],
        ),
        inquirer.Text(
            "home_phone",
            message="Enter the home phone",
            ignore=lambda x: "Home Phone" not in x["fields"],
        ),
        *address_query("Work"),
        *address_query("Home"),
        inquirer.Text(
            "organization",
            message="Enter the organization",
            ignore=lambda x: "Organization" not in x["fields"],
        ),
        inquirer.Text(
            "title",
            message="Enter the title",
            ignore=lambda x: "Title" not in x["fields"],
        ),
        inquirer.Text(
            "url",
            message="Enter the URL",
            ignore=lambda x: "URL" not in x["fields"],
        ),
        inquirer.Text(
            "note",
            message="Enter the note",
            ignore=lambda x: "Note" not in x["fields"],
        ),
    ]
    answers = inquirer.prompt(questions)
    if answers is None:
        raise SystemExit(1)

    vcard = VCard(answers["name"], answers["surname"])
    if "Email" in answers["fields"]:
        vcard.add_email(answers["email"])

    if "Work Phone" in answers["fields"]:
        vcard.add_work_phone(answers["work_phone"])

    if "Home Phone" in answers["fields"]:
        vcard.add_home_phone(answers["home_phone"])

    if "Work Address" in answers["fields"]:
        vcard.add_work_address(
            answers["work_street"],
            answers["work_city"],
            answers["work_state"],
            answers["work_zip"],
            answers["work_country"],
        )
    if "Home Address" in answers["fields"]:
        vcard.add_home_address(
            answers["home_street"],
            answers["home_city"],
            answers["home_state"],
            answers["home_zip"],
            answers["home_country"],
        )
    if "Organization" in answers["fields"]:
        vcard.add_organization(answers["organization"])

    if "Title" in answers["fields"]:
        vcard.add_title(answers["title"])

    if "URL" in answers["fields"]:
        vcard.add_url(answers["url"])
    return str(vcard)


def interactive():
    questions = [
        inquirer.List(
            "type",
            message="Select a type of QR code to generate",
            choices=["URL", "Contact"],
        ),
    ]
    answers = inquirer.prompt(questions)
    if answers is None:
        raise SystemExit(1)

    if answers["type"] == "URL":
        return url()

    if answers["type"] == "Contact":
        return contact()


if __name__ == "__main__":
    raise SystemExit(main())
