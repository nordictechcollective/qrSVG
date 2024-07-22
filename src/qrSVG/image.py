from pathlib import Path
from tempfile import NamedTemporaryFile
from xml.etree import ElementTree as ET

from cairosvg import svg2png
from PIL import Image
from qrcode.image.styles.moduledrawers import svg as SvgDrawer
from qrcode.image.svg import SvgImage
from qrcode.main import QRCode

from qrSVG.containers import CorrectionLevel


def svg2pil(path: Path, height: int, width: int) -> Image.Image:
    """Convert SVG to PIL image."""

    with NamedTemporaryFile(suffix=".png", delete=False, delete_on_close=False) as tmp:
        svg2png(
            url=str(path),
            write_to=tmp.name,
            output_height=height,
            output_width=width,
        )
        return Image.open(tmp.name)


def data2tree(data: str, error_correction: CorrectionLevel) -> ET.Element:
    """Data to QR SVG xml tree."""
    qr = QRCode(
        error_correction=error_correction.value,
        border=4,
    )
    qr.add_data(data)
    image = qr.make_image(
        image_factory=SvgImage,
        module_drawer=SvgDrawer.SvgCircleDrawer(),
    )
    return ET.fromstring(image.to_string())
