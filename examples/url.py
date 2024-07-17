from pathlib import Path

from qrSVG.qr import QR

url = "https://www.youtube.com/watch?v=xvFZjo5PgG0"

# Create a QRCode object
qr = QR(url)
qr.add_logo(
    Path(__file__).parent.with_name("test") / "svg" / "rick.svg",
    scale=0.4,
    blur=1,
    margin=1,
)
qr.save(Path(__file__).parent.with_name("docs") / "url.svg")
