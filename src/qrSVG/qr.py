from __future__ import annotations

from functools import cached_property
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np
from PIL import ImageFilter

from qrSVG.containers import CorrectionLevel, Offset, Size, ViewBox
from qrSVG.image import data2tree, svg2pil

UNIT = "mm"  # TODO: This is not working with other units


class QR:
    def __init__(self, data, error_correction: CorrectionLevel = CorrectionLevel.H):
        self._data = str(data)
        self.tree = data2tree(self._data, error_correction)

    @cached_property
    def size(self) -> Size:
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        root: ET.Element = self.tree.find(".")  # type: ignore
        return Size.from_string(
            height=root.attrib["height"],
            width=root.attrib["width"],
            unit=UNIT,
        )

    def save(self, output: Path):
        """Save SVG to given path."""
        output.write_bytes(ET.tostring(self.tree, xml_declaration=True))  # type: ignore

    def add_logo(  # noqa: PLR0913
        self,
        logo: Path,
        scale: float = 0.3,
        blur: float = 1,
        margin: int = 0,
        offset: Offset = Offset(0, 0),  # noqa: B008
    ):
        """Add a logo to the center of the QR code."""
        tree = ET.fromstring(logo.read_text())
        root: ET.Element = tree.find(".")  # type: ignore

        size = self._logo_size(root, scale)

        _offset = Offset(
            x=(self.size.width - size.width) / 2,
            y=(self.size.height - size.height) / 2,
        )

        mask = self._logo_mask(logo, size, _offset, blur, margin)
        self._mask_logo_intersection(mask)

        root.attrib["width"] = f"{size.width}{UNIT}"
        root.attrib["x"] = f"{_offset.x + offset.x}{UNIT}"
        root.attrib["height"] = f"{size.height}{UNIT}"
        root.attrib["y"] = f"{_offset.y+ offset.y}{UNIT}"
        self.tree.append(root)

    def _mask_logo_intersection(self, mask: np.ndarray):
        """Remove nodes that intersect with the logo."""
        mean = mask.mean()
        nodes = self.tree.findall(".//svg:circle", namespaces={"svg": "http://www.w3.org/2000/svg"})
        for node in reversed(nodes):
            x, y, _ = Size.from_string(node.attrib["cx"], node.attrib["cy"], UNIT)
            if mask[int(y - 1), int(x - 1)] > mean:  # type: ignore
                self.tree.remove(node)

    def _logo_size(self, node: ET.Element, scale: float) -> Size:
        """Get the current SVG logo size."""
        try:
            size = Size.from_string(
                width=node.attrib["width"],  # type: ignore
                height=node.attrib["height"],  # type: ignore
                unit="mm",
            )
        except KeyError as e:
            viewbox = ViewBox.from_string(node.attrib.get("viewBox", ""))

            if not viewbox:
                raise Exception("No size information found in the SVG file") from e

            size = Size(
                width=float(viewbox.width),
                height=float(viewbox.height),
                unit="mm",
            )

        # NOTE: We need to scale the logo to match the QR code size, as well as the scale factor
        qr_logo_scale = max(self.size.width, self.size.height) / max(size.width, size.height)
        _scale = scale * qr_logo_scale
        width = _scale * size.width
        height = _scale * size.height

        return Size(width=width, height=height, unit=size.unit)

    def _logo_mask(self, path: Path, logo: Size, offset: Offset, blur: float = 0, margin: int = 0) -> np.ndarray:  # noqa: PLR0913
        """Create a 2D array to be used as image reference."""
        img = svg2pil(
            path=path,
            height=int(logo.height) + 2 * margin,
            width=int(logo.width) + 2 * margin,
        )
        blurred = img.filter(ImageFilter.GaussianBlur(blur))

        array = np.array(blurred).sum(axis=2)
        output = np.zeros((int(self.size.height), int(self.size.width)))
        start = Offset(
            x=int(offset.x) - margin,
            y=int(offset.y) - margin,
        )
        y, x = array.shape
        end = Offset(
            x=start.x + x,
            y=start.y + y,
        )
        output[start.y : end.y, start.x : end.x] = array  # type: ignore
        return output
