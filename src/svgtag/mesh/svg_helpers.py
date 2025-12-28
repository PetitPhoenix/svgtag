"""SVG preparation and transformation for trimesh conversion"""
import re
import tempfile


# Trimesh angle conversion factor
TRIMESH_ANGLE_FACTOR = -3300


def convert_angle_for_trimesh(angle_svg):
    """
    Convert SVG angle to trimesh angle.
    
    Args:
        angle_svg: Angle in degrees (standard SVG)
    
    Returns:
        Angle for trimesh (degrees, scaled by 1/3300)
    """
    return angle_svg / TRIMESH_ANGLE_FACTOR


def prepare_for_trimesh_angles(svg):
    """
    Prepare SVG for trimesh by converting rotation angles.
    
    Args:
        svg: SVG object
    
    Returns:
        New SVG object with converted angles
    """
    from ..svg.base import SVG
    
    # Update content first
    svg.update_svg_content()
    svg_content = svg.content
    
    # Convert rotation angles in content
    def convert_rotation(match):
        angle = float(match.group(1))
        cx = match.group(2)
        cy = match.group(3)
        
        trimesh_angle = angle / TRIMESH_ANGLE_FACTOR
        return f'rotate({trimesh_angle} {cx} {cy})'
    
    converted_count = len(re.findall(r'rotate\(([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\)', svg_content))
    
    svg_content = re.sub(
        r'rotate\(([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\)',
        convert_rotation,
        svg_content
    )
    
    if converted_count > 0:
        print(f"  Converted {converted_count} rotation(s) for trimesh")
    
    # Create new SVG and preserve structure
    new_svg = SVG()
    new_svg.width = svg.width
    new_svg.height = svg.height
    new_svg.viewBox = svg.viewBox.copy() if svg.viewBox else None
    new_svg.unit = svg.unit
    
    # IMPORTANT: Copy elements structure (preserves matrix transforms like flip)
    new_svg.elements = [elem.copy() if isinstance(elem, dict) else elem for elem in svg.elements]
    
    # Now convert rotation angles in elements
    def convert_element_rotations(element):
        """Recursively convert rotation angles in elements."""
        if isinstance(element, dict):
            # Convert rotation if present
            if element.get('rotation') is not None:
                element['rotation'] = element['rotation'] / TRIMESH_ANGLE_FACTOR
            
            # Recurse into group elements
            if element.get('tag') == 'g' and element.get('elements'):
                for child in element['elements']:
                    convert_element_rotations(child)
    
    for element in new_svg.elements:
        convert_element_rotations(element)
    
    # Update content with converted elements
    new_svg.update_svg_content()
    
    return new_svg


def prepare_face_A(svg):
    """
    Prepare SVG for face A (recto).
    - Convert rotation angles for trimesh
    
    Args:
        svg: SVG object
    
    Returns:
        Prepared SVG object
    """
    return prepare_for_trimesh_angles(svg)


def prepare_face_B_extrusion(svg):
    """
    Prepare SVG for face B extrusion (shapes must be flipped).
    - Convert rotation angles for trimesh
    - Flip vertically for correct extrusion direction
    
    Args:
        svg: SVG object
    
    Returns:
        Prepared SVG object
    """
    # First convert angles
    prepared = prepare_for_trimesh_angles(svg)
    # Then flip
    return prepared.flip('vertical')


def prepare_face_B_visual(svg):
    """
    Prepare SVG for face B visualization (as seen from back).
    - Just flip vertically
    - No angle conversion (for SVG export/preview only)
    
    Args:
        svg: SVG object
    
    Returns:
        Flipped SVG object
    """
    return svg.flip('vertical')


def svg_to_tempfile(svg):
    """
    Save SVG object to a temporary file and return the path.
    
    Args:
        svg: SVG object
    
    Returns:
        Path to temporary file (caller must delete it)
    """
    svg.update_svg_content()
    
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False, encoding='utf-8')
    tmp.write(svg.content)
    tmp.close()
    
    return tmp.name