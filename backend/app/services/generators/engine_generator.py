"""
Engine component generator.
Single Responsibility: Generates only engine nacelle geometry.
"""
import numpy as np
import trimesh
import sys
from app.models import AeroParameters
from app.services.generators.base_generator import ComponentGenerator


class EngineGenerator(ComponentGenerator):
    """
    Generates engine nacelle meshes with realistic jet engine shapes.

    Responsibilities:
    - Generate engine geometry from parameters
    - Create cylindrical nacelle with intake and exhaust
    - Support variable radius along engine length
    - Validate engine-specific parameters
    """

    def get_component_type(self) -> str:
        return "engine"

    def validate_parameters(self, params: AeroParameters) -> bool:
        """Validate engine parameters."""
        if not params.engine_length or params.engine_length <= 0:
            return False
        if not params.engine_diameter or params.engine_diameter <= 0:
            return False
        return True

    def generate(self, params: AeroParameters) -> trimesh.Trimesh:
        """Generate engine nacelle mesh."""
        if not self.validate_parameters(params):
            raise ValueError("Invalid engine parameters")

        length = params.engine_length
        diameter = params.engine_diameter

        # Engine nacelle resolution
        num_segments = 24  # Circular cross-section
        num_length_segments = 20

        vertices = []
        faces = []

        # Generate engine from intake to exhaust
        for i in range(num_length_segments + 1):
            t = i / num_length_segments  # 0 (intake) to 1 (exhaust)
            x = (t - 0.5) * length  # Center at origin

            # Variable radius for realistic engine shape
            radius = self._calculate_radius_at_position(t, diameter)

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

        print(f"[ENGINE GENERATOR] Created single engine with {len(vertices_array)} vertices, {len(faces_array)} faces", file=sys.stderr, flush=True)
        print(f"[ENGINE GENERATOR] X range: {vertices_array[:, 0].min()} to {vertices_array[:, 0].max()}", file=sys.stderr, flush=True)

        return mesh

    def _calculate_radius_at_position(self, t: float, diameter: float) -> float:
        """
        Calculate engine radius at normalized position t (0 to 1).

        Args:
            t: Normalized position along engine (0=intake, 1=exhaust)
            diameter: Maximum engine diameter

        Returns:
            float: Radius at this position
        """
        radius_base = diameter / 2

        if t < 0.2:  # Intake - larger for air intake
            return radius_base * (1 + 0.3 * (1 - t / 0.2))
        elif t > 0.8:  # Exhaust nozzle - tapered for thrust
            return radius_base * (0.9 - 0.2 * (t - 0.8) / 0.2)
        else:  # Main engine body - cylindrical
            return radius_base
