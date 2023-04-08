"""
    make styled QR code
"""

from io import BytesIO
import base64

from qrcode.image.styles.moduledrawers.pil import (
    GappedSquareModuleDrawer,
    HorizontalBarsDrawer,
    RoundedModuleDrawer,
    VerticalBarsDrawer,
    SquareModuleDrawer,
    CircleModuleDrawer,
)
from qrcode.image.styledpil import StyledPilImage
# https://pypi.org/project/qrcode/
import qrcode

MODULES = {
    "Square": SquareModuleDrawer(),
    "Gapped Square": GappedSquareModuleDrawer(),
    "Circle": CircleModuleDrawer(),
    "Rounded": RoundedModuleDrawer(),
    "Vertical Bars": VerticalBarsDrawer(),
    "Horizontal Bars": HorizontalBarsDrawer(),
}

IMG_FORMAT = "png"


def select_options():
    """
    return list of options
        [ {"option": <option>, "value": <value> }, ...  ]
    so that select (lona.html.Select2) can be built

    ie.
        [ {"option": "Square", "value": "Square" }, ... ]
    """

    return [{"option": k, "value": k} for k in MODULES.keys()]


def image_src_str(url, qr_type=None):
    """
    generate qr code of url

    qr_type:
        "Square"
        "Gapped Square"
        "Circle"
        "Rounded"
        "Vertical Bars"
        "Horizontal Bars"

    return string that can be used for src in <img> tag
    """

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(url)
    qr.make(fit=True)

    # set module_drawer (defaults to SquareModuleDrawer)
    module_drawer = SquareModuleDrawer()
    if qr_type in MODULES:
        module_drawer = MODULES[qr_type]

    img = qr.make_image(image_factory=StyledPilImage, module_drawer=module_drawer)

    img_bytes = BytesIO()
    img.save(img_bytes, format=IMG_FORMAT)
    img_encoded = base64.b64encode(img_bytes.getvalue()).decode("utf-8")

    return f"data:image/{IMG_FORMAT};base64," + img_encoded
