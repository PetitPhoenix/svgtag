"""
Generic QR code generation (payload-agnostic).
https://github.com/lincolnloop/python-qrcode
"""
from pathlib import Path
import io
import qrcode
import qrcode.image.svg

from ..base import SVG, read_svg
from ..layouts import wifi_qr_layout


def qr_payload_svg(data, box_size=10, border=0, error_correction=None):
    """
    Generate a QR code for an arbitrary payload string, as an SVG string.

    Args:
        data: any string to encode (URL, vCard, mailto:, raw text, WIFI:..., etc.)
        box_size: size of each QR box
        border: border size in boxes
        error_correction: one of qrcode.constants.ERROR_CORRECT_{L,M,Q,H}
                          (default: L)

    Returns:
        SVG string
    """
    if error_correction is None:
        error_correction = qrcode.constants.ERROR_CORRECT_L

    qr = qrcode.QRCode(
        version=None,                 # smallest version that fits the data
        error_correction=error_correction,
        box_size=box_size,
        border=border,
        image_factory=qrcode.image.svg.SvgPathImage,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image()

    svg_io = io.BytesIO()
    img.save(svg_io)
    return svg_io.getvalue().decode("utf-8")


def qr_card_svg(payload, width_mm=100, height_mm=100, padding_mm=5, icon_path=None,
                layout=None):
    """
    Generate a QR card shape: a QR code for an arbitrary `payload`, positioned
    in a card layout, with an optional icon (top-right).

    Args:
        layout: optional pre-built Layout defining the card zones. Defaults to
            ``wifi_qr_layout`` (square card). Pass e.g. ``business_card_layout``
            for a landscape card. The layout must expose a ``qr_code`` area; the
            top-right icon is only drawn if it also exposes a ``signal_icon`` area.

    Returns:
        (svg, layout) — `layout` exposes the named text zones so callers can
        overlay their own labels/values (title, network_label, etc.).
    """
    svg = SVG()
    svg.unit = "mm"
    svg.width = width_mm
    svg.height = height_mm
    svg.viewBox = [0, 0, width_mm, height_mm]

    if layout is None:
        layout = wifi_qr_layout(width_mm, height_mm, padding_mm)

    # QR code — centré dans sa zone (le carré s'inscrit dans l'aire disponible)
    qr_svg_obj = SVG(qr_payload_svg(payload))
    qr_area = layout.get_area('qr_code')
    qr_scale = min(
        qr_area.width / qr_svg_obj.width,
        qr_area.height / qr_svg_obj.height,
    )
    qr_x = qr_area.x + (qr_area.width - qr_svg_obj.width * qr_scale) / 2
    qr_y = qr_area.y
    svg.add_group(qr_svg_obj.elements, translate=[qr_x, qr_y], scale=qr_scale)

    # Optional icon (top-right) — only if the layout provides a signal_icon zone
    icon_area = layout.get_area('signal_icon')
    if icon_path and icon_area is not None:
        icon_p = Path(icon_path)
        if icon_p.exists():
            icon = SVG(read_svg(str(icon_p)))
            icon_scale = min(
                icon_area.width / icon.width,
                icon_area.height / icon.height,
            )
            icon_x = icon_area.x + (icon_area.width - icon.width * icon_scale) / 2
            icon_y = icon_area.y + (icon_area.height - icon.height * icon_scale) / 2
            svg.add_group(icon.elements, translate=[icon_x, icon_y], scale=icon_scale)

    return svg, layout
