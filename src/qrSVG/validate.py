try:
    import numpy as np
    from cv2 import COLOR_RGBA2RGB, QRCodeDetector, cvtColor
    from PIL.Image import Image

except ImportError:
    print(
        """
        Missing optional dependency.

        Run `pip install qrSVG[validate]` to install the dependencies required for this module.
        """
    )
    raise


def read(image: Image) -> str:
    """Validate that the QR code can be read."""
    img = np.array(image)
    # if transparent make white
    img[img[:, :, 3] == 0] = (255, 255, 255, 255)
    qr = cvtColor(img, COLOR_RGBA2RGB)
    content, *_ = QRCodeDetector().detectAndDecode(qr)
    return content
