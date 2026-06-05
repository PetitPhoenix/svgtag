"""Layout system for defining printable areas in SVG"""
from dataclasses import dataclass
from typing import Literal, Dict, Optional


@dataclass
class PrintableArea:
    """Defines a rectangular zone for content"""
    x: float  # Position in mm
    y: float
    width: float  # Size in mm
    height: float
    name: Optional[str] = None
    rotation: int = 0  # 0, 90, 180, 270 degrees
    
    def as_tuple(self):
        """Returns (x, y, width, height) for compatibility"""
        return (self.x, self.y, self.width, self.height)


class Layout:
    """Manages a set of printable areas with automatic coordinate conversion"""
    
    def __init__(self, canvas_width: float, canvas_height: float, padding: float = 0):
        """
        Initialize a layout.
        
        Args:
            canvas_width: Total canvas width in mm
            canvas_height: Total canvas height in mm
            padding: Padding around edges in mm
        """
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.padding = padding
        self.areas: Dict[str, PrintableArea] = {}
    
    def add_area(
        self, 
        name: str, 
        x: float, 
        y: float, 
        width: float, 
        height: float, 
        rotation: int = 0,
        unit: Literal['ratio', 'mm'] = 'ratio'
    ):
        """
        Add a printable area.
        
        Args:
            name: Unique identifier for this area
            x, y: Position (ratio 0-1 or absolute mm)
            width, height: Size (ratio 0-1 or absolute mm)
            rotation: Rotation angle (0, 90, 180, 270)
            unit: 'ratio' for percentages (0-1), 'mm' for absolute values
        
        Example:
            # Half width, quarter height at top-left
            layout.add_area('header', 0, 0, 0.5, 0.25, unit='ratio')
            
            # 20mm x 30mm at position (10, 15)
            layout.add_area('logo', 10, 15, 20, 30, unit='mm')
        """
        if unit == 'ratio':
            # Convert ratio (0-1) to absolute mm
            available_width = self.canvas_width - 2 * self.padding
            available_height = self.canvas_height - 2 * self.padding
            
            abs_x = self.padding + x * available_width
            abs_y = self.padding + y * available_height
            abs_w = width * available_width
            abs_h = height * available_height
        else:
            abs_x, abs_y, abs_w, abs_h = x, y, width, height
        
        self.areas[name] = PrintableArea(
            x=abs_x,
            y=abs_y,
            width=abs_w,
            height=abs_h,
            name=name,
            rotation=rotation
        )
    
    def get_area(self, name: str) -> Optional[PrintableArea]:
        """Get a printable area by name"""
        return self.areas.get(name)

    @classmethod
    def from_spec(cls, spec, width, height, padding=3, param_overrides=None):
        """Build a Layout from a declarative spec (a plain ``dict``).

        Lets a new shape be described as data instead of a new Python function.
        See :func:`build_layout` / module docstring for the spec format.
        svgtag stays format-agnostic: callers bring the dict (from YAML/JSON/
        Python — their choice), svgtag adds no serialization dependency.
        """
        return build_layout(spec, width, height, padding, param_overrides)

    def list_areas(self) -> list[str]:
        """List all area names"""
        return list(self.areas.keys())
    
    def __repr__(self):
        return f"Layout({self.canvas_width}x{self.canvas_height}mm, {len(self.areas)} areas)"


# ---------------------------------------------------------------------------
# Declarative layout specs — describe a layout as data instead of code.
# ---------------------------------------------------------------------------
#
# A layout is pure data: a canvas plus named rectangular areas. Instead of
# writing one Python function per shape, a layout can be described as a dict
# and materialised into a Layout via the existing add_area() API.
#
# Boundary: a spec describes *placement* (areas, ratios, rotation) and a *role*
# hint (``kind``). It carries no rendering logic — generation stays in code.
#
# svgtag is format-agnostic: build_layout / Layout.from_spec take a plain dict.
# Callers decide how to obtain it (YAML, JSON, Python literal) — no extra
# dependency is added here.
#
# Spec shape::
#
#     {
#       "params": {"title_ratio": 0.12, "side_ratio": 0.12},   # optional rails
#       "areas": [
#         {"name": "main",      "x": 0, "y": 0, "w": 1.0, "h": 1.0,
#          "kind": "brand_surface"},
#         {"name": "title",     "x": "side_ratio", "y": 0,
#          "w": "1 - side_ratio", "h": "title_ratio", "kind": "text"},
#         {"name": "side_text", "x": 0, "y": "title_ratio",
#          "w": "side_ratio", "h": "1 - title_ratio", "rotation": -90,
#          "kind": "text"},
#         {"name": "main_text", "x": "side_ratio", "y": "title_ratio",
#          "w": "1 - side_ratio", "h": "1 - title_ratio", "kind": "number_grid"},
#       ],
#     }
#
# The example above is exactly ``layouts.narcose_layout`` expressed as data.
#
# Coordinate values accept a number, a param name, or a simple "a op b"
# expression (op in + / -) where a/b are a number or a param name. No eval.

# Role hints validated at load time. A kind drives *rendering* in the caller;
# it has no geometric effect here.
KNOWN_KINDS = {'text', 'number_grid', 'brand', 'brand_surface', 'qr', 'icon'}


def _resolve_coord(value, params):
    """Resolve a coordinate: number, param name, or ``"a op b"`` expression."""
    if isinstance(value, (int, float)):
        return float(value)

    tokens = str(value).split()

    def term(tok):
        if tok in params:
            return float(params[tok])
        try:
            return float(tok)
        except ValueError:
            raise ValueError(
                f"Invalid layout coordinate {tok!r} "
                f"(not a number nor a param among {sorted(params)})"
            )

    if len(tokens) == 1:
        return term(tokens[0])
    if len(tokens) == 3 and tokens[1] in ('+', '-'):
        a, op, b = tokens
        return term(a) + term(b) if op == '+' else term(a) - term(b)
    raise ValueError(f"Unsupported layout expression: {value!r}")


def validate_spec(spec):
    """Validate a layout spec's structure. Raises ``ValueError`` if invalid."""
    if not isinstance(spec, dict) or 'areas' not in spec:
        raise ValueError("Invalid layout spec: missing 'areas' key")
    seen = set()
    for area in spec['areas']:
        name = area.get('name')
        if not name:
            raise ValueError("Layout area without 'name'")
        if name in seen:
            raise ValueError(f"Duplicate layout area: {name!r}")
        seen.add(name)
        kind = area.get('kind', 'text')
        if kind not in KNOWN_KINDS:
            raise ValueError(
                f"Area {name!r}: unknown kind {kind!r} (known: {sorted(KNOWN_KINDS)})"
            )
        for key in ('x', 'y', 'w', 'h'):
            if key not in area:
                raise ValueError(f"Area {name!r}: missing coordinate {key!r}")
    return spec


def build_layout(spec, width, height, padding=3, param_overrides=None):
    """Materialise a declarative spec (dict) into a :class:`Layout`.

    Args:
        spec: a layout spec dict (validated here).
        width, height, padding: canvas dimensions in mm (drive ratio→mm).
        param_overrides: overrides for the spec ``params`` (e.g.
            ``{"title_ratio": 0.05}``); ``None`` values are ignored.

    Returns:
        A :class:`Layout` populated with the spec's areas.
    """
    spec = validate_spec(spec)

    params = dict(spec.get('params') or {})
    if param_overrides:
        params.update({k: v for k, v in param_overrides.items() if v is not None})

    layout = Layout(width, height, padding)
    for area in spec['areas']:
        layout.add_area(
            area['name'],
            _resolve_coord(area['x'], params),
            _resolve_coord(area['y'], params),
            _resolve_coord(area['w'], params),
            _resolve_coord(area['h'], params),
            rotation=int(area.get('rotation', 0)),
            unit=area.get('unit', 'ratio'),
        )
    return layout


def zone_kinds(spec):
    """Return ``{area_name: kind}`` for a spec."""
    spec = validate_spec(spec)
    return {a['name']: a.get('kind', 'text') for a in spec['areas']}