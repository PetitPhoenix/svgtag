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
    
    def list_areas(self) -> list[str]:
        """List all area names"""
        return list(self.areas.keys())
    
    def __repr__(self):
        return f"Layout({self.canvas_width}x{self.canvas_height}mm, {len(self.areas)} areas)"