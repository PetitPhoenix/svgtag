import os
import re


def read_svg(file_path):
    with open(file_path, encoding="utf-8") as file:
        return file.read()


def save_svg(svg_content, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(svg_content)


class SVG:
    def __init__(self, content="", ppi=96):
        self.content = content
        self.ppi = ppi
        self.elements = []
        self.header = '<svg xmlns="http://www.w3.org/2000/svg">'
        self.unit = "px"
        self.width, self.height = None, None
        self.viewBox = self.x = self.y = None
        # Parse initial content if provided
        if self.content:
            self.parse_svg()

    def parse_svg(self):
        self.extract_header()
        self.extract_dimensions()
        self.extract_elements_and_transforms(self.content)

    def parse_element_attributes(self, attrs_string):
        # Simplification: parse the 'd' attribute for <path>, should be extended for other attributes/elements
        attributes = {}
        d_match = re.search(r'd="([^"]*)"', attrs_string)
        if d_match:
            attributes["d"] = d_match.group(1)
        # Add extraction of other attributes here as needed
        return attributes

    def create_empty_copy(self):
        """
        Create an empty SVG with same dimensions but no elements.
        
        Returns:
            New empty SVG with copied dimensions
        """
        empty = SVG()
        empty.width = self.width
        empty.height = self.height
        empty.viewBox = self.viewBox.copy() if self.viewBox else None
        empty.unit = self.unit
        return empty
    
    def copy(self):
        """
        Create a deep copy of this SVG.
        
        Returns:
            New SVG with copied dimensions and elements
        """
        # Start with empty copy (dimensions already handled)
        new_svg = self.create_empty_copy()
        
        # Copy header and ppi
        new_svg.ppi = self.ppi
        new_svg.header = self.header
        
        # Deep copy elements
        import copy
        new_svg.elements = copy.deepcopy(self.elements)
        
        return new_svg

    def extract_header(self):
        match = re.search(r"<svg[^>]*>\n", self.content)
        if match:
            self.header = match.group(0)

    def extract_dimensions(self):
        width_match = re.search(r'width="([\d.]+)(px|mm|cm)?', self.content)
        height_match = re.search(r'height="([\d.]+)(px|mm|cm)?', self.content)
        viewBox_match = re.search(r'viewBox="([\d.\s]+)"', self.content)

        if width_match:
            self.width = float(width_match.group(1))
            if width_match.group(2):
                self.unit = width_match.group(2)

        if height_match:
            self.height = float(height_match.group(1))

        if viewBox_match:
            self.viewBox = list(map(float, viewBox_match.group(1).split()))
            if len(self.viewBox) == 4:
                self.x, self.y, viewBoxWidth, viewBoxHeight = self.viewBox
                if not width_match:
                    self.width = viewBoxWidth
                if not height_match:
                    self.height = viewBoxHeight
                self.cx, self.cy = self.x + self.width / 2, self.y + self.height / 2

    def extract_elements_and_transforms(
        self, content, parent_translate=[0.0, 0.0], parent_scale=1.0, parent_rotation=None, parent_rotation_center=None
    ):
        # Handle groups recursively
        group_matches = re.findall(r"<g([^>]*)>(.*?)</g>", content, re.DOTALL)
        for group_match in group_matches:
            group_attrs = group_match[0]
            group_content = group_match[1]
            group_transform = self.extract_transform_details(group_attrs)
            # Combine group transformations with parent
            combined_translate = [
                parent_translate[0] + group_transform[0][0],
                parent_translate[1] + group_transform[0][1],
            ]
            combined_scale = parent_scale * group_transform[1]
            combined_rotation = group_transform[2] if group_transform[2] is not None else parent_rotation
            combined_rotation_center = group_transform[3] if group_transform[3] is not None else parent_rotation_center
            
            self.extract_elements_and_transforms(
                group_content, combined_translate, combined_scale, combined_rotation, combined_rotation_center
            )

        # Extract elements only if no groups
        if not group_matches:
            self.extract_and_add_elements("path", content, parent_translate, parent_scale, parent_rotation, parent_rotation_center)
        # Add other calls to extract_and_add_elements for other SVG tags here

    def extract_and_add_elements(self, tag, content, parent_translate, parent_scale, parent_rotation, parent_rotation_center):
        element_matches = re.findall(f"<{tag}([^>]*)/>", content)
        for element_attrs in element_matches:
            attributes = self.parse_element_attributes(element_attrs)
            element_transform = self.extract_transform_details(element_attrs)
            final_translate = [
                parent_translate[0] + element_transform[0][0],
                parent_translate[1] + element_transform[0][1],
            ]
            final_scale = parent_scale * element_transform[1]
            final_rotation = element_transform[2] if element_transform[2] is not None else parent_rotation
            final_rotation_center = element_transform[3] if element_transform[3] is not None else parent_rotation_center

            # Add validation before adding element
            if isinstance(attributes, dict):
                self.elements.append(
                    {
                        "tag": tag,
                        "attributes": attributes,
                        "translate": final_translate,
                        "scale": final_scale,
                        "rotation": final_rotation,
                        "rotation_center": final_rotation_center
                    }
                )
            else:
                print(
                    f"Warning: Attributes for element <{tag}/> are not a dictionary. Skipping element."
                )

    def extract_transform_details(self, transform_string):
        """Extract transformation details from a transform string."""
        translate_match = re.search(r"translate\(([^)]*)\)", transform_string)
        scale_match = re.search(r"scale\(([^)]*)\)", transform_string)
        rotate_match = re.search(r"rotate\(([^)]*)\)", transform_string)

        translate = (
            [float(n) for n in translate_match.group(1).split(",")]
            if translate_match
            else [0.0, 0.0]
        )
        scale = float(scale_match.group(1)) if scale_match else 1.0
        
        rotation = None
        rotation_center = None
        if rotate_match:
            rotate_parts = [float(n) for n in rotate_match.group(1).split()]
            rotation = rotate_parts[0]
            if len(rotate_parts) == 3:
                rotation_center = [rotate_parts[1], rotate_parts[2]]

        return translate, scale, rotation, rotation_center

    def add_svg(self, other_svg):
        """Add elements from another SVG object to this one."""
        for element in other_svg.elements:
            self.elements.append(element)

    def add_element(self, tag, attributes, translate=None, scale=None, rotation=None, rotation_center=None):
        """
        Add an SVG element to the elements list.
        
        Args:
            tag: SVG element type
            attributes: Dictionary of attributes
            translate: Translation [x, y]
            scale: Scale factor
            rotation: Rotation angle in degrees
            rotation_center: Rotation center [cx, cy]
        """
        if isinstance(attributes, dict):
            element = {
                "tag": tag,
                "attributes": attributes,
                "translate": translate,
                "scale": scale,
                "rotation": rotation,
                "rotation_center": rotation_center
            }
            self.elements.append(element)
        else:
            print(
                f"Warning: Attributes for element <{tag}/> are not a dictionary. Skipping element."
            )

    def add_path(self, d, translate=None, scale=None, rotation=None, rotation_center=None, **style_attrs):
        """
        Add a path to the elements list with optional transformation and style.
        
        Args:
            d: SVG path string or Shapely geometry
            translate: Translation [x, y]
            scale: Scale factor
            rotation: Rotation angle in degrees
            rotation_center: Rotation center [cx, cy]
            **style_attrs: Additional style attributes (stroke, fill, stroke_width, etc.)
                        Note: underscores in keys are converted to hyphens (stroke_width → stroke-width)
        """
        # Convert Shapely geometry to SVG path if needed
        if hasattr(d, 'exterior'):  # It's a Shapely Polygon
            from svgtag.geom.converters import to_svg_path
            d = to_svg_path(d)
        
        # Convert underscores to hyphens in attribute names
        attributes = {"d": d}
        for key, value in style_attrs.items():
            svg_key = key.replace('_', '-')
            attributes[svg_key] = value
        
        element = {
            "tag": "path",
            "attributes": attributes,
            "translate": translate,
            "scale": scale,
            "rotation": rotation,
            "rotation_center": rotation_center
        }
        self.elements.append(element)

    def add_group(self, elements, translate=None, scale=None, rotation=None, rotation_center=None):
        """
        Add a group of elements to the elements list with optional transformation.
        
        Args:
            elements: List of elements to group
            translate: Translation [x, y]
            scale: Scale factor
            rotation: Rotation angle in degrees
            rotation_center: Rotation center [cx, cy] (optional)
        """
        group = {
            "tag": "g",
            "elements": elements,
            "translate": translate,
            "scale": scale,
            "rotation": rotation,
            "rotation_center": rotation_center
        }
        self.elements.append(group)

    def add_rectangle(
        self,
        x,
        y,
        width,
        height,
        stroke="black",
        fill="none",
        radius="0",
        stroke_width=0.1,
    ):
        """Add a rectangle to the elements list."""
        attributes = {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "stroke": stroke,
            "fill": fill,
            "rx": radius,
            "stroke-width": stroke_width,
        }
        element = {"tag": "rect", "attributes": attributes}
        self.elements.append(element)

    def convert_units(self, target_unit):
        if target_unit == self.unit:
            return  # No conversion needed

        # Determine the conversion function based on the target unit
        if target_unit == "mm" and self.unit == "px":
            conversion_func = self.px_to_mm
            scale_conversion = 25.4 / self.ppi
        elif target_unit == "px" and self.unit == "mm":
            conversion_func = self.mm_to_px
            scale_conversion = self.ppi / 25.4
        else:
            return  # Invalid unit conversion

        # Convert dimensions
        self.width = conversion_func(self.width) if self.width is not None else None
        self.height = conversion_func(self.height) if self.height is not None else None
        self.viewBox = (
            [conversion_func(value) for value in self.viewBox] if self.viewBox else []
        )
        self.x = conversion_func(self.x) if self.x is not None else None
        self.y = conversion_func(self.y) if self.y is not None else None
        self.cx = conversion_func(self.cx) if self.cx is not None else None
        self.cy = conversion_func(self.cy) if self.cy is not None else None

        # Adjust scale and translate for each element
        for element in self.elements:
            if element.get("scale"):
                element["scale"] *= scale_conversion
            if element.get("translate"):
                element["translate"] = [
                    conversion_func(t) for t in element["translate"]
                ]
            if element.get("rotation_center"):
                element["rotation_center"] = [
                    conversion_func(c) for c in element["rotation_center"]
                ]

        self.unit = target_unit
        self.update_svg_content()

    def format_attributes(self, attributes):
        """Format element attributes as a string for inclusion in markup."""
        return " ".join(f'{key}="{value}"' for key, value in attributes.items())

    def process_element(self, element):
        """Process a single SVG element to generate its string representation."""
        if isinstance(element, dict):
            attributes_str = self.format_attributes(element.get("attributes", {}))
            transform_parts = []
            
            # Matrix (priority - if present, use it alone)
            if element.get("matrix"):
                matrix = element["matrix"]
                transform_parts.append(f"matrix({matrix[0]},{matrix[1]},{matrix[2]},{matrix[3]},{matrix[4]},{matrix[5]})")
            else:
                # Translate
                if element.get("translate"):
                    translate = element["translate"]
                    transform_parts.append(f"translate({translate[0]}, {translate[1]})")

                # Scale
                if element.get("scale"):
                    scale = element["scale"]
                    if scale != 1:
                        transform_parts.append(f"scale({scale})")
                
                # Rotation
                if element.get("rotation") is not None:
                    rotation = element["rotation"]
                    rotation_center = element.get("rotation_center")
                    if rotation_center:
                        transform_parts.append(f"rotate({rotation} {rotation_center[0]} {rotation_center[1]})")
                    else:
                        transform_parts.append(f"rotate({rotation})")
            
            # Add transform attribute if needed
            if transform_parts:
                attributes_str += ' transform="' + " ".join(transform_parts) + '"'

            # Groups vs simple elements
            if element["tag"] == "g":
                children_content = "".join(
                    [self.process_element(child) for child in element.get("elements", [])]
                )
                return f"<g {attributes_str}>\n{children_content}</g>\n"
            else:
                return f"<{element['tag']} {attributes_str} />\n"
        else:
            print(f"Error: Element is not a dictionary. Received: {element}")
            return ""  # Return empty string on error to avoid corrupting SVG

    def update_svg_content(self):
        # Update or add width and height attributes
        if self.width and self.height:
            if 'width="' in self.header:
                self.header = re.sub(
                    r'width="[^"]*"', f'width="{self.width}{self.unit}"', self.header
                )
            else:
                self.header = (
                    self.header.rstrip(">\n") + f' width="{self.width}{self.unit}">\n'
                )

            if 'height="' in self.header:
                self.header = re.sub(
                    r'height="[^"]*"', f'height="{self.height}{self.unit}"', self.header
                )
            else:
                self.header = (
                    self.header.rstrip(">\n") + f' height="{self.height}{self.unit}">\n'
                )

        # Update or add viewBox
        if self.viewBox:
            new_viewBox_str = " ".join(map(str, self.viewBox))
            if 'viewBox="' in self.header:
                self.header = re.sub(
                    r'viewBox="[^"]*"', f'viewBox="{new_viewBox_str}"', self.header
                )
            else:
                self.header = (
                    self.header.rstrip(">\n") + f' viewBox="{new_viewBox_str}">\n'
                )

        svg_elements_content = "".join(
            [self.process_element(element) for element in self.elements]
        )
        self.content = f"{self.header}\n{svg_elements_content}</svg>"

    def flip(self, axis='vertical', center=None):
        """
        Flip the entire SVG content around an axis.
        
        Args:
            axis: 'vertical' (flip left↔right) or 'horizontal' (flip top↔bottom)
            center: (cx, cy) tuple for flip axis position, or None to auto-calculate from viewBox
        
        Returns:
            New SVG with flipped content
        
        Examples:
            svg.flip('vertical')  # Flip left↔right (mirror around vertical axis)
            svg.flip('horizontal')  # Flip top↔bottom (mirror around horizontal axis)
        """
        # Calculate flip center and matrix
        if center is None:
            # Auto: use viewBox center
            if self.viewBox:
                if axis == 'vertical':
                    # Flip left↔right: mirror around vertical axis at center
                    minx, _, viewbox_width, _ = self.viewBox
                    tx = 2 * (minx + viewbox_width / 2)
                    matrix = [-1, 0, 0, 1, tx, 0]
                elif axis == 'horizontal':
                    # Flip top↔bottom: mirror around horizontal axis
                    _, miny, _, viewbox_height = self.viewBox
                    ty = miny + viewbox_height
                    matrix = [1, 0, 0, -1, 0, ty]
                else:
                    raise ValueError(f"Invalid axis: {axis}. Use 'vertical' or 'horizontal'")
            else:
                # Fallback
                tx = self.width if self.width else 0
                ty = self.height if self.height else 0
                matrix = [-1, 0, 0, 1, tx, 0] if axis == 'vertical' else [1, 0, 0, -1, 0, ty]
        else:
            # Manual: use provided center
            cx, cy = center
            if axis == 'vertical':
                # Flip left↔right around vertical axis at x=cx
                tx = 2 * cx
                matrix = [-1, 0, 0, 1, tx, 0]
            elif axis == 'horizontal':
                # Flip top↔bottom around horizontal axis at y=cy
                ty = 2 * cy
                matrix = [1, 0, 0, -1, 0, ty]
            else:
                raise ValueError(f"Invalid axis: {axis}. Use 'vertical' or 'horizontal'")
        
        # Create new SVG
        new_svg = SVG()
        new_svg.width = self.width
        new_svg.height = self.height
        new_svg.viewBox = self.viewBox.copy() if self.viewBox else None
        new_svg.unit = self.unit
        
        # Copy elements
        new_svg.elements = [elem.copy() if isinstance(elem, dict) else elem for elem in self.elements]
        
        # Wrap all in group with matrix
        if new_svg.elements:
            flipped_group = {
                'tag': 'g',
                'elements': new_svg.elements,
                'matrix': matrix,
                'translate': None,
                'scale': None,
                'rotation': None,
                'rotation_center': None
            }
            new_svg.elements = [flipped_group]
        
        return new_svg

    def recalculate_viewbox(self, margin=0):
        """
        Recalculate viewBox to fit all elements with optional margin.
        Uses trimesh to calculate actual bounds from rendered paths.
        
        Args:
            margin: Additional space around content (default: 0)
        
        Returns:
            self (for chaining)
        """
        if not self.elements:
            # No elements, use width/height if available
            if self.width and self.height:
                self.viewBox = [0, 0, self.width, self.height]
            return self
        
        try:
            from svgtag.mesh.extrusion import svg_to_path2d
            
            # Convert SVG to path2d to get actual bounds
            path2d = svg_to_path2d(self)
            
            # Get bounds from all entities
            if hasattr(path2d, 'bounds'):
                bounds = path2d.bounds  # [[minx, miny], [maxx, maxy]]
                min_x, min_y = bounds[0]
                max_x, max_y = bounds[1]
                
                self.viewBox = [
                    min_x - margin,
                    min_y - margin,
                    (max_x - min_x) + 2 * margin,
                    (max_y - min_y) + 2 * margin
                ]
                print(self.viewBox)
            else:
                # Fallback
                if self.width and self.height:
                    self.viewBox = [0, 0, self.width, self.height]
        
        except Exception as e:
            print(f"Warning: Could not recalculate viewBox: {e}")
            # Fallback to width/height
            if self.width and self.height:
                self.viewBox = [0, 0, self.width, self.height]
        
        return self

    def flip_element(self, element_index, axis='horizontal', center=None):
        """
        Flip a specific element around an axis.
        
        Args:
            element_index: Index of element to flip (supports negative indexing)
            axis: 'vertical' (flip left↔right) or 'horizontal' (flip top↔bottom)
            center: (cx, cy) tuple for flip axis position, or None to auto-calculate from viewBox
        
        Returns:
            New SVG with element flipped
        """
        # Calculate matrix (same logic as flip())
        if center is None:
            if self.viewBox:
                if axis == 'vertical':
                    minx, _, viewbox_width, _ = self.viewBox
                    tx = 2 * (minx + viewbox_width / 2)
                    matrix = [-1, 0, 0, 1, tx, 0]
                elif axis == 'horizontal':
                    _, miny, _, viewbox_height = self.viewBox
                    ty = miny + viewbox_height
                    matrix = [1, 0, 0, -1, 0, ty]
                else:
                    raise ValueError(f"Invalid axis: {axis}. Use 'vertical' or 'horizontal'")
            else:
                tx = self.width if self.width else 0
                ty = self.height if self.height else 0
                matrix = [-1, 0, 0, 1, tx, 0] if axis == 'vertical' else [1, 0, 0, -1, 0, ty]
        else:
            cx, cy = center
            if axis == 'vertical':
                tx = 2 * cx
                matrix = [-1, 0, 0, 1, tx, 0]
            elif axis == 'horizontal':
                ty = 2 * cy
                matrix = [1, 0, 0, -1, 0, ty]
            else:
                raise ValueError(f"Invalid axis: {axis}. Use 'vertical' or 'horizontal'")
        
        # Create new SVG
        new_svg = SVG()
        new_svg.width = self.width
        new_svg.height = self.height
        new_svg.viewBox = self.viewBox.copy() if self.viewBox else None
        new_svg.unit = self.unit
        
        # Copy elements
        new_svg.elements = [elem.copy() if isinstance(elem, dict) else elem for elem in self.elements]
        
        # Handle negative indexing
        if element_index < 0:
            element_index = len(new_svg.elements) + element_index
        
        # Check bounds
        if 0 <= element_index < len(new_svg.elements):
            elem = new_svg.elements[element_index]
            
            # Wrap element in group with matrix
            flipped_elem = {
                'tag': 'g',
                'elements': [elem],
                'matrix': matrix,
                'translate': None,
                'scale': None,
                'rotation': None,
                'rotation_center': None
            }
            new_svg.elements[element_index] = flipped_elem
        
        return new_svg

    def px_to_mm(self, px):
        return px * 25.4 / self.ppi

    def mm_to_px(self, mm):
        return mm * self.ppi / 25.4

    def generate_svg_file(self, output_file):
        """
        Generate an SVG file from the current SVG instance.

        Args:
            output_file (str): Path to the output file.
        """
        self.update_svg_content()  # Ensure self.content is up to date
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(self.content)
        print(f"SVG saved at {os.path.abspath(output_file)}")


def main():
    # Usage example
    output_path = "../examples/outputs"
    svg_content = read_svg("../static/images/network.svg")
    svg = SVG(svg_content)
    print(f"Width: {svg.width}{svg.unit}, Height: {svg.height}{svg.unit}")
    svg.generate_svg_file(os.path.join(output_path, "test_mm.svg"))

    svg.convert_units("px")
    svg.generate_svg_file(os.path.join(output_path, "test_px.svg"))
    
    svg = SVG()
    svg.add_element(
        "rect",
        {
            "x": "10",
            "y": "10",
            "width": "80",
            "height": "80",
            "stroke": "black",
            "fill": "transparent",
        },
        translate=(10, 10),
        scale=None
    )
    svg.generate_svg_file(os.path.join(output_path, "test_mm_rect.svg"))


if __name__ == "__main__":
    main()