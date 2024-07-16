from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import NamedTuple
from xml.etree import ElementTree as ET

import numpy as np
from cairosvg import svg2png
from PIL import Image, ImageFilter
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.styles.moduledrawers import svg as SvgDrawer
from qrcode.image.svg import SvgImage
from qrcode.main import QRCode


class Size(NamedTuple):
    width: int
    height: int
    unit: str

    @classmethod
    def from_string(cls, width: str, height: str, unit: str):
        w, h = width.replace(unit, ""), height.replace(unit, "")
        return cls(width=int(float(w)), height=int(float(h)), unit=unit)


class QR:
    def __init__(self, data: str):
        self.data = data

    def with_logo(self, logo: Path, output: Path):
        qr = QRCode(
            error_correction=ERROR_CORRECT_H,
            border=4,
        )
        qr.add_data(self.data)
        img = qr.make_image(
            image_factory=SvgImage,
            module_drawer=SvgDrawer.SvgCircleDrawer(),
        )

        tree = ET.fromstring(img.to_string())
        nodes = tree.findall(
            ".//svg:circle",
            namespaces={
                "svg": "http://www.w3.org/2000/svg",
            },
        )
        root = tree.find(".")
        size = Size.from_string(root.attrib["height"], root.attrib["width"], "mm")  # type: ignore

        mask = self._svg2mask(logo, size.height, size.width)
        mean = mask.mean()
        for node in reversed(nodes):
            x, y, _ = Size.from_string(node.attrib["cx"], node.attrib["cy"], "mm")
            if mask[y, x] > mean:
                tree.remove(node)

        logo_tree = ET.fromstring(logo.read_text())
        logo_root = logo_tree.find(".")

        if logo_root is not None:
            logo_root.attrib["width"] = f"{size.width // 2}{size.unit}"
            logo_root.attrib["height"] = f"{size.height // 2}{size.unit}"
            logo_root.attrib["x"] = f"{size.width // 4}{size.unit}"
            logo_root.attrib["y"] = f"{size.height // 4}{size.unit}"

            tree.append(logo_root)

        ET.register_namespace("", "http://www.w3.org/2000/svg")
        output.write_bytes(ET.tostring(tree, xml_declaration=True))

    def _svg2mask(self, path: Path, height, width):
        png = svg2png(
            url=str(path.resolve()),
            output_height=height // 2,
            output_width=width // 2,
        )
        with NamedTemporaryFile(suffix=".png", delete=False, delete_on_close=False) as f:
            output = Path(f.name)
            output.write_bytes(png)
            img = Image.open(output)

        blurred = img.filter(ImageFilter.GaussianBlur(1))
        array = np.zeros((height, width))
        pattern = np.array(blurred).sum(axis=2)
        array[height // 4 : -height // 4, width // 4 : -width // 4] = pattern
        return array
