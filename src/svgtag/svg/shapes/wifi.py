"""
WiFi QR code card generation.

Built on top of the generic QR helpers in `qr.py`: the only WiFi-specific bit
is the `WIFI:...` payload string (see `build_wifi_payload`).
https://github.com/lincolnloop/python-qrcode
"""
from .qr import qr_payload_svg, qr_card_svg


def build_wifi_payload(network, password, protocol='WPA', hidden=False):
    """
    Build the standard WiFi QR payload string (Android/iOS network-join format).
    """
    def escape_wifi_string(s):
        special_chars = ['\\', ';', ':', ',', '"']
        for char in special_chars:
            s = s.replace(char, '\\' + char)
        return s

    network_escaped = escape_wifi_string(network)
    password_escaped = escape_wifi_string(password)
    hidden_str = 'true' if hidden else 'false'

    return f"WIFI:T:{protocol};S:{network_escaped};P:{password_escaped};H:{hidden_str};;"


def qr_code_svg(network, password, protocol='WPA', hidden=False, box_size=10, border=0):
    """
    Generate WiFi QR code as SVG string.

    Args:
        network: WiFi network name (SSID)
        password: WiFi password
        protocol: 'WPA', 'WEP', or 'nopass'
        hidden: True if network is hidden
        box_size: Size of each QR box
        border: Border size in boxes

    Returns:
        SVG string
    """
    payload = build_wifi_payload(network, password, protocol, hidden)
    return qr_payload_svg(payload, box_size=box_size, border=border)


def wifi_card_svg(
    network,
    password,
    width_mm=100,
    height_mm=100,
    padding_mm=5,
    protocol='WPA',
    hidden=False,
    signal_icon_path=None,
):
    """
    Generate WiFi card shape with QR code and optional signal icon.

    Thin wrapper over the generic `qr_card_svg`.
    """
    payload = build_wifi_payload(network, password, protocol, hidden)
    return qr_card_svg(
        payload,
        width_mm=width_mm,
        height_mm=height_mm,
        padding_mm=padding_mm,
        icon_path=signal_icon_path,
    )
