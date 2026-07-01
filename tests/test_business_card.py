"""Tests for the landscape business-card additions (v0.12.0):
- ``business_card_layout``
- ``text_svg(..., align=...)``
- ``qr_card_svg(..., layout=...)``
"""
from pathlib import Path

import pytest

from svgtag.svg.layouts import business_card_layout, wifi_qr_layout
from svgtag.svg.shapes import qr_card_svg
from svgtag.svg.text import text_svg


def _a_font():
    """Any .ttf on disk (the repo ships fonts under static/ ; fall back to a scan)."""
    for root in (Path(__file__).resolve().parent.parent, Path("/")):
        ttf = next(root.rglob("*.ttf"), None)
        if ttf is not None:
            return str(ttf)
    pytest.skip("no .ttf available")


# --- business_card_layout --------------------------------------------------

def test_business_card_layout_zones():
    layout = business_card_layout(85, 55, 5)
    zones = set(layout.areas)
    assert {"title", "org", "line1", "line2", "line3", "qr_code", "qr_caption"} <= zones


def test_business_card_layout_has_no_signal_icon():
    # The big QR carries the card; no top-right icon zone.
    assert business_card_layout(85, 55, 5).get_area("signal_icon") is None


def test_business_card_qr_is_on_the_right():
    layout = business_card_layout(85, 55, 5)
    qr = layout.get_area("qr_code")
    title = layout.get_area("title")
    # QR sits to the right of the (left-column) title zone.
    assert qr.x > title.x + title.width


# --- text_svg alignment ----------------------------------------------------

def test_text_align_changes_geometry():
    ttf = _a_font()
    left = text_svg("Hi", ttf, 12, 40, 8, x0=0, y0=0, align="left")
    center = text_svg("Hi", ttf, 12, 40, 8, x0=0, y0=0, align="center")
    right = text_svg("Hi", ttf, 12, 40, 8, x0=0, y0=0, align="right")
    assert repr(left.elements) != repr(center.elements)
    assert repr(center.elements) != repr(right.elements)


def test_text_align_defaults_to_center():
    ttf = _a_font()
    default = text_svg("Hi", ttf, 12, 40, 8, x0=0, y0=0)
    center = text_svg("Hi", ttf, 12, 40, 8, x0=0, y0=0, align="center")
    assert repr(default.elements) == repr(center.elements)


# --- qr_card_svg layout override ------------------------------------------

def test_qr_card_svg_accepts_custom_layout():
    layout = business_card_layout(85, 55, 5)
    svg, returned = qr_card_svg("BEGIN:VCARD\nEND:VCARD", 85, 55, 5,
                                icon_path=None, layout=layout)
    # The passed layout is used (and returned) as-is.
    assert returned is layout
    svg.update_svg_content()
    assert len(svg.content) > 0


def test_qr_card_svg_defaults_to_wifi_layout():
    svg, layout = qr_card_svg("hello", 100, 100, 5)
    assert layout.get_area("signal_icon") is not None
