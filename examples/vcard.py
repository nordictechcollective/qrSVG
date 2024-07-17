from pathlib import Path

from qrSVG.qr import QR
from qrSVG.vcard import VCard

# Create a new VCard object
vcard = VCard("Forest", "Gump")
vcard.add_organization("Bubba Gump Shrimp Co.")
vcard.add_work_address("100 Waters Edge", "Baytown", "LA", "30314", "USA")
vcard.add_work_phone("(800) 555-1212")
vcard.add_email("forest.gump@bubbagump.com")
vcard.add_url("http://www.bubbagump.com")
vcard.add_note("life is like a box of chocolates")

# Create a QRCode object
qr = QR(vcard)
qr.save(Path("vcard.svg"))
qr.add_logo(
    Path(__file__).parent.with_name("test") / "svg" / "Bubba_Gump_logo.svg",
    margin=2,
)
qr.save(Path(__file__).parent.with_name("docs") / "vcard.svg")
