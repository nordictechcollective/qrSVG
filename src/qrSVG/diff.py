"""
Diff logo and content of generated QR code
"""

from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from pathlib import Path
from xml.etree import ElementTree as ET

from qrSVG.image import svg2pil
from qrSVG.validate import read


class Parser(Namespace):
    file: Path
    content: bool | None
    logo: bool | None

    def initialize_selection(self):
        """Handle for no selection."""
        flag = ("content", "logo")

        if any(getattr(self, f) for f in flag):
            return

        for f in flag:
            setattr(self, f, True)


def metadata():
    """
    Get QRcode content and SVG logo part if any.
    """
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "file",
        type=Path,
    )
    parser.add_argument(
        *("-c", "--content"),
        action="store_true",
        help="return the data content of the QR code",
    )
    parser.add_argument(
        *("-l", "--logo"),
        action="store_true",
        help="return the SVG logo",
    )
    args = parser.parse_args(namespace=Parser())
    args.initialize_selection()

    if args.logo:
        tree = ET.parse(args.file)
        root = tree.getroot()
        namespace = "http://www.w3.org/2000/svg"
        logo = root.find("./svg", namespaces={"": namespace})

        if logo is None:
            return

        ET.register_namespace("", namespace)
        print(ET.tostring(logo).decode())

    if args.content:
        image = svg2pil(args.file, 2048, 2048)
        print(read(image))
