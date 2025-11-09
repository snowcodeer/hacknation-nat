"""
Fuselage component generator.
Single Responsibility: Generates only fuselage geometry.
"""
import numpy as np
import trimesh
from app.models import AeroParameters
from app.services.generators.base_generator import ComponentGenerator


class FuselageGenerator(ComponentGenerator):
    """
    Generates fuselage meshes with type-specific shapes.

    Responsibilities:
    - Generate fuselage geometry from parameters
    - Support multiple fuselage types (commercial, fighter, cargo, private)
    - Create aerodynamic body shapes
    - Validate fuselage-specific parameters
    """

    def get_component_type(self) -> str:
        return "fuselage"

    def validate_parameters(self, params: AeroParameters) -> bool:
        """Validate fuselage parameters."""
        if not params.fuselage_length or params.fuselage_length <= 0:
            return False
        if not params.fuselage_diameter or params.fuselage_diameter <= 0:
            return False
        if params.fuselage_type and params.fuselage_type not in ['commercial', 'fighter', 'cargo', 'private']:
            return False
        return True

    def generate(self, params: AeroParameters) -> trimesh.Trimesh:
        """Generate fuselage mesh based on type."""
        if not self.validate_parameters(params):
            raise ValueError("Invalid fuselage parameters")

        length = params.fuselage_length
        diameter = params.fuselage_diameter
        fuselage_type = params.fuselage_type or 'commercial'

        # Circular cross-section resolution
        num_segments = 32
        num_length_segments = 30

        vertices = []
        faces = []

        # Generate fuselage from nose to tail
        for i in range(num_length_segments + 1):
            t = i / num_length_segments  # 0 (nose) to 1 (tail)
            x = (t - 0.5) * length  # Center at origin

            # Type-specific radius calculation
            radius = self._calculate_radius_at_position(t, diameter, fuselage_type)

            # Create circular cross-section
            for j in range(num_segments):
                angle = 2 * np.pi * j / num_segments
                y = radius * np.cos(angle)
                z = radius * np.sin(angle)
                vertices.append([x, y, z])

        # Generate faces connecting the rings
        for i in range(num_length_segments):
            for j in range(num_segments):
                current = i * num_segments + j
                next_in_ring = i * num_segments + (j + 1) % num_segments
                next_ring = (i + 1) * num_segments + j
                next_ring_next = (i + 1) * num_segments + (j + 1) % num_segments

                faces.append([current, next_ring, next_in_ring])
                faces.append([next_in_ring, next_ring, next_ring_next])

        vertices_array = np.array(vertices, dtype=np.float32)
        faces_array = np.array(faces, dtype=np.int32)

        mesh = trimesh.Trimesh(vertices=vertices_array, faces=faces_array)
        mesh.fix_normals()

        return mesh

    def _calculate_radius_at_position(self, t: float, diameter: float, fuselage_type: str) -> float:
        """
        Calculate fuselage radius at normalized position t (0 to 1).

        Args:
            t: Normalized position along fuselage (0=nose, 1=tail)
            diameter: Maximum fuselage diameter
            fuselage_type: Type of fuselage shape

        Returns:
            float: Radius at this position
        """
        radius_base = diameter / 2

        if fuselage_type == 'fighter':
            # Fighter jet: very sharp nose, sleek body, tapered tail
            if t < 0.2:  # Sharp nose
                return radius_base * (t / 0.2) ** 1.5
            elif t > 0.8:  # Tapered tail
                return radius_base * ((1 - t) / 0.2) ** 1.2
            else:  # Streamlined body
                return radius_base * (1 - 0.1 * abs(0.5 - t))

        elif fuselage_type == 'cargo':
            # Cargo: boxy, wide, minimal taper
            if t < 0.1:  # Short nose
                return radius_base * (t / 0.1) ** 0.3
            elif t > 0.9:  # Short tail
                return radius_base * ((1 - t) / 0.1) ** 0.3
            else:  # Wide boxy body
                return radius_base

        elif fuselage_type == 'private':
            # Private: sleek, streamlined, medium taper
            if t < 0.12:  # Smooth nose
                return radius_base * (t / 0.12) ** 0.6
            elif t > 0.88:  # Smooth tail
                return radius_base * ((1 - t) / 0.12) ** 0.8
            else:  # Streamlined body
                return radius_base

        else:  # commercial (default)
            # Commercial: cylindrical with gentle nose and tail cones
            if t < 0.15:  # Nose cone
                return radius_base * (t / 0.15) ** 0.5
            elif t > 0.85:  # Tail cone
                return radius_base * ((1 - t) / 0.15) ** 0.7
            else:  # Main cylindrical body
                return radius_base
