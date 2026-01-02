"""
WiFi QR code card generation.
https://github.com/lincolnloop/python-qrcode
"""
import io
import qrcode
import qrcode.image.svg
from ..base import SVG, read_svg
from ..layouts import wifi_qr_layout


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
    factory = qrcode.image.svg.SvgPathImage
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
        image_factory=factory,
    )
    
    # Escape special characters
    def escape_wifi_string(s):
        special_chars = ['\\', ';', ':', ',', '"']
        for char in special_chars:
            s = s.replace(char, '\\' + char)
        return s
    
    network_escaped = escape_wifi_string(network)
    password_escaped = escape_wifi_string(password)
    hidden_str = 'true' if hidden else 'false'
    
    wifi_string = f"WIFI:T:{protocol};S:{network_escaped};P:{password_escaped};H:{hidden_str};;"
    
    qr.add_data(wifi_string)
    qr.make(fit=True)
    img = qr.make_image()
    
    svg_io = io.BytesIO()
    img.save(svg_io)
    svg_string = svg_io.getvalue().decode("utf-8")
    
    return svg_string

def wifi_card_svg(
    network,
    password,
    width_mm=100,
    height_mm=100,
    padding_mm=5,
    protocol='WPA',
    hidden=False,
    signal_icon_path=None
):
    """
    Generate WiFi card shape with QR code and optional signal icon.
    """
    from pathlib import Path
    
    # Create base SVG
    svg = SVG()
    svg.unit = "mm"
    svg.width = width_mm
    svg.height = height_mm
    svg.viewBox = [0, 0, width_mm, height_mm]
    
    # Get layout
    layout = wifi_qr_layout(width_mm, height_mm, padding_mm)
    
    # Add QR code
    qr_svg_string = qr_code_svg(network, password, protocol, hidden)
    qr_svg_obj = SVG(qr_svg_string)
    
    # Position and scale QR code (occupe toute la zone sans padding)
    qr_area = layout.get_area('qr_code')
    qr_scale = min(
        qr_area.width / qr_svg_obj.width,
        qr_area.height / qr_svg_obj.height
    )
    
    qr_x = qr_area.x + (qr_area.width - qr_svg_obj.width * qr_scale) / 2
    qr_y = qr_area.y  # Commence pile au centre vertical (pas de centrage)
    
    svg.add_group(
        qr_svg_obj.elements,
        translate=[qr_x, qr_y],
        scale=qr_scale
    )
    
    # Add signal icon if provided
    if signal_icon_path:
        signal_path = Path(signal_icon_path)
        
        if signal_path.exists():
            signal = SVG(read_svg(str(signal_path)))
            signal_area = layout.get_area('signal_icon')
            signal_scale = min(
                signal_area.width / signal.width,
                signal_area.height / signal.height
            )
            
            signal_x = signal_area.x + (signal_area.width - signal.width * signal_scale) / 2
            signal_y = signal_area.y + (signal_area.height - signal.height * signal_scale) / 2
            
            svg.add_group(
                signal.elements,
                translate=[signal_x, signal_y],
                scale=signal_scale
            )
    
    return svg, layout