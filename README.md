# SVGTag - SVG Tag & Label Generator

A versatile Python library for creating customizable SVG tags, labels, and 3D printable objects with text engraving. Perfect for diving equipment tags, nameplates, organizational labels, and more.

## ✨ What Can You Create?

- **🏷️ Tags & Labels**: Circle, rectangle, triangle shapes with auto-fitting text
- **📋 Tablets & Slates**: Custom layouts for diving slates, instruction cards, test sheets
- **🔄 Recto-Verso**: Double-sided designs with automatic text orientation
- **🎨 Branded Items**: Position logos with flip compensation for proper alignment
- **🖨️ 3D Models**: Export STL files ready for multi-material 3D printing
- **📐 Custom Layouts**: Title zones, side text, main content areas with rotation support

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/PetitPhoenix/svgtag.git
cd svgtag
pip install -e ".[developer]"
```

### Simple Example

```python
from svgtag.svg.shapes import tag_circle_svg
from svgtag.svg.composition import add_text_zone

# Create tag
svg, layout = tag_circle_svg(length=80, height=35, hole_diameter=6, border=3)

# Add text
area = layout.get_area('main')
add_text_zone(svg, "My Tag", "path/to/font.ttf", area)
svg.update_svg_content()
svg.generate_svg_file("tag.svg")
```

## 📖 Core Capabilities

### Tag Shapes
```python
# Available shapes
from svgtag.svg.shapes import tag_circle_svg, tag_rectangle_svg, tag_triangle_svg

# Customizable parameters
svg, layout = tag_circle_svg(
    length=80,           # Width in mm
    height=35,           # Height in mm
    hole_diameter=6,     # Mounting hole
    border=3            # Text margin
)
```

### Text Handling
```python
# Auto-fitting text with line control
add_text_zone(svg, "Your text here", font_path, area,
    n=2,              # Force 2 lines (None = auto)
    text_scale=0.8,   # 80% of max size
    rotation=90       # Optional rotation
)

# Manual line breaks
add_text_zone(svg, "Line 1\nLine 2", font_path, area, n=2)
```

### 3D Printing
```python
from svgtag.mesh.extrusion import svg_to_path2d, extrude_path
from svgtag.mesh.assembly import assemble_plate, export_stl

# Convert SVG to 3D mesh
shape_mesh = extrude_path(svg_to_path2d(shape_svg), thickness=3)
text_mesh = extrude_path(svg_to_path2d(text_svg), thickness=1)

# Assemble (boolean subtract text from shape)
plate = assemble_plate(shape_mesh, [text_mesh])

# Export STL for multi-material printing
export_stl([plate, text_mesh], "output_dir", ['plate.stl', 'text.stl'])
```

### Recto-Verso Tags
```python
# Flip text for back side
verso_svg = svg.flip_element(-1, axis='vertical', center=(cx, cy))

# Or flip entire SVG
verso_svg = svg.flip(axis='horizontal')
```

### Brand/Logo Positioning
```python
from svgtag.svg.layouts import brand_layout

# Logo with automatic flip compensation
brand_layout_obj = brand_layout(
    main_area=area,
    brand_position='bottom-right',  # Final position after flip
    brand_scale=0.35,               # 35% of area
    flip_axis='horizontal'          # Auto-adjusts for verso
)
```

### Custom Layouts
```python
from svgtag.svg.shapes import tablet_svg

# Pre-built layout with multiple zones
tablet, layout = tablet_svg(
    width=80, height=129,
    layout_type='narcose'  # title + side_text + main_text
)

# Access individual zones
title_area = layout.get_area('title')
side_area = layout.get_area('side_text')
main_area = layout.get_area('main_text')
```

## 📂 Examples

See `examples/` directory for complete working examples:
- `tag_*.py` - Various tag configurations (shapes, text, 3D, brands)
- `tablet_*.py` - Tablet/slate layouts with custom zones
- Run any example: `python examples/tag_3d_with_brand.py`

## 🏗️ Architecture

```
svgtag/
├── geom/          # Geometric primitives (Shapely-based)
├── svg/           # SVG generation and composition
│   ├── shapes/    # Tag/tablet shapes
│   ├── layouts.py # Layout generators
│   └── text.py    # Text rendering with auto-fitting
├── mesh/          # 3D operations (extrusion, assembly)
└── utils/         # Utilities (number generation, etc.)
```

## 🔧 Key Dependencies

- **FontTools** - TTF/OTF font manipulation
- **Trimesh** - 3D mesh operations and STL export
- **Shapely** - 2D geometric operations
- **NumPy** - Numerical computations

## 🤝 Contributing

Contributions welcome! Please submit issues or pull requests on GitHub.

## 🙏 Acknowledgments

Special thanks to:
- [FontTools](https://github.com/fonttools/fonttools) - Font manipulation
- [Trimesh](https://github.com/mikedh/trimesh) - 3D mesh processing
- [Shapely](https://github.com/shapely/shapely) - Geometric operations